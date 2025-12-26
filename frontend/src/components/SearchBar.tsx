import { useState, useEffect, useCallback } from 'react'
import { Input } from 'antd'
import { SearchOutlined } from '@ant-design/icons'

interface SearchBarProps {
  value?: string
  onSearch: (value: string) => void
  placeholder?: string
  debounceMs?: number
}

export function SearchBar({
  value = '',
  onSearch,
  placeholder = 'Search...',
  debounceMs = 300
}: SearchBarProps) {
  const [inputValue, setInputValue] = useState(value)

  // Sync external value changes
  useEffect(() => {
    setInputValue(value)
  }, [value])

  // Debounced search
  useEffect(() => {
    const timer = setTimeout(() => {
      if (inputValue !== value) {
        onSearch(inputValue)
      }
    }, debounceMs)

    return () => clearTimeout(timer)
  }, [inputValue, value, onSearch, debounceMs])

  const handleChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    setInputValue(e.target.value)
  }, [])

  const handlePressEnter = useCallback(() => {
    onSearch(inputValue)
  }, [inputValue, onSearch])

  return (
    <Input
      value={inputValue}
      onChange={handleChange}
      onPressEnter={handlePressEnter}
      placeholder={placeholder}
      prefix={<SearchOutlined />}
      allowClear
      size="large"
      style={{ maxWidth: '400px' }}
    />
  )
}
