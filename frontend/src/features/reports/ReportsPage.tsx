import { useQuery } from '@tanstack/react-query';
import { Alert, Button, Card, Col, Form, Input, Row, Space, Statistic, Table, Typography } from 'antd';
import { useState } from 'react';
import { getData } from '../../services/api';
import { errorMessage } from '../../utils/access';
import { money } from '../fines/FinesPage';
interface Report {
  summary: {
    books: number;
    copies: number;
    readers: number;
    active_readers: number;
    borrowed: number;
    overdue: number;
    paid_fines: string;
    unpaid_fines: string;
  };
  monthly: {
    month: string;
    count: number;
  }[];
  popular: {
    id: number;
    ten_sach: string;
    count: number;
  }[];
}
export function ReportsPage({
  dashboard = false
}: {
  dashboard?: boolean;
}) {
  const [range, setRange] = useState<{
    start_date?: string;
    end_date?: string;
  }>({});
  const query = useQuery({
    queryKey: ['reports', range],
    queryFn: () => getData<Report>('/reports', range)
  });
  const summary = query.data?.summary;
  return <Space orientation="vertical" className="full-width" size="large">
<Typography.Title level={1}>{dashboard ? 'Tổng quan thư viện' : 'Báo cáo và thống kê'}</Typography.Title>
<Form layout="inline" onFinish={v => setRange({
      start_date: v.start_date || undefined,
      end_date: v.end_date || undefined
    })}>
<Form.Item label="Từ ngày" name="start_date"><Input type="date" /></Form.Item>
<Form.Item label="Đến ngày" name="end_date"><Input type="date" /></Form.Item>
<Button type="primary" htmlType="submit">Áp dụng</Button>
</Form>
<Typography.Text type="secondary">Khoảng ngày theo giờ Việt Nam. Tổng kho và dư nợ phản ánh dữ liệu nghiệp vụ; lượt mượn và tiền phạt theo khoảng báo cáo.</Typography.Text>
{query.error && <Alert type="error" title={errorMessage(query.error)} action={<Button onClick={() => void query.refetch()}>Thử lại</Button>} />}
<Row gutter={[16, 16]}>{[{
        title: 'Đầu sách',
        value: summary?.books
      }, {
        title: 'Cuốn sách',
        value: summary?.copies
      }, {
        title: 'Độc giả',
        value: summary?.readers
      }, {
        title: 'Độc giả hoạt động',
        value: summary?.active_readers
      }, {
        title: 'Đang mượn',
        value: summary?.borrowed
      }, {
        title: 'Quá hạn',
        value: summary?.overdue
      }, {
        title: 'Phạt đã thu',
        value: summary ? money(summary.paid_fines) : undefined
      }, {
        title: 'Phạt chưa thu',
        value: summary ? money(summary.unpaid_fines) : undefined
      }].map(s => <Col xs={24} sm={12} xl={6} key={s.title}><Card loading={query.isLoading}><Statistic title={s.title} value={s.value ?? '—'} /></Card></Col>)}</Row>
<Row gutter={[24, 24]}>
<Col xs={24} lg={12}>
<Typography.Title level={2}>Lượt mượn theo tháng</Typography.Title>
<Table rowKey="month" loading={query.isLoading} dataSource={query.data?.monthly} columns={[{
          title: 'Tháng',
          dataIndex: 'month'
        }, {
          title: 'Số cuốn mượn',
          dataIndex: 'count'
        }, {
          title: 'Phân bố lượt mượn',
          render: (_, r) => <div role="img" aria-label={`${r.count} lượt mượn`} className="chart-bar" style={{
            width: `${Math.max(1, r.count / Math.max(1, ...(query.data?.monthly.map(m => m.count) ?? [])) * 100)}%`
          }} />
        }]} pagination={false} />
</Col>
<Col xs={24} lg={12}>
<Typography.Title level={2}>Sách được mượn nhiều</Typography.Title>
<Table rowKey="id" loading={query.isLoading} dataSource={query.data?.popular} columns={[{
          title: 'Tên sách',
          dataIndex: 'ten_sach'
        }, {
          title: 'Số lượt mượn',
          dataIndex: 'count'
        }]} pagination={false} />
</Col>
</Row>
</Space>;
}
