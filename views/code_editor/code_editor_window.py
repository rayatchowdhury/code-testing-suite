from PySide6.QtWidgets import QFileDialog, QMessageBox, QPushButton
from PySide6.QtGui import QFont, QCloseEvent
from widgets.sidebar import Sidebar
from views.base_window import SidebarWindowBase
from views.code_editor.code_editor_display_area import CodeEditorDisplay
from tools.compiler_runner import CompilerRunner
import os
from PySide6.QtCore import QTimer
from utils.file_operations import FileOperations

class CodeEditorWindow(SidebarWindowBase):
    def __init__(self, parent=None):
        super().__init__(parent)

        # Create sidebar
        self.sidebar = Sidebar("Code Editor")
        
        main_section = self.sidebar.add_section("File Operations")
        for button_text in ['New File', 'Open File', 'Save File']:  # Removed 'Run Code'
            self.sidebar.add_button(button_text, main_section)
        
        # Add footer items
        self.sidebar.add_help_button()
        self.sidebar.add_footer_divider()
        
        # Create buttons
        back_btn = QPushButton("Back")
        back_btn.setObjectName("back_button")
        back_btn.clicked.connect(lambda: self.handle_button_click("Back"))
        
        options_btn = QPushButton("⚙️")
        options_btn.setObjectName("back_button")
        options_btn.setFont(QFont('Segoe UI', 14))
        options_btn.clicked.connect(lambda: self.handle_button_click("Options"))
        
        # Setup horizontal footer buttons
        self.sidebar.setup_horizontal_footer_buttons(back_btn, options_btn)

        # Create editor display
        self.editor_display = CodeEditorDisplay()

        # Setup splitter
        self.setup_splitter(self.sidebar, self.editor_display)

        # Connect signals
        self.sidebar.button_clicked.connect(self.handle_button_click)
        self.editor_display.saveRequested.connect(self.save_file)

    def cleanup(self):
        """Clean up resources"""
        if hasattr(self.editor_display, 'compiler_runner'):
            self.editor_display.compiler_runner.stop_execution()

    def can_close(self):
        """Check if window can be closed"""
        return not self.editor_display.isCurrentFileModified()

    def closeEvent(self, event: QCloseEvent):
        """Handle window close event"""
        if self.can_close():
            self.cleanup()
            event.accept()
            self.parent.window_manager.show_window('main')
        else:
            result = self.handle_unsaved_changes()
            if result != QMessageBox.Cancel:
                self.cleanup()
                event.accept()
                self.parent.window_manager.show_window('main')
            else:
                event.ignore()

    def handle_button_click(self, button_text):
        if button_text == 'Help Center':
            self.parent.window_manager.show_window('help_center')
        elif button_text == 'Back':
            self.close()  # This will trigger closeEvent
        elif button_text == 'New File':
            if self.editor_display.isCurrentFileModified():
                self.handle_unsaved_changes()
            self.editor_display.add_new_tab()
        elif button_text == 'Open File':
            self.open_file()
        elif button_text == 'Save File':
            # Just delegate to the editor's save functionality
            self.save_file()
        elif button_text == 'Options':
            super().handle_button_click(button_text)

    def handle_unsaved_changes(self):
        reply = QMessageBox.question(
            self, 'Save Changes?',
            'Do you want to save your changes?',
            QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel
        )

        if reply == QMessageBox.Save:
            self.save_file()
        return reply != QMessageBox.Cancel

    def save_file(self):
        """Delegate save operation to current editor widget"""
        editor = self.editor_display.getCurrentEditor()
        if editor:
            return editor.saveFile()
        return False

    def open_file(self):
        if self.editor_display.isCurrentFileModified():
            if not self.handle_unsaved_changes():
                return

        file_name, content = FileOperations.open_file(self)
        if file_name and content:
            new_tab = self.editor_display.add_new_tab(os.path.basename(file_name))
            new_tab.editor.codeEditor.setPlainText(content)
            new_tab.editor.currentFilePath = file_name
            new_tab.editor.codeEditor._setup_syntax_highlighting(file_name)
            self.editor_display.updateTabTitle(self.editor_display.tab_widget.currentIndex())
            new_tab.editor.codeEditor.document().setModified(False)
