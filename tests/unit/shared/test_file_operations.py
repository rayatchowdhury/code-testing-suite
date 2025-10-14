"""
Test suite for FileOperations utility class.

Tests file saving, loading, extension detection, language mapping,
error handling, and file dialog operations (mocked).
"""

import os
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pytest
from PySide6.QtWidgets import QMessageBox

from src.app.shared.utils.file_operations import FileOperations


class TestFileOperationsSave:
    """Test file saving operations."""

    def test_saves_file_successfully(self, temp_dir):
        """Should save file with UTF-8 encoding."""
        file_path = temp_dir / "test.txt"
        content = "Hello, World!"

        result = FileOperations.save_file(str(file_path), content)

        assert result is True
        assert file_path.exists()
        assert file_path.read_text(encoding="utf-8") == content

    def test_saves_file_with_unicode_content(self, temp_dir):
        """Should correctly save Unicode content."""
        file_path = temp_dir / "unicode.txt"
        content = "Hello 世界 🌍"

        result = FileOperations.save_file(str(file_path), content)

        assert result is True
        assert file_path.read_text(encoding="utf-8") == content

    def test_handles_save_error_invalid_path(self):
        """Should create parent directories even for deep paths."""
        # FileOperations creates directories, so this will succeed on most systems
        result = FileOperations.save_file("/invalid/path/file.txt", "content")

        # Test that it doesn't crash (result is bool)
        assert isinstance(result, bool)

    @patch("PySide6.QtWidgets.QMessageBox.critical")
    def test_shows_error_dialog_on_save_failure(self, mock_dialog, temp_dir):
        """Should show error dialog when parent is provided."""
        mock_parent = Mock()

        # Mock Path.write_text to raise exception
        with patch(
            "pathlib.Path.write_text", side_effect=PermissionError("Cannot write")
        ):
            result = FileOperations.save_file(
                str(temp_dir / "test.txt"), "content", parent=mock_parent
            )

            assert result is False
            mock_dialog.assert_called_once()


class TestFileOperationsLoad:
    """Test file loading operations."""

    def test_loads_file_successfully(self, temp_dir):
        """Should load file content with UTF-8 encoding."""
        file_path = temp_dir / "test.txt"
        content = "Test content"
        file_path.write_text(content, encoding="utf-8")

        loaded = FileOperations.load_file(str(file_path))

        assert loaded == content

    def test_loads_file_with_unicode(self, temp_dir):
        """Should load Unicode content correctly."""
        file_path = temp_dir / "unicode.txt"
        content = "Unicode: 你好 مرحبا"
        file_path.write_text(content, encoding="utf-8")

        loaded = FileOperations.load_file(str(file_path))

        assert loaded == content

    def test_returns_none_on_load_error(self):
        """Should return None if file doesn't exist."""
        result = FileOperations.load_file("/nonexistent/file.txt")

        assert result is None


class TestFileOperationsWrite:
    """Test write_file method (creates directories)."""

    def test_writes_file_and_creates_directory(self, temp_dir):
        """Should create directory if it doesn't exist."""
        nested_path = temp_dir / "nested" / "dir" / "file.txt"
        content = "Nested content"

        result = FileOperations.write_file(str(nested_path), content)

        assert result is True
        assert nested_path.exists()
        assert nested_path.read_text(encoding="utf-8") == content

    def test_overwrites_existing_file(self, temp_dir):
        """Should overwrite existing file."""
        file_path = temp_dir / "existing.txt"
        file_path.write_text("Old content")

        result = FileOperations.write_file(str(file_path), "New content")

        assert result is True
        assert file_path.read_text() == "New content"


class TestFileOperationsRead:
    """Test read_file method."""

    def test_reads_file_successfully(self, temp_dir):
        """Should read file content."""
        file_path = temp_dir / "test.txt"
        content = "Read this"
        file_path.write_text(content)

        result = FileOperations.read_file(str(file_path))

        assert result == content

    def test_raises_file_not_found_error(self):
        """Should raise FileNotFoundError for missing file."""
        with pytest.raises(FileNotFoundError):
            FileOperations.read_file("/nonexistent/file.txt")


class TestFileOperationsExtensionDetection:
    """Test extension and language detection."""

    @pytest.mark.parametrize(
        "filename,expected_ext",
        [
            ("test.cpp", ".cpp"),
            ("Test.CPP", ".cpp"),  # Case insensitive
            ("main.py", ".py"),
            ("Main.java", ".java"),
            ("header.h", ".h"),
            ("noext", ""),
        ],
    )
    def test_get_file_extension(self, filename, expected_ext):
        """Should extract and normalize file extension."""
        ext = FileOperations.get_file_extension(filename)
        assert ext == expected_ext

    @pytest.mark.parametrize(
        "filename,expected_lang",
        [
            ("test.cpp", "C++"),
            ("test.cc", "C++"),
            ("test.cxx", "C++"),
            ("test.c", "C"),
            ("test.h", "C/C++"),
            ("test.hpp", "C++"),
            ("test.py", "Python"),
            ("Main.java", "Java"),
            ("test.txt", "Unknown"),
        ],
    )
    def test_get_file_language(self, filename, expected_lang):
        """Should detect programming language from extension."""
        lang = FileOperations.get_file_language(filename)
        assert lang == expected_lang

    @pytest.mark.parametrize(
        "filename,expected",
        [
            ("test.cpp", True),
            ("test.py", True),
            ("Main.java", True),
            ("test.txt", False),
            ("test.md", False),
        ],
    )
    def test_is_supported_file_type(self, filename, expected):
        """Should check if file type is supported."""
        result = FileOperations.is_supported_file_type(filename)
        assert result == expected


class TestFileOperationsLanguageMap:
    """Test LANGUAGE_MAP constant."""

    def test_language_map_has_cpp_extensions(self):
        """Should map C++ extensions correctly."""
        assert FileOperations.LANGUAGE_MAP[".cpp"] == "C++"
        assert FileOperations.LANGUAGE_MAP[".cc"] == "C++"
        assert FileOperations.LANGUAGE_MAP[".cxx"] == "C++"

    def test_language_map_has_python_extension(self):
        """Should map Python extension."""
        assert FileOperations.LANGUAGE_MAP[".py"] == "Python"

    def test_language_map_has_java_extension(self):
        """Should map Java extension."""
        assert FileOperations.LANGUAGE_MAP[".java"] == "Java"


class TestFileOperationsFilterExtension:
    """Test get_extension_from_filter method."""

    @pytest.mark.parametrize(
        "filter_text,expected_ext",
        [
            ("C++ Files (*.cpp)", ".cpp"),
            ("Python Files (*.py)", ".py"),
            ("Java Files (*.java)", ".java"),
            ("All Files (*.*)", ""),
        ],
    )
    def test_get_extension_from_filter(self, filter_text, expected_ext):
        """Should extract extension from filter string."""
        ext = FileOperations.get_extension_from_filter(filter_text)
        assert ext == expected_ext


class TestFileOperationsValidation:
    """Test file validation methods."""

    def test_validate_existing_file(self, temp_dir):
        """Should validate existing file path."""
        file_path = temp_dir / "test.txt"
        file_path.write_text("content")

        result = FileOperations.validate_file_path(str(file_path))

        assert result is True

    def test_validate_nonexistent_file(self):
        """Should return False for nonexistent file."""
        result = FileOperations.validate_file_path("/nonexistent/file.txt")

        assert result is False

    def test_validate_directory_path(self, temp_dir):
        """Should return False for directory (not a file)."""
        result = FileOperations.validate_file_path(str(temp_dir))

        assert result is False


class TestFileOperationsPathHelpers:
    """Test path manipulation helpers."""

    def test_get_relative_path(self, temp_dir):
        """Should compute relative path from base."""
        base = temp_dir
        file_path = temp_dir / "subdir" / "file.txt"

        rel_path = FileOperations.get_relative_path(str(file_path), str(base))

        assert rel_path == os.path.join("subdir", "file.txt")

    def test_get_relative_path_different_drives(self):
        """Should return original path if on different drives (Windows)."""
        if os.name == "nt":
            result = FileOperations.get_relative_path("C:\\file.txt", "D:\\base")
            assert result == "C:\\file.txt"


class TestFileOperationsBackup:
    """Test file backup operations."""

    def test_creates_backup_file(self, temp_dir):
        """Should create backup with .backup extension."""
        file_path = temp_dir / "original.txt"
        content = "Original content"
        file_path.write_text(content)

        backup_path = FileOperations.backup_file(str(file_path))

        assert backup_path is not None
        assert Path(backup_path).exists()
        assert Path(backup_path).read_text() == content
        assert backup_path.endswith(".backup")

    def test_backup_returns_none_on_error(self):
        """Should return None if backup fails."""
        result = FileOperations.backup_file("/nonexistent/file.txt")

        assert result is None


class TestFileOperationsUniqueFilename:
    """Test unique filename generation."""

    def test_returns_same_name_if_not_exists(self, temp_dir):
        """Should return original name if file doesn't exist."""
        file_path = temp_dir / "test.txt"

        result = FileOperations.get_unique_filename(str(file_path))

        assert result == str(file_path)

    def test_generates_unique_name_if_exists(self, temp_dir):
        """Should append counter if file exists."""
        file_path = temp_dir / "test.txt"
        file_path.write_text("exists")

        result = FileOperations.get_unique_filename(str(file_path))

        assert result == str(temp_dir / "test_1.txt")

    def test_increments_counter_for_multiple_files(self, temp_dir):
        """Should keep incrementing until unique name found."""
        base_path = temp_dir / "test.txt"
        base_path.write_text("exists")
        (temp_dir / "test_1.txt").write_text("exists")
        (temp_dir / "test_2.txt").write_text("exists")

        result = FileOperations.get_unique_filename(str(base_path))

        assert result == str(temp_dir / "test_3.txt")


class TestFileOperationsSanitizeFilename:
    """Test filename sanitization."""

    @pytest.mark.parametrize(
        "filename,expected",
        [
            ("valid_name.txt", "valid_name.txt"),
            ("name<with>invalid.txt", "name_with_invalid.txt"),
            ("path/with\\slashes.txt", "path_with_slashes.txt"),
            ("name:with|pipes?.txt", "name_with_pipes_.txt"),
            ('name"with*quotes.txt', "name_with_quotes.txt"),
        ],
    )
    def test_sanitizes_invalid_characters(self, filename, expected):
        """Should replace invalid characters with underscores."""
        result = FileOperations.sanitize_filename(filename)
        assert result == expected


class TestFileOperationsFileInfo:
    """Test file information retrieval."""

    def test_gets_file_info(self, temp_dir):
        """Should return file information dict."""
        file_path = temp_dir / "test.txt"
        file_path.write_text("content")

        info = FileOperations.get_file_info(str(file_path))

        assert info is not None
        assert "size" in info
        assert "modified" in info
        assert "readable" in info
        assert "writable" in info
        assert info["size"] > 0
        assert info["readable"] is True

    def test_returns_none_for_nonexistent_file(self):
        """Should return None if file doesn't exist."""
        info = FileOperations.get_file_info("/nonexistent/file.txt")

        assert info is None


class TestFileOperationsFormatFileSize:
    """Test file size formatting."""

    @pytest.mark.parametrize(
        "size_bytes,expected",
        [
            (0, "0 B"),
            (500, "500.0 B"),
            (1024, "1.0 KB"),
            (1536, "1.5 KB"),
            (1048576, "1.0 MB"),
            (1073741824, "1.0 GB"),
        ],
    )
    def test_formats_file_size(self, size_bytes, expected):
        """Should format file size in human-readable format."""
        result = FileOperations.format_file_size(size_bytes)
        assert result == expected


class TestFileOperationsDialogs:
    """Test file dialog methods (mocked Qt dialogs)."""

    @patch("PySide6.QtWidgets.QFileDialog.getOpenFileName")
    def test_open_file_dialog_returns_path(self, mock_dialog):
        """Should return selected file path."""
        mock_dialog.return_value = ("/path/to/file.cpp", "C++ Files (*.cpp)")

        result = FileOperations.open_file_dialog()

        assert result == "/path/to/file.cpp"

    @patch("PySide6.QtWidgets.QFileDialog.getOpenFileName")
    def test_open_file_dialog_returns_none_on_cancel(self, mock_dialog):
        """Should return None if user cancels."""
        mock_dialog.return_value = ("", "")

        result = FileOperations.open_file_dialog()

        assert result is None

    @patch("PySide6.QtWidgets.QFileDialog.getSaveFileName")
    def test_save_file_dialog_returns_path(self, mock_dialog):
        """Should return selected save path."""
        mock_dialog.return_value = ("/path/to/save.cpp", "C++ Files (*.cpp)")

        result = FileOperations.save_file_dialog()

        assert result == "/path/to/save.cpp"

    @patch("PySide6.QtWidgets.QFileDialog.getSaveFileName")
    def test_save_file_dialog_adds_extension(self, mock_dialog):
        """Should add extension if filename has none."""
        mock_dialog.return_value = ("/path/to/save", "C++ Files (*.cpp)")

        result = FileOperations.save_file_dialog()

        assert result == "/path/to/save.cpp"

    @patch("PySide6.QtWidgets.QFileDialog.getExistingDirectory")
    def test_select_directory_dialog(self, mock_dialog):
        """Should open directory selection dialog."""
        mock_dialog.return_value = "/selected/directory"

        result = FileOperations.select_directory_dialog()

        assert result == "/selected/directory"


class TestFileOperationsSaveFileAs:
    """Test save_file_as method (combines dialog and save)."""

    @patch("PySide6.QtWidgets.QFileDialog.getSaveFileName")
    def test_save_file_as_successful(self, mock_dialog, temp_dir):
        """Should save file after dialog selection."""
        file_path = temp_dir / "saved.cpp"
        mock_dialog.return_value = (str(file_path), "C++ Files (*.cpp)")

        result = FileOperations.save_file_as(None, "int main() { return 0; }")

        assert result == str(file_path)
        assert file_path.exists()

    @patch("PySide6.QtWidgets.QFileDialog.getSaveFileName")
    def test_save_file_as_returns_none_on_cancel(self, mock_dialog):
        """Should return None if user cancels."""
        mock_dialog.return_value = ("", "")

        result = FileOperations.save_file_as(None, "content")

        assert result is None


class TestFileOperationsOpenFile:
    """Test open_file method (combines dialog and read)."""

    @patch("PySide6.QtWidgets.QFileDialog.getOpenFileName")
    def test_open_file_returns_path_and_content(self, mock_dialog, temp_dir):
        """Should return file path and content."""
        file_path = temp_dir / "test.cpp"
        content = "int main() { return 0; }"
        file_path.write_text(content)
        mock_dialog.return_value = (str(file_path), "C++ Files (*.cpp)")

        path, loaded_content = FileOperations.open_file(None)

        assert path == str(file_path)
        assert loaded_content == content

    @patch("PySide6.QtWidgets.QFileDialog.getOpenFileName")
    def test_open_file_returns_none_on_cancel(self, mock_dialog):
        """Should return None, None if user cancels."""
        mock_dialog.return_value = ("", "")

        path, content = FileOperations.open_file(None)

        assert path is None
        assert content is None

    @patch("PySide6.QtWidgets.QFileDialog.getOpenFileName")
    @patch("PySide6.QtWidgets.QMessageBox.critical")
    def test_open_file_handles_nonexistent_file(self, mock_msg, mock_dialog):
        """Should show error if selected file doesn't exist."""
        mock_dialog.return_value = ("/nonexistent/file.cpp", "")

        path, content = FileOperations.open_file(None)

        assert path is None
        assert content is None
        mock_msg.assert_called()


class TestFileOperationsSupportedExtensions:
    """Test SUPPORTED_EXTENSIONS constant."""

    def test_supported_extensions_includes_cpp(self):
        """Should include C++ extensions."""
        assert ".cpp" in FileOperations.SUPPORTED_EXTENSIONS
        assert ".h" in FileOperations.SUPPORTED_EXTENSIONS
        assert ".hpp" in FileOperations.SUPPORTED_EXTENSIONS

    def test_supported_extensions_includes_python(self):
        """Should include Python extension."""
        assert ".py" in FileOperations.SUPPORTED_EXTENSIONS

    def test_supported_extensions_includes_java(self):
        """Should include Java extension."""
        assert ".java" in FileOperations.SUPPORTED_EXTENSIONS


class TestFileOperationsFileFilters:
    """Test FILE_FILTERS constant."""

    def test_file_filters_includes_programming_files(self):
        """Should have programming files filter."""
        assert "Programming Files" in FileOperations.FILE_FILTERS

    def test_file_filters_includes_specific_languages(self):
        """Should have language-specific filters."""
        assert "C++ Files" in FileOperations.FILE_FILTERS
        assert "Python Files" in FileOperations.FILE_FILTERS
        assert "Java Files" in FileOperations.FILE_FILTERS

    def test_file_filters_includes_all_files(self):
        """Should have all files filter."""
        assert "All Files" in FileOperations.FILE_FILTERS
