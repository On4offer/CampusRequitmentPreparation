import { NavLink, Outlet, useLocation } from 'react-router-dom'
import { useThemeMode } from '../hooks/useThemeMode'
import { setTheme, type ThemeMode } from '../theme/applyTheme'

const navItem =
  'block rounded-lg px-3 py-2 text-sm transition-[background,color] duration-200 hover:bg-[color-mix(in_oklab,var(--surface-2)_85%,var(--border))]'

const navActive =
  'bg-[color-mix(in_oklab,var(--brand)_12%,transparent)] text-[var(--brand)] font-medium'

export function AppShell() {
  const mode = useThemeMode()
  const loc = useLocation()
  const pageTitle =
    loc.pathname === '/chat'
      ? '对话'
      : loc.pathname === '/probe'
        ? '连接探针'
        : loc.pathname === '/memory'
          ? '记忆 Studio'
          : loc.pathname === '/eval'
            ? 'Eval Lab'
            : loc.pathname === '/emotion'
              ? '情绪仪表盘'
              : loc.pathname === '/trace'
                ? 'Trace 回放'
                : loc.pathname === '/ops'
                  ? '运营台'
                  : '控制台'

  const toggleTheme = () => {
    const next: ThemeMode = mode === 'dark' ? 'light' : 'dark'
    setTheme(next)
    window.dispatchEvent(new Event('companion-theme'))
  }

  return (
    <div className="flex min-h-dvh bg-[var(--surface)] text-[var(--text)]">
      <aside
        className="flex w-56 shrink-0 flex-col border-r border-[var(--border)] bg-[var(--surface-2)] px-3 py-5 transition-colors duration-200"
        aria-label="主导航"
      >
        <div className="mb-8 px-2">
          <p className="font-display text-lg font-semibold tracking-tight text-[var(--text)]">
            陪伴智能体
          </p>
          <p className="mt-1 text-xs text-[var(--text-muted)]">二期 · 控制台</p>
        </div>
        <nav className="flex flex-1 flex-col gap-1">
          <NavLink
            to="/chat"
            className={({ isActive }) => `${navItem} ${isActive ? navActive : 'text-[var(--text-muted)]'}`}
          >
            对话
          </NavLink>
          <NavLink
            to="/probe"
            className={({ isActive }) => `${navItem} ${isActive ? navActive : 'text-[var(--text-muted)]'}`}
          >
            连接探针
          </NavLink>
          <NavLink
            to="/memory"
            className={({ isActive }) => `${navItem} ${isActive ? navActive : 'text-[var(--text-muted)]'}`}
          >
            记忆 Studio
          </NavLink>
          <NavLink
            to="/eval"
            className={({ isActive }) => `${navItem} ${isActive ? navActive : 'text-[var(--text-muted)]'}`}
          >
            Eval Lab
          </NavLink>
          <NavLink
            to="/emotion"
            className={({ isActive }) => `${navItem} ${isActive ? navActive : 'text-[var(--text-muted)]'}`}
          >
            情绪仪表盘
          </NavLink>
          <NavLink
            to="/trace"
            className={({ isActive }) => `${navItem} ${isActive ? navActive : 'text-[var(--text-muted)]'}`}
          >
            Trace 回放
          </NavLink>
          <NavLink
            to="/ops"
            className={({ isActive }) => `${navItem} ${isActive ? navActive : 'text-[var(--text-muted)]'}`}
          >
            运营台
          </NavLink>
        </nav>
      </aside>
      <div className="flex min-w-0 flex-1 flex-col">
        <header className="flex items-center justify-between border-b border-[var(--border)] bg-[var(--surface-2)] px-6 py-3 transition-colors duration-200">
          <h1 className="font-display text-base font-medium text-[var(--text)]">
            二期 · {pageTitle}
          </h1>
          <button
            type="button"
            onClick={toggleTheme}
            className="rounded-lg border border-[var(--border)] bg-[var(--surface)] px-3 py-1.5 text-xs text-[var(--text-muted)] transition-[background,box-shadow] duration-200 hover:bg-[color-mix(in_oklab,var(--surface)_70%,var(--border))] focus:outline-none focus-visible:ring-2 focus-visible:ring-[var(--ring)]"
          >
            {mode === 'dark' ? '浅色模式' : '深色模式'}
          </button>
        </header>
        <main className="min-h-0 flex-1 overflow-auto p-6">
          <Outlet />
        </main>
      </div>
    </div>
  )
}
