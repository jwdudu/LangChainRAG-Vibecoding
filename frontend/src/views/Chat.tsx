import { useEffect, useRef, useState } from 'react'
import { Layout, List, Input, Button, message, Popconfirm, Tag, Spin, Modal } from 'antd'
import { PlusOutlined, DeleteOutlined, SendOutlined, EditOutlined, MessageOutlined } from '@ant-design/icons'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import { listSessions, createSession, deleteSession, renameSession, listMessages, streamChat, getSuggestions } from '../api'
import type { Session, Message, Source } from '../types'

export default function Chat() {
  const [sessions, setSessions] = useState<Session[]>([])
  const [currentId, setCurrentId] = useState<number | null>(null)
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')
  const [streaming, setStreaming] = useState(false)
  const [streamText, setStreamText] = useState('')
  const [renameId, setRenameId] = useState<number | null>(null)
  const [renameTitle, setRenameTitle] = useState('')
  const [systemQuestions, setSystemQuestions] = useState<string[]>([])
  const [kbQuestions, setKbQuestions] = useState<string[]>([])
  const [kbIndex, setKbIndex] = useState(0)
  const bottomRef = useRef<HTMLDivElement>(null)

  const loadSessions = async () => {
    setSessions(await listSessions())
  }

  useEffect(() => {
    loadSessions()
  }, [])

  // 拉取示例问题（系统问题 + 知识库相关问题）
  useEffect(() => {
    getSuggestions()
      .then((d: { system?: string[]; kb?: string[] }) => {
        setSystemQuestions(d.system || [])
        setKbQuestions(d.kb || [])
      })
      .catch(() => {
        // 拉取失败时给个兜底
        setSystemQuestions(['你能帮我做什么？'])
        setKbQuestions(['帮我推荐一个尺码', '这款商品支持退换吗？'])
      })
  }, [])

  // 知识库相关问题每 6 秒轮换一批（轮播）
  useEffect(() => {
    if (kbQuestions.length <= 2) return
    const timer = setInterval(() => {
      setKbIndex((i) => (i + 2) % kbQuestions.length)
    }, 6000)
    return () => clearInterval(timer)
  }, [kbQuestions.length])

  useEffect(() => {
    if (currentId) {
      listMessages(currentId).then(setMessages)
    }
  }, [currentId])

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, streamText])

  // 当前要展示的问题：1 条系统问题（固定）+ 最多 2 条知识库问题（轮播）
  const displayQuestions = (() => {
    const result: string[] = []
    if (systemQuestions.length > 0) result.push(systemQuestions[0])
    if (kbQuestions.length === 1) result.push(kbQuestions[0])
    else if (kbQuestions.length >= 2) {
      const i = kbIndex % kbQuestions.length
      result.push(kbQuestions[i], kbQuestions[(i + 1) % kbQuestions.length])
    }
    return result
  })()

  const handleNewSession = async () => {
    const s = await createSession()
    setSessions((prev) => [s, ...prev])
    setCurrentId(s.id)
    setMessages([])
  }

  const handleDeleteSession = async (id: number) => {
    await deleteSession(id)
    loadSessions()
    if (id === currentId) {
      setCurrentId(null)
      setMessages([])
    }
  }

  const openRename = (s: Session) => {
    setRenameId(s.id)
    setRenameTitle(s.title)
  }

  const handleRename = async () => {
    if (renameId == null) return
    await renameSession(renameId, renameTitle.trim() || '新会话')
    setRenameId(null)
    loadSessions()
  }

  const handleSend = async () => {
    if (!input.trim() || streaming || !currentId) return
    const question = input.trim()
    setInput('')
    setMessages((prev) => [...prev, { id: Date.now(), role: 'user', content: question, created_at: '' }])
    setStreaming(true)
    setStreamText('')

    let acc = ''
    await streamChat(currentId, question, {
      onDelta: (t) => {
        acc += t
        setStreamText(acc)
      },
      onDone: (sources) => {
        setMessages((prev) => [
          ...prev,
          { id: Date.now() + 1, role: 'assistant', content: acc, sources, created_at: '' },
        ])
        setStreamText('')
        setStreaming(false)
        loadSessions() // 刷新会话标题
      },
      onError: (msg) => {
        message.error(msg)
        setStreaming(false)
      },
    })
  }

  // 点击示例问题：若还没会话则自动新建，再填入输入框
  const handleExample = async (q: string) => {
    if (!currentId) {
      const s = await createSession()
      setSessions((prev) => [s, ...prev])
      setCurrentId(s.id)
      setMessages([])
    }
    setInput(q)
  }

  return (
    <Layout style={{ height: '100%', background: '#fff' }}>
      <Layout.Sider width={260} theme="light" style={{ background: '#fafafa', borderRight: '1px solid #eee' }}>
        <div style={{ padding: 12 }}>
          <Button type="primary" icon={<PlusOutlined />} block onClick={handleNewSession}>
            新建会话
          </Button>
        </div>
        <List
          size="small"
          dataSource={sessions}
          style={{ padding: '0 8px' }}
          renderItem={(s) => (
            <List.Item
              onClick={() => setCurrentId(s.id)}
              style={{
                cursor: 'pointer',
                background: s.id === currentId ? '#e6f4ff' : undefined,
                paddingInline: 8,
                borderRadius: 6,
              }}
              actions={[
                <EditOutlined
                  key="edit"
                  onClick={(e) => {
                    e.stopPropagation()
                    openRename(s)
                  }}
                />,
                <Popconfirm key="del" title="删除该会话？" onConfirm={() => handleDeleteSession(s.id)}>
                  <DeleteOutlined onClick={(e) => e.stopPropagation()} />
                </Popconfirm>,
              ]}
            >
              {s.title}
            </List.Item>
          )}
        />
      </Layout.Sider>

      <Layout.Content style={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
        <div style={{ flex: 1, overflow: 'auto', padding: 16 }}>
          {messages.length === 0 && !streamText ? (
            <EmptyState hasSession={currentId != null} onExample={handleExample} questions={displayQuestions} />
          ) : (
            messages.map((m) => (
              <div key={m.id} style={{ marginBottom: 16, textAlign: m.role === 'user' ? 'right' : 'left' }}>
                <div
                  style={{
                    display: 'inline-block',
                    maxWidth: '80%',
                    textAlign: 'left',
                    padding: '10px 14px',
                    borderRadius: 8,
                    background: m.role === 'user' ? '#1677ff' : '#f5f5f5',
                    color: m.role === 'user' ? '#fff' : '#000',
                  }}
                >
                  {m.role === 'assistant' ? (
                    <ReactMarkdown remarkPlugins={[remarkGfm]}>{m.content}</ReactMarkdown>
                  ) : (
                    m.content
                  )}
                  {m.sources && m.sources.length > 0 && <SourceList sources={m.sources} />}
                </div>
              </div>
            ))
          )}
          {streamText && (
            <div style={{ marginBottom: 16 }}>
              <div
                style={{
                  display: 'inline-block',
                  maxWidth: '80%',
                  padding: '10px 14px',
                  borderRadius: 8,
                  background: '#f5f5f5',
                }}
              >
                <ReactMarkdown remarkPlugins={[remarkGfm]}>{streamText}</ReactMarkdown>
                <Spin size="small" style={{ marginLeft: 8 }} />
              </div>
            </div>
          )}
          <div ref={bottomRef} />
        </div>

        <div style={{ padding: 16, borderTop: '1px solid #eee' }}>
          <div style={{ display: 'flex', gap: 8 }}>
            <Input.TextArea
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onPressEnter={(e) => {
                if (!e.shiftKey) {
                  e.preventDefault()
                  handleSend()
                }
              }}
              placeholder="输入您的问题，按 Enter 发送，Shift+Enter 换行"
              autoSize={{ minRows: 1, maxRows: 4 }}
              disabled={!currentId}
            />
            <Button type="primary" icon={<SendOutlined />} onClick={handleSend} loading={streaming}>
              发送
            </Button>
          </div>
          <div style={{ textAlign: 'center', fontSize: 12, color: '#bbb', marginTop: 8 }}>
            回答基于知识库内容生成，可能存在偏差，请以实际商品信息为准
          </div>
        </div>
      </Layout.Content>

      <Modal title="重命名会话" open={renameId != null} onOk={handleRename} onCancel={() => setRenameId(null)}>
        <Input value={renameTitle} onChange={(e) => setRenameTitle(e.target.value)} maxLength={200} />
      </Modal>
    </Layout>
  )
}

function EmptyState({
  hasSession,
  onExample,
  questions,
}: {
  hasSession: boolean
  onExample: (q: string) => void
  questions: string[]
}) {
  return (
    <div style={{ textAlign: 'center', marginTop: 60, padding: '0 40px' }}>
      <div
        style={{
          width: 64,
          height: 64,
          borderRadius: '50%',
          background: '#1677ff',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          margin: '0 auto',
        }}
      >
        <MessageOutlined style={{ fontSize: 32, color: '#fff' }} />
      </div>
      <div style={{ marginTop: 24, fontSize: 22, fontWeight: 700, color: '#1a1a1a' }}>
        欢迎使用电商知识库问答系统
      </div>
      <div style={{ marginTop: 12, fontSize: 14, color: '#999' }}>
        {hasSession ? '请在下方输入您的问题开始提问' : '请在左侧选择会话或创建新会话开始提问'}
      </div>
      <div style={{ marginTop: 32, fontSize: 14, color: '#666' }}>
        提示：您可以询问任何关于电商商品的问题，例如：
      </div>
      <div style={{ marginTop: 16, display: 'flex', flexDirection: 'column', gap: 12, alignItems: 'center' }}>
        {questions.map((q) => (
          <div
            key={q}
            onClick={() => onExample(q)}
            style={{
              cursor: 'pointer',
              width: 380,
              maxWidth: '100%',
              padding: '12px 16px',
              background: '#f5f5f5',
              borderRadius: 10,
              display: 'flex',
              alignItems: 'center',
              gap: 8,
              fontSize: 14,
              color: '#333',
            }}
          >
            <MessageOutlined style={{ color: '#1677ff' }} />
            <span>{q}</span>
          </div>
        ))}
      </div>
    </div>
  )
}

function SourceList({ sources }: { sources: Source[] }) {
  const [open, setOpen] = useState(false)
  return (
    <div style={{ marginTop: 8, borderTop: '1px dashed #ddd', paddingTop: 8, fontSize: 12 }}>
      <div
        onClick={() => setOpen((o) => !o)}
        style={{
          cursor: 'pointer',
          userSelect: 'none',
          display: 'flex',
          alignItems: 'center',
          gap: 6,
          fontWeight: 600,
          color: '#1677ff',
        }}
      >
        <span
          style={{
            display: 'inline-block',
            transition: 'transform 0.2s',
            transform: open ? 'rotate(90deg)' : 'rotate(0deg)',
            fontSize: 10,
          }}
        >
          ▶
        </span>
        引用来源（{sources.length}）
      </div>
      {open && (
        <div style={{ marginTop: 8 }}>
          {sources.map((s, i) => (
            <div key={i} style={{ marginBottom: 8, color: '#555', background: '#fafafa', padding: 8, borderRadius: 6 }}>
              <div>
                <Tag color="blue">{i + 1}</Tag>
                <span style={{ fontWeight: 500 }}>{s.doc_name}</span>
                {s.score != null && <span style={{ color: '#999' }}>（相关度 {s.score}）</span>}
              </div>
              <div style={{ marginTop: 4, whiteSpace: 'pre-wrap', color: '#333' }}>{s.content}</div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
