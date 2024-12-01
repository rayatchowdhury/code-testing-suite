from PySide6.QtWidgets import QWidget, QHBoxLayout, QFileDialog, QMessageBox, QSplitter
from PySide6.QtCore import Qt
from widgets.sidebar import Sidebar
from widgets.display_area_widgets.editor_window import EditorWindow
import subprocess
import os
from views.base_window import SidebarWindowBase


class CodeEditorWindow(SidebarWindowBase):
    def __init__(self, parent=None):
        super().__init__(parent)

        # Create sidebar
        self.sidebar = Sidebar("Code Editor")
        
        main_section = self.sidebar.add_section("File Operations")
        for button_text in ['New File', 'Open File', 'Save File', 'Run Code']:
            self.sidebar.add_button(button_text, main_section)
        self.sidebar.add_back_button()

        # Create editor window
        self.editor_window = EditorWindow()
        self.current_file = None

        # Setup splitter
        self.setup_splitter(self.sidebar, self.editor_window)

        # Connect signals
        self.sidebar.button_clicked.connect(self.handle_button_click)
        self.editor_window.compile_btn.clicked.connect(self.compile_code)
        self.editor_window.run_btn.clicked.connect(self.run_code)

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
        if self.editor_window.codeEditor.document().isModified():
            reply = QMessageBox.question(self, 'Save Changes?',
                                         'Do you want to save your changes before creating a new file?',
                                         QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel)

            if reply == QMessageBox.Save:
                self.save_file()
            elif reply == QMessageBox.Cancel:
                return

        self.editor_window.codeEditor.clear()
        self.current_file = None

    def open_file(self):
        if self.editor_window.codeEditor.document().isModified():
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
                    self.editor_window.codeEditor.setPlainText(file.read())
                    self.editor_window.currentFilePath = file_name
                    self.editor_window.updateTitleBar()
            except Exception as e:
                QMessageBox.critical(
                    self, "Error", f"Could not open file: {str(e)})")

    def save_file(self):
        if not self.current_file:
            file_name, _ = QFileDialog.getSaveFileName(self, "Save File", "",
                                                       "C++ Files (*.cpp *.h);;All Files (*)")
            if file_name:
                self.current_file = file_name
                self.editor_window.currentFilePath = file_name
                self.editor_window.updateTitleBar()
            else:
                return

        try:
            with open(self.current_file, 'w') as file:
                file.write(self.editor_window.getCode())
            self.editor_window.codeEditor.document().setModified(False)
        except Exception as e:
            QMessageBox.critical(
                self, "Error", f"Could not save file: {str(e)}))")

    def compile_code(self):
        if not self.current_file:
            self.save_file()  # Save file if not saved
            if not self.current_file:  # If user cancelled save
                return

        try:
            compile_process = subprocess.run(['g++', self.current_file, '-o',
                                           os.path.splitext(self.current_file)[0]],
                                           capture_output=True, text=True)
            
            if compile_process.returncode == 0:
                self.editor_window.console.displayOutput("Compilation successful!")
            else:
                self.editor_window.console.displayOutput(f"Compilation Error:\n{compile_process.stderr}")
        
        except Exception as e:
            self.editor_window.console.displayOutput(f"Error: {str(e)}")

    def run_code(self):
        if not self.current_file or not os.path.exists(os.path.splitext(self.current_file)[0]):
            self.compile_code()
            if not self.current_file:  # If compilation failed or was cancelled
                return

        try:
            run_process = subprocess.run([os.path.splitext(self.current_file)[0]],
                                       capture_output=True, text=True)
            
            self.editor_window.console.displayOutput("Program Output:")
            self.editor_window.console.displayOutput(run_process.stdout)
            
            if run_process.returncode != 0:
                self.editor_window.console.displayOutput(f"Runtime Error:\n{run_process.stderr}")
        
        except Exception as e:
            self.editor_window.console.displayOutput(f"Error: {str(e)}")
