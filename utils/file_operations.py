import os
from PySide6.QtWidgets import QFileDialog, QMessageBox

class FileOperations:
    FILE_FILTERS = "Programming Files (*.cpp *.h *.hpp *.py *.java);;" \
                   "C++ Files (*.cpp *.h *.hpp);;" \
                   "Python Files (*.py);;" \
                   "Java Files (*.java);;" \
                   "All Files (*.*)"

    @staticmethod
    def save_file(filepath, content, parent=None):
        try:
            with open(filepath, 'w', encoding='utf-8') as file:
                file.write(content)
            return True
        except Exception as e:
            if parent:
                QMessageBox.critical(parent, "Error", f"Could not save file: {str(e)}")
            return False

    @staticmethod
    def get_extension_from_filter(selected_filter):
        """Get file extension based on filter selection"""
        if 'C++' in selected_filter:
            return '.cpp'
        elif 'Python' in selected_filter:
            return '.py'
        elif 'Java' in selected_filter:
            return '.java'
        return ''

    @staticmethod
    def save_file_as(parent, content, current_path=None):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        file_name, selected_filter = QFileDialog.getSaveFileName(
            parent,
            "Save File",
            current_path or "",
            FileOperations.FILE_FILTERS,
            options=options
        )

        if file_name:
            # Add appropriate extension if none provided
            if '.' not in os.path.basename(file_name):
                file_name += FileOperations.get_extension_from_filter(selected_filter)

            if FileOperations.save_file(file_name, content, parent):
                return file_name
        return None

    @staticmethod
    def open_file(parent):
        try:
            file_name, _ = QFileDialog.getOpenFileName(
                parent,
                "Open File",
                "",
                FileOperations.FILE_FILTERS
            )
            
            if file_name and os.path.exists(file_name):
                try:
                    with open(file_name, 'r', encoding='utf-8') as file:
                        return file_name, file.read()
                except UnicodeDecodeError:
                    # Try alternative encodings if UTF-8 fails
                    try:
                        with open(file_name, 'r', encoding='latin-1') as file:
                            return file_name, file.read()
                    except Exception as e:
                        QMessageBox.critical(parent, "Error", f"Could not decode file: {str(e)}")
                except Exception as e:
                    QMessageBox.critical(parent, "Error", f"Could not read file: {str(e)}")
            elif file_name:  # File was selected but doesn't exist
                QMessageBox.critical(parent, "Error", "File not found")
        except Exception as e:
            QMessageBox.critical(parent, "Error", f"Error opening file: {str(e)}")
        
        return None, None

    @staticmethod
    def load_file(file_path, parent=None):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            # Log or display an error message as needed
            return None
