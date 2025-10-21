import json
import logging
import os
from datetime import datetime

from PySide6.QtCore import QTimer
from PySide6.QtGui import QCloseEvent, QFont, QShowEvent
from PySide6.QtWidgets import (
    QMainWindow,
    QVBoxLayout,
    QWidget,
    QMessageBox,
    QFileDialog,
    QPushButton,
)
from PySide6.QtCore import QEvent
from PySide6.QtGui import QCloseEvent
from src.app.presentation.services.navigation_service import NavigationService

logger = logging.getLogger(__name__)

from src.app.core.tools.compiler_runner import CompilerRunner
from src.app.presentation.views.code_editor.code_editor_display_area import (
    CodeEditorDisplay,
)
from src.app.presentation.widgets.sidebar import Sidebar
from src.app.presentation.window_controller.base_window import SidebarWindowBase
from src.app.shared.constants import EDITOR_STATE_FILE
from src.app.shared.utils.file_operations import FileOperations

class CodeEditorWindow(SidebarWindowBase):
    def __init__(self, parent=None):
        super().__init__(parent)

        # Lazy import for database manager for session management
        from src.app.persistence.database import DatabaseManager

        self.db_manager = DatabaseManager()

        # Create sidebar
        self.sidebar = Sidebar("Code Editor")

        main_section = self.sidebar.add_section("File Operations")
        for button_text in ["New File", "Open File", "Save File"]:  # Removed 'Run Code'
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
        options_btn.setFont(QFont("Segoe UI", 14))
        options_btn.clicked.connect(lambda: self.handle_button_click("Options"))

        # Setup horizontal footer buttons
        self.sidebar.setup_horizontal_footer_buttons(back_btn, options_btn)

        # Create editor display
        self.editor_display = CodeEditorDisplay()

        # Setup splitter
        self.setup_splitter(self.sidebar, self.editor_display)

        # Load previous session files
        self.state_file = EDITOR_STATE_FILE
        self.load_editor_state()

        # Connect signals
        self.sidebar.button_clicked.connect(self.handle_button_click)
        # Remove saveRequested connection since we removed that signal

        # Connect additional signals for state tracking
        self.editor_display.tab_widget.tabCloseRequested.connect(self.save_editor_state)
        self.editor_display.tab_widget.currentChanged.connect(self.save_editor_state)
        self.editor_display.filePathChanged.connect(self.save_editor_state)

        # Don't call add_new_tab() in __init__ anymore
        # The welcome screen will show by default

    def showEvent(self, event):
        """Handle window show event - reload AI config and refresh AI panels"""
        super().showEvent(event)
        # Reload AI configuration to pick up any changes made while window was closed
        try:
            from src.app.core.ai import reload_ai_config

            reload_ai_config()
        except ImportError:
            pass  # AI module not available

        # Refresh AI panels with current configuration
        self.refresh_ai_panels()

    def cleanup(self):
        """Clean up resources"""
        if hasattr(self.editor_display, "compiler_runner"):
            self.editor_display.compiler_runner.stop_execution()

    def refresh_ai_panels(self):
        """Refresh AI panel visibility based on current configuration"""
        # Refresh AI panels in all editor tabs
        for i in range(self.editor_display.tab_widget.count()):
            tab = self.editor_display.tab_widget.widget(i)
            if tab and hasattr(tab.editor, "ai_panel"):
                # Get the AI panel (this will initialize it if needed)
                ai_panel = tab.editor.get_ai_panel()
                if ai_panel:
                    ai_panel.refresh_visibility()

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
        """Handle window close event with improved unsaved changes check"""
        if not self.editor_display.has_editor:
            event.accept()
            NavigationService.instance().navigate_to("main")
            return

        # Check for any unsaved changes
        has_unsaved = any(
            self.editor_display.tab_widget.widget(i)
            .editor.codeEditor.document()
            .isModified()
            for i in range(self.editor_display.tab_widget.count())
        )

        if not has_unsaved:
            self.cleanup()
            event.accept()
            NavigationService.instance().navigate_to("main")
            return

        # Handle unsaved changes
        result = self.handle_unsaved_changes()
        if result == QMessageBox.Save:  # Save was successful
            self.save_editor_state()
            self.cleanup()
            event.accept()
            NavigationService.instance().navigate_to("main")
        elif result == QMessageBox.Discard:
            self.cleanup()
            event.accept()
            NavigationService.instance().navigate_to("main")
        else:  # Cancel or save failed
            event.ignore()

    def handle_button_click(self, button_text):
        if button_text == "Help Center":
            NavigationService.instance().navigate_to("help_center")
        elif button_text == "Back":
            self.close()  # This will trigger closeEvent
        elif button_text == "New File":
            if (
                not self.editor_display.has_editor
                or not self.editor_display.isCurrentFileModified()
            ):
                self.editor_display.add_new_tab()
                self.save_editor_state()
            else:
                self.handle_unsaved_changes()
        elif button_text == "Open File":
            if (
                not self.editor_display.has_editor
                or not self.editor_display.isCurrentFileModified()
            ):
                self.open_file()
            else:
                if self.handle_unsaved_changes() != QMessageBox.Cancel:
                    self.open_file()
        elif button_text == "Save File":
            editor = self.editor_display.getCurrentEditor()
            if editor:
                editor.saveFile()
        elif button_text == "Options":
            super().handle_button_click(button_text)

    def handle_unsaved_changes(self):
        """Handle unsaved changes with a dialog"""
        # Count unsaved files
        unsaved_count = sum(
            1
            for i in range(self.editor_display.tab_widget.count())
            if self.editor_display.tab_widget.widget(i)
            .editor.codeEditor.document()
            .isModified()
        )

        if unsaved_count > 1:
            message = (
                f"You have {unsaved_count} unsaved files. Do you want to save them?"
            )
        else:
            message = "Do you want to save your changes?"

        reply = QMessageBox.question(
            self,
            "Save Changes?",
            message,
            QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel,
        )

        if reply == QMessageBox.Save:
            return self._save_all_modified()
        return reply

    def _save_all_modified(self):
        """Save all modified files"""
        success = True
        for i in range(self.editor_display.tab_widget.count()):
            tab = self.editor_display.tab_widget.widget(i)
            if tab.editor.codeEditor.document().isModified():
                if not tab.editor.saveFile():
                    success = False
                    break
        return QMessageBox.Save if success else QMessageBox.Cancel

    def save_file(self):
        """Delegate save operation to current editor widget"""
        editor = self.editor_display.getCurrentEditor()
        if editor:
            return editor.saveFile()
        return False

    def open_file(self):
        """Handle opening a file with improved logic"""
        # Check for unsaved changes first
        if (
            self.editor_display.has_editor
            and self.editor_display.isCurrentFileModified()
        ):
            if self.handle_unsaved_changes() == QMessageBox.Cancel:
                return

        # Open file dialog
        file_name, content = FileOperations.open_file(self)
        if file_name is None:
            return

        # Try to reuse current tab if it's empty and untitled
        current_editor = self.editor_display.getCurrentEditor()
        if (
            self.editor_display.has_editor
            and current_editor
            and not current_editor.currentFilePath
            and not current_editor.codeEditor.document().isModified()
            and not current_editor.codeEditor.toPlainText().strip()
        ):
            self._update_existing_tab(current_editor, file_name, content)
        else:
            self._create_new_tab(file_name, content)

        self.save_editor_state()

    def _update_existing_tab(self, editor, file_path, content):
        editor.currentFilePath = file_path
        editor.codeEditor.setPlainText(content or "")
        editor.codeEditor._setup_syntax_highlighting(file_path)
        editor.codeEditor.document().setModified(False)
        self.editor_display.updateTabTitle(
            self.editor_display.tab_widget.currentIndex()
        )

    def _create_new_tab(self, file_path, content):
        new_tab = self.editor_display.add_new_tab(os.path.basename(file_path))
        new_tab.editor.currentFilePath = file_path
        new_tab.editor.codeEditor.setPlainText(content or "")
        new_tab.editor.codeEditor._setup_syntax_highlighting(file_path)
        new_tab.editor.codeEditor.document().setModified(False)
        self.editor_display.updateTabTitle(self.editor_display.tab_widget.count() - 1)

    def save_editor_state(self):
        """Save the state of opened files to both JSON and database"""
        # Save to traditional JSON file for backwards compatibility
        os.makedirs(os.path.dirname(self.state_file), exist_ok=True)

        state = {"open_files": []}

        open_files = []
        current_file = None

        for i in range(self.editor_display.tab_widget.count()):
            tab = self.editor_display.tab_widget.widget(i)
            if tab and tab.editor.currentFilePath:
                state["open_files"].append(tab.editor.currentFilePath)
                open_files.append(tab.editor.currentFilePath)

                # Track the current active file
                if i == self.editor_display.tab_widget.currentIndex():
                    current_file = tab.editor.currentFilePath

        # Save to JSON file
        with open(self.state_file, "w") as f:
            json.dump(state, f)

        # Save to database
        if open_files:
            # Lazy import
            from src.app.persistence.database import Session

            session = Session(
                session_name=f"Editor Session {datetime.now().strftime('%Y-%m-%d %H:%M')}",
                open_files=json.dumps(open_files),
                active_file=current_file or "",
                timestamp=datetime.now().isoformat(),
                project_name="Code Editor",
            )
            try:
                self.db_manager.save_session(session)
            except Exception as e:
                logger.error(f"Error saving session to database: {e}", exc_info=True)

    def load_editor_state(self):
        """Load previously opened files"""
        try:
            if not os.path.exists(self.state_file):
                return  # Let the welcome screen show instead of adding new tab

            with open(self.state_file, "r") as f:
                state = json.load(f)

            files = state.get("open_files", [])
            if not files:
                return  # No files to load, show welcome screen

            for file_path in files:
                if os.path.exists(file_path):
                    try:
                        with open(file_path, "r", encoding="utf-8") as f:
                            content = f.read()
                    except Exception as e:
                        logger.error(f"Error reading file {file_path}: {e}", exc_info=True)
                        continue

                    # Create new tab for each file
                    new_tab = self.editor_display.add_new_tab(
                        os.path.basename(file_path)
                    )
                    new_tab.editor.currentFilePath = file_path
                    new_tab.editor.codeEditor.setPlainText(content)
                    new_tab.editor.codeEditor._setup_syntax_highlighting(file_path)
                    self.editor_display.updateTabTitle(
                        self.editor_display.tab_widget.count() - 1
                    )

        except Exception as e:
            logger.error(f"Error loading editor state: {e}", exc_info=True)
            return  # Show welcome screen on error
