"""
Main Window Module

This module contains the main application window with sidebar navigation and display area.
Provides a clean interface for navigating between different application features.

Features:
- Sidebar with organized sections (Editor, Tests, History)
- Display area with glassmorphism welcome document
- Window management and navigation
- Unsaved changes detection on exit
"""

import logging
import sys
from typing import Optional

from PySide6.QtCore import QTimer, Signal
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QMainWindow, QMessageBox, QPushButton

logger = logging.getLogger(__name__)

from src.app.presentation.widgets.display_area import DisplayArea
from src.app.presentation.widgets.sidebar import Sidebar
from src.app.presentation.window_controller.base_window import SidebarWindowBase

class MainWindowConfig:
    """Configuration constants for the main window"""

    # Window properties
    WINDOW_TITLE = "Code Testing Suite"
    MIN_WIDTH = 1100
    MIN_HEIGHT = 700

    # Sidebar sections and buttons
    SIDEBAR_SECTIONS = {
        "Editor": ["Code Editor"],
        "Tests": ["Compare", "Validate", "Benchmark"],
    }

    # Window mapping for navigation
    WINDOW_MAPPING = {
        "Compare": "comparator",
        "Benchmark": "benchmarker",
        "Validate": "validator",
    }

    # Options button settings
    OPTIONS_ICON = "⚙️"
    OPTIONS_FONT_SIZE = 14

    # Timing constants
    CONTENT_INIT_DELAY = 0
    SPLITTER_UPDATE_DELAY = 100

class MainWindowContent(SidebarWindowBase):
    """Main window content with sidebar navigation and display area"""

    button_clicked = Signal(str)

    def __init__(self, parent: Optional[QMainWindow] = None):
        super().__init__(parent)
        self.main_content_widget: Optional[object] = None
        self._content_initialized = False

        self._setup_sidebar()
        self._setup_display_area()
        self._setup_layout()
        self._connect_signals()

    def _setup_sidebar(self) -> None:
        """Create and configure the sidebar with all sections and buttons"""
        self.sidebar = Sidebar(MainWindowConfig.WINDOW_TITLE)

        for section_name, buttons in MainWindowConfig.SIDEBAR_SECTIONS.items():
            section = self.sidebar.add_section(section_name)
            for button_name in buttons:
                self.sidebar.add_button(button_name, section)

        self.sidebar.add_results_button()
        self.sidebar.add_footer_button_divider()
        self.sidebar.add_help_button()
        self.sidebar.add_footer_divider()

        exit_btn = self._create_footer_button("Exit", self._handle_exit_request)
        options_btn = self._create_options_button()

        self.sidebar.setup_horizontal_footer_buttons(exit_btn, options_btn)

    def _create_footer_button(self, text: str, handler) -> QPushButton:
        """Create a standardized footer button"""
        button = QPushButton(text)
        button.setObjectName("back_button")
        button.clicked.connect(handler)
        return button

    def _create_options_button(self) -> QPushButton:
        """Create the options button with emoji icon"""
        button = QPushButton(MainWindowConfig.OPTIONS_ICON)
        button.setObjectName("back_button")
        button.setFont(QFont("Segoe UI", MainWindowConfig.OPTIONS_FONT_SIZE))
        button.clicked.connect(lambda: self.handle_button_click("Options"))
        return button

    def _setup_display_area(self) -> None:
        """Create and configure the display area"""
        self.display_area = DisplayArea()
        QTimer.singleShot(
            MainWindowConfig.CONTENT_INIT_DELAY, self._init_content_widget
        )

    def _setup_layout(self) -> None:
        """Setup the main layout with splitter"""
        self.setup_splitter(self.sidebar, self.display_area)
        QTimer.singleShot(
            MainWindowConfig.SPLITTER_UPDATE_DELAY, self.update_splitter_sizes
        )

    def _connect_signals(self) -> None:
        """Connect all necessary signals"""
        self.sidebar.button_clicked.connect(self.handle_button_click)

    def _init_content_widget(self) -> None:
        """Initialize main window document widget asynchronously"""
        if self._content_initialized:
            return

        try:
            from src.app.presentation.views.main_window.document import (
                create_main_window_document,
            )

            self.main_content_widget = create_main_window_document()
            self.display_area.layout.addWidget(self.main_content_widget)
            self._content_initialized = True

        except Exception as e:
            logger.error(f"Error initializing content widget: {e}", exc_info=True)

    def _handle_exit_request(self) -> None:
        """Handle exit request from footer button"""
        self._close_parent_window()

    def _close_parent_window(self) -> None:
        """Close the parent window or exit application"""
        if self.parent:
            self.parent.close()
        else:
            sys.exit()

    def handle_button_click(self, button_text: str) -> None:
        """Handle button clicks with improved organization"""
        handlers = {
            "Exit": self._close_parent_window,
            "Options": self._show_options_dialog,
        }

        # Handle special buttons
        if button_text in handlers:
            handlers[button_text]()
            return

        # Handle navigation buttons
        if button_text in [
            "Code Editor",
            "Compare",
            "Benchmark",
            "Validate",
            "Results",
            "Help Center",
        ]:
            self._navigate_to_window(button_text)

    def _show_options_dialog(self) -> None:
        """Show the configuration options dialog"""
        try:
            from src.app.core.config import ConfigView

            config_dialog = ConfigView(self)
            config_dialog.exec()
        except Exception as e:
            logger.error(f"Error opening options dialog: {e}", exc_info=True)

    def _navigate_to_window(self, button_text: str) -> None:
        """Navigate to the specified window"""
        if not (self.parent and hasattr(self.parent, "window_manager")):
            logger.warning(f"Cannot navigate to {button_text}: No window manager available")
            return

        window_name = MainWindowConfig.WINDOW_MAPPING.get(
            button_text, button_text.lower().replace(" ", "_")
        )

        try:
            from src.app.presentation.services.navigation_service import NavigationService
            NavigationService.instance().navigate_to(window_name)
        except Exception as e:
            logger.error(f"Error navigating to {window_name}: {e}", exc_info=True)

    # Deprecated method kept for backwards compatibility
    def handle_exit(self) -> None:
        """Handle exit button click (deprecated - use _handle_exit_request)"""
        self._handle_exit_request()

class UnsavedChangesHandler:
    """Handles checking and saving unsaved changes in the code editor"""

    @staticmethod
    def check_and_handle_unsaved_changes(window_manager) -> bool:
        """
        Check for unsaved changes and handle them.

        Returns:
            bool: True if should proceed with closing, False if should cancel
        """
        try:
            current = window_manager.get_current_window()

            # Import here to avoid circular imports
            from src.app.presentation.views.code_editor.code_editor_window import (
                CodeEditorWindow,
            )

            if not (
                current
                and isinstance(current, CodeEditorWindow)
                and current.editor_display.has_editor
            ):
                return True

            modified_tabs = UnsavedChangesHandler._get_modified_tabs(
                current.editor_display.tab_widget
            )

            if not modified_tabs:
                return True

            return UnsavedChangesHandler._handle_save_dialog(
                modified_tabs, current.editor_display.tab_widget
            )

        except Exception as e:
            logger.error(f"Error checking unsaved changes: {e}", exc_info=True)
            return True

    @staticmethod
    def _get_modified_tabs(tab_widget) -> list:
        """Get list of modified tab indices"""
        return [
            i
            for i in range(tab_widget.count())
            if tab_widget.widget(i).editor.codeEditor.document().isModified()
        ]

    @staticmethod
    def _handle_save_dialog(modified_tabs: list, tab_widget) -> bool:
        """Handle the save dialog and saving process"""
        unsaved_count = len(modified_tabs)
        message = (
            f"You have {unsaved_count} unsaved files. Do you want to save them?"
            if unsaved_count > 1
            else "Do you want to save your changes?"
        )

        reply = QMessageBox.question(
            None,
            "Save Changes?",
            message,
            QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel,
        )

        if reply == QMessageBox.Cancel:
            return False
        if reply == QMessageBox.Save:
            return UnsavedChangesHandler._save_modified_files(modified_tabs, tab_widget)

        return True  # Discard changes

    @staticmethod
    def _save_modified_files(modified_tabs: list, tab_widget) -> bool:
        """Save all modified files"""
        for tab_index in modified_tabs:
            try:
                tab = tab_widget.widget(tab_index)
                if not tab.editor.saveFile():
                    return False
            except Exception as e:
                logger.error(f"Error saving file at tab {tab_index}: {e}", exc_info=True)
                return False
        return True

class MainWindow(QMainWindow):
    """Main application window with window management and cleanup handling"""

    def __init__(self):
        super().__init__()
        self._setup_window()
        self._setup_window_manager()

    def _setup_window(self) -> None:
        """Configure the main window properties"""
        self.setWindowTitle(MainWindowConfig.WINDOW_TITLE)
        self.setMinimumSize(MainWindowConfig.MIN_WIDTH, MainWindowConfig.MIN_HEIGHT)

    def _setup_window_manager(self) -> None:
        """Setup window manager and show main content"""
        from src.app.presentation.window_controller.window_management import (
            WindowManager,
        )
        from src.app.presentation.services.navigation_service import NavigationService

        self.window_manager = WindowManager(self)
        
        NavigationService.instance().set_window_manager(self.window_manager)
        
        self.setCentralWidget(self.window_manager)
        self.window_manager.show_window("main")

    def return_to_main(self) -> None:
        """Return to main window"""
        self.window_manager.show_window("main")

    def closeEvent(self, event) -> None:
        """Handle application close with unsaved changes check"""
        try:
            # Check for unsaved changes
            should_close = UnsavedChangesHandler.check_and_handle_unsaved_changes(
                self.window_manager
            )

            if not should_close:
                event.ignore()
                return

            # Accept the event and cleanup
            event.accept()
            self._perform_cleanup()

        except RuntimeError:
            # Handle Qt runtime errors during shutdown
            event.accept()

    def _perform_cleanup(self) -> None:
        """Perform application cleanup"""
        try:
            # Simple cleanup - just cleanup window manager
            QTimer.singleShot(0, self.window_manager.cleanup_all)

        except Exception as e:
            logger.error(f"Error during cleanup: {e}", exc_info=True)
