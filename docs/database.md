# PostgreSQL và file SQL được cung cấp

Ngày cập nhật: 05/11/2026. Người dùng chọn kết nối server PostgreSQL local có sẵn trong pgAdmin, cổng **5432**. Backend đã chuyển sang server này.

## Kết nối hiện tại

| Thuộc tính | Giá trị |
|---|---|
| Host | 127.0.0.1 |
| Port | 5432 |
| Database | library_management |
| Username | library_app |
| Password | Xem riêng trong DATABASE_URL của backend/.env; không chia sẻ hoặc commit file |
| Driver SQLAlchemy | postgresql+psycopg |
| Migration hiện tại | 0002_auth_accounts |

Trong pgAdmin, đăng ký server với các thông tin trên và maintenance database `library_management`. Không dùng database `postgres` làm maintenance database nếu chỉ muốn thao tác database ứng dụng.

Server pgAdmin đang đăng ký dùng `localhost:5432`, maintenance database `postgres`, username `postgres`. Có thể giữ nguyên đăng ký này và Refresh mục Databases để thấy `library_management`. Backend dùng role riêng `library_app` không có SUPERUSER, CREATEDB hay CREATEROLE; không dùng tài khoản postgres cho ứng dụng.

Server là service PostgreSQL hiện có của máy; không sửa cấu hình service hoặc các database khác. Kiểm tra kết nối từ thư mục gốc:

```powershell
backend/.venv/Scripts/python.exe backend/scripts/check_database.py
```

## Instance riêng cũ ở cổng 5433

Database đã tạo trước đó trong `.local/postgres` vẫn được giữ nguyên để tránh mất dữ liệu. Bản lưu cấu hình kết nối cũ nằm trong `.local/backend-env-before-5432.txt`, được Git bỏ qua. Instance đó không còn là database backend đang sử dụng. Không chạy `setup_local_database.py` khi dùng server 5432.

Dừng riêng instance cũ nếu không cần chạy song song:

```powershell
& 'C:\Program Files\PostgreSQL\18\bin\pg_ctl.exe' -D 'D:\LibraryManagement\.local\postgres' -m fast -w stop
```

Không xóa `.local/postgres` vì đó là dữ liệu database thật. Không thay đổi cổng tự động hoặc khởi động Docker cùng cổng 5433 khi instance cũ còn chạy.

## Schema nhập từ file

Nguồn: `C:\Users\Admin3---\Downloads\library_management.sql`.
Bản sao nguyên vẹn: `backend/sql/library_management.sql`.
SHA256: `214D558B9C76B4DA4606ADB751908984A5DA284BADCF4B01B5964AB8EB870461`.

| Bảng | Số bản ghi mẫu khi nhập |
|---|---:|
| nguoi_dung | 5 |
| the_thu_vien | 3 |
| the_loai | 3 |
| tac_gia | 3 |
| nha_xuat_ban | 3 |
| sach | 3 |
| sach_tac_gia | 3 |
| cuon_sach | 5 |
| phieu_muon | 2 |
| chi_tiet_muon | 2 |
| dat_truoc_sach | 2 |
| tien_phat | 1 |

Alembic thêm bảng kỹ thuật `alembic_version` ngoài 12 bảng trên. Migration `0002_auth_accounts` đã thêm bảng `password_reset_request` và các cột auth_version/must_change_password vào nguoi_dung; tổng cộng 13 bảng chức năng. Đã sao lưu trước thay đổi và giữ nguyên 35 seed. Import hoàn tất trong transaction; migration không nhập trùng dữ liệu hoặc tự xóa/reset bảng.

Vai trò database/API giữ nguyên `ADMIN`, `THU_THU`, `DOC_GIA`. ORM, authentication và API nghiệp vụ đã triển khai. Mật khẩu seed `REPLACE_WITH_REAL_HASH` vẫn là placeholder; chạy bootstrap nhập ẩn trong README để tự đặt mật khẩu Admin, không có password demo.

Schema baseline được quản lý qua SQL migration; ORM metadata hiện khớp schema đã migrate (có test so sánh). CLI autogenerate vẫn chặn metadata trống. Downgrade chủ động từ chối xóa dữ liệu; muốn rollback phải sao lưu và lên kế hoạch riêng.

## Docker là phương án thay thế

`docker-compose.yml` vẫn giữ cấu hình PostgreSQL 17, đáp ứng SQL yêu cầu PostgreSQL 14+. Docker có volume riêng và không chia sẻ dữ liệu với cluster native.

Nếu muốn chuyển sang Docker: dừng instance native, điền `.env` gốc theo mẫu, chạy `docker compose up -d db`, cập nhật `backend/.env` đúng tài khoản Docker rồi chạy `alembic upgrade head` trên database trống. Không chạy script setup native khi đang sử dụng Docker.

## Tài liệu đối chiếu

- [PostgreSQL initdb](https://www.postgresql.org/docs/current/app-initdb.html)
- [SQLAlchemy driver SQL](https://docs.sqlalchemy.org/en/20/core/connections.html#sqlalchemy.engine.Connection.exec_driver_sql)
- [Alembic operations](https://alembic.sqlalchemy.org/en/latest/ops.html)
