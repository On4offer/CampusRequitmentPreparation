import { useState, type ComponentProps } from 'react'
import { ApiCallError, getApiErrorMessage, getHealth, postChat } from '../api/client'
import type { ChatResponse } from '../api/types'
import { usePersistentString } from '../hooks/usePersistentString'

const LS_USER = 'companion_user_id'
const LS_SESSION = 'companion_session_id'
const LS_ADMIN = 'companion_admin_token'

function Field({
  id,
  label,
  hint,
  ...inputProps
}: ComponentProps<'input'> & { id: string; label: string; hint?: string }) {
  return (
    <div className="flex flex-col gap-1">
      <label htmlFor={id} className="text-xs font-medium text-[var(--text-muted)]">
        {label}
      </label>
      <input
        id={id}
        className="rounded-lg border border-[var(--border)] bg-[var(--surface-2)] px-3 py-2 text-sm text-[var(--text)] shadow-sm transition-[border-color,box-shadow] duration-200 placeholder:text-[var(--text-muted)] focus:border-[var(--brand)] focus:outline-none focus-visible:ring-2 focus-visible:ring-[var(--ring)]"
        {...inputProps}
      />
      {hint ? <p className="text-xs text-[var(--text-muted)]">{hint}</p> : null}
    </div>
  )
}

export function ChatProbePage() {
  const [userId, setUserId] = usePersistentString(LS_USER, 'demo-user')
  const [sessionId, setSessionId] = usePersistentString(LS_SESSION, 'demo-session')
  const [adminToken, setAdminToken] = usePersistentString(LS_ADMIN, '')
  const [message, setMessage] = useState('你好，简单介绍一下你自己。')

  const [healthLoading, setHealthLoading] = useState(false)
  const [chatLoading, setChatLoading] = useState(false)
  const [healthOk, setHealthOk] = useState<string | null>(null)
  const [chatOk, setChatOk] = useState<ChatResponse | null>(null)
  const [error, setError] = useState<{ status?: number; message: string } | null>(null)

  const runHealth = async () => {
    setError(null)
    setHealthOk(null)
    setHealthLoading(true)
    try {
      const h = await getHealth()
      setHealthOk(
        `status=${h.status ?? 'ok'} · redis=${h.redis ?? '?'} · db=${h.database ?? '?'} · ltm_extract=${String(h.ltm_extract_enabled)}`,
      )
    } catch (e) {
      setError({
        status: e instanceof ApiCallError ? e.status : undefined,
        message: getApiErrorMessage(e),
      })
    } finally {
      setHealthLoading(false)
    }
  }

  const runChat = async () => {
    setError(null)
    setChatOk(null)
    setChatLoading(true)
    try {
      const res = await postChat(
        {
          message: message.trim(),
          user_id: userId.trim() || null,
          session_id: sessionId.trim() || null,
        },
        adminToken.trim() || undefined,
      )
      setChatOk(res)
    } catch (e) {
      setError({
        status: e instanceof ApiCallError ? e.status : undefined,
        message: getApiErrorMessage(e),
      })
    } finally {
      setChatLoading(false)
    }
  }

  return (
    <div className="mx-auto max-w-3xl space-y-8">
      <section className="rounded-2xl border border-[var(--border)] bg-[var(--surface-2)] p-6 shadow-sm transition-colors duration-200">
        <h2 className="font-display text-lg text-[var(--text)]">身份与 Token</h2>
        <p className="mt-1 text-sm text-[var(--text-muted)]">
          与后端约定一致：<code className="rounded bg-[var(--surface)] px-1 py-0.5 text-xs">user_id</code> /{' '}
          <code className="rounded bg-[var(--surface)] px-1 py-0.5 text-xs">session_id</code> 会持久化到
          localStorage。运营接口需要时在下方填写{' '}
          <code className="rounded bg-[var(--surface)] px-1 py-0.5 text-xs">X-Admin-Token</code>（普通{' '}
          <code className="rounded bg-[var(--surface)] px-1 py-0.5 text-xs">/chat</code> 可不填）。
        </p>
        <div className="mt-5 grid gap-4 sm:grid-cols-2">
          <Field
            id="user_id"
            label="user_id"
            value={userId}
            onChange={(e) => setUserId(e.target.value)}
            autoComplete="off"
          />
          <Field
            id="session_id"
            label="session_id"
            value={sessionId}
            onChange={(e) => setSessionId(e.target.value)}
            autoComplete="off"
          />
          <div className="sm:col-span-2">
            <Field
              id="admin_token"
              label="X-Admin-Token（可选）"
              type="password"
              value={adminToken}
              onChange={(e) => setAdminToken(e.target.value)}
              autoComplete="off"
              placeholder="与后端 ADMIN_CONFIG_TOKEN 一致时填写"
            />
          </div>
        </div>
      </section>

      <section className="rounded-2xl border border-[var(--border)] bg-[var(--surface-2)] p-6 shadow-sm transition-colors duration-200">
        <h2 className="font-display text-lg text-[var(--text)]">请求</h2>
        <div className="mt-4 flex flex-wrap gap-3">
          <button
            type="button"
            onClick={runHealth}
            disabled={healthLoading}
            className="rounded-lg border border-[var(--border)] bg-[var(--surface)] px-4 py-2 text-sm font-medium text-[var(--text)] transition-[background,opacity] duration-200 hover:bg-[color-mix(in_oklab,var(--surface)_65%,var(--border))] disabled:opacity-50 focus:outline-none focus-visible:ring-2 focus-visible:ring-[var(--ring)]"
          >
            {healthLoading ? '检查中…' : 'GET /health'}
          </button>
        </div>
        {healthOk != null ? (
          <p className="mt-4 text-sm text-[var(--ok)]">
            健康检查通过：<span className="font-mono">{healthOk}</span>
          </p>
        ) : null}

        <div className="mt-8">
          <label htmlFor="msg" className="text-xs font-medium text-[var(--text-muted)]">
            message
          </label>
          <textarea
            id="msg"
            rows={4}
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            className="mt-1 w-full resize-y rounded-lg border border-[var(--border)] bg-[var(--surface)] px-3 py-2 text-sm text-[var(--text)] focus:border-[var(--brand)] focus:outline-none focus-visible:ring-2 focus-visible:ring-[var(--ring)]"
          />
          <button
            type="button"
            onClick={runChat}
            disabled={chatLoading || !message.trim()}
            className="mt-4 rounded-lg bg-[var(--brand)] px-4 py-2 text-sm font-medium text-white transition-[background,opacity] duration-200 hover:bg-[var(--brand-hover)] disabled:opacity-50 focus:outline-none focus-visible:ring-2 focus-visible:ring-[var(--ring)]"
          >
            {chatLoading ? '发送中…' : 'POST /chat'}
          </button>
        </div>
      </section>

      {error ? (
        <section
          className="rounded-2xl border border-[var(--danger)]/35 bg-[color-mix(in_oklab,var(--danger)_08%,var(--surface-2))] p-6"
          role="alert"
        >
          <h3 className="font-display text-base text-[var(--danger)]">请求失败</h3>
          {error.status != null ? (
            <p className="mt-2 font-mono text-sm text-[var(--text-muted)]">HTTP {error.status}</p>
          ) : null}
          <pre className="mt-3 max-h-64 overflow-auto whitespace-pre-wrap break-words rounded-lg bg-[var(--surface)] p-3 font-mono text-xs text-[var(--text)]">
            {error.message}
          </pre>
        </section>
      ) : null}

      {chatOk ? (
        <section className="rounded-2xl border border-[var(--border)] bg-[var(--surface-2)] p-6 shadow-sm">
          <h3 className="font-display text-base text-[var(--text)]">回复摘要</h3>
          <p className="mt-3 whitespace-pre-wrap text-sm leading-relaxed text-[var(--text)]">{chatOk.reply}</p>
          <dl className="mt-4 grid gap-2 text-xs text-[var(--text-muted)] sm:grid-cols-2">
            <div>
              <dt className="font-medium">trace_id</dt>
              <dd className="mt-0.5 font-mono text-[var(--text)]">{chatOk.trace_id}</dd>
            </div>
            <div>
              <dt className="font-medium">user_id / session_id</dt>
              <dd className="mt-0.5 font-mono text-[var(--text)]">
                {chatOk.user_id} / {chatOk.session_id}
              </dd>
            </div>
          </dl>
          {(chatOk.citations?.length || chatOk.tool_summary) && (
            <details className="mt-4 text-sm text-[var(--text-muted)]">
              <summary className="cursor-pointer text-[var(--text)]">citations / tool_summary</summary>
              <pre className="mt-2 max-h-48 overflow-auto rounded-lg bg-[var(--surface)] p-3 font-mono text-xs">
                {JSON.stringify({ citations: chatOk.citations, tool_summary: chatOk.tool_summary }, null, 2)}
              </pre>
            </details>
          )}
        </section>
      ) : null}
    </div>
  )
}
