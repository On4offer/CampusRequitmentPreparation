const STORAGE_KEY = 'companion_theme'

export type ThemeMode = 'light' | 'dark'

export function readStoredTheme(): ThemeMode | null {
  try {
    const v = localStorage.getItem(STORAGE_KEY)
    if (v === 'light' || v === 'dark') return v
  } catch {
    /* ignore */
  }
  return null
}

export function writeStoredTheme(mode: ThemeMode) {
  try {
    localStorage.setItem(STORAGE_KEY, mode)
  } catch {
    /* ignore */
  }
}

/** 首次进入：无记录则跟随系统；有记录则用用户选择 */
export function initThemeOnLoad() {
  const stored = readStoredTheme()
  const root = document.documentElement
  if (stored) {
    root.dataset.theme = stored
    return
  }
  const prefersDark = window.matchMedia?.('(prefers-color-scheme: dark)').matches
  root.dataset.theme = prefersDark ? 'dark' : 'light'
}

export function setTheme(mode: ThemeMode) {
  document.documentElement.dataset.theme = mode
  writeStoredTheme(mode)
}
