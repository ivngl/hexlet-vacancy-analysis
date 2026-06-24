# AGENTS.md — Hexlet Vacancy Analysis

## Overview
Python/Django backend + React SPA frontend (Inertia.js) for aggregating & analyzing IT vacancies from HeadHunter, SuperJob, Telegram channels.

## Tech Stack
- **Backend:** Python 3.12+, Django 5.2, Celery 5.5 (Redis), PostgreSQL, Gunicorn
- **Frontend:** React 19, TypeScript 5.8, Vite 6, Mantine 8, Tailwind 4, Redux Toolkit
- **Package mgmt:** uv (Python), npm (frontend)
- **Testing:** pytest + pytest-django + factory-boy
- **Linting:** Ruff (Python), ESLint + tsc (frontend)

## Directory Layout
```
.
├── app/                    # Django project root
│   ├── homepage/           # Homepage Django app
│   ├── services/           # Business-logic apps
│   │   ├── vacancies/      # Core vacancy domain
│   │   ├── auth/           # Auth (users, GitHub, Yandex, Tinkoff)
│   │   ├── parser/         # Generic parser models/views
│   │   ├── hh/hh_parser/   # HeadHunter parser
│   │   ├── superjob/       # SuperJob parser
│   │   ├── telegram/       # Telegram parser
│   │   ├── ai/             # AI assistant (OpenRouter)
│   │   ├── pricing/        # Pricing plans
│   │   ├── blog/           # Blog
│   │   ├── map/            # Vacancy map
│   │   ├── account/        # User profile
│   │   └── foragencies/    # Agency feature
│   ├── frontend/           # React SPA (Vite + TypeScript)
│   │   └── src/
│   │       ├── components/pages/  # Page components
│   │       ├── components/shared/ # Shared UI
│   │       ├── store/     # Redux slices
│   │       └── hooks/     # Custom hooks
│   ├── templates/          # Django templates
│   ├── celery.py           # Celery app config
│   └── settings.py         # Django settings
├── pyproject.toml          # Python deps & metadata
└── Makefile                # Central task runner
```

## Commands

### Backend
```bash
make install-backend        # uv sync
make start-backend          # uv run python manage.py runserver
make lint-backend           # uv run ruff check .
make test-backend           # uv run python manage.py test --parallel
make migrate                # uv run python manage.py migrate
make render                 # uv run gunicorn app.wsgi:application
make run-telegram           # uv run python manage.py run_listener
```

### Frontend (run from `app/frontend/`)
```bash
npm install
npm run dev                 # Vite dev server (:5173)
npm run build               # tsc -b && vite build
npm run lint                # ESLint
npm run typecheck           # tsc --noEmit
```

### Make targets
```bash
make install        # install both backend + frontend deps
make build          # build frontend
make lint           # lint both
make test           # test backend only
```

## Conventions

### Backend (Python)
- snake_case for files, functions, variables; PascalCase for classes
- Django Class-Based Views with `inertia_render(request, "PageName", props={...})`
- Custom `QuerySet` / `Manager` classes for reusable ORM queries
- Singular PascalCase model names (e.g., `Vacancy`, `Company`, `HomePageBlock`)
- Private methods prefixed with `_`

### Frontend (TypeScript/React)
- PascalCase for components and files; camelCase for hooks/utils/variables
- Feature-Sliced Design: `app/`, `pages/`, `widgets/`, `features/`, `entities/`, `shared/`
- Pages imported dynamically by name via `import(`./components/pages/${name}.tsx`)`

### Architecture
- **Inertia.js** server-driven SPA — no REST API; Django renders React pages via props
- **Modular Django apps** under `app/services/` by domain
- **Celery** for async tasks (parsers, etc.)
- **OAuth** via GitHub, Yandex ID, Tinkoff ID
- **Async views** used for vacancy listing (`async def get`)

## Testing
- `pytest` with `pytest-django` and `factory-boy`
- Config: `pytest.ini` (sets `DJANGO_SETTINGS_MODULE=app.settings`)
- Coverage: `.coveragerc` (omits migrations, tests, admin, wsgi)

## Linting & Type Checking
- **Python lint:** `uv run ruff check .` (ruff.toml: line-length 89, rules E/F/I/C90)
- **Python types:** `mypy` with `django-stubs` plugin (mypy.ini)
- **Frontend lint:** `npm run lint` (ESLint flat config)
- **Frontend types:** `npm run typecheck` (strict TS config)
- **Pre-commit hooks:** trailing-whitespace, EOF fixer, ruff --fix + format, ESLint

## CI
- GitHub Actions (djangoCI.yml): push + PR, uses SQLite, runs lint + test
- Dependabot weekly for GHA, pip, npm
- Deployed on Render.com via `build.sh` + Gunicorn
