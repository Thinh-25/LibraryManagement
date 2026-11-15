# Book Cover Upload Implementation Plan

> **For agentic workers:** Use subagent-driven-development for independent frontend work and final review.

**Goal:** Chọn ảnh từ máy khi thêm/sửa sách, kiểm tra backend, xem trước và hiển thị ảnh.
**Architecture:** Multipart staff-only upload, generated local WebP paths, existing anh_bia column; reusable image form field.
**Tech Stack:** FastAPI/Pillow/python-multipart, React/Ant Design.
**Spec:** ../specs/2026-11-05-book-cover-upload-design.md; user approved “bắt đầu”.

## Constraints / contracts

- JPG/PNG/WebP <=5MiB; <=20million pixels; decode/re-encode static WebP with generated UUID filename, no supplied filesystem path.
- POST /api/v1/uploads/covers {file: multipart} ->201 {url:'/media/covers/<32hex>.webp'}; only ADMIN/THU_THU.
- GET /media/covers/{filename} public immutable file response only validated generated filename; 404 missing/invalid.
- Existing external HTTP(S) URLs remain valid. anh_bia also accepts exact local /media/covers/<32hex>.webp path; no traversal/arbitrary relative path.
- Store .local/uploads/covers by default, env COVER_UPLOAD_DIR override for tests. No schema migration.
- Cancel keeps original database value; no automatic deletion of old/orphan files. Save disabled during upload and on error until retry/remove.

## Tasks

- [x] Root: tests RED404 then storage/upload/media/schema implementation GREEN13upload tests.
- [x] Frontend agent: picker/preview/change/remove, generic image field and blocked Save, cover display; typecheck/build PASS.
- [x] Root: backend61tests, frontend5tests/build, Edge real file selection/create/edit/remove/cancel against isolated test DB PASS.
- [x] Independent review no blockers, README and verification updated.

## Review focus

- Forged content, decompression bombs, >5MiB input, unsafe file paths, no partial file on error.
- Auth upload and public media behavior, schema cannot link arbitrary local file.
- Rapid file selection/cancel and stale async upload, Save blocked until persisted upload URL available.
- Existing URL backward compatibility and correct backend origin for relative media paths.

## Ledger

No Git repository; no worktree/commit. Preserve all database records and active ports5000/8001/5432.

- Ruling: static images only, max20million input pixels and output longedge2400; preserve oldHTTP(S) URLs, no schema migration.
- Ruling: no deletion of old/orphan images, to protect other records; README explains separate backup/storage lifecycle.
- Final minor(deferred): mkdir/unlink storage failures may still surface500 instead of503; risk is less friendly error during storage permission failure.
- Final minor(deferred): multipart framework may spool requests before file-size check; public deployment should add upstream request limits, outside current local scope.
