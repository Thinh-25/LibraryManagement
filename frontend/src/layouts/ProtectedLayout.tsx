import { useEffect } from 'react';
import { Button, Layout, Menu, Result, Space, Typography } from 'antd';
import { useQueryClient } from '@tanstack/react-query';
import { Link, Navigate, Outlet, useLocation, useNavigate } from 'react-router';
import { useSession } from '../stores/session';
import { api } from '../services/api';
import { canVisit, homeFor } from '../utils/access';
const links = [['/dashboard', 'Tổng quan'], ['/books', 'Tra cứu sách'], ['/categories', 'Thể loại'], ['/authors', 'Tác giả'], ['/publishers', 'Nhà xuất bản'], ['/readers', 'Độc giả và thẻ'], ['/borrowings', 'Mượn / trả sách'], ['/reservations', 'Hàng đợi đặt trước'], ['/fines', 'Tiền phạt'], ['/reports', 'Báo cáo'], ['/users', 'Tài khoản'], ['/password-reset-requests', 'Khôi phục mật khẩu'], ['/my-borrowings', 'Sách của tôi'], ['/my-reservations', 'Đặt trước của tôi'], ['/my-fines', 'Tiền phạt của tôi']];
export function ProtectedLayout() {
  const {
    user,
    token,
    clear
  } = useSession();
  const location = useLocation();
  const client = useQueryClient();
  const navigate = useNavigate();
  useEffect(() => {
    if (!token) client.clear();
  }, [token, client]);
  if (!user) return <Navigate to="/login" replace />;
  if (user.must_change_password && location.pathname !== '/change-password') return <Navigate to="/change-password" replace />;
  const logout = async () => {
    try {
      await api.post('/auth/logout');
    } finally {
      clear();
      client.clear();
      void navigate('/login');
    }
  };
  return <Layout className="app-layout">
<Layout.Sider breakpoint="lg" collapsedWidth={0} width={240} theme="light">
<div className="brand">THƯ VIỆN</div>
<Menu mode="inline" selectedKeys={['/' + location.pathname.split('/')[1]]} items={user.must_change_password ? [] : links.filter(([path]) => canVisit(user.vai_tro, path)).map(([key, label]) => ({
        key,
        label: <Link to={key}>{label}</Link>
      }))} />
</Layout.Sider>
<Layout>
<Layout.Header className="app-header">
<Typography.Text>{user.ho_ten}</Typography.Text>
<Space>
<Link to="/profile">Hồ sơ</Link>
<Button onClick={() => void logout()}>Đăng xuất</Button>
</Space>
</Layout.Header>
<Layout.Content className="app-content">{canVisit(user.vai_tro, location.pathname) ? <Outlet /> : <Result status="403" title="Không có quyền truy cập" extra={<Link to={homeFor(user.vai_tro)}>Về trang chính</Link>} />}</Layout.Content>
</Layout>
</Layout>;
}
export function Landing() {
  const user = useSession(s => s.user);
  return <Navigate to={user ? homeFor(user.vai_tro) : '/login'} replace />;
}
