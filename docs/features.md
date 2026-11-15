# Các chức năng đã triển khai

Ảnh bìa sách đã hỗ trợ chọn JPG/PNG/WebP từ máy trong form thêm/sửa, tối đa5MB; có preview, thay/bỏ ảnh và chặn Lưu khi upload chưa thành công. Chỉ staff được upload. Backend kiểm tra nội dung/pixel, chuẩn hóa WebP và lưu local; URL ảnh cũ vẫn tương thích. Xem README để sao lưu thư mục ảnh cùng database.

| Use case | Giao diện | API chính |
|---|---|---|
| UC01 Tài khoản | /users | /users, /users/{id}/reset-password |
| UC02 Xác thực/hồ sơ | /login, /forgot-password, /profile, /change-password | /auth/*, /password-reset-requests |
| UC03 Độc giả/thẻ | /readers | /readers, /readers/{id}/card, /cards/{id} |
| UC04 Sách/bản sao | /books, /books/{id} | /books, /books/{id}/copies, /copies/{id} |
| UC05 Danh mục | /categories, /authors, /publishers | /categories, /authors, /publishers |
| UC06 Tra cứu | /books | /books với search/category_id/author_id/publisher_id |
| UC07 Mượn | /borrowings | POST /borrowings |
| UC08 Trả | Chi tiết phiếu, nút Nhận trả | POST /loan-items/{id}/return |
| UC09 Đặt trước | /reservations, /my-reservations | /reservations, /my-reservations, ready/cancel |
| UC10 Tiền phạt | /fines, /my-fines | /fines, /my-fines, /fines/{id}/pay |
| UC11 Mượn trả cá nhân | /my-borrowings | /my-borrowings theo borrowed/overdue/history |
| UC12 Báo cáo | /dashboard, /reports | /reports với start_date/end_date |

Tất cả endpoint có prefix /api/v1. Staff = ADMIN/THU_THU. Chỉ Admin quản lý tài khoản/yêu cầu khôi phục; chỉ độc giả thao tác trang cá nhân/đặt trước của mình. Metadata tra cứu được đọc bởi cả ba vai trò; mutation catalog chỉ staff. Không cho tự đăng ký.

Login dùng email/password JSON. Mật khẩu Argon2id, JWT HS256 30 phút mặc định. Token giữ trong bộ nhớ trình duyệt; không localStorage/cookie. Reload đăng nhập lại. Tài khoản mới/reset bị buộc đổi mật khẩu tạm; Admin xác minh và trao mật khẩu qua kênh ngoài hệ thống.

Mượn/trả, đánh dấu đặt trước và thanh toán khóa bản ghi trong PostgreSQL. Các test thực sự dùng hai session đồng thời chứng minh chỉ một thao tác thành công khi cùng mượn/trả/thanh toán; test khác bảo vệ COMPLETED trước tiến trình hết hạn READY.

Giữ 35 seed cũ; không tự biến placeholder thành mật khẩu đăng nhập. Chạy lệnh bootstrap trong README để tự chọn mật khẩu Admin. Dữ liệu test/E2E nằm riêng ở library_management_test và không xuất hiện trong database ứng dụng.

Điểm nhỏ chưa tối ưu: khi API tải danh mục lựa chọn bị lỗi, form/bộ lọc sách hiện options rỗng thay vì thông báo lỗi riêng; lỗi mutation chính vẫn hiển thị. Vendor bundle Ant Design còn cảnh báo >500 kB dù các trang đã lazy-load. Rate limit auth ở bộ nhớ một backend process; triển khai nhiều process cần bộ lưu rate limit dùng chung.
