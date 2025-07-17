# AI.CLI Tests

This directory contains the test suite for the AI.CLI tool.

## Test Structure

- `unit/`: Unit tests for individual components
- `integration/`: Integration tests for the complete system
  - `fixtures/`: Test data and configuration files
  - `projects/`: Sample projects for testing

## Running Tests

### Prerequisites

- Docker
- Docker Compose

### Running in Container (Recommended)

1. Build and start the test container:
   ```bash
   docker-compose -f docker-compose.test.yml up --build
   ```

2. For interactive development:
   ```bash
   docker-compose -f docker-compose.test.yml run --rm dev
   ```
   This will drop you into a shell in the container where you can run tests manually.

### Running Specific Tests

To run a specific test file or test case:

```bash
# Run all tests
pytest

# Run a specific test file
pytest tests/integration/test_container_setup.py

# Run a specific test case
pytest tests/integration/test_container_setup.py::test_environment_variables
```

## Test Environment

The test environment includes the following mock tools:

- `q-cli`: Mock Q CLI tool
- `gemini`: Mock Gemini tool
- `windsurf`: Mock Windsurf tool
- `cursor`: Mock Cursor tool

Each tool is available in the container's PATH and has a corresponding configuration directory in `~/.config/`.

## Writing Tests

### Unit Tests

Unit tests should be placed in the `tests/unit/` directory and follow the naming convention `test_*.py`.

### Integration Tests

Integration tests should be placed in the `tests/integration/` directory and test the interaction between components.

### Fixtures

Common test data and configuration should be placed in the `tests/integration/fixtures/` directory.

## Debugging Tests

To debug tests in the container:

1. Start the development container:
   ```bash
   docker-compose -f docker-compose.test.yml run --rm dev
   ```

2. Run tests with pdb:
   ```bash
   pytest --pdb
   ```

## Test Coverage

To generate a coverage report:

```bash
pytest --cov=ai_cli tests/
```

This will generate a coverage report in the terminal and an HTML report in the `htmlcov/` directory.
