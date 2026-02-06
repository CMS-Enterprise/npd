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

