# Library Management System — Hướng dẫn sử dụng

Ứng dụng quản lý thư viện bằng React + TypeScript + Ant Design, FastAPI + SQLAlchemy và PostgreSQL. Hệ thống hỗ trợ đủ UC01–UC12: tài khoản, hồ sơ, độc giả/thẻ, đầu sách/bản sao, danh mục, tra cứu, mượn–trả, đặt trước, tiền phạt và báo cáo.

Hướng dẫn dành cho Windows/PowerShell. Thư mục dự án trên máy hiện tại: **D:\LibraryManagement**.

## Mục lục

1. [Chạy nhanh trên máy hiện tại](#1-chạy-nhanh-trên-máy-hiện-tại)
2. [Tài khoản demo và mật khẩu](#2-tài-khoản-demo-và-mật-khẩu)
3. [Công nghệ, cổng và cấu trúc](#3-công-nghệ-cổng-và-cấu-trúc)
4. [Cài đặt trên máy mới](#4-cài-đặt-trên-máy-mới)
5. [Cấu hình môi trường](#5-cấu-hình-môi-trường)
6. [Kết nối PostgreSQL bằng pgAdmin](#6-kết-nối-postgresql-bằng-pgadmin)
7. [Sử dụng theo vai trò](#7-sử-dụng-theo-vai-trò)
8. [Luồng demo mượn–trả hoàn chỉnh](#8-luồng-demo-mượntrả-hoàn-chỉnh)
9. [Swagger và API](#9-swagger-và-api)
10. [Kiểm thử và build](#10-kiểm-thử-và-build)
11. [Migration và sao lưu](#11-migration-và-sao-lưu)
12. [Lỗi thường gặp](#12-lỗi-thường-gặp)
13. [Các script và tài liệu liên quan](#13-các-script-và-tài-liệu-liên-quan)

## 1. Chạy nhanh trên máy hiện tại

Database, dependency và file môi trường đã được cấu hình trên máy hiện tại. Không cần tạo lại database hoặc ghi đè các file .env.

### Bước 1 — Kiểm tra PostgreSQL

Mở terminal PowerShell tại thư mục dự án:

~~~powershell
cd D:\LibraryManagement
backend/.venv/Scripts/python.exe backend/scripts/check_database.py
~~~

Kết quả mong đợi: database library_management, user library_app, port 5432, revision 0002_auth_accounts và số bản ghi từng bảng.

Lệnh này kiểm tra kết nối database thực tế. API healthcheck chỉ kiểm tra tiến trình backend, không thay thế lệnh trên.

### Bước 2 — Chạy backend ở terminal thứ nhất

~~~powershell
cd D:\LibraryManagement\backend
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8001
~~~

Giữ terminal mở. Nếu cổng 8001 đã có backend của dự án đang chạy, sử dụng tiến trình đó thay vì chạy thêm một bản.

### Bước 3 — Chạy frontend ở terminal thứ hai

~~~powershell
cd D:\LibraryManagement\frontend
npm.cmd run dev
~~~

Mở **http://localhost:5000** và đăng nhập bằng một tài khoản ở phần 2.

Dùng npm.cmd để tránh PowerShell chặn npm.ps1; không cần thay ExecutionPolicy. Giữ terminal frontend mở trong lúc sử dụng.

### Bước 4 — Dừng ứng dụng

Nhấn Ctrl+C tại từng terminal frontend/backend. Service PostgreSQL của máy vẫn tiếp tục hoạt động. Khi mở máy lại, kiểm tra service PostgreSQL, sau đó chạy lại hai terminal trên.

## 2. Tài khoản demo và mật khẩu

**Chỉ dùng các mật khẩu công khai này cho demo local. Không dùng chúng khi triển khai hoặc lưu dữ liệu thật.** Database vẫn lưu mật khẩu dưới dạng hash Argon2id; bảng dưới được công khai theo yêu cầu để tiện thử nghiệm.

| Vai trò | Email đăng nhập | Mật khẩu dễ nhớ |
|---|---|---|
| Admin | admin.demo@library.example | AdminDemo@123 |
| Thủ thư | thuthu.demo@library.example | ThuThuDemo@123 |
| Độc giả | docgia.demo@library.example | DocGiaDemo@123 |

Cả ba mật khẩu trên đã được đặt trên database ứng dụng của máy hiện tại và kiểm tra đăng nhập qua API thành công. Các mật khẩu ngẫu nhiên đã cấp trước đó không còn hiệu lực. Tài khoản Độc giả demo đã có thẻ; tình trạng/hạn thẻ được xem tại màn hình Độc giả và thẻ.

### Các điểm cần biết khi đăng nhập

- Mật khẩu phân biệt chữ hoa/chữ thường; không thêm dấu cách.
- Các tài khoản demo được dùng ngay, không bị yêu cầu đổi mật khẩu tạm.
- Tài khoản thông thường do Admin tạo hoặc reset phải đổi mật khẩu ở lần sử dụng tiếp theo.
- Token chỉ giữ trong bộ nhớ trình duyệt: tải lại trang hoặc mở tab mới sẽ cần đăng nhập lại.
- Đăng xuất, đổi mật khẩu, khóa tài khoản hoặc đổi quyền làm token cũ mất hiệu lực.
- Muốn thử nhiều vai trò song song, mở các cửa sổ trình duyệt riêng/ẩn danh. Không tải lại trang để chuyển vai trò; dùng Đăng xuất rồi đăng nhập lại.

### Tạo lại tài khoản demo bằng script

Từ thư mục backend:

~~~powershell
.\.venv\Scripts\python.exe -X utf8 -m scripts.seed_demo_accounts
~~~

Script tạo các tài khoản còn thiếu và **sinh mật khẩu ngẫu nhiên**, in một lần ra terminal. Tài khoản đã tồn tại được giữ nguyên.

Đặt lại mật khẩu của cả ba tài khoản demo bằng mật khẩu ngẫu nhiên mới:

~~~powershell
.\.venv\Scripts\python.exe -X utf8 -m scripts.seed_demo_accounts --reset-passwords
~~~

Sau lệnh này, mật khẩu trong bảng README sẽ không còn đúng; dùng mật khẩu mới được in ra. Script không tự khôi phục ba mật khẩu dễ nhớ trong bảng. Với một tài khoản cụ thể, Admin có thể dùng màn hình Tài khoản → Đặt lại mật khẩu.

Không đưa mật khẩu database, JWT_SECRET hoặc mật khẩu người dùng thật vào README.

## 3. Công nghệ, cổng và cấu trúc

### Công nghệ

| Thành phần | Công nghệ |
|---|---|
| Frontend | React, TypeScript strict, Vite, Ant Design, React Router |
| Gọi API và state | Axios, TanStack Query, Zustand giữ phiên bộ nhớ |
| Backend | Python 3.12+, FastAPI, Uvicorn |
| Database access | SQLAlchemy 2.x, Psycopg 3 |
| Validation/config | Pydantic v2, Pydantic Settings |
| Bảo mật | JWT HS256, Argon2id, phân quyền backend |
| Migration/kiểm thử | Alembic, Pytest, Node test runner |

### Địa chỉ sử dụng

| Dịch vụ | Địa chỉ |
|---|---|
| Website | http://localhost:5000 |
| Backend | http://localhost:8001 |
| API | http://localhost:8001/api/v1 |
| Swagger | http://localhost:8001/docs |
| OpenAPI JSON | http://localhost:8001/openapi.json |
| API healthcheck | http://localhost:8001/api/v1/health |
| PostgreSQL hiện tại | 127.0.0.1:5432 |

Frontend có strictPort: true; không tự chuyển cổng nếu 5000 bị chiếm.

Instance dự án cũ tại 5433 và Docker Compose là phương án riêng, **không phải database đang dùng**. Không chạy setup_local_database.py khi đang dùng server pgAdmin 5432.

### Cấu trúc chính

~~~text
LibraryManagement/
├── frontend/
│   ├── src/
│   │   ├── app/                 # Provider và CSS
│   │   ├── components/          # Form, bảng và component chung
│   │   ├── features/            # Các module nghiệp vụ
│   │   ├── hooks/
│   │   ├── layouts/             # Layout và menu theo vai trò
│   │   ├── routes/
│   │   ├── services/            # Axios/API
│   │   ├── stores/              # Phiên đăng nhập trong bộ nhớ
│   │   ├── types/
│   │   └── utils/
│   ├── tests/
│   └── .env.example
├── backend/
│   ├── app/
│   │   ├── api/v1/endpoints/
│   │   ├── core/
│   │   ├── db/
│   │   ├── dependencies/
│   │   ├── models/
│   │   ├── repositories/
│   │   ├── schemas/
│   │   └── services/
│   ├── alembic/versions/
│   ├── scripts/
│   ├── sql/library_management.sql
│   ├── tests/
│   └── .env.example
├── docs/
├── .local/                      # Backup, dữ liệu/cấu hình local, bị Git bỏ qua
├── AGENTS.md
├── docker-compose.yml
└── README.md
~~~

Backend theo luồng Router → Service → Repository → Database. Nghiệp vụ và transaction nằm ở service; quyền truy cập được kiểm tra tại backend.

## 4. Cài đặt trên máy mới

Bỏ qua phần này nếu đang sử dụng máy đã cấu hình và chạy được theo phần 1.

### 4.1. Chuẩn bị công cụ

- Node.js 22.12+; để dùng đúng bộ lệnh test hiện tại, nên dùng Node.js 24 như môi trường đã kiểm chứng.
- Python 3.12 trở lên.
- PostgreSQL 18 và pgAdmin.
- PowerShell, VS Code tùy chọn.

Kiểm tra:

~~~powershell
node --version
npm.cmd --version
py -3 --version
~~~

Nếu lệnh py không tồn tại nhưng python hoạt động, thay py -3 bằng python và kiểm tra phiên bản trước khi tạo môi trường.

### 4.2. Cài backend

Từ thư mục gốc:

~~~powershell
cd D:\LibraryManagement
py -3 -m venv backend/.venv
backend/.venv/Scripts/python.exe -m pip install -e "./backend[dev]"
~~~

Không cần kích hoạt venv; gọi trực tiếp python.exe trong .venv để bảo đảm dùng đúng dependency.

Chỉ tạo file môi trường nếu chưa tồn tại:

~~~powershell
if (-not (Test-Path backend/.env)) {
    Copy-Item backend/.env.example backend/.env
}
~~~

Điền DATABASE_URL và JWT_SECRET theo phần 5 trước khi chạy migration hoặc đăng nhập.

### 4.3. Tạo database trống

Trong pgAdmin, kết nối server localhost:5432 bằng tài khoản quản trị PostgreSQL.

1. Vào Login/Group Roles → Create để tạo role library_app.
2. Đặt mật khẩu database riêng, bật quyền Can login; không bật Superuser/Create roles/Create databases cho tài khoản ứng dụng.
3. Vào Databases → Create → Database.
4. Đặt tên library_management, chọn owner library_app, encoding UTF8.
5. Điền mật khẩu role này vào DATABASE_URL của backend/.env.

Các mật khẩu demo tại phần 2 là mật khẩu đăng nhập website, **khác mật khẩu role PostgreSQL**.

Chỉ chạy migration khi database đích mới và trống, hoặc đã được quản lý bởi lịch sử Alembic của dự án:

~~~powershell
cd D:\LibraryManagement\backend
.\.venv\Scripts\python.exe -m alembic upgrade head
.\.venv\Scripts\python.exe -m alembic current
~~~

Revision hiện tại mong đợi: 0002_auth_accounts.

Không vừa nhập SQL thủ công vừa chạy baseline migration trên cùng database: sẽ trùng bảng. Database đã nhập SQL thủ công nhưng chưa có alembic_version cần được kiểm tra riêng trước khi tiếp tục; không tự stamp hoặc xóa bảng để né lỗi.

### 4.4. Khởi tạo tài khoản trên máy mới

Baseline SQL có Admin admin@library.example nhưng password hash là placeholder. Đặt mật khẩu tự chọn bằng lệnh nhập ẩn:

~~~powershell
cd D:\LibraryManagement\backend
.\.venv\Scripts\python.exe -X utf8 -m scripts.bootstrap_admin --email admin@library.example
~~~

Nhập và xác nhận mật khẩu từ 12 đến 256 ký tự. Script chỉ xử lý tài khoản ADMIN đã tồn tại; không dùng lệnh này cho tài khoản Thủ thư/Độc giả.

Để thêm tài khoản demo, chạy seed_demo_accounts theo phần 2 và lưu lại mật khẩu ngẫu nhiên được in ra. Ba mật khẩu dễ nhớ trong README được đặt trên máy hiện tại, không tự xuất hiện sau khi migrate database mới.

### 4.5. Cài frontend

~~~powershell
cd D:\LibraryManagement\frontend
npm.cmd ci
if (-not (Test-Path .env)) {
    Copy-Item .env.example .env
}
npm.cmd run dev
~~~

npm.cmd ci dùng package-lock.json để cài dependency. Dùng npm.cmd install khi chủ động thay dependency; không xóa lockfile để xử lý lỗi thông thường.

Sau đó chạy backend theo phần 1, mở website và đăng nhập.

## 5. Cấu hình môi trường

### Backend: backend/.env

~~~dotenv
DATABASE_URL=postgresql+psycopg://library_app:YOUR_DATABASE_PASSWORD@127.0.0.1:5432/library_management
JWT_SECRET=YOUR_UNIQUE_RANDOM_SECRET_AT_LEAST_32_CHARACTERS
CORS_ORIGINS=["http://localhost:5000"]
ACCESS_TOKEN_MINUTES=30
AUTH_RATE_LIMIT=20
AUTH_RATE_WINDOW_SECONDS=300
RESERVATION_HOLD_HOURS=48
~~~

| Biến | Ý nghĩa |
|---|---|
| DATABASE_URL | Kết nối PostgreSQL bằng Psycopg 3 |
| JWT_SECRET | Secret ký JWT riêng cho môi trường, tối thiểu 32 ký tự |
| CORS_ORIGINS | Danh sách JSON origin frontend được phép gọi API |
| ACCESS_TOKEN_MINUTES | Thời hạn access token, mặc định 30 phút |
| AUTH_RATE_LIMIT | Số yêu cầu auth tối đa theo IP trong cửa sổ thời gian |
| AUTH_RATE_WINDOW_SECONDS | Độ dài cửa sổ rate limit, mặc định 300 giây |
| RESERVATION_HOLD_HOURS | Thời hạn nhận khi đặt trước chuyển READY, mặc định 48 giờ |

Để sinh secret cho môi trường mới:

~~~powershell
backend/.venv/Scripts/python.exe -c "import secrets; print(secrets.token_hex(48))"
~~~

Dán kết quả vào JWT_SECRET của file .env riêng, không vào README. Với mật khẩu PostgreSQL chứa ký tự đặc biệt như @, :, / hoặc #, URL-encode phần mật khẩu trước khi điền DATABASE_URL.

Settings đọc file backend/.env; biến môi trường của terminal có thể ghi đè giá trị trong file. Nếu ứng dụng trỏ nhầm database, kiểm tra DATABASE_URL của terminal. Sau khi đổi .env, khởi động lại backend.

### Frontend: frontend/.env

~~~dotenv
VITE_API_BASE_URL=http://localhost:8001/api/v1
~~~

Khởi động lại Vite sau khi sửa file này. Biến VITE_* được đưa vào trình duyệt; không đặt mật khẩu database/JWT secret tại đây.

Root .env chỉ phục vụ phương án Docker Compose, không thay thế backend/.env.

## 6. Kết nối PostgreSQL bằng pgAdmin

Có thể tiếp tục dùng đăng ký server PostgreSQL local hiện tại:

| Trường | Giá trị |
|---|---|
| Host name/address | localhost hoặc 127.0.0.1 |
| Port | 5432 |
| Maintenance database | postgres |
| Username | postgres |
| Password | Mật khẩu PostgreSQL của bạn |

Nhấp phải Databases → Refresh → mở library_management → Schemas → public → Tables.

Nếu muốn đăng ký kết nối chỉ bằng tài khoản ứng dụng:

| Trường | Giá trị |
|---|---|
| Host name/address | 127.0.0.1 |
| Port | 5432 |
| Maintenance database | library_management |
| Username | library_app |
| Password | Mật khẩu DATABASE_URL trong backend/.env |

Schema gồm 12 bảng gốc, password_reset_request và bảng kỹ thuật alembic_version. Xem dữ liệu bằng View/Edit Data; không sửa trực tiếp hash mật khẩu, trạng thái mượn hoặc số tiền phạt để thử nghiệm giao diện.

## 7. Sử dụng theo vai trò

### 7.1. Admin

Các dropdown trong form và bộ lọc cho phép gõ để tìm lựa chọn. Danh sách lọc tại chỗ hỗ trợ không phân biệt hoa/thường và dấu tiếng Việt, ví dụ van hoc → Văn học, doc gia → Độc giả, hoặc nhập mã vạch để tìm cuốn. Dropdown độc giả/đầu sách trong phiếu mượn tìm qua API và tải thêm kết quả khi cuộn.

Đăng nhập admin.demo@library.example.

- **Tài khoản:** tìm kiếm, tạo Thủ thư/Độc giả, sửa thông tin, đổi quyền, khóa/mở và đặt lại mật khẩu.
- Tài khoản mới có mật khẩu tạm, phải đổi khi đăng nhập.
- Không thể tự khóa/hạ quyền Admin đang đăng nhập hoặc loại bỏ Admin hoạt động cuối cùng.
- **Khôi phục mật khẩu:** kiểm tra yêu cầu, xác minh danh tính qua kênh phù hợp, đặt mật khẩu tạm hoặc từ chối. Hệ thống không gửi email.
- Admin cũng thực hiện được nghiệp vụ của Thủ thư và xem báo cáo.

### 7.2. Thủ thư

Đăng nhập thuthu.demo@library.example.

**Chuẩn bị sách:**

1. Vào Thể loại, Tác giả, Nhà xuất bản để tạo danh mục.
2. Vào Tra cứu sách → Thêm sách.
3. Chọn thể loại/NXB, thêm tác giả và thông tin đầu sách.
4. Mở chi tiết sách → Thêm cuốn sách.
5. Nhập mã vạch riêng cho mỗi cuốn, vị trí kệ và tình trạng.

**Chọn/thay/bỏ ảnh bìa từ máy:**

1. Trong form Thêm sách hoặc Sửa sách, tìm mục Ảnh bìa → Chọn ảnh từ máy.
2. Chọn JPG/JPEG, PNG hoặc WebP tối đa 5 MB. Backend chỉ nhận ảnh tĩnh, không quá 20 triệu điểm ảnh; kiểm tra nội dung thật thay vì chỉ tên file.
3. Đợi ảnh tải lên và xuất hiện bản xem trước. Nút Lưu bị khóa khi đang upload hoặc upload lỗi; có thể thử tải lại hoặc bỏ lựa chọn lỗi.
4. Bấm Lưu để gắn ảnh vào sách. Khi sửa, chọn ảnh khác để thay hoặc Bỏ ảnh để xóa liên kết ảnh bìa.
5. Bấm Hủy để giữ nguyên dữ liệu sách; chọn/tải ảnh lên chưa tự lưu thay đổi sách.

Ảnh xuất hiện ở danh sách và chi tiết sách. URL ảnh cũ vẫn được hỗ trợ; không cần nhập URL khi chọn file từ máy. Ảnh được chuẩn hóa thành WebP, bỏ metadata và thu nhỏ cạnh dài tối đa 2400 pixel. Chỉ Admin/Thủ thư được upload.

Đầu sách/ấn phẩm là sach; từng bản sao vật lý là cuon_sach. Một đầu sách có thể có nhiều cuốn.

**Chuẩn bị độc giả/thẻ:**

1. Admin tạo tài khoản có vai trò Độc giả nếu chưa có.
2. Vào Độc giả và thẻ, tìm tài khoản.
3. Cấp thẻ với mã thẻ duy nhất, ngày cấp và hạn thẻ.
4. Ngày hết hạn phải sau ngày cấp.
5. Có thể gia hạn hoặc khóa/mở thẻ. Mỗi độc giả có tối đa một thẻ.

**Mượn và trả:**

- Lập phiếu ở Mượn / trả sách; chọn độc giả, đầu sách, bản sao AVAILABLE và hạn trả tương lai.
- Thêm từng cuốn vào phiếu rồi Xác nhận mượn. Tất cả cuốn được xử lý trong một transaction.
- Mở Chi tiết phiếu → Nhận trả để trả từng cuốn.
- Bình thường chuyển cuốn về AVAILABLE; hỏng/mất giữ DAMAGED/LOST.
- Nếu có phạt, nhập số tiền >0 và lý do. Không trả cùng lượt hai lần.

**Đặt trước và phạt:**

- Hàng đợi đặt trước xử lý theo FIFO: ngày đặt rồi id.
- Chỉ yêu cầu đầu hàng đợi được chuyển Sẵn sàng khi có cuốn AVAILABLE.
- Thời hạn nhận mặc định 48 giờ; trạng thái READY không giữ riêng một cuốn vật lý.
- Chọn Lập phiếu nhận để tạo phiếu và hoàn tất yêu cầu READY phù hợp.
- READY hết hạn được xử lý hủy khi truy vấn/xử lý hàng đợi, không cần scheduler riêng.
- Tiền phạt nhập thủ công; xác nhận thanh toán một lần. Chưa hỗ trợ trả góp/cổng thanh toán.
- Không thể xóa danh mục/sách/cuốn có ràng buộc hoặc lịch sử tham chiếu.

### 7.3. Độc giả

Đăng nhập docgia.demo@library.example.

- **Tra cứu sách:** tìm tên/ISBN, lọc thể loại/tác giả/NXB, xem chi tiết và số cuốn có thể mượn.
- **Đặt trước:** chọn đầu sách, xác nhận đặt trước; xem và hủy yêu cầu cá nhân.
- **Sách của tôi:** xem đang mượn, quá hạn và lịch sử trả/mất.
- **Tiền phạt của tôi:** chỉ xem khoản phạt thuộc tài khoản đang đăng nhập.
- **Hồ sơ:** sửa họ tên/số điện thoại và đổi mật khẩu; không tự đổi vai trò hoặc trạng thái.

### 7.4. Báo cáo

Admin/Thủ thư mở Tổng quan hoặc Báo cáo:

- Tổng đầu sách, bản sao, độc giả, độc giả hoạt động, đang mượn và quá hạn.
- Lượt mượn theo tháng và sách được mượn nhiều.
- Tiền phạt đã thu/chưa thu.
- Khoảng ngày theo múi giờ Việt Nam; hỗ trợ năm 1900–2200.
- Tổng kho hiện tại là ảnh chụp trạng thái hiện tại; lượt mượn và tiền phạt được lọc theo khoảng báo cáo.
- Số liệu lấy từ các bảng nghiệp vụ, không có bảng thống kê riêng.

## 8. Luồng demo mượn–trả hoàn chỉnh

1. Đăng nhập Thủ thư.
2. Kiểm tra Độc giả demo có thẻ ACTIVE, còn hạn.
3. Tra cứu một sách có ít nhất một bản sao AVAILABLE.
4. Vào Mượn / trả sách → Lập phiếu mượn.
5. Chọn Độc giả demo, đầu sách và mã vạch cuốn.
6. Đặt hạn trả tương lai → Thêm cuốn vào phiếu → Xác nhận mượn.
7. Kiểm tra phiếu vừa tạo và trạng thái cuốn BORROWED.
8. Đăng xuất, đăng nhập Độc giả demo, mở Sách của tôi để xem phiếu.
9. Đăng xuất, đăng nhập Thủ thư, mở Chi tiết phiếu → Nhận trả.
10. Chọn tình trạng Bình thường để cuốn về AVAILABLE; chọn Hỏng/Mất để kiểm tra trạng thái tương ứng.
11. Nếu tạo khoản phạt, vào Tiền phạt để xác nhận thanh toán.
12. Đăng nhập Độc giả để xem lịch sử và khoản phạt cá nhân.

Các thao tác demo ghi dữ liệu thật vào database local. Để không làm thay đổi dữ liệu cần giữ, dùng database test biệt lập thay cho database ứng dụng.

## 9. Swagger và API

Mở http://localhost:8001/docs khi backend đang chạy.

1. Tìm POST /api/v1/auth/login → Try it out.
2. Nhập email/password demo dưới dạng JSON → Execute.
3. Sao chép access_token từ phản hồi.
4. Bấm Authorize và dán token vào ô Bearer authentication.
5. Thử GET /api/v1/auth/me hoặc endpoint theo quyền.

Ví dụ request đăng nhập:

~~~json
{
  "email": "admin.demo@library.example",
  "password": "AdminDemo@123"
}
~~~

Các nhóm API:

| Nhóm | Endpoint tiêu biểu |
|---|---|
| Xác thực/hồ sơ | /auth/login, /auth/me, /auth/logout, /auth/change-password |
| Khôi phục | /auth/forgot-password, /password-reset-requests |
| Tài khoản | /users |
| Sách/bản sao | /books, /books/{id}/copies, /copies/{id} |
| Danh mục | /categories, /authors, /publishers |
| Độc giả/thẻ | /readers, /readers/{id}/card, /cards/{id} |
| Mượn/trả | /borrowings, /loan-items/{id}/return |
| Đặt trước | /reservations, /my-reservations |
| Tiền phạt | /fines, /my-fines |
| Lịch sử cá nhân | /my-borrowings |
| Báo cáo | /reports |

Tất cả đường dẫn trong bảng có prefix /api/v1.

Danh sách trả items, total, page, page_size; page_size tối đa 100. HTTP thường gặp: 401 phiên không hợp lệ, 403 thiếu quyền, 404 không tìm thấy/ngoài phạm vi cá nhân, 409 xung đột trạng thái/dữ liệu, 422 dữ liệu không hợp lệ, 429 vượt giới hạn auth.

## 10. Kiểm thử và build

### Máy hiện tại đã có database test

Từ thư mục gốc:

~~~powershell
cd D:\LibraryManagement
backend/.venv/Scripts/python.exe -m pytest backend/tests -q
backend/.venv/Scripts/python.exe -m pip check
backend/.venv/Scripts/python.exe -m compileall -q backend/app backend/alembic backend/scripts
~~~

Cấu hình test local nằm trong .local/test-database.env; được Git bỏ qua.

Frontend:

~~~powershell
cd D:\LibraryManagement\frontend
npm.cmd run typecheck
npm.cmd test
npm.cmd run build
~~~

Build tạo thư mục frontend/dist. Muốn xem build local:

~~~powershell
npm.cmd run preview
~~~

Preview cũng dùng cổng 5000, nên dừng Vite dev trước. Backend vẫn cần chạy ở 8001. Preview không phải cấu hình triển khai production.

### Chuẩn bị database test trên máy mới

1. Tạo database library_management_test, owner library_app trong pgAdmin.
2. Từ thư mục gốc, lấy URL database ứng dụng, đổi **chỉ tên database** sang database test trong biến môi trường cho terminal hiện tại.
3. Chạy migration trên DB test rồi chạy pytest.

~~~powershell
cd D:\LibraryManagement
$env:TEST_DATABASE_URL = & backend/.venv/Scripts/python.exe -c "from dotenv import dotenv_values; from sqlalchemy import make_url; u=make_url(dotenv_values('backend/.env')['DATABASE_URL']); print(u.set(database='library_management_test').render_as_string(hide_password=False))"
$env:DATABASE_URL = $env:TEST_DATABASE_URL
backend/.venv/Scripts/python.exe -m alembic -c backend/alembic.ini upgrade head
Remove-Item Env:DATABASE_URL
backend/.venv/Scripts/python.exe -m pytest backend/tests -q
Remove-Item Env:TEST_DATABASE_URL
~~~

Các biến trên chỉ dùng cho terminal test; không chạy backend ứng dụng trong terminal đang có DATABASE_URL trỏ DB test. Nếu terminal đã có DATABASE_URL chủ động từ trước, lưu lại và khôi phục giá trị thay vì xóa.

Fixtures chỉ chấp nhận database tên library_management_test, dùng savepoint; test đa luồng dọn đúng bản ghi nó tạo. Không chạy pytest trên database ứng dụng.

Đã có 48 test backend, 3 test frontend và kiểm chứng Edge desktop/mobile cùng luồng mượn–trả trong lần bàn giao chức năng. Kết quả là lịch sử kiểm chứng, không thay thế việc chạy lại sau khi đổi mã: xem [verification.md](docs/verification.md).

## 11. Migration và sao lưu

### Migration đang có

| Revision | Nội dung |
|---|---|
| 0001_library_schema | Nhập schema và seed từ SQL gốc |
| 0002_auth_accounts | Thêm auth_version, must_change_password và bảng password_reset_request |

Từ thư mục backend:

~~~powershell
.\.venv\Scripts\python.exe -m alembic current
.\.venv\Scripts\python.exe -m alembic history
.\.venv\Scripts\python.exe -m alembic upgrade head
~~~

Khi phát triển schema mới:

~~~powershell
.\.venv\Scripts\python.exe -m alembic revision --autogenerate -m "describe schema change"
~~~

Review migration và sao lưu trước khi áp dụng. Autogenerate không tự bảo đảm mọi thay đổi an toàn. Không dùng create_all tại startup, không drop bảng để xử lý lỗi và không tự downgrade phá dữ liệu.

### Sao lưu bằng pgAdmin

1. Nhấp phải database library_management → Backup.
2. Chọn file đích có ngày giờ và định dạng Custom.
3. Thực hiện Backup và kiểm tra thông báo thành công.
4. Giữ bản sao trước khi thay migration hoặc nhập dữ liệu khác.

Bản sao trước migration chức năng trên máy hiện tại nằm ở .local/library-before-features-20261105-225133.backup. Bản sao này được tạo **trước các thay đổi tài khoản demo sau đó**, nên không chứa trạng thái/mật khẩu demo hiện tại.

Chỉ Restore vào database đích đã được kiểm tra; không khôi phục đè database ứng dụng khi chưa xác định ảnh hưởng. Hướng dẫn database bổ sung tại [database.md](docs/database.md).

### Sao lưu ảnh bìa

Ảnh upload mặc định nằm ở .local/uploads/covers, được phục vụ từ backend qua /media/covers/<tên-ngẫu-nhiên>.webp. Cột anh_bia chỉ lưu đường dẫn; backup PostgreSQL **không bao gồm các file ảnh**. Khi chuyển máy hoặc khôi phục dữ liệu, sao lưu/khôi phục cả database và thư mục ảnh tương ứng.

Có thể cấu hình COVER_UPLOAD_DIR trong backend/.env bằng đường dẫn thư mục lưu ảnh riêng có quyền ghi; khởi động lại backend sau khi đổi. Nếu không đặt, ứng dụng tự dùng .local/uploads/covers của dự án. Không xóa thư mục này nếu còn sách dùng ảnh bên trong. Bỏ/thay ảnh hoặc hủy form không tự xóa file cũ, để tránh ảnh hưởng bản ghi đang tham chiếu; dọn file không dùng là thao tác bảo trì riêng.

## 12. Lỗi thường gặp

| Hiện tượng | Kiểm tra/cách xử lý |
|---|---|
| Không mở được localhost:5000 | Kiểm tra terminal frontend, chạy npm.cmd run dev từ frontend |
| Frontend báo không kết nối được | Kiểm tra backend8001, VITE_API_BASE_URL và khởi động lại Vite sau khi đổi .env |
| PowerShell chặn npm.ps1 | Dùng npm.cmd, không cần tắt chính sách bảo vệ toàn máy |
| ModuleNotFoundError | Dùng python trong backend/.venv; cài lại dependency theo phần4.2 |
| Python/pip không đúng môi trường | Gọi .venv/Scripts/python.exe -m pip thay cho pip hệ thống |
| Connection refused PostgreSQL | Kiểm tra service PostgreSQL và 127.0.0.1:5432; chạy check_database.py |
| Password authentication failed | Kiểm tra mật khẩu role library_app trong DATABASE_URL, không dùng mật khẩu website thay thế |
| Backend trỏ nhầm DB | Kiểm tra biến DATABASE_URL của terminal có ghi đè backend/.env không |
| Thiếu JWT_SECRET/secret ngắn | Điền secret riêng tối thiểu32 ký tự, khởi động lại backend |
| Đăng nhập demo không đúng | Kiểm tra chữ hoa/thường; mật khẩu bảng README chỉ đúng nếu chưa đổi/reset lại |
| Tài khoản seed SQL không đăng nhập được | Hash placeholder chưa hợp lệ; dùng bootstrap cho Admin hoặc tài khoản demo |
| Reload trang bị đăng xuất | Đúng thiết kế token bộ nhớ; đăng nhập lại |
| Bị chuyển tới Đổi mật khẩu | Tài khoản mới/reset cần đổi mật khẩu tạm trước |
| HTTP403 | Tài khoản không có quyền với chức năng; kiểm tra vai trò đang đăng nhập |
| HTTP409 khi xóa | Dữ liệu còn tham chiếu/lịch sử; xử lý nghiệp vụ thay vì xóa trực tiếp trong DB |
| Không mượn được | Kiểm tra tài khoản độc giả hoạt động, thẻ ACTIVE/còn hạn, cuốn AVAILABLE, hạn trả tương lai |
| Đặt trước chưa thể READY | Kiểm tra FIFO, yêu cầu cũ hơn và số cuốn AVAILABLE |
| Đã thanh toán không trả lại được trạng thái | Hệ thống không cho thanh toán hai lần hoặc hoàn tiền trong phạm vi hiện tại |
| HTTP429 | Quá nhiều yêu cầu auth; mặc định chờ cửa sổ300 giây hoặc kiểm tra cấu hình rate limit |
| Pytest yêu cầu TEST_DATABASE_URL | Chuẩn bị database test theo phần10, không dùng DB ứng dụng |
| Migration báo bảng đã tồn tại | Kiểm tra đã nhập SQL thủ công/chạy migration chưa; không tự xóa bảng hoặc stamp để né lỗi |
| Build cảnh báo chunk >500KB | Build vẫn có thể thành công; vendor Ant Design còn lớn, các trang đã lazy-load |

### Kiểm tra cổng bị chiếm

~~~powershell
Get-NetTCPConnection -LocalPort 5000,8001,5432 -State Listen |
    Select-Object LocalAddress, LocalPort, OwningProcess
~~~

Dùng OwningProcess để xác định ứng dụng:

~~~powershell
Get-Process -Id <PID>
~~~

Thay <PID> bằng số thực tế trước khi chạy. Không tự dừng tiến trình không rõ nguồn gốc hoặc đổi cổng. 8000 thuộc ứng dụng khác nên dự án này dùng 8001.

## 13. Các script và tài liệu liên quan

| Script | Mục đích |
|---|---|
| backend/scripts/check_database.py | Kiểm tra kết nối và số bản ghi qua SQLAlchemy |
| backend/scripts/bootstrap_admin.py | Đặt mật khẩu cho ADMIN hiện có bằng nhập ẩn |
| backend/scripts/seed_demo_accounts.py | Tạo demo còn thiếu; tùy chọn reset bằng mật khẩu ngẫu nhiên |
| backend/scripts/setup_local_database.py | Instance riêng cũ5433; không dùng cho server hiện tại5432 |

- [Chức năng và chính sách](docs/features.md)
- [Database/pgAdmin](docs/database.md)
- [Kiến trúc](docs/architecture.md)
- [Kết quả kiểm chứng](docs/verification.md)
- [Nội dung đặc tả từ DOCX](docs/requirements-library.md)
- [Thiết kế chức năng đã duyệt](docs/superpowers/specs/2026-11-05-library-features-design.md)
- [Danh mục skill](SKILLS-AUDIT.md)

Các file .env thật, .local/, backup và node_modules/.venv không đưa vào Git. Ba mật khẩu demo công khai trong README là ngoại lệ phục vụ demo local theo yêu cầu; không áp dụng ngoại lệ này cho database password, JWT_SECRET hoặc tài khoản thật.
