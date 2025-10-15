import os

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QHBoxLayout,
    QMessageBox,
    QPushButton,
    QSplitter,
    QTabWidget,
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
from src.app.presentation.widgets.display_area_widgets.editor_tab_widget import (
    EditorTabWidget,
)


class CodeEditorDisplay(QWidget):
    filePathChanged = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
        self._connect_signals()

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

        # Create inner panel for content
        left_panel = QWidget()
        left_panel.setStyleSheet(
            f"""
          background-color: {MATERIAL_COLORS['surface']};
        """
        )

        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(0)

        # Create editor tab widget
        self.editor_tabs = EditorTabWidget()
        left_layout.addWidget(self.editor_tabs)

        # Add inner panel to outer panel
        outer_layout.addWidget(left_panel)

        # Setup console
        self.console = ConsoleOutput()
        self.console.setMinimumWidth(200)

        # Add panels to splitter
        self.splitter.addWidget(outer_panel)
        self.splitter.addWidget(self.console)

        # Configure splitter
        self.splitter.setCollapsible(0, False)  # Left panel (editor) not collapsible
        self.splitter.setCollapsible(1, True)  # Right panel (console) collapsible

        # Set initial sizes (editor: 70%, console: 30%)
        self.splitter.setSizes([700, 300])

        # Add splitter to main layout
        main_layout.addWidget(self.splitter)

        # Initialize compiler
        self.compiler_runner = CompilerRunner(self.console)

    def _connect_signals(self):
        # Connect editor tab widget signals
        self.editor_tabs.filePathChanged.connect(self.filePathChanged.emit)
        self.editor_tabs.currentTabChanged.connect(self._on_current_tab_changed)

        # Connect console compile & run button
        self.console.compile_run_btn.clicked.connect(self.compile_and_run_code)

    def _on_current_tab_changed(self, index):
        """Handle current tab change to update signals."""
        # Emit file path changed for external listeners
        self.filePathChanged.emit()

    @property
    def editor(self):
        """Get the current editor widget for backward compatibility."""
        return self.editor_tabs.current_editor

    @property
    def has_editor(self):
        """Check if there's an active editor (always True for editor tabs)."""
        return self.editor_tabs.current_editor is not None

    @property
    def tab_widget(self):
        """Get the tab widget for backward compatibility."""
        return self.editor_tabs.tab_widget

    def add_new_tab(self, title="Untitled"):
        """Add a new editor tab."""
        return self.editor_tabs.add_new_tab(title)

    def close_tab(self, index):
        """Close tab at specified index."""
        self.editor_tabs.close_tab(index)

    def open_file_in_new_tab(self, file_path):
        """Open a file in a new tab."""
        return self.editor_tabs.open_file_in_new_tab(file_path)

    def compile_and_run_code(self):
        """Compile and run the current code."""
        current_editor = self.editor_tabs.current_editor
        if not current_editor or not current_editor.currentFilePath:
            return

        # Check for unsaved changes before compiling
        if current_editor.codeEditor.document().isModified():
            reply = QMessageBox.question(
                self,
                "Unsaved Changes",
                "Do you want to save changes before compiling?",
                QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel,
            )

            if reply == QMessageBox.Save:
                if not current_editor.saveFile():
                    return
            elif reply == QMessageBox.Cancel:
                return

        self.console.compile_run_btn.setEnabled(False)

        def on_complete():
            self.console.compile_run_btn.setEnabled(True)
            self.compiler_runner.finished.disconnect(on_complete)

        self.compiler_runner.finished.connect(on_complete)
        self.compiler_runner.compile_and_run_code(current_editor.currentFilePath)

    def save_editor_state(self):
        """Save the state of opened files"""
        # Save state implementation can be added here if needed

    def getCurrentEditor(self):
        """Get the current editor widget with safety checks"""
        return self.editor_tabs.current_editor

    def isCurrentFileModified(self):
        """Check if current file has unsaved changes"""
        return self.editor_tabs.has_unsaved_changes()
