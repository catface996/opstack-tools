import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { Card, Typography, Button, Spin, message } from 'antd'
import { ArrowLeftOutlined } from '@ant-design/icons'
import { ToolForm } from '@/components/ToolForm'
import { toolApi } from '@/services/toolApi'
import type { Tool } from '@/types'

const { Title } = Typography

export function ToolEdit() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const [tool, setTool] = useState<Tool | null>(null)
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)

  useEffect(() => {
    async function fetchTool() {
      if (!id) return

      setLoading(true)
      try {
        const data = await toolApi.getTool(id)
        setTool(data)
      } catch (error) {
        message.error('Failed to load tool')
        console.error(error)
      } finally {
        setLoading(false)
      }
    }

    fetchTool()
  }, [id])

  const handleSubmit = async (values: Parameters<typeof toolApi.updateTool>[1]) => {
    if (!id) return

    setSaving(true)
    try {
      await toolApi.updateTool(id, values)
      message.success('Tool updated successfully')
      navigate(`/tools/${id}`)
    } catch (error) {
      console.error(error)
      message.error('Failed to update tool')
    } finally {
      setSaving(false)
    }
  }

  const handleCancel = () => {
    navigate(`/tools/${id}`)
  }

  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: '48px' }}>
        <Spin size="large" />
      </div>
    )
  }

  if (!tool) {
    return (
      <div style={{ padding: '24px' }}>
        <Button icon={<ArrowLeftOutlined />} onClick={() => navigate('/tools')}>
          Back to Tools
        </Button>
        <Card style={{ marginTop: '16px' }}>
          <p>Tool not found</p>
        </Card>
      </div>
    )
  }

  return (
    <div style={{ padding: '24px' }}>
      <div style={{ marginBottom: '24px' }}>
        <Button icon={<ArrowLeftOutlined />} onClick={() => navigate(`/tools/${id}`)}>
          Back to Tool
        </Button>
      </div>

      <Card>
        <Title level={3} style={{ marginBottom: '24px' }}>
          Edit Tool: {tool.name}
        </Title>
        <ToolForm
          initialValues={{
            name: tool.name,
            description: tool.description || undefined,
            executor_type: tool.executor_type,
            script_content: tool.script_content || undefined,
            input_schema: tool.input_schema || undefined,
            is_active: tool.is_active,
          }}
          onSubmit={handleSubmit}
          onCancel={handleCancel}
          submitText="Save Changes"
          loading={saving}
        />
      </Card>
    </div>
  )
}
