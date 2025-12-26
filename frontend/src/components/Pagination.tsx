import { Pagination as AntPagination } from 'antd'

interface PaginationProps {
  current: number
  total: number
  pageSize: number
  onChange: (page: number) => void
}

export function Pagination({ current, total, pageSize, onChange }: PaginationProps) {
  if (total <= pageSize) {
    return null
  }

  return (
    <AntPagination
      current={current}
      total={total}
      pageSize={pageSize}
      onChange={onChange}
      showSizeChanger={false}
      showQuickJumper={total > pageSize * 5}
      showTotal={(total, range) => `${range[0]}-${range[1]} of ${total} tools`}
    />
  )
}
