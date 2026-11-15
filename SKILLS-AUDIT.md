# Rà soát skill — Library Management System

Ngày: 04/11/2026. Stack do người dùng cung cấp: React + TypeScript + Ant Design; FastAPI + SQLAlchemy; PostgreSQL. Cổng: frontend 5000, backend 8000, PostgreSQL 5433.

## Phạm vi và kết quả

- Trước khi dọn: 53 skill cài trong `.agents/skills`.
- Đã xóa 14 skill, giữ 39; đã đồng bộ `skills-lock.json`.
- Không chỉnh sửa mã nguồn và không xóa skill dùng chung của tài khoản hoặc plugin.
- Tại thời điểm rà soát, thư mục gốc chỉ có dữ liệu cấu hình/skill; chưa có mã nguồn để xác minh stack thực tế.

## Toàn bộ skill của dự án trước khi dọn

Mô tả dưới đây lấy trực tiếp từ SKILL.md để thể hiện chính xác điều kiện sử dụng của từng skill. Giữ = còn cài; Xóa = đã gỡ khỏi dự án.

| Skill | Kết quả | Khi sử dụng (mô tả gốc) |
|---|---|---|
| `ask-matt` | Giữ | Ask which skill or flow fits your situation. A router over the skills in this repo. |
| `brainstorming` | Giữ | "You MUST use this before any creative work - creating features, building components, adding functionality, modifying behavior, or planning anything new, in software or out of it (a talk, a business, a renovation)." |
| `chief-of-staff` | Xóa | Pursue a long-running goal in a single session by co-ordinating subagents. |
| `claude-handoff` | Xóa | Hand the current conversation off to a fresh background agent that picks up the work immediately. |
| `code-review` | Giữ | "Review the changes since a fixed point (commit, branch, tag, or merge-base) along two axes: Standards (does the code follow this repo's documented coding standards?) and Spec (does the code match what the originating issue/spec asked for?). Runs both reviews in parallel sub-agents and reports them side by side. Use when the user wants to review a branch, a PR, work-in-progress changes, or asks to \"review since X\"." |
| `codebase-design` | Giữ | Shared vocabulary for designing deep modules. Use when the user wants to design or improve a module's interface, find deepening opportunities, decide where a seam goes, make code more testable or AI-navigable, or when another skill needs the deep-module vocabulary. |
| `diagnosing-bugs` | Giữ | Diagnosis loop for hard bugs and performance regressions. Use when the user says "diagnose"/"debug this", or reports something broken/throwing/failing/slow. |
| `diagnosing-superpowers` | Xóa | Use when a superpowers session went wrong and your human partner wants to know why — repeated work, ignored plans, stumbles, poor results, a skill that didn't fire, "it took too long", "why is it so expensive", "what is it doing" — or wants to build a bug report for the superpowers maintainers, for the current session or a past one identified by id or path, on any harness. |
| `dispatching-parallel-agents` | Giữ | Use when facing 2+ independent tasks that can be worked on without shared state or sequential dependencies |
| `domain-modeling` | Giữ | Build and sharpen a project's domain model. Use when discussing codebase terminology, writing or editing a GLOSSARY.md, or recording or editing an ADR. |
| `executing-plans` | Giữ | Use when executing an implementation plan in the current session as the implementer yourself — your human partner chose inline execution, or no subagent tool is available |
| `finishing-a-development-branch` | Giữ | Use when implementation is complete, all tests pass, and you need to decide how to integrate the work |
| `git-guardrails-claude-code` | Xóa | Set up Claude Code hooks to block dangerous git commands (push, reset --hard, clean, branch -D, etc.) before they execute. Use when user wants to prevent destructive git operations, add git safety hooks, or block git push/reset in Claude Code. |
| `grill-me` | Giữ | A relentless interview to sharpen a plan or design. |
| `grill-with-docs` | Giữ | A relentless interview to sharpen a plan or design, which also creates docs (ADR's and glossary) as we go. |
| `grilling` | Giữ | Grill the user relentlessly about a plan, decision, or idea. Use when the user wants to stress-test their thinking, or uses any 'grill' trigger phrases. |
| `handoff` | Giữ | Compact the current conversation into a handoff document for another agent to pick up. |
| `implement` | Giữ | "Implement a piece of work based on a spec or set of tickets." |
| `implement-spec` | Giữ | "Implement the result of /to-spec and /to-tickets in code." |
| `improve-codebase-architecture` | Giữ | Scan a codebase for deepening opportunities, present them as a visual HTML report, then grill through whichever one you pick. |
| `loop-me` | Xóa | Grill me about specs for the workflows I want to build, within this workspace. |
| `migrate-to-shoehorn` | Xóa | Migrate test files from `as` type assertions to @total-typescript/shoehorn. Use when user mentions shoehorn, wants to replace `as` in tests, or needs partial test data. |
| `pr` | Giữ | "Use when writing a PR body." |
| `prototype` | Giữ | Build a throwaway prototype to answer a design question. Use when the user wants to sanity-check whether a state model or logic feels right, or explore what a UI should look like. |
| `receiving-code-review` | Giữ | Use when receiving code review feedback, before implementing suggestions, especially if feedback seems unclear or technically questionable - requires technical rigor and verification, not performative agreement or blind implementation |
| `requesting-code-review` | Giữ | Use when completing tasks, implementing major features, or before merging to verify work meets requirements |
| `research` | Giữ | Investigate a question against high-trust primary sources and capture the findings as a Markdown file in the repo. Use when the user wants a topic researched, docs or API facts gathered, or reading legwork delegated to a background agent. |
| `retro` | Xóa | "Conduct a retrospective on a coding session." |
| `scaffold-exercises` | Xóa | Create exercise directory structures with sections, problems, solutions, and explainers that pass linting. Use when user wants to scaffold exercises, create exercise stubs, or set up a new course section. |
| `setup-matt-pocock-skills` | Giữ | "Configure this repo for the engineering skills: set up its issue tracker, triage label vocabulary, and domain doc layout. Run once before first use of the other engineering skills." |
| `setup-pre-commit` | Giữ | Set up Husky pre-commit hooks with lint-staged (Prettier), type checking, and tests in the current repo. Use when user wants to add pre-commit hooks, set up Husky, configure lint-staged, or add commit-time formatting/typechecking/testing. |
| `setup-ts-deep-modules` | Giữ | Wire dependency-cruiser into a TypeScript repo so each package is a deep module, with implementation hidden in subfolders and reachable only through its entry-point files. User-invoked. |
| `subagent-driven-development` | Giữ | Use when executing implementation plans with independent tasks in the current session |
| `systematic-debugging` | Giữ | Use when encountering any bug, test failure, or unexpected behavior, before proposing fixes |
| `tdd` | Giữ | Test-driven development. Use when the user wants to build features or fix bugs test-first, mentions "red-green-refactor", or wants integration tests. |
| `teach` | Xóa | Teach the user a new skill or concept, within this workspace. |
| `test-driven-development` | Giữ | Use when implementing any feature or bugfix, before writing implementation code |
| `to-questionnaire` | Xóa | Turn a decision you can't fully answer into a questionnaire for someone else to fill in. |
| `to-spec` | Giữ | "Turn the current conversation into a spec and publish it to the project issue tracker: no interview, just synthesis of what you've already discussed." |
| `to-tickets` | Giữ | Break a plan, spec, or the current conversation into a set of tracer-bullet tickets, each declaring its blocking edges, published to the configured tracker (edges as text in one file per ticket locally, or native blocking links on a real tracker). |
| `triage` | Giữ | Move issues and external PRs through a state machine of triage roles, categorise, verify, grill if needed, and write agent-ready briefs. |
| `using-git-worktrees` | Giữ | Use when starting feature work that needs isolation from current workspace or before executing implementation plans - ensures an isolated workspace exists via native tools or git worktree fallback |
| `using-superpowers` | Giữ | Use when starting any conversation - establishes how to find and use skills, requiring skill invocation before ANY response including clarifying questions |
| `verification-before-completion` | Giữ | Use when about to claim work is complete, fixed, or passing, before committing or creating PRs - requires running verification commands and confirming output before making any success claims; evidence before assertions always |
| `wait-what` | Xóa | "Stop. That last message did not land: re-pitch it." |
| `wayfinder` | Giữ | Plan a huge chunk of work (more than one agent session can hold) as a shared map of decision tickets on your issue tracker, and resolve them one at a time until the way to the destination is clear. |
| `wizard` | Giữ | Generate an interactive bash wizard that walks a human through steps only they can perform. Use when provisioning infrastructure, setting up credentials or CI secrets, walking an unfamiliar third-party dashboard, or running a one-off migration or cutover. Don't invoke this for steps the agent can perform itself. |
| `writing-beats` | Xóa | Writing, exploit; assemble raw material into a journey of beats, grounding each term before a beat leans on it. |
| `writing-for-agents` | Giữ | Writing documents for agents. Use when creating or editing skills, or modifying AGENTS.md or CLAUDE.md. |
| `writing-fragments` | Xóa | "Writing, explore: mine raw fragments, no structure yet." |
| `writing-plans` | Giữ | Use when you have a spec or requirements for a multi-step task, before touching code |
| `writing-shape` | Xóa | "Writing, exploit: shape raw material into an article, paragraph by paragraph." |
| `writing-skills` | Giữ | Use when creating new skills, editing existing skills, or verifying skills work before deployment |
## Skill dùng chung và plugin có trong phiên

Các skill này nằm ngoài thư mục dự án. Bảng sau bổ sung những tên chưa nằm trong bảng 53 skill ở trên; không xóa chúng vì có thể được dự án khác sử dụng.

| Skill | Khi sử dụng / mức phù hợp |
|---|---|
| `using-agent-skills` | Chọn quy trình phù hợp cho từng công việc. |
| `api-and-interface-design` | Thiết kế API FastAPI và hợp đồng dữ liệu frontend/backend. |
| `frontend-ui-engineering` | Xây giao diện React, responsive và accessibility. |
| `ui-ux-pro-max` | Rà soát bố cục, tương tác, màu sắc, typography. |
| `ui-styling` | Styling giao diện; phần shadcn/Tailwind chỉ dùng nếu dự án thực sự chọn chúng. Với dự án này ưu tiên Ant Design. |
| `design-system` | Token và quy chuẩn component; có thể bổ trợ theme Ant Design. |
| `browser-testing-with-devtools` | Kiểm chứng giao diện chạy thực tế; cần Chrome DevTools MCP được cấu hình. |
| `security-and-hardening` | Xử lý đầu vào, đăng nhập, phân quyền, dữ liệu cá nhân và tích hợp. |
| `performance-optimization` | Đo và tối ưu frontend, API, truy vấn database. |
| `observability-and-instrumentation` | Logging, metrics, tracing và cảnh báo. |
| `ci-cd-and-automation` | Thiết lập pipeline build, test, deploy. |
| `shipping-and-launch` | Chuẩn bị phát hành, theo dõi và rollback. |
| `deprecation-and-migration` | Thay đổi schema/API và ngừng chức năng cũ. |
| `documentation-and-adrs` | Ghi quyết định kiến trúc, tài liệu chức năng/API. |
| `code-review-and-quality` | Review chất lượng và rủi ro trước khi merge. |
| `code-simplification` | Refactor giảm độ phức tạp, giữ nguyên hành vi. |
| `debugging-and-error-recovery` | Tìm nguyên nhân lỗi, tương tự nhóm debugging đang cài trong dự án. |
| `git-workflow-and-versioning` | Quản lý branch, commit, PR, release. |
| `constraint-driven-development` | Ghi rõ và kiểm soát ngưỡng chất lượng. |
| `context-engineering` | Cấu hình ngữ cảnh và quy tắc cho agent. |
| `doubt-driven-development` | Phản biện quyết định quan trọng hoặc có rủi ro cao. |
| `source-driven-development` | Đối chiếu tài liệu chính thức trước khi chọn cách triển khai. |
| `incremental-implementation` | Chia thay đổi thành các lát nhỏ có thể kiểm chứng. |
| `planning-and-task-breakdown` | Chia yêu cầu thành nhiệm vụ có thứ tự và phụ thuộc. |
| `spec-driven-development` | Viết đặc tả và tiêu chí chấp nhận trước khi xây tính năng. |
| `interview-me` | Làm rõ mục tiêu khi yêu cầu chưa đủ cụ thể. |
| `idea-refine` | Phát triển và sàng lọc ý tưởng còn sơ khai. |
| `find-skills` | Tìm skill bổ sung; không có gói bên ngoài nào được cài trong lần rà soát này. |
| `skill-installer` | Cài skill từ bộ tuyển chọn hoặc repository khi có yêu cầu. |
| `skill-creator` | Soạn hoặc cập nhật skill nội bộ cho dự án. |
| `openai-docs` | Tra cứu sản phẩm/API OpenAI; chỉ liên quan nếu dự án tích hợp OpenAI. |
| `imagegen` | Tạo/sửa ảnh bitmap; chỉ cần khi có yêu cầu tài sản hình ảnh. |
| `banner-design` | Thiết kế banner quảng bá; ngoài phạm vi phát triển nghiệp vụ thư viện hiện tại. |
| `brand` | Giọng điệu, nhận diện và tính nhất quán thương hiệu. |
| `design` | Thiết kế logo, ấn phẩm, tài sản hình ảnh hoặc trình bày. |
| `slides` | Tạo bài trình bày HTML. |
| `plugin-management:plugin-management` | Quản lý hoặc kết nối plugin/dịch vụ bên ngoài. |
| `sites:sites` | Xây, sửa hoặc xuất bản website qua Sites; không cần chuyển dự án FastAPI sang Sites. |
| `sites:sites-remix` | Tạo bản remix từ website Sites đã xác định. |
| `work-pets:create-pet` | Tạo pet hoạt hình trong ChatGPT Work; không liên quan dự án. |
| `work-pets:pets` | Quản lý pet trong ChatGPT Work; không liên quan dự án. |
| `work-pets:update-pet` | Sửa pet trong ChatGPT Work; không liên quan dự án. |

Tên `test-driven-development` xuất hiện ở cả cấp dự án và cấp tài khoản: cùng tên nhưng là hai nguồn hướng dẫn. Các nhóm lập kế hoạch, debugging, review và TDD cũng có phần giao nhau. Không xóa chỉ vì tên gần nghĩa: một số skill đang dẫn chiếu lẫn nhau.

## Lý do xóa 14 skill

| Skill | Lý do |
|---|---|
| `chief-of-staff` | Điều phối mục tiêu dài hạn bằng nhiều agent; chưa cần cho quy trình hiện tại. |
| `claude-handoff` | Chuyển phiên sang background agent theo workflow riêng. |
| `git-guardrails-claude-code` | Hook dành riêng cho Claude Code. |
| `scaffold-exercises` | Tạo bài tập khóa học. |
| `teach` | Quản lý workspace dạy học nhiều phiên. |
| `loop-me` | Phỏng vấn đặc tả workflow, không trực tiếp phục vụ nghiệp vụ thư viện. |
| `writing-beats` | Biên tập bài viết theo nhịp nội dung. |
| `writing-fragments` | Thu thập ý tưởng cho bài viết. |
| `writing-shape` | Dựng cấu trúc bài viết. |
| `wait-what` | Lệnh yêu cầu diễn đạt lại; có thể yêu cầu trực tiếp trong chat. |
| `to-questionnaire` | Soạn bảng hỏi gửi người khác. |
| `migrate-to-shoehorn` | Chuyển test sang thư viện shoehorn; chưa có yêu cầu dùng thư viện này. |
| `diagnosing-superpowers` | Điều tra lỗi của chính hệ thống Superpowers. |
| `retro` | Tổng kết phiên làm việc; chưa cần cho quy trình dự án. |

## Skill chuyên biệt còn thiếu — đề xuất nội dung nội bộ

Đây là các phạm vi skill đề xuất, chưa phải tên gói đã được tìm kiếm hoặc xác minh trên marketplace; chưa cài hay tạo thêm.

| Tên đề xuất | Khi cần / nội dung nên có | Ưu tiên |
|---|---|---|
| `react-typescript-ant-design` | Form, Table, pagination, filter, loading/error, theme, accessibility và chuẩn TypeScript theo Ant Design. | Cao |
| `fastapi-sqlalchemy` | Dependency/session lifecycle, Pydantic schema, transaction, exception mapping, async/sync nhất quán và phân trang. | Cao |
| `postgresql-alembic` | Migration, khóa ngoại, unique/check constraints, index, EXPLAIN và rollback. | Cao |
| `library-domain-rules` | Phân biệt đầu sách/bản sao, trạng thái sách, mượn/trả/gia hạn/đặt trước, hạn trả và quy tắc xử lý đồng thời. | Cao |
| `library-auth-rbac` | Quyền quản trị/thủ thư/độc giả, kiểm tra quyền sở hữu dữ liệu, token/session và kiểm thử phân quyền. | Cao |
| `fullstack-testing` | pytest cho API/database, Vitest + React Testing Library cho UI, Playwright cho luồng mượn/trả. | Cao |
| `local-dev-environment` | Frontend 5000, API 8000, PostgreSQL host 5433; biến môi trường, CORS, proxy, healthcheck và seed dữ liệu. Khi dùng container cần phân biệt cổng host và container. | Vừa |
| `openapi-typescript-contract` | Đồng bộ hợp đồng OpenAPI với TypeScript, thống nhất lỗi và kiểm tra breaking changes. | Vừa |

Ưu tiên tận dụng skill dùng chung đang có cho security, performance, CI/CD và giao diện; chỉ bổ sung kiến thức đặc thù stack/nghiệp vụ để tránh tạo thêm nhiều skill trùng chức năng.
