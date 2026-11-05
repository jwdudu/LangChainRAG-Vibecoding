// 与后端 Pydantic schema 对应的 TypeScript 类型

export interface User {
  id: number
  username: string
  role: string
  created_at: string
}

export interface Session {
  id: number
  title: string
  created_at: string
  updated_at: string
}

export interface Source {
  doc_name: string
  content: string
  score?: number | null
}

export interface Message {
  id: number
  role: 'user' | 'assistant'
  content: string
  sources?: Source[] | null
  created_at: string
}

export interface DocumentItem {
  id: number
  filename: string
  file_type: string
  chunk_count: number
  status: string
  size: number
  created_at: string
}
