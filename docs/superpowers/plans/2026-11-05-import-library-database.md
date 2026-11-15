# Import Library Database Implementation Plan

> **For agentic workers:** Use superpowers:executing-plans for changes and verification.

**Goal:** Tạo và kết nối database từ file SQL người dùng cung cấp.
**Architecture:** PostgreSQL 18 đã cài; cluster riêng .local/postgres tại 127.0.0.1:5433. Backend sử dụng Settings/SQLAlchemy hiện có. Alembic giữ baseline SQL.
**Tech Stack:** PostgreSQL 18, Psycopg 3, SQLAlchemy 2, Alembic.
**Spec:** File library_management.sql được cung cấp; người dùng đã chọn native PostgreSQL 18 thay Docker.

## Global Constraints

- Không thay đổi service PostgreSQL có sẵn hoặc database khác.
- Không ghi đè dữ liệu, không drop/reset bảng.
- Không in hoặc commit secret; giữ nguyên file SQL nguồn.

## Review Focus

- Migration luôn nhắm đúng database local, kể cả shell có DATABASE_URL khác.
- SQLAlchemy metadata chưa có ORM mappings, không để CLI autogenerate đề xuất xóa toàn bộ schema.
- Import một lần, chạy lại không nhân đôi seed; downgrade không phá dữ liệu.

## Tasks và kết quả

- [x] Đọc SQL; xác nhận 12 bảng, seed và transaction, không có DROP/TRUNCATE/DELETE thực thi.
- [x] Người dùng chọn PostgreSQL native; tạo cluster riêng, database và role ứng dụng không có quyền quản trị server.
- [x] Lưu SQL nguyên vẹn, tạo migration baseline; nhập thành công 35 bản ghi.
- [x] Tạo backend/.env bị ignore, kiểm tra qua engine ứng dụng; không tạo endpoint nghiệp vụ.
- [x] Review độc lập bằng database_review phát hiện rủi ro URL kế thừa; thêm test RED rồi sửa GREEN.
- [x] Thêm test RED/GREEN chặn CLI autogenerate khi metadata rỗng.
- [x] Cập nhật AGENTS.md, README, kiến trúc, hướng dẫn database và verification.

## Rulings

- Theo lựa chọn người dùng, dùng native PostgreSQL thay Docker; giữ Compose làm phương án thay thế với volume riêng.
- Dùng IPv4 127.0.0.1 tường minh cho kết nối local. Không thay cổng hoặc service hệ thống.
- Chưa tạo ORM mappings/auth. Giữ nguyên vai trò và hash placeholder trong SQL; sẽ xử lý trong tính năng tương ứng.
- Không tự sinh downgrade xóa schema; yêu cầu kế hoạch rollback có backup riêng.
