import { useEffect } from 'react'
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { Toaster } from 'react-hot-toast'
import useAtlasStore from './store/useAtlasStore'
import { getUserConfig } from './services/api'
import LoginPage from './pages/LoginPage'
import MainPage from './pages/MainPage'

const panelRoutes = ['', 'chat', 'system', 'analytics', 'security', 'study', 'media', 'ml', 'bangladesh']

function App() {
  const { isAuthenticated, setUserName } = useAtlasStore()

  useEffect(() => {
    getUserConfig().then(cfg => {
      if (cfg.user_name) setUserName(cfg.user_name)
    }).catch(() => {})
  }, [])

  return (
    <>
      <Toaster position="top-right" toastOptions={{
        style: { background: '#001020', color: '#00ffc8', border: '1px solid rgba(0,255,200,0.3)' }
      }} />
      <BrowserRouter future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
        <Routes>
          <Route path="/login" element={!isAuthenticated ? <LoginPage /> : <Navigate to="/" />} />
          <Route path="/" element={isAuthenticated ? <MainPage /> : <Navigate to="/login" />} />
          {panelRoutes.map(p => p && (
            <Route key={p} path={`/${p}`} element={isAuthenticated ? <MainPage /> : <Navigate to="/login" />} />
          ))}
        </Routes>
      </BrowserRouter>
    </>
  )
}

export default App