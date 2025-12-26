import { useState, useEffect } from 'react'
import { Input, Typography, Alert } from 'antd'

const { TextArea } = Input
const { Text } = Typography

interface JsonSchemaEditorProps {
  value?: Record<string, unknown>
  onChange?: (value: Record<string, unknown> | undefined) => void
}

const defaultSchema = {
  type: 'object',
  properties: {},
  required: []
}

export function JsonSchemaEditor({ value, onChange }: JsonSchemaEditorProps) {
  const [textValue, setTextValue] = useState(() => {
    if (value) {
      return JSON.stringify(value, null, 2)
    }
    return JSON.stringify(defaultSchema, null, 2)
  })
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (value) {
      setTextValue(JSON.stringify(value, null, 2))
    }
  }, [value])

  const handleChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    const newValue = e.target.value
    setTextValue(newValue)

    if (!newValue.trim()) {
      setError(null)
      onChange?.(undefined)
      return
    }

    try {
      const parsed = JSON.parse(newValue)
      setError(null)
      onChange?.(parsed)
    } catch (err) {
      setError('Invalid JSON')
    }
  }

  return (
    <div>
      <TextArea
        value={textValue}
        onChange={handleChange}
        rows={8}
        style={{ fontFamily: 'monospace', fontSize: '13px' }}
        placeholder={JSON.stringify(defaultSchema, null, 2)}
      />
      {error && (
        <Alert
          message={error}
          type="error"
          showIcon
          style={{ marginTop: '8px' }}
        />
      )}
      <Text type="secondary" style={{ display: 'block', marginTop: '8px', fontSize: '12px' }}>
        Define input parameters using JSON Schema format. Example: {"{ \"type\": \"object\", \"properties\": { \"query\": { \"type\": \"string\" } }, \"required\": [\"query\"] }"}
      </Text>
    </div>
  )
}
