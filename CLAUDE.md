# Codebase Guidelines

## Architecture

- This is a Django project called **Sono**, built on Python 3.14.
- User authentication uses `django-allauth` (with MFA support via `allauth.mfa`).
- The front end is mostly standard Django views and templates.
- HTMX and Alpine.js are used to provide single-page-app user experience with Django templates.
- HTMX is used for interactions which require accessing the backend, and Alpine.js is used for browser-only interactions.
- JavaScript and CSS files are kept in the `/static/` folder and built by Vite.
- Assets are loaded via Django templates using `django-vite`.
- The front end uses Tailwind CSS (v4) and DaisyUI (v5) with 6 themes (light, dark, contrast, material, dim, material-dark).
- The main database is PostgreSQL (SQLite as fallback in development).
- Celery is used for background jobs and scheduled tasks.
- Redis is used as the default cache and the message broker for Celery.
- `django-cotton` is used for reusable template components (in the `templates/components/` directory).
- `django-htmx` provides HTMX middleware and utilities; `HtmxTemplateMixin` in `apps/core/viewmixins.py` handles partial template rendering for HTMX requests.

## Project Structure

```
sono/
├── apps/
│   ├── core/               # Shared utilities, mixins, validators, middleware, managers
│   ├── dashboard/          # Main dashboard app
│   └── users/              # User model, profiles, auth adapters, signals
├── config/
│   ├── settings/
│   │   ├── base.py         # Shared settings
│   │   ├── local.py        # Local development overrides
│   │   ├── production.py   # Production settings
│   │   └── test.py         # Test settings
│   ├── celery_app.py
│   └── urls.py
├── static/
│   ├── css/                # Tailwind + DaisyUI styles and plugin overrides
│   └── js/                 # Alpine.js + HTMX entry points
├── templates/              # Django HTML templates
│   ├── components/         # django-cotton reusable components
│   ├── partials/           # Included template fragments
│   ├── dashboard/
│   ├── account/
│   └── users/
├── manage.py
├── vite.config.mjs
└── pyproject.toml
```

## Commands You Can Run

A `Makefile` is provided to centralize commands:

```bash
make        # List all available commands
make help   # Same as above
```

### First-time Setup

```bash
make init   # Install Python + npm deps, build assets, run migrations, seed data
```

### Starting the Application

```bash
make dev    # Start Django + Vite dev servers concurrently
```

Access the app at http://localhost:8000 and Vite at http://localhost:5173.

### Common Commands

#### Development

```bash
make shell                      # Open the Django shell
make manage ARGS='<command>'    # Run any Django management command
make clean                      # Remove .pyc files, __pycache__, and Django caches
```

#### Database

```bash
make migrations     # Create new migrations (makemigrations)
make migrate        # Apply pending migrations
make reset-db       # Drop and recreate the database
make seed           # Populate the database with test data
make fresh          # reset-db + migrate + seed
```

#### Testing

```bash
make test                    # Run the full test suite
make test ARGS='-x'          # Stop on first failure
make test ARGS='apps/users'  # Run tests for a specific app
```

#### Python Code Quality

```bash
make ruff-format    # Format Python code with Ruff
make ruff-lint      # Lint and auto-fix Python code with Ruff
make ruff           # Run both format and lint
```

#### Python / uv

```bash
make uv add '<package>'             # Add a new Python package
make uv remove '<package>'          # Remove a Python package
make uv run '<command> <args>'      # Run a command in the project's environment
```

#### Frontend

```bash
make npm-install                    # Install all npm packages
make npm-install <package-name>     # Install a specific npm package
make npm-uninstall <package-name>   # Uninstall a specific npm package
make npm-dev                        # Start the Vite dev server only
make npm-build                      # Build frontend assets for production
```

Note: Vite runs automatically with hot-reload when using `make dev`.

#### Translations

```bash
make translations   # Extract and compile i18n translation strings
```

## Test Credentials

After running `make seed`, the following accounts are available:

| Email                  | Password | Role         |
| ---------------------- | -------- | ------------ |
| `dppazlopez@gmail.com` | `12345`  | 👑 Superuser |
| `alissonpef@gmail.com` | `12345`  | 👑 Superuser |

1,000 regular test users are also created with password `12345`.

---

## General Coding Preferences

- Always prefer simple solutions.
- Avoid duplication of code — check for existing similar functionality before writing new code.
- Only make changes that are clearly requested or directly related to the task at hand.
- When fixing a bug, exhaust all options within the existing implementation before introducing new patterns or libraries. If a new approach is adopted, remove the old implementation to avoid duplicate logic.
- Keep the codebase clean and organized.
- Avoid writing one-off scripts in files; prefer Django management commands for reusable operations.
- Try to keep files under 200–300 lines of code. Refactor when approaching that limit.
- Never add mock data inside application code. Mocks belong in tests or test-only utilities.
- Always consider what other areas of the codebase may be affected by a change.
- Never overwrite the `.env` file without first asking and confirming.

---

## Python Code Guidelines

### Code Style

- Follow PEP 8 with a 119-character line limit.
- Use double quotes for strings (enforced by Ruff).
- Sort imports with isort (via Ruff), using `force-single-line = true`.
- Use type hints in new code where practical. Strict type-checking is not enforced; omit annotations when they add unnecessary complexity.

### Preferred Practices

- Use Django signals sparingly and always document them clearly (see `apps/users/signals.py` for the existing pattern).
- Always use the Django ORM. Apply best practices: lazy queryset evaluation, `select_related`, and `prefetch_related` where appropriate.
- Use class-based views (CBVs) as the default, consistent with the existing codebase. Use `HtmxTemplateMixin` from `apps/core/viewmixins.py` for views that serve both full-page and HTMX partial responses.
- Always validate user input server-side.
- Handle errors explicitly — avoid silent failures.
- Use `gettext_lazy` (`_()`) for all user-facing strings.

### Django Models

- The project's user model is `apps.users.models.User` and should be imported directly or referenced via `settings.AUTH_USER_MODEL` / `get_user_model()` as appropriate.
- Models that need `created_at`/`updated_at` fields should use `model_utils.models.TimeStampedModel` or similar from `django-model-utils`, as already used in `User` and `UserProfile`.
- Models that need UUID primary keys should use `model_utils.models.UUIDModel` or similar, as already used in `User`.
- Use `apps.core.managers.ActiveQuerySet` as a base for querysets that need an `.active()` filter.
- Use `apps.core.validators.FileSizeValidator` for file size validation on file/image fields.

---

## Django Template Guidelines

- Indent templates with **2 spaces**.
- Use standard Django template syntax.
- Use `{% trans %}` or `{% blocktranslate trimmed %}` for all user-facing text. Always `{% load i18n %}` when needed.
- Load Vite-managed JS/CSS with `{% vite_asset %}` or `{% vite_asset_url %}` from `django-vite` (requires `{% load django_vite %}`).
- Use `{% static %}` for images and any static files not managed by Vite.
- Use `{% load django_htmx %}` and `{% htmx_script %}` where HTMX is required (already in `base.html`).
- Prefer Alpine.js for page-level JavaScript. Avoid inline `<script>` tags where possible.
- Break reusable template fragments into separate files using `{% include %}` (goes in `templates/partials/`) or `django-cotton` components (goes in `templates/components/`).
- Use **DaisyUI** markup for available components. Fall back to Tailwind CSS utility classes otherwise.
- Stick to the DaisyUI color palette (e.g. `btn-primary`, `text-error`, `bg-base-200`) whenever possible.
- Theme-aware styles should use CSS variables defined in `static/css/base/daisyui.css`.

---

## JavaScript Code Guidelines

### Code Style

- Use ES6+ syntax.
- Use 2 spaces for indentation in JS and HTML files.
- Use double quotes for strings (consistent with `.editorconfig`).
- Use camelCase for variable and function names.
- Use ES6 `import`/`export` for module management.

### Preferred Practices

- Use HTMX for server-driven interactions; follow progressive enhancement patterns.
- Use Alpine.js (`x-data`, `x-text`, etc.) for client-side interactivity that doesn't require server interaction.
- Avoid inline `<script>` tags wherever possible.
- Validate user input on both client and server side.
- Handle errors explicitly in promise chains and async/await functions.

### Build System

- Code is bundled with **Vite** and served via `django-vite`.
- Entry points are `static/js/main.js` (JavaScript) and `static/css/styles.css` (CSS), defined in `vite.config.mjs`.
- Output goes to `static/dist/`.
- The `LayoutCustomizer` class in `static/js/partials/layout.js` manages theme persistence via `localStorage` under the key `__SONO_CONFIG__`.
