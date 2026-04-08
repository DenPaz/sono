# Sono

Sono App.

---

## 🧰 Tech Stack

### Backend

|     | Library                                                          | Purpose                         |
| --- | ---------------------------------------------------------------- | ------------------------------- |
| 🐍  | [Django 6.0](https://www.djangoproject.com/)                     | Web framework                   |
| 🐘  | [PostgreSQL](https://www.postgresql.org/)                        | Primary database                |
| 🌿  | [Celery](https://docs.celeryq.dev/) + [Redis](https://redis.io/) | Async task queue and cache      |
| 🔐  | [django-allauth](https://allauth.readthedocs.io/)                | Authentication with MFA support |
| 🦄  | [Gunicorn](https://gunicorn.org/)                                | WSGI server for production      |

### Frontend

|     | Library                                     | Purpose                      |
| --- | ------------------------------------------- | ---------------------------- |
| ⚡  | [Vite 8](https://vite.dev/)                 | Asset bundler and dev server |
| 🎨  | [Tailwind CSS v4](https://tailwindcss.com/) | Utility-first CSS            |
| 🌼  | [DaisyUI v5](https://daisyui.com/)          | Component library (6 themes) |
| 🏔️  | [Alpine.js](https://alpinejs.dev/)          | Lightweight reactivity       |
| 🚀  | [HTMX](https://htmx.org/)                   | Server-driven interactivity  |

### Tooling

|     | Tool                                                                              | Purpose                     |
| --- | --------------------------------------------------------------------------------- | --------------------------- |
| 📦  | [uv](https://docs.astral.sh/uv/)                                                  | Python package manager      |
| 🔍  | [Ruff](https://docs.astral.sh/ruff/)                                              | Python linter and formatter |
| 🧪  | [pytest](https://pytest.org/) + [factory-boy](https://factoryboy.readthedocs.io/) | Testing                     |
| 🧹  | [djLint](https://www.djlint.com/)                                                 | HTML/template linter        |

---

## 📋 Requirements

- 🐍 Python 3.14
- 🟢 Node.js ≥ 24
- 🐘 PostgreSQL
- 🔴 Redis

---

## 🚀 Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/DenPaz/sono
cd sono
```

### 2. Set up environment variables

```bash
cp .env.example .env
# Edit .env and fill in at minimum DATABASE_URL and REDIS_URL
```

> `REDIS_URL` defaults to `redis://localhost:6379/0` if not set.

### 3. First-time setup

```bash
make init
```

> Runs: Python deps → npm deps → JS/CSS build → DB migrations → seed data.

### 4. Start the development servers

```bash
make dev
```

> Django → `http://localhost:8000` · Vite → `http://localhost:5173`

---

## ⚙️ Common Commands

| Command             | Description                                       |
| ------------------- | ------------------------------------------------- |
| `make dev`          | 🖥️ Start Django + Vite dev servers                |
| `make dev-fresh`    | 🔄 Full DB reset + seed, then start dev           |
| `make django`       | 🐍 Start Django server only                       |
| `make migrate`      | 🗄️ Apply pending database migrations              |
| `make migrations`   | 📝 Create new migrations                          |
| `make fresh`        | 🔄 Drop DB, re-migrate, and re-seed               |
| `make seed`         | 🌱 Populate DB with test data                     |
| `make test`         | 🧪 Run the test suite                             |
| `make format`       | 🎨 Format Tailwind classes, templates, and Python |
| `make lint`         | 🔍 Lint Python and templates                      |
| `make translations` | 🌐 Extract and compile i18n strings               |
| `make shell`        | 🐚 Open the Django shell                          |

> Run `make help` to see all available commands.

---

## 🔑 Test Credentials

After running `make seed`, the following accounts are available:

| Email                  | Password | Role         |
| ---------------------- | -------- | ------------ |
| `dppazlopez@gmail.com` | `12345`  | 👑 Superuser |
| `alissonpef@gmail.com` | `12345`  | 👑 Superuser |

> 1,000 regular test users are also created with password `12345`.

---

## 📁 Project Structure

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

---

## 📄 License

MIT © 2026 [Dennis Paz](mailto:dppazlopez@gmail.com)
