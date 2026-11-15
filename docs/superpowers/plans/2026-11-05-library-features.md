# Library Features Implementation Plan

> **For agentic workers:** Use subagent-driven-development; independent ownership, tests and final review.

**Goal:** Implement all UC01–UC12 from approved DOCX design, not placeholders.
**Architecture:** Existing React/Ant Design frontend and FastAPI router/service/repository backend. PostgreSQL5432 preserved; migrations additive. No Git repository exists; no commits/worktrees.
**Tech Stack:** React, TypeScript, Ant Design, FastAPI, SQLAlchemy2, PostgreSQL, JWT/Argon2.
**Spec:** ../specs/2026-11-05-library-features-design.md (approved by user: “bắt đầi”).

## Global Constraints

- Frontend5000 strictPort, backend8001, PostgreSQL5432. Do not touch unrelated DBs/services.
- Database/API field names follow supplied Vietnamese SQL. Roles ADMIN/THU_THU/DOC_GIA.
- Lists return {items,total,page,page_size}; page_size<=100. Errors {detail: string}.
- Auth Authorization Bearer; token in client memory only. Password recovery handled by Admin.
- No mass assignment, destructive migrations, shared demo password or real-DB truncation.
- Test on dedicated library_management_test DB; application users/schema preserved.

## Review Focus

- Cross-role and cross-reader data leakage, disabled/versioned/forced-change tokens.
- Concurrent checkout/return/payment and rollback of partial multi-copy checkout.
- Reference-aware deletion, no manual BORROWED state bypass.
- FIFO reservations including expiry and checkout completion, manual positive fines.
- Vietnam timezone date boundaries and Decimal money; no fake reports.

## Task 1 — Models, migration, authentication/accounts (auth agent)

Own models/entities.py, models/__init__.py, migration0002, core/security.py, dependencies/auth.py, schemas/auth.py, repositories/accounts.py, services/accounts.py, endpoints/auth.py and users.py, scripts/bootstrap_admin.py, tests/test_auth*.py. May edit pyproject/config for auth dependencies. Must provide models early.

Models use class names User, LibraryCard, Category, Author, Publisher, Book, BookAuthor, BookCopy, Borrowing, LoanItem, Reservation, Fine, PasswordResetRequest with Vietnamese column attribute names. Added User.auth_version, User.must_change_password. No relationships required; do not auto-create/drop tables.

Auth endpoints: POST /auth/login {email,password}->{access_token,token_type,user}; GET/PATCH /auth/me; POST /auth/change-password {current_password,new_password}; POST /auth/logout; POST /auth/forgot-password {email}. Users endpoints staff/admin access as spec: GET/POST /users, GET/PATCH /users/{id}; POST /users/{id}/reset-password {new_password}; GET /password-reset-requests; POST /password-reset-requests/{id}/resolve {new_password?,reject:false}. Reset changes force password change and invalidate tokens.

Dependency require_roles(*roles) returns FastAPI callable with authenticated User; get_current_user checks active/version and must_change_password except me/change-password/logout. Signup not offered. Schemas input extra=forbid. Bootstrap prompts hidden password, never seeds known secret.

- [ ] Tests RED, implement, tests GREEN including role/ownership/token revocation/reset.
- [ ] Additive migration on test DB then review.

## Task 2 — Catalog/readers/cards (catalog agent)

Own schemas/catalog.py, repositories/catalog.py, services/catalog.py, endpoints/catalog.py, tests/test_catalog.py. Models/dependencies from task1; no shared file edits.

GET /books?search&category_id&author_id&publisher_id -> paginated book objects id,isbn,ten_sach,the_loai_id,nha_xuat_ban_id,nam_xuat_ban,mo_ta,anh_bia,authors:[{id,ho_ten}],available_copies,total_copies,category_name,publisher_name. GET /books/{id} adds copies list. POST/PATCH body: SQL field names plus author_ids:number[]. DELETE /books/{id}. POST /books/{id}/copies {ma_vach,vi_tri_ke?,tinh_trang?}; PATCH/DELETE /copies/{id}. GET/POST/PATCH/DELETE /categories,/authors,/publishers (item id path for patch/delete); fields match SQL. GET /readers?search, GET /readers/{id} -> user fields + card; POST /readers/{id}/card {ma_the,ngay_cap,ngay_het_han}; PATCH /cards/{id} {ngay_het_han?,trang_thai?}. Reader history via GET /borrowings?reader_id=.

- [ ] Tests RED then CRUD/filter/ref-integrity/card validation GREEN.

## Task 3 — Frontend full UI (frontend agent)

Own frontend/src and frontend package if needed. Real API all12, no fake data. Auth memory store and Axios auth, 401 clear session. Reader landing /books, staff /dashboard. Restricted forced-password-change route. Dynamic reusable typed CRUD forms allowed but no any. Inputs/outputs per contracts here and task1/2/4. Implement all menus/pages and meaningful actions, loading/errors/empty, filters/pagination/details. Query invalidation only after success. README auth note later root.

- [ ] TypeScript and production build; add frontend tests where meaningful.

## Task 4 — Borrowing/return/reservation/fines/reports (root)

Own repositories/circulation.py, services/circulation.py, schemas/circulation.py, endpoints/circulation.py, tests/test_circulation.py. Common errors/repository utilities owned root. Integration router/main/test fixtures root.

GET /borrowings?reader_id -> paginated id,doc_gia_id,thu_thu_id,doc_gia_name,thu_thu_name,ngay_muon,ghi_chu,items[]. GET /borrowings/{id}; POST /borrowings {doc_gia_id,ghi_chu?,items:[{cuon_sach_id,han_tra}],reservation_id?}. Item id,cuon_sach_id,ten_sach,ma_vach,han_tra,ngay_tra,trang_thai,tinh_trang_khi_tra. POST /loan-items/{id}/return {condition:GOOD|DAMAGED|LOST,note?,fine_amount?,fine_reason?}. GET /my-borrowings?status=borrowed|overdue|history.

GET /reservations staff, /my-reservations reader -> paginated id,doc_gia_id,sach_id,doc_gia_name,ten_sach,ngay_dat,ngay_het_han,trang_thai. POST /reservations reader {sach_id}; POST /reservations/{id}/cancel (owner reader or staff); POST /reservations/{id}/ready staff. Completed only during POST borrowing reservation_id. FIFO active oldest; expiry cancels READY; hold48h config.

GET /fines staff, /my-fines reader -> id,chi_tiet_muon_id,doc_gia_name,ten_sach,ly_do,so_tien,trang_thai,ngay_tao,ngay_thanh_toan. POST /fines staff {chi_tiet_muon_id,ly_do,so_tien}; POST /fines/{id}/pay. GET /reports?start_date&end_date -> {summary:{books,copies,readers,active_readers,borrowed,overdue,paid_fines,unpaid_fines},monthly:[{month,count}],popular:[{id,ten_sach,count}]}.

- [ ] Integration tests RED/GREEN for permissions, atomic checkout, double return/payment, FIFO/expiry, personal scope and reports.

## Task 5 — Integration, migration, verification and review (root + reviewer)

- [ ] Configure isolated PostgreSQL test DB and fixtures, tests use TEST_DATABASE_URL only and refuse application DB.
- [ ] Wire routers + BusinessError and IntegrityError handlers (generic409, rollback dependency).
- [ ] Run backend suite, typecheck/build, check migrations on test DB, back up application DB then apply additive migration.
- [ ] Bootstrap command/documentation; never set shared/default credentials.
- [ ] HTTP/browser checks if tools available; final independent review and fix important findings with regression tests.

## Execution ledger

- Approved scope: all12 use cases, Admin recovery, manual fines, FIFO48h, memory token. No additional permission needed for reversible implementation.
- Ruling: use isolated test DB; no Git actions because project has no .git.
- Task1 complete: auth/account10tests, full13model metadata mapped; independent review fixed null/numeric email validation regression; final suite includes coverage.
- Task2 complete: catalog8tests; metadata GET allowed all roles for reader filters, mutation staff-only.
- Task3 complete: all feature pages, Node3tests/typecheck/build PASS; real Edge role navigation and checkout/return UI PASS on isolated DB.
- Task4 complete: circulation, reports and real PostgreSQLconcurrency tests; expiry/COMPLETED regression RED→GREEN using atomic guarded UPDATE. Report date bounds and timezone/Decimal assertions verified.
- Task5 complete: backend48tests PASS, frontend3tests PASS, metadata zero differences, compileall/pipcheck. Independent review Critical0; Important email-type validation fixed RED→GREEN. Other important race from earlier review fixed with real concurrency test.
- Application migration0002 applied only after backup .local/library-before-features-20261105-225133.backup; all35prior rows preserved. No seed password auto-initialization.
- Ruling: report date years limited1900–2200 to avoid overflow and maintain coherent supported range; out-of-range422.
- Ruling: keep auth token memory-only/reload-login and logout-all versions as approved; password recovery Admin-handled, no mail integration.
- Final: minor(deferred): book selection metadata options lack separate fetch-error UI; main requests/mutations still show errors. Cost: troubleshooting an options failure requires retrying page.
- Final: minor(deferred): large AntDesign vendor chunk warning; routes lazy loaded. Cost: initial download performance, not functionality.
