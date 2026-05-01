# Sono

A full-stack Django application with a modern frontend using Vite, Tailwind CSS 4, DaisyUI 5, Alpine.js, and HTMX.

## Tech Stack

| Layer          | Technology                                           |
| -------------- | ---------------------------------------------------- |
| Backend        | Django 6.0 · Python 3.14                             |
| Frontend       | Vite · Tailwind CSS 4 · DaisyUI 5 · Alpine.js · HTMX |
| Database       | PostgreSQL · psycopg 3                               |
| Cache / Broker | Redis                                                |
| Task Queue     | Celery · django-celery-beat                          |
| Authentication | django-allauth (email-only, MFA)                     |
| Email          | django-anymail · Amazon SES                          |
| File Storage   | WhiteNoise (static) · AWS S3 (media, production)     |
| Python deps    | uv                                                   |
| JS deps        | npm · Node 24+                                       |

## Prerequisites

- Python 3.14
- Node.js 24+
- PostgreSQL
- Redis
- [uv](https://docs.astral.sh/uv/)

## Getting Started

### 1. Clone and set up the environment

```bash
git clone https://github.com/DenPaz/sono.git
cd sono
cp .env.example .env  # then edit with your local values
```

Key variables to set in `.env`:

```bash
DATABASE_URL=postgresql://user:password@localhost:5432/sono
REDIS_URL=redis://localhost:6379/0
DJANGO_SECRET_KEY=<your-secret-key>
```

See `.env.example` for the full list of available variables.

### 2. Install dependencies and initialize

```bash
make setup   # installs Python + JS deps, builds assets, installs pre-commit hooks
make db      # runs migrations and populates the database with test data
```

Or do everything in one shot:

```bash
make all
```

### 3. Start the development servers

```bash
make dev
```

This starts Django on [http://localhost:8000](http://localhost:8000) and the Vite dev server on [http://localhost:5173](http://localhost:5173) with hot-reload. Press Ctrl-C to stop both.

### Test credentials

After `make db`, the following accounts are available:

| Role       | Email                       | Password |
| ---------- | --------------------------- | -------- |
| Admin      | `dppazlopez@gmail.com`      | `12345`  |
| Admin      | `alissonpef@gmail.com`      | `12345`  |
| Specialist | _(1000 randomly generated)_ | `12345`  |
| Parent     | _(1000 randomly generated)_ | `12345`  |

## Project Structure

```
apps/
  core/        # BaseModel, validators, middleware, template tags, management commands
  users/       # User model, Admin/Specialist/Parent proxy models, profiles, allauth config
  dashboard/   # Authenticated landing page
config/
  settings/    # base.py, local.py, production.py, test.py
  celery_app.py
  urls.py
  wsgi.py
static/        # Source CSS (static/css/) and JS (static/js/) — built by Vite into static/dist/
templates/     # Django templates
  components/  # django-cotton components (<c-... /> syntax)
  partials/    # {% include %} partials (sidebar, header, footer, etc.)
  account/     # django-allauth templates
locale/        # Gettext .po files (pt_BR)
fixtures/
```

### User roles

The application has three roles, each with a corresponding proxy model and profile:

- **Admin** — full staff/superuser access, manages the platform.
- **Specialist** — standard authenticated user (non-staff).
- **Parent** — standard authenticated user (non-staff); assigned by default on public sign-up.

Each role maps to a Django group created automatically on first migration. Profiles (avatar, language, timezone) are created automatically via signals on user save.

## Common Commands

```bash
make help          # list all available commands

# Development
make dev           # start Django + Vite dev servers
make shell         # open Django shell
make clean         # clear cache and compiled .pyc files

# Database
make migrations    # create new migrations after model changes
make migrate       # apply pending migrations
make db            # migrate + populate with test data
make db-fresh      # drop, recreate, migrate, and re-populate
make reset-db      # drop and recreate the database (no data)

# Testing
make test                              # run all tests
make test ARGS="-k test_name"          # run specific tests
make test ARGS="apps/users/tests/"     # run a specific directory
make test-fresh                        # run tests with a fresh database

# Code quality
make format        # run all formatters (prettier, djlint, ruff, tailwhip)
make lint          # run all linters (ruff, djlint)

# Translations
make translations  # extract and compile all .po files
```

## Frontend

JavaScript and CSS source files live under `static/js/` and `static/css/` and are bundled by Vite. The two entry points are:

- `static/js/scripts.js` — imports HTMX, Alpine.js, and all page-level JS modules.
- `static/css/styles.css` — imports Tailwind CSS 4, DaisyUI 5, and custom CSS layers.

There is no `tailwind.config.js` — Tailwind 4 is configured entirely in CSS. DaisyUI themes are defined in `static/css/base/daisyui.css`. The project ships six custom themes: `light` (default), `dark`, `contrast`, `material`, `dim`, and `material-dark`.

Icons use the Iconify Tailwind plugin: `<span class="iconify lucide--settings"></span>`. Available prefixes: `lucide`, `hugeicons`, `ri`.

Reusable UI components live in `templates/components/` and are rendered with [django-cotton](https://django-cotton.com):

```html
<c-forms.input :field="form.email" icon="lucide--mail" />
```

## Configuration

All configuration is managed through environment variables via `django-environ`. Copy `.env.example` to `.env` and fill in your values. Settings modules:

| Module                       | Purpose                                                    |
| ---------------------------- | ---------------------------------------------------------- |
| `config.settings.local`      | Local development (debug on, eager Celery, browser-reload) |
| `config.settings.production` | Production (HTTPS, S3, SES, Redis cache, HSTS)             |
| `config.settings.test`       | Test suite (fast password hashing, in-memory email)        |

Set `DJANGO_SETTINGS_MODULE` to select the active module. In local development, `DJANGO_READ_DOT_ENV_FILE=True` causes the settings to read your `.env` file automatically.

## Running Tests

Tests use [pytest](https://pytest.org) with `pytest-django` and [factory-boy](https://factoryboy.readthedocs.io). The test database is reused between runs by default.

```bash
make test                        # run the full suite
make test ARGS="-x --tb=short"   # stop on first failure with short tracebacks
make test-fresh                  # recreate the test database from scratch
```

## Translations

The project supports English (`en`) and Brazilian Portuguese (`pt-br`, the default). To update translations after adding new strings:

```bash
make translations
```

This extracts strings from Python and template files into `locale/pt_BR/LC_MESSAGES/django.po` and `djangojs.po`, then compiles them.

## Deployment

The `Procfile` defines four process types for Heroku-style platforms:

```
release: python manage.py migrate
web:     gunicorn config.wsgi:application
worker:  celery -A config.celery_app worker --loglevel=info
beat:    celery -A config.celery_app beat --loglevel=info
```

Before deploying:

1. Set all required production environment variables (see `.env.example`).
2. Build frontend assets: `make npm-build`.
3. Collect static files: `uv run manage.py collectstatic --no-input`.

Production requires AWS credentials for S3 (media storage) and SES (email). See the `DJANGO_AWS_*` variables in `.env.example`.

## Contributing

1. Fork the repository and create a feature branch.
2. Run `make setup` to install dependencies and pre-commit hooks.
3. Make your changes following the conventions in `CLAUDE.md`.
4. Run `make format && make lint && make test` before opening a pull request.

Pre-commit hooks run automatically on `git commit` and enforce Ruff, djlint, Prettier, tailwhip, and django-upgrade.

## Authors

- [Dennis Paz](https://github.com/DenPaz)
- [Alisson Pereira](https://github.com/alissonpef)

## License

[MIT](LICENSE) © 2026 Dennis Paz
