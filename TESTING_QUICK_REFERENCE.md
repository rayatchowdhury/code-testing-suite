# Testing Quick Reference

**Code Testing Suite - pytest Quick Reference Guide**

---

## 🚀 Quick Start

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Skip slow tests
pytest -m "not slow"
```

---

## 📋 Common Commands

### Basic Test Execution

```bash
# Run all tests with verbose output
pytest -v

# Run specific test file
pytest tests/unit/core/test_base_runner.py

# Run specific test class
pytest tests/unit/core/test_base_runner.py::TestBaseRunner

# Run specific test method
pytest tests/unit/core/test_base_runner.py::TestBaseRunner::test_init

# Run tests matching name pattern
pytest -k "database"
pytest -k "test_database or test_connection"
pytest -k "not slow"
```

### Test Selection by Markers

```bash
# Run unit tests only
pytest -m unit

# Run integration tests only
pytest -m integration

# Run E2E tests only
pytest -m e2e

# Run GUI tests
pytest -m gui

# Run database tests
pytest -m database

# Combine markers (AND)
pytest -m "unit and database"

# Combine markers (OR)
pytest -m "unit or integration"

# Exclude markers
pytest -m "not slow"
pytest -m "not (slow or gui)"
```

### Output Control

```bash
# Verbose output with test names
pytest -v

# Very verbose (show individual assertions)
pytest -vv

# Quiet mode (minimal output)
pytest -q

# Show captured output even for passing tests
pytest -s

# Show local variables on failure
pytest -l

# Disable output capture
pytest --capture=no

# Short traceback
pytest --tb=short

# No traceback
pytest --tb=no

# Line-only traceback
pytest --tb=line
```

### Test Execution Control

```bash
# Stop on first failure
pytest -x

# Stop after N failures
pytest --maxfail=3

# Run last failed tests
pytest --lf
pytest --last-failed

# Run failed tests first, then others
pytest --ff
pytest --failed-first

# Run specific number of tests
pytest --count=5 tests/unit/

# Parallel execution (requires pytest-xdist)
pytest -n auto          # Auto-detect CPU cores
pytest -n 4             # Use 4 workers
```

---

## 📊 Coverage Commands

### Generate Coverage Reports

```bash
# HTML report (interactive)
pytest --cov=src --cov-report=html
start htmlcov/index.html  # Open in browser (Windows)
open htmlcov/index.html   # Open in browser (macOS/Linux)

# Terminal report with missing lines
pytest --cov=src --cov-report=term-missing

# XML report (for CI/CD)
pytest --cov=src --cov-report=xml

# JSON report (for analysis)
pytest --cov=src --cov-report=json

# Multiple reports at once
pytest --cov=src --cov-report=html --cov-report=term-missing --cov-report=xml
```

### Coverage Analysis

```bash
# Show only files with missing coverage
pytest --cov=src --cov-report=term-missing:skip-covered

# Fail if coverage below threshold
pytest --cov=src --cov-fail-under=70

# Coverage for specific module
pytest --cov=src.app.core --cov-report=term-missing

# Coverage with branch checking
pytest --cov=src --cov-branch
```

---

## 🔍 Debugging Tests

### Running in Debug Mode

```bash
# Drop into debugger on failure
pytest --pdb

# Drop into debugger at start of each test
pytest --trace

# Show local variables on failure
pytest -l

# Very verbose with full diff
pytest -vv

# Show print statements
pytest -s

# Longer timeout for debugging
pytest --timeout=1000
```

### Inspecting Test Discovery

```bash
# List all discovered tests (don't run)
pytest --collect-only

# Show test collection tree
pytest --collect-only -q

# Show fixtures available for a test
pytest --fixtures tests/unit/core/test_base_runner.py
```

### Filtering and Selection

```bash
# Run tests modified recently
pytest --lf

# Run tests in specific directory
pytest tests/unit/

# Exclude specific directory
pytest --ignore=tests/integration/

# Run tests from file list
pytest --file-list=test_files.txt
```

---

## ⚡ Performance

### Show Slowest Tests

```bash
# Show 10 slowest tests
pytest --durations=10

# Show all test durations
pytest --durations=0

# Show slowest setups/teardowns
pytest --durations-min=1.0
```

### Parallel Execution

```bash
# Auto-detect cores and run in parallel
pytest -n auto

# Use specific number of workers
pytest -n 4

# Distributed testing with load balancing
pytest -n auto --dist loadscope

# Parallel with live output
pytest -n auto -v
```

---

## 🎯 Running Specific Test Types

### By Test Layer

```bash
# Unit tests (fast, isolated)
pytest tests/unit/ -v

# Integration tests (multi-component)
pytest tests/integration/ -v

# E2E tests (full application)
pytest tests/e2e/ -v

# Performance tests
pytest tests/performance/ -v -m benchmark
```

### By Component

```bash
# Core tools tests
pytest tests/unit/core/ -v

# Database tests
pytest tests/unit/database/ -v -m database

# Presentation layer tests
pytest tests/unit/presentation/ -v -m gui

# Shared utilities tests
pytest tests/unit/shared/ -v
```

### By Feature

```bash
# Compilation tests
pytest -m compilation -v

# GUI tests (headless)
pytest -m gui -v

# Slow tests (long-running)
pytest -m slow -v

# AI-dependent tests
pytest -m ai -v
```

---

## 📝 Fixtures Reference

### Common Fixtures

```python
# Temporary directory (auto-cleanup)
def test_example(temp_dir):
    file_path = temp_dir / "test.txt"
    # ... use temp_dir

# Temporary workspace structure
def test_example(temp_workspace):
    comparator_dir = temp_workspace / "comparator"
    # ... use temp_workspace

# Temporary database
def test_example(temp_database):
    temp_database.save_result(...)
    # ... use temp_database

# Sample code fixtures
def test_example(sample_cpp_code):
    compile_file(sample_cpp_code)

# Qt testing (pytest-qt)
def test_widget(qtbot):
    widget = MyWidget()
    qtbot.addWidget(widget)
    qtbot.mouseClick(widget.button, Qt.LeftButton)
```

### Listing Available Fixtures

```bash
# Show all fixtures
pytest --fixtures

# Show fixtures for specific test
pytest --fixtures tests/unit/core/test_base_runner.py

# Show fixture setup order
pytest --setup-show tests/unit/core/test_base_runner.py -v
```

---

## 🏗️ Writing Tests Cheatsheet

### Test Function Template

```python
import pytest

@pytest.mark.unit  # Mark test type
def test_function_name(fixture_name):
    """Brief description of what is being tested."""
    # ARRANGE - Setup
    input_data = "test"
    expected = "result"
    
    # ACT - Execute
    actual = function_under_test(input_data)
    
    # ASSERT - Verify
    assert actual == expected
```

### Common Assertions

```python
# Equality
assert x == y
assert x != y

# Identity
assert x is y
assert x is not y

# Boolean
assert x
assert not x

# Membership
assert item in collection
assert item not in collection

# Comparisons
assert x < y
assert x <= y
assert x > y
assert x >= y

# Type checking
assert isinstance(obj, MyClass)

# Exception handling
with pytest.raises(ValueError):
    function_that_should_raise()

# Exception with message
with pytest.raises(ValueError, match="invalid input"):
    function_that_should_raise()

# Warning checking
with pytest.warns(UserWarning):
    function_that_warns()

# Approximate equality (floats)
assert x == pytest.approx(3.14159, rel=1e-5)
```

### Parametrize Tests

```python
@pytest.mark.parametrize("input,expected", [
    (2, 4),
    (3, 9),
    (4, 16),
])
def test_square(input, expected):
    assert square(input) == expected

# Multiple parameters
@pytest.mark.parametrize("x,y,expected", [
    (1, 2, 3),
    (2, 3, 5),
])
def test_add(x, y, expected):
    assert add(x, y) == expected
```

### Mocking

```python
from unittest.mock import Mock, patch, MagicMock

# Mock object
mock_db = Mock()
mock_db.query.return_value = [1, 2, 3]

# Patch function
@patch('module.function')
def test_with_patch(mock_function):
    mock_function.return_value = "mocked"
    # ... test code

# Patch with context manager
def test_with_context_patch():
    with patch('module.function') as mock_func:
        mock_func.return_value = "mocked"
        # ... test code
```

---

## 🐛 Troubleshooting

### Common Issues

#### Tests Not Discovered

```bash
# Check test discovery
pytest --collect-only

# Ensure test files follow naming convention
test_*.py or *_test.py

# Ensure test functions start with test_
def test_something():
    pass
```

#### Import Errors

```bash
# Check PYTHONPATH
echo $PYTHONPATH  # Linux/macOS
echo %PYTHONPATH%  # Windows

# Run from project root
cd /path/to/project
pytest

# Check pytest.ini has pythonpath setting
pythonpath = . src
```

#### Qt GUI Errors

```bash
# Set headless mode
export QT_QPA_PLATFORM=offscreen  # Linux/macOS
set QT_QPA_PLATFORM=offscreen     # Windows

# Use qtbot fixture
def test_gui(qtbot):
    widget = MyWidget()
    qtbot.addWidget(widget)  # Proper cleanup
```

#### Coverage Not Working

```bash
# Clean old coverage data
rm .coverage
rm -rf htmlcov/

# Re-run with coverage
pytest --cov=src --cov-report=html

# Check coverage is installed
pip show pytest-cov
```

---

## 🔧 Configuration Files

### pytest.ini

```ini
[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
pythonpath = . src
addopts = --strict-markers --verbose
```

### .coveragerc

```ini
[run]
source = src
omit = */tests/*

[report]
precision = 2
show_missing = True
```

---

## 📚 Documentation Links

- [pytest Documentation](https://docs.pytest.org/)
- [pytest-cov Documentation](https://pytest-cov.readthedocs.io/)
- [pytest-qt Documentation](https://pytest-qt.readthedocs.io/)
- [Coverage.py Documentation](https://coverage.readthedocs.io/)

---

## 💡 Tips & Tricks

### Faster Test Runs

```bash
# Skip slow tests
pytest -m "not slow"

# Run in parallel
pytest -n auto

# Run only failed tests from last run
pytest --lf

# Stop on first failure
pytest -x
```

### Better Output

```bash
# Show full diff for assertions
pytest -vv

# Show print statements
pytest -s

# Show local variables
pytest -l

# Capture everything
pytest --capture=no -v
```

### CI/CD Commands

```bash
# Full test suite with all reports
pytest --cov=src \
       --cov-report=html \
       --cov-report=xml \
       --cov-report=term-missing \
       --junit-xml=test-results.xml \
       --cov-fail-under=54

# Lint and format check
black --check src/ tests/
isort --check-only src/ tests/
pylint src/ --exit-zero
```

---

**Last Updated**: October 14, 2025  
**Project**: Code Testing Suite  
**Maintainer**: Testing Team
