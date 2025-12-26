import { Modal, Typography } from 'antd'
import { ExclamationCircleOutlined } from '@ant-design/icons'

const { Text } = Typography

interface DeleteConfirmModalProps {
  open: boolean
  title?: string
  itemName: string
  onConfirm: () => void
  onCancel: () => void
  loading?: boolean
}

export function DeleteConfirmModal({
  open,
  title = 'Delete Confirmation',
  itemName,
  onConfirm,
  onCancel,
  loading = false
}: DeleteConfirmModalProps) {
  return (
    <Modal
      title={
        <span>
          <ExclamationCircleOutlined style={{ color: '#faad14', marginRight: '8px' }} />
          {title}
        </span>
      }
      open={open}
      onOk={onConfirm}
      onCancel={onCancel}
      okText="Delete"
      okButtonProps={{ danger: true, loading }}
      cancelText="Cancel"
    >
      <p>
        Are you sure you want to delete <Text strong>{itemName}</Text>?
      </p>
      <p>
        <Text type="secondary">This action cannot be undone.</Text>
      </p>
    </Modal>
  )
}
