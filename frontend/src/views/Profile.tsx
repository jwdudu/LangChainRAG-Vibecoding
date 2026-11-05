import { Card, Descriptions, Form, Input, Button, message } from 'antd'
import { useAuth } from '../stores/auth'
import { changePassword } from '../api'

export default function Profile() {
  const user = useAuth((s) => s.user)

  const onChangePwd = async (values: { old_password: string; new_password: string }) => {
    try {
      await changePassword(values.old_password, values.new_password)
      message.success('密码修改成功')
    } catch (e: any) {
      message.error(e.response?.data?.detail || '修改失败')
    }
  }

  return (
    <div style={{ maxWidth: 600 }}>
      <Card title="个人信息" style={{ marginBottom: 16 }}>
        <Descriptions column={1}>
          <Descriptions.Item label="用户名">{user?.username}</Descriptions.Item>
          <Descriptions.Item label="角色">{user?.role === 'admin' ? '管理员' : '普通用户'}</Descriptions.Item>
          <Descriptions.Item label="注册时间">
            {user?.created_at ? new Date(user.created_at).toLocaleString() : '-'}
          </Descriptions.Item>
        </Descriptions>
      </Card>
      <Card title="修改密码">
        <Form onFinish={onChangePwd} layout="vertical" style={{ maxWidth: 360 }}>
          <Form.Item name="old_password" label="旧密码" rules={[{ required: true, message: '请输入旧密码' }]}>
            <Input.Password />
          </Form.Item>
          <Form.Item name="new_password" label="新密码" rules={[{ required: true, min: 6, message: '至少 6 位' }]}>
            <Input.Password />
          </Form.Item>
          <Button type="primary" htmlType="submit">
            确认修改
          </Button>
        </Form>
      </Card>
    </div>
  )
}
