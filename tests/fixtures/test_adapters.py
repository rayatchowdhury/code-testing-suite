"""Test adapters and wrappers for isolating GUI components during testing."""

import os
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch
from typing import Optional, Dict, Any

from PySide6.QtWidgets import QWidget, QApplication
from PySide6.QtCore import QObject, Signal

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))


class MockConfigManager:
    """Mock configuration manager for testing."""
    
    def __init__(self, config_data: Optional[Dict] = None):
        self.config_data = config_data or self._get_default_config()
        self.save_called = False
        self.load_called = False
    
    def load_config(self) -> Dict[str, Any]:
        """Mock config loading."""
        self.load_called = True
        return self.config_data.copy()
    
    def save_config(self, config: Dict[str, Any]) -> None:
        """Mock config saving."""
        self.save_called = True
        self.config_data = config.copy()
    
    def get_default_config(self) -> Dict[str, Any]:
        """Get default configuration."""
        return self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Default configuration for testing."""
        return {
            'cpp_version': 'c++17',
            'workspace_folder': '/test/workspace',
            'gemini': {
                'enabled': False,
                'api_key': '',
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


class MockDatabaseManager:
    """Mock database manager for testing."""
    
    def __init__(self):
        self.test_results = {}
        self.sessions = {}
        self.test_cases = {}
        self.projects = {}
        self.next_id = 1
        
        self.save_test_result_called = False
        self.get_test_result_called = False
        self.connect_called = False
        self.close_called = False
    
    def connect(self):
        """Mock database connection."""
        self.connect_called = True
        return MagicMock()
    
    def close(self):
        """Mock database close."""
        self.close_called = True
    
    def save_test_result(self, test_result):
        """Mock saving test result."""
        self.save_test_result_called = True
        test_result.id = self.next_id
        self.test_results[self.next_id] = test_result
        self.next_id += 1
        return test_result.id
    
    def get_test_result(self, result_id: int):
        """Mock getting test result."""
        self.get_test_result_called = True
        return self.test_results.get(result_id)
    
    def get_all_test_results(self):
        """Mock getting all test results."""
        return list(self.test_results.values())
    
    def save_test_case_result(self, test_case, test_result_id: int):
        """Mock saving test case result."""
        test_case.id = self.next_id
        self.test_cases[self.next_id] = (test_case, test_result_id)
        self.next_id += 1
        return test_case.id
    
    def get_test_cases_for_result(self, test_result_id: int):
        """Mock getting test cases for result."""
        return [case for case, result_id in self.test_cases.values() 
                if result_id == test_result_id]
    
    def save_session(self, session):
        """Mock saving session."""
        session.id = self.next_id
        self.sessions[self.next_id] = session
        self.next_id += 1
        return session.id
    
    def get_session(self, session_id: int):
        """Mock getting session."""
        return self.sessions.get(session_id)
    
    def delete_test_result(self, result_id: int):
        """Mock deleting test result."""
        if result_id in self.test_results:
            del self.test_results[result_id]
            return True
        return False


class MockFileOperations:
    """Mock file operations for testing."""
    
    def __init__(self):
        self.saved_files = {}  # path -> content
        self.save_file_called = False
        self.open_file_called = False
        self.save_file_as_called = False
        
    def save_file(self, filepath, content, parent=None):
        """Mock save file."""
        self.save_file_called = True
        self.saved_files[str(filepath)] = content
        return True
    
    def open_file(self, parent):
        """Mock open file."""
        self.open_file_called = True
        # Return first saved file for testing
        if self.saved_files:
            path, content = next(iter(self.saved_files.items()))
            return path, content
        return None, None
    
    def save_file_as(self, parent, content, current_path=None):
        """Mock save file as."""
        self.save_file_as_called = True
        test_path = "/test/saved_file.cpp"
        self.saved_files[test_path] = content
        return test_path
    
    @staticmethod
    def get_extension_from_filter(selected_filter):
        """Mock extension from filter."""
        if 'C++' in selected_filter:
            return '.cpp'
        elif 'Python' in selected_filter:
            return '.py'
        elif 'Java' in selected_filter:
            return '.java'
        return ''


class MockGeminiClient:
    """Mock Gemini AI client for testing."""
    
    def __init__(self, api_key: str = "test-key"):
        self.api_key = api_key
        self.requests_made = []
        self.generate_content_called = False
        
        # Default mock response
        self.mock_response = {
            "candidates": [{
                "content": {
                    "parts": [{
                        "text": "This is a mock AI response for testing."
                    }]
                }
            }]
        }
    
    def generate_content(self, prompt: str) -> Dict[str, Any]:
        """Mock content generation."""
        self.generate_content_called = True
        self.requests_made.append(prompt)
        return self.mock_response
    
    def set_mock_response(self, response: Dict[str, Any]):
        """Set custom mock response."""
        self.mock_response = response
    
    def is_configured(self) -> bool:
        """Check if client is configured."""
        return bool(self.api_key and self.api_key != "")


class TestableMainWindow(QWidget):
    """Testable version of MainWindow with mocked dependencies."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Code Testing Suite - Test Mode")
        
        # Mock dependencies
        self.config_manager = MockConfigManager()
        self.database_manager = MockDatabaseManager()
        self.file_operations = MockFileOperations()
        self.gemini_client = MockGeminiClient()
        
        # Track method calls for testing
        self.init_called = True
        self.show_called = False
        self.close_called = False
        
        # Minimal UI setup for testing
        self.setup_minimal_ui()
    
    def setup_minimal_ui(self):
        """Set up minimal UI components for testing."""
        self.resize(800, 600)
    
    def show(self):
        """Override show to track calls."""
        self.show_called = True
        super().show()
    
    def close(self):
        """Override close to track calls."""
        self.close_called = True
        return super().close()
    
    def get_config_manager(self):
        """Get mock config manager."""
        return self.config_manager
    
    def get_database_manager(self):
        """Get mock database manager."""
        return self.database_manager
    
    def get_file_operations(self):
        """Get mock file operations."""
        return self.file_operations
    
    def get_gemini_client(self):
        """Get mock Gemini client."""
        return self.gemini_client


class TestableEditorWidget(QWidget):
    """Testable version of EditorWidget."""
    
    # Mock signals
    text_changed = Signal(str)
    file_saved = Signal(str)
    file_opened = Signal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.content = ""
        self.current_file = None
        self.is_modified = False
        
        # Track method calls
        self.set_content_called = False
        self.get_content_called = False
        self.save_file_called = False
        self.open_file_called = False
    
    def set_content(self, content: str):
        """Set editor content."""
        self.set_content_called = True
        self.content = content
        self.is_modified = True
        self.text_changed.emit(content)
    
    def get_content(self) -> str:
        """Get editor content."""
        self.get_content_called = True
        return self.content
    
    def save_file(self, filepath: Optional[str] = None):
        """Mock save file."""
        self.save_file_called = True
        if filepath:
            self.current_file = filepath
        if self.current_file:
            self.file_saved.emit(self.current_file)
            self.is_modified = False
            return True
        return False
    
    def open_file(self, filepath: str):
        """Mock open file."""
        self.open_file_called = True
        self.current_file = filepath
        self.content = f"// Content of {filepath}"
        self.is_modified = False
        self.file_opened.emit(filepath)
        return True
    
    def get_current_file(self) -> Optional[str]:
        """Get current file path."""
        return self.current_file
    
    def is_file_modified(self) -> bool:
        """Check if file is modified."""
        return self.is_modified


class TestableConsoleWidget(QWidget):
    """Testable version of ConsoleWidget."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.output_buffer = []
        self.clear_called = False
        self.append_called = False
    
    def append_output(self, text: str):
        """Append text to console output."""
        self.append_called = True
        self.output_buffer.append(text)
    
    def clear_output(self):
        """Clear console output."""
        self.clear_called = True
        self.output_buffer.clear()
    
    def get_output(self) -> str:
        """Get all console output."""
        return '\n'.join(self.output_buffer)


class TestContext:
    """Context manager for test isolation."""
    
    def __init__(self):
        self.patches = []
        self.mocks = {}
    
    def __enter__(self):
        """Enter test context."""
        # Patch key modules with mocks
        config_patch = patch('src.app.core.config.core.config_handler.ConfigManager', MockConfigManager)
        db_patch = patch('src.app.persistence.database.database_manager.DatabaseManager', MockDatabaseManager)
        file_patch = patch('src.app.shared.utils.file_operations.FileOperations', MockFileOperations)
        
        self.patches = [config_patch, db_patch, file_patch]
        
        for patch_obj in self.patches:
            mock_obj = patch_obj.start()
            self.mocks[patch_obj.attribute] = mock_obj
        
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit test context."""
        for patch_obj in self.patches:
            patch_obj.stop()
        
        self.patches.clear()
        self.mocks.clear()
    
    def get_mock(self, attribute_name: str):
        """Get mock object by attribute name."""
        return self.mocks.get(attribute_name)


class TestDataFactory:
    """Factory for creating test data objects."""
    
    @staticmethod
    def create_test_result(**kwargs):
        """Create TestResult for testing."""
        from src.app.persistence.database.database_manager import TestResult
        
        defaults = {
            'test_type': 'stress',
            'file_path': '/test/file.cpp',
            'test_count': 10,
            'passed_tests': 8,
            'failed_tests': 2,
            'total_time': 1.5,
            'timestamp': '2023-01-01T12:00:00',
            'project_name': 'TestProject'
        }
        
        defaults.update(kwargs)
        return TestResult(**defaults)
    
    @staticmethod
    def create_test_case_result(**kwargs):
        """Create TestCaseResult for testing."""
        from src.app.persistence.database.database_manager import TestCaseResult
        
        defaults = {
            'test_number': 1,
            'passed': True,
            'input_data': '5 3',
            'expected_output': '8',
            'actual_output': '8',
            'execution_time': 0.001,
            'timestamp': '2023-01-01T12:00:01'
        }
        
        defaults.update(kwargs)
        return TestCaseResult(**defaults)
    
    @staticmethod
    def create_session(**kwargs):
        """Create Session for testing."""
        from src.app.persistence.database.database_manager import Session
        
        defaults = {
            'session_name': 'Test Session',
            'open_files': '["file1.cpp", "file2.py"]',
            'active_file': 'file1.cpp',
            'timestamp': '2023-01-01T12:00:00',
            'project_name': 'TestProject'
        }
        
        defaults.update(kwargs)
        return Session(**defaults)
    
    @staticmethod
    def create_sample_code_files():
        """Create sample code files for testing."""
        return {
            'main.cpp': '''#include <iostream>
using namespace std;

int main() {
    int a, b;
    cin >> a >> b;
    cout << a + b << endl;
    return 0;
}''',
            'generator.cpp': '''#include <iostream>
#include <random>
using namespace std;

int main() {
    random_device rd;
    mt19937 gen(rd());
    uniform_int_distribution<> dis(1, 100);
    
    cout << dis(gen) << " " << dis(gen) << endl;
    return 0;
}''',
            'test.py': '''#!/usr/bin/env python3

def add_numbers(a, b):
    return a + b

if __name__ == "__main__":
    x, y = map(int, input().split())
    print(add_numbers(x, y))
'''
        }


def setup_test_environment():
    """Setup test environment with mocked dependencies."""
    # Ensure QApplication exists for GUI tests
    if not QApplication.instance():
        app = QApplication([])
        app.setOrganizationName("TestCodeSuite")
        app.setApplicationName("TestCodeSuite")
    
    return TestContext()


def create_isolated_widget(widget_class, **kwargs):
    """Create widget in isolated environment with mocked dependencies."""
    with setup_test_environment():
        widget = widget_class(**kwargs)
        return widget