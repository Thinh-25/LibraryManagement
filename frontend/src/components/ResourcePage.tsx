import { Alert, Button, Form, Input, InputNumber, Modal, Select, Space, Switch, Table, Typography, Popconfirm } from 'antd';
import { useQuery } from '@tanstack/react-query';
import { useCallback, useRef, useState } from 'react';
import { ImagePicker } from './ImagePicker';
import { getData } from '../services/api';
import type { Page } from '../services/api';
import { useAction } from '../hooks/useAction';
import { errorMessage } from '../utils/access';
import { filterSelectOption } from '../utils/selectSearch';
export type Values = Record<string, string | number | boolean | number[] | null>;
export interface Row extends Values {
  id: number;
}
export interface Field {
  name: string;
  label: string;
  type?: 'text' | 'textarea' | 'number' | 'password' | 'boolean' | 'select' | 'date' | 'datetime' | 'image';
  required?: boolean;
  options?: {
    label: string;
    value: string | number;
  }[];
  multiple?: boolean;
  min?: number;
  max?: number;
}
export function Fields({
  fields,
  onImageBlockedChange
}: {
  fields: Field[];
  onImageBlockedChange?: (name: string, blocked: boolean) => void;
}) {
  return <>{fields.map(f => <Form.Item key={f.name} name={f.name} label={f.label} valuePropName={f.type === 'boolean' ? 'checked' : 'value'} rules={[{
      required: f.required,
      message: `Vui lòng nhập ${f.label.toLowerCase()}.`
    }, ...(f.type === 'password' && f.name !== 'current_password' ? [{
      min: 12,
      message: 'Mật khẩu mới cần ít nhất 12 ký tự.'
    }] : []), ...(f.name === 'email' ? [{
      type: 'email' as const,
      message: 'Email không hợp lệ.'
    }] : []), ...(f.name === 'so_dien_thoai' ? [{
      pattern: /^[0-9+]{9,15}$/,
      message: 'Số điện thoại gồm 9–15 chữ số hoặc dấu +.'
    }] : [])]}>
{f.type === 'image' ? <ImagePicker onBlockedChange={blocked => onImageBlockedChange?.(f.name, blocked)} /> : f.type === 'textarea' ? <Input.TextArea rows={3} /> : f.type === 'password' ? <Input.Password autoComplete={f.name === 'current_password' ? 'current-password' : 'new-password'} /> : f.type === 'boolean' ? <Switch /> : f.type === 'number' ? <InputNumber min={f.min} max={f.max} className="full-width" /> : f.type === 'select' ? <Select allowClear showSearch filterOption={filterSelectOption} mode={f.multiple ? 'multiple' : undefined} options={f.options} /> : <Input type={f.type === 'date' ? 'date' : f.type === 'datetime' ? 'datetime-local' : 'text'} />}
</Form.Item>)}</>;
}
export function EditDialog({
  title,
  fields,
  initial,
  onSave,
  onClose,
  pending
}: {
  title: string;
  fields: Field[];
  initial?: Values;
  onSave: (v: Values) => void;
  onClose: () => void;
  pending: boolean;
}) {
  const blockedFields = useRef(new Set<string>());
  const [imageBlocked, setImageBlocked] = useState(false);
  const onImageBlockedChange = useCallback((name: string, blocked: boolean) => {
    if (blocked) blockedFields.current.add(name);
    else blockedFields.current.delete(name);
    setImageBlocked(blockedFields.current.size > 0);
  }, []);
  return <Modal open title={title} footer={null} onCancel={onClose} destroyOnHidden><Form layout="vertical" initialValues={initial} onFinish={(values: Values) => { if (!blockedFields.current.size && !pending) onSave(Object.fromEntries(Object.entries(values).map(([key, value]) => [key, value === '' ? null : value]))); }}>
<Fields fields={fields} onImageBlockedChange={onImageBlockedChange} />
<Space>
<Button type="primary" htmlType="submit" loading={pending} disabled={imageBlocked}>Lưu</Button>
<Button onClick={onClose}>Hủy</Button>
</Space>
</Form></Modal>;
}
export function ResourcePage({
  title,
  path,
  fields,
  columns
}: {
  title: string;
  path: string;
  fields: Field[];
  columns: {
    key: string;
    title: string;
  }[];
}) {
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState('');
  const [editing, setEditing] = useState<Row | true | null>(null);
  const action = useAction();
  const query = useQuery({
    queryKey: [path, page, search],
    queryFn: () => getData<Page<Row>>(path, {
      page,
      page_size: 20,
      search
    })
  });
  return <Space orientation="vertical" className="full-width" size="middle">
<Typography.Title level={1}>{title}</Typography.Title>
<Space wrap>
<Input.Search placeholder="Tìm kiếm" aria-label="Tìm kiếm" onSearch={v => {
        setSearch(v);
        setPage(1);
      }} allowClear />
<Button type="primary" onClick={() => setEditing(true)}>Thêm mới</Button>
</Space>
{query.error && <Alert type="error" title={errorMessage(query.error)} action={<Button onClick={() => void query.refetch()}>Thử lại</Button>} />}
<Table<Row> rowKey="id" loading={query.isLoading} dataSource={query.data?.items} scroll={{
      x: 650
    }} pagination={{
      current: page,
      pageSize: 20,
      total: query.data?.total,
      onChange: setPage,
      showSizeChanger: false
    }} columns={[...columns.map(c => ({
      title: c.title,
      dataIndex: c.key,
      render: (v: unknown) => typeof v === 'boolean' ? v ? 'Hoạt động' : 'Đã khóa' : String(v ?? '—')
    })), {
      title: 'Thao tác',
      render: (_, r) => <Space>
<Button onClick={() => setEditing(r)}>Sửa</Button>
<Popconfirm title="Xóa bản ghi này?" description="Chỉ xóa khi không có dữ liệu tham chiếu." onConfirm={() => action.mutateAsync({
          path: `${path}/${r.id}`,
          method: 'delete'
        })}><Button danger loading={action.isPending}>Xóa</Button></Popconfirm>
</Space>
    }]} />
{editing && <EditDialog title={editing === true ? 'Thêm mới' : 'Chỉnh sửa'} fields={fields} initial={editing === true ? undefined : editing} pending={action.isPending} onClose={() => setEditing(null)} onSave={v => action.mutate({
      path: editing === true ? path : `${path}/${editing.id}`,
      method: editing === true ? 'post' : 'patch',
      body: v
    }, {
      onSuccess: () => setEditing(null)
    })} />}
</Space>;
}
