"""Unit tests for FileOperations utility class."""

import os
import tempfile
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock, mock_open

from PySide6.QtWidgets import QFileDialog, QMessageBox

from src.app.shared.utils.file_operations import FileOperations


class TestFileOperations:
    """Test cases for FileOperations class."""

    def test_file_filters_constant(self):
        """Test that FILE_FILTERS constant is properly defined."""
        filters = FileOperations.FILE_FILTERS
        assert "Programming Files" in filters
        assert "C++ Files" in filters
        assert "Python Files" in filters
        assert "Java Files" in filters
        assert "All Files" in filters

    def test_supported_extensions_constant(self):
        """Test that SUPPORTED_EXTENSIONS contains expected extensions."""
        extensions = FileOperations.SUPPORTED_EXTENSIONS
        expected = ['.cpp', '.h', '.hpp', '.py', '.java', '.c', '.cc', '.cxx']
        
        for ext in expected:
            assert ext in extensions

    def test_language_map_constant(self):
        """Test that LANGUAGE_MAP maps extensions to correct languages."""
        lang_map = FileOperations.LANGUAGE_MAP
        
        # Test C++ extensions
        assert lang_map['.cpp'] == 'C++'
        assert lang_map['.hpp'] == 'C++'
        assert lang_map['.cc'] == 'C++'
        
        # Test Python extension
        assert lang_map['.py'] == 'Python'
        
        # Test Java extension
        assert lang_map['.java'] == 'Java'
        
        # Test C extension
        assert lang_map['.c'] == 'C'

    def test_get_extension_from_filter(self):
        """Test extension extraction from filter strings."""
        # Test C++ filter
        cpp_filter = "C++ Files (*.cpp *.h *.hpp)"
        assert FileOperations.get_extension_from_filter(cpp_filter) == '.cpp'
        
        # Test Python filter
        python_filter = "Python Files (*.py)"
        assert FileOperations.get_extension_from_filter(python_filter) == '.py'
        
        # Test Java filter
        java_filter = "Java Files (*.java)"
        assert FileOperations.get_extension_from_filter(java_filter) == '.java'
        
        # Test unknown filter
        unknown_filter = "Unknown Files (*.unknown)"
        assert FileOperations.get_extension_from_filter(unknown_filter) == ''

    def test_save_file_success(self, tmp_path):
        """Test successful file saving."""
        test_file = tmp_path / "test.cpp"
        test_content = "#include <iostream>\nint main() { return 0; }"
        
        result = FileOperations.save_file(test_file, test_content)
        
        assert result is True
        assert test_file.exists()
        assert test_file.read_text(encoding='utf-8') == test_content

    def test_save_file_with_string_path(self, tmp_path):
        """Test file saving with string path instead of Path object."""
        test_file = str(tmp_path / "test.py")
        test_content = "print('Hello, World!')"
        
        result = FileOperations.save_file(test_file, test_content)
        
        assert result is True
        assert Path(test_file).exists()
        assert Path(test_file).read_text(encoding='utf-8') == test_content

    @patch('pathlib.Path.write_text', side_effect=PermissionError("Access denied"))
    def test_save_file_permission_error_without_parent(self, mock_write_text, tmp_path):
        """Test file saving with permission error and no parent widget."""
        test_file = tmp_path / "test.cpp"
        test_content = "test content"
        
        result = FileOperations.save_file(test_file, test_content)
        
        assert result is False

    @patch('pathlib.Path.write_text', side_effect=PermissionError("Access denied"))
    @patch('PySide6.QtWidgets.QMessageBox.critical')
    def test_save_file_permission_error_with_parent(self, mock_critical, mock_write_text, tmp_path):
        """Test file saving with permission error and parent widget."""
        test_file = tmp_path / "test.cpp"
        test_content = "test content"
        parent_widget = MagicMock()
        
        result = FileOperations.save_file(test_file, test_content, parent_widget)
        
        assert result is False
        mock_critical.assert_called_once()
        args = mock_critical.call_args[0]
        assert args[0] == parent_widget
        assert "Error" in args[1]
        assert "Could not save file" in args[2]

    @patch('PySide6.QtWidgets.QFileDialog.getSaveFileName')
    def test_save_file_as_success(self, mock_get_save_filename, tmp_path):
        """Test save file as dialog with successful save."""
        test_file = str(tmp_path / "test.cpp")
        test_content = "#include <iostream>"
        parent_widget = MagicMock()
        
        # Mock dialog return values
        mock_get_save_filename.return_value = (test_file, "C++ Files (*.cpp *.h *.hpp)")
        
        with patch.object(FileOperations, 'save_file', return_value=True) as mock_save:
            result = FileOperations.save_file_as(parent_widget, test_content)
            
            assert result == test_file
            mock_save.assert_called_once_with(test_file, test_content, parent_widget)

    @patch('PySide6.QtWidgets.QFileDialog.getSaveFileName')
    def test_save_file_as_adds_extension(self, mock_get_save_filename, tmp_path):
        """Test that save file as adds appropriate extension."""
        test_file_no_ext = str(tmp_path / "test")  # No extension
        test_content = "print('hello')"
        parent_widget = MagicMock()
        
        # Mock dialog return values - Python filter selected
        mock_get_save_filename.return_value = (test_file_no_ext, "Python Files (*.py)")
        
        with patch.object(FileOperations, 'save_file', return_value=True) as mock_save:
            result = FileOperations.save_file_as(parent_widget, test_content)
            
            expected_file = test_file_no_ext + ".py"
            assert result == expected_file
            mock_save.assert_called_once_with(expected_file, test_content, parent_widget)

    @patch('PySide6.QtWidgets.QFileDialog.getSaveFileName')
    def test_save_file_as_cancelled(self, mock_get_save_filename):
        """Test save file as dialog when user cancels."""
        parent_widget = MagicMock()
        test_content = "test content"
        
        # Mock dialog return values - empty filename means cancelled
        mock_get_save_filename.return_value = ("", "")
        
        result = FileOperations.save_file_as(parent_widget, test_content)
        
        assert result is None

    @patch('PySide6.QtWidgets.QFileDialog.getSaveFileName')
    def test_save_file_as_save_fails(self, mock_get_save_filename, tmp_path):
        """Test save file as when actual save operation fails."""
        test_file = str(tmp_path / "test.cpp")
        test_content = "test content"
        parent_widget = MagicMock()
        
        mock_get_save_filename.return_value = (test_file, "C++ Files (*.cpp)")
        
        with patch.object(FileOperations, 'save_file', return_value=False):
            result = FileOperations.save_file_as(parent_widget, test_content)
            
            assert result is None

    @patch('PySide6.QtWidgets.QFileDialog.getOpenFileName')
    def test_open_file_success_utf8(self, mock_get_open_filename, tmp_path):
        """Test successful file opening with UTF-8 encoding."""
        test_file = tmp_path / "test.cpp"
        test_content = "#include <iostream>\n// UTF-8 content"
        test_file.write_text(test_content, encoding='utf-8')
        
        parent_widget = MagicMock()
        mock_get_open_filename.return_value = (str(test_file), "C++ Files (*.cpp)")
        
        file_path, content = FileOperations.open_file(parent_widget)
        
        assert file_path == str(test_file)
        assert content == test_content

    @patch('PySide6.QtWidgets.QFileDialog.getOpenFileName')
    def test_open_file_success_latin1_fallback(self, mock_get_open_filename, tmp_path):
        """Test file opening with latin-1 fallback when UTF-8 fails."""
        test_file = tmp_path / "test.cpp"
        # Create file with latin-1 encoding that would fail UTF-8 decoding
        with open(test_file, 'wb') as f:
            f.write(b'#include <iostream>\n// \xe9\xe8\xe7')  # Special characters
        
        parent_widget = MagicMock()
        mock_get_open_filename.return_value = (str(test_file), "C++ Files (*.cpp)")
        
        with patch('pathlib.Path.read_text') as mock_read:
            # First call (UTF-8) fails, second call (latin-1) succeeds
            mock_read.side_effect = [
                UnicodeDecodeError('utf-8', b'test', 0, 1, 'invalid utf-8'),
                "file content"
            ]
            
            file_path, content = FileOperations.open_file(parent_widget)
            
            assert file_path == str(test_file)
            assert content == "file content"
            assert mock_read.call_count == 2

    @patch('PySide6.QtWidgets.QFileDialog.getOpenFileName')
    @patch('PySide6.QtWidgets.QMessageBox.critical')
    def test_open_file_decode_error(self, mock_critical, mock_get_open_filename, tmp_path):
        """Test file opening when both UTF-8 and latin-1 decoding fail."""
        test_file = tmp_path / "test.cpp"
        test_file.write_text("test")  # File exists
        
        parent_widget = MagicMock()
        mock_get_open_filename.return_value = (str(test_file), "C++ Files (*.cpp)")
        
        with patch('pathlib.Path.read_text', side_effect=UnicodeDecodeError('utf-8', b'test', 0, 1, 'error')):
            file_path, content = FileOperations.open_file(parent_widget)
            
            assert file_path is None
            assert content is None
            mock_critical.assert_called_once()

    @patch('PySide6.QtWidgets.QFileDialog.getOpenFileName')
    @patch('PySide6.QtWidgets.QMessageBox.critical')
    def test_open_file_not_found(self, mock_critical, mock_get_open_filename, tmp_path):
        """Test file opening when file doesn't exist."""
        test_file = tmp_path / "nonexistent.cpp"
        parent_widget = MagicMock()
        mock_get_open_filename.return_value = (str(test_file), "C++ Files (*.cpp)")
        
        file_path, content = FileOperations.open_file(parent_widget)
        
        assert file_path is None
        assert content is None
        mock_critical.assert_called_once()
        args = mock_critical.call_args[0]
        assert "File not found" in args[2]

    @patch('PySide6.QtWidgets.QFileDialog.getOpenFileName')
    def test_open_file_cancelled(self, mock_get_open_filename):
        """Test file opening when user cancels dialog."""
        parent_widget = MagicMock()
        mock_get_open_filename.return_value = ("", "")  # Empty means cancelled
        
        file_path, content = FileOperations.open_file(parent_widget)
        
        assert file_path is None
        assert content is None

    @patch('PySide6.QtWidgets.QFileDialog.getOpenFileName', side_effect=Exception("Dialog error"))
    @patch('PySide6.QtWidgets.QMessageBox.critical')
    def test_open_file_dialog_exception(self, mock_critical, mock_get_open_filename):
        """Test file opening when dialog raises exception."""
        parent_widget = MagicMock()
        
        file_path, content = FileOperations.open_file(parent_widget)
        
        assert file_path is None
        assert content is None
        mock_critical.assert_called_once()
        args = mock_critical.call_args[0]
        assert "Error opening file" in args[2]

    def test_class_constants_immutability(self):
        """Test that class constants maintain their expected values."""
        # These should remain constant for the application to work correctly
        assert isinstance(FileOperations.FILE_FILTERS, str)
        assert isinstance(FileOperations.SUPPORTED_EXTENSIONS, list)
        assert isinstance(FileOperations.LANGUAGE_MAP, dict)
        
        # Verify key extensions are present
        required_extensions = ['.cpp', '.py', '.java', '.h']
        for ext in required_extensions:
            assert ext in FileOperations.SUPPORTED_EXTENSIONS
            assert ext in FileOperations.LANGUAGE_MAP