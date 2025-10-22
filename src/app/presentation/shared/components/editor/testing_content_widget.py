# -*- coding: utf-8 -*-
"""
TestingContentWidget - Unified content widget for test windows.

This widget provides the shared editor + console + test tabs structure
used by Benchmarker, Validator, and Comparator windows. It encapsulates
the common functionality and reduces code duplication.
"""

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QHBoxLayout,
    QMessageBox,
    QSplitter,
    QVBoxLayout,
    QWidget,
)

from src.app.presentation.shared.design_system.styles.components.code_editor_display_area import (
    OUTER_PANEL_STYLE,
    SPLITTER_STYLE,
)
from src.app.presentation.shared.components.console import ConsoleWidget
from src.app.presentation.shared.components.editor.editor_widget import EditorWidget
from src.app.presentation.shared.components.editor.test_tab_widget import (
    TestTabWidget,
)
from src.app.shared.constants import WORKSPACE_DIR
from src.app.presentation.services import ErrorHandlerService

class TestingContentWidget(QWidget):
    """
    Unified content widget for test windows (Benchmarker, Validator, Comparator).
    
    Contains:
    - Editor widget with AI panel support
    - Console output
    - Test tabs for file switching
    - Horizontal splitter layout
    
    Signals:
    - filePathChanged: Emitted when the current file changes
    """

    filePathChanged = Signal()

    def __init__(
        self,
        parent=None,
        tab_config=None,
        default_tab=None,
        test_type="comparator",
        compiler_runner_class=None,
        ai_panel_type="comparison",
    ):
        """
        Initialize TestingContentWidget.

        Args:
            parent: Parent widget
            tab_config: Dict mapping tab names to file configs
            default_tab: Name of the tab to activate by default
            test_type: Type of test (comparator/validator/benchmarker)
            compiler_runner_class: Class to use for compilation (optional)
            ai_panel_type: Type of AI panel (comparison/validator/benchmark)
        """
        super().__init__(parent)
        
        # Configuration
        self.workspace_dir = WORKSPACE_DIR
        self.test_type = test_type
        self.ai_panel_type = ai_panel_type
        self.tab_config = tab_config or {}
        self.default_tab = default_tab
        self.compiler_runner_class = compiler_runner_class

        self._setup_ui()
        self._connect_signals()

        if compiler_runner_class:
            self.compiler_runner = compiler_runner_class(self.console)

        # Activate default tab
        self.test_tabs.activate_default_tab()

        # Backward compatibility property for window files
        self.file_buttons = self.test_tabs.file_buttons

    def _setup_ui(self):
        """Setup the main UI layout."""
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        self.splitter = QSplitter(Qt.Horizontal)
        self.splitter.setStyleSheet(SPLITTER_STYLE)
        self.splitter.setChildrenCollapsible(False)
        self.splitter.setHandleWidth(0)

        outer_panel = QWidget()
        outer_panel.setMinimumWidth(400)
        outer_panel.setStyleSheet(OUTER_PANEL_STYLE)
        outer_layout = QVBoxLayout(outer_panel)
        outer_layout.setContentsMargins(3, 3, 3, 3)
        outer_layout.setSpacing(0)

        self.editor = EditorWidget()

        self.test_tabs = TestTabWidget(
            parent=self,
            tab_config=self.tab_config,
            default_tab=self.default_tab,
            multi_language=True,
            default_language="cpp",
            test_type=self.test_type,
        )

        self.test_tabs.set_content_widget(self.editor)

        self.ai_panel = self.editor.get_ai_panel()
        self.ai_panel.set_panel_type(self.ai_panel_type)

        outer_layout.addWidget(self.test_tabs)

        self.console = ConsoleWidget()
        self.console.setMinimumWidth(200)

        self.splitter.addWidget(outer_panel)
        self.splitter.addWidget(self.console)

        self.splitter.setCollapsible(0, False)
        self.splitter.setCollapsible(1, True)
        self.splitter.setSizes([700, 300])

        main_layout.addWidget(self.splitter)

    def _connect_signals(self):
        """Connect UI signals to their handlers."""
        self.test_tabs.fileChanged.connect(self._handle_file_changed)
        self.test_tabs.tabClicked.connect(self._handle_tab_clicked)
        self.test_tabs.languageChanged.connect(self._handle_language_changed)

        self.console.compile_run_btn.clicked.connect(self.compile_and_run_code)

        self.editor.fileSaved.connect(self.handle_file_saved)
        self.editor.textChanged.connect(self._handle_text_changed)

        # Connect AI panel refresh if the method exists
        try:
            self.filePathChanged.connect(self.ai_panel.refresh_context)
        except AttributeError:
            pass  # ai_panel doesn't have refresh_context method

    def _handle_file_changed(self, file_path):
        """Handle file change from test tabs."""
        self.editor.openFile(file_path)
        # Mark tab as saved since we just loaded an existing file
        self.test_tabs.mark_current_tab_saved()
        self.filePathChanged.emit()

    def _handle_tab_clicked(self, action_or_tab_name):
        """Handle tab clicks and special actions."""
        if action_or_tab_name == "save_current":
            # Save current file and continue with tab switch
            if self.editor.saveFile():
                # Mark as saved
                self.test_tabs.mark_current_tab_saved()
        else:
            # Regular tab click - no additional action needed
            pass

    def _handle_language_changed(self, tab_name, language):
        """Handle language switching in tabs."""
        try:
            self.ai_panel.refresh_context()
        except AttributeError:
            pass  # ai_panel doesn't have refresh_context method

    def _handle_text_changed(self):
        """Handle text changes in editor."""
        self.test_tabs.mark_current_tab_unsaved()

    def handle_file_saved(self):
        """Handle file saved event."""
        self.test_tabs.mark_current_tab_saved()

    def _handle_file_button(self, button_name, skip_save_prompt=False):
        """Backward compatibility method for window files."""
        self.test_tabs.activate_tab(button_name, skip_save_prompt)

    def compile_and_run_code(self):
        """Compile and run the current code."""
        error_service = ErrorHandlerService.instance()
        # Check for unsaved changes before compiling
        if self.test_tabs.has_unsaved_changes():
            reply = error_service.ask_save_discard_cancel(
                "Unsaved Changes",
                "Do you want to save changes before compiling?",
                self
            )

            if reply == QMessageBox.Save:
                if not self.editor.saveFile():
                    return
            elif reply == QMessageBox.Cancel:
                return

        current_file = self.editor.currentFilePath
        if not current_file:
            return

        # Only compile if we have a compiler runner (conditionally created in __init__)
        if hasattr(self, "compiler_runner"):
            self.console.compile_run_btn.setEnabled(False)

            def on_complete():
                self.console.compile_run_btn.setEnabled(True)
                self.compiler_runner.finished.disconnect(on_complete)

            self.compiler_runner.finished.connect(on_complete)
            self.compiler_runner.compile_and_run_code(current_file)

    def refresh_ai_panel(self):
        """Refresh AI panel visibility based on current configuration."""
        try:
            self.ai_panel.refresh_visibility()
        except AttributeError:
            pass  # ai_panel doesn't have refresh_visibility method
            self.ai_panel.refresh_visibility()
