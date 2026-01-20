# Tests directory

This directory contains all test files for the Derby Names application.

## Test Structure

- `conftest.py` - Shared pytest fixtures
- `test_models.py` - SQLModel model tests
- `test_database.py` - Database operation tests
- `test_generator.py` - Name generator tests
- `test_api.py` - FastAPI endpoint tests

## Running Tests

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=. --cov-report=term-missing

# Run specific test file
uv run pytest tests/test_models.py

# Run with verbose output
uv run pytest -v
```

## Test Coverage

Current coverage: **56%**
- Models: 100%
- Database: 100%
- Generator: 67%
- API: 52%
