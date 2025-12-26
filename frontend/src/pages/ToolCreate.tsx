import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Card, Typography, Button, message } from 'antd'
import { ArrowLeftOutlined } from '@ant-design/icons'
import { ToolForm } from '@/components/ToolForm'
import { toolApi } from '@/services/toolApi'

const { Title } = Typography

export function ToolCreate() {
  const navigate = useNavigate()
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (values: Parameters<typeof toolApi.createTool>[0]) => {
    setLoading(true)
    try {
      const tool = await toolApi.createTool(values)
      message.success('Tool created successfully')
      navigate(`/tools/${tool.id}`)
    } catch (error) {
      console.error(error)
      message.error('Failed to create tool')
    } finally {
      setLoading(false)
    }
  }

  const handleCancel = () => {
    navigate('/tools')
  }

  return (
    <div style={{ padding: '24px' }}>
      <div style={{ marginBottom: '24px' }}>
        <Button icon={<ArrowLeftOutlined />} onClick={() => navigate('/tools')}>
          Back to Tools
        </Button>
      </div>

      <Card>
        <Title level={3} style={{ marginBottom: '24px' }}>Create New Tool</Title>
        <ToolForm
          onSubmit={handleSubmit}
          onCancel={handleCancel}
          submitText="Create Tool"
          loading={loading}
        />
      </Card>
    </div>
  )
}
