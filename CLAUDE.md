# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Quick Start

```bash
# Initial setup (one-time)
make setup

# Initialize database with test data
make db

# Start development servers (Django + Vite)
make dev

# Run tests
make test
```

Development servers run at:

- Django: http://localhost:8000
- Vite: http://localhost:5173

## Architecture

- This is a Django project (Django 6.0) built on Python 3.14.
- Python dependencies are managed by `uv` (see `pyproject.toml` and `uv.lock`).
- Frontend dependencies are managed by `npm` (see `package.json`). Node 24+ is required.
- All configuration is loaded from environment variables via `django-environ` (see `.env.example`).
  Configuration values should not be hardcoded.
- User authentication uses `django-allauth` with email-based login (no usernames) and MFA support.
  Allauth is also used to secure the Django admin (`DJANGO_ADMIN_FORCE_ALLAUTH = True`).
- The front end is standard Django views and templates — there is no SPA framework and no DRF / OpenAPI client.
- HTMX and Alpine.js are used to provide a single-page-app user experience with Django templates.
  HTMX is used for interactions which require accessing the backend, and Alpine.js is used for
  browser-only interactions.
- Reusable template components live under `templates/components/` and are rendered with
  [`django-cotton`](https://django-cotton.com) using the `<c-component-name />` syntax
  (e.g. `<c-forms.input :field="form.email" />`). No `{% load %}` tag is required for Cotton —
  it works automatically once the app is installed. Cotton's component dir is configured via
  `COTTON_DIR = "components"`.
- JavaScript and CSS files are kept in `/static/js/` and `/static/css/` respectively, and are built by Vite.
  They are loaded into Django templates via `django-vite` (`{% vite_asset %}` and `{% vite_asset_url %}`).
  The Vite entry points are `static/js/scripts.js` and `static/css/styles.css`.
- The front end uses Tailwind CSS 4 and DaisyUI 5. There is **no `tailwind.config.js`** — it is
  deprecated in Tailwind 4. All Tailwind / DaisyUI configuration lives in CSS files under
  `static/css/` (see `static/css/base/daisyui.css` for theme configuration and
  `static/css/styles.css` for plugin imports). The project ships 6 custom DaisyUI themes:
  `light` (default), `dark`, `contrast`, `material`, `dim`, `material-dark`.
- Icons are rendered with the Iconify Tailwind plugin: `<span class="iconify {prefix}--{icon-name}"></span>`.
  Available prefixes are `lucide`, `hugeicons`, and `ri`.
- The main database is **Postgres**. A SQLite fallback is wired into `env.db()` for convenience but
  is not supported as a real development target — `psycopg` is a hard dependency and the rest of
  the setup assumes Postgres. Set `DATABASE_URL` to a Postgres URL in your `.env`.
- Celery is used for background jobs and scheduled tasks (`django-celery-beat` for the scheduler).
  In `local` settings Celery runs eagerly (`CELERY_TASK_ALWAYS_EAGER = True`), so no worker is
  needed in development. To start a real worker manually:
  `uv run celery -A config.celery_app worker --loglevel=info`.
- Redis is used as the default cache and the message broker for Celery.
- Internationalization is enabled. Configured languages are English (`en`) and Brazilian Portuguese
  (`pt-br`, the default). Default timezone is `America/Sao_Paulo`. The project ships custom
  `UserLocaleMiddleware` and `UserTimezoneMiddleware` that activate the language/timezone stored
  on the authenticated user's profile.
- Email is sent via `django-anymail` with the Amazon SES backend in production. Local
  development uses the SMTP backend by default (override `DJANGO_EMAIL_BACKEND` to use the
  console backend).
- Static files are served by **WhiteNoise** in all environments. **Media** (user uploads) are
  served from local disk in development and from **S3** (via `django-storages`) in production.

## Project Layout

```
apps/
  core/      # BaseModel, validators, middleware, template tags, form mixins, management commands
  users/     # User + Admin/Specialist/Parent proxy models, profiles, allauth glue
  dashboard/ # Authenticated landing page
config/
  settings/  # base.py, local.py, production.py, test.py
  celery_app.py
  urls.py
  wsgi.py / asgi.py
static/      # Source CSS/JS (built by Vite into static/dist/)
templates/   # Django templates (templates/components/ for django-cotton, templates/partials/ for {% include %})
locale/      # gettext .po files (en, pt_BR)
fixtures/
```

### Settings

Environment-specific settings live in `config/settings/`:

- `base.py`: shared configuration
- `local.py`: local development (`DEBUG=True`, eager Celery, `django-browser-reload`, `django-watchfiles`)
- `production.py`: production settings (S3, SES, HTTPS, security headers)
- `test.py`: test environment (in-memory email, fast password hashers)

The active settings module is selected via `DJANGO_SETTINGS_MODULE` (or by `pytest` for tests).

## Commands you can run

The following commands can be used for various tools and workflows.
A `Makefile` is provided to help centralize commands:

```bash
make  # List available commands
```

### First-time Setup

```bash
make setup
```

This installs Python deps (`uv sync`), npm deps, builds frontend assets, and installs
pre-commit hooks. After it finishes, run `make db` to initialize the database.

To do everything in one shot (setup + database + dev servers):

```bash
make all
```

### Database

```bash
make db          # Apply migrations and populate with test data (admins, specialists, parents)
make db-fresh    # Drop, recreate, migrate, and re-populate the database
make migrate     # Apply pending migrations only
make migrations  # Create new migrations after model changes
make reset-db    # Drop and recreate the database (no migrations / no data)
```

### Starting the Application

Note: there is no `make start` / `make stop` for background services in this project.
Postgres and Redis are expected to already be running locally (e.g. via Docker or a
system service manager).

```bash
make dev         # Start Django (runserver) + Vite dev server with hot-reload
make dev-fresh   # Same as `make dev` but starts from a fresh database
```

Both processes run in the foreground via `script.sh`; press Ctrl-C to shut them down
cleanly. Defaults: Django on port 8000, Vite on port 5173. Override with `DJANGO_PORT`
and `DJANGO_VITE_SERVER_PORT`.

Access the app at http://localhost:8000.

## Common Commands

### Development

```bash
make shell                              # Open Django shell
uv run manage.py dbshell                # Open PostgreSQL shell
uv run manage.py <command> [args]       # Run any Django management command
make clean                              # Clear Django cache and compiled .pyc files
```

### Project-specific management commands

Custom commands live in `apps/*/management/commands/` and are invoked with
`uv run manage.py <name>`:

- `update_site` — sync the `django.contrib.sites` `Site` row from `SITE_NAME` / `SITE_DOMAIN` settings
- `create_test_admins` — create the two admin users (`dppazlopez@gmail.com`, `alissonpef@gmail.com`)
- `create_test_specialists` — bulk-create test specialists (defaults to 1000; supports `--count`; always passes `--reset` when called via `make populate-db`)
- `create_test_parents` — bulk-create test parents (defaults to 1000; supports `--count`; always passes `--reset` when called via `make populate-db`)
- `clear_cache` — clear the Django cache (Redis)
- `reset_db` — drop and recreate the database (from `django-extensions`)

### Testing

Tests use `pytest` (with `pytest-django`), `pytest-sugar`, and `factory-boy`. The test
settings module (`config.settings.test`) is wired up via `pyproject.toml`, and the database
is reused by default (`--reuse-db`). Tests live in `apps/<app>/tests/` directories
(e.g. `apps/users/tests/test_models.py`).

```bash
make test                                            # Run all tests
make test ARGS='apps/users/tests/test_models.py'     # Run a specific test file
make test ARGS='-k test_email_field -x'              # Pass any pytest flags
make test-fresh                                      # Run tests with a freshly-created database
```

### Python — uv

```bash
uv sync                       # Install / update Python dependencies from uv.lock
uv add '<package>'            # Add a new runtime dependency
uv add --dev '<package>'      # Add a new dev dependency
uv run <command> [args]       # Run a command inside the project's virtualenv
```

### Frontend — npm / Vite

```bash
make npm-install              # Install npm packages
make npm-build                # Build frontend assets for production (runs `vite build`)
npm install <package>         # Install a specific package
npm uninstall <package>       # Uninstall a package
npm run dev                   # Run the Vite dev server only (normally started by `make dev`)
npm run build                 # Build for production (same as `make npm-build`)
```

There is no TypeScript in this project — JS is plain ES modules.
Vite is run automatically with hot-reload as part of `make dev`.

### Translations

```bash
make translations             # Extract messages and compile both django.po and djangojs.po
```

This runs `makemessages --all` (for `django.po` and `djangojs.po`) followed by
`compilemessages`, ignoring `node_modules`, `venv`, and `.venv`. Strings marked with
`gettext_lazy()` in Python or `{% trans %}` / `{% blocktranslate %}` in templates are
extracted into `.po` files under `locale/` (currently `locale/pt_BR/`).

### Linting & Formatting

There are several formatters and linters wired up. Use the umbrella commands when in doubt.

```bash
make format                   # Run all formatters: prettier, djlint, ruff format, tailwhip
make lint                     # Run all linters:    ruff check --fix, djlint --lint
```

Individual tools:

```bash
make ruff-format              # Format Python with Ruff
make ruff-lint                # Lint and auto-fix Python with Ruff
make djlint-format            # Format Django templates with djlint
make djlint-lint              # Lint Django templates with djlint
make prettier-format          # Format CSS/JS/JSON/YAML/Markdown with Prettier
make tailwhip                 # Sort Tailwind classes in templates and CSS files
```

### Pre-commit hooks

Pre-commit is installed automatically by `make setup` (or manually with `make pre-commit-install`).
It runs Ruff, djlint, Prettier, `tailwhip`, and `django-upgrade` before every commit. Hooks can
be skipped with `git commit --no-verify` — but only sparingly; CI will fail if formatting drifts.

## General Coding Preferences

- Always prefer simple solutions.
- Avoid duplication of code whenever possible, which means checking for other areas of the codebase that might already have similar code and functionality (especially `apps/core/` for shared utilities).
- Only make changes that are requested or that you are confident are well understood and related to the change being requested.
- When fixing an issue or bug, do not introduce a new pattern or technology without first exhausting all options for the existing implementation. And if you finally do this, make sure to remove the old implementation afterwards so we don't have duplicate logic.
- Keep the codebase clean and organized.
- Avoid writing scripts in files if possible, especially if the script is likely only to be run once.
- Try to avoid having files over 200–300 lines of code. Refactor at that point.
- Don't ever add mock data to functions. Only add mocks to tests or utilities that are only used by tests.
- Always think about what other areas of code might be affected by any changes made.
- Never overwrite the `.env` file without first asking and confirming.

## Python Code Guidelines

### Code Style

- The project follows the `ruff` configuration in `pyproject.toml`. Run `make format` and `make lint` before committing — pre-commit will also enforce this.
- Ruff is configured with a broad rule set (`A`, `B`, `DJ`, `E`, `F`, `I`, `N`, `PL`, `RUF`, `S`, `SIM`, `UP`, etc.). Migrations and `staticfiles/` are excluded.
- Use double quotes for Python strings (Ruff enforced).
- Use one import per line. Imports are sorted with `ruff` / isort using `force-single-line = true` — do not group imports with parentheses.
- Try to use type hints in new code. Strict type-checking is not enforced; you can leave them out if it's burdensome. There is no need to add type hints to existing code if it does not already use them.
- Target Python 3.14 syntax (`django-upgrade --target-version 6.0` runs in pre-commit).

### Preferred Practices

- Use Django signals sparingly and document them well. See `apps/users/signals.py` for the existing pattern (profile + group creation on user save).
- Always use the Django ORM if possible. Use best practices like lazily evaluating querysets and selecting or prefetching related objects when necessary.
- Use function-based views by default. Class-based views are fine when the framework calls for them (e.g. `extra_views`, `formtools` wizards, generic CBVs).
- Always validate user input server-side.
- Handle errors explicitly, avoid silent failures.
- Use translation markup, usually `gettext_lazy as _` for strings on classes (verbose names, choices, model fields, validator messages) and `gettext` (or template `{% trans %}`/`{% blocktranslate %}`) for runtime strings.

### Django models

- All Django models extend `apps.core.models.BaseModel`, which combines `model_utils.TimeStampedModel` and `model_utils.UUIDModel`. This gives every model a UUID `id` primary key and `created` / `modified` timestamp fields. **Note**: the field names are `created` and `modified` (not `created_at` / `updated_at`) — this comes from `django-model-utils`.
- The project's user model is `apps.users.models.User` (`AUTH_USER_MODEL = "users.User"`). `User` extends both `BaseModel` and `AbstractUser`, has no `username` (email is the login field), and exposes a `role` field along with `Admin`, `Specialist`, and `Parent` proxy models. Each role has a corresponding `*Profile` model linked via `OneToOneField`.
- When you need to reference the user model in a foreign key from another app, use `settings.AUTH_USER_MODEL` rather than importing `User` directly. When you need the class itself (in views, forms, signals), import from `apps.users.models`.
- After model changes, run `make migrations` to generate migration files, review them, then `make migrate` to apply.

## Django Template Coding Guidelines for HTML files

- Indent templates with two spaces (enforced by `djlint`, `max_line_length = 119`).
- Use standard Django template syntax. The project also uses `django-cotton` — components from `templates/components/` are referenced as `<c-namespace.name attr="value" />`. Pass Python expressions as attributes with the `:attr="..."` syntax. djlint is configured with `custom_blocks = "cotton,partialdef,slot"` so these blocks format correctly.
- Use translation markup, usually `{% trans %}` or `{% blocktranslate trimmed %}` with user-facing text. Don't forget `{% load i18n %}` if needed.
- JavaScript and CSS bundles built with Vite must be included with the `{% vite_asset %}` / `{% vite_asset_url %}` template tags from `django-vite` (after `{% load django_vite %}`). The base template already wires up the standard bundles via `{% include "partials/styles.html" %}` and `{% include "partials/scripts.html" %}`.
- Use the Django `{% static %}` tag for loading images, fonts, and any other assets not managed by Vite.
- Prefer using Alpine.js for page-level JavaScript, and avoid inline `<script>` tags where possible. If a small Alpine component is needed, register it inside a JS file under `static/js/partials/` (see `topbar.js` for the pattern with `Alpine.data(...)`).
- Break re-usable template components into separate templates under `templates/components/` and render them with `django-cotton`'s `<c-... />` syntax. Use `{% include %}` for non-component partials in `templates/partials/`.
- Custom template tags live in `apps/core/templatetags/core_tags.py` (load with `{% load core_tags %}`). The `active_class` tag is the most-used one for navigation highlighting.
- Use DaisyUI styling markup for available components. When not available, fall back to standard Tailwind CSS classes. To override a DaisyUI style, append `!` to the Tailwind utility (e.g. `bg-red-500!`) — do not use `!important`.
- Stick with the DaisyUI color palette (`primary`, `secondary`, `accent`, `neutral`, `base-*`, `info`, `success`, `warning`, `error`) whenever possible. There is no need for `dark:` variants — DaisyUI swaps colors automatically based on `data-theme`.
- Tailwind classes in templates and CSS files are sorted by `tailwhip` (run via `make tailwhip` or `make format`).

## JavaScript Code Guidelines

### Code Style

- Use ES6+ syntax for JavaScript code (plain ES modules — no TypeScript in this project).
- Use 2 spaces for indentation in JavaScript and HTML files (enforced by Prettier and `djlint`).
- Use single quotes for JavaScript strings (Prettier enforced).
- End statements with semicolons.
- Use `camelCase` for variable and function names.
- Use ES6 `import` / `export` syntax for module management.
- The `@` alias resolves to `static/js/` in Vite (see `vite.config.mjs`), so `import foo from '@/partials/foo.js'` works.

### Preferred Practices

- When using HTMX, follow progressive enhancement patterns. The project ships an
  `HtmxMessagesMiddleware` (in `apps/core/middleware/messages.py`) that surfaces Django
  messages on HTMX responses via the `messages` event — listen for it on the client
  (see `static/js/partials/toasts.js`).
- Use Alpine.js for client-side interactivity that doesn't require server interaction.
  Register data components on the `alpine:init` event (see `static/js/partials/topbar.js`).
- Avoid inline `<script>` tags wherever possible. Add new modules under `static/js/partials/`
  and import them from `static/js/scripts.js`.
- Validate user input on both client and server side.
- Handle errors explicitly in promise chains and async functions.
- Theme / font preferences are managed by `static/js/partials/layout.js` and persisted in
  `localStorage` under the key `__SONO_CONFIG__`. Don't roll a parallel mechanism — extend
  this one if you need to persist new client-side preferences.

### Build System

- Code is bundled by Vite (see `vite.config.mjs`) and served with `django-vite`.
- During `make dev`, Vite runs in dev mode (`DJANGO_VITE.dev_mode = True` is set in
  `config/settings/local.py`) and assets are served from the Vite dev server with HMR.
- For production, `make npm-build` writes hashed bundles into `static/dist/` and
  `django-vite` reads `static/dist/.vite/manifest.json` to resolve URLs.

## Common Workflows

### Adding a new feature

1. Create or modify models in the appropriate app (extend `apps.core.models.BaseModel`).
2. Run `make migrations` and review the generated migration file.
3. Run `make migrate` to apply changes.
4. Implement views/URLs/forms/templates in the app.
5. Write tests under `apps/<app>/tests/` (use `factory-boy` factories — see `apps/users/tests/factories.py`).
6. Run `make test` to verify.
7. Run `make format` and `make lint` before committing.

### Modifying the frontend

1. Edit templates in `templates/` or Cotton components in `templates/components/`.
2. Update CSS under `static/css/` or JS under `static/js/`.
3. Vite hot-reloads CSS/JS automatically while `make dev` is running.
4. Run `make format` to sort Tailwind classes (`tailwhip`) and run `prettier` / `djlint`.
5. Verify in the browser at http://localhost:8000.

### Adding translatable strings

1. Wrap strings with `gettext_lazy() as _` (Python) or `{% trans %}` / `{% blocktranslate %}` (templates).
2. Run `make translations` to extract them into `locale/pt_BR/LC_MESSAGES/django.po`.
3. Fill in the `msgstr ""` entries (or use the `translate-po` Claude skill to auto-translate).
4. Run `make translations` again to recompile the `.mo` files.
