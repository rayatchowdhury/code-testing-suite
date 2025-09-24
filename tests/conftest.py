"""Test configuration and shared fixtures."""

import os
import sys
import tempfile
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add src directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QSettings
from PySide6.QtTest import QTest

# Test data directory
TEST_DATA_DIR = Path(__file__).parent / "fixtures" / "data"
TEST_DATA_DIR.mkdir(parents=True, exist_ok=True)


@pytest.fixture(scope="session")
def qapp():
    """Create QApplication for GUI tests."""
    if not QApplication.instance():
        app = QApplication([])
        app.setOrganizationName("TestCodeSuite")
        app.setApplicationName("TestCodeSuite")
        yield app
        app.quit()
    else:
        yield QApplication.instance()


@pytest.fixture
def qtbot(qapp, qtbot):
    """Enhanced qtbot with application context."""
    return qtbot


@pytest.fixture
def temp_config_dir():
    """Create temporary directory for config tests."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir


@pytest.fixture
def sample_config():
    """Sample configuration data for testing."""
    return {
        'cpp_version': 'c++17',
        'workspace_folder': '/test/workspace',
        'gemini': {
            'enabled': True,
            'api_key': 'test-api-key',
            'model': 'gemini-2.5-flash'
        },
        'editor_settings': {
            'autosave': True,
            'autosave_interval': 5,
            'tab_width': 4,
            'font_size': 12,
            'font_family': 'Consolas',
            'bracket_matching': True
        }
    }


@pytest.fixture
def invalid_config():
    """Invalid configuration data for error testing."""
    return {
        'cpp_version': 123,  # Should be string
        'workspace_folder': '',
        'gemini': 'invalid',  # Should be dict
        'editor_settings': {
            'autosave': 'yes',  # Should be bool
            'tab_width': 'four'  # Should be int
        }
    }


@pytest.fixture
def mock_database():
    """Mock database for testing."""
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as temp_db:
        temp_db_path = temp_db.name
    
    yield temp_db_path
    
    # Cleanup
    try:
        os.unlink(temp_db_path)
    except OSError:
        pass


@pytest.fixture
def sample_code_files():
    """Sample code files for testing."""
    return {
        'generator.cpp': '''
#include <iostream>
#include <random>

int main() {
    std::random_device rd;
    std::mt19937 gen(rd());
    std::uniform_int_distribution<> dis(1, 100);
    
    std::cout << dis(gen) << " " << dis(gen) << std::endl;
    return 0;
}
''',
        'correct.cpp': '''
#include <iostream>

int main() {
    int a, b;
    std::cin >> a >> b;
    std::cout << a + b << std::endl;
    return 0;
}
''',
        'test.cpp': '''
#include <iostream>

int main() {
    int a, b;
    std::cin >> a >> b;
    std::cout << a - b << std::endl;  // Intentional bug
    return 0;
}
'''
    }


@pytest.fixture
def mock_gemini_response():
    """Mock Gemini API response."""
    return {
        "candidates": [{
            "content": {
                "parts": [{
                    "text": "This is a mock response from Gemini API."
                }]
            }
        }]
    }


@pytest.fixture(autouse=True)
def clean_qt_settings():
    """Clean Qt settings before each test."""
    QSettings().clear()
    yield
    QSettings().clear()


@pytest.fixture
def mock_file_system():
    """Mock file system operations."""
    with patch('pathlib.Path.exists') as mock_exists, \
         patch('pathlib.Path.read_text') as mock_read, \
         patch('pathlib.Path.write_text') as mock_write:
        mock_exists.return_value = True
        mock_read.return_value = "mock file content"
        mock_write.return_value = None
        yield {
            'exists': mock_exists,
            'read_text': mock_read,
            'write_text': mock_write
        }


class TestHelper:
    """Helper utilities for tests."""
    
    @staticmethod
    def create_test_file(path: Path, content: str) -> Path:
        """Create a test file with given content."""
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)
        return path
    
    @staticmethod
    def wait_for_condition(condition, timeout=1000):
        """Wait for a condition to become true."""
        import time
        start_time = time.time()
        while time.time() - start_time < timeout / 1000:
            if condition():
                return True
            QTest.qWait(10)
        return False