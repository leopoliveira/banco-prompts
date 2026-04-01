# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Dependencies (uv, not pip)
uv pip install -e ".[dev]"

# Django
python src/manage.py runserver
python src/manage.py migrate

# Tests
pytest                           # all tests
pytest tests/test_prompts.py     # single file
pytest -k test_index_returns_ok  # single test by name
pytest --cov                     # with coverage

# Linting
ruff check src/ tests/
ruff format src/ tests/

# Alembic migrations (SQLAlchemy schema changes)
PYTHONPATH=src alembic revision --autogenerate -m "description"
PYTHONPATH=src alembic upgrade head

# Docker
docker compose up --build
```

## Architecture

Hybrid Django + SQLAlchemy project using a `src/` layout.

- **Django** handles HTTP routing, admin, auth, sessions, and middleware.
- **SQLAlchemy 2.0+** handles all domain models (not Django ORM). Models use `Mapped[]` type annotations and `MappedAsDataclass` for dataclass-style init.
- **Alembic** manages database schema migrations by reading SQLAlchemy's `Base.metadata`.
- **PostgreSQL 17** is the single database, shared by both Django (auth/sessions) and SQLAlchemy (domain models) via `psycopg`.
- **Tailwind CSS** via CDN with class-based dark mode.
- **uv** for dependency management (not pip).
- **Docker + Docker Compose** for containerized development.

### Project structure

```
src/
├── apps/prompts/
│   ├── models.py          # SQLAlchemy domain models (Category, LLMProvider, Prompt, M2M tables)
│   ├── views.py           # Thin Django views (index, prompt_list_api, prompt_detail_api, submit)
│   ├── services.py        # Business logic layer (queries, serialization, creation)
│   ├── urls.py            # App URL routing (namespace: "prompts")
│   └── admin_views.py     # Staff-only admin views (approve/reject, CRUD for categories/providers)
├── config/
│   ├── settings.py        # Django settings + DATABASE_URL for SQLAlchemy
│   └── urls.py            # Root URL config (admin CRUD routes + app includes)
├── db/
│   ├── base.py            # SQLAlchemy Base (DeclarativeBase + MappedAsDataclass)
│   ├── engine.py          # SessionLocal, get_db() context manager
│   └── migrations/        # Alembic migrations (versions/ with 001-, 002- prefix pattern)
├── static/js/
│   ├── theme-init.js      # Dark mode init (runs in <head>, prevents flash)
│   ├── base.js            # Alert auto-dismiss + theme toggle
│   └── prompts.js         # Index page: infinite scroll, filters, search, cards, modal, copy
└── templates/
    ├── base.html          # Base layout (nav, messages, theme toggle)
    ├── prompts/
    │   ├── index.html     # Main browsing page (card grid, filter chips, modal)
    │   └── submit.html    # Public submission form
    └── admin/
        ├── dashboard.html     # Admin dashboard with pending count
        ├── prompt_list.html   # Prompt approval/rejection table
        ├── sqla_list.html     # Generic list template (categories/providers)
        └── index.html         # Django admin index override
tests/
├── conftest.py            # Fixtures (db_engine, db_session, _patch_session, sample data)
└── test_prompts.py        # Model, view, and API tests
```

### Database wiring

`config/settings.py` defines both Django's `DATABASES` dict and a `DATABASE_URL` string built from the same env vars. `db/engine.py` creates the SQLAlchemy engine from `settings.DATABASE_URL`. Alembic's `env.py` reads the URL from Django settings (via `django.setup()`), not from `alembic.ini`. All three must point to the same PostgreSQL instance.

### Key conventions

- All domain models inherit from `db.base.Base` — this is what Alembic scans for migrations.
- Django apps live under `src/apps/`. Each app owns its own `models.py` (SQLAlchemy), `views.py`, `services.py`, and `urls.py`.
- App URLs are namespaced (`app_name = "prompts"`) and included from `config/urls.py`.
- Views are thin — business logic lives in `services.py`.
- `db/engine.py` provides `SessionLocal` and a `get_db()` context manager for obtaining database sessions. Views use `with get_db() as session:`.
- Configuration uses environment variables (12-factor). Copy `.env.example` to `.env` for local dev.
- Tests live outside `src/` in `tests/`. Pytest is configured in `pyproject.toml` with `DJANGO_SETTINGS_MODULE = "config.settings"` and `pythonpath = ["src"]`.
- Test fixtures monkeypatch `db.engine.SessionLocal` for isolation — each test gets its own rolled-back session.
- Alembic migrations use `001-{slug}.py` naming convention (set via `file_template` in `alembic.ini`).
- Alembic's `env.py` has an `include_object()` filter that ignores Django-managed tables (auth_*, django_*, etc.).
- Frontend uses JSON APIs for data (`/api/prompts/`, `/api/prompts/<id>/`) — templates don't receive prompt data from context, only categories/providers for filter chips.
- JavaScript is extracted into static files under `src/static/js/`, loaded via `{% static %}` template tags.
- UI text is in Portuguese (pt-BR). Dark mode is class-based with localStorage persistence.

### URL routes

| Pattern | View | Name |
|---|---|---|
| `/` | `views.index` | `prompts:index` |
| `/api/prompts/` | `views.prompt_list_api` | `prompts:prompt_list_api` |
| `/api/prompts/<id>/` | `views.prompt_detail_api` | `prompts:prompt_detail_api` |
| `/enviar/` | `views.submit` | `prompts:submit` |
| `/admin/painel/` | `admin_views.dashboard` | `admin_dashboard` |
| `/admin/prompts/` | `admin_views.prompt_list` | `admin_prompt_list` |
| `/admin/prompts/<pk>/aprovar/` | `admin_views.prompt_approve` | `admin_prompt_approve` |
| `/admin/prompts/<pk>/rejeitar/` | `admin_views.prompt_reject` | `admin_prompt_reject` |
| `/admin/categorias/` | `admin_views.category_list` | `admin_category_list` |
| `/admin/categorias/<pk>/excluir/` | `admin_views.category_delete` | `admin_category_delete` |
| `/admin/provedores/` | `admin_views.provider_list` | `admin_provider_list` |
| `/admin/provedores/<pk>/excluir/` | `admin_views.provider_delete` | `admin_provider_delete` |

### Domain models

- **Category** — `id`, `name` (unique)
- **LLMProvider** — `id`, `name` (unique)
- **Prompt** — `id`, `title`, `content`, `author`, `is_approved` (default False), `created_at`, `updated_at`, `categories` (M2M), `providers` (M2M)
- Junction tables: `prompt_categories`, `prompt_llm_providers`

### Docker

- `Dockerfile`: Python 3.14-slim, uv for deps, `entrypoint.sh` runs Django migrate then Alembic upgrade head before starting the server.
- `docker-compose.yml`: PostgreSQL 17 (host port 5433) + web service. DB healthcheck ensures web waits for PostgreSQL.
