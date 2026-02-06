# Makefile

# set NPD_DEVELOPMENT to "True" in your shell to skip dangerous action
# confirmation steps
NPD_DEVELOPMENT ?= no

# default target
.DEFAULT_GOAL := help

help:
	@echo "Available commands:"
	@echo ""
	@echo "  build          Build all Docker containers for the application"
	@echo "  setup          Set up development environment (build + create-db + migrate)"
	@echo "  install-tools  Install development support tools"
	@echo "  update         Update development environment"
	@echo ""
	@echo "  create-db      Start postgres, create and populate a development DB"
	@echo "  migrate        Apply pending migrations to the development database"
	@echo ""
	@echo "  up             Start the NPD application at http://localhost:8000"
	@echo "  down           Stop all running docker compose services"
	@echo ""
	@echo "  test           Run the full frontend and backend test suites with DB setup"
	@echo "  test-setup     Set up test database (drop/create test DB + run test migrations)"
	@echo "  test-backend   Run the backend test suite without rerunning database setup"
	@echo "                 Use ARGS=... to pass arguments"
	@echo "  test-frontend  Run the frontend test suite"
	@echo "                 Use ARGS=... to pass arguments"
	@echo "  test-server    Start a test server for e2e testing with Playwright"
	@echo "  playwright     Run the playwright e2e test suite (on host)"
	@echo ""
	@echo "  clean          Remove cache files, test artifacts, and transient frontend assets"
	@echo ""
	@echo "  lint           Check code against the appropriate linter (ruff or eslint)"
	@echo "  format         Format code with the approrpriate formatter (ruff or prettier)"
	@echo ""
	@echo "  createsuperuser  Interactively set up a Django superuser account."
	@echo "                   Pass env vars to run automatically:"
	@echo "                     DJANGO_SUPERUSER_EMAIL"
	@echo "                     DJANGO_SUPERUSER_USERNAME"
	@echo "                     DJANGO_SUPERUSER_PASSWORD"
	@echo ""
	@echo "  drop-db      \033[31m[DANGEROUS]\033[0m Drop the development database"
	@echo "  reset-db     \033[31m[DANGEROUS]\033[0m Drop and fully recreate the development database"
	@echo ""
	@echo "  help         Show this help message"
	@echo ""
	@echo "Common workflows:"
	@echo "  First time setup:   make setup && make install-tools && make up"
	@echo "  Daily development:  git pull && make update && make up"
	@echo "  Before committing:  make test && make lint"
	@echo "  Run isolated tests: make test"
	@echo "  Run e2e tests:      make test-server &; make playwright"
	@echo "  Run some tests:     make test-backend ARGS=npdfhir.tests"
	@echo "  Run one test:       make test-backend ARGS=provider_directory.tests.test_frontend_settings.TestFeatureFlags.test_returns_flags_json"
	@echo "  Clean shutdown:     make down && make clean"

.PHONY: build
build:
	@docker compose build

.PHONY: install-tools
install-tools:
	@echo "Setting up local python virtual environment"
	@$(MAKE) -C backend .venv/bin/activate
	@source backend/.venv/bin/activate; \
		echo "Setting up local development tools using $(shell which pip)"; \
		$(MAKE) -C backend install-tools; \
		pre-commit install
	@echo "Setting up playwright on host"
	@cd playwright; \
		npm install; \
		npx playwright install --with-deps chromium;


.PHONY: lint
lint:
	@echo "\033[2m[ lint backend ]\033[0m"
	@$(MAKE) -C backend lint
	@echo "\033[2m[ lint frontend ]\033[0m"
	@bin/npr npm run lint

.PHONY: format
format:
	@echo "\033[2m[ format backend ]\033[0m"
	@$(MAKE) -C backend format
	@echo "\033[2m[ format frontend ]\033[0m"
	@bin/npr npm run format

###
## Database management
###

.PHONY: drop-db
drop-db:
ifneq ($(NPD_DEVELOPMENT), True)
	@printf "Are you sure you want to drop your local database? [y/N] " && read ans && ( [[ "$${ans:-N}" == y ]] || ( echo "cancelling changes" && exit 1 ) )
endif
	@echo "Dropping development database..."
	@docker compose up -d db
	@docker compose run --rm db sh -c 'echo "dropping $$POSTGRES_DB"; PGPASSWORD=$$POSTGRES_PASSWORD psql -h db -U $$POSTGRES_USER -d postgres -c "DROP DATABASE IF EXISTS $$POSTGRES_DB" || echo "failed to drop $$POSTGRES_DB"'

.PHONY: create-db
create-db:
	@echo "Creating development database..."
	@docker compose up -d db
	# create development database only if it doesn't already exist
	@docker compose run --rm db sh -c 'echo "creating $$POSTGRES_DB"; PGPASSWORD=$$POSTGRES_PASSWORD psql -h db -U $$POSTGRES_USER -d postgres -c "CREATE DATABASE $$POSTGRES_DB" || echo "$$POSTGRES_DB already exists"'
	
# run all flyway migrations for the development environment
.PHONY: migrate
migrate:
	@echo "Migrating the development database..."
	@docker compose up -d db
	@bin/npr migrate

# drop, create, and then run all flyway migrations for the development environment
.PHONY: reset-db
reset-db:
	@echo "Resetting the development database..."
	@docker compose down db
	@$(MAKE) drop-db
	@$(MAKE) create-db
	@$(MAKE) migrate

###
# Frontend asset management
###

.PHONY: clean-frontend
clean-frontend:
	@echo "Removing frontend assets from backend/provider_directory/static"
	@rm -rf backend/provider_directory/static/*
	@rm -rf backend/provider_directory/static/.vite

# only rebuild frontend assets if they don't already exist
backend/provider_directory/static/.vite/manifest.json:
	@echo "Building frontend assets with VITE_API_BASE_URL=$(VITE_API_BASE_URL)"
	@bin/npr npm install
	@bin/npr -e VITE_API_BASE_URL=$(VITE_API_BASE_URL) npm run build

.PHONY: build-frontend-assets
build-frontend-assets: clean-frontend
	export VITE_API_BASE_URL=http://localhost:8000; \
		$(MAKE) backend/provider_directory/static/.vite/manifest.json

# build frontend assets and ensure the backend application is running
.PHONY: up
up:
	@echo "Staring django-web and web services..."
	@docker compose up -d django-web web
	@echo "Backend is running"
	@echo "  site: http://localhost:8000/"
	@echo "  docs: http://localhost:8000/fhir/docs/"

.PHONY: down
down:
	@echo "Shutting down all docker compose services..."
	@docker compose down

.PHONY: test-setup
test-setup:
	@echo "Setting up test database..."
	@docker compose -f compose.test.yml up -d --wait db
# drop, create, and migrate test database
	@docker compose -f compose.test.yml exec db sh -c 'echo "DROP   $$POSTGRES_DB"; PGPASSWORD=$$POSTGRES_PASSWORD psql -q -h localhost -U "$$POSTGRES_USER" -d postgres -c "DROP DATABASE IF EXISTS $$POSTGRES_DB"'
	@docker compose -f compose.test.yml exec db sh -c 'echo "CREATE $$POSTGRES_DB"; PGPASSWORD=$$POSTGRES_PASSWORD psql -q -h localhost -U "$$POSTGRES_USER" -d postgres -c "CREATE DATABASE $$POSTGRES_DB"'
	@bin/npr -t migrate

.PHONY: test-backend
test-backend:
	@echo "Running backend tests..."
	@bin/npr -t python manage.py test $(ARGS)

.PHONY: test-frontend
test-frontend:
	@echo "Running frontend tests..."
	@bin/npr npm test $(ARGS)

.PHONY: test
test: test-setup
	@$(MAKE) test-backend
	@$(MAKE) test-frontend

.PHONY: playwright
playwright:
	@cd playwright; \
		npx playwright test

# clean up test artifacts
.PHONY: clean
clean: clean-frontend
	@$(MAKE) -C backend clean

###
# Data seeding utilities
###

.PHONY: createsuperuser
createsuperuser:
ifeq ($(and $(DJANGO_SUPERUSER_EMAIL),$(DJANGO_SUPERUSER_USERNAME),$(DJANGO_SUPERUSER_PASSWORD)),)
	@bin/npr python manage.py createsuperuser
else
	@bin/npr \
		-e DJANGO_SUPERUSER_EMAIL="$(DJANGO_SUPERUSER_EMAIL)" \
		-e DJANGO_SUPERUSER_USERNAME="$(DJANGO_SUPERUSER_USERNAME)" \
		-e DJANGO_SUPERUSER_PASSWORD="$(DJANGO_SUPERUSER_PASSWORD)" \
		python manage.py createsuperuser --no-input
endif

.PHONY: seed-users
seed-users:
	@bin/npr \
		-e DJANGO_SUPERUSER_EMAIL="npd.admin@cms.hhs.gov" \
		-e DJANGO_SUPERUSER_USERNAME="npdadmin" \
		-e DJANGO_SUPERUSER_PASSWORD="password123" \
		python manage.py createsuperuser --no-input

##
# end-to-end test support
##

.PHONY: build-frontend-test-assets
build-frontend-test-assets: clean-frontend
	export VITE_API_BASE_URL=http://localhost:8008; \
		$(MAKE) backend/provider_directory/static/.vite/manifest.json

.PHONY: watch-frontend-test-assets
watch-frontend-test-assets:
	bin/npr -e VITE_API_BASE_URL=http://localhost:8008 npm run watch

.PHONY: test-system-setup
test-system-setup: test-setup
	bin/npr --test python manage.py seeduser
	bin/npr --test python manage.py seedsystem

.PHONY: test-server
test-server: test-system-setup build-frontend-test-assets
	bin/npr --test --publish 8008:8008 python manage.py runserver 0.0.0.0:8008

###
# whole project concerns
###

# prepare the local working copy for NPD development
.PHONY: setup
setup: build create-db migrate
	@$(MAKE) -C backend setup

# bring local working copy up to date
.PHONY: update
update: build migrate build-frontend-assets