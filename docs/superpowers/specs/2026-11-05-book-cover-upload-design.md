# Chọn ảnh bìa từ máy khi thêm/sửa sách

Trạng thái: người dùng đã duyệt “bắt đầu”; đã triển khai và kiểm chứng qua test/backend, build/frontend và Edge E2E.

## Phạm vi

Thay trường nhập URL ảnh bìa trong form thêm/sửa đầu sách bằng chọn file từ máy. Hiện các thực thể khác chưa có trường ảnh; không tự thêm avatar hoặc ảnh cho tác giả/danh mục.

## Cách thực hiện đề xuất

- Nút Chọn ảnh từ máy, nhận JPG/JPEG, PNG và WebP, tối đa 5 MB/file.
- Xem trước ảnh đã chọn; khi sửa hiển thị ảnh hiện tại, cho thay hoặc bỏ ảnh.
- Upload thành công mới nhận URL vào form; nút Lưu bị chặn khi đang upload. Lưu sách mới cập nhật trường anh_bia; Hủy không thay đổi dữ liệu sách.
- Giữ URL ảnh cũ để không phá dữ liệu. Chọn file là luồng chính; không bắt người dùng nhập URL.
- Hiển thị ảnh bìa ở danh sách/chi tiết sách, có trạng thái khi chưa có ảnh hoặc ảnh lỗi.

## Backend và lưu trữ

- POST /api/v1/uploads/covers dùng multipart, chỉ ADMIN/THU_THU được upload.
- Kiểm tra kích thước và decode nội dung ảnh bằng thư viện xử lý ảnh; không tin extension/MIME do client gửi, không nhận SVG.
- Đặt tên ngẫu nhiên, chuẩn hóa thành WebP, bỏ metadata; giới hạn kích thước pixel để tránh ảnh nén bất thường.
- Lưu trong .local/uploads/covers, phục vụ qua /media/covers; đường dẫn ảnh được lưu trong cột anh_bia hiện có, không cần migration.
- GET ảnh bìa là tài nguyên công khai của website; không chứa credential. Chỉ chấp nhận đường dẫn local do backend sinh hoặc URL HTTP(S) hợp lệ khi cập nhật sách.
- Không tự xóa file ảnh cũ vì có thể đang được bản ghi khác dùng. File đã upload nhưng hủy form được giữ lại trong local storage; dọn file không tham chiếu là việc bảo trì riêng.
- Lưu local phù hợp môi trường PostgreSQL/backend hiện tại. Không đưa thêm cloud storage hoặc database blob vào phạm vi.

## Kiểm chứng

- Backend: upload hợp lệ, đọc lại ảnh, quyền của ba vai trò, file giả ảnh/hỏng, file quá lớn và đường dẫn không hợp lệ.
- Frontend: TypeScript/build, Edge chọn file bằng input thực tế khi tạo và sửa, preview/lưu/hiển thị, bỏ ảnh và giữ ảnh khi hủy.
- Cập nhật README hướng dẫn và vị trí backup ảnh; database backup không tự bao gồm file ảnh.

## File dự kiến

Frontend: component chọn ảnh, ResourcePage field ảnh, BooksPages và helper dựng URL ảnh.
Backend: endpoint upload, service xử lý/lưu ảnh, cấu hình thư mục/static mount, schema anh_bia và dependency xử lý ảnh/multipart.
Không đổi cổng 5000/8001/5432 hoặc dữ liệu hiện có.
