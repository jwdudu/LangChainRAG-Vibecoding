import { useEffect, useMemo, useState } from 'react'
import { Table, Upload, Button, message, Popconfirm, Tag, Space, Card, Statistic, Row, Col, Select } from 'antd'
import {
  ReloadOutlined,
  InboxOutlined,
  FileTextOutlined,
  DatabaseOutlined,
  CheckCircleOutlined,
} from '@ant-design/icons'
import { listDocuments, uploadDocument, deleteDocument } from '../api'
import type { DocumentItem } from '../types'

const { Dragger } = Upload

const statusMap: Record<string, { color: string; text: string }> = {
  pending: { color: 'default', text: '待处理' },
  processing: { color: 'processing', text: '处理中' },
  done: { color: 'success', text: '已完成' },
  failed: { color: 'error', text: '失败' },
}

export default function KnowledgeBase() {
  const [docs, setDocs] = useState<DocumentItem[]>([])
  const [loading, setLoading] = useState(false)
  const [statusFilter, setStatusFilter] = useState('all')

  const load = async () => {
    setLoading(true)
    try {
      setDocs(await listDocuments())
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    load()
  }, [])

  const handleUpload = async (file: File) => {
    try {
      await uploadDocument(file)
      message.success(`已上传 ${file.name}，后台处理中`)
      load()
    } catch (e: any) {
      message.error(e.response?.data?.detail || '上传失败')
    }
    return false // 阻止 antd 自动上传，改由我们手动调用接口
  }

  const handleDelete = async (id: number) => {
    await deleteDocument(id)
    message.success('已删除')
    load()
  }

  // 统计卡片数据：从文档列表前端计算得出
  const stats = useMemo(
    () => ({
      total: docs.length,
      totalChunks: docs.reduce((s, d) => s + d.chunk_count, 0),
      indexed: docs.filter((d) => d.status === 'done').length,
      totalSize: docs.reduce((s, d) => s + d.size, 0),
    }),
    [docs],
  )

  const filteredDocs = statusFilter === 'all' ? docs : docs.filter((d) => d.status === statusFilter)

  const columns = [
    { title: '文件名', dataIndex: 'filename' },
    { title: '类型', dataIndex: 'file_type', width: 80 },
    { title: '大小', dataIndex: 'size', width: 100, render: (v: number) => formatSize(v) },
    { title: '块数', dataIndex: 'chunk_count', width: 80 },
    {
      title: '状态',
      dataIndex: 'status',
      width: 110,
      render: (v: string) => {
        const s = statusMap[v] || statusMap.pending
        return <Tag color={s.color}>{s.text}</Tag>
      },
    },
    {
      title: '上传时间',
      dataIndex: 'created_at',
      width: 170,
      render: (v: string) => new Date(v).toLocaleString(),
    },
    {
      title: '操作',
      width: 80,
      render: (_: unknown, r: DocumentItem) => (
        <Popconfirm title="删除该文档？" onConfirm={() => handleDelete(r.id)}>
          <Button danger size="small" type="text">
            删除
          </Button>
        </Popconfirm>
      ),
    },
  ]

  return (
    <div>
      {/* 统计卡片 */}
      <Row gutter={16} style={{ marginBottom: 16 }}>
        <Col span={6}>
          <Card>
            <Statistic title="文档总数" value={stats.total} prefix={<FileTextOutlined />} />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic title="文本块总数" value={stats.totalChunks} prefix={<DatabaseOutlined />} />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="已索引"
              value={stats.indexed}
              prefix={<CheckCircleOutlined />}
              valueStyle={{ color: '#3f8600' }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic title="总大小" value={formatSize(stats.totalSize)} />
          </Card>
        </Col>
      </Row>

      {/* 上传文档（支持拖拽） */}
      <Card title="上传文档" style={{ marginBottom: 16 }}>
        <Dragger beforeUpload={handleUpload} showUploadList={false} multiple>
          <p className="ant-upload-drag-icon">
            <InboxOutlined />
          </p>
          <p className="ant-upload-text">点击或拖拽文件到此处上传</p>
          <p className="ant-upload-hint">支持 TXT、Markdown、PDF、Word、Excel、CSV 格式，单文件最大 50MB</p>
        </Dragger>
      </Card>

      {/* 文档列表 */}
      <Card
        title="文档列表"
        extra={
          <Space>
            <Select
              value={statusFilter}
              onChange={setStatusFilter}
              style={{ width: 130 }}
              options={[
                { value: 'all', label: '全部状态' },
                { value: 'pending', label: '待处理' },
                { value: 'processing', label: '处理中' },
                { value: 'done', label: '已完成' },
                { value: 'failed', label: '失败' },
              ]}
            />
            <Button icon={<ReloadOutlined />} onClick={load}>
              刷新
            </Button>
          </Space>
        }
      >
        <Table rowKey="id" loading={loading} columns={columns} dataSource={filteredDocs} pagination={{ pageSize: 10 }} />
      </Card>
    </div>
  )
}

function formatSize(v: number) {
  if (v < 1024) return `${v} B`
  if (v < 1024 * 1024) return `${(v / 1024).toFixed(1)} KB`
  return `${(v / 1024 / 1024).toFixed(1)} MB`
}
