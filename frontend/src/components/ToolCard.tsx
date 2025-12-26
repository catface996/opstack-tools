import { Card, Tag, Typography } from 'antd'
import { CodeOutlined, ApiOutlined } from '@ant-design/icons'
import type { Tool } from '@/types'

const { Text, Paragraph } = Typography

interface ToolCardProps {
  tool: Tool
  onClick?: () => void
}

export function ToolCard({ tool, onClick }: ToolCardProps) {
  const executorIcon = tool.executor_type === 'python'
    ? <CodeOutlined />
    : <ApiOutlined />

  return (
    <Card
      hoverable
      onClick={onClick}
      style={{ height: '100%' }}
      styles={{ body: { padding: '16px' } }}
    >
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '8px' }}>
        <Text strong style={{ fontSize: '16px' }}>{tool.name}</Text>
        <Tag color={tool.is_active ? 'green' : 'default'}>
          {tool.is_active ? 'Active' : 'Inactive'}
        </Tag>
      </div>

      <Paragraph
        ellipsis={{ rows: 2 }}
        style={{ color: '#666', marginBottom: '12px' }}
      >
        {tool.description || 'No description'}
      </Paragraph>

      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Tag icon={executorIcon}>
          {tool.executor_type}
        </Tag>
        <Text type="secondary" style={{ fontSize: '12px' }}>
          v{tool.version}
        </Text>
      </div>
    </Card>
  )
}
