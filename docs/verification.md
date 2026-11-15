# Kết quả kiểm chứng bộ khung

Hoàn tất ngày 05/11/2026 (Asia/Saigon).

## Tìm kiếm trong dropdown — cập nhật mới nhất

- Đã bật nhập tìm kiếm cho tất cả Select trong form/bộ lọc: danh mục sách, vai trò/trạng thái, cuốn có sẵn và các trang cá nhân.
- Lọc local dùng nhãn/mã lựa chọn, không phân biệt hoa thường và dấu tiếng Việt; remote độc giả/sách giữ tìm kiếm API và phân trang cuộn.
- PASS: frontend7tests, TypeScript strict và production build. Cảnh báo vendor chunk lớn vẫn giữ nguyên.
- PASS: Edge thực tế tìm van hoc → Văn học, nguyen → Nguyễn Nhật Ánh, san sang → Sẵn sàng nhận, trạng thái thanh toán, mã vạch BC0002 và tìm độc giả/đầu sách qua API. Kiểm tra chỉ đọc, không lưu form hoặc ghi dữ liệu nghiệp vụ.

## Chọn ảnh bìa từ máy — cập nhật mới nhất

- PASS: 61 test backend (48 có sẵn +13 upload), gồm quyền staff/reader/anonymous, PNG/JPEG/WebP, ảnh giả/hỏng, >5MiB, >20triệu pixel, metadata stripping, resize và lưu/bỏ đường dẫn ảnh trên sách.
- PASS: frontend5tests, TypeScript strict, production build; pip check và compileall. Cảnh báo kích thước vendor bundle và Starlette TestClient/httpx cũ vẫn còn.
- PASS: Edge dùng input file thật trên DB test: thêm sách có ảnh, preview sau upload, Lưu bị khóa khi upload, thay ảnh, Hủy giữ ảnh DB cũ, Bỏ ảnh lưu null, upload lỗi khóa Lưu và có thể bỏ lựa chọn lỗi. Ảnh WebP được tải công khai và hiển thị ở giao diện. Artifact .local/browser/cover-upload-detail.png.
- POST /api/v1/uploads/covers chỉ ADMIN/THU_THU; media GET /media/covers/{uuid}.webp. Thư mục mặc định .local/uploads/covers; chỉ lưu đường dẫn trong anh_bia, không cần migration.
- Review độc lập không phát hiện blocker. Minor deferred: lỗi mkdir/unlink bất thường có thể trả500; giới hạn5MiB ở mức file sau multipart parsing, chưa có giới hạn request tổng tại proxy/ASGI cho triển khai công khai.
- Sau E2E đã dừng API test và chạy lại backend trên database ứng dụng, cổng8001. README bổ sung thao tác chọn/thay/bỏ ảnh và yêu cầu backup cả thư mục ảnh.

## UC01–UC12 — kết quả mới nhất

- PASS: 48 kiểm thử backend trên database riêng library_management_test, gồm quyền, token revocation, tài khoản/thẻ/catalog, mượn–trả, phạt, FIFO/expiry, báo cáo múi giờ/Decimal và input sai kiểu.
- PASS: kiểm thử PostgreSQL đa luồng cho mượn/trả/thanh toán, và regression không để expiry ghi đè COMPLETED.
- PASS: so sánh ORM metadata với schema test đã migrate — không có khác biệt; pip check và compileall.
- PASS: frontend TypeScript strict, production build và 3 Node tests quyền/xử lý lỗi/phiên bộ nhớ.
- PASS: Edge headless đăng nhập cả ba vai trò, điều hướng 12 trang Admin/10 trang Thủ thư/4 trang Độc giả; desktop và mobile390px, không có pageerror/HTTP500; tạo thể loại qua UI trên DB test.
- PASS: Edge luồng chọn độc giả/sách/cuốn → lập phiếu → chi tiết → nhận trả; trạng thái API trả RETURNED. Artifact ảnh tại .local/browser/.
- PASS: sao lưu database ứng dụng trước migration vào .local/library-before-features-20261105-225133.backup; áp dụng 0002_auth_accounts thành công, số bản ghi cả 12 bảng cũ giữ nguyên (35 bản ghi). JWT_SECRET riêng đã cấu hình trong backend/.env, không in ra hoặc commit.
- Review độc lập phát hiện và đã sửa bằng test RED→GREEN: race expiry/COMPLETED; email null/số gây500. Ngoài ra response validation không còn echo password và ngày báo cáo ngoài1900–2200 trả422.
- Minor deferred: options danh mục sách chưa có thông báo lỗi tải riêng; vendor bundle >500kB và cảnh báo Starlette TestClient/httpx deprecation còn giữ nguyên.

Chưa đặt mật khẩu đăng nhập cho seed Admin theo đúng thiết kế. Người dùng chạy bootstrap nhập mật khẩu ẩn theo README; không có password demo. Chức năng và chính sách: [features.md](features.md).

## Server pgAdmin 5432 — cấu hình đang sử dụng

Theo ảnh server và yêu cầu mới nhất, đã tạo database library_management và role library_app trên server PostgreSQL có sẵn tại 127.0.0.1:5432. Đã nhập migration 0001_library_schema: 12 bảng nghiệp vụ, 35 bản ghi. Script check_database qua SQLAlchemy xác nhận đúng port 5432, tài khoản library_app không có quyền quản trị server. Backend/.env và file mẫu đã chuyển sang 5432. Cluster cũ 5433 vẫn giữ nguyên; các mục bên dưới ghi nhận quá trình thiết lập trước đó.

## Database từ SQL — cập nhật mới nhất

Người dùng đã chọn PostgreSQL 18 native thay cho Docker. Instance riêng tại `127.0.0.1:5433`, database `library_management`, backend kết nối qua `backend/.env` bằng tài khoản `library_app`. Không thay đổi service PostgreSQL có sẵn của máy.

- PASS: bản sao `backend/sql/library_management.sql` có SHA256 trùng file nguồn trong Downloads.
- PASS: migration `0001_library_schema` đã áp dụng, 12 bảng nghiệp vụ và 35 bản ghi mẫu; có thêm bảng kỹ thuật alembic_version.
- PASS: script check_database dùng chính SQLAlchemy engine của backend xác nhận database, port, tài khoản và số bản ghi từng bảng. Tài khoản ứng dụng không có SUPERUSER/CREATEDB/CREATEROLE.
- PASS: 6 test backend, gồm 2 test bảo vệ mới: CLI autogenerate metadata rỗng bị chặn trước khi kết nối, setup không dùng DATABASE_URL kế thừa để chạy migration nhầm database.
- PASS: compileall app, Alembic và scripts; revision hiện tại là head.
- Review độc lập phát hiện rủi ro DATABASE_URL kế thừa; đã tái hiện bằng test thất bại rồi sửa và chạy xanh.
- Chưa triển khai ORM mappings hoặc API nghiệp vụ. Healthcheck vẫn chỉ xác nhận API; kiểm tra database bằng `backend/.venv/Scripts/python.exe backend/scripts/check_database.py`.
- Mật khẩu tài khoản seed là placeholder; chưa thể dùng để đăng nhập. Vai trò SQL THU_THU/DOC_GIA cần ánh xạ khi triển khai auth.

Xem [database.md](database.md) để kết nối bằng pgAdmin và khởi động lại instance sau khi restart Windows.

## Lịch sử kiểm chứng bộ khung trước khi tạo database

Cập nhật cổng theo yêu cầu người dùng: backend chuyển từ 8000 sang **8001**. Đã cập nhật AGENTS.md, README.md, frontend/.env và frontend/.env.example. Các ghi nhận lỗi 8000 dưới đây là lịch sử trước khi đổi cổng.

Kiểm chứng sau khi đổi: Uvicorn khởi động thành công tại 127.0.0.1:8001; GET /api/v1/health trả 200; OpenAPI xác nhận đúng Library Management System API; CORS cho http://localhost:5000 hợp lệ. Frontend vẫn 5000, PostgreSQL vẫn 5433.

| Kiểm tra | Kết quả |
|---|---|
| Backend pytest | PASS — 4 test: healthcheck, OpenAPI, CORS origin hợp lệ và không hợp lệ. |
| Python compileall cho app/Alembic | PASS |
| pip check trong backend/.venv | PASS — không có dependency bị thiếu/xung đột. |
| Alembic upgrade head --sql | PASS với URL thử nghiệm qua biến môi trường, không kết nối database; chưa có migration nghiệp vụ. |
| Frontend TypeScript strict | PASS |
| Frontend production build | PASS; build cuối có VITE_API_BASE_URL từ file mẫu. |
| Frontend HTTP tại localhost:5000 | PASS — trả 200 từ Vite, không thay thế kiểm thử render trong trình duyệt. |
| Compose YAML, cổng, healthcheck | PASS bằng parser YAML; chưa xác nhận bằng Docker Compose. |
| Docker Compose config/runtime và PostgreSQL thật | NOT RUN — Docker chưa được cài/không có trong PATH. |
| Uvicorn thực tế tại 8000 | FAIL khi bind: cổng đã được PID 20108 (python) sử dụng. Không dừng tiến trình đó hoặc đổi cổng. |
| Browser/UI tương tác | NOT RUN — không có Chrome DevTools MCP hoặc browser tool. |
| ESLint/frontend unit test | NOT RUN — chưa cấu hình trong phạm vi bộ khung. |

Khi kiểm tra cổng 8000, API đang chạy trả tên `itms-backend`, không phải ứng dụng mới. Phản hồi đó không được tính là kiểm chứng backend của dự án. Backend mới được kiểm thử qua FastAPI TestClient.

Dependency đã được cài vào frontend/node_modules và backend/.venv. Frontend có package-lock.json. Chưa có file .env thật cho database; phải điền thông tin theo README trước khi chạy PostgreSQL và migration online.

Review độc lập không phát hiện lỗi Critical/Important. Hai điểm nhỏ để cải thiện sau: kiểm tra VITE_API_BASE_URL ngay ở bước build và làm test healthcheck độc lập hoàn toàn với DATABASE_URL của môi trường chạy. Hiện thiếu VITE_API_BASE_URL sẽ báo lỗi runtime; README yêu cầu sao chép file mẫu.

Cảnh báo giữ nguyên để theo dõi: bundle frontend khoảng 882 kB trước gzip; TestClient/Starlette cảnh báo chuyển từ httpx sang httpx2. Chưa tối ưu chunk hoặc thay dependency test ngoài phạm vi khởi tạo.
