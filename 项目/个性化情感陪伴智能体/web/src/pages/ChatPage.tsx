import { useCallback, useEffect, useMemo, useRef, useState, type ReactNode } from 'react'
import { Link } from 'react-router-dom'
import { ChatMarkdown } from '../components/ChatMarkdown'
import { useToast } from '../context/ToastContext'
import {
  ApiCallError,
  deleteSession,
  getApiErrorMessage,
  getSessionMessages,
  getSessions,
  getTrace,
  listTraces,
  postChat,
  postChatStream,
  postFeedback,
  postLtmUndoExtract,
} from '../api/client'
import type { ChatResponse, TraceRecordOut } from '../api/types'
import { usePersistentString } from '../hooks/usePersistentString'

const LS_USER = 'companion_user_id'
const LS_SESSION = 'companion_session_id'
const LS_STREAM = 'companion_chat_stream'

function titlesKey(uid: string) {
  return `companion_session_titles:${uid.trim() || 'default'}`
}

function loadSessionTitles(uid: string): Record<string, string> {
  try {
    const raw = localStorage.getItem(titlesKey(uid))
    if (!raw) return {}
    const o = JSON.parse(raw) as unknown
    if (typeof o !== 'object' || o === null) return {}
    return o as Record<string, string>
  } catch {
    return {}
  }
}

function persistSessionTitles(uid: string, map: Record<string, string>) {
  try {
    localStorage.setItem(titlesKey(uid), JSON.stringify(map))
  } catch {
    /* ignore */
  }
}

function readInitialSessionId(): string {
  try {
    const v = localStorage.getItem(LS_SESSION)
    if (v && v.trim()) return v.trim()
  } catch {
    /* ignore */
  }
  return crypto.randomUUID()
}

const COLLAPSE_CHARS = 560

type UiMsg = {
  id: string
  role: 'user' | 'assistant'
  content: string
  trace_id?: string
  citations?: unknown[] | null
  tool_summary?: Record<string, unknown> | null
  createdAt?: number
  /** 流式生成中：用纯文本展示，完成后关闭 */
  streaming?: boolean
}

function isMemHit(c: unknown): c is { id: string; type?: string; score?: number } {
  return typeof c === 'object' && c !== null && typeof (c as { id?: unknown }).id === 'string'
}

function toastLtmExtract(
  showToast: (msg: string, variant?: 'ok' | 'neutral') => void,
  written: unknown,
  updated: unknown,
) {
  const w = typeof written === 'number' ? written : 0
  const u = typeof updated === 'number' ? updated : 0
  if (w <= 0 && u <= 0) return
  if (w > 0 && u > 0) {
    showToast(`长期记忆：新增 ${w} 条，合并更新 ${u} 条`, 'ok')
  } else if (w > 0) {
    showToast(`长期记忆：已记录 ${w} 条`, 'ok')
  } else {
    showToast(`长期记忆：已合并更新 ${u} 条`, 'ok')
  }
}

function formatChatError(e: unknown): string {
  const base = getApiErrorMessage(e)
  if (e instanceof ApiCallError) {
    if (e.status === 429) {
      return `请求过于频繁或配额已用尽（429）。可稍后再试。\n${base}`
    }
    if (e.status === 502) {
      return `模型或上游服务异常（502）。请稍后重试。\n${base}`
    }
    if (e.status === 401) {
      return `鉴权失败（401）。请检查管理 Token 或 user_id。\n${base}`
    }
  }
  return base
}

function fmtMsgTime(ms?: number): ReactNode {
  if (ms == null) return null
  try {
    return <span className="text-[10px] text-[var(--text-muted)]">{new Date(ms).toLocaleString('zh-CN')}</span>
  } catch {
    return null
  }
}

function MessageBlock({ m }: { m: UiMsg }) {
  const [expanded, setExpanded] = useState(false)
  const long = m.content.length > COLLAPSE_CHARS
  const showFull = !long || expanded
  const preview = long && !expanded ? `${m.content.slice(0, COLLAPSE_CHARS)}…` : m.content

  const copyContent = async () => {
    try {
      await navigator.clipboard.writeText(m.content)
    } catch {
      /* ignore */
    }
  }

  return (
    <div
      className={`max-w-[min(100%,42rem)] rounded-2xl px-4 py-3 text-sm leading-relaxed shadow-sm ${
        m.role === 'user'
          ? 'bg-[color-mix(in_oklab,var(--brand)_18%,var(--surface))] text-[var(--text)]'
          : 'border border-[var(--border)] bg-[var(--surface)] text-[var(--text)]'
      }`}
    >
      <div className="mb-1 flex flex-wrap items-center justify-end gap-2">
        {fmtMsgTime(m.createdAt)}
        <button
          type="button"
          onClick={() => void copyContent()}
          className="text-[10px] text-[var(--accent)] hover:underline"
        >
          复制全文
        </button>
      </div>
      {m.role === 'assistant' && m.streaming ? (
        <p className="whitespace-pre-wrap">{m.content || '…'}</p>
      ) : m.role === 'assistant' && showFull ? (
        <ChatMarkdown content={m.content} />
      ) : (
        <p className="whitespace-pre-wrap">{preview}</p>
      )}
      {long ? (
        <button
          type="button"
          onClick={() => setExpanded((x) => !x)}
          className="mt-2 text-[11px] text-[var(--accent)] hover:underline"
        >
          {expanded ? '收起' : '展开全文'}
        </button>
      ) : null}
      {m.role === 'assistant' && !m.streaming && m.citations && m.citations.length > 0 ? (
        <div className="mt-3 border-t border-[var(--border)] pt-3">
          <p className="text-[10px] font-medium uppercase text-[var(--text-muted)]">引用记忆</p>
          <ul className="mt-2 space-y-2">
            {m.citations.map((c, i) =>
              isMemHit(c) ? (
                <li key={`${c.id}-${i}`}>
                  <Link
                    to={`/memory?ltm_id=${encodeURIComponent(c.id)}`}
                    className="block rounded-lg border border-[var(--border)] bg-[color-mix(in_oklab,var(--accent)_08%,var(--surface))] p-2 transition-colors hover:border-[var(--accent)]/40"
                  >
                    <span className="font-mono text-[11px] text-[var(--accent)]">{c.type ?? 'LTM'}</span>
                    <span className="ml-2 font-mono text-[10px] text-[var(--text-muted)]">{c.id.slice(0, 8)}…</span>
                    {typeof c.score === 'number' ? (
                      <span className="ml-2 text-[10px] text-[var(--text-muted)]">score {c.score.toFixed(3)}</span>
                    ) : null}
                    <span className="mt-1 block text-[10px] text-[var(--text-muted)]">在 Memory Studio 中打开 →</span>
                  </Link>
                </li>
              ) : (
                <li
                  key={i}
                  className="rounded-lg bg-[color-mix(in_oklab,var(--accent)_08%,var(--surface))] p-2 font-mono text-[11px] text-[var(--text-muted)]"
                >
                  {typeof c === 'object' && c !== null ? JSON.stringify(c) : String(c)}
                </li>
              ),
            )}
          </ul>
        </div>
      ) : null}
      {m.role === 'assistant' && !m.streaming && m.tool_summary && Object.keys(m.tool_summary).length > 0 ? (
        <div className="mt-3 border-t border-[var(--border)] pt-3">
          <p className="text-[10px] font-medium uppercase text-[var(--text-muted)]">工具调用</p>
          <dl className="mt-2 grid gap-1.5 font-mono text-[11px]">
            {Object.entries(m.tool_summary).map(([k, v]) => (
              <div
                key={k}
                className="flex flex-wrap gap-2 rounded-md bg-[color-mix(in_oklab,var(--surface)_90%,var(--border))] px-2 py-1"
              >
                <dt className="shrink-0 font-medium text-[var(--text)]">{k}</dt>
                <dd className="min-w-0 break-all text-[var(--text-muted)]">{String(v)}</dd>
              </div>
            ))}
          </dl>
        </div>
      ) : null}
    </div>
  )
}

function newId() {
  return crypto.randomUUID()
}

function shortId(s: string) {
  return s.length <= 12 ? s : `${s.slice(0, 8)}…`
}

export function ChatPage() {
  const { showToast } = useToast()
  const [userId, setUserId] = usePersistentString(LS_USER, 'demo-user')
  const [useStream, setUseStream] = usePersistentString(LS_STREAM, '1')
  const [sessionTitles, setSessionTitles] = useState<Record<string, string>>({})
  const [sessionId, setSessionIdState] = useState(readInitialSessionId)

  const setSessionId = useCallback((next: string) => {
    setSessionIdState(next)
    try {
      localStorage.setItem(LS_SESSION, next)
    } catch {
      /* ignore */
    }
  }, [])

  const [serverSessions, setServerSessions] = useState<{ session_id: string; message_count: number }[]>([])
  const [localOnlyIds, setLocalOnlyIds] = useState<string[]>([])
  const [messages, setMessages] = useState<UiMsg[]>([])
  const [draft, setDraft] = useState('')
  const [sending, setSending] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [lastFailedMessage, setLastFailedMessage] = useState<string | null>(null)
  const [lastTrace, setLastTrace] = useState<TraceRecordOut | null>(null)
  const [correction, setCorrection] = useState('')
  const [feedbackNote, setFeedbackNote] = useState<string | null>(null)
  const [fbLoading, setFbLoading] = useState(false)
  /** 本轮若隐式写入了 LTM，可用 trace_id 调用 undo_extract */
  const [undoExtractTraceId, setUndoExtractTraceId] = useState<string | null>(null)
  const [undoLtLoading, setUndoLtLoading] = useState(false)
  /** 异步隐式 LTM：轮询 Trace 合并结果的 timeout id */
  const ltmAsyncPollRef = useRef<ReturnType<typeof setTimeout> | null>(null)

  const clearLtmAsyncPoll = useCallback(() => {
    if (ltmAsyncPollRef.current != null) {
      clearTimeout(ltmAsyncPollRef.current)
      ltmAsyncPollRef.current = null
    }
  }, [])

  /** 后台抽取合并后：steps 会变长，或 decision 出现 written/updated/new_ids */
  const scheduleLtmAsyncTracePoll = useCallback(
    (traceId: string, userUid: string, baselineStepCount: number) => {
      clearLtmAsyncPoll()
      let attempt = 0
      const maxAttempts = 15
      const delayMs = 450

      const run = () => {
        ltmAsyncPollRef.current = null
        void (async () => {
          try {
            const tr = await getTrace(traceId, userUid)
            const nSteps = Array.isArray(tr.steps) ? tr.steps.length : 0
            const dec = tr.decision as Record<string, unknown>
            const ids = dec?.ltm_extract_new_ids
            const w = Number(dec?.ltm_extract_written ?? 0)
            const u = Number(dec?.ltm_extract_updated ?? 0)
            const merged =
              nSteps > baselineStepCount || w > 0 || u > 0 || (Array.isArray(ids) && ids.length > 0)
            if (merged) {
              setLastTrace(tr)
              if (Array.isArray(ids) && ids.length > 0) {
                setUndoExtractTraceId(traceId)
              }
              if (w > 0 || u > 0) {
                toastLtmExtract(showToast, w, u)
              }
              return
            }
          } catch {
            /* 单次失败忽略，靠后续重试 */
          }
          attempt += 1
          if (attempt < maxAttempts) {
            ltmAsyncPollRef.current = setTimeout(run, delayMs)
          }
        })()
      }
      ltmAsyncPollRef.current = setTimeout(run, delayMs)
    },
    [clearLtmAsyncPoll, showToast],
  )

  useEffect(() => () => clearLtmAsyncPoll(), [clearLtmAsyncPoll])

  const mergedSessions = useMemo(() => {
    const serverIds = new Set(serverSessions.map((s) => s.session_id))
    const localRows = localOnlyIds
      .filter((id) => !serverIds.has(id))
      .map((session_id) => ({ session_id, message_count: 0, local: true as const }))
    const serverRows = serverSessions.map((s) => ({ ...s, local: false as const }))
    const combined = [...localRows, ...serverRows]
    const seen = new Set(combined.map((c) => c.session_id))
    if (sessionId && !seen.has(sessionId)) {
      combined.unshift({ session_id: sessionId, message_count: 0, local: true })
    }
    return combined
  }, [serverSessions, localOnlyIds, sessionId])

  const refreshSessionList = useCallback(async () => {
    const uid = userId.trim() || 'default'
    const r = await getSessions(uid)
    setServerSessions(r.sessions)
  }, [userId])

  const loadTraceForSession = useCallback(
    async (sid: string) => {
      const uid = userId.trim() || 'default'
      try {
        const tr = await listTraces(uid, sid, 1)
        if (tr.items[0]) {
          setLastTrace(tr.items[0])
        } else {
          setLastTrace(null)
        }
      } catch {
        setLastTrace(null)
      }
    },
    [userId],
  )

  const loadMessagesForSession = useCallback(
    async (sid: string) => {
      const uid = userId.trim() || 'default'
      // 侧栏「未发送」会话：服务端尚无 STM key，请求会 404；直接展示空消息即可，避免刷日志
      const isLocalPending = mergedSessions.some((r) => r.session_id === sid && r.local)
      if (isLocalPending) {
        setMessages([])
        await loadTraceForSession(sid)
        return
      }
      try {
        const m = await getSessionMessages(uid, sid)
        setMessages(
          m.messages.map((x) => ({
            id: newId(),
            role: x.role === 'assistant' ? 'assistant' : 'user',
            content: x.content,
          })),
        )
      } catch (e) {
        if (e instanceof ApiCallError && e.status === 404) {
          setMessages([])
        } else {
          throw e
        }
      }
      await loadTraceForSession(sid)
    },
    [userId, loadTraceForSession, mergedSessions],
  )

  useEffect(() => {
    void refreshSessionList().catch(() => {})
  }, [refreshSessionList])

  useEffect(() => {
    setSessionTitles(loadSessionTitles(userId.trim() || 'default'))
  }, [userId])

  useEffect(() => {
    try {
      localStorage.setItem(LS_SESSION, sessionId)
    } catch {
      /* ignore */
    }
  }, [sessionId])

  useEffect(() => {
    const sid = sessionId.trim()
    if (!sid) return
    setError(null)
    setFeedbackNote(null)
    void (async () => {
      try {
        await loadMessagesForSession(sid)
      } catch (e) {
        setError(getApiErrorMessage(e))
      }
    })()
  }, [sessionId, userId, loadMessagesForSession])

  const startNewSession = () => {
    const id = crypto.randomUUID()
    setLocalOnlyIds((prev) => [...prev, id])
    setSessionId(id)
    setMessages([])
    setLastTrace(null)
    setError(null)
    setFeedbackNote(null)
  }

  const selectSession = (sid: string) => {
    if (sid === sessionId) return
    setSessionId(sid)
  }

  const renameSession = (sid: string) => {
    const uid = userId.trim() || 'default'
    const current = sessionTitles[sid] ?? ''
    const next = window.prompt('会话显示名称（仅本地保存）', current)
    if (next === null) return
    const t = next.trim()
    setSessionTitles((prev) => {
      const copy = { ...prev }
      if (t) copy[sid] = t
      else delete copy[sid]
      persistSessionTitles(uid, copy)
      return copy
    })
  }

  const removeSession = async (sid: string) => {
    const uid = userId.trim() || 'default'
    if (!window.confirm(`删除会话 ${shortId(sid)} ？将清空该会话短期记忆。`)) return
    setError(null)
    try {
      await deleteSession(uid, sid)
      setLocalOnlyIds((prev) => prev.filter((x) => x !== sid))
      await refreshSessionList()
      if (sid === sessionId) {
        startNewSession()
      }
    } catch (e) {
      setError(getApiErrorMessage(e))
    }
  }

  const sendMessage = async (textOverride?: string) => {
    const text = (textOverride ?? draft).trim()
    if (!text || sending) return
    const uid = userId.trim() || 'default'
    const sid = sessionId
    clearLtmAsyncPoll()
    setSending(true)
    setError(null)
    setLastFailedMessage(null)
    setFeedbackNote(null)
    setUndoExtractTraceId(null)
    const now = Date.now()
    const userMsg: UiMsg = { id: newId(), role: 'user', content: text, createdAt: now }
    setMessages((prev) => [...prev, userMsg])
    if (textOverride == null) setDraft('')
    const streamOn = useStream === '1' || useStream === 'true'
    const assistantId = newId()
    try {
      if (streamOn) {
        setMessages((prev) => [
          ...prev,
          {
            id: assistantId,
            role: 'assistant',
            content: '',
            streaming: true,
            createdAt: Date.now(),
          },
        ])
        const res = await postChatStream(
          { message: text, user_id: uid, session_id: sid },
          {
            onDelta: (chunk) => {
              setMessages((prev) =>
                prev.map((m) => (m.id === assistantId ? { ...m, content: m.content + chunk } : m)),
              )
            },
          },
        )
        setMessages((prev) =>
          prev.map((m) =>
            m.id === assistantId
              ? {
                  ...m,
                  streaming: false,
                  content: res.reply,
                  trace_id: res.trace_id,
                  citations: res.citations ?? null,
                  tool_summary: res.tool_summary ?? null,
                }
              : m,
          ),
        )
        setLocalOnlyIds((prev) => prev.filter((x) => x !== sid))
        await refreshSessionList()
        const tr = await getTrace(res.trace_id, uid)
        setLastTrace(tr)
        const baselineSteps = Array.isArray(tr.steps) ? tr.steps.length : 0
        if (res.quota_degraded) {
          showToast('本轮已启用配额省流（无 RAG 记忆注入）', 'neutral')
        }
        if (res.ltm_extract_async_pending) {
          showToast(
            '长期记忆：隐式抽取已入队后台处理，侧栏将自动刷新 Trace；也可手动点「刷新 Trace」',
            'neutral',
          )
          scheduleLtmAsyncTracePoll(res.trace_id, uid, baselineSteps)
        }
        toastLtmExtract(showToast, res.ltm_extract_written, res.ltm_extract_updated)
        if (Array.isArray(res.ltm_extract_new_ids) && res.ltm_extract_new_ids.length > 0) {
          setUndoExtractTraceId(res.trace_id)
        }
      } else {
        const res: ChatResponse = await postChat({
          message: text,
          user_id: uid,
          session_id: sid,
        })
        setMessages((prev) => [
          ...prev,
          {
            id: newId(),
            role: 'assistant',
            content: res.reply,
            trace_id: res.trace_id,
            citations: res.citations ?? null,
            tool_summary: res.tool_summary ?? null,
            createdAt: Date.now(),
          },
        ])
        setLocalOnlyIds((prev) => prev.filter((x) => x !== sid))
        await refreshSessionList()
        const tr = await getTrace(res.trace_id, uid)
        setLastTrace(tr)
        const baselineSteps = Array.isArray(tr.steps) ? tr.steps.length : 0
        if (res.quota_degraded) {
          showToast('本轮已启用配额省流（无 RAG 记忆注入）', 'neutral')
        }
        if (res.ltm_extract_async_pending) {
          showToast(
            '长期记忆：隐式抽取已入队后台处理，侧栏将自动刷新 Trace；也可手动点「刷新 Trace」',
            'neutral',
          )
          scheduleLtmAsyncTracePoll(res.trace_id, uid, baselineSteps)
        }
        toastLtmExtract(showToast, res.ltm_extract_written, res.ltm_extract_updated)
        if (Array.isArray(res.ltm_extract_new_ids) && res.ltm_extract_new_ids.length > 0) {
          setUndoExtractTraceId(res.trace_id)
        }
      }
    } catch (e) {
      setError(formatChatError(e))
      setLastFailedMessage(text)
      setMessages((prev) =>
        prev.filter((m) => m.id !== userMsg.id && (!streamOn || m.id !== assistantId)),
      )
    } finally {
      setSending(false)
    }
  }

  const undoLastLtmExtract = async () => {
    if (!undoExtractTraceId) return
    const uid = userId.trim() || 'default'
    setUndoLtLoading(true)
    setError(null)
    try {
      const r = await postLtmUndoExtract({ trace_id: undoExtractTraceId, user_id: uid })
      setUndoExtractTraceId(null)
      showToast(`已撤销本轮隐式记忆（${r.deactivated} 条）`, 'ok')
    } catch (e) {
      setError(getApiErrorMessage(e))
    } finally {
      setUndoLtLoading(false)
    }
  }

  const submitFeedback = async (rating: 'like' | 'dislike') => {
    const trId = lastTrace?.trace_id
    if (!trId) return
    const uid = userId.trim() || 'default'
    setFbLoading(true)
    setFeedbackNote(null)
    try {
      const corr = correction.trim() || null
      await postFeedback({
        trace_id: trId,
        user_id: uid,
        rating,
        correction: corr,
      })
      const note = rating === 'like' ? '已记录：点赞' : '已记录：点踩'
      setFeedbackNote(note)
      showToast(note, 'ok')
      if (rating === 'dislike' || corr) setCorrection('')
    } catch (e) {
      setError(getApiErrorMessage(e))
    } finally {
      setFbLoading(false)
    }
  }

  const copyTrace = async () => {
    const id = lastTrace?.trace_id
    if (!id) return
    try {
      await navigator.clipboard.writeText(id)
      setFeedbackNote('trace_id 已复制')
    } catch {
      setFeedbackNote('复制失败，请手动选择')
    }
  }

  const decision = lastTrace?.decision ?? {}
  const metrics = lastTrace?.metrics ?? {}
  const emotion = (decision.emotion ?? null) as Record<string, unknown> | null

  return (
    <div className="flex h-[calc(100dvh-56px-48px)] min-h-[480px] flex-col gap-4 lg:h-[calc(100dvh-56px-3rem)] lg:flex-row">
      {/* 会话列 */}
      <aside className="flex w-full min-w-[11rem] max-w-[22rem] shrink-0 flex-col overflow-auto rounded-2xl border border-[var(--border)] bg-[var(--surface-2)] lg:h-auto lg:max-w-[26rem] lg:resize-x">
        <div className="border-b border-[var(--border)] p-3">
          <label className="text-[10px] font-medium uppercase tracking-wide text-[var(--text-muted)]">user_id</label>
          <p className="mt-0.5 text-[9px] leading-tight text-[var(--text-muted)]">
            修改后将影响会话隔离、记忆与 Trace 归属；与运营台、Memory 共用同一标识。
          </p>
          <input
            value={userId}
            onChange={(e) => setUserId(e.target.value)}
            className="mt-1 w-full rounded-lg border border-[var(--border)] bg-[var(--surface)] px-2 py-1.5 text-xs text-[var(--text)]"
          />
          <label className="mt-3 flex cursor-pointer items-center gap-2 text-[10px] text-[var(--text-muted)]">
            <input
              type="checkbox"
              className="rounded border-[var(--border)]"
              checked={useStream === '1' || useStream === 'true'}
              onChange={(e) => setUseStream(e.target.checked ? '1' : '0')}
            />
            流式输出（SSE）
          </label>
          <button
            type="button"
            onClick={startNewSession}
            className="mt-2 w-full rounded-lg bg-[var(--brand)] py-2 text-xs font-medium text-white hover:bg-[var(--brand-hover)]"
          >
            新对话
          </button>
        </div>
        <div className="min-h-0 flex-1 overflow-y-auto p-2">
          <p className="mb-2 px-1 text-[10px] text-[var(--text-muted)]">会话</p>
          <ul className="space-y-1">
            {mergedSessions.map((row) => (
              <li key={row.session_id} className="group flex items-center gap-1">
                <button
                  type="button"
                  onClick={() => selectSession(row.session_id)}
                  className={`min-w-0 flex-1 rounded-lg px-2 py-2 text-left text-xs transition-colors ${
                    row.session_id === sessionId
                      ? 'bg-[color-mix(in_oklab,var(--brand)_14%,transparent)] text-[var(--text)]'
                      : 'text-[var(--text-muted)] hover:bg-[color-mix(in_oklab,var(--surface)_80%,var(--border))]'
                  }`}
                >
                  <span className="block truncate text-left font-mono text-[11px]">
                    {sessionTitles[row.session_id]?.trim() || shortId(row.session_id)}
                  </span>
                  <span className="text-[10px] text-[var(--text-muted)]">
                    {row.local ? '未发送' : `${row.message_count} 条`}
                  </span>
                </button>
                <button
                  type="button"
                  title="重命名"
                  onClick={() => renameSession(row.session_id)}
                  className="shrink-0 rounded px-0.5 py-1 text-[10px] text-[var(--text-muted)] opacity-0 transition-opacity hover:text-[var(--accent)] group-hover:opacity-100"
                >
                  ✎
                </button>
                <button
                  type="button"
                  title="删除"
                  onClick={() => removeSession(row.session_id)}
                  className="shrink-0 rounded p-1 text-[var(--text-muted)] opacity-0 transition-opacity hover:text-[var(--danger)] group-hover:opacity-100"
                >
                  ×
                </button>
              </li>
            ))}
          </ul>
        </div>
      </aside>

      {/* 消息区 */}
      <section className="flex min-h-0 min-w-0 flex-1 flex-col rounded-2xl border border-[var(--border)] bg-[var(--surface-2)]">
        <div className="min-h-0 flex-1 space-y-4 overflow-y-auto p-4">
          {messages.length === 0 ? (
            <p className="text-center text-sm text-[var(--text-muted)]">开始说话吧，我会认真听。</p>
          ) : (
            messages.map((m) => (
              <div key={m.id} className={`flex ${m.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                <MessageBlock m={m} />
              </div>
            ))
          )}
        </div>
        {error ? (
          <div className="border-t border-[var(--danger)]/30 bg-[color-mix(in_oklab,var(--danger)_06%,var(--surface-2))] px-4 py-3 text-xs text-[var(--danger)]">
            <div className="flex flex-wrap items-start justify-between gap-3">
              <p className="min-w-0 flex-1 whitespace-pre-wrap">{error}</p>
              <div className="flex shrink-0 flex-wrap gap-2">
                {lastFailedMessage ? (
                  <button
                    type="button"
                    disabled={sending}
                    onClick={() => void sendMessage(lastFailedMessage)}
                    className="rounded-lg border border-[var(--danger)]/40 bg-[var(--surface)] px-3 py-1.5 text-[11px] font-medium text-[var(--danger)] hover:bg-[color-mix(in_oklab,var(--danger)_08%,var(--surface))] disabled:opacity-50"
                  >
                    重试上一次
                  </button>
                ) : null}
                <button
                  type="button"
                  onClick={() => {
                    setError(null)
                    setLastFailedMessage(null)
                  }}
                  className="rounded-lg border border-[var(--border)] px-3 py-1.5 text-[11px] text-[var(--text-muted)] hover:bg-[var(--surface)]"
                >
                  关闭
                </button>
              </div>
            </div>
          </div>
        ) : null}
        <div className="border-t border-[var(--border)] p-3">
          <textarea
            value={draft}
            onChange={(e) => setDraft(e.target.value)}
            rows={3}
            placeholder="输入消息，Enter 发送（Shift+Enter 换行）"
            className="w-full resize-none rounded-xl border border-[var(--border)] bg-[var(--surface)] px-3 py-2 text-sm text-[var(--text)] placeholder:text-[var(--text-muted)] focus:border-[var(--brand)] focus:outline-none focus-visible:ring-2 focus-visible:ring-[var(--ring)]"
            onKeyDown={(e) => {
              if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault()
                void sendMessage()
              }
            }}
          />
          <div className="mt-2 flex justify-end gap-2">
            <button
              type="button"
              disabled={sending || !draft.trim()}
              onClick={() => void sendMessage()}
              className="rounded-lg bg-[var(--brand)] px-4 py-2 text-sm font-medium text-white disabled:opacity-50 hover:bg-[var(--brand-hover)]"
            >
              {sending ? '发送中…' : '发送'}
            </button>
          </div>
        </div>
      </section>

      {/* 诊断 + 反馈 */}
      <aside className="flex w-full shrink-0 flex-col gap-3 lg:w-72">
        <div className="rounded-2xl border border-[var(--border)] bg-[var(--surface-2)] p-4">
          <h3 className="font-display text-sm text-[var(--text)]">诊断</h3>
          {lastTrace ? (
            <dl className="mt-3 space-y-2 text-xs text-[var(--text-muted)]">
              <div>
                <dt className="font-medium text-[var(--text)]">trace_id</dt>
                <dd className="mt-0.5 break-all font-mono text-[11px]">{lastTrace.trace_id}</dd>
                <div className="mt-1 flex flex-wrap gap-x-3 gap-y-1">
                  <button
                    type="button"
                    onClick={() => void copyTrace()}
                    className="text-[11px] text-[var(--accent)] hover:underline"
                  >
                    复制
                  </button>
                  <Link
                    to={`/trace?id=${encodeURIComponent(lastTrace.trace_id)}`}
                    className="text-[11px] text-[var(--accent)] hover:underline"
                  >
                    Trace 回放
                  </Link>
                  <button
                    type="button"
                    onClick={() => {
                      void (async () => {
                        const tid = lastTrace.trace_id
                        const uid = userId.trim() || 'default'
                        try {
                          const tr = await getTrace(tid, uid)
                          setLastTrace(tr)
                          const dec = tr.decision as Record<string, unknown>
                          const ids = dec?.ltm_extract_new_ids
                          if (Array.isArray(ids) && ids.length > 0) {
                            setUndoExtractTraceId(tid)
                          }
                        } catch (err) {
                          setError(getApiErrorMessage(err))
                        }
                      })()
                    }}
                    className="text-[11px] text-[var(--accent)] hover:underline"
                  >
                    刷新 Trace
                  </button>
                </div>
              </div>
              <div>
                <dt className="font-medium text-[var(--text)]">情绪 / 风险</dt>
                <dd>
                  {emotion
                    ? `${String(emotion.label ?? '')} · 强度 ${String(emotion.intensity ?? '')} · ${String(emotion.risk_tier ?? '')}`
                    : '—'}
                </dd>
              </div>
              <div>
                <dt className="font-medium text-[var(--text)]">模式</dt>
                <dd>{String(decision.mode ?? '—')}</dd>
              </div>
              {decision.degraded_mode === true ? (
                <div className="rounded-lg border border-[color-mix(in_oklab,var(--accent)_30%,var(--border))] bg-[color-mix(in_oklab,var(--accent)_10%,var(--surface))] px-2 py-2 text-[11px] leading-snug text-[var(--text)]">
                  配额省流：本轮已去掉 RAG 记忆块并完成回复（trace 中 <code className="font-mono">quota_exceeded</code> 与{' '}
                  <code className="font-mono">degraded_mode</code> 为真）。
                </div>
              ) : null}
              <div>
                <dt className="font-medium text-[var(--text)]">延迟 / Token</dt>
                <dd>
                  {String(metrics.latency_ms ?? '—')} ms · in/out {String(metrics.token_in ?? '—')} /{' '}
                  {String(metrics.token_out ?? '—')}
                </dd>
              </div>
              <div>
                <dt className="font-medium text-[var(--text)]">模型</dt>
                <dd className="break-all">{String(metrics.model ?? '—')}</dd>
              </div>
            </dl>
          ) : (
            <p className="mt-3 text-xs text-[var(--text-muted)]">发送一条消息后，将展示本轮 Trace 摘要。</p>
          )}
        </div>

        <div className="rounded-2xl border border-[var(--border)] bg-[var(--surface-2)] p-4">
          <h3 className="font-display text-sm text-[var(--text)]">反馈</h3>
          <p className="mt-1 text-[11px] text-[var(--text-muted)]">关联最近一次 Trace（本会话最后一轮）。</p>
          <textarea
            value={correction}
            onChange={(e) => setCorrection(e.target.value)}
            rows={2}
            placeholder="可选：写下期望的回复或纠错"
            className="mt-2 w-full rounded-lg border border-[var(--border)] bg-[var(--surface)] px-2 py-1.5 text-xs text-[var(--text)]"
          />
          <div className="mt-2 flex flex-wrap gap-2">
            <button
              type="button"
              disabled={!lastTrace || fbLoading}
              onClick={() => void submitFeedback('like')}
              className="min-w-[5rem] flex-1 rounded-lg border border-[var(--border)] py-2 text-xs font-medium hover:bg-[var(--surface)] disabled:opacity-40"
            >
              点赞
            </button>
            <button
              type="button"
              disabled={!lastTrace || fbLoading}
              onClick={() => void submitFeedback('dislike')}
              className="min-w-[5rem] flex-1 rounded-lg border border-[var(--border)] py-2 text-xs font-medium hover:bg-[var(--surface)] disabled:opacity-40"
            >
              点踩
            </button>
            <button
              type="button"
              disabled={!undoExtractTraceId || undoLtLoading}
              onClick={() => void undoLastLtmExtract()}
              title="撤销本轮对话自动写入的长期记忆（dialogue_extract）"
              className="w-full rounded-lg border border-[color-mix(in_oklab,var(--accent)_35%,var(--border))] py-2 text-xs font-medium text-[var(--text)] hover:bg-[color-mix(in_oklab,var(--accent)_8%,var(--surface))] disabled:opacity-40 sm:w-auto sm:flex-1"
            >
              {undoLtLoading ? '撤销中…' : '撤销本轮隐式记忆'}
            </button>
          </div>
          {feedbackNote ? <p className="mt-2 text-xs text-[var(--ok)]">{feedbackNote}</p> : null}
        </div>
      </aside>
    </div>
  )
}
