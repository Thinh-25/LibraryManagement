import { RouterProvider } from 'react-router';
import { Suspense } from 'react';
import { Spin } from 'antd';
import { router } from '../routes/router';
import { Providers } from './providers';

export function App() {
  return (
    <Providers>
      <Suspense fallback={<Spin fullscreen tip="Đang tải trang…" />}>
        <RouterProvider router={router} />
      </Suspense>
    </Providers>
  );
}
