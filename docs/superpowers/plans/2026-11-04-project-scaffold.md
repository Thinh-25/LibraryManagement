# Project Scaffold Implementation Plan

> **For agentic workers:** Use superpowers:executing-plans to implement task-by-task.

**Goal:** Tạo bộ khung chạy tối thiểu theo thiết kế đã được người dùng duyệt bằng yêu cầu “bắt đầu”.
**Architecture:** Monorepo frontend/backend; frontend theo tính năng, backend theo lớp. PostgreSQL chạy Docker; ứng dụng chạy trên host.
**Tech Stack:** React, TypeScript, Ant Design, FastAPI, SQLAlchemy, PostgreSQL.
**Spec:** ../specs/2026-11-04-project-scaffold-design.md

## Global Constraints

- Giữ cổng frontend 5000 (localhost, strictPort), backend 8001 (cập nhật theo yêu cầu người dùng ngày 05/11/2026) và database host 5433.
- Chưa xây nghiệp vụ hoặc đăng nhập; không thay AGENTS.md hoặc các skill.
- Không khởi tạo Git/commit tự động; thư mục chưa có repository.
- Thực thi trực tiếp theo yêu cầu bắt đầu; không yêu cầu duyệt lại cùng phạm vi.

## Review Focus

- API healthcheck chạy khi database chưa kết nối, không báo database sẵn sàng.
- CORS chỉ cho origin frontend đã định, kiểm tra origin sai bị từ chối.
- Database URL lấy từ môi trường và không xuất mật khẩu ra API/log.
- Router hiển thị trang không tìm thấy khi đường dẫn không tồn tại.
- Docker dùng biến môi trường, host loopback và không tự đổi cổng.

## Task 1: Backend và cấu hình database

Files: backend/pyproject.toml, backend/tests/test_health.py, backend/app/{main.py,core/config.py,db/base.py,db/session.py,dependencies/database.py,schemas/health.py,api/v1/router.py,api/v1/endpoints/health.py}, backend/alembic.ini, backend/alembic/{env.py,script.py.mako}, docker-compose.yml, .env.example, backend/.env.example.

- [ ] Tạo môi trường Python và khai báo dependency.
- [ ] Viết rồi chạy test healthcheck, CORS và OpenAPI trước implementation.
- [ ] Tạo cấu hình Settings, SQLAlchemy session, router và Alembic; không tạo schema nghiệp vụ.
- [ ] Chạy pytest, compileall và Alembic offline.

Interface: GET /api/v1/health -> 200 {"status":"ok"}; database session dependency yield Session và đóng sau request; transaction thuộc service trong các tính năng sau.

## Task 2: Frontend tối thiểu

Files: frontend/package.json, frontend/tsconfig*.json, frontend/vite.config.ts, frontend/index.html, frontend/src/{main.tsx,app/App.tsx,app/providers.tsx,app/styles.css,routes/router.tsx,services/api.ts,services/health.ts,types/health.ts,features/dashboard/StartupPage.tsx}, frontend/.env.example.

- [ ] Tạo app provider, router, Axios và trang khởi động tiếng Việt.
- [ ] Trang hiển thị loading/error/success từ healthcheck, có nút thử lại.
- [ ] Tạo thư mục tính năng và shared theo thiết kế; khai báo Zustand nhưng chưa tạo store không có nhu cầu.
- [ ] Cài dependency, chạy TypeScript và production build.

## Task 3: Tài liệu và kiểm chứng

Files: README.md, .gitignore, docs/architecture.md.

- [ ] Viết hướng dẫn môi trường mẫu và lệnh chạy đúng cổng, lưu ý healthcheck chỉ kiểm tra API.
- [ ] Kiểm tra HTTP thực tế nếu có thể; Docker và browser ghi NOT RUN khi thiếu công cụ.
- [ ] Review độc lập toàn bộ bộ khung, khắc phục phát hiện quan trọng.
- [ ] Ghi kết quả kiểm chứng thực tế vào phần kết quả dưới đây.

## Kết quả

- Task 1: hoàn tất. RED: pytest lỗi thiếu app.main sau khi dependency đã cài. GREEN: 4 test qua; compileall, pip check và Alembic offline qua.
- Task 2: hoàn tất. TypeScript và production build qua. HTTP Vite tại localhost:5000 trả 200. Đã tạo frontend/.env từ mẫu (không có secret), không ghi đè file tồn tại.
- Task 3: hoàn tất tài liệu và review độc lập bằng agent scaffold_review; không có Critical/Important. Kiểm tra Docker runtime và browser chưa thực hiện do thiếu công cụ.
- Ruling: chưa có Git repository, thực hiện trong workspace hiện tại; không tạo worktree/commit hoặc chạy script ledger phụ thuộc Git.
- Ruling: không đổi cổng hoặc dừng tiến trình khác. Backend Uvicorn không bind được 8000 vì PID 20108 (python) đang sử dụng; phản hồi từ tiến trình đó nhận diện itms-backend, không dùng nó làm bằng chứng cho API mới.
- Final: minor (deferred): VITE_API_BASE_URL chưa được kiểm tra ở bước build; thiếu biến gây lỗi runtime rõ ràng. README yêu cầu tạo .env và workspace đã có bản sao mẫu.
- Final: minor (deferred): test healthcheck chưa chủ động xóa DATABASE_URL khỏi môi trường; lần test thực tế chạy khi chưa tạo backend/.env.
- Cảnh báo hiện tại: Vite bundle khoảng 882 kB trước gzip; Starlette cảnh báo deprecation khi dùng TestClient với httpx. Không tăng ngưỡng hoặc tắt cảnh báo.

Chi tiết bàn giao: ../../verification.md.
