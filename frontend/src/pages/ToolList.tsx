import { useState, useEffect, useCallback } from 'react'
import { useSearchParams, useNavigate } from 'react-router-dom'
import { Row, Col, Empty, Spin, message } from 'antd'
import { ToolCard } from '@/components/ToolCard'
import { SearchBar } from '@/components/SearchBar'
import { Pagination } from '@/components/Pagination'
import { toolApi } from '@/services/toolApi'
import type { Tool } from '@/types'

const PAGE_SIZE = 12

export function ToolList() {
  const [searchParams, setSearchParams] = useSearchParams()
  const navigate = useNavigate()

  const [tools, setTools] = useState<Tool[]>([])
  const [total, setTotal] = useState(0)
  const [loading, setLoading] = useState(true)

  const page = Number(searchParams.get('page')) || 1
  const keyword = searchParams.get('q') || ''

  const fetchTools = useCallback(async () => {
    setLoading(true)
    try {
      const response = await toolApi.getTools({
        page,
        size: PAGE_SIZE,
        search: keyword || undefined,
      })
      setTools(response.items)
      setTotal(response.total)
    } catch (error) {
      message.error('Failed to load tools')
      console.error(error)
    } finally {
      setLoading(false)
    }
  }, [page, keyword])

  useEffect(() => {
    fetchTools()
  }, [fetchTools])

  const handleSearch = useCallback((value: string) => {
    const params = new URLSearchParams(searchParams)
    if (value) {
      params.set('q', value)
    } else {
      params.delete('q')
    }
    params.set('page', '1')
    setSearchParams(params)
  }, [searchParams, setSearchParams])

  const handlePageChange = useCallback((newPage: number) => {
    const params = new URLSearchParams(searchParams)
    params.set('page', String(newPage))
    setSearchParams(params)
  }, [searchParams, setSearchParams])

  const handleToolClick = useCallback((tool: Tool) => {
    navigate(`/tools/${tool.id}`)
  }, [navigate])

  return (
    <div style={{ padding: '24px' }}>
      <div style={{ marginBottom: '24px' }}>
        <SearchBar
          value={keyword}
          onSearch={handleSearch}
          placeholder="Search tools by name or description..."
        />
      </div>

      {loading ? (
        <div style={{ textAlign: 'center', padding: '48px' }}>
          <Spin size="large" />
        </div>
      ) : tools.length === 0 ? (
        <Empty description="No tools found" />
      ) : (
        <>
          <Row gutter={[16, 16]}>
            {tools.map((tool) => (
              <Col key={tool.id} xs={24} sm={12} md={8} lg={6}>
                <ToolCard tool={tool} onClick={() => handleToolClick(tool)} />
              </Col>
            ))}
          </Row>

          <div style={{ marginTop: '24px', textAlign: 'center' }}>
            <Pagination
              current={page}
              total={total}
              pageSize={PAGE_SIZE}
              onChange={handlePageChange}
            />
          </div>
        </>
      )}
    </div>
  )
}
