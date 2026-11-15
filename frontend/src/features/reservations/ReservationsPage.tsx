import { statusLabel } from '../../utils/labels';
import { filterSelectOption } from '../../utils/selectSearch';
import { useQuery } from '@tanstack/react-query';
import { Alert, Button, Popconfirm, Select, Space, Table, Typography } from 'antd';
import { useState } from 'react';
import { getData } from '../../services/api';
import type { Page } from '../../services/api';
import { useAction } from '../../hooks/useAction';
import { errorMessage } from '../../utils/access';
import { CheckoutDialog, dateText } from '../borrowings/BorrowingsPage';
interface Reservation {
  id: number;
  doc_gia_id: number;
  sach_id: number;
  doc_gia_name: string;
  ten_sach: string;
  ngay_dat: string;
  ngay_het_han: string | null;
  trang_thai: string;
}
export function ReservationsPage({
  personal = false
}: {
  personal?: boolean;
}) {
  const [page, setPage] = useState(1);
  const [status, setStatus] = useState<string>();
  const [checkout, setCheckout] = useState<Reservation | null>(null);
  const action = useAction();
  const path = personal ? '/my-reservations' : '/reservations';
  const query = useQuery({
    queryKey: [path, page, status],
    queryFn: () => getData<Page<Reservation>>(path, {
      page,
      page_size: 20,
      status
    })
  });
  return <Space orientation="vertical" className="full-width" size="middle">
<Typography.Title level={1}>{personal ? 'Đặt trước của tôi' : 'Hàng đợi đặt trước'}</Typography.Title>
<Alert type="info" title={personal ? 'Đặt trước đầu sách từ màn hình Tra cứu sách. Khi sẵn sàng, vui lòng nhận trong thời hạn hiển thị.' : 'Xử lý theo thứ tự đặt trước. Chỉ đánh dấu sẵn sàng khi yêu cầu đứng đầu và có cuốn khả dụng. Hoàn tất bằng một phiếu mượn thực tế.'} />
<Select showSearch filterOption={filterSelectOption} className="filter-select" allowClear placeholder="Lọc trạng thái" aria-label="Lọc trạng thái" value={status} onChange={v => {
      setStatus(v);
      setPage(1);
    }} options={['PENDING', 'READY', 'COMPLETED', 'CANCELLED'].map(value => ({
      value,
      label: statusLabel(value)
    }))} />
{query.error && <Alert type="error" title={errorMessage(query.error)} />}
<Table<Reservation> rowKey="id" dataSource={query.data?.items} loading={query.isLoading} scroll={{
      x: 850
    }} pagination={{
      current: page,
      total: query.data?.total,
      pageSize: 20,
      onChange: setPage,
      showSizeChanger: false
    }} columns={[{
      title: 'Đầu sách',
      dataIndex: 'ten_sach'
    }, {
      title: 'Độc giả',
      dataIndex: 'doc_gia_name'
    }, {
      title: 'Ngày đặt',
      render: (_, r) => dateText(r.ngay_dat)
    }, {
      title: 'Hạn nhận',
      render: (_, r) => dateText(r.ngay_het_han)
    }, {
      title: 'Trạng thái',
      dataIndex: 'trang_thai',
      render: (v: string) => statusLabel(v)
    }, {
      title: 'Thao tác',
      render: (_, r) => <Space wrap>
{!personal && <>
<Popconfirm title="Đánh dấu sẵn sàng theo FIFO?" onConfirm={() => action.mutateAsync({
            path: `/reservations/${r.id}/ready`
          })}><Button disabled={r.trang_thai !== 'PENDING'} loading={action.isPending}>Sẵn sàng</Button></Popconfirm>
<Button disabled={r.trang_thai !== 'READY'} onClick={() => setCheckout(r)}>Lập phiếu nhận</Button>
</>}
<Popconfirm title="Hủy yêu cầu đặt trước?" onConfirm={() => action.mutateAsync({
          path: `/reservations/${r.id}/cancel`
        })}><Button danger disabled={!['PENDING', 'READY'].includes(r.trang_thai)} loading={action.isPending}>Hủy đặt</Button></Popconfirm>
</Space>
    }]} />
{checkout && <CheckoutDialog reservation={checkout} onClose={() => setCheckout(null)} />}
</Space>;
}
