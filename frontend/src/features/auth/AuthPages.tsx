import { Alert, Button, Card, Form, Input, Space, Typography } from 'antd';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { Link, Navigate, useNavigate } from 'react-router';
import { api } from '../../services/api';
import { useSession } from '../../stores/session';
import type { User } from '../../stores/session';
import { errorMessage, homeFor } from '../../utils/access';
import { Fields } from '../../components/ResourcePage';
import type { Values } from '../../components/ResourcePage';
export function LoginPage() {
  const session = useSession();
  const navigate = useNavigate();
  const client = useQueryClient();
  const login = useMutation({
    mutationFn: async (v: {
      email: string;
      password: string;
    }) => (await api.post<{
      access_token: string;
      user: User;
    }>('/auth/login', v)).data,
    onSuccess: r => {
      client.clear();
      session.setSession(r.access_token, r.user);
      void navigate(r.user.must_change_password ? '/change-password' : homeFor(r.user.vai_tro));
    }
  });
  if (session.user) return <Navigate to={session.user.must_change_password ? '/change-password' : homeFor(session.user.vai_tro)} />;
  return <main className="auth-page"><Card>
<Typography.Title level={1}>Thư viện</Typography.Title>
<Typography.Paragraph>Đăng nhập để sử dụng thư viện.</Typography.Paragraph>
{login.error && <Alert type="error" title={errorMessage(login.error)} />}
<Form layout="vertical" onFinish={v => login.mutate(v)}>
<Form.Item name="email" label="Email" rules={[{
          required: true,
          type: 'email'
        }]}><Input autoComplete="username" /></Form.Item>
<Form.Item name="password" label="Mật khẩu" rules={[{
          required: true
        }]}><Input.Password autoComplete="current-password" /></Form.Item>
<Button block type="primary" htmlType="submit" loading={login.isPending}>Đăng nhập</Button>
</Form>
<Link to="/forgot-password">Quên mật khẩu?</Link>
</Card></main>;
}
export function ForgotPasswordPage() {
  const mutation = useMutation({
    mutationFn: (v: Values) => api.post('/auth/forgot-password', v)
  });
  return <main className="auth-page"><Card title="Yêu cầu khôi phục mật khẩu">
<Typography.Paragraph>Quản trị viên sẽ xác minh danh tính và hỗ trợ đặt lại mật khẩu qua kênh liên hệ bên ngoài.</Typography.Paragraph>
{mutation.isSuccess && <Alert type="success" title="Nếu tài khoản phù hợp, yêu cầu đã được ghi nhận." />}
{mutation.error && <Alert type="error" title={errorMessage(mutation.error)} />}
<Form layout="vertical" onFinish={v => mutation.mutate(v)}>
<Form.Item label="Email" name="email" rules={[{
          required: true,
          type: 'email'
        }]}><Input type="email" autoComplete="email" /></Form.Item>
<Button htmlType="submit" type="primary" loading={mutation.isPending}>Gửi yêu cầu</Button>
</Form>
<Link to="/login">Trở lại đăng nhập</Link>
</Card></main>;
}
export function ProfilePage({
  password = false
}: {
  password?: boolean;
}) {
  const session = useSession();
  const client = useQueryClient();
  const navigate = useNavigate();
  const mutation = useMutation({
    mutationFn: async (v: Values) => password ? api.post('/auth/change-password', v) : api.patch<User>('/auth/me', {
      ...v,
      so_dien_thoai: v.so_dien_thoai || null
    }),
    onSuccess: async () => {
      if (password) {
        session.clear();
        client.clear();
        void navigate('/login');
      } else {
        session.setUser((await api.get<User>('/auth/me')).data);
      }
    }
  });
  const fields = password ? [{
    name: 'current_password',
    label: 'Mật khẩu hiện tại',
    type: 'password' as const,
    required: true
  }, {
    name: 'new_password',
    label: 'Mật khẩu mới (ít nhất 12 ký tự)',
    type: 'password' as const,
    required: true
  }] : [{
    name: 'ho_ten',
    label: 'Họ tên',
    required: true
  }, {
    name: 'so_dien_thoai',
    label: 'Số điện thoại'
  }];
  return <Card className="form-card">
<Typography.Title level={1}>{password ? 'Đổi mật khẩu' : 'Hồ sơ cá nhân'}</Typography.Title>
{session.user?.must_change_password && <Alert type="warning" title="Bạn phải đổi mật khẩu tạm trước khi tiếp tục." />}
{mutation.error && <Alert type="error" title={errorMessage(mutation.error)} />}
{mutation.isSuccess && !password && <Alert type="success" title="Đã cập nhật hồ sơ." />}
<Form layout="vertical" initialValues={password ? undefined : {
      ho_ten: session.user?.ho_ten,
      so_dien_thoai: session.user?.so_dien_thoai
    }} onFinish={v => mutation.mutate(v)}>
<Fields fields={fields} />
<Space>
<Button type="primary" htmlType="submit" loading={mutation.isPending}>Lưu</Button>
{!password && <Link to="/change-password">Đổi mật khẩu</Link>}
</Space>
</Form>
</Card>;
}
