import Editor, { OnChange } from '@monaco-editor/react'

interface MonacoEditorProps {
  value?: string
  defaultValue?: string
  onChange?: (value: string | undefined) => void
  language?: string
  height?: string
  readOnly?: boolean
}

export function MonacoEditor({
  value,
  defaultValue,
  onChange,
  language = 'python',
  height = '300px',
  readOnly = false
}: MonacoEditorProps) {
  const handleChange: OnChange = (newValue) => {
    onChange?.(newValue)
  }

  return (
    <div style={{ border: '1px solid #d9d9d9', borderRadius: '6px', overflow: 'hidden' }}>
      <Editor
        height={height}
        language={language}
        value={value}
        defaultValue={defaultValue}
        onChange={handleChange}
        options={{
          minimap: { enabled: false },
          fontSize: 14,
          lineNumbers: 'on',
          scrollBeyondLastLine: false,
          automaticLayout: true,
          tabSize: 4,
          readOnly,
          wordWrap: 'on'
        }}
        theme="vs-dark"
      />
    </div>
  )
}
