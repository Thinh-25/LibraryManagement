import { useQuery } from '@tanstack/react-query';
import { Alert, Button, Card, Space, Spin, Typography } from 'antd';
import { getHealth } from '../../services/health';

const { Title, Paragraph, Text } = Typography;

export function StartupPage() {
  const health = useQuery({ queryKey: ['health'], queryFn: getHealth });

  return (
    <main className="startup-page">
      <header className="startup-header">
        <Text className="eyebrow">LIBRARY MANAGEMENT SYSTEM</Text>
        <Title>Quản lý thư viện</Title>
        <Paragraph>Nền tảng kết nối tri thức và bạn đọc.</Paragraph>
      </header>
      <Card title="Kết nối hệ thống">
        <Space orientation="vertical" size="large" className="full-width">
          <Paragraph>
            Bộ khung dự án đã sẵn sàng để phát triển quản lý sách, bạn đọc và hoạt động mượn trả.
          </Paragraph>
          <div role="status" aria-live="polite">
            {health.isPending && <Space><Spin size="small" /><span>Đang kiểm tra kết nối…</span></Space>}
            {health.isError && <Alert type="error" showIcon title="Chưa kết nối được máy chủ" description="Vui lòng kiểm tra máy chủ và thử lại." />}
            {health.isSuccess && <Alert type="success" showIcon title="Máy chủ đang hoạt động" description="Kết nối API thành công. Trạng thái cơ sở dữ liệu chưa được kiểm tra." />}
          </div>
          <Button onClick={() => void health.refetch()} loading={health.isFetching}>
            Kiểm tra lại
          </Button>
        </Space>
      </Card>
    </main>
  );
}
