# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

**Package manager:** `uv` (not pip)

```bash
# Development server
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Docker (preferred for local dev — starts PostgreSQL + backend)
docker-compose up

# Tests
uv run pytest
uv run pytest tests/test_health.py        # single file
uv run pytest -v -k "test_name"           # single test

# Database migrations
alembic upgrade head
alembic revision --autogenerate -m "description"
alembic downgrade -1

# Linting & formatting
uv run ruff check .
uv run black .
uv run mypy .
```

## Architecture

**Pattern:** Modular clean architecture — each feature is a self-contained module under `app/modules/`.

**Request flow:**
```
routes.py → dependencies.py → service.py → repository.py → SQLAlchemy ORM → PostgreSQL
```

Each module (`auth`, `users`, `health`, `bookings`) follows this structure:
- `routes.py` — FastAPI router with endpoint definitions
- `service.py` — Business logic (no DB calls directly)
- `repository.py` — All database access (async SQLAlchemy sessions)
- `schemas.py` — Pydantic request/response models
- `dependencies.py` — FastAPI `Depends()` factories for the module
- `exceptions.py` — Module-specific exception types (optional)

**Core infrastructure** (`app/core/`):
- `config.py` — Pydantic Settings; all env vars go here
- `security.py` — JWT creation/verification + password hashing
- `exceptions.py` — Base exception hierarchy mapped to HTTP status codes
- `error_handlers.py` — Registers exception → HTTP response handlers on the app
- `logging.py` / `logging_context.py` — JSON-structured logging with `request_id` ContextVar
- `middleware/request_logging.py` — Logs all requests/responses; masks sensitive fields
- `timings.py` — SQL query timing instrumentation

**Infrastructure** (`app/infra/`):
- `db/session.py` — Async SQLAlchemy session factory
- `db/base.py` — Declarative base (import all models here for Alembic autogenerate)
- `db/models/` — ORM models; use UUID PKs and `created_at`/`updated_at` timestamps
- `redis/`, `celery/` — Scaffolded but not yet integrated

## Key Conventions

**Dependency injection:** Database sessions and shared services are injected via `app/core/dependencies.py`. Module-specific DI goes in the module's own `dependencies.py`.

**Auth guards:** Use `require_active_user` or `require_superuser` from `app/modules/auth/dependencies.py` as FastAPI dependencies on protected routes.

**Exceptions:** Raise custom exceptions from `app/core/exceptions.py` (or module-level ones); the error handlers translate them to HTTP responses automatically. Do not raise `HTTPException` directly in services or repositories.

**Async everywhere:** All DB operations use `AsyncSession` with `await`. Alembic migrations run synchronously via psycopg (see `alembic/env.py`).

**Environment variables:** Defined in `.env.example`. Required vars: `DB_HOST`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `SECRET_KEY`.