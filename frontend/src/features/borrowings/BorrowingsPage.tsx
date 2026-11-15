import { useLookup } from '../../hooks/useLookup';
import { statusLabel } from '../../utils/labels';
import { filterSelectOption } from '../../utils/selectSearch';
import { useQuery } from '@tanstack/react-query';
import { Alert, Button, Drawer, Form, Input, Modal, Select, Space, Table, Tag, Typography } from 'antd';
import { useState } from 'react';
import { getData } from '../../services/api';
import type { Page } from '../../services/api';
import { useAction } from '../../hooks/useAction';
import { EditDialog } from '../../components/ResourcePage';
import { errorMessage } from '../../utils/access';
import { useSession } from '../../stores/session';
import type { User } from '../../stores/session';
import type { Book } from '../books/BooksPages';
export interface LoanItem {
  id: number;
  cuon_sach_id: number;
  ten_sach: string;
  ma_vach: string;
  han_tra: string;
  ngay_tra: string | null;
  trang_thai: string;
  tinh_trang_khi_tra: string | null;
}
interface Borrowing {
  id: number;
  doc_gia_id: number;
  doc_gia_name: string;
  thu_thu_name: string;
  ngay_muon: string;
  ghi_chu: string | null;
  items: LoanItem[];
}
export const dateText = (v: string | null | undefined) => v ? new Intl.DateTimeFormat('vi-VN', {
  dateStyle: 'short',
  timeStyle: 'short',
  timeZone: 'Asia/Ho_Chi_Minh'
}).format(new Date(v)) : '—';
export function LoanItems({
  items,
  staff
}: {
  items: LoanItem[];
  staff: boolean;
}) {
  const action = useAction();
  const [returning, setReturning] = useState<LoanItem | null>(null);
  return <>
<Table<LoanItem> rowKey="id" dataSource={items} size="small" pagination={false} scroll={{
      x: 650
    }} columns={[{
      title: 'Sách / Mã vạch',
      render: (_, r) => <>{r.ten_sach}<br />{r.ma_vach} · Lượt #{r.id}</>
    }, {
      title: 'Hạn trả',
      render: (_, r) => <Space orientation="vertical">
{dateText(r.han_tra)}
{r.trang_thai === 'BORROWED' && new Date(r.han_tra) < new Date() && <Tag color="red">Quá hạn</Tag>}
</Space>
    }, {
      title: 'Ngày trả',
      render: (_, r) => dateText(r.ngay_tra)
    }, {
      title: 'Trạng thái',
      dataIndex: 'trang_thai',
      render: (v: string) => statusLabel(v)
    }, ...(staff ? [{
      title: 'Thao tác',
      render: (_: unknown, r: LoanItem) => <Button disabled={r.trang_thai !== 'BORROWED'} onClick={() => setReturning(r)}>Nhận trả</Button>
    }] : [])]} />
{returning && <EditDialog title={`Nhận trả ${returning.ma_vach}`} pending={action.isPending} initial={{
      condition: 'GOOD'
    }} fields={[{
      name: 'condition',
      label: 'Tình trạng nhận trả',
      type: 'select',
      required: true,
      options: [{
        value: 'GOOD',
        label: 'Bình thường'
      }, {
        value: 'DAMAGED',
        label: 'Hư hỏng'
      }, {
        value: 'LOST',
        label: 'Báo mất'
      }]
    }, {
      name: 'note',
      label: 'Ghi chú',
      type: 'textarea'
    }, {
      name: 'fine_amount',
      label: 'Tiền phạt tùy chọn (VND, lớn hơn 0)',
      type: 'number',
      min: 1
    }, {
      name: 'fine_reason',
      label: 'Lý do phạt (bắt buộc nếu có phạt)'
    }]} onClose={() => setReturning(null)} onSave={v => action.mutate({
      path: `/loan-items/${returning.id}/return`,
      body: {
        ...v,
        fine_amount: v.fine_amount || undefined,
        fine_reason: v.fine_amount ? v.fine_reason : undefined
      }
    }, {
      onSuccess: () => setReturning(null)
    })} />}
</>;
}
interface CheckoutLine {
  cuon_sach_id: number;
  han_tra: string;
  label: string;
}
export function CheckoutDialog({
  reservation,
  onClose
}: {
  reservation?: {
    id: number;
    doc_gia_id: number;
    sach_id: number;
  };
  onClose: () => void;
}) {
  const action = useAction();
  const [reader, setReader] = useState<number | undefined>(reservation?.doc_gia_id);
  const [readerSearch, setReaderSearch] = useState('');
  const [bookSearch, setBookSearch] = useState('');
  const [bookId, setBookId] = useState<number | undefined>(reservation?.sach_id);
  const [lines, setLines] = useState<CheckoutLine[]>([]);
  const [copyId, setCopyId] = useState<number>();
  const [due, setDue] = useState('');
  const [note, setNote] = useState('');
  const [localError, setLocalError] = useState('');
  const readers = useLookup<User>('/readers', readerSearch);
  const books = useLookup<Book>('/books', bookSearch);
  const book = useQuery({
    queryKey: ['book', bookId],
    queryFn: () => getData<Book>(`/books/${bookId}`),
    enabled: !!bookId
  });
  const add = () => {
    if (!copyId || !due || new Date(due) <= new Date()) {
      setLocalError('Chọn cuốn sách và hạn trả trong tương lai.');
      return;
    }
    const copy = book.data?.copies.find(c => c.id === copyId);
    if (!copy) return;
    setLines([...lines, {
      cuon_sach_id: copyId,
      han_tra: new Date(due).toISOString(),
      label: `${book.data?.ten_sach} · ${copy.ma_vach}`
    }]);
    setCopyId(undefined);
    setLocalError('');
  };
  return <Modal open title={reservation ? 'Lập phiếu và hoàn tất đặt trước' : 'Lập phiếu mượn nhiều cuốn'} onCancel={onClose} width={800} footer={<Space>
<Button onClick={onClose}>Hủy</Button>
<Button type="primary" loading={action.isPending} disabled={!reader || !lines.length} onClick={() => action.mutate({
      path: '/borrowings',
      body: {
        doc_gia_id: reader,
        ghi_chu: note || undefined,
        items: lines.map(({
          cuon_sach_id,
          han_tra
        }) => ({
          cuon_sach_id,
          han_tra
        })),
        reservation_id: reservation?.id
      }
    }, {
      onSuccess: onClose
    })}>Xác nhận mượn</Button>
</Space>}><Space orientation="vertical" className="full-width" size="middle">
<Alert type="info" title="Thẻ phải hoạt động và còn hạn. Tất cả cuốn được kiểm tra lại khi xác nhận." />
{localError && <Alert type="error" title={localError} />}
{[readers.error, books.error, book.error].filter(Boolean).map((e, i) => <Alert key={i} type="error" title={errorMessage(e)} />)}
<Form layout="vertical">
<Form.Item label="Độc giả" required><Select aria-label="Độc giả" value={reader} disabled={!!reservation} showSearch filterOption={false} onSearch={setReaderSearch} onPopupScroll={readers.loadMore} loading={readers.isFetching} onChange={setReader} options={readers.items.map(r => ({
            value: r.id,
            label: `${r.ho_ten} · ${r.email}`
          }))} /></Form.Item>
<Form.Item label="Đầu sách"><Select aria-label="Đầu sách" value={bookId} showSearch filterOption={false} onSearch={setBookSearch} onPopupScroll={books.loadMore} loading={books.isFetching} onChange={v => {
            setBookId(v);
            setCopyId(undefined);
          }} options={books.items.map(b => ({
            value: b.id,
            label: b.ten_sach
          }))} /></Form.Item>
<Form.Item label="Cuốn có sẵn"><Select showSearch filterOption={filterSelectOption} aria-label="Cuốn có sẵn" value={copyId} onChange={setCopyId} loading={book.isLoading} options={book.data?.copies.filter(c => c.tinh_trang === 'AVAILABLE' && !lines.some(l => l.cuon_sach_id === c.id)).map(c => ({
            value: c.id,
            label: `${c.ma_vach} · ${c.vi_tri_ke ?? 'Chưa có kệ'}`
          }))} /></Form.Item>
<Form.Item label="Hạn trả (giờ địa phương)"><Input aria-label="Hạn trả" type="datetime-local" value={due} onChange={e => setDue(e.target.value)} /></Form.Item>
<Button onClick={add}>Thêm cuốn vào phiếu</Button>
<Form.Item label="Ghi chú"><Input.TextArea aria-label="Ghi chú" value={note} maxLength={500} onChange={e => setNote(e.target.value)} /></Form.Item>
</Form>
<Table<CheckoutLine> rowKey="cuon_sach_id" dataSource={lines} pagination={false} columns={[{
        title: 'Sách / Mã vạch',
        dataIndex: 'label'
      }, {
        title: 'Hạn trả',
        render: (_, r) => dateText(r.han_tra)
      }, {
        title: 'Thao tác',
        render: (_, r) => <Button danger onClick={() => setLines(lines.filter(l => l.cuon_sach_id !== r.cuon_sach_id))}>Bỏ cuốn</Button>
      }]} />
</Space></Modal>;
}
export function BorrowingsPage({
  personal = false,
  readerId
}: {
  personal?: boolean;
  readerId?: number;
}) {
  const staff = useSession(s => s.user?.vai_tro !== 'DOC_GIA');
  const [page, setPage] = useState(1);
  const [status, setStatus] = useState('borrowed');
  const [create, setCreate] = useState(false);
  const [selected, setSelected] = useState<Borrowing | null>(null);
  const path = personal ? '/my-borrowings' : '/borrowings';
  const query = useQuery({
    queryKey: [path, page, status, readerId],
    queryFn: () => getData<Page<Borrowing>>(path, {
      page,
      page_size: 20,
      reader_id: readerId,
      status: personal ? status : undefined
    })
  });
  const detail = useQuery({
    queryKey: ['borrowing', selected?.id],
    queryFn: () => getData<Borrowing>(`/borrowings/${selected?.id}`),
    enabled: !!selected
  });
  return <Space orientation="vertical" className="full-width" size="middle">
<Typography.Title level={readerId ? 3 : 1}>{personal ? 'Sách đang mượn và lịch sử' : 'Phiếu mượn / Trả sách'}</Typography.Title>
<Space>{personal ? <Select showSearch filterOption={filterSelectOption} aria-label="Lọc lượt mượn cá nhân" value={status} onChange={v => {
        setStatus(v);
        setPage(1);
      }} options={[{
        value: 'borrowed',
        label: 'Đang mượn'
      }, {
        value: 'overdue',
        label: 'Quá hạn'
      }, {
        value: 'history',
        label: 'Lịch sử trả / mất'
      }]} /> : !readerId && <Button type="primary" onClick={() => setCreate(true)}>Lập phiếu mượn</Button>}</Space>
{query.error && <Alert type="error" title={errorMessage(query.error)} action={<Button onClick={() => void query.refetch()}>Thử lại</Button>} />}
<Table<Borrowing> rowKey="id" loading={query.isLoading} dataSource={query.data?.items} pagination={{
      current: page,
      total: query.data?.total,
      pageSize: 20,
      onChange: setPage,
      showSizeChanger: false
    }} scroll={{
      x: 600
    }} expandable={{
      expandedRowRender: r => <LoanItems items={r.items} staff={staff} />
    }} columns={[{
      title: 'Phiếu',
      dataIndex: 'id'
    }, {
      title: 'Độc giả',
      dataIndex: 'doc_gia_name'
    }, {
      title: 'Ngày mượn',
      render: (_, r) => dateText(r.ngay_muon)
    }, {
      title: 'Số cuốn',
      render: (_, r) => r.items.length
    }, {
      title: 'Thao tác',
      render: (_, r) => <Button onClick={() => setSelected(r)}>Chi tiết</Button>
    }]} />
{create && <CheckoutDialog onClose={() => setCreate(false)} />}
<Drawer title={`Phiếu mượn #${selected?.id ?? ''}`} open={!!selected} onClose={() => setSelected(null)} size="large">
{detail.error && <Alert type="error" title={errorMessage(detail.error)} />}
{selected && <>
<Typography.Paragraph>{(detail.data ?? selected).ghi_chu}</Typography.Paragraph>
<LoanItems items={(detail.data ?? selected).items} staff={staff} />
</>}
</Drawer>
</Space>;
}
