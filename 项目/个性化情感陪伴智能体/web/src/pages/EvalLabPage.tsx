import { useEffect, useRef, useState } from 'react'
import { getApiErrorMessage, getEvalJob, postEvalRun } from '../api/client'
import type { EvalJobStatusResponse, EvalRunRequest } from '../api/types'
import { usePersistentString } from '../hooks/usePersistentString'

const LS_ADMIN = 'companion_admin_token'
const LS_EVAL_USER = 'eval_lab_user'

const SAMPLE_JSONL = `{"message": "你好"}
{"message": "今天有点累"}
`

function downloadText(filename: string, content: string, mime: string) {
  const blob = new Blob([content], { type: mime })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = filename
  a.click()
  URL.revokeObjectURL(url)
}

function resultsToCsv(rows: Record<string, unknown>[]): string {
  if (!rows.length) return ''
  const keys = [...new Set(rows.flatMap((r) => Object.keys(r)))]
  const esc = (v: unknown) => {
    const s = v === null || v === undefined ? '' : typeof v === 'object' ? JSON.stringify(v) : String(v)
    if (/[",\n\r]/.test(s)) return `"${s.replace(/"/g, '""')}"`
    return s
  }
  return [keys.join(','), ...rows.map((r) => keys.map((k) => esc(r[k])).join(','))].join('\n')
}

export function EvalLabPage() {
  const [adminToken, setAdminToken] = usePersistentString(LS_ADMIN, '')
  const [evalUserId, setEvalUserId] = usePersistentString(LS_EVAL_USER, 'eval_lab_user')
  const [dataset, setDataset] = useState<'builtin' | 'upload'>('builtin')
  const [jsonl, setJsonl] = useState(SAMPLE_JSONL)
  const [limit, setLimit] = useState(30)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [jobId, setJobId] = useState<string | null>(null)
  const [status, setStatus] = useState<EvalJobStatusResponse | null>(null)
  const pollRef = useRef<number | null>(null)

  useEffect(() => {
    return () => {
      if (pollRef.current != null) window.clearInterval(pollRef.current)
    }
  }, [])

  const tokenOpt = adminToken.trim() || undefined

  const startRun = async () => {
    setError(null)
    setStatus(null)
    setBusy(true)
    if (pollRef.current != null) {
      window.clearInterval(pollRef.current)
      pollRef.current = null
    }
    try {
      const body: EvalRunRequest = {
        dataset,
        user_id: evalUserId.trim() || null,
        limit,
        jsonl: dataset === 'upload' ? jsonl : null,
      }
      const r = await postEvalRun(body, tokenOpt)
      setJobId(r.job_id)

      const poll = async () => {
        try {
          const s = await getEvalJob(r.job_id, tokenOpt)
          setStatus(s)
          if (s.status === 'done' || s.status === 'failed') {
            if (pollRef.current != null) window.clearInterval(pollRef.current)
            pollRef.current = null
            setBusy(false)
          }
        } catch (e) {
          setError(getApiErrorMessage(e))
          if (pollRef.current != null) window.clearInterval(pollRef.current)
          pollRef.current = null
          setBusy(false)
        }
      }
      await poll()
      pollRef.current = window.setInterval(poll, 900)
    } catch (e) {
      setError(getApiErrorMessage(e))
      setBusy(false)
    }
  }

  const summary = status?.summary as Record<string, number> | undefined
  const progressPct =
    status && status.total > 0 ? Math.round((100 * status.progress) / status.total) : 0

  return (
    <div className="mx-auto max-w-5xl space-y-5">
      <header className="rounded-2xl border border-[var(--border)] bg-[var(--surface-2)] p-5">
        <h2 className="font-display text-xl text-[var(--text)]">Eval Lab</h2>
        <p className="mt-1 text-sm text-[var(--text-muted)]">
          异步跑批评测：逐条调用与对话相同的 /chat 链路。每条使用独立 session，避免 STM 串话。
        </p>
        <p className="mt-2 rounded-lg bg-[color-mix(in_oklab,var(--brand)_08%,var(--surface))] px-3 py-2 text-xs text-[var(--text-muted)]">
          <strong className="text-[var(--text)]">注意</strong>：真实环境会消耗 LLM
          Token。若服务端配置了 <code className="text-[11px]">ADMIN_CONFIG_TOKEN</code>，请在下方填写{' '}
          <code className="text-[11px]">X-Admin-Token</code>；本机未配置时通常可直接调用。
        </p>

        <div className="mt-4 grid gap-3 sm:grid-cols-2">
          <div>
            <label htmlFor="eval-admin" className="text-xs font-medium text-[var(--text-muted)]">
              X-Admin-Token（可选）
            </label>
            <input
              id="eval-admin"
              type="password"
              value={adminToken}
              onChange={(e) => setAdminToken(e.target.value)}
              className="mt-1 w-full rounded-lg border border-[var(--border)] bg-[var(--surface)] px-3 py-2 text-sm"
              autoComplete="off"
            />
          </div>
          <div>
            <label htmlFor="eval-user" className="text-xs font-medium text-[var(--text-muted)]">
              评测 user_id（隔离 STM）
            </label>
            <input
              id="eval-user"
              value={evalUserId}
              onChange={(e) => setEvalUserId(e.target.value)}
              className="mt-1 w-full rounded-lg border border-[var(--border)] bg-[var(--surface)] px-3 py-2 text-sm"
            />
          </div>
        </div>

        <fieldset className="mt-4 space-y-2">
          <legend className="text-xs font-medium text-[var(--text-muted)]">数据集</legend>
          <label className="mr-4 inline-flex items-center gap-2 text-sm">
            <input
              type="radio"
              name="ds"
              checked={dataset === 'builtin'}
              onChange={() => setDataset('builtin')}
            />
            内置（data/eval_builtin.jsonl）
          </label>
          <label className="inline-flex items-center gap-2 text-sm">
            <input
              type="radio"
              name="ds"
              checked={dataset === 'upload'}
              onChange={() => setDataset('upload')}
            />
            粘贴 JSONL
          </label>
        </fieldset>

        {dataset === 'upload' ? (
          <div className="mt-3">
            <label htmlFor="eval-jsonl" className="text-xs text-[var(--text-muted)]">
              JSONL（每行一个 JSON，须含 <code className="text-[11px]">message</code>）
            </label>
            <textarea
              id="eval-jsonl"
              value={jsonl}
              onChange={(e) => setJsonl(e.target.value)}
              rows={8}
              className="mt-1 w-full rounded-lg border border-[var(--border)] bg-[var(--surface)] px-3 py-2 font-mono text-xs"
            />
          </div>
        ) : null}

        <div className="mt-3 flex flex-wrap items-end gap-3">
          <div>
            <label htmlFor="eval-limit" className="text-xs text-[var(--text-muted)]">
              最多条数（1–200）
            </label>
            <input
              id="eval-limit"
              type="number"
              min={1}
              max={200}
              value={limit}
              onChange={(e) => setLimit(Number(e.target.value) || 1)}
              className="mt-1 w-24 rounded-lg border border-[var(--border)] bg-[var(--surface)] px-3 py-2 text-sm"
            />
          </div>
          <button
            type="button"
            disabled={busy}
            onClick={() => void startRun()}
            className="rounded-lg bg-[var(--brand)] px-5 py-2 text-sm font-medium text-white disabled:opacity-50 hover:bg-[var(--brand-hover)]"
          >
            {busy ? '运行中…' : '开始跑批'}
          </button>
        </div>
      </header>

      {error ? (
        <div className="rounded-xl border border-[var(--danger)]/40 bg-[color-mix(in_oklab,var(--danger)_08%,var(--surface-2))] px-4 py-3 text-sm text-[var(--danger)]">
          {error}
        </div>
      ) : null}

      {jobId ? (
        <section className="rounded-2xl border border-[var(--border)] bg-[var(--surface-2)] p-5">
          <p className="font-mono text-xs text-[var(--text-muted)]">
            job_id: <span className="text-[var(--text)]">{jobId}</span>
          </p>
          {status ? (
            <>
              <div className="mt-3 flex items-center gap-3">
                <span className="text-sm text-[var(--text)]">状态：{status.status}</span>
                <span className="text-xs text-[var(--text-muted)]">
                  {status.progress}/{status.total}
                </span>
              </div>
              <div className="mt-2 h-2 w-full overflow-hidden rounded-full bg-[var(--border)]">
                <div
                  className="h-full bg-[var(--brand)] transition-[width] duration-300"
                  style={{ width: `${progressPct}%` }}
                />
              </div>
              {status.error ? (
                <p className="mt-3 text-sm text-[var(--danger)]">{status.error}</p>
              ) : null}
              {summary ? (
                <div className="mt-4 grid gap-3 sm:grid-cols-3">
                  <div className="rounded-xl border border-[var(--border)] bg-[var(--surface)] p-3 text-center">
                    <p className="text-2xl font-semibold text-[var(--ok)]">{summary.success ?? 0}</p>
                    <p className="text-xs text-[var(--text-muted)]">成功</p>
                  </div>
                  <div className="rounded-xl border border-[var(--border)] bg-[var(--surface)] p-3 text-center">
                    <p className="text-2xl font-semibold text-[var(--danger)]">{summary.failed ?? 0}</p>
                    <p className="text-xs text-[var(--text-muted)]">失败</p>
                  </div>
                  <div className="rounded-xl border border-[var(--border)] bg-[var(--surface)] p-3 text-center">
                    <p className="text-2xl font-semibold text-[var(--text)]">{summary.avg_latency_ms_ok ?? 0}</p>
                    <p className="text-xs text-[var(--text-muted)]">成功样本平均延迟 ms</p>
                  </div>
                </div>
              ) : null}
              {status.status === 'done' && status.results.length > 0 ? (
                <div className="mt-4 flex flex-wrap gap-2">
                  <button
                    type="button"
                    onClick={() =>
                      downloadText(`eval-${jobId}.json`, JSON.stringify(status.results, null, 2), 'application/json')
                    }
                    className="rounded-lg border border-[var(--border)] px-3 py-1.5 text-xs"
                  >
                    导出 JSON
                  </button>
                  <button
                    type="button"
                    onClick={() => downloadText(`eval-${jobId}.csv`, resultsToCsv(status.results), 'text/csv')}
                    className="rounded-lg border border-[var(--border)] px-3 py-1.5 text-xs"
                  >
                    导出 CSV
                  </button>
                </div>
              ) : null}
              <div className="mt-4 overflow-x-auto">
                <table className="w-full min-w-[640px] border-collapse text-left text-xs">
                  <thead>
                    <tr className="border-b border-[var(--border)] text-[var(--text-muted)]">
                      <th className="py-2 pr-2">#</th>
                      <th className="py-2 pr-2">ok</th>
                      <th className="py-2 pr-2">message</th>
                      <th className="py-2 pr-2">trace_id</th>
                      <th className="py-2 pr-2">ms</th>
                      <th className="py-2">备注</th>
                    </tr>
                  </thead>
                  <tbody>
                    {status.results.map((row, i) => {
                      const r = row as Record<string, unknown>
                      return (
                        <tr key={i} className="border-b border-[var(--border)]/80">
                          <td className="py-2 pr-2 font-mono">{String(r.index ?? i)}</td>
                          <td className="py-2 pr-2">{r.ok === true ? '✓' : '×'}</td>
                          <td className="max-w-[200px] truncate py-2 pr-2" title={String(r.message ?? '')}>
                            {String(r.message ?? '')}
                          </td>
                          <td className="max-w-[120px] truncate py-2 pr-2 font-mono text-[10px]">
                            {String(r.trace_id ?? '—')}
                          </td>
                          <td className="py-2 pr-2">{String(r.latency_ms ?? '—')}</td>
                          <td className="max-w-[240px] truncate py-2 text-[var(--danger)]" title={String(r.error ?? r.reply_preview ?? '')}>
                            {String(r.error ?? r.reply_preview ?? '')}
                          </td>
                        </tr>
                      )
                    })}
                  </tbody>
                </table>
              </div>
            </>
          ) : (
            <p className="mt-2 text-sm text-[var(--text-muted)]">等待任务状态…</p>
          )}
        </section>
      ) : null}
    </div>
  )
}
