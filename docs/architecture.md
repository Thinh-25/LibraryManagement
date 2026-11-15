# Kiến trúc ứng dụng

Frontend tổ chức theo feature. `app/` cấu hình QueryClient và Ant Design; `routes/` quản lý điều hướng có lazy loading; `services/api.ts` là Axios client chung, đọc VITE_API_BASE_URL và gắn Bearer token. Layout/menu kiểm tra quyền để hiển thị giao diện, backend vẫn là nơi quyết định quyền truy cập.

Server state thuộc TanStack Query; mutation thành công invalidate dữ liệu. Zustand giữ token/user trong bộ nhớ, không localStorage. Reload cần đăng nhập lại. Phiên bị xóa khi401, query cache được làm sạch để tránh dùng dữ liệu phiên trước. Local state thuộc component.

Backend theo Router → Service → Repository → Database. Các nhóm accounts, catalog và circulation thực hiện đủ UC01–UC12; repository chịu trách nhiệm truy vấn, service quản lý quy tắc/transaction, router xác thực và nhận schema. Healthcheck chỉ xác nhận tiến trình API. Lỗi validation/domain trả detail string và không echo mật khẩu; lỗi constraint trả409 thay vì SQL thô.

SQLAlchemy engine tạo khi cần truy cập database; session theo request. Service quản lý transaction, dependency không tự commit. Các thao tác mượn/trả/phạt/đặt trước dùng khóa hàng và cập nhật trạng thái có điều kiện. ORM ánh xạ đủ13 bảng, metadata khớp PostgreSQL qua kiểm thử. Migration baseline0001 giữ SQL gốc;0002 cộng thêm bảo mật và yêu cầu khôi phục. Không dùng create_all tại startup.

Theo lựa chọn mới nhất của người dùng ngày 05/11/2026, backend dùng server PostgreSQL local có sẵn trong pgAdmin tại 127.0.0.1:5432. Database và role ứng dụng riêng đã được tạo trên server này. Cluster cũ `.local/postgres` tại 5433 được giữ nguyên, Docker Compose là phương án thay thế với dữ liệu riêng. `backend/.env` phục vụ Settings; `frontend/.env` phục vụ Vite. Không commit các file `.env` thật hoặc `.local/`. Nội dung biến `VITE_*` được gửi tới trình duyệt, vì vậy tuyệt đối không đặt secret tại đó.

JWT HS256 kiểm tra expiry/chữ ký/auth_version và tài khoản active trên request. Role giữ ADMIN/THU_THU/DOC_GIA. Mật khẩu Argon2id; tài khoản tạo/reset buộc đổi mật khẩu. Quên mật khẩu được Admin xử lý. Các endpoint cá nhân luôn giới hạn theo user đăng nhập. Chính sách cụ thể trong features.md.

Kiểm thử dùng library_management_test, savepoints và fixture đa luồng cleanup theoID, không truncate database ứng dụng. Edge E2E cũng chỉ kết nối database test. Dữ liệu ứng dụng đã được sao lưu trước migration0002 và giữ nguyên35seed.
