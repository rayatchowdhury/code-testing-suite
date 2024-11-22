from PySide6.QtWidgets import QWidget, QHBoxLayout, QFileDialog, QMessageBox
from widgets.sidebar import Sidebar
from widgets.display_area_widgets.editor import EditorWidget
import subprocess
import os


class CodeEditorWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Create sidebar and editor directly
        self.sidebar = Sidebar("Code Editor")
        self.editor_widget = EditorWidget()
        self.current_file = None

        # Add buttons to sidebar
        main_section = self.sidebar.add_section("File Operations")
        for button_text in ['New File', 'Open File', 'Save File', 'Run Code']:
            self.sidebar.add_button(button_text, main_section)
        self.sidebar.add_back_button()

        # Add widgets directly to layout
        layout.addWidget(self.sidebar)
        layout.addWidget(self.editor_widget)

        # Connect signals
        self.sidebar.button_clicked.connect(self.handle_button_click)

    def handle_button_click(self, button_text):
        if button_text == 'Back':
            self.parent.return_to_main()
        elif button_text == 'New File':
            self.new_file()
        elif button_text == 'Open File':
            self.open_file()
        elif button_text == 'Save File':
            self.save_file()
        elif button_text == 'Run Code':
            self.run_code()

    def new_file(self):
        if self.editor_widget.codeEditor.document().isModified():
            reply = QMessageBox.question(self, 'Save Changes?',
                                         'Do you want to save your changes before creating a new file?',
                                         QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel)

            if reply == QMessageBox.Save:
                self.save_file()
            elif reply == QMessageBox.Cancel:
                return

        self.editor_widget.codeEditor.clear()
        self.current_file = None

    def open_file(self):
        if self.editor_widget.codeEditor.document().isModified():
            reply = QMessageBox.question(self, 'Save Changes?',
                                         'Do you want to save your changes before opening another file?',
                                         QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel)

            if reply == QMessageBox.Save:
                self.save_file()
            elif reply == QMessageBox.Cancel:
                return

        file_name, _ = QFileDialog.getOpenFileName(self, "Open File", "",
                                                   "C++ Files (*.cpp *.h);;All Files (*)")
        if file_name:
            try:
                with open(file_name, 'r') as file:
                    self.editor_widget.codeEditor.setPlainText(file.read())
                    self.current_file = file_name
            except Exception as e:
                QMessageBox.critical(
                    self, "Error", f"Could not open file: {str(e)})")

    def save_file(self):
        if not self.current_file:
            file_name, _ = QFileDialog.getSaveFileName(self, "Save File", "",
                                                       "C++ Files (*.cpp *.h);;All Files (*)")
            if file_name:
                self.current_file = file_name
            else:
                return

        try:
            with open(self.current_file, 'w') as file:
                file.write(self.editor_widget.getCode())
            self.editor_widget.codeEditor.document().setModified(False)
        except Exception as e:
            QMessageBox.critical(
                self, "Error", f"Could not save file: {str(e)}))")

    def run_code(self):
        if self.editor_widget.codeEditor.document().isModified() or not self.current_file:
            reply = QMessageBox.question(self, 'Save Required',
                                         'The file needs to be saved before running. Save now?',
                                         QMessageBox.Yes | QMessageBox.Cancel)

            if reply == QMessageBox.Yes:
                self.save_file()
            else:
                return

        if not self.current_file:
            QMessageBox.warning(self, "Warning", "Please save the file first")
            return

        try:
            # Compile
            compile_process = subprocess.run(['g++', self.current_file, '-o',
                                              os.path.splitext(self.current_file)[0]],
                                             capture_output=True, text=True)

            if compile_process.returncode != 0:
                QMessageBox.critical(
                    self, "Compilation Error", compile_process.stderr)
                return

            # Run
            run_process = subprocess.run([os.path.splitext(self.current_file)[0]],
                                         capture_output=True, text=True)

            if run_process.returncode == 0:
                QMessageBox.information(self, "Output", run_process.stdout)
            else:
                QMessageBox.critical(self, "Runtime Error", run_process.stderr)

        except Exception as e:
            QMessageBox.critical(
                self, "Error", f"Error running code: {str(e)})")
