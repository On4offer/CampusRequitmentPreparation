import { useEffect, useState } from 'react'
import type { ThemeMode } from '../theme/applyTheme'

export function useThemeMode(): ThemeMode {
  const [mode, setMode] = useState<ThemeMode>(() => {
    const d = document.documentElement.dataset.theme
    return d === 'dark' || d === 'light' ? d : 'light'
  })

  useEffect(() => {
    const sync = () => {
      const d = document.documentElement.dataset.theme
      setMode(d === 'dark' || d === 'light' ? d : 'light')
    }
    window.addEventListener('companion-theme', sync)
    return () => window.removeEventListener('companion-theme', sync)
  }, [])

  return mode
}
