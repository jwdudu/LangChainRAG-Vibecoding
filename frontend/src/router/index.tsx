import type { ReactElement } from 'react'
import { Routes, Route, Navigate } from 'react-router-dom'
import { useAuth } from '../stores/auth'
import MainLayout from '../components/MainLayout'
import Login from '../views/Login'
import Register from '../views/Register'
import Chat from '../views/Chat'
import KnowledgeBase from '../views/KnowledgeBase'
import Profile from '../views/Profile'

// 登录守卫：未登录跳转登录页
function RequireAuth({ children }: { children: ReactElement }) {
  const token = useAuth((s) => s.token)
  if (!token) return <Navigate to="/login" replace />
  return children
}

// 管理员守卫：非 admin 无法进入知识库管理页
function RequireAdmin({ children }: { children: ReactElement }) {
  const user = useAuth((s) => s.user)
  if (user?.role !== 'admin') return <Navigate to="/chat" replace />
  return children
}

export default function AppRoutes() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route path="/register" element={<Register />} />
      <Route
        path="/"
        element={
          <RequireAuth>
            <MainLayout />
          </RequireAuth>
        }
      >
        <Route index element={<Navigate to="/chat" replace />} />
        <Route path="chat" element={<Chat />} />
        <Route
          path="kb"
          element={
            <RequireAdmin>
              <KnowledgeBase />
            </RequireAdmin>
          }
        />
        <Route path="profile" element={<Profile />} />
      </Route>
      <Route path="*" element={<Navigate to="/chat" replace />} />
    </Routes>
  )
}
