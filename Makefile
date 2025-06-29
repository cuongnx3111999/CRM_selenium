# Type checking
typecheck:
	mypy pages/ utils/ config/ tests/

typecheck-strict:
	mypy --strict pages/ utils/ config/ tests/

typecheck-all:
	mypy .

# Fix type issues
fix-types:
	mypy pages/ utils/ config/ tests/ --show-error-codes

# Install dev dependencies
install-dev:
	pip install -e ".[dev]"

# Run all checks
check-all: typecheck
	black --check .
	flake8 .
	pytest --collect-only

# Format and fix
format:
	black .
	isort .
