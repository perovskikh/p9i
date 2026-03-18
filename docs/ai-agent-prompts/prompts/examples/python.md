# Example: Python Web Application Adaptation

## Scenario

**Input:** A Python FastAPI project with PostgreSQL

**Project Structure:**
```
my-project/
├── app/
│   ├── __init__.py
│   ├── main.py          # FastAPI app
│   ├── api/
│   │   ├── __init__.py
│   │   └── v1/
│   │       └── endpoints/
│   ├── models/
│   │   └── user.py
│   └── services/
│       └── user_service.py
├── tests/
│   └── test_api/
├── requirements.txt
├── pyproject.toml
└── .env.example
```

---

## Running the Adapter

```bash
claude "Using prompts/universal-adapter.md, analyze this Python FastAPI project"
```

Or with config:

```yaml
# project-config.yaml
project:
  name: "My FastAPI App"
  type: "web-app"
  description: "REST API with authentication"

stack:
  language: "python"
  framework: "fastapi"
  database: "postgresql"
```

---

## Generated Output

### ANALYSIS-MyFastAPIApp.md

```markdown
# Project Analysis: My FastAPI App

## Overview

REST API application built with FastAPI, providing user authentication
and CRUD operations with PostgreSQL backend.

## Technology Stack

| Component | Technology | Version | Notes |
|-----------|-----------|---------|-------|
| Language | Python | 3.11 | From pyproject.toml |
| Framework | FastAPI | 0.109.0 | From requirements.txt |
| Database | PostgreSQL | 14+ | Async with asyncpg |
| ORM | SQLAlchemy | 2.0 | Async support |
| Auth | JWT | - | python-jose |
| Testing | pytest | 7.4 | pytest-asyncio |

## Architecture

```
User Request
    ↓
FastAPI (app/main.py)
    ↓
API Router (app/api/v1/)
    ↓
Service Layer (app/services/)
    ↓
SQLAlchemy Models (app/models/)
    ↓
PostgreSQL Database
```

## Key Components

| Component | Path | Purpose |
|-----------|------|---------|
| App Entry | `app/main.py` | FastAPI application factory |
| API Routes | `app/api/v1/` | REST endpoints |
| Models | `app/models/` | SQLAlchemy ORM models |
| Services | `app/services/` | Business logic |
| Auth | `app/security/` | JWT handling |

## Development Setup

### Prerequisites
- Python 3.11+
- PostgreSQL 14+
- Redis (optional, for caching)

### Installation
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Copy environment
cp .env.example .env
# Edit .env with your settings
```

### Running Locally
```bash
# Development server with hot reload
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Or with alembic for migrations
alembic upgrade head
```

### Testing
```bash
# Run all tests
pytest -v

# With coverage
pytest --cov=app --cov-report=html
```

### API Documentation
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Key Files to Understand

1. **`app/main.py`** — Application setup, middleware, CORS
2. **`app/api/v1/endpoints/users.py`** — User CRUD endpoints
3. **`app/models/user.py`** — User model definition
4. **`app/services/user_service.py`** — Business logic
5. **`tests/test_api/test_users.py`** — API tests

## Common Gotchas

- **Auth:** JWT tokens expire in 60 minutes (configurable in settings)
- **Database:** Async sessions require explicit commit/close
- **Migrations:** Always run `alembic upgrade head` after pulling changes
- **Env Vars:** `.env` is not committed; copy from `.env.example`

## Risks & Gaps

| Issue | Severity | Recommendation |
|-------|----------|----------------|
| No integration tests | Medium | Add tests for API endpoints |
| Missing rate limiting | Medium | Add slowapi for production |
| No API versioning strategy | Low | Consider /v1/, /v2/ structure |

## Next Steps (First Session)

1. **Setup:** Run `pip install -r requirements.txt` and configure `.env`
2. **Database:** Run `alembic upgrade head` to create tables
3. **Verify:** Start server with `uvicorn app.main:app --reload`
4. **Test:** Visit http://localhost:8000/docs and try the API
5. **Explore:** Read `app/api/v1/endpoints/users.py` for endpoint patterns
```

---

## Key Insights from This Example

### What the Adapter Detected

1. **Language:** Python (from `pyproject.toml`, `requirements.txt`)
2. **Framework:** FastAPI (from imports in `app/main.py`)
3. **Architecture:** Layered (API → Service → Model)
4. **Database:** PostgreSQL with SQLAlchemy ORM
5. **Testing:** pytest

### What It Created

1. **Technology matrix** — All dependencies with versions
2. **Architecture diagram** — Request flow visualization
3. **Setup instructions** — Copy-paste commands
4. **Key files mapping** — What each important file does
5. **Gotchas** — Project-specific pitfalls
6. **Action plan** — 5 concrete steps to get started

---

## Follow-up Questions

After running the adapter, you can ask:

> "How does authentication work in this project?"

> "What are the database migration commands?"

> "Show me an example of how to add a new endpoint"

---

**See also:**
- [Node.js Example](nodejs.md)
- [Go Example](go.md)
- [Clean Project Example](clean-project.md)
