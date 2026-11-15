import { statusLabel } from '../../utils/labels';
import { Alert, Button, Descriptions, Drawer, Input, Space, Table, Typography } from 'antd';
import { useQuery } from '@tanstack/react-query';
import { useState } from 'react';
import { EditDialog } from '../../components/ResourcePage';
import { useAction } from '../../hooks/useAction';
import { getData } from '../../services/api';
import type { Page } from '../../services/api';
import type { User } from '../../stores/session';
import { errorMessage } from '../../utils/access';
import { BorrowingsPage } from '../borrowings/BorrowingsPage';
interface Card {
  id: number;
  ma_the: string;
  ngay_cap: string;
  ngay_het_han: string;
  trang_thai: string;
}
interface Reader extends User {
  card: Card | null;
}
export function ReadersPage() {
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState('');
  const [selected, setSelected] = useState<Reader | null>(null);
  const [edit, setEdit] = useState(false);
  const action = useAction();
  const query = useQuery({
    queryKey: ['readers', page, search],
    queryFn: () => getData<Page<Reader>>('/readers', {
      page,
      page_size: 20,
      search
    })
  });
  const detail = useQuery({
    queryKey: ['reader', selected?.id],
    queryFn: () => getData<Reader>(`/readers/${selected?.id}`),
    enabled: !!selected
  });
  const reader = detail.data ?? selected;
  return <Space orientation="vertical" className="full-width" size="middle">
<Typography.Title level={1}>Độc giả và thẻ thư viện</Typography.Title>
<Input.Search placeholder="Tên hoặc email" aria-label="Tìm độc giả" onSearch={v => {
      setSearch(v);
      setPage(1);
    }} allowClear />
{query.error && <Alert type="error" title={errorMessage(query.error)} />}
<Table<Reader> rowKey="id" loading={query.isLoading} dataSource={query.data?.items} pagination={{
      current: page,
      total: query.data?.total,
      pageSize: 20,
      onChange: setPage,
      showSizeChanger: false
    }} columns={[{
      title: 'Họ tên',
      dataIndex: 'ho_ten'
    }, {
      title: 'Email',
      dataIndex: 'email'
    }, {
      title: 'Mã thẻ',
      render: (_, r) => r.card?.ma_the ?? 'Chưa cấp'
    }, {
      title: 'Thao tác',
      render: (_, r) => <Button onClick={() => setSelected(r)}>Chi tiết / Lịch sử</Button>
    }]} />
<Drawer open={!!selected} onClose={() => {
      setSelected(null);
      setEdit(false);
    }} title="Chi tiết độc giả" size="large">{reader && <Space orientation="vertical" className="full-width" size="middle">
{detail.error && <Alert type="error" title={errorMessage(detail.error)} />}
<Descriptions column={1} items={[{
          key: 'name',
          label: 'Họ tên',
          children: reader.ho_ten
        }, {
          key: 'email',
          label: 'Email',
          children: reader.email
        }, {
          key: 'phone',
          label: 'Điện thoại',
          children: reader.so_dien_thoai
        }, {
          key: 'card',
          label: 'Mã thẻ',
          children: reader.card?.ma_the ?? 'Chưa cấp'
        }, {
          key: 'expiry',
          label: 'Hạn thẻ',
          children: reader.card?.ngay_het_han
        }, {
          key: 'status',
          label: 'Trạng thái thẻ',
          children: reader.card ? statusLabel(reader.card.trang_thai) : undefined
        }]} />
<Button type="primary" onClick={() => setEdit(true)}>{reader.card ? 'Gia hạn / Khóa thẻ' : 'Cấp thẻ'}</Button>
<BorrowingsPage readerId={reader.id} />
</Space>}</Drawer>
{edit && reader && <EditDialog title={reader.card ? 'Cập nhật thẻ' : 'Cấp thẻ'} pending={action.isPending} initial={reader.card ? {
      ngay_het_han: reader.card.ngay_het_han,
      trang_thai: reader.card.trang_thai
    } : undefined} fields={reader.card ? [{
      name: 'ngay_het_han',
      label: 'Hạn mới',
      type: 'date'
    }, {
      name: 'trang_thai',
      label: 'Trạng thái',
      type: 'select',
      options: ['ACTIVE', 'BLOCKED', 'EXPIRED'].map(value => ({
        value,
        label: statusLabel(value)
      }))
    }] : [{
      name: 'ma_the',
      label: 'Mã thẻ',
      required: true
    }, {
      name: 'ngay_cap',
      label: 'Ngày cấp',
      type: 'date',
      required: true
    }, {
      name: 'ngay_het_han',
      label: 'Ngày hết hạn',
      type: 'date',
      required: true
    }]} onClose={() => setEdit(false)} onSave={v => action.mutate({
      path: reader.card ? `/cards/${reader.card.id}` : `/readers/${reader.id}/card`,
      method: reader.card ? 'patch' : 'post',
      body: reader.card && v.ngay_het_han === reader.card.ngay_het_han ? {
        trang_thai: v.trang_thai
      } : v
    }, {
      onSuccess: () => setEdit(false)
    })} />}
</Space>;
}
