import { CoverImage } from '../../components/CoverImage';
import { statusLabel } from '../../utils/labels';
import { filterSelectOption } from '../../utils/selectSearch';
import { useQuery } from '@tanstack/react-query';
import { Alert, Button, Descriptions, Input, Popconfirm, Select, Space, Table, Tag, Typography } from 'antd';
import { useState } from 'react';
import { Link, useParams } from 'react-router';
import { EditDialog } from '../../components/ResourcePage';
import type { Field, Row, Values } from '../../components/ResourcePage';
import { useAction } from '../../hooks/useAction';
import { getAllPages, getData } from '../../services/api';
import type { Page } from '../../services/api';
import { useSession } from '../../stores/session';
import { errorMessage } from '../../utils/access';
export interface Copy {
  id: number;
  ma_vach: string;
  vi_tri_ke: string | null;
  tinh_trang: string;
}
export interface Book {
  id: number;
  ten_sach: string;
  isbn: string | null;
  the_loai_id: number;
  nha_xuat_ban_id: number;
  nam_xuat_ban: number | null;
  mo_ta: string | null;
  anh_bia: string | null;
  authors: {
    id: number;
    ho_ten: string;
  }[];
  available_copies: number;
  total_copies: number;
  category_name: string;
  publisher_name: string;
  copies: Copy[];
}
export function useCatalogOptions() {
  const categories = useQuery({
    queryKey: ['options', 'categories'],
    queryFn: () => getAllPages<Row>('/categories')
  });
  const authors = useQuery({
    queryKey: ['options', 'authors'],
    queryFn: () => getAllPages<Row>('/authors')
  });
  const publishers = useQuery({
    queryKey: ['options', 'publishers'],
    queryFn: () => getAllPages<Row>('/publishers')
  });
  return {
    categories: (categories.data ?? []).map(r => ({
      value: r.id,
      label: String(r.ten_the_loai)
    })),
    authors: (authors.data ?? []).map(r => ({
      value: r.id,
      label: String(r.ho_ten)
    })),
    publishers: (publishers.data ?? []).map(r => ({
      value: r.id,
      label: String(r.ten_nxb)
    }))
  };
}
export function BooksPage() {
  const staff = useSession(s => s.user?.vai_tro !== 'DOC_GIA');
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState('');
  const [filters, setFilters] = useState<Record<string, number | undefined>>({});
  const [editing, setEditing] = useState<Book | true | null>(null);
  const action = useAction();
  const options = useCatalogOptions();
  const query = useQuery({
    queryKey: ['books', page, search, filters],
    queryFn: () => getData<Page<Book>>('/books', {
      page,
      page_size: 20,
      search,
      ...filters
    })
  });
  const fields: Field[] = [{
    name: 'ten_sach',
    label: 'Tên sách',
    required: true
  }, {
    name: 'isbn',
    label: 'ISBN'
  }, {
    name: 'the_loai_id',
    label: 'Thể loại',
    type: 'select',
    required: true,
    options: options.categories
  }, {
    name: 'nha_xuat_ban_id',
    label: 'Nhà xuất bản',
    type: 'select',
    required: true,
    options: options.publishers
  }, {
    name: 'author_ids',
    label: 'Tác giả',
    type: 'select',
    multiple: true,
    options: options.authors
  }, {
    name: 'nam_xuat_ban',
    label: 'Năm xuất bản',
    type: 'number',
    min: 1450,
    max: 2200
  }, {
    name: 'mo_ta',
    label: 'Mô tả',
    type: 'textarea'
  }, {
    name: 'anh_bia',
    label: 'Ảnh bìa',
    type: 'image'
  }];
  const initial: Values | undefined = editing && editing !== true ? {
    ten_sach: editing.ten_sach,
    isbn: editing.isbn,
    the_loai_id: editing.the_loai_id,
    nha_xuat_ban_id: editing.nha_xuat_ban_id,
    author_ids: editing.authors.map(a => a.id),
    nam_xuat_ban: editing.nam_xuat_ban,
    mo_ta: editing.mo_ta,
    anh_bia: editing.anh_bia
  } : undefined;
  return <Space orientation="vertical" className="full-width" size="middle">
<Typography.Title level={1}>Tra cứu sách</Typography.Title>
<Space wrap>
<Input.Search aria-label="Tên sách hoặc ISBN" placeholder="Tên sách hoặc ISBN" allowClear onSearch={v => {
        setSearch(v);
        setPage(1);
      }} />
{(['category_id', 'author_id', 'publisher_id'] as const).map((key, i) => <Select showSearch filterOption={filterSelectOption} key={key} aria-label={['Thể loại', 'Tác giả', 'Nhà xuất bản'][i]} placeholder={['Thể loại', 'Tác giả', 'Nhà xuất bản'][i]} className="filter-select" allowClear options={[options.categories, options.authors, options.publishers][i]} onChange={v => {
        setFilters({
          ...filters,
          [key]: v
        });
        setPage(1);
      }} />)}
{staff && <Button type="primary" onClick={() => setEditing(true)}>Thêm sách</Button>}
</Space>
{query.error && <Alert type="error" title={errorMessage(query.error)} action={<Button onClick={() => void query.refetch()}>Thử lại</Button>} />}
<Table<Book> rowKey="id" loading={query.isLoading} dataSource={query.data?.items} scroll={{
      x: 850
    }} pagination={{
      current: page,
      total: query.data?.total,
      pageSize: 20,
      onChange: setPage,
      showSizeChanger: false
    }} columns={[{
      title: 'Ảnh bìa',
      width: 90,
      render: (_, r) => <CoverImage value={r.anh_bia} alt={`Ảnh bìa ${r.ten_sach}`} small />
    }, {
      title: 'Tên sách',
      render: (_, r) => <Link to={`/books/${r.id}`}>{r.ten_sach}</Link>
    }, {
      title: 'ISBN',
      dataIndex: 'isbn'
    }, {
      title: 'Thể loại',
      dataIndex: 'category_name'
    }, {
      title: 'Tác giả',
      render: (_, r) => r.authors.map(a => a.ho_ten).join(', ')
    }, {
      title: 'Có sẵn / Tổng',
      render: (_, r) => `${r.available_copies} / ${r.total_copies}`
    }, {
      title: 'Thao tác',
      render: (_, r) => <Space>{staff ? <>
<Button onClick={() => setEditing(r)}>Sửa</Button>
<Popconfirm title="Xóa đầu sách này?" onConfirm={() => action.mutateAsync({
            path: `/books/${r.id}`,
            method: 'delete'
          })}><Button danger>Xóa</Button></Popconfirm>
</> : <Popconfirm title="Đặt trước đầu sách này?" onConfirm={() => action.mutateAsync({
          path: '/reservations',
          body: {
            sach_id: r.id
          }
        })}><Button loading={action.isPending}>Đặt trước</Button></Popconfirm>}</Space>
    }]} />
{editing && <EditDialog title={editing === true ? 'Thêm đầu sách' : 'Chỉnh sửa đầu sách'} fields={fields} initial={initial} pending={action.isPending} onClose={() => setEditing(null)} onSave={v => action.mutate({
      path: editing === true ? '/books' : `/books/${editing.id}`,
      method: editing === true ? 'post' : 'patch',
      body: {
        ...v,
        author_ids: v.author_ids ?? []
      }
    }, {
      onSuccess: () => setEditing(null)
    })} />}
</Space>;
}
export function BookDetailPage() {
  const {
    id
  } = useParams();
  const staff = useSession(s => s.user?.vai_tro !== 'DOC_GIA');
  const query = useQuery({
    queryKey: ['book', id],
    queryFn: () => getData<Book>(`/books/${id}`)
  });
  const [editing, setEditing] = useState<Copy | true | null>(null);
  const action = useAction();
  const book = query.data;
  return <Space orientation="vertical" className="full-width" size="middle">
<Link to="/books">← Danh sách sách</Link>
{query.error && <Alert type="error" title={errorMessage(query.error)} />}
<Typography.Title level={1}>{book?.ten_sach ?? 'Chi tiết sách'}</Typography.Title>
{book && <CoverImage value={book.anh_bia} alt={`Ảnh bìa ${book.ten_sach}`} />}
<Descriptions bordered column={{
      xs: 1,
      md: 2
    }} items={[{
      key: 'isbn',
      label: 'ISBN',
      children: book?.isbn ?? '—'
    }, {
      key: 'authors',
      label: 'Tác giả',
      children: book?.authors.map(a => a.ho_ten).join(', ')
    }, {
      key: 'category',
      label: 'Thể loại',
      children: book?.category_name
    }, {
      key: 'publisher',
      label: 'NXB',
      children: book?.publisher_name
    }, {
      key: 'year',
      label: 'Năm xuất bản',
      children: book?.nam_xuat_ban
    }, {
      key: 'description',
      label: 'Mô tả',
      children: book?.mo_ta
    }]} />
{staff ? <Button type="primary" onClick={() => setEditing(true)}>Thêm cuốn sách</Button> : <Popconfirm title="Đặt trước sách này?" onConfirm={() => action.mutateAsync({
      path: '/reservations',
      body: {
        sach_id: Number(id)
      }
    })}><Button type="primary">Đặt trước</Button></Popconfirm>}
<Table<Copy> rowKey="id" loading={query.isLoading} dataSource={book?.copies} columns={[{
      title: 'Mã vạch',
      dataIndex: 'ma_vach'
    }, {
      title: 'Vị trí kệ',
      dataIndex: 'vi_tri_ke'
    }, {
      title: 'Tình trạng',
      render: (_, r) => <Tag>{statusLabel(r.tinh_trang)}</Tag>
    }, ...(staff ? [{
      title: 'Thao tác',
      render: (_: unknown, r: Copy) => <Space>
<Button disabled={r.tinh_trang === 'BORROWED'} onClick={() => setEditing(r)}>Sửa</Button>
<Popconfirm title="Xóa cuốn sách này?" onConfirm={() => action.mutateAsync({
          path: `/copies/${r.id}`,
          method: 'delete'
        })}><Button danger disabled={r.tinh_trang === 'BORROWED'}>Xóa</Button></Popconfirm>
</Space>
    }] : [])]} />
{editing && <EditDialog title={editing === true ? 'Thêm cuốn sách' : 'Sửa cuốn sách'} fields={[{
      name: 'ma_vach',
      label: 'Mã vạch',
      required: true
    }, {
      name: 'vi_tri_ke',
      label: 'Vị trí kệ'
    }, {
      name: 'tinh_trang',
      label: 'Tình trạng',
      type: 'select',
      options: ['AVAILABLE', 'DAMAGED', 'LOST'].map(value => ({
        value,
        label: statusLabel(value)
      }))
    }]} initial={editing === true ? {
      tinh_trang: 'AVAILABLE'
    } : {
      ma_vach: editing.ma_vach,
      vi_tri_ke: editing.vi_tri_ke,
      tinh_trang: editing.tinh_trang
    }} pending={action.isPending} onClose={() => setEditing(null)} onSave={v => action.mutate({
      path: editing === true ? `/books/${id}/copies` : `/copies/${editing.id}`,
      method: editing === true ? 'post' : 'patch',
      body: v
    }, {
      onSuccess: () => setEditing(null)
    })} />}
</Space>;
}
