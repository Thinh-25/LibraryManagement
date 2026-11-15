export type Role = 'ADMIN' | 'THU_THU' | 'DOC_GIA';
export const homeFor = (role: Role) => role === 'DOC_GIA' ? '/books' : '/dashboard';
export function canVisit(role: Role, path: string): boolean {
  if (path === '/') return true;
  if (['/profile', '/change-password'].includes(path) || /^\/books(?:\/\d+)?$/.test(path)) return true;
  if (['/users', '/password-reset-requests'].includes(path)) return role === 'ADMIN';
  if (path.startsWith('/my-')) return role === 'DOC_GIA';
  return role !== 'DOC_GIA' && ['/dashboard', '/reports', '/categories', '/authors', '/publishers', '/readers', '/borrowings', '/reservations', '/fines'].includes(path);
}
export function errorMessage(error: unknown): string {
  if (typeof error === 'object' && error !== null && 'response' in error) {
    const response = error.response;
    if (typeof response === 'object' && response !== null && 'data' in response) {
      const data = response.data;
      if (typeof data === 'object' && data !== null && 'detail' in data && typeof data.detail === 'string') return data.detail;
    }
  }
  return 'Không thể thực hiện. Vui lòng kiểm tra dữ liệu và thử lại.';
}
