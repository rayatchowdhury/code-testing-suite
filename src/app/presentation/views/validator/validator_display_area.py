# -*- coding: utf-8 -*-
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QHBoxLayout,
    QMessageBox,
    QPushButton,
    QSplitter,
    QVBoxLayout,
    QWidget,
)

from src.app.core.tools.compiler_runner import CompilerRunner
from src.app.presentation.styles.components.code_editor_display_area import (
    OUTER_PANEL_STYLE,
    SPLITTER_STYLE,
)
from src.app.presentation.styles.style import MATERIAL_COLORS
from src.app.presentation.widgets.display_area_widgets.ai_panel import AIPanel
from src.app.presentation.widgets.display_area_widgets.console import ConsoleOutput
from src.app.presentation.widgets.display_area_widgets.editor import EditorWidget
from src.app.presentation.widgets.display_area_widgets.test_tab_widget import (
    TestTabWidget,
)
from src.app.shared.constants import WORKSPACE_DIR


class ValidatorDisplay(QWidget):
    filePathChanged = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        # Workspace structure is initialized at application startup
        self.workspace_dir = WORKSPACE_DIR

        self._setup_ui()
        self._connect_signals()

        # Initialize threaded compiler
        self.compiler_runner = CompilerRunner(self.console)

        # Activate default tab
        self.test_tabs.activate_default_tab()

        # Add backward compatibility property for window files
        self.file_buttons = self.test_tabs.file_buttons

    def _setup_ui(self):
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Create splitter
        self.splitter = QSplitter(Qt.Horizontal)
        self.splitter.setStyleSheet(SPLITTER_STYLE)
        self.splitter.setChildrenCollapsible(False)
        self.splitter.setHandleWidth(0)

        # Create outer panel
        outer_panel = QWidget()
        outer_panel.setMinimumWidth(400)
        outer_panel.setStyleSheet(OUTER_PANEL_STYLE)
        outer_layout = QVBoxLayout(outer_panel)
        outer_layout.setContentsMargins(3, 3, 3, 3)
        outer_layout.setSpacing(0)

        # Create editor
        self.editor = EditorWidget()

        # Create test tabs widget with validator configuration (multi-language)
        tab_config = {
            "Generator": {
                "cpp": "generator.cpp",
                "py": "generator.py",
                "java": "Generator.java",
            },
            "Test Code": {"cpp": "test.cpp", "py": "test.py", "java": "TestCode.java"},
            "Validator Code": {
                "cpp": "validator.cpp",
                "py": "validator.py",
                "java": "ValidatorCode.java",
            },
        }
        self.test_tabs = TestTabWidget(
            parent=self,
            tab_config=tab_config,
            default_tab="Generator",
            multi_language=True,
            default_language="cpp",
            test_type="validator",  # Use nested validator directory
        )

        # Set editor as the content widget for tabs
        self.test_tabs.set_content_widget(self.editor)

        # Initialize AI panel with validator type (lazy loading)
        self.ai_panel = self.editor.get_ai_panel()
        self.ai_panel.set_panel_type("validator")

        # Add test tabs to outer panel
        outer_layout.addWidget(self.test_tabs)

        # Setup console
        self.console = ConsoleOutput()
        self.console.setMinimumWidth(200)

        # Add panels to splitter
        self.splitter.addWidget(outer_panel)
        self.splitter.addWidget(self.console)

        # Configure splitter
        self.splitter.setCollapsible(0, False)
        self.splitter.setCollapsible(1, True)
        self.splitter.setSizes([700, 300])

        # Set splitter as main widget
        main_layout.addWidget(self.splitter)

    def _connect_signals(self):
        """Connect UI signals to their handlers."""
        # Connect test tabs signals
        self.test_tabs.fileChanged.connect(self._handle_file_changed)
        self.test_tabs.tabClicked.connect(self._handle_tab_clicked)
        self.test_tabs.languageChanged.connect(self._handle_language_changed)

        # Connect console compile & run button
        self.console.compile_run_btn.clicked.connect(self.compile_and_run_code)

        # Connect editor signals
        self.editor.fileSaved.connect(self.handle_file_saved)
        self.editor.textChanged.connect(self._handle_text_changed)

        # Connect AI panel refresh to editor file changes (if method exists)
        if hasattr(self.ai_panel, "refresh_context"):
            self.filePathChanged.connect(self.ai_panel.refresh_context)

    def _handle_file_changed(self, file_path):
        """Handle file change from test tabs."""
        # Load file in editor
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
        print(f"Validator: Switched {tab_name} to {language.upper()}")
        # Update AI panel context if needed
        if hasattr(self.ai_panel, "refresh_context"):
            self.ai_panel.refresh_context()

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
        # Check for unsaved changes before compiling
        if self.test_tabs.has_unsaved_changes():
            reply = QMessageBox.question(
                self,
                "Unsaved Changes",
                f"Do you want to save changes before compiling?",
                QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel,
            )

            if reply == QMessageBox.Save:
                if not self.editor.saveFile():
                    return
            elif reply == QMessageBox.Cancel:
                return

        current_file = self.editor.currentFilePath
        if not current_file:
            return

        self.console.compile_run_btn.setEnabled(False)

        def on_complete():
            self.console.compile_run_btn.setEnabled(True)
            self.compiler_runner.finished.disconnect(on_complete)

        self.compiler_runner.finished.connect(on_complete)
        self.compiler_runner.compile_and_run_code(current_file)

    def set_content(self, widget):
        """
        Replace display area content with the given widget.

        This method supports unified status view integration by allowing
        the display area to be dynamically replaced with a status view widget.

        Args:
            widget: QWidget to display
        """
        # Clear existing content
        layout = self.layout()
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().setParent(None)

        # Add new widget
        layout.addWidget(widget)
