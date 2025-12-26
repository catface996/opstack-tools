import { ReactNode } from 'react'
import { useNavigate, useLocation } from 'react-router-dom'
import { Layout as AntLayout, Menu, Typography, Button } from 'antd'
import { ToolOutlined, PlusOutlined } from '@ant-design/icons'

const { Header, Content } = AntLayout
const { Title } = Typography

interface LayoutProps {
  children: ReactNode
}

export function Layout({ children }: LayoutProps) {
  const navigate = useNavigate()
  const location = useLocation()

  const menuItems = [
    {
      key: '/tools',
      icon: <ToolOutlined />,
      label: 'Tools',
      onClick: () => navigate('/tools'),
    },
  ]

  const selectedKey = location.pathname.startsWith('/tools') ? '/tools' : location.pathname

  return (
    <AntLayout style={{ minHeight: '100vh' }}>
      <Header style={{ display: 'flex', alignItems: 'center', background: '#001529' }}>
        <Title
          level={4}
          style={{ color: 'white', margin: 0, marginRight: '24px', cursor: 'pointer' }}
          onClick={() => navigate('/')}
        >
          AIOps Tools
        </Title>
        <Menu
          theme="dark"
          mode="horizontal"
          selectedKeys={[selectedKey]}
          items={menuItems}
          style={{ flex: 1, minWidth: 0 }}
        />
        <Button
          type="primary"
          icon={<PlusOutlined />}
          onClick={() => navigate('/tools/new')}
        >
          New Tool
        </Button>
      </Header>
      <Content style={{ background: '#f5f5f5', minHeight: 'calc(100vh - 64px)' }}>
        {children}
      </Content>
    </AntLayout>
  )
}
