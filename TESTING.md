# Testing Guidelines & Best Practices

**Code Testing Suite - Comprehensive Testing Documentation**

**Last Updated**: October 13, 2025  
**Coverage**: 48% (Target: 70%)  
**Tests**: 1,666 passing, 5 skipped  
**Framework**: pytest 8.4.2 with pytest-cov, pytest-qt, pytest-mock

---

## 📋 Table of Contents

1. [Quick Start](#quick-start)
2. [Test Organization](#test-organization)
3. [Writing Tests](#writing-tests)
4. [Best Practices](#best-practices)
5. [Fixtures & Utilities](#fixtures--utilities)
6. [Running Tests](#running-tests)
7. [Coverage Guidelines](#coverage-guidelines)
8. [Common Patterns](#common-patterns)
9. [Troubleshooting](#troubleshooting)
10. [CI/CD Integration](#cicd-integration)

---

## 🚀 Quick Start

###install Dependencies

```bash
# Install test dependencies
pip install -r requirements-dev.txt

# Includes: pytest, pytest-cov, pytest-qt, pytest-mock, pytest-asyncio
```

### Run Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/unit/core/test_base_runner.py

# Run tests matching pattern
pytest -k "test_compilation"

# Open HTML coverage report
start htmlcov/index.html  # Windows
open htmlcov/index.html   # Mac/Linux
```

---

## 📁 Test Organization

### Directory Structure

```
tests/
├── conftest.py                    # Root fixtures & configuration
├── fixtures/                      # Shared test data
│   ├── database_fixtures.py      # Database test fixtures
│   └── sample_code/              # Sample source files
│
├── unit/                          # Unit tests (isolated components)
│   ├── app/                      # Application entry tests
│   ├── core/                     # Core layer tests
│   │   ├── ai/                   # AI module tests
│   │   ├── config/               # Configuration tests
│   │   └── tools/                # Tool tests
│   ├── database/                 # Database layer tests
│   ├── presentation/             # Presentation layer tests
│   │   ├── widgets/              # Widget tests
│   │   └── window_controller/   # Window management tests
│   └── shared/                   # Shared utilities tests
│
├── integration/                   # Integration tests (multi-component)
│   └── (planned for future)
│
└── e2e/                          # End-to-end tests
    └── (planned for future)
```

### File Naming Conventions

- **Test files**: `test_<module>.py` or `<module>_test.py`
- **Test classes**: `Test<ClassName>` or `Test<Feature>`
- **Test functions**: `test_<action>_<condition>_<result>`

**Examples**:
```python
# ✅ Good
tests/unit/core/test_base_runner.py
class TestBaseRunnerInitialization:
    def test_init_creates_compiler(self):
        ...

# ❌ Bad
tests/runner_tests.py
class TestRunner:
    def test_runner(self):
        ...
```

---

## ✍️ Writing Tests

### AAA Pattern (Arrange, Act, Assert)

**Always structure tests in three clear phases**:

```python
def test_user_creation():
    # Arrange: Set up test data and dependencies
    username = "testuser"
    email = "test@example.com"
    
    # Act: Perform the action being tested
    user = User(username, email)
    
    # Assert: Verify the expected outcome
    assert user.username == username
    assert user.email == email
```

### Test Naming Conventions

**Format**: `test_<action>_<condition>_<expected_result>`

```python
# ✅ Good test names (clear and descriptive)
def test_compile_all_returns_true_on_success(self):
    """Should return True when all files compile successfully."""
    ...

def test_save_file_creates_directory_if_missing(self):
    """Should create parent directory when saving file."""
    ...

def test_run_tests_raises_error_when_worker_missing(self):
    """Should raise ValueError if no worker is configured."""
    ...

# ❌ Bad test names (vague or unclear)
def test_compile(self):
    ...

def test_file(self):
    ...

def test_error(self):
    ...
```

### Docstrings

**Always include docstrings** for test classes and functions:

```python
class TestDatabaseConnection:
    """
    Test suite for DatabaseConnection singleton pattern.
    
    Tests verify singleton behavior, thread safety, and connection lifecycle.
    """
    
    def test_returns_same_instance(self):
        """Should return the same DatabaseConnection instance on multiple calls."""
        conn1 = DatabaseConnection()
        conn2 = DatabaseConnection()
        assert conn1 is conn2
```

---

## ⭐ Best Practices

### 1. One Assertion Per Test (When Possible)

```python
# ✅ Good: Focused test with one assertion
def test_file_exists_after_save(self, temp_dir):
    file_path = temp_dir / "test.txt"
    save_file(file_path, "content")
    assert file_path.exists()

def test_file_content_matches_after_save(self, temp_dir):
    file_path = temp_dir / "test.txt"
    content = "test content"
    save_file(file_path, content)
    assert file_path.read_text() == content

# ⚠️ Acceptable: Related assertions
def test_user_initialization(self):
    user = User("john", "john@example.com")
    assert user.username == "john"
    assert user.email == "john@example.com"
    assert user.is_active is True
```

### 2. Use Fixtures for Setup

```python
# ✅ Good: Use fixtures for reusable setup
@pytest.fixture
def sample_user():
    return User("testuser", "test@example.com")

def test_user_can_login(self, sample_user):
    result = sample_user.login("password123")
    assert result is True

# ❌ Bad: Duplicate setup in each test
def test_user_can_login(self):
    user = User("testuser", "test@example.com")
    result = user.login("password123")
    assert result is True

def test_user_can_logout(self):
    user = User("testuser", "test@example.com")  # Duplicate!
    ...
```

### 3. Mock External Dependencies

```python
# ✅ Good: Mock external calls
@patch('subprocess.run')
def test_compilation_executes_command(self, mock_run):
    mock_run.return_value = Mock(returncode=0)
    
    compiler = Compiler()
    result = compiler.compile("test.cpp")
    
    assert result is True
    mock_run.assert_called_once()

# ❌ Bad: Don't rely on actual external processes
def test_compilation_works(self):
    compiler = Compiler()
    result = compiler.compile("test.cpp")  # Actually runs g++!
    assert result is True
```

### 4. Test Edge Cases

```python
def test_divide_by_zero_raises_error(self):
    """Should raise ZeroDivisionError when dividing by zero."""
    calculator = Calculator()
    
    with pytest.raises(ZeroDivisionError):
        calculator.divide(10, 0)

def test_empty_list_returns_none(self):
    """Should return None when finding max of empty list."""
    result = find_max([])
    assert result is None

def test_handles_none_input_gracefully(self):
    """Should handle None input without crashing."""
    processor = DataProcessor()
    result = processor.process(None)
    assert result == []
```

### 5. Keep Tests Fast

```python
# ✅ Good: Fast unit test (<100ms)
def test_config_validates_quickly(self):
    config = Config({"timeout": 30})
    assert config.is_valid()

# ⚠️ Acceptable: Slower integration test (mark as slow)
@pytest.mark.slow
def test_full_compilation_workflow(self):
    # May take 1-5 seconds
    ...

# ❌ Bad: Unnecessarily slow
def test_config_validates(self):
    time.sleep(2)  # Don't add delays!
    config = Config({"timeout": 30})
    assert config.is_valid()
```

---

## 🔧 Fixtures & Utilities

### Built-in Fixtures

The project provides several reusable fixtures in `tests/conftest.py`:

#### Temporary Directories

```python
def test_file_operations(temp_dir):
    """temp_dir is automatically cleaned up after test."""
    file_path = temp_dir / "test.txt"
    file_path.write_text("content")
    assert file_path.exists()

def test_workspace_structure(temp_workspace):
    """temp_workspace creates nested directory structure."""
    assert (temp_workspace / "comparator" / "inputs").exists()
    assert (temp_workspace / "validator" / "outputs").exists()
```

#### Sample Code

```python
def test_cpp_compilation(sample_cpp_test, temp_dir):
    """Use predefined sample code for testing."""
    source_file = temp_dir / "test.cpp"
    source_file.write_text(sample_cpp_test)
    
    compiler = Compiler()
    result = compiler.compile(str(source_file))
    assert result is True
```

#### Mock Objects

```python
def test_database_operations(mock_database_manager):
    """Use mocked database for tests."""
    service = Service(mock_database_manager)
    service.save_data({"key": "value"})
    
    mock_database_manager.save_test_result.assert_called_once()
```

### Creating Custom Fixtures

```python
# In conftest.py or test file
@pytest.fixture
def sample_config():
    """Provide sample configuration for tests."""
    return {
        'compiler': 'g++',
        'flags': ['-O2', '-std=c++17'],
        'timeout': 30
    }

@pytest.fixture
def mock_compiler(monkeypatch):
    """Mock compiler for tests that don't need real compilation."""
    mock = Mock()
    mock.compile_all.return_value = True
    monkeypatch.setattr('src.app.core.tools.Compiler', lambda *args: mock)
    return mock
```

---

## 🏃 Running Tests

### Basic Commands

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific file
pytest tests/unit/core/test_base_runner.py

# Run specific test
pytest tests/unit/core/test_base_runner.py::TestBaseRunnerInitialization::test_init_creates_compiler

# Run tests matching pattern
pytest -k "compilation"

# Run last failed tests
pytest --lf

# Stop on first failure
pytest -x

# Show local variables on failure
pytest -l
```

### Coverage Commands

```bash
# Generate HTML coverage report
pytest --cov=src --cov-report=html

# Generate terminal coverage report
pytest --cov=src --cov-report=term-missing

# Generate XML coverage (for CI/CD)
pytest --cov=src --cov-report=xml

# Coverage for specific module
pytest --cov=src/app/core/tools --cov-report=term

# Fail if coverage below threshold
pytest --cov=src --cov-fail-under=70
```

### Marker-Based Selection

```bash
# Run only unit tests
pytest -m unit

# Run only database tests
pytest -m database

# Skip slow tests
pytest -m "not slow"

# Run unit AND database tests
pytest -m "unit or database"

# Run GUI tests only
pytest -m gui
```

### Parallel Execution

```bash
# Run tests in parallel (requires pytest-xdist)
pytest -n auto

# Run with 4 workers
pytest -n 4
```

---

## 📊 Coverage Guidelines

### Coverage Targets by Layer

| Layer | Target | Current | Priority |
|-------|--------|---------|----------|
| Core Tools | 85% | 79% | CRITICAL |
| Database | 90% | 89% | HIGH |
| Utilities | 75% | 91% | ✅ EXCEEDED |
| Presentation (Widgets) | 60% | 87% | ✅ EXCEEDED |
| Overall | 70% | 48% | **CRITICAL** |

### What to Test

✅ **DO Test**:
- Business logic and algorithms
- Error handling and edge cases
- Integration between components
- Public API methods
- Data validation
- Complex conditionals
- Critical user workflows

❌ **DON'T Test**:
- Trivial getters/setters
- Framework code (Qt, SQLAlchemy)
- Third-party libraries
- Auto-generated code
- Simple pass-through methods

### Coverage Quality Over Quantity

```python
# ✅ Good: Meaningful coverage
def test_user_validation_rejects_invalid_email(self):
    validator = UserValidator()
    
    # Test multiple invalid cases
    assert not validator.is_valid("invalid")
    assert not validator.is_valid("missing@")
    assert not validator.is_valid("@nodomain")

# ❌ Bad: Artificial coverage
def test_getter_returns_value(self):
    user = User("name")
    assert user.get_name() == "name"  # Trivial!
```

---

## 🎨 Common Patterns

### Pattern 1: Testing Qt Widgets

```python
import pytest
from PySide6.QtWidgets import QWidget

@pytest.fixture
def sidebar_widget(qtbot):
    """Create widget with qtbot for proper cleanup."""
    widget = Sidebar("Test")
    qtbot.addWidget(widget)  # Ensures cleanup
    return widget

def test_sidebar_displays_title(sidebar_widget):
    """Test widget property."""
    assert sidebar_widget.title_label.text() == "Test"

def test_button_click_emits_signal(sidebar_widget, qtbot):
    """Test signal emission."""
    # Use SignalBlocker to wait for signal
    with qtbot.waitSignal(sidebar_widget.button_clicked, timeout=1000):
        sidebar_widget.test_button.click()
```

### Pattern 2: Testing Async Code

```python
import pytest
import asyncio

@pytest.mark.asyncio
async def test_async_operation():
    """Test asynchronous function."""
    result = await async_function()
    assert result == expected_value

def test_async_with_event_loop():
    """Test async code with manual event loop."""
    loop = asyncio.get_event_loop()
    result = loop.run_until_complete(async_function())
    assert result == expected_value
```

### Pattern 3: Testing Database Operations

```python
@pytest.fixture
def test_db():
    """Create temporary test database."""
    db_path = ":memory:"  # In-memory SQLite
    connection = DatabaseConnection(db_path)
    connection.initialize()
    yield connection
    connection.close()

def test_save_and_retrieve(test_db):
    """Test database persistence."""
    manager = DatabaseManager(test_db)
    
    # Save
    test_id = manager.save_test_result(test_data)
    
    # Retrieve
    result = manager.get_test_result(test_id)
    assert result.test_type == test_data.test_type
```

### Pattern 4: Testing File Operations

```python
def test_file_creation(temp_dir):
    """Test file operations with temp directory."""
    file_path = temp_dir / "test.cpp"
    content = "int main() { return 0; }"
    
    # Save file
    FileOperations.save_file(file_path, content)
    
    # Verify
    assert file_path.exists()
    assert file_path.read_text() == content
```

### Pattern 5: Testing Thread Safety

```python
import threading

def test_singleton_is_thread_safe():
    """Test singleton pattern with multiple threads."""
    instances = []
    
    def create_instance():
        instances.append(DatabaseConnection())
    
    # Create threads
    threads = [threading.Thread(target=create_instance) for _ in range(10)]
    
    # Start all threads
    for thread in threads:
        thread.start()
    
    # Wait for completion
    for thread in threads:
        thread.join()
    
    # All instances should be the same
    assert all(inst is instances[0] for inst in instances)
```

---

## 🔍 Troubleshooting

### Common Issues

#### Issue 1: Qt Platform Plugin Error

**Error**: `qt.qpa.plugin: Could not find the Qt platform plugin "windows"`

**Solution**:
```python
# In conftest.py (already configured)
def pytest_configure(config):
    os.environ['QT_QPA_PLATFORM'] = 'offscreen'
```

#### Issue 2: Test Discovery Problems

**Error**: Tests not being discovered

**Solution**:
```bash
# Check pytest configuration
pytest --collect-only

# Ensure files follow naming convention
# - test_*.py or *_test.py
# - Classes: Test*
# - Functions: test_*
```

#### Issue 3: Import Errors

**Error**: `ModuleNotFoundError: No module named 'src'`

**Solution**:
```ini
# In pytest.ini (already configured)
[tool:pytest]
pythonpath = . src
```

#### Issue 4: Flaky Tests

**Problem**: Tests pass sometimes, fail other times

**Solution**:
```python
# Mark as flaky
@pytest.mark.flaky(reruns=3)
def test_sometimes_fails():
    ...

# Or fix timing issues
@pytest.mark.timeout(5)
def test_with_timeout():
    ...
```

#### Issue 5: Slow Tests

**Problem**: Test suite takes too long

**Solution**:
```bash
# Identify slow tests
pytest --durations=10

# Run only fast tests
pytest -m "not slow"

# Parallelize
pytest -n auto
```

###Debugging Tests

```bash
# Drop into debugger on failure
pytest --pdb

# Drop into debugger on first failure
pytest -x --pdb

# Print output (disable capture)
pytest -s

# Show local variables
pytest -l --tb=long
```

---

## 🔄 CI/CD Integration

### GitHub Actions Configuration

The project uses GitHub Actions for automated testing. See `.github/workflows/test.yml`.

**Workflow triggers**:
- Push to `main` or `develop`
- Pull requests to `main` or `develop`

**Test matrix**:
- Operating Systems: Windows, Ubuntu, macOS
- Python Versions: 3.12, 3.13

**Steps**:
1. Checkout code
2. Set up Python environment
3. Install dependencies
4. Install compilers (g++, javac)
5. Run pytest with coverage
6. Upload coverage to Codecov
7. Generate test artifacts

### Pre-commit Hooks

```bash
# Install pre-commit
pip install pre-commit

# Set up hooks
pre-commit install

# Run manually
pre-commit run --all-files
```

### Coverage Requirements

**Branch protection rules**:
- All tests must pass
- Coverage must not decrease
- Code review required

---

## 📚 Additional Resources

### Documentation
- [pytest documentation](https://docs.pytest.org/)
- [pytest-cov documentation](https://pytest-cov.readthedocs.io/)
- [pytest-qt documentation](https://pytest-qt.readthedocs.io/)
- [Coverage.py documentation](https://coverage.readthedocs.io/)

### Internal Documentation
- `COVERAGE_ANALYSIS.md` - Detailed coverage breakdown
- `migration_playbook.md` - Testing strategy and phases
- `README.md` - Project overview

### Getting Help
- Check existing tests for patterns
- Review conftest.py for available fixtures
- Ask team members for guidance
- Search pytest documentation

---

## 🎯 Summary

### Key Principles
1. **Test behavior, not implementation**
2. **Keep tests fast and focused**
3. **Use fixtures for setup**
4. **Mock external dependencies**
5. **Write clear, descriptive test names**
6. **Follow AAA pattern**
7. **One assertion per test (when possible)**
8. **Test edge cases and errors**

### Quick Checklist
- [ ] Test follows AAA pattern
- [ ] Test name is descriptive
- [ ] Test has docstring
- [ ] Uses fixtures for setup
- [ ] Mocks external dependencies
- [ ] Tests edge cases
- [ ] Runs fast (<100ms for unit tests)
- [ ] Appropriate markers applied
- [ ] Coverage increases (or stays same)

---

**Document maintained by**: Development Team  
**Last reviewed**: October 13, 2025  
**Version**: 1.0

For questions or updates, please create an issue or pull request.
