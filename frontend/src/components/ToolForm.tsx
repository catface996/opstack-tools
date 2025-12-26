import { Form, Input, Select, Switch, Button, Space, message } from 'antd'
import { MonacoEditor } from '@/components/MonacoEditor'
import { JsonSchemaEditor } from '@/components/JsonSchemaEditor'

const { TextArea } = Input

interface ToolFormValues {
  name: string
  description?: string
  executor_type: string
  script_content?: string
  input_schema?: Record<string, unknown>
  is_active: boolean
}

interface ToolFormProps {
  initialValues?: Partial<ToolFormValues>
  onSubmit: (values: ToolFormValues) => Promise<void>
  onCancel: () => void
  submitText?: string
  loading?: boolean
}

export function ToolForm({
  initialValues,
  onSubmit,
  onCancel,
  submitText = 'Create',
  loading = false
}: ToolFormProps) {
  const [form] = Form.useForm<ToolFormValues>()
  const executorType = Form.useWatch('executor_type', form)

  const handleFinish = async (values: ToolFormValues) => {
    try {
      await onSubmit(values)
    } catch (error) {
      console.error(error)
      message.error('Failed to save tool')
    }
  }

  const defaultValues: Partial<ToolFormValues> = {
    executor_type: 'python',
    is_active: true,
    ...initialValues
  }

  return (
    <Form
      form={form}
      layout="vertical"
      initialValues={defaultValues}
      onFinish={handleFinish}
    >
      <Form.Item
        name="name"
        label="Name"
        rules={[
          { required: true, message: 'Please enter a tool name' },
          { pattern: /^[a-z][a-z0-9_]*$/, message: 'Name must be lowercase, start with a letter, and contain only letters, numbers, and underscores' },
          { max: 100, message: 'Name must be at most 100 characters' }
        ]}
        tooltip="Tool name in snake_case format (e.g., get_weather, calculate_sum)"
      >
        <Input placeholder="my_tool_name" />
      </Form.Item>

      <Form.Item
        name="description"
        label="Description"
        rules={[
          { max: 500, message: 'Description must be at most 500 characters' }
        ]}
      >
        <TextArea rows={3} placeholder="Describe what this tool does..." />
      </Form.Item>

      <Form.Item
        name="executor_type"
        label="Executor Type"
        rules={[{ required: true, message: 'Please select an executor type' }]}
      >
        <Select>
          <Select.Option value="python">Python</Select.Option>
          <Select.Option value="http">HTTP</Select.Option>
        </Select>
      </Form.Item>

      {executorType === 'python' && (
        <Form.Item
          name="script_content"
          label="Python Script"
          rules={[
            { required: executorType === 'python', message: 'Script is required for Python executor' }
          ]}
          tooltip="Python script that receives input via stdin as JSON and outputs result as JSON to stdout"
        >
          <MonacoEditor
            language="python"
            height="300px"
            defaultValue={initialValues?.script_content || `import json
import sys

# Read input from stdin
input_data = json.loads(sys.stdin.read())

# Your code here
result = {}

# Output result as JSON
print(json.dumps(result))
`}
          />
        </Form.Item>
      )}

      <Form.Item
        name="input_schema"
        label="Input Schema (JSON Schema)"
        tooltip="JSON Schema defining the input parameters for this tool"
      >
        <JsonSchemaEditor />
      </Form.Item>

      <Form.Item
        name="is_active"
        label="Active"
        valuePropName="checked"
      >
        <Switch />
      </Form.Item>

      <Form.Item>
        <Space>
          <Button type="primary" htmlType="submit" loading={loading}>
            {submitText}
          </Button>
          <Button onClick={onCancel}>
            Cancel
          </Button>
        </Space>
      </Form.Item>
    </Form>
  )
}
