import { lazy } from 'react';
import { createBrowserRouter, Link } from 'react-router';
import { Result } from 'antd';
import { ProtectedLayout, Landing } from '../layouts/ProtectedLayout';
const LoginPage = lazy(() => import('../features/auth/AuthPages').then(module => ({default:module.LoginPage})));
const ForgotPasswordPage = lazy(() => import('../features/auth/AuthPages').then(module => ({default:module.ForgotPasswordPage})));
const ProfilePage = lazy(() => import('../features/auth/AuthPages').then(module => ({default:module.ProfilePage})));
const BooksPage = lazy(() => import('../features/books/BooksPages').then(module => ({default:module.BooksPage})));
const BookDetailPage = lazy(() => import('../features/books/BooksPages').then(module => ({default:module.BookDetailPage})));
import { ResourcePage } from '../components/ResourcePage';
const ReadersPage = lazy(() => import('../features/readers/ReadersPage').then(module => ({default:module.ReadersPage})));
const UsersPage = lazy(() => import('../features/users/UsersPages').then(module => ({default:module.UsersPage})));
const ResetRequestsPage = lazy(() => import('../features/users/UsersPages').then(module => ({default:module.ResetRequestsPage})));
const BorrowingsPage = lazy(() => import('../features/borrowings/BorrowingsPage').then(module => ({default:module.BorrowingsPage})));
const ReservationsPage = lazy(() => import('../features/reservations/ReservationsPage').then(module => ({default:module.ReservationsPage})));
const FinesPage = lazy(() => import('../features/fines/FinesPage').then(module => ({default:module.FinesPage})));
const ReportsPage = lazy(() => import('../features/reports/ReportsPage').then(module => ({default:module.ReportsPage})));
export const router = createBrowserRouter([{
  path: '/login',
  element: <LoginPage />
}, {
  path: '/forgot-password',
  element: <ForgotPasswordPage />
}, {
  path: '/',
  element: <ProtectedLayout />,
  children: [{
    index: true,
    element: <Landing />
  }, {
    path: 'profile',
    element: <ProfilePage />
  }, {
    path: 'change-password',
    element: <ProfilePage password />
  }, {
    path: 'dashboard',
    element: <ReportsPage dashboard />
  }, {
    path: 'reports',
    element: <ReportsPage />
  }, {
    path: 'books',
    element: <BooksPage />
  }, {
    path: 'books/:id',
    element: <BookDetailPage />
  }, {
    path: 'categories',
    element: <ResourcePage title="Quản lý thể loại" path="/categories" columns={[{
      key: 'ten_the_loai',
      title: 'Tên thể loại'
    }, {
      key: 'mo_ta',
      title: 'Mô tả'
    }]} fields={[{
      name: 'ten_the_loai',
      label: 'Tên thể loại',
      required: true
    }, {
      name: 'mo_ta',
      label: 'Mô tả',
      type: 'textarea'
    }]} />
  }, {
    path: 'authors',
    element: <ResourcePage title="Quản lý tác giả" path="/authors" columns={[{
      key: 'ho_ten',
      title: 'Họ tên'
    }, {
      key: 'tieu_su',
      title: 'Tiểu sử'
    }]} fields={[{
      name: 'ho_ten',
      label: 'Họ tên',
      required: true
    }, {
      name: 'tieu_su',
      label: 'Tiểu sử',
      type: 'textarea'
    }]} />
  }, {
    path: 'publishers',
    element: <ResourcePage title="Quản lý nhà xuất bản" path="/publishers" columns={[{
      key: 'ten_nxb',
      title: 'Nhà xuất bản'
    }, {
      key: 'dia_chi',
      title: 'Địa chỉ'
    }, {
      key: 'so_dien_thoai',
      title: 'Điện thoại'
    }]} fields={[{
      name: 'ten_nxb',
      label: 'Tên nhà xuất bản',
      required: true
    }, {
      name: 'dia_chi',
      label: 'Địa chỉ'
    }, {
      name: 'so_dien_thoai',
      label: 'Điện thoại'
    }]} />
  }, {
    path: 'readers',
    element: <ReadersPage />
  }, {
    path: 'users',
    element: <UsersPage />
  }, {
    path: 'password-reset-requests',
    element: <ResetRequestsPage />
  }, {
    path: 'borrowings',
    element: <BorrowingsPage />
  }, {
    path: 'my-borrowings',
    element: <BorrowingsPage personal />
  }, {
    path: 'reservations',
    element: <ReservationsPage />
  }, {
    path: 'my-reservations',
    element: <ReservationsPage personal />
  }, {
    path: 'fines',
    element: <FinesPage />
  }, {
    path: 'my-fines',
    element: <FinesPage personal />
  }]
}, {
  path: '*',
  element: <Result status="404" title="Không tìm thấy trang" extra={<Link to="/">Về trang chính</Link>} />
}]);
