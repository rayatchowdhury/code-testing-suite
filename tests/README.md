# Testing Guide

This document describes how to run and contribute to the test suite for Code Testing Suite.

## Running Tests

### Prerequisites
```bash
pip install -r requirements.txt
```

### Run All Tests
```bash
python -m pytest
```

### Run Specific Test Categories
```bash
# Unit tests only
python -m pytest -m unit

# Integration tests only  
python -m pytest -m integration

# Tests in specific module
python -m pytest tests/test_utils/

# Specific test file
python -m pytest tests/test_utils/test_constants.py

# Specific test
python -m pytest tests/test_utils/test_constants.py::TestPathConstants::test_project_root_exists
```

### Test Options
```bash
# Verbose output
python -m pytest -v

# Stop on first failure
python -m pytest -x

# Run with coverage
python -m pytest --cov=.

# Short traceback format
python -m pytest --tb=short
```

## Test Structure

```
tests/
├── __init__.py              # Test package initialization
├── conftest.py              # Shared fixtures and configuration
├── test_utils/              # Tests for utility modules
│   ├── test_constants.py    # Path constants tests
│   └── test_ai_config.py    # AI configuration tests
├── test_views/              # Tests for UI components
├── test_tools/              # Tests for compilation/AI tools
└── test_integration/        # Integration tests
```

## Test Markers

Tests are organized with markers for easy filtering:

- `@pytest.mark.unit` - Fast, isolated unit tests
- `@pytest.mark.integration` - Tests that require multiple components
- `@pytest.mark.slow` - Tests that take longer to run  
- `@pytest.mark.ui` - Tests that require UI components

## Writing Tests

### Test File Naming
- Test files: `test_*.py`
- Test classes: `Test*`
- Test functions: `test_*`

### Example Test Structure
```python
import pytest
from unittest.mock import patch

class TestMyModule:
    @pytest.mark.unit
    def test_basic_functionality(self):
        """Test basic functionality with clear docstring."""
        # Arrange
        # Act  
        # Assert
        
    @pytest.mark.unit
    def test_edge_case_with_fixture(self, temp_dir):
        """Test using shared fixture."""
        # Test implementation
        
    @pytest.mark.integration
    def test_module_integration(self):
        """Test interaction between modules."""
        # Integration test implementation
```

### Available Fixtures

- `temp_dir` - Temporary directory for file operations
- `mock_user_data_dir` - Mock user data directory
- `mock_config_file` - Mock configuration file
- `mock_qapplication` - Mock Qt application for GUI tests
- `sample_code_files` - Sample code files for testing

## Current Test Coverage

### Utils Module
- ✅ `constants.py` - 13 tests (path constants and utilities)
- ✅ `ai_config.py` - 17 tests (AI configuration and validation)

### Total: 30 tests passing

## Adding New Tests

1. Create test file in appropriate directory
2. Follow naming conventions
3. Use appropriate markers
4. Include docstrings
5. Use fixtures for common setup
6. Run tests to verify they pass

## CI Integration

Tests will run automatically in CI with:
- Python 3.9, 3.10, 3.11 matrix
- Coverage reporting
- Linting with pylint

Example CI command:
```bash
python -m pytest --cov=. --cov-report=xml --tb=short
```
