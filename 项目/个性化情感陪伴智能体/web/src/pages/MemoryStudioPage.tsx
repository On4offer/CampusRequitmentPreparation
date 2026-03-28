import { useCallback, useEffect, useState, type ReactNode } from 'react'
import { useSearchParams } from 'react-router-dom'
import { deleteLtm, getApiErrorMessage, getLtmItem, getLtmList, patchLtm, postLtm } from '../api/client'
import type { LTMItemOut, LTMTypeName } from '../api/types'
import { usePersistentString } from '../hooks/usePersistentString'

const LS_USER = 'companion_user_id'

const LTM_TYPES: LTMTypeName[] = ['Preference', 'Profile', 'Event', 'Constraint']

const PAGE = 12

function formatTs(ms: number) {
  try {
    return new Date(ms).toLocaleString('zh-CN')
  } catch {
    return String(ms)
  }
}

function parseTags(s: string): string[] {
  return s
    .split(/[,，]/)
    .map((x) => x.trim())
    .filter(Boolean)
}

function Modal({
  title,
  children,
  onClose,
}: {
  title: string
  children: ReactNode
  onClose: () => void
}) {
  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/45 p-4"
      role="dialog"
      aria-modal="true"
      aria-labelledby="mem-modal-title"
      onClick={onClose}
    >
      <div
        className="max-h-[90vh] w-full max-w-lg overflow-y-auto rounded-2xl border border-[var(--border)] bg-[var(--surface-2)] p-5 shadow-lg"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="mb-4 flex items-center justify-between gap-2">
          <h2 id="mem-modal-title" className="font-display text-lg text-[var(--text)]">
            {title}
          </h2>
          <button
            type="button"
            onClick={onClose}
            className="rounded-lg px-2 py-1 text-sm text-[var(--text-muted)] hover:bg-[var(--surface)]"
          >
            关闭
          </button>
        </div>
        {children}
      </div>
    </div>
  )
}

export function MemoryStudioPage() {
  const [searchParams, setSearchParams] = useSearchParams()
  const [userId, setUserId] = usePersistentString(LS_USER, 'demo-user')
  const [typeFilter, setTypeFilter] = useState<string>('')
  const [sourceFilter, setSourceFilter] = useState<string>('')
  const [qInput, setQInput] = useState('')
  const [debouncedQ, setDebouncedQ] = useState('')
  const [offset, setOffset] = useState(0)
  const [items, setItems] = useState<LTMItemOut[]>([])
  const [total, setTotal] = useState(0)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [toast, setToast] = useState<string | null>(null)

  const [createOpen, setCreateOpen] = useState(false)
  const [editItem, setEditItem] = useState<LTMItemOut | null>(null)
  const [deleteItem, setDeleteItem] = useState<LTMItemOut | null>(null)

  useEffect(() => {
    const t = window.setTimeout(() => setDebouncedQ(qInput.trim()), 350)
    return () => window.clearTimeout(t)
  }, [qInput])

  useEffect(() => {
    setOffset(0)
  }, [typeFilter, sourceFilter, debouncedQ, userId])

  const uid = userId.trim() || 'default'

  const ltmFocusId = searchParams.get('ltm_id')?.trim() ?? ''

  useEffect(() => {
    if (!ltmFocusId) return
    const lid = ltmFocusId
    void (async () => {
      try {
        const item = await getLtmItem(lid, uid)
        setEditItem(item)
        setToast('已从对话引用打开该条记忆')
      } catch (e) {
        setError(getApiErrorMessage(e))
      } finally {
        setSearchParams(
          (prev) => {
            const next = new URLSearchParams(prev)
            next.delete('ltm_id')
            return next
          },
          { replace: true },
        )
      }
    })()
  }, [ltmFocusId, uid, setSearchParams])

  const load = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const r = await getLtmList({
        userId: uid,
        type: typeFilter || undefined,
        source: sourceFilter || undefined,
        q: debouncedQ || undefined,
        limit: PAGE,
        offset,
      })
      setItems(r.items)
      setTotal(r.total)
    } catch (e) {
      setError(getApiErrorMessage(e))
      setItems([])
      setTotal(0)
    } finally {
      setLoading(false)
    }
  }, [uid, typeFilter, sourceFilter, debouncedQ, offset])

  useEffect(() => {
    void load()
  }, [load])

  useEffect(() => {
    if (!toast) return
    const t = window.setTimeout(() => setToast(null), 3200)
    return () => window.clearTimeout(t)
  }, [toast])

  const fromIdx = total === 0 ? 0 : offset + 1
  const toIdx = offset + items.length
  const canPrev = offset > 0
  const canNext = offset + PAGE < total

  return (
    <div className="mx-auto max-w-5xl space-y-4">
      <header className="rounded-2xl border border-[var(--border)] bg-[var(--surface-2)] p-5">
        <h2 className="font-display text-xl text-[var(--text)]">Memory Studio</h2>
        <p className="mt-1 text-sm text-[var(--text-muted)]">
          长期记忆（LTM）与对话里的「引用记忆」同源：开启 RAG 时仅检索本列表中的生效条目。来源可为「新建记忆/API」或环境变量开启{' '}
          <code className="rounded bg-[var(--surface)] px-1 font-mono text-[11px]">LTM_EXTRACT_ENABLED</code> 后由对话隐式写入的{' '}
          <code className="font-mono text-[11px]">dialogue_extract</code>。软删除后不再参与检索。
        </p>
        <div className="mt-4 flex flex-wrap items-end gap-3">
          <div className="min-w-[140px]">
            <label htmlFor="mem-user" className="text-xs font-medium text-[var(--text-muted)]">
              user_id
            </label>
            <input
              id="mem-user"
              value={userId}
              onChange={(e) => setUserId(e.target.value)}
              className="mt-1 w-full rounded-lg border border-[var(--border)] bg-[var(--surface)] px-3 py-2 text-sm"
            />
          </div>
          <div className="min-w-[160px]">
            <label htmlFor="mem-type" className="text-xs font-medium text-[var(--text-muted)]">
              类型
            </label>
            <select
              id="mem-type"
              value={typeFilter}
              onChange={(e) => setTypeFilter(e.target.value)}
              className="mt-1 w-full rounded-lg border border-[var(--border)] bg-[var(--surface)] px-3 py-2 text-sm"
            >
              <option value="">全部</option>
              {LTM_TYPES.map((t) => (
                <option key={t} value={t}>
                  {t}
                </option>
              ))}
            </select>
          </div>
          <div className="min-w-[180px]">
            <label htmlFor="mem-source" className="text-xs font-medium text-[var(--text-muted)]">
              来源
            </label>
            <select
              id="mem-source"
              value={sourceFilter}
              onChange={(e) => setSourceFilter(e.target.value)}
              className="mt-1 w-full rounded-lg border border-[var(--border)] bg-[var(--surface)] px-3 py-2 text-sm"
            >
              <option value="">全部</option>
              <option value="dialogue_extract">对话隐式抽取</option>
            </select>
          </div>
          <div className="min-w-[200px] flex-1">
            <label htmlFor="mem-q" className="text-xs font-medium text-[var(--text-muted)]">
              搜索（内容包含）
            </label>
            <input
              id="mem-q"
              value={qInput}
              onChange={(e) => setQInput(e.target.value)}
              placeholder="关键词…"
              className="mt-1 w-full rounded-lg border border-[var(--border)] bg-[var(--surface)] px-3 py-2 text-sm"
            />
          </div>
          <button
            type="button"
            onClick={() => setCreateOpen(true)}
            className="rounded-lg bg-[var(--brand)] px-4 py-2 text-sm font-medium text-white hover:bg-[var(--brand-hover)]"
          >
            新建记忆
          </button>
        </div>
      </header>

      {toast ? (
        <div className="rounded-xl border border-[var(--ok)]/40 bg-[color-mix(in_oklab,var(--ok)_10%,var(--surface-2))] px-4 py-2 text-sm text-[var(--ok)]">
          {toast}
        </div>
      ) : null}

      {error ? (
        <div className="rounded-xl border border-[var(--danger)]/40 bg-[color-mix(in_oklab,var(--danger)_08%,var(--surface-2))] px-4 py-3 text-sm text-[var(--danger)]">
          {error}
        </div>
      ) : null}

      <div className="rounded-2xl border border-[var(--border)] bg-[var(--surface-2)]">
        <div className="flex items-center justify-between border-b border-[var(--border)] px-4 py-3 text-xs text-[var(--text-muted)]">
          <span>
            {total === 0 ? '无数据' : `第 ${fromIdx}–${toIdx} 条，共 ${total} 条`}
          </span>
          <div className="flex gap-2">
            <button
              type="button"
              disabled={!canPrev || loading}
              onClick={() => setOffset((o) => Math.max(0, o - PAGE))}
              className="rounded-lg border border-[var(--border)] px-3 py-1 disabled:opacity-40"
            >
              上一页
            </button>
            <button
              type="button"
              disabled={!canNext || loading}
              onClick={() => setOffset((o) => o + PAGE)}
              className="rounded-lg border border-[var(--border)] px-3 py-1 disabled:opacity-40"
            >
              下一页
            </button>
          </div>
        </div>

        {loading ? (
          <ul className="divide-y divide-[var(--border)] p-4">
            {Array.from({ length: 6 }).map((_, i) => (
              <li key={i} className="animate-pulse py-4">
                <div className="h-4 w-1/3 rounded bg-[var(--border)]" />
                <div className="mt-2 h-3 w-full rounded bg-[var(--border)]" />
                <div className="mt-2 h-3 w-2/3 rounded bg-[var(--border)]" />
              </li>
            ))}
          </ul>
        ) : items.length === 0 ? (
          <div className="px-6 py-16 text-center text-sm text-[var(--text-muted)]">
            <p>暂无记忆条目。</p>
            <p className="mt-2 text-xs">
              可点「新建记忆」或 <code className="font-mono text-[10px]">POST /memory/ltm</code> 添加；若服务端开启{' '}
              <code className="font-mono text-[10px]">LTM_EXTRACT_ENABLED</code> 且满足每 N 轮等条件，对话也会隐式写入（来源{' '}
              <code className="font-mono text-[10px]">dialogue_extract</code>，可用上方「来源」筛选）。对话始终更新{' '}
              <strong className="text-[var(--text)]">STM</strong>；RAG 仅引用本列表中生效条目。
            </p>
          </div>
        ) : (
          <ul className="divide-y divide-[var(--border)]">
            {items.map((row) => (
              <li key={row.id} className="px-4 py-4 transition-colors hover:bg-[color-mix(in_oklab,var(--surface)_92%,var(--border))]">
                <div className="flex flex-wrap items-start justify-between gap-2">
                  <div className="min-w-0 flex-1">
                    <div className="flex flex-wrap items-center gap-2 text-xs text-[var(--text-muted)]">
                      <span className="rounded-md bg-[color-mix(in_oklab,var(--accent)_12%,transparent)] px-2 py-0.5 font-medium text-[var(--accent)]">
                        {row.type}
                      </span>
                      {row.source === 'dialogue_extract' ? (
                        <span className="rounded-md bg-[color-mix(in_oklab,var(--brand)_14%,transparent)] px-2 py-0.5 text-[11px] font-medium text-[var(--brand)]">
                          隐式
                        </span>
                      ) : null}
                      <span className="font-mono text-[10px] opacity-80">{row.id.slice(0, 8)}…</span>
                      <span>置信度 {row.confidence}</span>
                      <span>向量 {row.embedding_status}</span>
                    </div>
                    <p className="mt-2 whitespace-pre-wrap text-sm text-[var(--text)]">{row.content}</p>
                    <div className="mt-2 flex flex-wrap gap-x-3 gap-y-1 text-[11px] text-[var(--text-muted)]">
                      <span>来源：{row.source || '—'}</span>
                      <span>标签：{row.tags?.length ? row.tags.join('、') : '—'}</span>
                      <span>创建 {formatTs(row.created_at)}</span>
                      <span>更新 {formatTs(row.updated_at)}</span>
                    </div>
                  </div>
                  <div className="flex shrink-0 gap-2">
                    <button
                      type="button"
                      onClick={() => setEditItem(row)}
                      className="rounded-lg border border-[var(--border)] px-3 py-1.5 text-xs hover:bg-[var(--surface)]"
                    >
                      编辑
                    </button>
                    <button
                      type="button"
                      onClick={() => setDeleteItem(row)}
                      className="rounded-lg border border-[var(--danger)]/40 px-3 py-1.5 text-xs text-[var(--danger)] hover:bg-[color-mix(in_oklab,var(--danger)_08%,var(--surface))]"
                    >
                      删除
                    </button>
                  </div>
                </div>
              </li>
            ))}
          </ul>
        )}
      </div>

      {createOpen ? (
        <CreateLtmModal
          userId={uid}
          onClose={() => setCreateOpen(false)}
          onCreated={async () => {
            setCreateOpen(false)
            setToast('已创建')
            setOffset(0)
            await load()
          }}
        />
      ) : null}

      {editItem ? (
        <EditLtmModal
          item={editItem}
          userId={uid}
          onClose={() => setEditItem(null)}
          onSaved={async () => {
            setEditItem(null)
            setToast('已保存')
            await load()
          }}
        />
      ) : null}

      {deleteItem ? (
        <Modal title="确认软删除？" onClose={() => setDeleteItem(null)}>
          <p className="text-sm text-[var(--text-muted)]">
            将标记为失效，不再参与检索。条目 id：<span className="font-mono text-xs">{deleteItem.id}</span>
          </p>
          <div className="mt-4 flex justify-end gap-2">
            <button
              type="button"
              onClick={() => setDeleteItem(null)}
              className="rounded-lg border border-[var(--border)] px-4 py-2 text-sm"
            >
              取消
            </button>
            <button
              type="button"
              onClick={async () => {
                try {
                  await deleteLtm(deleteItem.id, uid)
                  setDeleteItem(null)
                  setToast('已删除')
                  await load()
                } catch (e) {
                  setError(getApiErrorMessage(e))
                }
              }}
              className="rounded-lg bg-[var(--danger)] px-4 py-2 text-sm text-white"
            >
              确认删除
            </button>
          </div>
        </Modal>
      ) : null}
    </div>
  )
}

function CreateLtmModal({
  userId,
  onClose,
  onCreated,
}: {
  userId: string
  onClose: () => void
  onCreated: () => void | Promise<void>
}) {
  const [type, setType] = useState<LTMTypeName>('Preference')
  const [content, setContent] = useState('')
  const [source, setSource] = useState('web_ui')
  const [confidence, setConfidence] = useState('0.9')
  const [tags, setTags] = useState('')
  const [busy, setBusy] = useState(false)
  const [localErr, setLocalErr] = useState<string | null>(null)

  const submit = async () => {
    const c = content.trim()
    if (!c) {
      setLocalErr('内容不能为空')
      return
    }
    const conf = Number(confidence)
    if (Number.isNaN(conf) || conf < 0 || conf > 1) {
      setLocalErr('置信度须在 0～1')
      return
    }
    setBusy(true)
    setLocalErr(null)
    try {
      await postLtm({
        user_id: userId,
        type,
        content: c,
        source: source.trim(),
        confidence: conf,
        tags: parseTags(tags),
      })
      await onCreated()
    } catch (e) {
      setLocalErr(getApiErrorMessage(e))
    } finally {
      setBusy(false)
    }
  }

  return (
    <Modal title="新建长期记忆" onClose={onClose}>
      {localErr ? <p className="mb-3 text-sm text-[var(--danger)]">{localErr}</p> : null}
      <div className="space-y-3">
        <div>
          <label className="text-xs text-[var(--text-muted)]">类型</label>
          <select
            value={type}
            onChange={(e) => setType(e.target.value as LTMTypeName)}
            className="mt-1 w-full rounded-lg border border-[var(--border)] bg-[var(--surface)] px-3 py-2 text-sm"
          >
            {LTM_TYPES.map((t) => (
              <option key={t} value={t}>
                {t}
              </option>
            ))}
          </select>
        </div>
        <div>
          <label className="text-xs text-[var(--text-muted)]">内容</label>
          <textarea
            value={content}
            onChange={(e) => setContent(e.target.value)}
            rows={4}
            className="mt-1 w-full rounded-lg border border-[var(--border)] bg-[var(--surface)] px-3 py-2 text-sm"
          />
        </div>
        <div>
          <label className="text-xs text-[var(--text-muted)]">来源</label>
          <input
            value={source}
            onChange={(e) => setSource(e.target.value)}
            className="mt-1 w-full rounded-lg border border-[var(--border)] bg-[var(--surface)] px-3 py-2 text-sm"
          />
        </div>
        <div>
          <label className="text-xs text-[var(--text-muted)]">置信度 0～1</label>
          <input
            value={confidence}
            onChange={(e) => setConfidence(e.target.value)}
            type="text"
            inputMode="decimal"
            className="mt-1 w-full rounded-lg border border-[var(--border)] bg-[var(--surface)] px-3 py-2 text-sm"
          />
        </div>
        <div>
          <label className="text-xs text-[var(--text-muted)]">标签（逗号分隔）</label>
          <input
            value={tags}
            onChange={(e) => setTags(e.target.value)}
            className="mt-1 w-full rounded-lg border border-[var(--border)] bg-[var(--surface)] px-3 py-2 text-sm"
          />
        </div>
      </div>
      <div className="mt-5 flex justify-end gap-2">
        <button type="button" onClick={onClose} className="rounded-lg border border-[var(--border)] px-4 py-2 text-sm">
          取消
        </button>
        <button
          type="button"
          disabled={busy}
          onClick={() => void submit()}
          className="rounded-lg bg-[var(--brand)] px-4 py-2 text-sm text-white disabled:opacity-50"
        >
          {busy ? '提交中…' : '创建'}
        </button>
      </div>
    </Modal>
  )
}

function EditLtmModal({
  item,
  userId,
  onClose,
  onSaved,
}: {
  item: LTMItemOut
  userId: string
  onClose: () => void
  onSaved: () => void | Promise<void>
}) {
  const [content, setContent] = useState(item.content)
  const [confidence, setConfidence] = useState(String(item.confidence))
  const [tags, setTags] = useState(item.tags.join(', '))
  const [busy, setBusy] = useState(false)
  const [localErr, setLocalErr] = useState<string | null>(null)

  const submit = async () => {
    const c = content.trim()
    if (!c) {
      setLocalErr('内容不能为空')
      return
    }
    const conf = Number(confidence)
    if (Number.isNaN(conf) || conf < 0 || conf > 1) {
      setLocalErr('置信度须在 0～1')
      return
    }
    setBusy(true)
    setLocalErr(null)
    try {
      await patchLtm(item.id, userId, {
        content: c,
        confidence: conf,
        tags: parseTags(tags),
      })
      await onSaved()
    } catch (e) {
      setLocalErr(getApiErrorMessage(e))
    } finally {
      setBusy(false)
    }
  }

  return (
    <Modal title={`编辑 · ${item.type}`} onClose={onClose}>
      {localErr ? <p className="mb-3 text-sm text-[var(--danger)]">{localErr}</p> : null}
      <p className="mb-3 font-mono text-[10px] text-[var(--text-muted)]">{item.id}</p>
      <div className="space-y-3">
        <div>
          <label className="text-xs text-[var(--text-muted)]">内容</label>
          <textarea
            value={content}
            onChange={(e) => setContent(e.target.value)}
            rows={5}
            className="mt-1 w-full rounded-lg border border-[var(--border)] bg-[var(--surface)] px-3 py-2 text-sm"
          />
        </div>
        <div>
          <label className="text-xs text-[var(--text-muted)]">置信度</label>
          <input
            value={confidence}
            onChange={(e) => setConfidence(e.target.value)}
            className="mt-1 w-full rounded-lg border border-[var(--border)] bg-[var(--surface)] px-3 py-2 text-sm"
          />
        </div>
        <div>
          <label className="text-xs text-[var(--text-muted)]">标签（逗号分隔）</label>
          <input
            value={tags}
            onChange={(e) => setTags(e.target.value)}
            className="mt-1 w-full rounded-lg border border-[var(--border)] bg-[var(--surface)] px-3 py-2 text-sm"
          />
        </div>
      </div>
      <div className="mt-5 flex justify-end gap-2">
        <button type="button" onClick={onClose} className="rounded-lg border border-[var(--border)] px-4 py-2 text-sm">
          取消
        </button>
        <button
          type="button"
          disabled={busy}
          onClick={() => void submit()}
          className="rounded-lg bg-[var(--brand)] px-4 py-2 text-sm text-white disabled:opacity-50"
        >
          {busy ? '保存中…' : '保存'}
        </button>
      </div>
    </Modal>
  )
}
