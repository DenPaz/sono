.PHONY: help setup-env uv-sync npm-install-deps init \
        migrate migrations reset-db seed fresh \
        dev dev-fresh django shell manage clean \
        test translations \
        npm-install npm-uninstall npm-build npm-dev \
        ruff-format djlint-format tailwhip format \
        ruff-lint djlint-lint lint \
        uv

.DEFAULT_GOAL := help

help:
	@echo ""
	@echo "  🎵 Sono — Development Makefile"
	@echo ""
	@grep -hE '^[a-zA-Z0-9_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "     \033[36m%-20s\033[0m %s\n", $$1, $$2}'
	@echo ""

# ============================================================
#  Setup
# ============================================================
uv-sync: ## Install Python dependencies
	@echo "  📦 Installing Python dependencies..."
	@uv sync

npm-install-deps: ## Install all npm dependencies
	@echo "  📦 Installing npm dependencies..."
	@npm install

init: uv-sync npm-install-deps npm-build migrate seed ## Full first-time setup
	@echo ""
	@echo "  ✅ Project is ready — run 'make dev' to start."
	@echo ""

# ============================================================
#  Database
# ============================================================
migrations: ## Create new migrations
	@echo "  🗄️  Creating migrations..."
	@uv run manage.py makemigrations

migrate: ## Run pending migrations
	@echo "  🗄️  Running migrations..."
	@uv run manage.py migrate

reset-db: ## Drop and recreate the database
	@echo "  🗄️  Resetting database..."
	@uv run manage.py reset_db --noinput
	@echo "  ✅ Database reset."

seed: ## Populate database with test data
	@echo "  🌱 Seeding database..."
	@uv run manage.py update_site
	@uv run manage.py create_test_superusers
	@uv run manage.py create_test_users
	@echo "  ✅ Test data seeded."

fresh: reset-db migrate seed ## reset-db + migrate + seed
	@echo "  ✅ Fresh database ready."

# ============================================================
#  Development
# ============================================================
dev: clean ## Start Django + Vite dev servers
	@./script.sh

dev-fresh: fresh dev ## fresh + dev (full reset before starting)

django: ## Start Django server only
	@uv run manage.py runserver

shell: ## Open Django shell
	@uv run manage.py shell

manage: ## Run any manage.py command. E.g. make manage ARGS='createsuperuser'
	@uv run manage.py ${ARGS}

clean: ## Remove .pyc files, __pycache__ and Django caches
	@echo "  🧹 Cleaning caches and compiled files..."
	@uv run manage.py clear_cache
	@find . -not -path './.venv/*' -name '*.pyc' -delete
	@find . -not -path './.venv/*' -name '__pycache__' -type d -exec rm -rf {} + 2>/dev/null || true
	@echo "  ✅ Clean."

# ============================================================
#  Testing
# ============================================================
test: ## Run test suite. E.g. make test ARGS='-x'
	@echo "  🧪 Running tests..."
	@uv run pytest ${ARGS}

# ============================================================
#  i18n
# ============================================================
translations: ## Extract and compile translation strings
	@echo "  🌐 Extracting and compiling translations..."
	@uv run manage.py makemessages --all --ignore node_modules --ignore venv --ignore .venv
	@uv run manage.py makemessages -d djangojs --all --ignore node_modules --ignore venv --ignore .venv
	@uv run manage.py compilemessages --ignore venv --ignore .venv
	@echo "  ✅ Translations compiled."

# ============================================================
#  npm
# ============================================================
npm-build: ## Production JS/CSS build
	@echo "  🎨 Building frontend assets..."
	@npm run build

npm-dev: ## Start Vite dev server only
	@npm run dev

npm-install: ## Install an npm package. E.g. make npm-install htmx.org
	@npm install $(filter-out $@,$(MAKECMDGOALS))

npm-uninstall: ## Remove an npm package. E.g. make npm-uninstall htmx.org
	@npm uninstall $(filter-out $@,$(MAKECMDGOALS))

# ============================================================
#  Formatting
# ============================================================
ruff-format: ## Format Python code with Ruff
	@echo "  🐍 Formatting Python code..."
	@uv run ruff format .

ruff-lint: ## Lint Python code with Ruff
	@echo "  🐍 Linting Python code..."
	@uv run ruff check --fix .

djlint-format: ## Format Django templates with djLint
	@echo "  🎨 Formatting templates..."
	@uv run djlint templates/ --reformat

djlint-lint: ## Lint Django templates with djLint
	@echo "  🎨 Linting templates..."
	@uv run djlint templates/ --lint

tailwhip: ## Sort Tailwind CSS classes in templates and CSS files
	@echo "  🌀 Sorting Tailwind classes..."
	@uv run tailwhip "templates/**/*.html" "static/css/**/*.css" --write

format: tailwhip djlint-format ruff-format ## Format everything (Tailwind classes, templates, Python)
	@echo "  ✅ Code formatted."

lint: ruff-lint djlint-lint ## Lint everything (Python and templates)
	@echo "  ✅ Code linted."

# ============================================================
#  uv passthrough
# ============================================================
uv: ## Run a uv command. E.g. make uv add requests
	@uv $(filter-out $@,$(MAKECMDGOALS))

%:
	@:
