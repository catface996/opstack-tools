import { useState } from 'react'
import { Card, Button, Input, Alert, Spin, Typography } from 'antd'
import { PlayCircleOutlined } from '@ant-design/icons'
import type { Tool } from '@/types'

const { TextArea } = Input
const { Text } = Typography

interface ToolTestPanelProps {
  tool: Tool
  onExecute: (inputData: Record<string, unknown>) => Promise<{
    success: boolean
    result?: Record<string, unknown> | null
    error?: string | null
    duration_ms?: number
  }>
}

export function ToolTestPanel({ tool, onExecute }: ToolTestPanelProps) {
  const [inputValue, setInputValue] = useState(() => {
    // Default to empty object matching the schema
    if (tool.input_schema && tool.input_schema.properties) {
      const defaultObj: Record<string, unknown> = {}
      const props = tool.input_schema.properties as Record<string, { type?: string }>
      for (const key of Object.keys(props)) {
        const propType = props[key]?.type
        if (propType === 'string') defaultObj[key] = ''
        else if (propType === 'number' || propType === 'integer') defaultObj[key] = 0
        else if (propType === 'boolean') defaultObj[key] = false
        else if (propType === 'array') defaultObj[key] = []
        else if (propType === 'object') defaultObj[key] = {}
      }
      return JSON.stringify(defaultObj, null, 2)
    }
    return '{}'
  })
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<{
    success: boolean
    result?: Record<string, unknown> | null
    error?: string | null
    duration_ms?: number
  } | null>(null)
  const [parseError, setParseError] = useState<string | null>(null)

  const handleExecute = async () => {
    setParseError(null)
    setResult(null)

    let inputData: Record<string, unknown>
    try {
      inputData = JSON.parse(inputValue)
    } catch (err) {
      setParseError('Invalid JSON input')
      return
    }

    setLoading(true)
    try {
      const execResult = await onExecute(inputData)
      setResult(execResult)
    } catch (err) {
      setResult({
        success: false,
        error: err instanceof Error ? err.message : 'Execution failed',
      })
    } finally {
      setLoading(false)
    }
  }

  return (
    <Card
      type="inner"
      title="Test Tool"
      style={{ marginTop: '16px' }}
      extra={
        <Button
          type="primary"
          icon={<PlayCircleOutlined />}
          onClick={handleExecute}
          loading={loading}
          disabled={!tool.is_active}
        >
          Execute
        </Button>
      }
    >
      <div style={{ marginBottom: '16px' }}>
        <Text strong>Input (JSON):</Text>
        <TextArea
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          rows={6}
          style={{ fontFamily: 'monospace', marginTop: '8px' }}
          placeholder="{}"
        />
        {parseError && (
          <Alert message={parseError} type="error" showIcon style={{ marginTop: '8px' }} />
        )}
      </div>

      {loading && (
        <div style={{ textAlign: 'center', padding: '24px' }}>
          <Spin tip="Executing..." />
        </div>
      )}

      {result && (
        <div>
          <Text strong>Result:</Text>
          {result.success ? (
            <Alert
              message="Success"
              description={
                <div>
                  {result.duration_ms !== undefined && (
                    <Text type="secondary" style={{ display: 'block', marginBottom: '8px' }}>
                      Duration: {result.duration_ms}ms
                    </Text>
                  )}
                  <pre style={{ margin: 0, overflow: 'auto', maxHeight: '200px' }}>
                    {JSON.stringify(result.result, null, 2)}
                  </pre>
                </div>
              }
              type="success"
              showIcon
              style={{ marginTop: '8px' }}
            />
          ) : (
            <Alert
              message="Error"
              description={
                <div>
                  {result.duration_ms !== undefined && (
                    <Text type="secondary" style={{ display: 'block', marginBottom: '8px' }}>
                      Duration: {result.duration_ms}ms
                    </Text>
                  )}
                  <pre style={{ margin: 0, overflow: 'auto' }}>
                    {result.error || 'Unknown error'}
                  </pre>
                </div>
              }
              type="error"
              showIcon
              style={{ marginTop: '8px' }}
            />
          )}
        </div>
      )}

      {!tool.is_active && (
        <Alert
          message="Tool is inactive"
          description="Activate this tool to enable execution."
          type="warning"
          showIcon
        />
      )}
    </Card>
  )
}
