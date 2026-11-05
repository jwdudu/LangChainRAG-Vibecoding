import { useState } from 'react'
import { Layout, Menu, Dropdown, Avatar, Button } from 'antd'
import { Outlet, useNavigate, useLocation } from 'react-router-dom'
import {
  MessageOutlined,
  DatabaseOutlined,
  UserOutlined,
  LogoutOutlined,
  MenuFoldOutlined,
  MenuUnfoldOutlined,
} from '@ant-design/icons'
import { useAuth } from '../stores/auth'

const { Sider, Header, Content } = Layout

export default function MainLayout() {
  const navigate = useNavigate()
  const location = useLocation()
  const user = useAuth((s) => s.user)
  const logout = useAuth((s) => s.logout)
  const [collapsed, setCollapsed] = useState(false)

  const menuItems = [
    { key: '/chat', icon: <MessageOutlined />, label: '我的会话' },
    // 只有管理员能看到知识库管理入口
    ...(user?.role === 'admin' ? [{ key: '/kb', icon: <DatabaseOutlined />, label: '知识库管理' }] : []),
    { key: '/profile', icon: <UserOutlined />, label: '个人中心' },
  ]

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  return (
    <Layout style={{ height: '100vh' }}>
      <Sider width={220} collapsible collapsed={collapsed} trigger={null} theme="dark">
        <div
          style={{
            color: '#fff',
            padding: 20,
            fontSize: collapsed ? 18 : 16,
            fontWeight: 600,
            textAlign: collapsed ? 'center' : 'left',
          }}
        >
          {collapsed ? 'RAG' : '商品知识库问答'}
        </div>
        <Menu
          theme="dark"
          mode="inline"
          selectedKeys={[location.pathname]}
          items={menuItems}
          onClick={(e) => navigate(e.key)}
        />
      </Sider>
      <Layout>
        <Header
          style={{
            background: '#fff',
            display: 'flex',
            alignItems: 'center',
            paddingInline: 16,
          }}
        >
          <Button
            type="text"
            icon={collapsed ? <MenuUnfoldOutlined /> : <MenuFoldOutlined />}
            onClick={() => setCollapsed(!collapsed)}
            style={{ fontSize: 16 }}
          />
          <div style={{ flex: 1 }} />
          <Dropdown
            menu={{
              items: [{ key: 'logout', icon: <LogoutOutlined />, label: '退出登录', onClick: handleLogout }],
            }}
          >
            <span style={{ cursor: 'pointer' }}>
              <Avatar size="small" icon={<UserOutlined />} style={{ marginRight: 8 }} />
              {user?.username}（{user?.role === 'admin' ? '管理员' : '用户'}）
            </span>
          </Dropdown>
        </Header>
        <Content style={{ padding: 16, overflow: 'auto' }}>
          <Outlet />
        </Content>
      </Layout>
    </Layout>
  )
}
