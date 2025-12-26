import api from './api'

export interface ToolCategory {
  id: string
  name: string
  description?: string
  icon?: string
  color?: string
  created_at: string
  updated_at: string
}

interface CreateCategoryParams {
  name: string
  description?: string
  icon?: string
  color?: string
}

interface UpdateCategoryParams {
  name?: string
  description?: string
  icon?: string
  color?: string
}

export const categoryApi = {
  // Category CRUD operations - All POST mode
  async listCategories(): Promise<ToolCategory[]> {
    const response = await api.post<ToolCategory[]>('/tools/categories/list')
    return response.data
  },

  async getCategory(id: string): Promise<ToolCategory> {
    const response = await api.post<ToolCategory>('/tools/categories/get', { category_id: id })
    return response.data
  },

  async createCategory(data: CreateCategoryParams): Promise<ToolCategory> {
    const response = await api.post<ToolCategory>('/tools/categories/create', data)
    return response.data
  },

  async updateCategory(id: string, data: UpdateCategoryParams): Promise<ToolCategory> {
    const response = await api.post<ToolCategory>('/tools/categories/update', { category_id: id, ...data })
    return response.data
  },

  async deleteCategory(id: string): Promise<void> {
    await api.post('/tools/categories/delete', { category_id: id })
  },
}
