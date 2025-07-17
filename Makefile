.PHONY: help install test test-unit test-integration test-container build-container run-container dev-shell clean format lint check-format

# Variables
DOCKER_COMPOSE := docker compose -f docker-compose.test.yml
PYTHON := python3
PIP := pip3

# Help target
help:
	@echo "Available targets:"
	@echo "  install       - Install development dependencies"
	@echo "  test          - Run all tests"
	@echo "  test-unit     - Run unit tests"
	@echo "  test-integration - Run integration tests"
	@echo "  test-container - Run tests in container"
	@echo "  build-container - Build test container"
	@echo "  run-container - Run test container"
	@echo "  dev-shell     - Start a shell in the dev container"
	@echo "  clean         - Remove temporary files"
	@echo "  format        - Format code"
	@echo "  lint          - Run linters"
	@echo "  check-format  - Check code formatting"

# Install development dependencies
install:
	$(PIP) install -e .[test]
	$(PIP) install black isort flake8 mypy

# Run all tests
test: test-unit test-integration

# Run unit tests
test-unit:
	$(PYTHON) -m pytest tests/unit/ -v

# Run integration tests
test-integration:
	$(PYTHON) -m pytest tests/integration/ -v

# Run tests in container
test-container:
	$(DOCKER_COMPOSE) up --build --exit-code-from test

# Build test container
build-container:
	$(DOCKER_COMPOSE) build

# Run test container
run-container:
	$(DOCKER_COMPOSE) up

# Start a shell in the dev container
dev-shell:
	$(DOCKER_COMPOSE) run --rm dev

# Clean up
clean:
	find . -type d -name "__pycache__" -exec rm -r {} +
	find . -type d -name ".pytest_cache" -exec rm -r {} +
	find . -type f -name "*.py[co]" -delete
	find . -type d -name ".mypy_cache" -exec rm -r {} +
	rm -rf .coverage htmlcov/

# Format code
format:
	black ai_cli/ tests/
	isort ai_cli/ tests/

# Run linters
lint:
	flake8 ai_cli/ tests/
	mypy ai_cli/ tests/

# Check code formatting
check-format:
	black --check ai_cli/ tests/
	isort --check-only ai_cli/ tests/
