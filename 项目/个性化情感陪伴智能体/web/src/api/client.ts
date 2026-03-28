import type {
  AdminHotConfigPatch,
  AdminHotConfigSnapshot,
  AdminQuotaResponse,
  AdminRiskEventsResponse,
  ChatRequest,
  ChatResponse,
  FastAPIErrorBody,
  FeedbackExportResponse,
  FeedbackListResponse,
  FeedbackRequest,
  FeedbackResponse,
  HealthResponse,
  EmotionStatsResponse,
  EvalJobStatusResponse,
  EvalRunRequest,
  EvalRunResponse,
  LTMPatchRequest,
  LTMItemOut,
  LTMListResponse,
  LTMUndoExtractRequest,
  LTMUndoExtractResponse,
  LTMWriteRequest,
  SessionListResponse,
  SessionMessagesResponse,
  TraceListResponse,
  TraceRecordOut,
  UserForgetResponse,
} from './types'

function apiBase(): string {
  const v = import.meta.env.VITE_API_BASE as string | undefined
  if (v != null && v.trim() !== '') {
    return v.replace(/\/$/, '')
  }
  if (import.meta.env.DEV) {
    return '/api'
  }
  return ''
}

export class ApiCallError extends Error {
  readonly status: number
  readonly body: unknown

  constructor(status: number, body: unknown, message?: string) {
    super(message ?? `HTTP ${status}`)
    this.name = 'ApiCallError'
    this.status = status
    this.body = body
  }
}

function formatFastAPIError(body: unknown): string {
  if (body == null) return '（无响应体）'
  if (typeof body === 'string') return body
  if (typeof body !== 'object') return String(body)
  const b = body as FastAPIErrorBody
  if (!('detail' in b)) {
    try {
      return JSON.stringify(body, null, 2)
    } catch {
      return String(body)
    }
  }
  const d = b.detail
  if (typeof d === 'string') return d
  if (Array.isArray(d)) {
    return d
      .map((item) => {
        const loc = item.loc?.join('.') ?? ''
        return loc ? `${loc}: ${item.msg}` : item.msg
      })
      .join('\n')
  }
  return JSON.stringify(body, null, 2)
}

export function getApiErrorMessage(err: unknown): string {
  if (err instanceof ApiCallError) {
    return formatFastAPIError(err.body) || err.message
  }
  if (err instanceof Error) return err.message
  return String(err)
}

async function parseJsonOrText(res: Response): Promise<unknown> {
  const text = await res.text()
  if (!text) return null
  try {
    return JSON.parse(text) as unknown
  } catch {
    return text
  }
}

export type FetchOptions = RequestInit & {
  /** 写入请求头 `X-Admin-Token`（运营接口预留；/chat 通常不需要） */
  adminToken?: string
}

export async function apiFetch<T>(path: string, init?: FetchOptions): Promise<T> {
  const url = `${apiBase()}${path.startsWith('/') ? path : `/${path}`}`
  const headers = new Headers(init?.headers)
  if (init?.body != null && !headers.has('Content-Type')) {
    headers.set('Content-Type', 'application/json')
  }
  const token = init?.adminToken?.trim()
  if (token) headers.set('X-Admin-Token', token)

  const {
    adminToken: _omitAdmin,
    headers: _h,
    ...rest
  } = init ?? {}
  void _omitAdmin
  void _h
  const res = await fetch(url, { ...rest, headers })
  const body = await parseJsonOrText(res)
  if (!res.ok) {
    throw new ApiCallError(res.status, body, formatFastAPIError(body))
  }
  return body as T
}

export async function postChat(req: ChatRequest, adminToken?: string): Promise<ChatResponse> {
  return apiFetch<ChatResponse>('/chat', {
    method: 'POST',
    body: JSON.stringify(req),
    adminToken,
  })
}

/** SSE `/chat/stream`：流式增量 + 最终 `done` 与 `/chat` JSON 对齐（含脱敏后 reply） */
export async function postChatStream(
  req: ChatRequest,
  options: {
    adminToken?: string
    onDelta?: (chunk: string) => void
    onMeta?: (meta: { trace_id: string; user_id: string; session_id: string; quota_degraded?: boolean }) => void
  } = {},
): Promise<ChatResponse> {
  const url = `${apiBase()}/chat/stream`
  const headers = new Headers()
  headers.set('Content-Type', 'application/json')
  const t = options.adminToken?.trim()
  if (t) headers.set('X-Admin-Token', t)
  const res = await fetch(url, { method: 'POST', headers, body: JSON.stringify(req) })
  if (!res.ok) {
    const body = await parseJsonOrText(res)
    throw new ApiCallError(res.status, body, formatFastAPIError(body))
  }
  if (!res.body) throw new ApiCallError(502, null, 'No response body')

  const reader = res.body.getReader()
  const dec = new TextDecoder()
  let buf = ''
  let donePayload: ChatResponse | null = null

  while (true) {
    const { done, value } = await reader.read()
    buf += dec.decode(value ?? new Uint8Array(), { stream: !done })
    const blocks = buf.split('\n\n')
    buf = blocks.pop() ?? ''
    for (const block of blocks) {
      const dataLine = block.split('\n').find((l) => l.startsWith('data: '))
      if (!dataLine) continue
      const raw = dataLine.slice(6).trim()
      if (!raw) continue
      let ev: Record<string, unknown>
      try {
        ev = JSON.parse(raw) as Record<string, unknown>
      } catch {
        continue
      }
      const kind = ev.event
      if (kind === 'meta' && typeof ev.trace_id === 'string') {
        options.onMeta?.({
          trace_id: ev.trace_id,
          user_id: String(ev.user_id ?? ''),
          session_id: String(ev.session_id ?? ''),
          quota_degraded: Boolean(ev.quota_degraded),
        })
      } else if (kind === 'delta' && typeof ev.c === 'string' && ev.c) {
        options.onDelta?.(ev.c)
      } else if (kind === 'error') {
        const st = typeof ev.status === 'number' ? ev.status : 502
        throw new ApiCallError(st, ev.detail, formatFastAPIError(ev.detail))
      } else if (kind === 'done') {
        const { event: _e, ...rest } = ev
        void _e
        donePayload = rest as unknown as ChatResponse
      }
    }
    if (done) break
  }

  if (!donePayload) {
    throw new ApiCallError(502, null, '流式响应未收到结束事件')
  }
  return donePayload
}

export async function getHealth(): Promise<HealthResponse> {
  return apiFetch<HealthResponse>('/health', { method: 'GET' })
}

export async function getEmotionStats(userId: string, window: 'day' | 'week'): Promise<EmotionStatsResponse> {
  const sp = new URLSearchParams({ user_id: userId, window })
  return apiFetch<EmotionStatsResponse>(`/emotion/stats?${sp}`)
}

export async function getSessions(userId: string): Promise<SessionListResponse> {
  const q = new URLSearchParams({ user_id: userId })
  return apiFetch<SessionListResponse>(`/sessions?${q}`)
}

export async function getSessionMessages(userId: string, sessionId: string): Promise<SessionMessagesResponse> {
  const q = new URLSearchParams({ user_id: userId })
  return apiFetch<SessionMessagesResponse>(`/sessions/${encodeURIComponent(sessionId)}/messages?${q}`)
}

export async function deleteSession(userId: string, sessionId: string): Promise<{ ok: boolean; existed: boolean }> {
  const q = new URLSearchParams({ user_id: userId })
  return apiFetch(`/sessions/${encodeURIComponent(sessionId)}?${q}`, { method: 'DELETE' })
}

export async function getTrace(traceId: string, userId?: string): Promise<TraceRecordOut> {
  const q = userId != null && userId !== '' ? `?user_id=${encodeURIComponent(userId)}` : ''
  return apiFetch<TraceRecordOut>(`/trace/${encodeURIComponent(traceId)}${q}`)
}

export async function listTraces(userId: string, sessionId: string, limit = 15): Promise<TraceListResponse> {
  const q = new URLSearchParams({
    user_id: userId,
    session_id: sessionId,
    limit: String(limit),
  })
  return apiFetch<TraceListResponse>(`/traces?${q}`)
}

export async function postFeedback(body: FeedbackRequest): Promise<FeedbackResponse> {
  return apiFetch<FeedbackResponse>('/feedback', {
    method: 'POST',
    body: JSON.stringify(body),
  })
}

export async function getLtmList(params: {
  userId: string
  type?: string
  q?: string
  /** 与后端 LTM.source 精确匹配，如 dialogue_extract */
  source?: string
  limit?: number
  offset?: number
}): Promise<LTMListResponse> {
  const sp = new URLSearchParams()
  sp.set('user_id', params.userId)
  if (params.type) sp.set('type', params.type)
  if (params.q) sp.set('q', params.q)
  if (params.source) sp.set('source', params.source)
  sp.set('limit', String(params.limit ?? 12))
  sp.set('offset', String(params.offset ?? 0))
  return apiFetch<LTMListResponse>(`/memory/ltm?${sp}`)
}

export async function getLtmItem(id: string, userId: string): Promise<LTMItemOut> {
  const q = new URLSearchParams({ user_id: userId })
  return apiFetch<LTMItemOut>(`/memory/ltm/${encodeURIComponent(id)}?${q}`)
}

export async function postLtm(body: LTMWriteRequest): Promise<{ id: string }> {
  return apiFetch('/memory/ltm', { method: 'POST', body: JSON.stringify(body) })
}

export async function postLtmUndoExtract(body: LTMUndoExtractRequest): Promise<LTMUndoExtractResponse> {
  return apiFetch<LTMUndoExtractResponse>('/memory/ltm/undo_extract', {
    method: 'POST',
    body: JSON.stringify(body),
  })
}

export async function patchLtm(id: string, userId: string, body: LTMPatchRequest): Promise<LTMItemOut> {
  const q = new URLSearchParams({ user_id: userId })
  return apiFetch(`/memory/ltm/${encodeURIComponent(id)}?${q}`, {
    method: 'PATCH',
    body: JSON.stringify(body),
  })
}

export async function deleteLtm(id: string, userId: string): Promise<{ ok: boolean; id: string }> {
  const q = new URLSearchParams({ user_id: userId })
  return apiFetch(`/memory/ltm/${encodeURIComponent(id)}?${q}`, { method: 'DELETE' })
}

export async function postEvalRun(body: EvalRunRequest, adminToken?: string): Promise<EvalRunResponse> {
  return apiFetch<EvalRunResponse>('/admin/eval/run', {
    method: 'POST',
    body: JSON.stringify(body),
    adminToken,
  })
}

export async function getEvalJob(jobId: string, adminToken?: string): Promise<EvalJobStatusResponse> {
  return apiFetch<EvalJobStatusResponse>(`/admin/eval/jobs/${encodeURIComponent(jobId)}`, {
    method: 'GET',
    adminToken,
  })
}

export async function getAdminConfig(adminToken?: string): Promise<AdminHotConfigSnapshot> {
  return apiFetch<AdminHotConfigSnapshot>('/admin/config', { method: 'GET', adminToken })
}

export async function patchAdminConfig(
  body: AdminHotConfigPatch,
  adminToken?: string,
): Promise<AdminHotConfigSnapshot> {
  return apiFetch<AdminHotConfigSnapshot>('/admin/config', {
    method: 'PATCH',
    body: JSON.stringify(body),
    adminToken,
  })
}

export async function getAdminQuota(userId: string | undefined, adminToken?: string): Promise<AdminQuotaResponse> {
  const sp = new URLSearchParams()
  if (userId != null && userId.trim() !== '') sp.set('user_id', userId.trim())
  const q = sp.toString()
  return apiFetch<AdminQuotaResponse>(`/admin/quota${q ? `?${q}` : ''}`, { adminToken })
}

export async function getAdminRiskEvents(limit: number, adminToken?: string): Promise<AdminRiskEventsResponse> {
  const sp = new URLSearchParams({ limit: String(limit) })
  return apiFetch<AdminRiskEventsResponse>(`/admin/risk_events?${sp}`, { adminToken })
}

export async function getFeedbackRecent(limit: number, userId?: string): Promise<FeedbackListResponse> {
  const sp = new URLSearchParams({ limit: String(limit) })
  if (userId != null && userId.trim() !== '') sp.set('user_id', userId.trim())
  return apiFetch<FeedbackListResponse>(`/feedback/recent?${sp}`)
}

export async function getFeedbackExport(limit: number, userId?: string): Promise<FeedbackExportResponse> {
  const sp = new URLSearchParams({ limit: String(limit) })
  if (userId != null && userId.trim() !== '') sp.set('user_id', userId.trim())
  return apiFetch<FeedbackExportResponse>(`/feedback/export?${sp}`)
}

/** 合规导出 JSON（附件流，解析后格式化为可读字符串下载） */
export async function fetchUserExportJson(userId: string, adminToken?: string): Promise<string> {
  const url = `${apiBase()}/users/${encodeURIComponent(userId)}/export`
  const headers = new Headers()
  const t = adminToken?.trim()
  if (t) headers.set('X-Admin-Token', t)
  const res = await fetch(url, { method: 'GET', headers })
  const text = await res.text()
  if (!res.ok) {
    let parsed: unknown = text
    try {
      parsed = JSON.parse(text) as unknown
    } catch {
      /* keep text */
    }
    throw new ApiCallError(res.status, parsed, formatFastAPIError(parsed))
  }
  try {
    return JSON.stringify(JSON.parse(text) as object, null, 2)
  } catch {
    return text
  }
}

export async function postUserForget(
  userId: string,
  body: { confirm: boolean; clear_stm?: boolean },
  adminToken?: string,
): Promise<UserForgetResponse> {
  return apiFetch<UserForgetResponse>(`/users/${encodeURIComponent(userId)}/forget`, {
    method: 'POST',
    body: JSON.stringify(body),
    adminToken,
  })
}
