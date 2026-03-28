import { useCallback, useEffect, useMemo, useState } from 'react'
import { useSearchParams } from 'react-router-dom'
import { getApiErrorMessage, getTrace } from '../api/client'
import type { TraceRecordOut } from '../api/types'
import { usePersistentString } from '../hooks/usePersistentString'

const LS_USER = 'companion_user_id'

type StepBucket = 'all' | 'rag' | 'tool' | 'quota' | 'safety' | 'other'

function stepBucket(name: string): Exclude<StepBucket, 'all'> {
  const n = name.toLowerCase()
  if (n.includes('retrieve') || n.includes('ltm') || n.includes('rewrite')) return 'rag'
  if (n.includes('tool')) return 'tool'
  if (n.includes('quota')) return 'quota'
  if (n.includes('safety') || n.includes('content_safety')) return 'safety'
  return 'other'
}

type StepRow = {
  name: string
  start_ms: number
  end_ms: number
  input_summary?: string | null
  output_summary?: string | null
  error?: string | null
}

function asSteps(raw: unknown[]): StepRow[] {
  return raw.map((x) => {
    const o = x as Record<string, unknown>
    return {
      name: String(o.name ?? ''),
      start_ms: Number(o.start_ms ?? 0),
      end_ms: Number(o.end_ms ?? 0),
      input_summary: o.input_summary as string | null | undefined,
      output_summary: o.output_summary as string | null | undefined,
      error: o.error as string | null | undefined,
    }
  })
}

const FILTERS: { key: StepBucket; label: string }[] = [
  { key: 'all', label: '全部' },
  { key: 'rag', label: 'RAG / 检索' },
  { key: 'tool', label: '工具' },
  { key: 'quota', label: '配额' },
  { key: 'safety', label: '安全' },
  { key: 'other', label: '其他' },
]

export function TraceViewerPage() {
  const [searchParams] = useSearchParams()
  const [userId, setUserId] = usePersistentString(LS_USER, 'demo-user')
  const [traceId, setTraceId] = useState(() => searchParams.get('id')?.trim() ?? '')
  const [filter, setFilter] = useState<StepBucket>('all')
  const [trace, setTrace] = useState<TraceRecordOut | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [copied, setCopied] = useState(false)

  useEffect(() => {
    const id = searchParams.get('id')?.trim()
    if (id) setTraceId(id)
  }, [searchParams])

  const load = useCallback(async () => {
    const id = traceId.trim()
    if (!id) {
      setError('请填写 trace_id')
      return
    }
    setLoading(true)
    setError(null)
    setTrace(null)
    try {
      const uid = userId.trim() || undefined
      const t = await getTrace(id, uid)
      setTrace(t)
    } catch (e) {
      setError(getApiErrorMessage(e))
    } finally {
      setLoading(false)
    }
  }, [traceId, userId])

  const steps = useMemo(() => (trace ? asSteps(trace.steps) : []), [trace])

  const filteredSteps = useMemo(() => {
    if (filter === 'all') return steps
    return steps.filter((s) => stepBucket(s.name) === filter)
  }, [steps, filter])

  const copyFull = async () => {
    if (!trace) return
    try {
      await navigator.clipboard.writeText(JSON.stringify(trace, null, 2))
      setCopied(true)
      window.setTimeout(() => setCopied(false), 2000)
    } catch {
      setCopied(false)
    }
  }

  return (
    <div className="mx-auto max-w-4xl space-y-5">
      <header className="rounded-2xl border border-[var(--border)] bg-[var(--surface-2)] p-5">
        <h2 className="font-display text-xl text-[var(--text)]">Trace 回放</h2>
        <p className="mt-1 text-sm text-[var(--text-muted)]">
          拉取完整链路步骤与 decision/metrics。URL 可带参数 <code className="text-xs">?id=trace_id</code>。
        </p>
        <div className="mt-4 flex flex-wrap gap-3">
          <div className="min-w-[200px] flex-1">
            <label htmlFor="tv-tid" className="text-xs text-[var(--text-muted)]">
              trace_id
            </label>
            <input
              id="tv-tid"
              value={traceId}
              onChange={(e) => setTraceId(e.target.value)}
              className="mt-1 w-full rounded-lg border border-[var(--border)] bg-[var(--surface)] px-3 py-2 font-mono text-sm"
              placeholder="uuid"
            />
          </div>
          <div className="w-40">
            <label htmlFor="tv-uid" className="text-xs text-[var(--text-muted)]">
              user_id（隔离校验）
            </label>
            <input
              id="tv-uid"
              value={userId}
              onChange={(e) => setUserId(e.target.value)}
              className="mt-1 w-full rounded-lg border border-[var(--border)] bg-[var(--surface)] px-3 py-2 text-sm"
            />
          </div>
          <div className="flex items-end">
            <button
              type="button"
              disabled={loading}
              onClick={() => void load()}
              className="rounded-lg bg-[var(--brand)] px-4 py-2 text-sm font-medium text-white disabled:opacity-50"
            >
              {loading ? '加载中…' : '加载'}
            </button>
          </div>
        </div>
      </header>

      {error ? (
        <div className="rounded-xl border border-[var(--danger)]/40 bg-[color-mix(in_oklab,var(--danger)_08%,var(--surface-2))] px-4 py-3 text-sm text-[var(--danger)]">
          {error}
        </div>
      ) : null}

      {trace ? (
        <>
          <section className="rounded-2xl border border-[var(--border)] bg-[var(--surface-2)] p-5">
            <div className="flex flex-wrap items-center justify-between gap-2">
              <h3 className="text-sm font-medium text-[var(--text)]">步骤时间线</h3>
              <button
                type="button"
                onClick={() => void copyFull()}
                className="rounded-lg border border-[var(--border)] px-3 py-1 text-xs"
              >
                {copied ? '已复制 JSON' : '复制完整 JSON'}
              </button>
            </div>
            <div className="mt-3 flex flex-wrap gap-2">
              {FILTERS.map((f) => (
                <button
                  key={f.key}
                  type="button"
                  onClick={() => setFilter(f.key)}
                  className={`rounded-full px-3 py-1 text-xs ${
                    filter === f.key
                      ? 'bg-[var(--accent)] text-white'
                      : 'border border-[var(--border)] text-[var(--text-muted)]'
                  }`}
                >
                  {f.label}
                </button>
              ))}
            </div>
            <ul className="mt-4 space-y-3 border-l-2 border-[var(--border)] pl-4">
              {filteredSteps.length === 0 ? (
                <li className="text-sm text-[var(--text-muted)]">当前筛选下无步骤</li>
              ) : (
                filteredSteps.map((s, i) => {
                  const dur = Math.max(0, s.end_ms - s.start_ms)
                  return (
                    <li key={`${s.name}-${i}`} className="relative text-sm">
                      <span className="absolute -left-[calc(1rem+5px)] top-1.5 h-2 w-2 rounded-full bg-[var(--brand)]" />
                      <p className="font-mono text-xs text-[var(--brand)]">{s.name}</p>
                      <p className="text-[11px] text-[var(--text-muted)]">
                        {s.start_ms}–{s.end_ms} ms（Δ {dur} ms）
                      </p>
                      {s.input_summary ? (
                        <p className="mt-1 text-xs text-[var(--text-muted)]">in: {s.input_summary}</p>
                      ) : null}
                      {s.output_summary ? (
                        <p className="text-xs text-[var(--text-muted)]">out: {s.output_summary}</p>
                      ) : null}
                      {s.error ? <p className="text-xs text-[var(--danger)]">err: {s.error}</p> : null}
                    </li>
                  )
                })
              )}
            </ul>
          </section>

          <details className="rounded-2xl border border-[var(--border)] bg-[var(--surface-2)] p-5">
            <summary className="cursor-pointer text-sm font-medium text-[var(--text)]">decision / metrics</summary>
            <pre className="mt-3 max-h-64 overflow-auto rounded-lg bg-[var(--surface)] p-3 font-mono text-[11px] text-[var(--text-muted)]">
              {JSON.stringify({ decision: trace.decision, metrics: trace.metrics }, null, 2)}
            </pre>
          </details>

          <details className="rounded-2xl border border-[var(--border)] bg-[var(--surface-2)] p-5">
            <summary className="cursor-pointer text-sm font-medium text-[var(--text)]">请求摘要</summary>
            <pre className="mt-3 max-h-48 overflow-auto rounded-lg bg-[var(--surface)] p-3 font-mono text-[11px]">
              {JSON.stringify(
                {
                  trace_id: trace.trace_id,
                  user_id: trace.user_id,
                  session_id: trace.session_id,
                  timestamp_ms: trace.timestamp_ms,
                  message: trace.message,
                },
                null,
                2,
              )}
            </pre>
          </details>
        </>
      ) : null}
    </div>
  )
}
