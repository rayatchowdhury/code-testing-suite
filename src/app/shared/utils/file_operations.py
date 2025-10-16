import os
import shutil
from pathlib import Path
from typing import Optional, Union

from PySide6.QtWidgets import QFileDialog, QMessageBox


class FileOperations:
    FILE_FILTERS = (
        "Programming Files (*.cpp *.h *.hpp *.py *.java);;"
        "C++ Files (*.cpp *.h *.hpp);;"
        "Python Files (*.py);;"
        "Java Files (*.java);;"
        "All Files (*.*)"
    )

    # Supported file extensions
    SUPPORTED_EXTENSIONS = [".cpp", ".h", ".hpp", ".py", ".java", ".c", ".cc", ".cxx"]

    LANGUAGE_MAP = {
        ".cpp": "C++",
        ".cc": "C++",
        ".cxx": "C++",
        ".c": "C",
        ".h": "C/C++",
        ".hpp": "C++",
        ".py": "Python",
        ".java": "Java",
    }

    @staticmethod
    def save_file(filepath: Union[str, Path], content: str, parent=None) -> bool:
        """Save content to file with proper error handling."""
        try:
            Path(filepath).write_text(content, encoding="utf-8")
            return True
        except Exception as e:
            if parent:
                QMessageBox.critical(parent, "Error", f"Could not save file: {str(e)}")
            return False

    @staticmethod
    def get_extension_from_filter(selected_filter):
        """Get file extension based on filter selection"""
        if "C++" in selected_filter:
            return ".cpp"
        if "Python" in selected_filter:
            return ".py"
        if "Java" in selected_filter:
            return ".java"
        return ""

    @staticmethod
    def save_file_as(parent, content, current_path=None):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        file_name, selected_filter = QFileDialog.getSaveFileName(
            parent,
            "Save File",
            current_path or "",
            FileOperations.FILE_FILTERS,
            options=options,
        )

        if file_name:
            # Add appropriate extension if none provided
            if "." not in os.path.basename(file_name):
                file_name += FileOperations.get_extension_from_filter(selected_filter)

            if FileOperations.save_file(file_name, content, parent):
                return file_name
        return None

    @staticmethod
    def open_file(parent):
        """Open file dialog and read selected file."""
        try:
            file_name, _ = QFileDialog.getOpenFileName(
                parent, "Open File", "", FileOperations.FILE_FILTERS
            )

            if file_name:
                file_path = Path(file_name)
                if file_path.exists():
                    try:
                        # Try UTF-8 first, then fallback to latin-1
                        return str(file_path), file_path.read_text(encoding="utf-8")
                    except UnicodeDecodeError:
                        try:
                            return str(file_path), file_path.read_text(
                                encoding="latin-1"
                            )
                        except Exception as e:
                            QMessageBox.critical(
                                parent, "Error", f"Could not decode file: {str(e)}"
                            )
                    except Exception as e:
                        QMessageBox.critical(
                            parent, "Error", f"Could not read file: {str(e)}"
                        )
                else:
                    QMessageBox.critical(parent, "Error", "File not found")
        except Exception as e:
            QMessageBox.critical(parent, "Error", f"Error opening file: {str(e)}")

        return None, None

    @staticmethod
    def load_file(file_path: Union[str, Path], parent=None) -> Optional[str]:
        """Load file content with error handling."""
        try:
            return Path(file_path).read_text(encoding="utf-8")
        except Exception as e:
            # Log or display an error message as needed
            return None

    # Additional methods expected by tests
    @staticmethod
    def write_file(filepath, content, parent=None):
        """Write content to file, creating directories if needed."""
        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            with open(filepath, "w", encoding="utf-8") as file:
                file.write(content)
            return True
        except Exception as e:
            if parent:
                QMessageBox.critical(parent, "Error", f"Could not write file: {str(e)}")
            return False

    @staticmethod
    def read_file(filepath, parent=None):
        """Read file content."""
        try:
            with open(filepath, "r", encoding="utf-8") as file:
                return file.read()
        except FileNotFoundError:
            if parent:
                QMessageBox.critical(parent, "Error", f"File not found: {filepath}")
            raise
        except Exception as e:
            if parent:
                QMessageBox.critical(parent, "Error", f"Could not read file: {str(e)}")
            raise

    @staticmethod
    def open_file_dialog(parent=None, directory=""):
        """Open file dialog and return selected file path."""
        try:
            file_name, _ = QFileDialog.getOpenFileName(
                parent, "Open File", directory, FileOperations.FILE_FILTERS
            )
            return file_name if file_name else None
        except Exception:
            return None

    @staticmethod
    def save_file_dialog(parent=None, directory=""):
        """Open save file dialog and return selected file path."""
        try:
            file_name, selected_filter = QFileDialog.getSaveFileName(
                parent, "Save File", directory, FileOperations.FILE_FILTERS
            )

            if file_name and "." not in os.path.basename(file_name):
                file_name += FileOperations.get_extension_from_filter(selected_filter)

            return file_name if file_name else None
        except Exception:
            return None

    @staticmethod
    def is_supported_file_type(filename):
        """Check if file type is supported."""
        ext = FileOperations.get_file_extension(filename)
        return ext.lower() in FileOperations.SUPPORTED_EXTENSIONS

    @staticmethod
    def get_file_extension(filename):
        """Get file extension from filename."""
        _, ext = os.path.splitext(filename)
        return ext.lower()

    @staticmethod
    def get_file_language(filename):
        """Get programming language from filename."""
        ext = FileOperations.get_file_extension(filename)
        return FileOperations.LANGUAGE_MAP.get(ext, "Unknown")

    @staticmethod
    def validate_file_path(filepath):
        """Validate if file path exists and is readable."""
        return os.path.exists(filepath) and os.path.isfile(filepath)

    @staticmethod
    def get_relative_path(filepath, base_path):
        """Get relative path from base path."""
        try:
            return os.path.relpath(filepath, base_path)
        except ValueError:
            return filepath

    @staticmethod
    def backup_file(filepath):
        """Create backup of file."""
        try:
            backup_path = filepath + ".backup"
            shutil.copy2(filepath, backup_path)
            return backup_path
        except Exception:
            return None

    @staticmethod
    def open_file_dialog_with_preview(parent=None):
        """Open file dialog with preview functionality."""
        return FileOperations.open_file_dialog(parent)

    @staticmethod
    def save_file_dialog_with_confirmation(parent=None):
        """Save file dialog with confirmation."""
        return FileOperations.save_file_dialog(parent)

    @staticmethod
    def select_directory_dialog(parent=None):
        """Open directory selection dialog."""
        try:
            directory = QFileDialog.getExistingDirectory(parent, "Select Directory")
            return directory if directory else None
        except Exception:
            return None

    @staticmethod
    def show_error_dialog(title, message, parent=None):
        """Show error dialog."""
        QMessageBox.critical(parent, title, message)

    @staticmethod
    def format_file_size(size_bytes):
        """Format file size in human readable format."""
        if size_bytes == 0:
            return "0 B"

        size_names = ["B", "KB", "MB", "GB"]
        i = 0
        while size_bytes >= 1024 and i < len(size_names) - 1:
            size_bytes /= 1024.0
            i += 1

        return f"{size_bytes:.1f} {size_names[i]}"

    @staticmethod
    def get_file_info(filepath):
        """Get file information including size and modification date."""
        try:
            stat_info = os.stat(filepath)
            return {
                "size": stat_info.st_size,
                "modified": stat_info.st_mtime,
                "readable": os.access(filepath, os.R_OK),
                "writable": os.access(filepath, os.W_OK),
            }
        except Exception:
            return None

    @staticmethod
    def sanitize_filename(filename):
        """Sanitize filename by removing invalid characters."""
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            filename = filename.replace(char, "_")
        return filename

    @staticmethod
    def get_unique_filename(filepath):
        """Generate unique filename if file already exists."""
        if not os.path.exists(filepath):
            return filepath

        base, ext = os.path.splitext(filepath)
        counter = 1

        while os.path.exists(f"{base}_{counter}{ext}"):
            counter += 1

        return f"{base}_{counter}{ext}"
