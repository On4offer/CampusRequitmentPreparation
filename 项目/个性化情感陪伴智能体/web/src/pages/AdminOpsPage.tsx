import { useCallback, useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import {
  fetchUserExportJson,
  getAdminConfig,
  getAdminQuota,
  getAdminRiskEvents,
  getApiErrorMessage,
  getFeedbackExport,
  getFeedbackRecent,
  patchAdminConfig,
  postUserForget,
} from '../api/client'
import type {
  AdminHotConfigSnapshot,
  AdminQuotaResponse,
  AdminRiskEventsResponse,
  FeedbackItemOut,
} from '../api/types'
import { usePersistentString } from '../hooks/usePersistentString'

const LS_ADMIN = 'companion_admin_token'
const LS_USER = 'companion_user_id'

type Tab = 'config' | 'quota' | 'feedback' | 'risk' | 'compliance'

function fmtTs(ms: number) {
  try {
    return new Date(ms).toLocaleString('zh-CN')
  } catch {
    return String(ms)
  }
}

function downloadBlob(filename: string, content: string, mime: string) {
  const blob = new Blob([content], { type: mime })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = filename
  a.click()
  URL.revokeObjectURL(url)
}

function BoolField({
  label,
  checked,
  onChange,
}: {
  label: string
  checked: boolean
  onChange: (v: boolean) => void
}) {
  return (
    <label className="flex cursor-pointer items-center gap-2 text-sm">
      <input type="checkbox" checked={checked} onChange={(e) => onChange(e.target.checked)} className="rounded" />
      <span className="text-[var(--text)]">{label}</span>
    </label>
  )
}

function NumField({
  label,
  value,
  onChange,
  step,
}: {
  label: string
  value: number
  onChange: (v: number) => void
  step?: string
}) {
  return (
    <div>
      <label className="text-xs text-[var(--text-muted)]">{label}</label>
      <input
        type="number"
        step={step ?? '1'}
        value={Number.isNaN(value) ? '' : value}
        onChange={(e) => onChange(parseFloat(e.target.value) || 0)}
        className="mt-1 w-full rounded-lg border border-[var(--border)] bg-[var(--surface)] px-3 py-2 text-sm"
      />
    </div>
  )
}

export function AdminOpsPage() {
  const [adminToken, setAdminToken] = usePersistentString(LS_ADMIN, '')
  const [userId, setUserId] = usePersistentString(LS_USER, 'demo-user')
  const [tab, setTab] = useState<Tab>('config')

  const [configDraft, setConfigDraft] = useState<AdminHotConfigSnapshot | null>(null)
  const [quota, setQuota] = useState<AdminQuotaResponse | null>(null)
  const [feedbackItems, setFeedbackItems] = useState<FeedbackItemOut[]>([])
  const [risk, setRisk] = useState<AdminRiskEventsResponse | null>(null)

  const [fbLimit, setFbLimit] = useState(40)
  const [fbUserFilter, setFbUserFilter] = useState('')
  const [riskLimit, setRiskLimit] = useState(30)

  const [forgetConfirm, setForgetConfirm] = useState(false)
  const [forgetClearStm, setForgetClearStm] = useState(true)

  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [toast, setToast] = useState<string | null>(null)

  const tokenOpt = adminToken.trim() || undefined

  const showToast = (msg: string) => {
    setToast(msg)
    window.setTimeout(() => setToast(null), 3200)
  }

  const loadConfig = useCallback(async () => {
    setError(null)
    const c = await getAdminConfig(tokenOpt)
    setConfigDraft(c)
  }, [tokenOpt])

  const loadQuota = useCallback(async () => {
    setError(null)
    const q = await getAdminQuota(userId.trim() || undefined, tokenOpt)
    setQuota(q)
  }, [userId, tokenOpt])

  const loadFeedback = useCallback(async () => {
    setError(null)
    const r = await getFeedbackRecent(
      fbLimit,
      fbUserFilter.trim() || undefined,
    )
    setFeedbackItems(r.items)
  }, [fbLimit, fbUserFilter])

  const loadRisk = useCallback(async () => {
    setError(null)
    const r = await getAdminRiskEvents(riskLimit, tokenOpt)
    setRisk(r)
  }, [riskLimit, tokenOpt])

  /** 切换 Tab 时拉一次；反馈/配额筛选项改后请点「刷新」 */
  useEffect(() => {
    if (tab === 'compliance') {
      setLoading(false)
      return
    }
    let cancelled = false
    void (async () => {
      setLoading(true)
      setError(null)
      try {
        if (tab === 'config') {
          const c = await getAdminConfig(tokenOpt)
          if (!cancelled) setConfigDraft(c)
        } else if (tab === 'quota') {
          const q = await getAdminQuota(userId.trim() || undefined, tokenOpt)
          if (!cancelled) setQuota(q)
        } else if (tab === 'feedback') {
          const r = await getFeedbackRecent(
            fbLimit,
            fbUserFilter.trim() || undefined,
          )
          if (!cancelled) setFeedbackItems(r.items)
        } else if (tab === 'risk') {
          const r = await getAdminRiskEvents(riskLimit, tokenOpt)
          if (!cancelled) setRisk(r)
        }
      } catch (e) {
        if (!cancelled) setError(getApiErrorMessage(e))
      } finally {
        if (!cancelled) setLoading(false)
      }
    })()
    return () => {
      cancelled = true
    }
  }, [tab, tokenOpt, userId, riskLimit]) // eslint-disable-line react-hooks/exhaustive-deps -- 反馈 limit/过滤改后点「刷新列表」，避免 deps 含 fbLimit、fbUserFilter

  const applyConfig = async () => {
    if (!configDraft) return
    setLoading(true)
    setError(null)
    try {
      const next = await patchAdminConfig(configDraft, tokenOpt)
      setConfigDraft(next)
      showToast('热参数已应用并写入服务端')
    } catch (e) {
      setError(getApiErrorMessage(e))
    } finally {
      setLoading(false)
    }
  }

  const exportFeedback = async () => {
    setLoading(true)
    setError(null)
    try {
      const r = await getFeedbackExport(Math.min(2000, fbLimit * 5), fbUserFilter.trim() || undefined)
      downloadBlob(`feedback-export-${Date.now()}.jsonl`, r.content, 'application/x-ndjson')
      showToast(`已导出 ${r.line_count} 行`)
    } catch (e) {
      setError(getApiErrorMessage(e))
    } finally {
      setLoading(false)
    }
  }

  const exportUserPackage = async () => {
    const uid = userId.trim() || 'default'
    setLoading(true)
    setError(null)
    try {
      const text = await fetchUserExportJson(uid, tokenOpt)
      const safe = uid.replace(/[^\w.-]+/g, '_').slice(0, 80) || 'user'
      downloadBlob(`user-export-${safe}.json`, text, 'application/json')
      showToast('已下载用户数据导出 JSON')
    } catch (e) {
      setError(getApiErrorMessage(e))
    } finally {
      setLoading(false)
    }
  }

  const runUserForget = async () => {
    if (!forgetConfirm) {
      setError('请先勾选「我已知悉后果」再执行遗忘。')
      return
    }
    const uid = userId.trim() || 'default'
    setLoading(true)
    setError(null)
    try {
      const r = await postUserForget(uid, { confirm: true, clear_stm: forgetClearStm }, tokenOpt)
      showToast(`已处理：LTM 软删 ${r.ltm_deactivated} 条；STM 清空 ${r.stm_sessions_cleared} 个会话`)
      setForgetConfirm(false)
    } catch (e) {
      setError(getApiErrorMessage(e))
    } finally {
      setLoading(false)
    }
  }

  const tabBtn = (t: Tab, label: string) => (
    <button
      type="button"
      onClick={() => setTab(t)}
      className={`rounded-lg px-4 py-2 text-sm font-medium transition-colors ${
        tab === t ? 'bg-[var(--brand)] text-white' : 'text-[var(--text-muted)] hover:bg-[var(--surface)]'
      }`}
    >
      {label}
    </button>
  )

  return (
    <div className="mx-auto max-w-4xl space-y-5">
      <header className="rounded-2xl border border-[var(--border)] bg-[var(--surface-2)] p-5">
        <h2 className="font-display text-xl text-[var(--text)]">运营台</h2>
        <p className="mt-1 text-sm text-[var(--text-muted)]">
          热参数、配额、反馈与风险事件；与 Gradio 运营台同源接口。若配置了{' '}
          <code className="text-xs">ADMIN_CONFIG_TOKEN</code> 须填写 Token；本机访问通常可直接调用 admin 接口。
        </p>
        <div className="mt-4 flex flex-wrap gap-3">
          <div className="min-w-[200px] flex-1">
            <label htmlFor="ops-token" className="text-xs text-[var(--text-muted)]">
              X-Admin-Token
            </label>
            <input
              id="ops-token"
              type="password"
              value={adminToken}
              onChange={(e) => setAdminToken(e.target.value)}
              className="mt-1 w-full rounded-lg border border-[var(--border)] bg-[var(--surface)] px-3 py-2 text-sm"
              autoComplete="off"
            />
          </div>
          <div className="min-w-[140px]">
            <label htmlFor="ops-uid" className="text-xs text-[var(--text-muted)]">
              默认 user_id（配额）
            </label>
            <input
              id="ops-uid"
              value={userId}
              onChange={(e) => setUserId(e.target.value)}
              className="mt-1 w-full rounded-lg border border-[var(--border)] bg-[var(--surface)] px-3 py-2 text-sm"
            />
          </div>
        </div>
        <p className="mt-3 text-xs text-[var(--text-muted)]">
          评测跑批见 <Link to="/eval" className="text-[var(--accent)] hover:underline">Eval Lab</Link>
        </p>
      </header>

      {toast ? (
        <div className="rounded-lg border border-[var(--ok)]/40 bg-[color-mix(in_oklab,var(--ok)_10%,var(--surface-2))] px-4 py-2 text-sm text-[var(--ok)]">
          {toast}
        </div>
      ) : null}

      {error ? (
        <div className="rounded-xl border border-[var(--danger)]/40 bg-[color-mix(in_oklab,var(--danger)_08%,var(--surface-2))] px-4 py-3 text-sm text-[var(--danger)]">
          {error}
        </div>
      ) : null}

      <div className="flex flex-wrap items-center gap-2 border-b border-[var(--border)] pb-3">
        {tabBtn('config', '热参数')}
        {tabBtn('quota', '配额')}
        {tabBtn('feedback', '反馈')}
        {tabBtn('risk', '风险事件')}
        {tabBtn('compliance', '合规')}
        {loading ? (
          <span className="ml-2 text-xs text-[var(--text-muted)]">加载中…</span>
        ) : null}
      </div>

      {tab === 'config' && !configDraft ? (
        <p className="text-sm text-[var(--text-muted)]">正在拉取热参数…</p>
      ) : null}

      {tab === 'config' && configDraft ? (
        <section className="space-y-6 rounded-2xl border border-[var(--border)] bg-[var(--surface-2)] p-5">
          <div className="flex flex-wrap items-center justify-between gap-2">
            <h3 className="text-sm font-medium text-[var(--text)]">热参数（PATCH /admin/config）</h3>
            <button
              type="button"
              disabled={loading}
              onClick={() => void loadConfig().catch((e) => setError(getApiErrorMessage(e)))}
              className="text-xs text-[var(--accent)] hover:underline"
            >
              重新拉取
            </button>
          </div>

          <div className="space-y-4">
            <p className="text-xs font-medium uppercase text-[var(--text-muted)]">RAG</p>
            <div className="grid gap-3 sm:grid-cols-2">
              <BoolField
                label="rag_enabled"
                checked={configDraft.rag_enabled}
                onChange={(v) => setConfigDraft({ ...configDraft, rag_enabled: v })}
              />
              <BoolField
                label="rag_use_hybrid"
                checked={configDraft.rag_use_hybrid}
                onChange={(v) => setConfigDraft({ ...configDraft, rag_use_hybrid: v })}
              />
              <BoolField
                label="rag_rewrite_enabled"
                checked={configDraft.rag_rewrite_enabled}
                onChange={(v) => setConfigDraft({ ...configDraft, rag_rewrite_enabled: v })}
              />
              <NumField
                label="rag_top_k"
                value={configDraft.rag_top_k}
                onChange={(v) => setConfigDraft({ ...configDraft, rag_top_k: Math.round(v) })}
              />
              <NumField
                label="rag_bm25_top_k"
                value={configDraft.rag_bm25_top_k}
                onChange={(v) => setConfigDraft({ ...configDraft, rag_bm25_top_k: Math.round(v) })}
              />
              <NumField
                label="rag_min_score"
                value={configDraft.rag_min_score}
                onChange={(v) => setConfigDraft({ ...configDraft, rag_min_score: v })}
                step="0.01"
              />
              <NumField
                label="rag_rewrite_min_score"
                value={configDraft.rag_rewrite_min_score}
                onChange={(v) => setConfigDraft({ ...configDraft, rag_rewrite_min_score: v })}
                step="0.01"
              />
              <NumField
                label="rag_max_chars"
                value={configDraft.rag_max_chars}
                onChange={(v) => setConfigDraft({ ...configDraft, rag_max_chars: Math.round(v) })}
              />
            </div>
          </div>

          <div className="space-y-3">
            <p className="text-xs font-medium uppercase text-[var(--text-muted)]">工具 / 配额 / STM</p>
            <div className="grid gap-3 sm:grid-cols-2">
              <BoolField
                label="tool_enabled"
                checked={configDraft.tool_enabled}
                onChange={(v) => setConfigDraft({ ...configDraft, tool_enabled: v })}
              />
              <BoolField
                label="quota_enabled"
                checked={configDraft.quota_enabled}
                onChange={(v) => setConfigDraft({ ...configDraft, quota_enabled: v })}
              />
              <NumField
                label="quota_token_per_user_per_day"
                value={configDraft.quota_token_per_user_per_day}
                onChange={(v) => setConfigDraft({ ...configDraft, quota_token_per_user_per_day: Math.round(v) })}
              />
              <NumField
                label="quota_qps_per_user"
                value={configDraft.quota_qps_per_user}
                onChange={(v) => setConfigDraft({ ...configDraft, quota_qps_per_user: v })}
                step="0.1"
              />
              <BoolField
                label="quota_degrade_on_exhaust"
                checked={configDraft.quota_degrade_on_exhaust}
                onChange={(v) => setConfigDraft({ ...configDraft, quota_degrade_on_exhaust: v })}
              />
              <div className="sm:col-span-2">
                <label htmlFor="ops-degrade-hint" className="text-xs text-[var(--text-muted)]">
                  quota_degrade_system_hint（空则用内置短提示）
                </label>
                <textarea
                  id="ops-degrade-hint"
                  value={configDraft.quota_degrade_system_hint}
                  onChange={(e) => setConfigDraft({ ...configDraft, quota_degrade_system_hint: e.target.value })}
                  rows={2}
                  className="mt-1 w-full rounded-lg border border-[var(--border)] bg-[var(--surface)] px-3 py-2 text-sm"
                />
              </div>
              <NumField
                label="stm_max_chars"
                value={configDraft.stm_max_chars}
                onChange={(v) => setConfigDraft({ ...configDraft, stm_max_chars: Math.round(v) })}
              />
            </div>
          </div>

          <div className="space-y-3">
            <p className="text-xs font-medium uppercase text-[var(--text-muted)]">安全 / 反馈</p>
            <div className="grid gap-3 sm:grid-cols-2">
              <BoolField
                label="content_safety_enabled"
                checked={configDraft.content_safety_enabled}
                onChange={(v) => setConfigDraft({ ...configDraft, content_safety_enabled: v })}
              />
              <BoolField
                label="content_safety_filter_output"
                checked={configDraft.content_safety_filter_output}
                onChange={(v) => setConfigDraft({ ...configDraft, content_safety_filter_output: v })}
              />
              <BoolField
                label="feedback_enabled"
                checked={configDraft.feedback_enabled}
                onChange={(v) => setConfigDraft({ ...configDraft, feedback_enabled: v })}
              />
            </div>
          </div>

          <div className="space-y-3">
            <p className="text-xs font-medium uppercase text-[var(--text-muted)]">隐式 LTM（V1.1）</p>
            <p className="text-[11px] text-[var(--text-muted)]">
              与 <code className="font-mono">LTM_EXTRACT_*</code> 环境变量一致；热更新后立即作用于下一轮{' '}
              <code className="font-mono">/chat</code>。<code className="font-mono">ltm_extract_every_n_turns=0</code>{' '}
              表示不按 assistant 条数触发抽取。
            </p>
            <div className="grid gap-3 sm:grid-cols-2">
              <BoolField
                label="ltm_extract_enabled"
                checked={configDraft.ltm_extract_enabled}
                onChange={(v) => setConfigDraft({ ...configDraft, ltm_extract_enabled: v })}
              />
              <BoolField
                label="ltm_extract_dedup_enabled"
                checked={configDraft.ltm_extract_dedup_enabled}
                onChange={(v) => setConfigDraft({ ...configDraft, ltm_extract_dedup_enabled: v })}
              />
              <BoolField
                label="ltm_extract_count_toward_quota"
                checked={configDraft.ltm_extract_count_toward_quota}
                onChange={(v) => setConfigDraft({ ...configDraft, ltm_extract_count_toward_quota: v })}
              />
              <BoolField
                label="ltm_extract_async"
                checked={configDraft.ltm_extract_async}
                onChange={(v) => setConfigDraft({ ...configDraft, ltm_extract_async: v })}
              />
              <NumField
                label="ltm_extract_every_n_turns"
                value={configDraft.ltm_extract_every_n_turns}
                onChange={(v) => setConfigDraft({ ...configDraft, ltm_extract_every_n_turns: Math.round(v) })}
              />
            </div>
          </div>

          <button
            type="button"
            disabled={loading}
            onClick={() => void applyConfig()}
            className="rounded-lg bg-[var(--brand)] px-5 py-2.5 text-sm font-medium text-white disabled:opacity-50"
          >
            应用全部当前表单值
          </button>
          <p className="text-[11px] text-[var(--text-muted)]">
            后端会校验范围（如 rag_top_k 1–50、ltm_extract_every_n_turns 0–20）；非法值将返回 400。
          </p>
        </section>
      ) : null}

      {tab === 'quota' ? (
        <section className="rounded-2xl border border-[var(--border)] bg-[var(--surface-2)] p-5">
          <div className="flex flex-wrap items-center justify-between gap-2">
            <h3 className="text-sm font-medium text-[var(--text)]">配额快照</h3>
            <button
              type="button"
              disabled={loading}
              onClick={() => {
                void (async () => {
                  setLoading(true)
                  setError(null)
                  try {
                    await loadQuota()
                  } catch (e) {
                    setError(getApiErrorMessage(e))
                  } finally {
                    setLoading(false)
                  }
                })()
              }}
              className="rounded-lg border border-[var(--border)] px-3 py-1.5 text-xs"
            >
              刷新
            </button>
          </div>
          {quota ? (
            <dl className="mt-4 grid gap-2 text-sm sm:grid-cols-2">
              <div>
                <dt className="text-[var(--text-muted)]">user_id</dt>
                <dd className="font-mono">{quota.user_id}</dd>
              </div>
              <div>
                <dt className="text-[var(--text-muted)]">quota_enabled</dt>
                <dd>{quota.quota_enabled ? '是' : '否'}</dd>
              </div>
              <div>
                <dt className="text-[var(--text-muted)]">used_today</dt>
                <dd>{quota.used_today}</dd>
              </div>
              <div>
                <dt className="text-[var(--text-muted)]">limit_per_day</dt>
                <dd>{quota.limit_per_day}</dd>
              </div>
              <div>
                <dt className="text-[var(--text-muted)]">qps_per_user</dt>
                <dd>{quota.qps_per_user}</dd>
              </div>
            </dl>
          ) : (
            <p className="mt-4 text-sm text-[var(--text-muted)]">点击刷新加载</p>
          )}
        </section>
      ) : null}

      {tab === 'feedback' ? (
        <section className="rounded-2xl border border-[var(--border)] bg-[var(--surface-2)] p-5">
          <div className="flex flex-wrap items-end gap-3">
            <div>
              <label className="text-xs text-[var(--text-muted)]">limit</label>
              <input
                type="number"
                min={1}
                max={500}
                value={fbLimit}
                onChange={(e) => setFbLimit(Number(e.target.value) || 30)}
                className="mt-1 w-20 rounded-lg border border-[var(--border)] bg-[var(--surface)] px-2 py-1.5 text-sm"
              />
            </div>
            <div className="min-w-[140px]">
              <label className="text-xs text-[var(--text-muted)]">user_id 过滤（可选）</label>
              <input
                value={fbUserFilter}
                onChange={(e) => setFbUserFilter(e.target.value)}
                className="mt-1 w-full rounded-lg border border-[var(--border)] bg-[var(--surface)] px-3 py-1.5 text-sm"
              />
            </div>
            <button
              type="button"
              disabled={loading}
              onClick={() => {
                void (async () => {
                  setLoading(true)
                  setError(null)
                  try {
                    await loadFeedback()
                  } catch (e) {
                    setError(getApiErrorMessage(e))
                  } finally {
                    setLoading(false)
                  }
                })()
              }}
              className="rounded-lg bg-[var(--accent)] px-4 py-2 text-sm text-white"
            >
              刷新列表
            </button>
            <button
              type="button"
              disabled={loading}
              onClick={() => void exportFeedback()}
              className="rounded-lg border border-[var(--border)] px-4 py-2 text-sm"
            >
              导出 JSONL
            </button>
          </div>
          <div className="mt-4 overflow-x-auto">
            <table className="w-full min-w-[640px] text-left text-xs">
              <thead>
                <tr className="border-b border-[var(--border)] text-[var(--text-muted)]">
                  <th className="py-2">时间</th>
                  <th className="py-2">user</th>
                  <th className="py-2">rating</th>
                  <th className="py-2">trace</th>
                  <th className="py-2">纠错</th>
                </tr>
              </thead>
              <tbody>
                {feedbackItems.map((row) => (
                  <tr key={row.id} className="border-b border-[var(--border)]/70">
                    <td className="py-2 whitespace-nowrap">{fmtTs(row.timestamp_ms)}</td>
                    <td className="py-2 font-mono">{row.user_id}</td>
                    <td className="py-2">{row.rating}</td>
                    <td className="py-2">
                      <Link
                        to={`/trace?id=${encodeURIComponent(row.trace_id)}`}
                        className="text-[var(--accent)] hover:underline"
                      >
                        {row.trace_id.slice(0, 8)}…
                      </Link>
                    </td>
                    <td className="max-w-[200px] truncate py-2" title={row.correction ?? ''}>
                      {row.correction || '—'}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
            {feedbackItems.length === 0 ? <p className="mt-4 text-sm text-[var(--text-muted)]">暂无数据</p> : null}
          </div>
        </section>
      ) : null}

      {tab === 'risk' ? (
        <section className="rounded-2xl border border-[var(--border)] bg-[var(--surface-2)] p-5">
          <div className="flex flex-wrap items-end gap-3">
            <div>
              <label className="text-xs text-[var(--text-muted)]">limit</label>
              <input
                type="number"
                min={1}
                max={200}
                value={riskLimit}
                onChange={(e) => setRiskLimit(Number(e.target.value) || 25)}
                className="mt-1 w-20 rounded-lg border border-[var(--border)] bg-[var(--surface)] px-2 py-1.5 text-sm"
              />
            </div>
            <button
              type="button"
              disabled={loading}
              onClick={() => {
                void (async () => {
                  setLoading(true)
                  setError(null)
                  try {
                    await loadRisk()
                  } catch (e) {
                    setError(getApiErrorMessage(e))
                  } finally {
                    setLoading(false)
                  }
                })()
              }}
              className="rounded-lg bg-[var(--accent)] px-4 py-2 text-sm text-white"
            >
              刷新
            </button>
          </div>
          {risk ? (
            <>
              <p className="mt-3 text-xs text-[var(--text-muted)]">
                storage={risk.storage} · {risk.note}
              </p>
              <div className="mt-4 overflow-x-auto">
                <table className="w-full min-w-[640px] text-left text-xs">
                  <thead>
                    <tr className="border-b border-[var(--border)] text-[var(--text-muted)]">
                      <th className="py-2">时间</th>
                      <th className="py-2">user</th>
                      <th className="py-2">trace</th>
                      <th className="py-2">原因</th>
                      <th className="py-2">预览</th>
                    </tr>
                  </thead>
                  <tbody>
                    {risk.items.map((row, i) => (
                      <tr key={String(row.trace_id ?? i)} className="border-b border-[var(--border)]/70">
                        <td className="py-2 whitespace-nowrap">{fmtTs(Number(row.timestamp_ms ?? 0))}</td>
                        <td className="py-2 font-mono">{String(row.user_id ?? '')}</td>
                        <td className="py-2">
                          <Link
                            to={`/trace?id=${encodeURIComponent(String(row.trace_id ?? ''))}`}
                            className="text-[var(--accent)] hover:underline"
                          >
                            {String(row.trace_id ?? '').slice(0, 8)}…
                          </Link>
                        </td>
                        <td className="max-w-[180px] truncate py-2" title={String(row.reason ?? '')}>
                          {String(row.reason ?? '—')}
                        </td>
                        <td className="max-w-[160px] truncate py-2" title={String(row.message_preview ?? '')}>
                          {String(row.message_preview ?? '')}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
                {risk.items.length === 0 ? (
                  <p className="mt-4 text-sm text-[var(--text-muted)]">暂无风险事件（或当前为内存 Trace 存储）</p>
                ) : null}
              </div>
            </>
          ) : null}
        </section>
      ) : null}

      {tab === 'compliance' ? (
        <section className="space-y-5 rounded-2xl border border-[var(--border)] bg-[var(--surface-2)] p-5">
          <div>
            <h3 className="text-sm font-medium text-[var(--text)]">用户维度导出 / 遗忘</h3>
            <p className="mt-1 text-xs text-[var(--text-muted)]">
              使用页眉中的「默认 user_id」作为目标用户。鉴权同{' '}
              <code className="text-[11px]">/admin/config</code>。
            </p>
            <p className="mt-2 text-xs text-[var(--text-muted)]">
              <code className="text-[11px]">GET /users/&#123;id&#125;/export</code>：LTM（含 is_active）、STM
              会话、反馈 JSONL 中该用户行。<code className="text-[11px]">POST /users/&#123;id&#125;/forget</code>
              ：全部生效 LTM 软删并移出 RAG 索引；Trace 与反馈文件不自动删除。
            </p>
          </div>
          <div className="flex flex-wrap gap-3">
            <button
              type="button"
              disabled={loading}
              onClick={() => void exportUserPackage()}
              className="rounded-lg bg-[var(--accent)] px-4 py-2 text-sm text-white disabled:opacity-50"
            >
              导出 JSON 包
            </button>
          </div>
          <div className="border-t border-[var(--border)] pt-4">
            <p className="text-xs font-medium text-[var(--danger)]">危险操作</p>
            <div className="mt-3 space-y-3">
              <BoolField
                label="同时清空该用户全部 STM 会话"
                checked={forgetClearStm}
                onChange={setForgetClearStm}
              />
              <BoolField
                label="我已知悉：将软删其全部生效 LTM，且不可从前端撤销"
                checked={forgetConfirm}
                onChange={setForgetConfirm}
              />
              <button
                type="button"
                disabled={loading}
                onClick={() => void runUserForget()}
                className="rounded-lg border border-[var(--danger)]/50 bg-[color-mix(in_oklab,var(--danger)_08%,var(--surface))] px-4 py-2 text-sm text-[var(--danger)] disabled:opacity-50"
              >
                执行遗忘（confirm=true）
              </button>
            </div>
          </div>
        </section>
      ) : null}
    </div>
  )
}
