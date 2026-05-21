# FastAPI API Best Practices

Prescriptive conventions for building production-grade FastAPI applications — API layer only, not full-stack (no templates, Jinja2, SSR, static files).

## Compatibility Baseline

Pin to these versions or newer. All examples assume them.

| Dependency | Minimum | Notes |
| --- | --- | --- |
| Python | 3.11 | `StrEnum`, `X | Y` union syntax |
| FastAPI | 0.115 | `Annotated[T, Depends(...)]` is idiomatic |
| Pydantic | 2.7 | v1 APIs removed; `pydantic-settings` is separate |
| SQLModel | 0.0.22 | Built on Pydantic v2 + SQLAlchemy 2.0 |
| SQLAlchemy | 2.0 | Async API as default |
| psycopg | 3 | **Never psycopg2** — it's the old synchronous driver |
| Alembic | 1.13 | Async-aware migrations |
| httpx | 0.27 | `ASGITransport` for in-process tests |
| PyJWT | 2.9 | Not `python-jose` (unmaintained) |
| ruff | 0.6 | Replaces black, isort, autoflake |
| ty | 0.1 | Astral type checker — drop mypy |
| uv | 0.6 | Package manager + venv, drop pip/poetry |
| aiofiles | 24 | Async file I/O |

---

## Project Structure

Organize by **domain** (bounded context), not by file type. File-type grouping (`routers/`, `models/`, `schemas/`) collapses under growth.

```text
app/
├── {domain}/            # auth/, posts/, payments/
│   ├── router.py        # Endpoints — core of the module
│   ├── schemas.py       # Pydantic models (request/response shapes)
│   ├── models.py        # SQLModel / SQLAlchemy ORM tables
│   ├── service.py       # Business logic
│   ├── dependencies.py  # Route dependencies (auth, validation, DB lookups)
│   ├── config.py        # Domain-scoped BaseSettings
│   ├── constants.py     # Error codes, enumerations
│   ├── exceptions.py    # Domain-specific exception classes
│   └── utils.py         # Pure helpers (not business logic)
├── cli/                 # CLI entry points (typer)
│   ├── __init__.py
│   ├── users.py
│   └── db.py
├── config.py            # Global BaseSettings
├── database.py          # Async engine + session factory
├── exceptions.py        # Global exception base + handlers
└── main.py              # FastAPI app, lifespan, router includes
```

**Cross-domain imports** — always use the explicit package name. Never `from app.auth import *`.

```python
from app.auth import constants as auth_constants
from app.notifications import service as notification_service
from app.posts.constants import ErrorCode as PostsErrorCode
```

---

## Async Routes: The Decision Tree

The single biggest source of production outages is blocking calls inside `async def` routes. Every route decision starts here:

| The route does this | Use | Because |
| --- | --- | --- |
| `await`-able non-blocking I/O (httpx, asyncpg, aiofiles) | `async def` | Keeps the event loop free |
| Blocking I/O with no async client available | `def` | FastAPI runs it in a threadpool, loop stays clear |
| Mix of async I/O + one blocking call | `async def` + `await asyncio.to_thread(...)` | Best of both; don't push the whole route to a thread |
| CPU-bound work (>50 ms compute) | Offload to a worker (Celery / Arq / RQ) | Threads can't help — the GIL serializes Python CPU work |

### Do / Don't

```python
# DON'T — blocking call freezes the entire event loop
@router.get("/bad")
async def bad():
    time.sleep(10)             # every request on this worker is stuck
    return {"ok": True}

# DON'T — sync file read inside async def (same problem)
async def process(path: Path) -> None:
    text = path.read_text()    # BLOCKS the event loop

# DO — sync route (FastAPI moves it to a threadpool)
@router.get("/sync-ok")
def sync_ok():
    time.sleep(10)
    return {"ok": True}

# DO — async route with awaitable I/O
@router.get("/async-ok")
async def async_ok():
    await asyncio.sleep(10)
    return {"ok": True}

# DO — wrap a sync call in asyncio.to_thread
async def process(path: Path) -> None:
    text = await asyncio.to_thread(path.read_text)

# DO — use aiofiles for async file I/O
import aiofiles
async def process(path: Path) -> None:
    async with aiofiles.open(path) as f:
        text = await f.read()

# DO — async route with one blocking dependency
from fastapi.concurrency import run_in_threadpool

@router.get("/wrap")
async def wrap():
    result = await run_in_threadpool(legacy_sync_client.fetch, "id")
    return result
```

---

## Pydantic v2: Schemas and Validation

### Use Pydantic exhaustively

Built-in validators remove boilerplate and produce automatic OpenAPI documentation.

```python
from enum import StrEnum
from pydantic import AnyUrl, BaseModel, EmailStr, Field

class MusicBand(StrEnum):
    AEROSMITH = "AEROSMITH"
    QUEEN = "QUEEN"
    ACDC = "AC/DC"

class UserCreate(BaseModel):
    first_name: str = Field(min_length=1, max_length=128)
    username: str = Field(min_length=1, max_length=128, pattern=r"^[A-Za-z0-9_-]+$")
    email: EmailStr
    age: int = Field(ge=18)                   # required, must be >= 18
    favorite_band: MusicBand | None = None
    website: AnyUrl | None = None
```

**Don't** write `Field(ge=18, default=None)`. The constraint and the default contradict each other. Choose one: required (`Field(ge=18)`) or optional (`int | None = Field(default=None, ge=18)`).

### Custom base model

`json_encoders` is gone in Pydantic v2. Use `@field_serializer`.

```python
from datetime import datetime
from zoneinfo import ZoneInfo
from pydantic import BaseModel, ConfigDict, field_serializer

class CustomModel(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    @field_serializer("*", when_used="json", check_fields=False)
    def _serialize_datetimes(self, value):
        if isinstance(value, datetime):
            if value.tzinfo is None:
                value = value.replace(tzinfo=ZoneInfo("UTC"))
            return value.strftime("%Y-%m-%dT%H:%M:%S%z")
        return value
```

### Separate request and response schemas

Never expose internal ORM fields in API responses. Create dedicated `*Response` and `*Create`/`*Update` schemas.

```python
# DON'T — leaks internal state
class UserRead(User.table):
    pass

# DO — explicit public shape
class UserResponse(BaseModel):
    id: UUID4
    username: str
    created_at: datetime

class UserCreate(BaseModel):
    username: str = Field(min_length=3, max_length=64)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
```

---

## Dependency Injection

### Use `Annotated` form — the idiomatic style since FastAPI 0.95

```python
from typing import Annotated
from fastapi import Depends

PostDep = Annotated[dict, Depends(valid_post_id)]

@router.get("/posts/{post_id}")
async def get_post(post: PostDep):
    return post

# The legacy default-argument form still works but avoid it:
# async def get_post(post: dict = Depends(valid_post_id)):
```

### Dependencies are for validation, not just injection

Validate data against the database inside dependencies — not in every endpoint. FastAPI caches dependency results per request, so the same `Depends(x)` called 5 times in one route runs `x` once.

```python
# dependencies.py
async def valid_post_id(post_id: UUID4) -> dict:
    post = await service.get_by_id(post_id)
    if not post:
        raise PostNotFound()
    return post

# router.py
@router.get("/posts/{post_id}")
async def get_post(post: PostDep):
    return post  # post is already validated and loaded

@router.put("/posts/{post_id}")
async def update_post(update: PostUpdate, post: PostDep):
    return await service.update(post["id"], update)
```

### Chain dependencies for composable auth + ownership

```python
async def parse_jwt_data(
    token: Annotated[str, Depends(OAuth2PasswordBearer(tokenUrl="/auth/token"))],
) -> dict:
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALG])
    except InvalidTokenError as exc:
        raise InvalidCredentials() from exc
    return {"user_id": payload["id"]}

async def valid_owned_post(
    post: Annotated[dict, Depends(valid_post_id)],
    token_data: Annotated[dict, Depends(parse_jwt_data)],
) -> dict:
    if post["creator_id"] != token_data["user_id"]:
        raise UserNotOwner()
    return post
```

**Tip**: use the same path-variable name across routers when you want to reuse a dependency. E.g., `profile_id` in both `/profiles/{profile_id}` and `/creators/{profile_id}` lets you chain
`valid_profile_id` → `valid_creator_id`.

### Prefer `async def` dependencies

Even for small CPU-only checks, `async def` dependencies avoid unnecessary threadpool overhead. Sync deps run in the threadpool by default.

---

## Configuration: BaseSettings

### Split across domains

**Never** keep one monolithic `BaseSettings` for the entire app. Each domain owns its config.

```python
# app/auth/config.py
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import SecretStr

class AuthConfig(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="AUTH_", env_file=".env", extra="ignore")

    JWT_ALG: str = "HS256"
    JWT_SECRET: SecretStr               # raises at startup if missing
    JWT_EXP_MINUTES: int = 15
    REFRESH_TOKEN_KEY: SecretStr
    REFRESH_TOKEN_EXP_MINUTES: int = 60 * 24 * 30
    SECURE_COOKIES: bool = True

auth_settings = AuthConfig()  # validates on import
```

### Validate env var shape at startup

Use Pydantic's types to enforce the shape of URLs, secrets, and tokens. A missing or malformed env var should crash at import time, not at 3 AM when a request hits it.

```python
from pydantic import PostgresDsn, RedisDsn, SecretStr, AnyHttpUrl

class Config(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    DATABASE_URL: PostgresDsn       # malformed URL → immediate failure
    REDIS_URL: RedisDsn
    SENTRY_DSN: AnyHttpUrl | None = None
    SECRET_KEY: SecretStr           # must be set, never defaults
    CORS_ORIGINS: list[AnyHttpUrl]  # validates each origin is a valid URL
    ENVIRONMENT: Literal["local", "staging", "production"] = "local"
```

---

## Database: SQLModel + psycopg 3 + Async

### Engine setup

```python
# app/database.py
from sqlmodel import SQLModel
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

engine = create_async_engine(
    str(settings.DATABASE_URL),
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
)
SessionFactory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def get_db() -> AsyncSession:
    async with SessionFactory() as session:
        yield session

async def init_db() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
```

### psycopg 3 — never psycopg2

psycopg2 is synchronous-only and unmaintained in its async fork. Always use `psycopg` (v3) with the async driver.

```text
# requirements or pyproject.toml
psycopg[binary]>=3.2
```

The connection URL uses the `+psycopg` (v3) or `+asyncpg` driver prefix, never `+psycopg2`:

```text
DATABASE_URL=postgresql+psycopg://user:pass@localhost:5432/dbname
```

### SQLModel tables

SQLModel combines SQLAlchemy ORM + Pydantic validation in one class.

```python
from sqlmodel import Field, SQLModel
from uuid import UUID, uuid4

class User(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    username: str = Field(min_length=3, max_length=64, unique=True)
    email: str = Field(max_length=255)
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=utcnow)
```

### SQL-first, Pydantic-second

Push joins, aggregation, and JSON shaping into the database — Postgres is orders of magnitude faster at this than CPython. Use Pydantic only for response validation, not for data transformation.

```python
# app/posts/service.py
from sqlalchemy import select, func, desc
from sqlalchemy.sql.functions import coalesce
from sqlmodel import col

async def get_posts(db: AsyncSession, creator_id: UUID, *, limit: int = 10, offset: int = 0):
    stmt = (
        select(Post, User.username)
        .join(User, Post.creator_id == User.id)
        .where(Post.creator_id == creator_id)
        .order_by(desc(coalesce(Post.updated_at, Post.created_at)))
        .limit(limit)
        .offset(offset)
    )
    result = await db.execute(stmt)
    return result.all()  # hydrates into response schemas in the router, not here
```

### Naming conventions

- `lower_case_snake` everywhere
- Singular table names: `post`, `user`, `payment_account`
- Group related tables with a prefix: `payment_bill`, `payment_subscription`
- `_at` suffix for datetime columns, `_date` suffix for date columns
- Same FK column name across all tables that reference it (`profile_id`, not `user_id` here and `profile_id` there)

### Index naming convention

```python
from sqlalchemy import MetaData

POSTGRES_INDEXES_NAMING_CONVENTION = {
    "ix": "%(column_0_label)s_idx",
    "uq": "%(table_name)s_%(column_0_name)s_key",
    "ck": "%(table_name)s_%(constraint_name)s_check",
    "fk": "%(table_name)s_%(column_0_name)s_fkey",
    "pk": "%(table_name)s_pkey",
}
metadata = MetaData(naming_convention=POSTGRES_INDEXES_NAMING_CONVENTION)
```

---

## Error Handling

### Domain exceptions + FastAPI exception handlers

Business-logic code should raise domain exceptions, not `HTTPException`. Let the API layer map them to HTTP responses.

```python
# app/exceptions.py
class AppError(Exception):
    """Base for all application errors."""

class NotFoundError(AppError):
    pass

class ConflictError(AppError):
    pass

class UnauthorizedError(AppError):
    pass

# app/main.py
from fastapi import Request
from fastapi.responses import JSONResponse

@app.exception_handler(NotFoundError)
async def not_found_handler(request: Request, exc: NotFoundError):
    return JSONResponse(status_code=404, content={"detail": str(exc)})

@app.exception_handler(ConflictError)
async def conflict_handler(request: Request, exc: ConflictError):
    return JSONResponse(status_code=409, content={"detail": str(exc)})

@app.exception_handler(UnauthorizedError)
async def unauthorized_handler(request: Request, exc: UnauthorizedError):
    return JSONResponse(status_code=401, content={"detail": str(exc)})
```

### Don't catch `Exception` broadly

A bare `try: ... except Exception: ...` around a route body silently swallows bugs and turns 500s into 200s. Catch the specific exception class you expect.

---

## Lifespan (Startup / Shutdown)

Use the `lifespan` context manager — not the deprecated `@app.on_event("startup")` / `@app.on_event("shutdown")`.

```python
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: runs before the app accepts requests
    await init_db()
    yield
    # Shutdown: runs after the last request completes
    await engine.dispose()

app = FastAPI(lifespan=lifespan)
```

**Startup validation**: check that runtime dependencies (files on disk, external service reachability) are available inside `lifespan` before the `yield`. Crash early, not on the first request.

```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    config_path = Path("/etc/myapp/config.yaml")
    if not config_path.exists():
        raise RuntimeError(f"Required config file missing: {config_path}")
    yield
```

---

## Background Tasks vs Task Queues

| Use `BackgroundTasks` when… | Use Celery / Arq / RQ when… |
| --- | --- |
| Task is < 1 second | Task takes seconds to minutes |
| Failure can be silently dropped | You need retries, dead-letter handling, or visibility |
| Task is in-process (send email, log a row) | Task needs a separate worker pool or CPU isolation |
| No scheduling needed | Cron, ETA, or rate limiting required |

`BackgroundTasks` run **after the response is sent, in the same worker process**. If the worker dies, the task is gone — no retry, no log. Don't use them for anything you'd page on.

---

## Testing

### Async client from day one

```python
import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app

@pytest.fixture
async def client() -> AsyncClient:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

@pytest.mark.asyncio
async def test_create_post(client: AsyncClient):
    resp = await client.post("/posts", json={"title": "hello"})
    assert resp.status_code == 201
```

Never use `async_asgi_testclient` — it's unmaintained. `httpx.AsyncClient` + `ASGITransport` is the supported path.

### Override dependencies, don't monkeypatch

```python
from app.auth.dependencies import parse_jwt_data
from app.main import app

def fake_user():
    return {"user_id": "00000000-0000-0000-0000-000000000001"}

@pytest.fixture(autouse=True)
def _override_auth():
    app.dependency_overrides[parse_jwt_data] = fake_user
    yield
    app.dependency_overrides.clear()
```

### Register pytest markers

If you use custom markers like `@pytest.mark.integration` or `@pytest.mark.slow`, register them in `pytest.ini` at the project root — not in `pyproject.toml`. Unregistered markers produce warnings and
muddy CI output.

```ini
# pytest.ini
[pytest]
markers =
    integration: marks tests that require a real database
    slow: marks tests that take longer than 1 second
```

### Integration tests: use a real database

Don't mock the database in integration tests — mock/prod divergence inevitably fires in production. Use testcontainers, an ephemeral test schema, or a local dev DB with `dependency_overrides` for auth
and external services only.

---

## Migrations: Alembic

- Use the async template: `alembic init -t async migrations`
- Migrations must be **static** and **reversible**. No dynamic data generation.
- Descriptive filenames:

```ini
# alembic.ini
file_template = %%(year)d-%%(month).2d-%%(day).2d_%%(slug)s
```

This produces names like `2026-05-18_add_post_content_idx.py`.

---

## API Documentation

### Hide docs in production

Unless your API is public, disable OpenAPI docs outside local/staging:

```python
from app.config import settings

SHOW_DOCS_IN = {"local", "staging"}
app_kwargs = {"title": "My API"}
if settings.ENVIRONMENT not in SHOW_DOCS_IN:
    app_kwargs["openapi_url"] = None

app = FastAPI(**app_kwargs)
```

### Document endpoints fully

Every endpoint gets `response_model`, `status_code`, `summary`, `description`, `tags`, and `responses` for non-200 outcomes.

```python
@router.post(
    "/items",
    response_model=ItemResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create an item",
    description="Creates an item owned by the authenticated user.",
    tags=["items"],
    responses={
        status.HTTP_400_BAD_REQUEST: {"model": ErrorResponse, "description": "Validation error"},
        status.HTTP_409_CONFLICT:    {"model": ErrorResponse, "description": "Slug already exists"},
    },
)
async def create_item(payload: ItemCreate) -> ItemResponse: ...
```

---

## Tooling: uv, ruff, ty

All three are Astral tools, designed to work together. They replace pip/poetry, black/isort/flake8, and mypy respectively — each is an order of magnitude faster.

### uv — package manager

```bash
uv init                    # create pyproject.toml
uv add fastapi uvicorn     # add dependencies
uv add --dev pytest httpx  # add dev dependencies
uv sync                    # install all
uv run uvicorn app.main:app --reload
```

Always use `uv` for dependency management — never `pip` or `poetry`.

### ruff — linter + formatter

```bash
ruff check --fix app tests
ruff format app tests
```

Add to CI and pre-commit. Ruff replaces black + isort + autoflake + most of flake8.

Configure in a separate `ruff.toml` at the project root — never in `pyproject.toml`:

```toml
# ruff.toml
target-version = "py311"
line-length = 100

[lint]
select = ["E", "W", "F", "I", "N", "UP", "B", "SIM", "RUF"]

[format]
quote-style = "double"
```

### ty — type checker

```bash
ty check app tests
```

Run in CI. `ty` replaces mypy — same checks, dramatically faster.

Configure in a separate `ty.toml` at the project root — never in `pyproject.toml`:

```toml
# ty.toml
strict = true
```

---

## CLI Scripts

CLI entry points live in `app/cli/` and use [typer](https://typer.tiangolo.com/) (built on Click, with FastAPI-style type annotations).

```python
# app/cli/__init__.py
import typer
from app.cli import users, db

app = typer.Typer()
app.add_typer(users.app, name="users")
app.add_typer(db.app, name="db")

def main():
    app()
```

```python
# app/cli/users.py
import typer
from app.database import SessionFactory
from app.users import service

app = typer.Typer()

@app.command()
def create(email: str, username: str):
    """Create a new user."""
    ...
```

Register the entry point in `pyproject.toml`:

```toml
[project.scripts]
myapp = "app.cli:main"
```

Now `uv run myapp users create --email a@b.com --username alice` works. CLI scripts import from `app.*` just like any other module — they share the same database session factory, config, and services.
Don't duplicate logic between CLI and API.

---

## Anti-Patterns: Common AI-Agent Mistakes

Watch for these in every diff. Each is a real failure mode.

| Anti-pattern | Why wrong | Fix |
| --- | --- | --- |
| `requests.get(...)` inside `async def` | Blocks the event loop | `httpx.AsyncClient` or `await asyncio.to_thread(...)` |
| `time.sleep` / `path.read_text()` / sync DB driver inside `async def` | Blocks the event loop | Async equivalent or `asyncio.to_thread` |
| `from jose import jwt` | `python-jose` is unmaintained | `import jwt` (PyJWT) |
| `psycopg2` anywhere | Sync-only, old | `psycopg` (v3) with `+psycopg://` in the URL |
| `model_config = ConfigDict(json_encoders={...})` | Deprecated in Pydantic v2 | `@field_serializer` |
| Returning a Pydantic model when `response_model=` is the same class | Model constructed twice (validate + serialize) | Return a dict/ORM row and let `response_model` validate, or drop `response_model` |
| One monolithic `BaseSettings` for the whole app | Every domain reads every var, hard to reason about | One per domain with `env_prefix` |
| `Field(ge=18, default=None)` | Constraint contradicts default | `Field(ge=18)` or `int \| None = Field(default=None, ge=18)` |
| Catching `Exception` around a route body | Hides bugs, turns 500s into 200s | Catch the specific exception class |
| `BackgroundTasks` for anything you'd page on | No retry, dies with worker | Celery / Arq / RQ |
| Two lists that must stay in sync | Drift is inevitable | Single source of truth (dict, enum, or database lookup) |
| Unregistered pytest markers | CI warnings, missed filtering | Register in `pytest.ini` under `[pytest]` |
| `from async_asgi_testclient import TestClient` | Unmaintained | `httpx.AsyncClient` + `ASGITransport` |
| `@app.on_event("startup")` / `@app.on_event("shutdown")` | Deprecated | `lifespan` context manager |
| `DATABASE_URL=postgresql+psycopg2://...` | Old driver | `postgresql+psycopg://...` |

---

## Quick Reference

| Scenario | Solution |
| --- | --- |
| Package management | `uv` (add, sync, run) |
| Non-blocking I/O | `async def` route with `await` |
| Blocking I/O (no async client exists) | `def` route (sync, runs in threadpool) |
| Sync call inside async route | `await asyncio.to_thread(fn, *args)` |
| Async file I/O | `aiofiles` |
| CPU-bound work | Celery / Arq / RQ worker process |
| Request validation against DB | Dependency that loads + validates + returns |
| Reuse logic across routes | Chain dependencies |
| Dependency injection modern form | `Annotated[T, Depends(...)]` |
| Per-request dependency caching | Default — same `Depends(x)` runs once per request |
| Per-domain config | One `BaseSettings` subclass per domain, `env_prefix` |
| Custom datetime serialization | `@field_serializer` |
| Fire-and-forget short task | `BackgroundTasks` |
| Reliable / scheduled / heavy task | Celery / Arq / RQ |
| JWT | `PyJWT` (`import jwt`) |
| Async DB | SQLModel + `psycopg` (v3) + `AsyncSession` |
| HTTP test client | `httpx.AsyncClient` + `ASGITransport` |
| Swap dep in tests | `app.dependency_overrides[dep] = fake` |
| Startup / shutdown | `lifespan` context manager |
| Lint + format | `ruff check --fix` + `ruff format` |
| Tool configs | Separate files: `ruff.toml`, `ty.toml` at project root |
| API docs in production | Disable via `openapi_url=None` |
| ORM table definition | SQLModel (`class Foo(SQLModel, table=True)`) |
| CLI scripts | `app/cli/` with typer, registered in `pyproject.toml` |
