.venv/bin/activate:
	@echo "Creating .venv directory"
	@python -m venv .venv

.PHONY: install-tools
install-tools:
	@pip install ruff
	@pip install pre-commit

.PHONY: setup
setup:
	$(MAKE) .venv/bin/activate
	$(MAKE) install-tools

.PHONY: lint
lint:
	@ruff check .

.PHONY: format
format:
# force ruff to fix isort (import sorting) errors in all files
	@ruff check --select I --fix .
# do ruff style formatting
	@ruff format

.PHONY: clean
clean:
	@echo "Cleaning up cache files, test artifacts..."
	@find . -type d -name "__pycache__" -exec rm -rf {} +
	@rm -rf artifacts/
	$(MAKE) clean-frontend
	@echo "Cleanup done."

.PHONY: fastapi-run
fastapi-run:
	@uvicorn fastapi_app.main:app --host 0.0.0.0 --port 8001 --reload

.PHONY: fastapi-test
fastapi-test:
	@python -m unittest discover -s tests_fastapi -p 'test_*.py'

.PHONY: api-parity-practitioner
api-parity-practitioner:
	@python -m tools.api_parity.runner \
		--corpus tools/api_parity/corpus/practitioner.yaml \
		--django-base-url http://localhost:8000 \
		--fastapi-base-url http://localhost:8001

.PHONY: api-parity-practitioner-role
api-parity-practitioner-role:
	@python -m tools.api_parity.runner \
		--corpus tools/api_parity/corpus/practitioner_role.yaml \
		--django-base-url http://localhost:8000 \
		--fastapi-base-url http://localhost:8001

.PHONY: api-parity-organization-affiliation
api-parity-organization-affiliation:
	@python -m tools.api_parity.runner \
		--corpus tools/api_parity/corpus/organization_affiliation.yaml \
		--django-base-url http://localhost:8000 \
		--fastapi-base-url http://localhost:8001

.PHONY: api-parity-all
api-parity-all:
	@python -m tools.api_parity.suite \
		--django-base-url http://localhost:8000 \
		--fastapi-base-url http://localhost:8001

.PHONY: api-parity-organization
api-parity-organization:
	@python -m tools.api_parity.runner \
		--corpus tools/api_parity/corpus/organization.yaml \
		--django-base-url http://localhost:8000 \
		--fastapi-base-url http://localhost:8001

.PHONY: api-parity-location
api-parity-location:
	@python -m tools.api_parity.runner \
		--corpus tools/api_parity/corpus/location.yaml \
		--django-base-url http://localhost:8000 \
		--fastapi-base-url http://localhost:8001

.PHONY: api-parity-endpoint
api-parity-endpoint:
	@python -m tools.api_parity.runner \
		--corpus tools/api_parity/corpus/endpoint.yaml \
		--django-base-url http://localhost:8000 \
		--fastapi-base-url http://localhost:8001
