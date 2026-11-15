# AGENTS.md — Library Management System

## 1. Project Overview

This project is a web-based Library Management System (LMS).

The system supports library operations including:

- Authentication and authorization
- Dashboard and statistics
- Book management
- Book category management
- Author and publisher management
- Physical book copy management
- Reader management
- Borrowing and returning books
- Book reservations
- User management
- Reports and statistics

The system has three primary roles:

- ADMIN: System administration and user management
- THU_THU: Library operations and inventory management
- DOC_GIA: Search books, view borrowing history, and make reservations

Do not implement additional business features unless explicitly requested.

---

## 2. Technology Stack

### Frontend

- React
- TypeScript
- Vite
- Ant Design
- React Router
- Axios
- TanStack Query
- Zustand

### Backend

- Python 3.12+
- FastAPI
- Uvicorn
- SQLAlchemy 2.x
- Alembic
- Pydantic v2
- Pydantic Settings
- Psycopg 3
- JWT Authentication
- Pytest

### Database

- PostgreSQL
- Docker Compose

### Development Tools

- Visual Studio Code
- OpenAI Codex
- Google Antigravity
- Git and GitHub
- Postman
- Swagger / OpenAPI

Do not change the technology stack without explicit approval.

---

## 3. Development Environment

The following ports are mandatory.

| Service    | Address                      |
| ---------- | ---------------------------- |
| Frontend   | http://localhost:5000        |
| Backend    | http://localhost:8001        |
| API        | http://localhost:8001/api/v1 |
| Swagger    | http://localhost:8001/docs   |
| PostgreSQL | localhost:5432               |

### Frontend

Vite must use:

- Host: localhost
- Port: 5000
- strictPort: true

### Backend

Run the backend with:

uvicorn app.main:app --reload --host 127.0.0.1 --port 8001

### Database

Use the existing PostgreSQL local server shown in pgAdmin, explicitly selected by the user on 2026-11-05.

- Active server: the machine's existing PostgreSQL service, not `.local/postgres`.
- Listen address: 127.0.0.1
- Port: 5432
- Database: library_management
- Application role: library_app; connection credentials are in backend/.env.
- Do not change the system PostgreSQL service or existing clusters.
- The previous project cluster and Docker alternative use 5433 and are not the active database. Do not run setup_local_database.py to configure the active server.

Do not automatically change ports when a port is occupied.

Report the conflict and suggest a solution.

---

## 4. Project Architecture

The project follows a monorepo structure.

```text
library-management-system/
├── AGENTS.md
├── .agents/
│   └── skills/
├── frontend/
├── backend/
├── docs/
├── docker-compose.yml
├── .env.example
├── .gitignore
└── README.md
```

### Frontend Architecture

Use a feature-based architecture.

```text
frontend/src/
├── app/
├── assets/
├── components/
├── features/
│   ├── auth/
│   ├── dashboard/
│   ├── books/
│   ├── categories/
│   ├── readers/
│   ├── borrowings/
│   ├── reservations/
│   ├── users/
│   └── reports/
├── hooks/
├── layouts/
├── routes/
├── services/
├── stores/
├── types/
└── utils/
```

### Backend Architecture

Follow the layered architecture:

API Router → Service → Repository → Database

```text
backend/
├── app/
│   ├── api/
│   │   └── v1/
│   │       └── endpoints/
│   ├── core/
│   ├── db/
│   ├── models/
│   ├── schemas/
│   ├── repositories/
│   ├── services/
│   ├── dependencies/
│   └── main.py
├── alembic/
├── tests/
├── .env.example
└── pyproject.toml
```

Respect the existing project structure.

Do not reorganize directories unless explicitly requested.

---

## 5. Mandatory AI Workflow

Before executing any user request, follow this workflow.

### Step 1: Read Project Instructions

Read this AGENTS.md file.

Understand:

- Project goals
- Technology stack
- Architecture
- Coding conventions
- Existing functionality
- Current development environment

If additional instructions exist in relevant subdirectories, read them.

### Step 2: Inspect the Existing Codebase

Before writing code:

- Inspect relevant files
- Understand existing implementations
- Identify dependencies
- Check reusable components
- Check existing APIs and database models

Never assume a file or feature exists without checking.

### Step 3: Discover Relevant Skills

Inspect available skills in:

.agents/skills/

For each task:

- Identify relevant skills
- Read the corresponding SKILL.md
- Follow the applicable instructions
- Avoid loading unrelated skills

Examples:

Frontend tasks:

- frontend-design
- react-typescript
- ui-ux-design

Backend tasks:

- fastapi-development
- api-design

Database tasks:

- postgresql
- database-design

Testing tasks:

- testing-debugging
- code-review

Planning tasks:

- software-planning

These names are examples, not guaranteed installed skills.

If a skill does not exist, continue using the project rules.

Do not claim a skill was loaded unless it was actually read.

### Step 4: Analyze the Request

Determine:

- What the user wants
- Which modules are affected
- Which files require changes
- Whether database changes are necessary
- Whether API changes are necessary
- Which tests should be executed

For complex tasks, provide a short implementation plan.

### Step 5: Implement

Follow the existing architecture.

Prefer:

- Small changes
- Reusable components
- Clear naming
- Type safety
- Maintainable code
- Minimal dependencies

Do not modify unrelated functionality.

### Step 6: Validate

After implementation:

- Check syntax
- Check TypeScript types
- Run relevant tests
- Check API contracts
- Check database migrations when applicable
- Review changed files

Never report PASS without executing the corresponding check.

### Step 7: Report Results

Respond in Vietnamese.

Include:

1. Summary of completed work
2. Files created or modified
3. Important implementation details
4. Tests performed and results
5. Remaining issues, if any

---

## 6. Frontend Development Rules

### React

- Use functional components.
- Use TypeScript for all application code.
- Prefer reusable components.
- Avoid unnecessary component complexity.
- Keep components focused on a single responsibility.
- Do not directly manipulate the DOM unless necessary.

### TypeScript

- Use strict typing.
- Avoid `any` whenever possible.
- Define interfaces or types for API responses.
- Validate external data when necessary.
- Avoid unsafe type assertions.

### UI

Use Ant Design as the primary UI component library.

Maintain consistent:

- Colors
- Typography
- Spacing
- Forms
- Tables
- Navigation
- Modals
- Notifications

Support responsive layouts where appropriate.

Use Vietnamese for user-facing interface text unless requested otherwise.

### State Management

- Use TanStack Query for server state.
- Use Zustand for appropriate client-side global state.
- Use local React state for component-specific state.
- Avoid unnecessary global state.

### API Integration

- Use Axios.
- Centralize API configuration.
- Use VITE_API_BASE_URL.
- Handle loading, error, and empty states.
- Do not hardcode API URLs in individual components.

---

## 7. Backend Development Rules

Use FastAPI and the existing layered architecture.

### API Router

Responsibilities:

- Define endpoints
- Receive requests
- Validate request schemas
- Apply authentication dependencies
- Return appropriate HTTP responses

Avoid placing complex business logic inside routers.

### Service Layer

Responsibilities:

- Implement business rules
- Coordinate repository operations
- Validate business conditions
- Manage workflows

### Repository Layer

Responsibilities:

- Database queries
- CRUD operations
- Data persistence

Avoid mixing HTTP logic into repositories.

### Schemas

Use Pydantic v2 for:

- Request validation
- Response validation
- Data serialization

Do not expose sensitive database fields.

### API Conventions

Use the prefix:

/api/v1

Use appropriate HTTP methods:

- GET: Read data
- POST: Create resources
- PUT/PATCH: Update resources
- DELETE: Delete resources

Use appropriate HTTP status codes.

Document APIs through FastAPI OpenAPI.

---

## 8. Database Rules

Use PostgreSQL with SQLAlchemy 2.x.

### Database Design

Follow relational database design principles.

Use:

- Primary keys
- Foreign keys
- Appropriate constraints
- Unique constraints where necessary
- Indexes for frequently queried columns
- Appropriate relationships

### Library Business Rules

Distinguish between:

- Book titles or editions
- Physical copies of books

A book title may have multiple physical copies.

Borrowing operations should reference physical copies when inventory tracking is required.

Do not assume that a book title represents one physical book.

### Migrations

Use Alembic for schema migrations.

Before changing the database:

1. Inspect existing models.
2. Inspect existing migrations.
3. Evaluate backward compatibility.
4. Create an appropriate migration.
5. Review migration operations.

Never automatically delete production data.

Do not drop tables or columns without explicit approval.

Avoid destructive migrations.

### Transactions

Use database transactions when operations must succeed or fail together.

Examples:

- Creating borrowing records
- Updating physical copy availability
- Processing returns
- Updating reservation status

---

## 9. Security Rules

Security is mandatory.

### Authentication

- Use secure password hashing.
- Never store plaintext passwords.
- Validate JWT tokens.
- Enforce token expiration.
- Implement role-based authorization.

### Authorization

Supported roles:

- ADMIN
- THU_THU
- DOC_GIA

Enforce authorization on the backend.

Do not rely only on frontend route protection.

### Environment Variables

Never hardcode:

- Database passwords
- JWT secrets
- API keys
- Private credentials

Use environment variables.

Do not commit .env files.

Maintain .env.example with placeholder values.

### Sensitive Information

Do not log:

- Passwords
- Access tokens
- Refresh tokens
- Private secrets

---

## 10. Code Modification Rules

Before modifying any file:

- Read the existing implementation.
- Understand its purpose.
- Identify related dependencies.

Do not:

- Delete unrelated code.
- Replace entire files unnecessarily.
- Change public interfaces without checking callers.
- Install unnecessary packages.
- Modify database schema without reviewing consequences.
- Change environment ports.
- Remove working functionality.

Prefer minimal and focused changes.

Preserve existing coding conventions.

If a change introduces breaking behavior, explain it before proceeding.

---

## 11. Testing and Debugging

### Frontend

When relevant:

- Run TypeScript checks.
- Run linting.
- Run available frontend tests.
- Check production builds.

### Backend

When relevant:

- Run Pytest.
- Validate API schemas.
- Test success and failure cases.
- Check authentication and authorization.
- Verify database interactions.

### Debugging

When encountering an error:

1. Read the complete error message.
2. Identify the root cause.
3. Inspect related files.
4. Propose the smallest reasonable fix.
5. Apply the fix.
6. Run relevant validation.
7. Report the result.

Do not hide errors.

Do not invent successful test results.

Use:

- PASS: Test executed successfully
- FAIL: Test executed and failed
- NOT RUN: Test not executed

---

## 12. Git and Version Control

Follow the existing Git workflow.

Before making changes:

- Check the current branch.
- Inspect relevant uncommitted changes.
- Avoid overwriting user modifications.

Do not automatically:

- Force push
- Delete branches
- Reset commits
- Discard uncommitted changes
- Merge pull requests
- Push code to remote repositories

These actions require explicit user approval.

Use meaningful commit messages.

Do not commit:

- .env files
- Secrets
- Credentials
- Generated temporary files

---

## 13. Communication and Final Rules

### Language

Always communicate with the user in Vietnamese.

Code identifiers may use English.

Technical explanations should be clear and concise.

### Before Implementation

For complex tasks, briefly explain:

- What will be changed
- Which files are involved
- Potential risks

### After Implementation

Report:

- Completed changes
- Modified files
- Validation results
- Remaining problems

### Mandatory Principles

1. Read AGENTS.md before working.
2. Inspect the existing codebase.
3. Read relevant available skills.
4. Follow the existing architecture.
5. Do not modify unrelated files.
6. Do not change the technology stack.
7. Do not change configured ports.
8. Protect existing user data.
9. Never claim tests passed without running them.
10. Respond in Vietnamese.

### Priority

When instructions conflict, follow this order:

1. System and platform safety requirements
2. Explicit user instructions
3. AGENTS.md project rules
4. Applicable SKILL.md instructions
5. Existing project conventions

If instructions conflict or are ambiguous, explain the conflict and ask for clarification when necessary.
