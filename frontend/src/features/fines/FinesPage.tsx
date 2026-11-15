import { statusLabel } from '../../utils/labels';
import { filterSelectOption } from '../../utils/selectSearch';
import { useQuery } from '@tanstack/react-query';
import { Alert, Button, Popconfirm, Select, Space, Table, Typography } from 'antd';
import { useState } from 'react';
import { getData } from '../../services/api';
import type { Page } from '../../services/api';
import { useAction } from '../../hooks/useAction';
import { EditDialog } from '../../components/ResourcePage';
import { errorMessage } from '../../utils/access';
import { dateText } from '../borrowings/BorrowingsPage';
interface Fine {
  id: number;
  chi_tiet_muon_id: number;
  doc_gia_name: string;
  ten_sach: string;
  ly_do: string;
  so_tien: string;
  trang_thai: string;
  ngay_tao: string;
  ngay_thanh_toan: string | null;
}
export const money = (v: string | number | undefined) => new Intl.NumberFormat('vi-VN', {
  style: 'currency',
  currency: 'VND'
}).format(Number(v ?? 0));
export function FinesPage({
  personal = false
}: {
  personal?: boolean;
}) {
  const [page, setPage] = useState(1);
  const [status, setStatus] = useState<string>();
  const [create, setCreate] = useState(false);
  const action = useAction();
  const path = personal ? '/my-fines' : '/fines';
  const query = useQuery({
    queryKey: [path, page, status],
    queryFn: () => getData<Page<Fine>>(path, {
      page,
      page_size: 20,
      status
    })
  });
  return <Space orientation="vertical" className="full-width" size="middle">
<Typography.Title level={1}>{personal ? 'Tiền phạt của tôi' : 'Quản lý tiền phạt'}</Typography.Title>
<Space>
<Select showSearch filterOption={filterSelectOption} aria-label="Trạng thái thanh toán" className="filter-select" allowClear placeholder="Trạng thái thanh toán" value={status} onChange={v => {
        setStatus(v);
        setPage(1);
      }} options={[{
        value: 'UNPAID',
        label: 'Chưa thanh toán'
      }, {
        value: 'PAID',
        label: 'Đã thanh toán'
      }]} />
{!personal && <Button type="primary" onClick={() => setCreate(true)}>Lập khoản phạt</Button>}
</Space>
{query.error && <Alert type="error" title={errorMessage(query.error)} />}
<Table<Fine> rowKey="id" dataSource={query.data?.items} loading={query.isLoading} scroll={{
      x: 1000
    }} pagination={{
      current: page,
      total: query.data?.total,
      pageSize: 20,
      onChange: setPage,
      showSizeChanger: false
    }} columns={[{
      title: 'Độc giả',
      dataIndex: 'doc_gia_name'
    }, {
      title: 'Sách',
      dataIndex: 'ten_sach'
    }, {
      title: 'Lượt mượn',
      dataIndex: 'chi_tiet_muon_id'
    }, {
      title: 'Lý do',
      dataIndex: 'ly_do'
    }, {
      title: 'Số tiền',
      render: (_, r) => money(r.so_tien)
    }, {
      title: 'Trạng thái',
      dataIndex: 'trang_thai',
      render: (v: string) => statusLabel(v)
    }, {
      title: 'Ngày lập / Thanh toán',
      render: (_, r) => <>
{dateText(r.ngay_tao)}
<br />
{dateText(r.ngay_thanh_toan)}
</>
    }, ...(!personal ? [{
      title: 'Thao tác',
      render: (_: unknown, r: Fine) => <Popconfirm title={`Xác nhận đã thu ${money(r.so_tien)}?`} description="Ghi nhận toàn bộ khoản phạt, không thể thu lần hai." onConfirm={() => action.mutateAsync({
        path: `/fines/${r.id}/pay`
      })}><Button disabled={r.trang_thai !== 'UNPAID'} loading={action.isPending}>Xác nhận thanh toán</Button></Popconfirm>
    }] : [])]} />
{create && <EditDialog title="Lập khoản phạt thủ công" fields={[{
      name: 'chi_tiet_muon_id',
      label: 'Mã lượt mượn (xem tại chi tiết phiếu mượn)',
      type: 'number',
      min: 1,
      required: true
    }, {
      name: 'ly_do',
      label: 'Lý do phạt',
      required: true
    }, {
      name: 'so_tien',
      label: 'Số tiền (VND)',
      type: 'number',
      min: 1,
      required: true
    }]} pending={action.isPending} onClose={() => setCreate(false)} onSave={v => action.mutate({
      path: '/fines',
      body: v
    }, {
      onSuccess: () => setCreate(false)
    })} />}
</Space>;
}
