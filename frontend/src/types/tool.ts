export interface Tool {
  id: string
  name: string
  description: string
  category_id: string | null
  executor_type: string
  script_content: string | null
  input_schema: Record<string, unknown> | null
  output_schema: Record<string, unknown> | null
  is_active: boolean
  version: number
  created_at: string
  updated_at: string
}

export interface ToolCategory {
  id: string
  name: string
  description: string | null
  icon: string | null
}

export interface ToolListResponse {
  items: Tool[]
  total: number
  page: number
  size: number
  pages: number
}

export interface ToolExecutionRequest {
  input_data: Record<string, unknown>
}

export interface ToolExecutionResponse {
  execution_id: string
  tool_id: string
  status: 'pending' | 'running' | 'completed' | 'failed'
  output_data: Record<string, unknown> | null
  error_message: string | null
  duration_ms: number | null
  created_at: string
}
