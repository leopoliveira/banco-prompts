# Banco de Prompts

A web application for discovering, sharing, and copying AI prompts. Users can browse approved prompts, filter by category and LLM provider, and submit new prompts for review.

## Features

- **Prompt cards** with title, preview, author, date, category/provider badges, and copy button
- **Infinite scroll** for seamless browsing
- **Filter chips** by category (Escrita, Programacao, Marketing, etc.) and LLM provider (ChatGPT, Claude, Gemini, etc.)
- **Title search** with debounce
- **Detail modal** with full prompt content and copy-to-clipboard
- **Public submission form** with manual approval workflow
- **Admin dashboard** for approving/rejecting prompts and managing categories/providers
- **Dark mode** with persistent theme toggle

## Tech Stack

- **Python 3.14** / **Django 6.0+** (routing, admin, auth, sessions)
- **SQLAlchemy 2.0+** (domain models with `MappedAsDataclass`)
- **Alembic** (database migrations)
- **PostgreSQL 17** (single database shared by Django and SQLAlchemy)
- **Tailwind CSS** (via CDN)
- **uv** (package manager)
- **Docker** + **Docker Compose**

## Quick Start

### With Docker (recommended)

```bash
docker compose up --build
```

The app will be available at `http://localhost:8000`.

This automatically runs Django migrations, Alembic migrations, and seeds initial categories/providers.

### Local Development

1. **Prerequisites**: Python 3.14+, PostgreSQL, [uv](https://docs.astral.sh/uv/)

2. **Configure environment**:
   ```bash
   cp .env.example .env
   # Edit .env with your PostgreSQL credentials
   ```

3. **Install dependencies**:
   ```bash
   uv pip install -e ".[dev]"
   ```

4. **Run migrations**:
   ```bash
   python src/manage.py migrate
   PYTHONPATH=src alembic upgrade head
   ```

5. **Start the server**:
   ```bash
   python src/manage.py runserver
   ```

## Project Structure

```
banco-prompts/
├── src/
│   ├── apps/prompts/          # Main app
│   │   ├── models.py          # SQLAlchemy domain models
│   │   ├── views.py           # Django views (thin layer)
│   │   ├── services.py        # Business logic
│   │   ├── urls.py            # App URL routing
│   │   └── admin_views.py     # Staff admin views
│   ├── config/                # Django settings & root URLs
│   ├── db/                    # SQLAlchemy engine & Alembic migrations
│   ├── static/js/             # JavaScript (theme, base, prompts)
│   └── templates/             # Django templates
├── tests/                     # Pytest test suite
├── Dockerfile
├── docker-compose.yml
└── pyproject.toml
```

## Admin

1. Create a superuser:
   ```bash
   python src/manage.py createsuperuser
   ```

2. Access the admin dashboard at `/admin/` or use the "Admin" link in the navbar (visible to staff users).

From the admin dashboard you can:
- Approve or reject submitted prompts
- Manage categories and LLM providers

## Testing

```bash
pytest                           # all tests
pytest tests/test_prompts.py     # single file
pytest -k test_index_returns_ok  # single test by name
pytest --cov                     # with coverage
```

## Linting

```bash
ruff check src/ tests/
ruff format src/ tests/
```
