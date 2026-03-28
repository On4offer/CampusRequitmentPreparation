import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom'
import { ToastProvider } from './context/ToastContext'
import { AppShell } from './layout/AppShell'
import { ChatPage } from './pages/ChatPage'
import { ChatProbePage } from './pages/ChatProbePage'
import { EmotionDashboardPage } from './pages/EmotionDashboardPage'
import { EvalLabPage } from './pages/EvalLabPage'
import { MemoryStudioPage } from './pages/MemoryStudioPage'
import { AdminOpsPage } from './pages/AdminOpsPage'
import { TraceViewerPage } from './pages/TraceViewerPage'

export default function App() {
  return (
    <BrowserRouter>
      <ToastProvider>
      <Routes>
        <Route path="/" element={<AppShell />}>
          <Route index element={<Navigate to="/chat" replace />} />
          <Route path="chat" element={<ChatPage />} />
          <Route path="probe" element={<ChatProbePage />} />
          <Route path="memory" element={<MemoryStudioPage />} />
          <Route path="eval" element={<EvalLabPage />} />
          <Route path="emotion" element={<EmotionDashboardPage />} />
          <Route path="trace" element={<TraceViewerPage />} />
          <Route path="ops" element={<AdminOpsPage />} />
          <Route path="*" element={<Navigate to="/chat" replace />} />
        </Route>
      </Routes>
      </ToastProvider>
    </BrowserRouter>
  )
}
