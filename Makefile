.PHONY: help uv-sync npm-install npm-build pre-commit-install setup migrations migrate populate-db reset-db db db-fresh clean dev dev-fresh test test-fresh translations tailwhip djlint-format djlint-lint ruff-format ruff-lint prettier-format format lint

.DEFAULT_GOAL := help

help:
	@echo ""
	@echo "  Sono — Development Makefile"
	@echo ""
	@grep -hE '^[a-zA-Z0-9_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'
	@echo ""

all: setup db dev ## Set up the development environment, initialize the database, and start development servers

uv-sync: ## Install Python dependencies
	@echo ""
	@echo "Installing Python dependencies..."
	@uv sync

npm-install: ## Install npm dependencies
	@echo ""
	@echo "Installing npm dependencies..."
	@npm install

npm-build: ## Build frontend assets
	@echo ""
	@echo "Building frontend assets..."
	@npm run build

pre-commit-install: ## Install pre-commit hooks
	@echo ""
	@echo "Installing pre-commit hooks..."
	@uv run pre-commit install

setup: uv-sync npm-install npm-build pre-commit-install ## Set up the development environment
	@echo ""
	@echo ""
	@printf "\033[32m✓ Setup complete\033[0m — run \033[36mmake db\033[0m to initialize the database\n"
	@echo ""

migrations: ## Create new migrations
	@echo ""
	@echo "Creating new migrations..."
	@uv run manage.py makemigrations

migrate: ## Apply pending migrations
	@echo ""
	@echo "Applying pending migrations..."
	@uv run manage.py migrate

populate-db: ## Populate the database with test data
	@echo ""
	@echo "Populating the database with test data..."
	@uv run manage.py update_site
	@uv run manage.py create_test_admins
	@uv run manage.py create_test_specialists --reset
	@uv run manage.py create_test_parents --reset
	@uv run manage.py create_test_patients --reset

reset-db: ## Drop and recreate the database
	@echo ""
	@echo "Resetting the database..."
	@uv run manage.py reset_db --noinput

db: migrate populate-db ## Initialize the database
	@echo ""
	@printf "\033[32m✓ Database initialized\033[0m — run \033[36mmake dev\033[0m to start the development servers\n"

db-fresh: reset-db migrate populate-db ## Reset and initialize the database
	@echo ""
	@printf "\033[32m✓ Database reset and initialized\033[0m — run \033[36mmake dev\033[0m to start the development servers\n"

clean: ## Clear cache and compiled Python files
	@echo ""
	@echo "Clearing cache and compiled Python files..."
	@uv run manage.py clear_cache
	@find . -not -path './.venv/*' -name '*.pyc' -delete
	@find . -not -path './.venv/*' -name '__pycache__' -type d -exec rm -rf {} + 2>/dev/null || true

dev: ## Start development servers
	@./script.sh

dev-fresh: db-fresh dev ## Start development servers with a fresh database

test: ## Run tests (use ARGS="..." to pass extra pytest flags)
	@echo ""
	@echo "Running tests..."
	@uv run pytest ${ARGS}

test-fresh: ## Run tests with a fresh database (use ARGS="..." to pass extra pytest flags)
	@echo ""
	@echo "Running tests with a fresh database..."
	@uv run pytest --create-db ${ARGS}

shell: ## Open Django shell
	@echo ""
	@echo "Opening Django shell..."
	@uv run manage.py shell

translations: ## Extract and compile translation strings
	@echo ""
	@echo "Extracting and compiling translation strings..."
	@uv run manage.py makemessages --all --ignore node_modules --ignore .venv
	@uv run manage.py makemessages -d djangojs --all --ignore node_modules --ignore .venv
	@uv run manage.py compilemessages --ignore .venv

tailwhip: ## Sort Tailwind CSS classes with Tailwhip
	@echo ""
	@echo "Sorting Tailwind CSS classes with Tailwhip..."
	@uv run tailwhip . --write

djlint-format: ## Format Django templates with djlint
	@echo ""
	@echo "Formatting Django templates with djlint..."
	@uv run djlint templates/ --reformat

djlint-lint: ## Lint Django templates with djlint
	@echo ""
	@echo "Linting Django templates with djlint..."
	@uv run djlint templates/ --lint

ruff-format: ## Format Python code with Ruff
	@echo ""
	@echo "Formatting Python code with Ruff..."
	@uv run ruff format .

ruff-lint: ## Lint Python code with Ruff
	@echo ""
	@echo "Linting Python code with Ruff..."
	@uv run ruff check --fix .

prettier-format: ## Format CSS/JS/JSON/YAML/Markdown files with Prettier
	@echo ""
	@echo "Formatting CSS/JS/JSON/YAML/Markdown files with Prettier..."
	@npx prettier --write "**/*.{css,js,mjs,json,jsonc,yaml,yml,md,markdown}" --ignore-path .gitignore

format: prettier-format djlint-format ruff-format tailwhip ## Format all code
	@echo ""
	@printf "\033[32m✓ Code formatted\033[0m\n"

lint: ruff-lint djlint-lint ## Lint all code
	@echo ""
	@printf "\033[32m✓ Code linted\033[0m\n"
