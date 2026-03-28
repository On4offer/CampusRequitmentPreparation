import { createContext, useCallback, useContext, useMemo, useState, type ReactNode } from 'react'

type ToastCtx = {
  showToast: (message: string, variant?: 'ok' | 'neutral') => void
}

const Ctx = createContext<ToastCtx | null>(null)

export function ToastProvider({ children }: { children: ReactNode }) {
  const [msg, setMsg] = useState<string | null>(null)
  const [variant, setVariant] = useState<'ok' | 'neutral'>('neutral')

  const showToast = useCallback((message: string, v: 'ok' | 'neutral' = 'neutral') => {
    setVariant(v)
    setMsg(message)
    window.setTimeout(() => setMsg(null), 3200)
  }, [])

  const value = useMemo(() => ({ showToast }), [showToast])

  return (
    <Ctx.Provider value={value}>
      {children}
      {msg ? (
        <div
          className={`fixed bottom-6 left-1/2 z-[100] max-w-[min(90vw,24rem)] -translate-x-1/2 rounded-xl border px-4 py-3 text-sm shadow-lg transition-opacity duration-200 ${
            variant === 'ok'
              ? 'border-[var(--ok)]/40 bg-[color-mix(in_oklab,var(--ok)_12%,var(--surface-2))] text-[var(--ok)]'
              : 'border-[var(--border)] bg-[var(--surface-2)] text-[var(--text)]'
          }`}
          role="status"
        >
          {msg}
        </div>
      ) : null}
    </Ctx.Provider>
  )
}

export function useToast() {
  const x = useContext(Ctx)
  if (!x) throw new Error('useToast outside ToastProvider')
  return x
}
