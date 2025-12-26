import api from './api'
import type { Tool, ToolListResponse } from '@/types'

interface ListToolsRequest {
  page?: number
  page_size?: number
  search?: string
  category_id?: string
  status?: string
}

interface CreateToolParams {
  name: string
  display_name?: string
  description?: string
  category_id?: string
  executor_type: string
  script_content?: string
  input_schema?: Record<string, unknown>
  output_schema?: Record<string, unknown>
  is_active?: boolean
}

interface UpdateToolParams {
  name?: string
  display_name?: string
  description?: string
  category_id?: string
  script_content?: string
  input_schema?: Record<string, unknown>
  output_schema?: Record<string, unknown>
  is_active?: boolean
}

export const toolApi = {
  // Tool CRUD operations - All POST mode
  async getTools(params: ListToolsRequest = {}): Promise<ToolListResponse> {
    const response = await api.post<ToolListResponse>('/tools/list', {
      page: params.page || 1,
      page_size: params.page_size || 20,
      search: params.search,
      category_id: params.category_id,
      status: params.status,
    })
    return response.data
  },

  async getTool(id: string): Promise<Tool> {
    const response = await api.post<Tool>('/tools/get', { tool_id: id })
    return response.data
  },

  async createTool(data: CreateToolParams): Promise<Tool> {
    const response = await api.post<Tool>('/tools/create', data)
    return response.data
  },

  async updateTool(id: string, data: UpdateToolParams): Promise<Tool> {
    const response = await api.post<Tool>('/tools/update', { tool_id: id, ...data })
    return response.data
  },

  async deleteTool(id: string): Promise<void> {
    await api.post('/tools/delete', { tool_id: id })
  },

  async activateTool(id: string): Promise<Tool> {
    const response = await api.post<Tool>('/tools/activate', { tool_id: id })
    return response.data
  },

  async deactivateTool(id: string): Promise<Tool> {
    const response = await api.post<Tool>('/tools/deactivate', { tool_id: id })
    return response.data
  },

  // LLM-compatible API (OpenAI function calling format)
  async listToolsForLLM() {
    const response = await api.post('/llm/tools/list')
    return response.data
  },

  async getToolForLLM(toolName: string) {
    const response = await api.post('/llm/tools/get', { tool_name: toolName })
    return response.data
  },

  async invokeTool(toolName: string, args: Record<string, unknown> = {}) {
    const response = await api.post('/llm/tools/invoke', {
      tool_name: toolName,
      arguments: args,
    })
    return response.data
  },
}
