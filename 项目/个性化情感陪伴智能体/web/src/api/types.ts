/** 与后端 `ChatRequest` / `ChatResponse` 对齐（OpenAPI 同步后可改为生成类型） */

export type ChatRequest = {
  message: string
  user_id?: string | null
  session_id?: string | null
}

export type ChatResponse = {
  reply: string
  trace_id: string
  user_id: string
  session_id: string
  debug?: Record<string, unknown> | null
  citations?: unknown[] | null
  tool_summary?: Record<string, unknown> | null
  /** 日配额触顶后走省流降级（去 RAG）完成本轮 */
  quota_degraded?: boolean
  /** V1.1：本轮隐式写入 LTM 条数 */
  ltm_extract_written?: number
  /** V1.1 P1：本轮因相似合并更新的 LTM 条数 */
  ltm_extract_updated?: number
  /** V1.1 P1：本轮抽取新建的 LTM id，可 undo_extract */
  ltm_extract_new_ids?: string[]
  /** V1.1 P2：抽取已异步排队，本响应中 ltm 计数可能仍为 0 */
  ltm_extract_async_pending?: boolean
}

export type HealthResponse = {
  status?: string
  /** REDIS_URL 未配置 skipped；配置且连通 ok；失败 error */
  redis?: string
  /** DATABASE_URL 未配置 skipped；配置且连通 ok；失败 error */
  database?: string
  /** V1.1：LTM_EXTRACT_ENABLED，隐式记忆抽取总开关 */
  ltm_extract_enabled?: boolean
}

/** FastAPI HTTPException / 校验错误常见形态 */
export type FastAPIValidationItem = {
  loc?: (string | number)[]
  msg: string
  type?: string
}

export type FastAPIErrorBody = {
  detail: string | FastAPIValidationItem[]
}

export type SessionItemOut = {
  session_id: string
  message_count: number
}

export type SessionListResponse = {
  user_id: string
  sessions: SessionItemOut[]
}

export type ChatMessageOut = {
  role: string
  content: string
}

export type SessionMessagesResponse = {
  user_id: string
  session_id: string
  messages: ChatMessageOut[]
}

export type TraceRecordOut = {
  trace_id: string
  user_id: string
  session_id: string
  message: string
  timestamp_ms: number
  steps: unknown[]
  decision: Record<string, unknown>
  metrics: Record<string, unknown>
}

export type TraceListResponse = {
  items: TraceRecordOut[]
}

export type FeedbackRequest = {
  trace_id: string
  user_id?: string | null
  rating: 'like' | 'dislike'
  correction?: string | null
}

export type FeedbackResponse = {
  ok: boolean
  feedback_id: string
  mirrored_to_eval?: boolean
}

export type LTMTypeName = 'Preference' | 'Profile' | 'Event' | 'Constraint'

export type LTMItemOut = {
  id: string
  user_id: string
  type: string
  content: string
  created_at: number
  source: string
  confidence: number
  tags: string[]
  is_active: boolean
  updated_at: number
  embedding_status: string
}

export type LTMListResponse = {
  items: LTMItemOut[]
  total: number
  offset: number
  limit: number
}

export type LTMWriteRequest = {
  user_id: string
  type: string
  content: string
  source?: string
  confidence?: number
  tags?: string[]
}

export type LTMUndoExtractRequest = {
  trace_id: string
  user_id?: string | null
}

export type LTMUndoExtractResponse = {
  ok: boolean
  trace_id: string
  deactivated: number
}

export type LTMPatchRequest = {
  content?: string
  confidence?: number
  tags?: string[] | null
  is_active?: boolean | null
}

export type EvalRunRequest = {
  dataset: 'upload' | 'builtin'
  jsonl?: string | null
  user_id?: string | null
  limit?: number
}

export type EvalRunResponse = {
  job_id: string
  total: number
}

export type EvalJobStatusResponse = {
  job_id: string
  status: string
  progress: number
  total: number
  results: Record<string, unknown>[]
  error?: string | null
  summary?: Record<string, unknown> | null
}

export type EmotionSeriesPoint = {
  bucket: string
  count: number
}

export type AdminHotConfigSnapshot = {
  rag_enabled: boolean
  rag_top_k: number
  rag_min_score: number
  rag_max_chars: number
  rag_use_hybrid: boolean
  rag_bm25_top_k: number
  rag_rewrite_enabled: boolean
  rag_rewrite_min_score: number
  tool_enabled: boolean
  quota_enabled: boolean
  quota_token_per_user_per_day: number
  quota_qps_per_user: number
  stm_max_chars: number
  content_safety_enabled: boolean
  content_safety_filter_output: boolean
  feedback_enabled: boolean
  quota_degrade_on_exhaust: boolean
  quota_degrade_system_hint: string
  ltm_extract_enabled: boolean
  ltm_extract_every_n_turns: number
  ltm_extract_dedup_enabled: boolean
  ltm_extract_count_toward_quota: boolean
  ltm_extract_async: boolean
}

/** PATCH body：与后端一致，可只传要改的字段 */
export type AdminHotConfigPatch = Partial<AdminHotConfigSnapshot>

export type AdminQuotaResponse = {
  user_id: string
  quota_enabled: boolean
  used_today: number
  limit_per_day: number
  qps_per_user: number
}

export type UserForgetResponse = {
  ok: boolean
  user_id: string
  ltm_deactivated: number
  stm_sessions_cleared: number
}

export type FeedbackItemOut = {
  id: string
  trace_id: string
  user_id: string
  rating: string
  correction?: string | null
  timestamp_ms: number
  session_id?: string | null
}

export type FeedbackListResponse = {
  items: FeedbackItemOut[]
}

export type AdminRiskEventsResponse = {
  items: Array<Record<string, unknown>>
  storage: string
  note: string
  count: number
}

export type FeedbackExportResponse = {
  format: string
  line_count: number
  content: string
}

export type EmotionStatsResponse = {
  user_id: string
  emotion_log_enabled: boolean
  log_file: string
  log_file_exists: boolean
  window: 'day' | 'week'
  record_count: number
  by_label: Record<string, number>
  by_risk_tier: Record<string, number>
  series: EmotionSeriesPoint[]
  disclaimer: string
  hint?: string | null
}
