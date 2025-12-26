import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { ToolList } from '@/pages/ToolList'
import { ToolDetail } from '@/pages/ToolDetail'
import { ToolCreate } from '@/pages/ToolCreate'
import { ToolEdit } from '@/pages/ToolEdit'
import { Layout } from '@/components/Layout'
import { ErrorBoundary } from '@/components/ErrorBoundary'

function App() {
  return (
    <ErrorBoundary>
      <BrowserRouter>
        <Layout>
          <Routes>
            <Route path="/" element={<Navigate to="/tools" replace />} />
            <Route path="/tools" element={<ToolList />} />
            <Route path="/tools/new" element={<ToolCreate />} />
            <Route path="/tools/:id" element={<ToolDetail />} />
            <Route path="/tools/:id/edit" element={<ToolEdit />} />
          </Routes>
        </Layout>
      </BrowserRouter>
    </ErrorBoundary>
  )
}

export default App
