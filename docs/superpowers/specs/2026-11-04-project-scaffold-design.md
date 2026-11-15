# Thiết kế bộ khung Library Management System

## Mục tiêu và phạm vi

Tạo cấu trúc monorepo theo AGENTS.md để bắt đầu phát triển bằng React + TypeScript + Ant Design, FastAPI + SQLAlchemy và PostgreSQL. Bộ khung có cấu hình chạy tối thiểu, trang khởi động và API healthcheck. Chưa triển khai đăng nhập, CRUD hoặc nghiệp vụ mượn/trả.

## Phương án

Chọn monorepo với frontend và backend tách biệt như AGENTS.md đã quy định. Tách repository hoặc tạo hệ thống microservice sẽ làm thay đổi cấu trúc đã chọn và tăng công việc cấu hình không cần thiết ở giai đoạn này.

## Cấu trúc dự kiến

```text
frontend/
  src/
    app/ assets/ components/ hooks/ layouts/ routes/
    services/ stores/ types/ utils/
    features/
      auth/ dashboard/ books/ categories/ readers/
      borrowings/ reservations/ users/ reports/
  package.json
  tsconfig.json
  vite.config.ts
  .env.example
backend/
  app/
    api/v1/endpoints/
    core/ db/ models/ schemas/ repositories/ services/ dependencies/
    main.py
  alembic/versions/
  tests/
  alembic.ini
  pyproject.toml
  .env.example
docs/
docker-compose.yml
.env.example
.gitignore
README.md
```

Giữ nguyên AGENTS.md, các skill và báo cáo kiểm kê. Thư mục chưa có triển khai sẽ có file giữ chỗ khi cần.

## Cấu hình và hành vi tối thiểu

Cập nhật 05/11/2026 theo yêu cầu đổi cổng: backend dùng localhost:8001, API tại http://localhost:8001/api/v1 và Swagger tại http://localhost:8001/docs. Frontend vẫn dùng 5000, PostgreSQL host 5433.

- Frontend: Vite trên localhost:5000, strictPort=true; TypeScript strict; giao diện khởi động tiếng Việt bằng Ant Design. Khai báo React Router, Axios, TanStack Query và Zustand theo stack đã chọn; chưa tạo state nghiệp vụ không cần thiết.
- Axios đọc VITE_API_BASE_URL; TanStack Query provider và router được cấu hình ở cấp app.
- Backend: Python 3.12+, FastAPI, Pydantic Settings, SQLAlchemy 2.x, Psycopg 3; tách router/service/repository theo AGENTS.md. Healthcheck cơ bản tại /api/v1/health xác nhận tiến trình API, không khẳng định database đã sẵn sàng.
- SQLAlchemy dùng session đồng bộ và đóng session theo request. Alembic có cấu hình sẵn, chưa tạo bảng hoặc migration nghiệp vụ.
- PostgreSQL chạy bằng Docker Compose, ánh xạ 127.0.0.1:5433 sang 5432 trong container, có volume và healthcheck. Frontend/backend chạy trên máy phát triển.
- Biến môi trường có file mẫu; không lưu mật khẩu thật. CORS cho phép origin frontend đã quy định.
- README hướng dẫn tạo môi trường Python, cài dependency, khởi động database/API/frontend và xử lý xung đột cổng.

## Kiểm chứng dự kiến

Kiểm tra TypeScript và production build nếu cài được dependency; kiểm tra import ứng dụng, pytest cho healthcheck và OpenAPI; kiểm tra docker compose config nếu Docker khả dụng. Báo rõ NOT RUN khi môi trường thiếu công cụ. Không tự đổi cổng hoặc báo thành công cho kiểm tra chưa chạy.

## Trạng thái

Người dùng đã duyệt bằng yêu cầu “bắt đầu”. Bộ khung đã triển khai; xem kế hoạch và docs/verification.md để biết kết quả kiểm chứng và giới hạn môi trường.
