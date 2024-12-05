from PySide6.QtWidgets import QFileDialog, QMessageBox, QPushButton
from PySide6.QtGui import QFont, QCloseEvent
from widgets.sidebar import Sidebar
from views.base_window import SidebarWindowBase
from views.code_editor.code_editor_display_area import CodeEditorDisplay
from tools.compiler_runner import CompilerRunner
import os
from PySide6.QtCore import QTimer
from utils.file_operations import FileOperations
import json

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

        # Load previous session files
        self.state_file = os.path.join(os.path.expanduser('~'), '.code_testing_suite', 'editor_state.json')
        self.load_editor_state()

        # Connect signals
        self.sidebar.button_clicked.connect(self.handle_button_click)
        self.editor_display.saveRequested.connect(self.save_file)

        # Connect additional signals for state tracking
        self.editor_display.tab_widget.tabCloseRequested.connect(self.save_editor_state)
        self.editor_display.tab_widget.currentChanged.connect(self.save_editor_state)
        self.editor_display.filePathChanged.connect(self.save_editor_state)

        # Don't call add_new_tab() in __init__ anymore
        # The welcome screen will show by default

    def cleanup(self):
        """Clean up resources"""
        if hasattr(self.editor_display, 'compiler_runner'):
            self.editor_display.compiler_runner.stop_execution()

    def can_close(self):
        """Check if any tab has unsaved changes"""
        if not self.editor_display.has_editor:
            return True
            
        # Check all tabs for unsaved changes
        for i in range(self.editor_display.tab_widget.count()):
            tab = self.editor_display.tab_widget.widget(i)
            if tab and tab.editor.codeEditor.document().isModified():
                return False
        return True

    def closeEvent(self, event: QCloseEvent):
        """Handle window close event"""
        if not self.editor_display.has_editor:
            event.accept()
            self.parent.window_manager.show_window('main')
            return
            
        if self.can_close():
            self.save_editor_state()
            self.cleanup()
            event.accept()
            self.parent.window_manager.show_window('main')
        else:
            result = self.handle_unsaved_changes()
            if result == QMessageBox.Save:
                if self.save_file():  # Only continue if save was successful
                    self.save_editor_state()
                    self.cleanup()
                    event.accept()
                    self.parent.window_manager.show_window('main')
                else:
                    event.ignore()
            elif result == QMessageBox.Discard:
                self.cleanup()
                event.accept()
                self.parent.window_manager.show_window('main')
            else:  # Cancel
                event.ignore()

    def handle_button_click(self, button_text):
        if button_text == 'Help Center':
            self.parent.window_manager.show_window('help_center')
        elif button_text == 'Back':
            self.close()  # This will trigger closeEvent
        elif button_text == 'New File':
            if not self.editor_display.has_editor or not self.editor_display.isCurrentFileModified():
                self.editor_display.add_new_tab()
                self.save_editor_state()
            else:
                self.handle_unsaved_changes()
        elif button_text == 'Open File':
            if not self.editor_display.has_editor or not self.editor_display.isCurrentFileModified():
                self.open_file()
            else:
                if self.handle_unsaved_changes() != QMessageBox.Cancel:
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
        if not self.editor_display.has_editor:
            file_name, content = FileOperations.open_file(self)
            if file_name is not None:
                new_tab = self.editor_display.add_new_tab(os.path.basename(file_name))
                new_tab.editor.currentFilePath = file_name
                new_tab.editor.codeEditor.setPlainText(content or "")
                new_tab.editor.codeEditor._setup_syntax_highlighting(file_name)
                new_tab.editor.codeEditor.document().setModified(False)
                self.save_editor_state()
                return

        if self.editor_display.isCurrentFileModified():
            if not self.handle_unsaved_changes():
                return

        file_name, content = FileOperations.open_file(self)
        if file_name is not None:
            current_editor = self.editor_display.getCurrentEditor()
            if (current_editor and not current_editor.currentFilePath and 
                not current_editor.codeEditor.document().isModified() and 
                not current_editor.codeEditor.toPlainText().strip()):
                self._update_existing_tab(current_editor, file_name, content)
            else:
                self._create_new_tab(file_name, content)
            self.save_editor_state()

    def _update_existing_tab(self, editor, file_path, content):
        editor.currentFilePath = file_path
        editor.codeEditor.setPlainText(content or "")
        editor.codeEditor._setup_syntax_highlighting(file_path)
        editor.codeEditor.document().setModified(False)
        self.editor_display.updateTabTitle(self.editor_display.tab_widget.currentIndex())

    def _create_new_tab(self, file_path, content):
        new_tab = self.editor_display.add_new_tab(os.path.basename(file_path))
        new_tab.editor.currentFilePath = file_path
        new_tab.editor.codeEditor.setPlainText(content or "")
        new_tab.editor.codeEditor._setup_syntax_highlighting(file_path)
        new_tab.editor.codeEditor.document().setModified(False)
        self.editor_display.updateTabTitle(self.editor_display.tab_widget.count() - 1)

    def save_editor_state(self):
        """Save the state of opened files"""
        os.makedirs(os.path.dirname(self.state_file), exist_ok=True)
        
        state = {
            'open_files': []
        }
        
        for i in range(self.editor_display.tab_widget.count()):
            tab = self.editor_display.tab_widget.widget(i)
            if tab and tab.editor.currentFilePath:
                state['open_files'].append(tab.editor.currentFilePath)
        
        with open(self.state_file, 'w') as f:
            json.dump(state, f)

    def load_editor_state(self):
        """Load previously opened files"""
        try:
            if not os.path.exists(self.state_file):
                return  # Let the welcome screen show instead of adding new tab

            with open(self.state_file, 'r') as f:
                state = json.load(f)

            files = state.get('open_files', [])
            if not files:
                return  # No files to load, show welcome screen

            for file_path in files:
                if os.path.exists(file_path):
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                    except Exception as e:
                        print(f"Error reading file {file_path}: {e}")
                        continue

                    # Create new tab for each file
                    new_tab = self.editor_display.add_new_tab(os.path.basename(file_path))
                    new_tab.editor.currentFilePath = file_path
                    new_tab.editor.codeEditor.setPlainText(content)
                    new_tab.editor.codeEditor._setup_syntax_highlighting(file_path)
                    self.editor_display.updateTabTitle(self.editor_display.tab_widget.count() - 1)

        except Exception as e:
            print(f"Error loading editor state: {e}")
            return  # Show welcome screen on error
