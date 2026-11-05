import http from './http'

// ---- 认证 ----
export const login = (username: string, password: string) =>
  http.post('/auth/login', { username, password }).then((r) => r.data)

export const register = (username: string, password: string) =>
  http.post('/auth/register', { username, password }).then((r) => r.data)

export const changePassword = (old_password: string, new_password: string) =>
  http.post('/auth/change-password', { old_password, new_password }).then((r) => r.data)

// ---- 会话 ----
export const listSessions = () => http.get('/sessions').then((r) => r.data)
export const createSession = (title = '新会话') => http.post('/sessions', { title }).then((r) => r.data)
export const renameSession = (id: number, title: string) => http.patch(`/sessions/${id}`, { title }).then((r) => r.data)
export const deleteSession = (id: number) => http.delete(`/sessions/${id}`).then((r) => r.data)
export const listMessages = (sessionId: number) => http.get(`/sessions/${sessionId}/messages`).then((r) => r.data)

// ---- 知识库（管理员）----
export const listDocuments = () => http.get('/kb/documents').then((r) => r.data)
export const uploadDocument = (file: File) => {
  const form = new FormData()
  form.append('file', file)
  return http.post('/kb/upload', form).then((r) => r.data)
}
export const deleteDocument = (id: number) => http.delete(`/kb/documents/${id}`).then((r) => r.data)
export const getSuggestions = () => http.get('/kb/suggestions').then((r) => r.data)

// ---- 问答（SSE 流式，用 fetch 读取流）----
export interface ChatStreamHandlers {
  onDelta: (text: string) => void
  onDone: (sources: any[]) => void
  onError: (msg: string) => void
}

export async function streamChat(
  sessionId: number,
  question: string,
  handlers: ChatStreamHandlers,
): Promise<void> {
  const token = localStorage.getItem('token')
  const res = await fetch('/api/chat', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify({ session_id: sessionId, question }),
  })

  if (!res.ok || !res.body) {
    handlers.onError(`请求失败 (${res.status})`)
    return
  }

  const reader = res.body.getReader()
  const decoder = new TextDecoder('utf-8')
  let buffer = ''

  while (true) {
    const { done, value } = await reader.read()
    if (done) break
    buffer += decoder.decode(value, { stream: true })
    // SSE 事件以空行分隔
    const events = buffer.split('\n\n')
    buffer = events.pop() ?? ''
    for (const evt of events) {
      const line = evt.trim()
      if (!line.startsWith('data:')) continue
      const payload = line.slice(5).trim()
      if (!payload) continue
      try {
        const data = JSON.parse(payload)
        if (data.type === 'delta') handlers.onDelta(data.content)
        else if (data.type === 'done') handlers.onDone(data.sources ?? [])
        else if (data.type === 'error') handlers.onError(data.message ?? '生成失败')
      } catch {
        // 忽略无法解析的分片
      }
    }
  }
}
