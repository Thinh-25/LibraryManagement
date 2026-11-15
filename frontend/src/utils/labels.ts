const labels: Record<string, string> = {
  ADMIN: 'Quản trị viên',
  THU_THU: 'Thủ thư',
  DOC_GIA: 'Độc giả',
  ACTIVE: 'Hoạt động',
  BLOCKED: 'Đã khóa',
  EXPIRED: 'Hết hạn',
  AVAILABLE: 'Có sẵn',
  BORROWED: 'Đang mượn',
  RETURNED: 'Đã trả',
  DAMAGED: 'Hư hỏng',
  LOST: 'Mất',
  PENDING: 'Chờ xử lý',
  READY: 'Sẵn sàng nhận',
  COMPLETED: 'Hoàn tất',
  CANCELLED: 'Đã hủy',
  UNPAID: 'Chưa thanh toán',
  PAID: 'Đã thanh toán',
  RESOLVED: 'Đã xử lý',
  REJECTED: 'Từ chối'
};
export const statusLabel = (value: string) => labels[value] ?? value;
