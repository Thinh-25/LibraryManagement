import { Alert, Button, Input, Popconfirm, Space, Table, Tag, Typography } from 'antd';
import { useQuery } from '@tanstack/react-query';
import { useState } from 'react';
import { EditDialog } from '../../components/ResourcePage';
import type { Values } from '../../components/ResourcePage';
import { useAction } from '../../hooks/useAction';
import { getData } from '../../services/api';
import type { Page } from '../../services/api';
import type { User } from '../../stores/session';
import { errorMessage } from '../../utils/access';
import { statusLabel } from '../../utils/labels';
export function UsersPage() {
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState('');
  const [editing, setEditing] = useState<User | true | null>(null);
  const [reset, setReset] = useState<User | null>(null);
  const action = useAction();
  const query = useQuery({
    queryKey: ['users', page, search],
    queryFn: () => getData<Page<User>>('/users', {
      page,
      page_size: 20,
      search
    })
  });
  const initial: Values | undefined = editing && editing !== true ? {
    ho_ten: editing.ho_ten,
    email: editing.email,
    so_dien_thoai: editing.so_dien_thoai,
    vai_tro: editing.vai_tro,
    trang_thai: editing.trang_thai
  } : {
    vai_tro: 'DOC_GIA'
  };
  return <Space orientation="vertical" className="full-width" size="middle">
<Typography.Title level={1}>Quản lý tài khoản</Typography.Title>
<Space>
<Input.Search placeholder="Tên hoặc email" aria-label="Tìm tài khoản" onSearch={v => {
        setSearch(v);
        setPage(1);
      }} />
<Button type="primary" onClick={() => setEditing(true)}>Tạo tài khoản</Button>
</Space>
{query.error && <Alert type="error" title={errorMessage(query.error)} />}
<Table<User> rowKey="id" loading={query.isLoading} dataSource={query.data?.items} scroll={{
      x: 850
    }} pagination={{
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
      title: 'Vai trò',
      dataIndex: 'vai_tro',
      render: (v: string) => statusLabel(v)
    }, {
      title: 'Trạng thái',
      render: (_, r) => <Tag>{r.trang_thai ? 'Hoạt động' : 'Đã khóa'}</Tag>
    }, {
      title: 'Thao tác',
      render: (_, r) => <Space>
<Button onClick={() => setEditing(r)}>Sửa</Button>
<Popconfirm title={r.trang_thai ? 'Khóa tài khoản?' : 'Mở khóa tài khoản?'} onConfirm={() => action.mutateAsync({
          path: `/users/${r.id}`,
          method: 'patch',
          body: {
            trang_thai: !r.trang_thai
          }
        })}><Button>{r.trang_thai ? 'Khóa' : 'Mở khóa'}</Button></Popconfirm>
<Button onClick={() => setReset(r)}>Đặt lại mật khẩu</Button>
</Space>
    }]} />
{editing && <EditDialog title={editing === true ? 'Tạo tài khoản' : 'Sửa tài khoản'} initial={initial} pending={action.isPending} onClose={() => setEditing(null)} fields={[{
      name: 'ho_ten',
      label: 'Họ tên',
      required: true
    }, {
      name: 'email',
      label: 'Email',
      required: true
    }, {
      name: 'so_dien_thoai',
      label: 'Số điện thoại'
    }, {
      name: 'vai_tro',
      label: 'Vai trò',
      required: true,
      type: 'select',
      options: (editing === true ? ['THU_THU', 'DOC_GIA'] : ['ADMIN', 'THU_THU', 'DOC_GIA']).map(value => ({
        value,
        label: statusLabel(value)
      }))
    }, ...(editing === true ? [{
      name: 'password',
      label: 'Mật khẩu tạm (ít nhất 12 ký tự)',
      required: true,
      type: 'password' as const
    }] : [{
      name: 'trang_thai',
      label: 'Hoạt động',
      type: 'boolean' as const
    }])]} onSave={v => action.mutate({
      path: editing === true ? '/users' : `/users/${editing.id}`,
      method: editing === true ? 'post' : 'patch',
      body: v
    }, {
      onSuccess: () => setEditing(null)
    })} />}
{reset && <EditDialog title={`Đặt mật khẩu tạm cho ${reset.ho_ten}`} fields={[{
      name: 'new_password',
      label: 'Mật khẩu tạm mới (ít nhất 12 ký tự)',
      type: 'password',
      required: true
    }]} pending={action.isPending} onClose={() => setReset(null)} onSave={v => action.mutate({
      path: `/users/${reset.id}/reset-password`,
      body: v
    }, {
      onSuccess: () => setReset(null)
    })} />}
</Space>;
}
interface ResetRequest {
  id: number;
  email?: string;
  ho_ten?: string;
  trang_thai: string;
  ngay_tao?: string;
}
export function ResetRequestsPage() {
  const [page, setPage] = useState(1);
  const [selected, setSelected] = useState<ResetRequest | null>(null);
  const action = useAction();
  const query = useQuery({
    queryKey: ['reset-requests', page],
    queryFn: () => getData<Page<ResetRequest>>('/password-reset-requests', {
      page,
      page_size: 20
    })
  });
  return <Space orientation="vertical" className="full-width">
<Typography.Title level={1}>Yêu cầu khôi phục mật khẩu</Typography.Title>
<Alert type="info" title="Xác minh danh tính qua kênh liên hệ phù hợp trước khi đặt mật khẩu tạm. Giao mật khẩu trực tiếp cho người dùng; hệ thống không gửi email." />
{query.error && <Alert type="error" title={errorMessage(query.error)} />}
<Table<ResetRequest> rowKey="id" dataSource={query.data?.items} loading={query.isLoading} pagination={{
      current: page,
      total: query.data?.total,
      pageSize: 20,
      onChange: setPage,
      showSizeChanger: false
    }} columns={[{
      title: 'ID',
      dataIndex: 'id'
    }, {
      title: 'Email',
      dataIndex: 'email'
    }, {
      title: 'Họ tên',
      dataIndex: 'ho_ten'
    }, {
      title: 'Trạng thái',
      dataIndex: 'trang_thai',
      render: (v: string) => statusLabel(v)
    }, {
      title: 'Thao tác',
      render: (_, r) => <Space>
<Button disabled={r.trang_thai !== 'PENDING'} onClick={() => setSelected(r)}>Đặt lại mật khẩu</Button>
<Popconfirm title="Từ chối yêu cầu này?" onConfirm={() => action.mutateAsync({
          path: `/password-reset-requests/${r.id}/resolve`,
          body: {
            reject: true
          }
        })}><Button danger disabled={r.trang_thai !== 'PENDING'}>Từ chối</Button></Popconfirm>
</Space>
    }]} />
{selected && <EditDialog title="Mật khẩu tạm sau xác minh" fields={[{
      name: 'new_password',
      label: 'Mật khẩu mới (ít nhất 12 ký tự)',
      type: 'password',
      required: true
    }]} pending={action.isPending} onClose={() => setSelected(null)} onSave={v => action.mutate({
      path: `/password-reset-requests/${selected.id}/resolve`,
      body: {
        ...v,
        reject: false
      }
    }, {
      onSuccess: () => setSelected(null)
    })} />}
</Space>;
}
