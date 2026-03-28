import { useCallback, useEffect, useState } from 'react'
import { getApiErrorMessage, getEmotionStats } from '../api/client'
import type { EmotionStatsResponse } from '../api/types'
import { usePersistentString } from '../hooks/usePersistentString'

const LS_USER = 'companion_user_id'

export function EmotionDashboardPage() {
  const [userId, setUserId] = usePersistentString(LS_USER, 'demo-user')
  const [windowMode, setWindowMode] = useState<'day' | 'week'>('week')
  const [view, setView] = useState<'chart' | 'table'>('chart')
  const [data, setData] = useState<EmotionStatsResponse | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const load = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const r = await getEmotionStats(userId.trim() || 'default', windowMode)
      setData(r)
    } catch (e) {
      setError(getApiErrorMessage(e))
      setData(null)
    } finally {
      setLoading(false)
    }
  }, [userId, windowMode])

  useEffect(() => {
    void load()
  }, [load])

  const maxSeries = data ? Math.max(1, ...data.series.map((s) => s.count)) : 1

  return (
    <div className="mx-auto max-w-4xl space-y-5">
      <section className="rounded-2xl border border-[var(--border)] border-amber-700/25 bg-[color-mix(in_oklab,oklch(0.75 0.12 75)_12%,var(--surface-2))] p-4 text-sm leading-relaxed text-[var(--text)]">
        <strong className="text-amber-900 dark:text-amber-200">免责声明</strong>
        <p className="mt-2 text-[var(--text-muted)]">
          {data?.disclaimer ??
            '以下为对话情绪标签的统计展示，不构成心理健康或医学诊断；如有需要请咨询专业机构。'}
        </p>
      </section>

      <header className="rounded-2xl border border-[var(--border)] bg-[var(--surface-2)] p-5">
        <h2 className="font-display text-xl text-[var(--text)]">情绪仪表盘</h2>
        <p className="mt-1 text-sm text-[var(--text-muted)]">
          数据来自服务端情绪日志（JSONL）。时间轴为 <span className="font-mono">UTC</span> 整点/日历日。
        </p>
        <div className="mt-4 flex flex-wrap items-end gap-3">
          <div>
            <label htmlFor="emo-user" className="text-xs text-[var(--text-muted)]">
              user_id
            </label>
            <input
              id="emo-user"
              value={userId}
              onChange={(e) => setUserId(e.target.value)}
              className="mt-1 w-48 rounded-lg border border-[var(--border)] bg-[var(--surface)] px-3 py-2 text-sm"
            />
          </div>
          <div>
            <span className="text-xs text-[var(--text-muted)]">时间窗</span>
            <div className="mt-1 flex rounded-lg border border-[var(--border)] p-0.5">
              {(['week', 'day'] as const).map((w) => (
                <button
                  key={w}
                  type="button"
                  onClick={() => setWindowMode(w)}
                  className={`rounded-md px-3 py-1.5 text-xs ${
                    windowMode === w ? 'bg-[var(--brand)] text-white' : 'text-[var(--text-muted)]'
                  }`}
                >
                  {w === 'week' ? '近 7 日' : '近 24 小时'}
                </button>
              ))}
            </div>
          </div>
          <div>
            <span className="text-xs text-[var(--text-muted)]">展示</span>
            <div className="mt-1 flex rounded-lg border border-[var(--border)] p-0.5">
              {(['chart', 'table'] as const).map((v) => (
                <button
                  key={v}
                  type="button"
                  onClick={() => setView(v)}
                  className={`rounded-md px-3 py-1.5 text-xs ${
                    view === v ? 'bg-[var(--accent)] text-white' : 'text-[var(--text-muted)]'
                  }`}
                >
                  {v === 'chart' ? '图表' : '表格'}
                </button>
              ))}
            </div>
          </div>
          <button
            type="button"
            onClick={() => void load()}
            className="rounded-lg border border-[var(--border)] px-3 py-2 text-xs"
          >
            刷新
          </button>
        </div>
        <p className="mt-3 text-[11px] text-[var(--text-muted)]">
          日志文件：{data?.log_file ?? '…'} · 存在：{data ? (data.log_file_exists ? '是' : '否') : '—'} ·
          落盘开关：{data ? (data.emotion_log_enabled ? '开' : '关') : '—'}
        </p>
      </header>

      {error ? (
        <div className="rounded-xl border border-[var(--danger)]/40 bg-[color-mix(in_oklab,var(--danger)_08%,var(--surface-2))] px-4 py-3 text-sm text-[var(--danger)]">
          {error}
        </div>
      ) : null}

      {loading ? (
        <div className="animate-pulse space-y-3 rounded-2xl border border-[var(--border)] p-6">
          <div className="h-6 w-1/3 rounded bg-[var(--border)]" />
          <div className="h-40 rounded bg-[var(--border)]" />
        </div>
      ) : data ? (
        <>
          {data.hint ? (
            <div className="rounded-xl border border-[var(--border)] bg-[var(--surface-2)] px-4 py-3 text-sm text-[var(--text-muted)]">
              {data.hint}
            </div>
          ) : null}

          {view === 'chart' ? (
            <section className="rounded-2xl border border-[var(--border)] bg-[var(--surface-2)] p-5">
              <h3 className="text-sm font-medium text-[var(--text)]">条数趋势</h3>
              <div className="mt-4 flex h-48 items-end gap-1 border-b border-[var(--border)] pb-1">
                {data.series.map((s) => (
                  <div key={s.bucket} className="flex min-w-0 flex-1 flex-col items-center gap-1">
                    <div
                      className="w-full max-w-[2rem] rounded-t bg-[color-mix(in_oklab,var(--brand)_85%,transparent)] transition-[height] duration-300"
                      style={{ height: `${(100 * s.count) / maxSeries}%`, minHeight: s.count > 0 ? '4px' : '0' }}
                      title={`${s.bucket}: ${s.count}`}
                    />
                    <span className="max-w-full truncate text-center text-[9px] text-[var(--text-muted)]">
                      {windowMode === 'week' ? s.bucket.slice(5) : s.bucket.slice(11, 13) + 'h'}
                    </span>
                  </div>
                ))}
              </div>
            </section>
          ) : (
            <section className="rounded-2xl border border-[var(--border)] bg-[var(--surface-2)] p-5">
              <h3 className="text-sm font-medium text-[var(--text)]">时间桶明细</h3>
              <div className="mt-3 overflow-x-auto">
                <table className="w-full text-left text-xs">
                  <thead>
                    <tr className="border-b border-[var(--border)] text-[var(--text-muted)]">
                      <th className="py-2">bucket</th>
                      <th className="py-2">count</th>
                    </tr>
                  </thead>
                  <tbody>
                    {data.series.map((s) => (
                      <tr key={s.bucket} className="border-b border-[var(--border)]/60">
                        <td className="py-1.5 font-mono">{s.bucket}</td>
                        <td className="py-1.5">{s.count}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </section>
          )}

          <div className="grid gap-4 sm:grid-cols-2">
            <section className="rounded-2xl border border-[var(--border)] bg-[var(--surface-2)] p-5">
              <h3 className="text-sm font-medium text-[var(--text)]">情绪标签</h3>
              <ul className="mt-3 space-y-2 text-sm">
                {Object.entries(data.by_label).length === 0 ? (
                  <li className="text-[var(--text-muted)]">无</li>
                ) : (
                  Object.entries(data.by_label).map(([k, v]) => (
                    <li key={k} className="flex justify-between gap-2">
                      <span>{k}</span>
                      <span className="font-mono text-[var(--text-muted)]">{v}</span>
                    </li>
                  ))
                )}
              </ul>
            </section>
            <section className="rounded-2xl border border-[var(--border)] bg-[var(--surface-2)] p-5">
              <h3 className="text-sm font-medium text-[var(--text)]">风险分层</h3>
              <ul className="mt-3 space-y-2 text-sm">
                {Object.entries(data.by_risk_tier).length === 0 ? (
                  <li className="text-[var(--text-muted)]">无</li>
                ) : (
                  Object.entries(data.by_risk_tier).map(([k, v]) => (
                    <li key={k} className="flex justify-between gap-2">
                      <span>{k}</span>
                      <span className="font-mono text-[var(--text-muted)]">{v}</span>
                    </li>
                  ))
                )}
              </ul>
            </section>
          </div>

          <p className="text-center text-xs text-[var(--text-muted)]">当前窗内记录数：{data.record_count}</p>
        </>
      ) : null}
    </div>
  )
}
