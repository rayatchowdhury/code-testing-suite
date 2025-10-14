"""
Root conftest.py - Shared fixtures for all tests.

This module provides common fixtures, test configuration, and utilities
used across unit, integration, and e2e tests.
"""

import os
import shutil
import sys
import tempfile
from pathlib import Path
from typing import Generator
from unittest.mock import MagicMock, Mock

import pytest

# Add src to path for imports
src_path = Path(__file__).parent.parent / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

# ============================================================================
# Pytest Configuration Hooks
# ============================================================================


def pytest_configure(config):
    """Configure pytest environment before tests run."""
    # Set Qt platform for headless testing
    os.environ["QT_QPA_PLATFORM"] = "offscreen"
    os.environ["QT_API"] = "pyside6"

    # Disable AI by default in tests
    os.environ["GEMINI_ENABLED"] = "false"

    # Set test mode flag
    os.environ["TESTING"] = "true"


def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers automatically."""
    for item in items:
        # Auto-mark based on path
        if "unit" in str(item.fspath):
            item.add_marker(pytest.mark.unit)
        elif "integration" in str(item.fspath):
            item.add_marker(pytest.mark.integration)
        elif "e2e" in str(item.fspath):
            item.add_marker(pytest.mark.e2e)

        # Mark GUI tests
        if "gui" in str(item.fspath) or "widget" in str(item.fspath):
            item.add_marker(pytest.mark.gui)

        # Mark database tests
        if "database" in str(item.fspath) or "repository" in str(item.fspath):
            item.add_marker(pytest.mark.database)


# ============================================================================
# Temporary Directory Fixtures
# ============================================================================


@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    """
    Create a temporary directory for test isolation.

    Yields:
        Path to temporary directory

    Usage:
        def test_file_creation(temp_dir):
            file_path = temp_dir / "test.txt"
            file_path.write_text("content")
            assert file_path.exists()
    """
    temp_path = Path(tempfile.mkdtemp())
    yield temp_path
    shutil.rmtree(temp_path, ignore_errors=True)


@pytest.fixture
def temp_workspace(temp_dir) -> Path:
    """
    Create a temporary workspace with nested directory structure.

    Creates:
        workspace/
        ├── comparator/
        │   ├── inputs/
        │   └── outputs/
        ├── validator/
        │   ├── inputs/
        │   └── outputs/
        └── benchmarker/
            ├── inputs/
            └── outputs/

    Yields:
        Path to workspace root
    """
    workspace = temp_dir / "workspace"

    # Create nested structure
    for test_type in ["comparator", "validator", "benchmarker"]:
        test_dir = workspace / test_type
        (test_dir / "inputs").mkdir(parents=True, exist_ok=True)
        (test_dir / "outputs").mkdir(parents=True, exist_ok=True)

    return workspace


@pytest.fixture
def temp_db(temp_dir) -> Generator[Path, None, None]:
    """
    Create a temporary SQLite database for testing.

    Yields:
        Path to temporary database file
    """
    db_path = temp_dir / "test.db"
    yield db_path
    if db_path.exists():
        db_path.unlink()


# ============================================================================
# Sample Source Code Fixtures
# ============================================================================


@pytest.fixture
def sample_cpp_generator() -> str:
    """Simple C++ generator code for testing."""
    return """#include <iostream>
int main() {
    std::cout << "5\\n";
    return 0;
}
"""


@pytest.fixture
def sample_cpp_test() -> str:
    """Simple C++ test solution for testing."""
    return """#include <iostream>
int main() {
    int n;
    std::cin >> n;
    std::cout << n * 2 << std::endl;
    return 0;
}
"""


@pytest.fixture
def sample_cpp_correct() -> str:
    """Simple C++ correct solution for testing."""
    return """#include <iostream>
int main() {
    int n;
    std::cin >> n;
    std::cout << n * 2 << std::endl;
    return 0;
}
"""


@pytest.fixture
def sample_python_code() -> str:
    """Simple Python code for testing."""
    return """def main():
    n = int(input())
    print(n * 2)

if __name__ == '__main__':
    main()
"""


@pytest.fixture
def sample_java_code() -> str:
    """Simple Java code for testing."""
    return """import java.util.Scanner;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int n = sc.nextInt();
        System.out.println(n * 2);
        sc.close();
    }
}
"""


# ============================================================================
# Mock Fixtures
# ============================================================================


@pytest.fixture
def mock_qapplication(monkeypatch):
    """Mock QApplication for tests that don't need real Qt."""
    mock_app = MagicMock()
    monkeypatch.setattr("PySide6.QtWidgets.QApplication.instance", lambda: mock_app)
    return mock_app


@pytest.fixture
def mock_database_manager():
    """Mock DatabaseManager for tests that don't need real database."""
    mock_db = Mock()
    mock_db.save_test_result.return_value = 1
    mock_db.get_test_results.return_value = []
    mock_db.get_test_result_by_id.return_value = None
    mock_db.delete_test_result.return_value = True
    return mock_db


@pytest.fixture
def mock_compiler():
    """Mock compiler for tests that don't need real compilation."""
    mock = Mock()
    mock.compile.return_value = (True, "Compilation successful")
    mock.get_executable_path.return_value = Path("test.exe")
    return mock


# ============================================================================
# Skip Conditions
# ============================================================================


@pytest.fixture
def requires_compiler():
    """Skip test if C++ compiler is not available."""
    import shutil

    if not shutil.which("g++") and not shutil.which("cl"):
        pytest.skip("C++ compiler (g++/cl) not found in PATH")


@pytest.fixture
def requires_python():
    """Skip test if Python is not available."""
    import shutil

    if not shutil.which("python"):
        pytest.skip("Python interpreter not found in PATH")


@pytest.fixture
def requires_java():
    """Skip test if Java compiler is not available."""
    import shutil

    if not (shutil.which("javac") and shutil.which("java")):
        pytest.skip("Java compiler/runtime not found in PATH")


# ============================================================================
# Cleanup Fixtures
# ============================================================================


@pytest.fixture(autouse=True)
def cleanup_test_files():
    """
    Automatically cleanup test artifacts after each test.

    Removes common test file patterns to prevent pollution.
    """
    yield

    # Cleanup patterns
    patterns = ["*.exe", "*.o", "*.class", "__pycache__"]
    for pattern in patterns:
        for file in Path(".").glob(pattern):
            try:
                if file.is_file():
                    file.unlink()
                elif file.is_dir():
                    shutil.rmtree(file, ignore_errors=True)
            except (PermissionError, OSError):
                pass  # Ignore cleanup errors
