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
alembic revision --autogenerate -m "description"
alembic upgrade head
```

## Architecture

Hybrid Django + SQLAlchemy project using a `src/` layout.

- **Django** handles HTTP routing, admin, auth, sessions, and middleware.
- **SQLAlchemy 2.0+** handles all domain models (not Django ORM). Models use `Mapped[]` type annotations and `MappedAsDataclass` for dataclass-style init.
- **Alembic** manages database schema migrations by reading SQLAlchemy's `Base.metadata`.
- **PostgreSQL** is the single database, shared by both Django (auth/sessions) and SQLAlchemy (domain models) via `psycopg`.

### Database wiring

`config/settings.py` defines both Django's `DATABASES` dict and a `DATABASE_URL` string built from the same env vars. `db/engine.py` creates the SQLAlchemy engine from `settings.DATABASE_URL`. Alembic reads its own URL from `alembic.ini`. All three must point to the same PostgreSQL instance.

### Key conventions

- All domain models inherit from `db.base.Base` — this is what Alembic scans for migrations.
- Django apps live under `src/apps/`. Each app owns its own `models.py` (SQLAlchemy), `views.py`, and `urls.py`.
- App URLs are namespaced (`app_name = "prompts"`) and included from `config/urls.py`.
- `db/engine.py` provides `SessionLocal` and a `get_session()` generator for obtaining database sessions.
- Configuration uses environment variables (12-factor). Copy `.env.example` to `.env` for local dev.
- Tests live outside `src/` in `tests/`. Pytest is configured in `pyproject.toml` with `DJANGO_SETTINGS_MODULE = "config.settings"` and `pythonpath = ["src"]`.
