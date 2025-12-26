import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { Card, Descriptions, Tag, Button, Space, Spin, message, Typography } from 'antd'
import { ArrowLeftOutlined, EditOutlined, CodeOutlined, ApiOutlined, DeleteOutlined } from '@ant-design/icons'
import { toolApi } from '@/services/toolApi'
import { ToolTestPanel } from '@/components/ToolTestPanel'
import { DeleteConfirmModal } from '@/components/DeleteConfirmModal'
import type { Tool } from '@/types'
import api from '@/services/api'

const { Title, Text } = Typography

export function ToolDetail() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()

  const [tool, setTool] = useState<Tool | null>(null)
  const [loading, setLoading] = useState(true)
  const [deleteModalOpen, setDeleteModalOpen] = useState(false)
  const [deleting, setDeleting] = useState(false)
  const [toggling, setToggling] = useState(false)

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
          <Text type="secondary">Tool not found</Text>
        </Card>
      </div>
    )
  }

  const executorIcon = tool.executor_type === 'python'
    ? <CodeOutlined />
    : <ApiOutlined />

  return (
    <div style={{ padding: '24px' }}>
      <div style={{ marginBottom: '24px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Button icon={<ArrowLeftOutlined />} onClick={() => navigate('/tools')}>
          Back to Tools
        </Button>
        <Space>
          <Button
            type="primary"
            icon={<EditOutlined />}
            onClick={() => navigate(`/tools/${id}/edit`)}
          >
            Edit
          </Button>
          <Button
            danger
            icon={<DeleteOutlined />}
            onClick={() => setDeleteModalOpen(true)}
          >
            Delete
          </Button>
        </Space>
      </div>

      <Card>
        <div style={{ marginBottom: '16px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Title level={3} style={{ margin: 0 }}>{tool.name}</Title>
          <Space>
            <Button
              size="small"
              loading={toggling}
              onClick={async () => {
                if (!id) return
                setToggling(true)
                try {
                  const updated = await toolApi.updateTool(id, { is_active: !tool.is_active })
                  setTool(updated)
                  message.success(`Tool ${updated.is_active ? 'activated' : 'deactivated'}`)
                } catch (error) {
                  message.error('Failed to toggle status')
                  console.error(error)
                } finally {
                  setToggling(false)
                }
              }}
            >
              {tool.is_active ? 'Deactivate' : 'Activate'}
            </Button>
            <Tag color={tool.is_active ? 'green' : 'default'}>
              {tool.is_active ? 'Active' : 'Inactive'}
            </Tag>
            <Tag icon={executorIcon}>{tool.executor_type}</Tag>
          </Space>
        </div>

        <Text type="secondary">{tool.description || 'No description'}</Text>

        <Descriptions style={{ marginTop: '24px' }} column={2} bordered>
          <Descriptions.Item label="ID">{tool.id}</Descriptions.Item>
          <Descriptions.Item label="Version">{tool.version}</Descriptions.Item>
          <Descriptions.Item label="Created At">
            {new Date(tool.created_at).toLocaleString()}
          </Descriptions.Item>
          <Descriptions.Item label="Updated At">
            {new Date(tool.updated_at).toLocaleString()}
          </Descriptions.Item>
        </Descriptions>

        {tool.input_schema && (
          <Card
            type="inner"
            title="Input Schema"
            style={{ marginTop: '16px' }}
          >
            <pre style={{ margin: 0, overflow: 'auto' }}>
              {JSON.stringify(tool.input_schema, null, 2)}
            </pre>
          </Card>
        )}

        {tool.script_content && (
          <Card
            type="inner"
            title="Script Content"
            style={{ marginTop: '16px' }}
          >
            <pre style={{ margin: 0, overflow: 'auto', maxHeight: '400px' }}>
              {tool.script_content}
            </pre>
          </Card>
        )}

        {tool.executor_type === 'python' && tool.script_content && (
          <ToolTestPanel
            tool={tool}
            onExecute={async (inputData) => {
              const response = await api.post<{
                success: boolean
                result?: Record<string, unknown> | null
                error?: string | null
                duration_ms?: number
              }>(`/llm/tools/${tool.name}/invoke`, { arguments: inputData })
              return response.data
            }}
          />
        )}
      </Card>

      <DeleteConfirmModal
        open={deleteModalOpen}
        itemName={tool.name}
        onConfirm={async () => {
          if (!id) return
          setDeleting(true)
          try {
            await toolApi.deleteTool(id)
            message.success('Tool deleted successfully')
            navigate('/tools')
          } catch (error) {
            message.error('Failed to delete tool')
            console.error(error)
          } finally {
            setDeleting(false)
            setDeleteModalOpen(false)
          }
        }}
        onCancel={() => setDeleteModalOpen(false)}
        loading={deleting}
      />
    </div>
  )
}
