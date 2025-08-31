"""
Pytest configuration and shared fixtures.

This module provides:
- Test fixtures for common test setup
- Mock configurations for testing
- Test utilities and helpers
"""

import pytest
import tempfile
import shutil
import os
from pathlib import Path
from unittest.mock import patch, MagicMock

# Test data directory
TEST_DATA_DIR = Path(__file__).parent / "data"


@pytest.fixture
def temp_dir():
    """Create a temporary directory for tests."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def mock_user_data_dir(temp_dir):
    """Mock the user data directory to use temp directory."""
    with patch('constants.paths.USER_DATA_DIR', temp_dir):
        yield temp_dir


@pytest.fixture
def mock_config_file(temp_dir):
    """Create a mock config file for testing."""
    config_path = os.path.join(temp_dir, 'config.json')
    config_data = {
        "ai_settings": {
            "use_ai_panel": True,
            "gemini_api_key": "test_api_key_12345678901234567890"
        },
        "editor_settings": {
            "cpp_version": "C++17",
            "workspace_folder": temp_dir
        }
    }
    
    import json
    with open(config_path, 'w') as f:
        json.dump(config_data, f)
    
    yield config_path


@pytest.fixture
def mock_qapplication():
    """Mock QApplication for GUI tests."""
    app_mock = MagicMock()
    with patch('PySide6.QtWidgets.QApplication', return_value=app_mock):
        with patch('PySide6.QtWidgets.QApplication.instance', return_value=app_mock):
            yield app_mock


@pytest.fixture(scope="session")
def test_project_root():
    """Get the project root directory for tests."""
    return Path(__file__).parent.parent


@pytest.fixture
def sample_code_files(temp_dir):
    """Create sample code files for testing."""
    files = {}
    
    # Sample C++ file
    cpp_content = '''#include <iostream>
using namespace std;

int main() {
    cout << "Hello World!" << endl;
    return 0;
}'''
    cpp_path = os.path.join(temp_dir, 'test.cpp')
    with open(cpp_path, 'w') as f:
        f.write(cpp_content)
    files['cpp'] = cpp_path
    
    # Sample Python file
    py_content = '''def hello_world():
    print("Hello World!")

if __name__ == "__main__":
    hello_world()'''
    py_path = os.path.join(temp_dir, 'test.py')
    with open(py_path, 'w') as f:
        f.write(py_content)
    files['python'] = py_path
    
    return files


def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers", "unit: mark test as a unit test"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as an integration test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )
    config.addinivalue_line(
        "markers", "ui: mark test as requiring UI"
    )
