import { useCallback, useEffect, useState } from 'react'

/** localStorage 持久化字符串；SSR 安全（仅客户端读写） */
export function usePersistentString(key: string, initial: string) {
  const [value, setValue] = useState(initial)

  useEffect(() => {
    try {
      const raw = localStorage.getItem(key)
      if (raw != null) setValue(raw)
    } catch {
      /* ignore */
    }
  }, [key])

  const set = useCallback(
    (next: string) => {
      setValue(next)
      try {
        localStorage.setItem(key, next)
      } catch {
        /* ignore */
      }
    },
    [key],
  )

  return [value, set] as const
}
