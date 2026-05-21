---
name: fastapi-api
description: FastAPI API best practices. Use whenever the user mentions FastAPI, wants to build a REST API with Python, create FastAPI endpoints, routers, middleware, project structure, Pydantic schemas, dependency injection, error handling, API tests, configuration, or FastAPI with SQLModel / SQLAlchemy. Applies to new projects and refactoring existing FastAPI API code.
---

# FastAPI API Best Practices

Use this skill for production-grade FastAPI API work: app structure, routers, schemas, dependencies, database access, error handling, tests, migrations, and tooling. This skill is API-layer only: do
not introduce templates, Jinja2, SSR, or static-file frontend patterns unless the user explicitly asks.

## Default workflow

1. Inspect the existing project before adding patterns. Preserve established conventions unless they conflict with a gotcha below or the user asked for a refactor.
2. If the task needs implementation details, read `references/api-guide.md` for the relevant section instead of relying on memory.
3. Organize new code by domain/bounded context, not by file type.
4. Start every route/dependency design by deciding whether the code is async-safe or blocking.
5. Keep schemas, database models, services, and route dependencies explicit; avoid magic imports and catch-all helpers.
6. Add or update tests using `httpx.AsyncClient` with `ASGITransport` for API tests.
7. Run the project’s existing validation commands. If none exist, prefer `uv run ruff check`, `uv run ruff format --check`, and the project’s pytest command.

## Compatibility baseline

Prefer these defaults for new code unless the project pins something else:

| Area | Default |
| --- | --- |
| Python | 3.11+ |
| FastAPI | 0.115+ |
| Pydantic | v2; `pydantic-settings` for `BaseSettings` |
| Database | SQLAlchemy 2.0 async APIs; SQLModel when the project already uses it |
| PostgreSQL driver | `psycopg` v3, never `psycopg2` for async apps |
| HTTP tests | `httpx.AsyncClient` + `ASGITransport` |
| JWT | PyJWT (`import jwt`), not `python-jose` |
| Tooling | Prefer existing project tools; for new projects use `uv`, `ruff`, and the configured type checker |

## Project structure default

Organize by domain:

```text
app/
├── {domain}/
│   ├── router.py
│   ├── schemas.py
│   ├── models.py
│   ├── service.py
│   ├── dependencies.py
│   ├── config.py
│   ├── constants.py
│   ├── exceptions.py
│   └── utils.py
├── config.py
├── database.py
├── exceptions.py
└── main.py
```

Use explicit cross-domain imports:

```python
from app.auth import constants as auth_constants
from app.posts.constants import ErrorCode as PostsErrorCode
```

## Core defaults

- Use `Annotated[T, Depends(...)]` for dependency injection.
- Use dependencies to load and validate database-backed route inputs once per request.
- Separate request, response, and ORM/database models. Never expose internal ORM fields accidentally.
- Use domain exceptions in business logic and FastAPI exception handlers at the API boundary.
- Use the lifespan context manager for startup/shutdown; avoid `@app.on_event`.
- Disable OpenAPI docs in production unless the API is intentionally public.
- Keep migrations static, reversible, and descriptive.

## Async decision table

| Situation | Route/dependency shape |
| --- | --- |
| Awaitable non-blocking I/O | `async def` with `await` |
| Blocking I/O with no async client | `def` route/dependency so FastAPI uses the threadpool |
| Mostly async plus one blocking call | `async def` + `await asyncio.to_thread(...)` or `run_in_threadpool` |
| CPU-bound or long-running work | Offload to a worker queue, not `BackgroundTasks` |

## Gotchas and common mistakes

- Never call `requests`, `time.sleep`, sync file reads, or sync DB drivers directly inside `async def` routes.
- Do not use `psycopg2` or `postgresql+psycopg2://` in async FastAPI projects.
- Do not use `python-jose`; use PyJWT.
- Do not use Pydantic v1 patterns such as `json_encoders`; use Pydantic v2 serializers.
- Do not catch broad `Exception` around route bodies; catch specific domain errors.
- Do not use `BackgroundTasks` for work that needs retries, observability, scheduling, or reliability.
- Register custom pytest markers so CI output stays clean.
- Avoid monolithic `BaseSettings`; use domain-scoped settings with `env_prefix` when configuration grows.

## When to read the reference guide

Read `references/api-guide.md` when you need concrete examples for:

- Pydantic v2 schema patterns and serializers
- dependency chaining and auth/ownership checks
- async SQLAlchemy / SQLModel database setup
- error-handler examples
- lifespan startup validation
- background task vs worker-queue decisions
- API test fixtures and dependency overrides
- Alembic configuration
- OpenAPI documentation patterns
- `uv`, `ruff`, `ty`, and CLI conventions
- the full anti-pattern table
