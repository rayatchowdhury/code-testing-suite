# -*- coding: utf-8 -*-
from PySide6.QtWidgets import QWidget, QVBoxLayout, QSplitter, QHBoxLayout, QPushButton, QMessageBox
from PySide6.QtCore import Qt, Signal
import os

from src.app.presentation.widgets.display_area_widgets.editor import EditorWidget
from src.app.presentation.widgets.display_area_widgets.console import ConsoleOutput
from src.app.presentation.widgets.display_area_widgets.ai_panel import AIPanel
from src.app.core.tools.validation_compiler_runner import ValidationCompilerRunner
from src.app.presentation.styles.style import MATERIAL_COLORS
from src.app.presentation.styles.components.code_editor_display_area import SPLITTER_STYLE, OUTER_PANEL_STYLE
from src.app.presentation.styles.components.test_view_styles import (
    TEST_VIEW_BUTTON_PANEL_STYLE,
    TEST_VIEW_FILE_BUTTON_STYLE,
    TEST_VIEW_CONTENT_PANEL_STYLE
)
from src.app.shared.constants import WORKSPACE_DIR

class ValidatorDisplay(QWidget):
    filePathChanged = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.workspace_dir = WORKSPACE_DIR
        os.makedirs(self.workspace_dir, exist_ok=True)
        self._setup_ui()
        self._connect_signals()
        # Open generator file by default
        self._handle_file_button('Generator')

        # Initialize threaded compiler instead of regular compiler
        self.compiler_runner = ValidationCompilerRunner(self.console)

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

        # Create button panel with background
        button_panel = QWidget()
        button_panel.setStyleSheet(TEST_VIEW_BUTTON_PANEL_STYLE)
        button_layout = QHBoxLayout(button_panel)
        button_layout.setContentsMargins(8, 8, 8, 8)
        button_layout.setSpacing(8)

        # Create file buttons with improved styling
        self.file_buttons = {}
        self.current_button = None  # Track active button
        
        for name in ['Generator', 'Validator', 'Test Code']:
            btn = QPushButton(name)
            btn.setMinimumHeight(36)
            btn.setProperty("isActive", False)
            btn.setStyleSheet(TEST_VIEW_FILE_BUTTON_STYLE)
            self.file_buttons[name] = btn
            button_layout.addWidget(btn)

        # Create editor and AI panel in correct order
        self.editor = EditorWidget()
        
        # Create inner panel for content
        content_panel = QWidget()
        content_panel.setStyleSheet(TEST_VIEW_CONTENT_PANEL_STYLE)
        content_layout = QVBoxLayout(content_panel)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)
        content_layout.addWidget(button_panel)
        content_layout.addWidget(self.editor)

        # Initialize AI panel with validator type (lazy loading)
        self.ai_panel = self.editor.get_ai_panel()
        self.ai_panel.set_panel_type("validator")

        # Add inner panel to outer panel
        outer_layout.addWidget(content_panel)

        # Setup console
        self.console = ConsoleOutput()
        self.console.setMinimumWidth(200)

        # Add panels to splitter
        self.splitter.addWidget(outer_panel)
        self.splitter.addWidget(self.console)

        # Configure splitter
        self.splitter.setCollapsible(0, False)
        self.splitter.setCollapsible(1, False)
        self.splitter.setSizes([800, 200])

        # Set splitter as main widget
        main_layout.addWidget(self.splitter)

    def _connect_signals(self):
        # Connect file button clicks
        for btn_name, btn in self.file_buttons.items():
            btn.clicked.connect(lambda checked, name=btn_name: self._handle_file_button(name))
        
        # Connect editor signals
        self.editor.fileSaved.connect(self.handle_file_saved)
        self.editor.textChanged.connect(self._handle_text_changed)
        
        # Connect AI panel refresh to editor file changes (if method exists)
        if hasattr(self.ai_panel, 'refresh_context'):
            self.filePathChanged.connect(self.ai_panel.refresh_context)

    def _handle_file_button(self, button_name):
        # Update button states
        if self.current_button:
            self.current_button.setProperty("isActive", False)
            self.current_button.style().polish(self.current_button)
        
        # Set new active button
        new_button = self.file_buttons[button_name]
        new_button.setProperty("isActive", True)
        new_button.style().polish(new_button)
        self.current_button = new_button
        
        # Map button names to file paths
        file_mapping = {
            'Generator': os.path.join(self.workspace_dir, 'generator.cpp'),
            'Validator': os.path.join(self.workspace_dir, 'validator.cpp'),
            'Test Code': os.path.join(self.workspace_dir, 'test.cpp')
        }
        
        file_path = file_mapping[button_name]
        
        # Create file if it doesn't exist with appropriate content
        if not os.path.exists(file_path):
            default_content = self._get_default_content(button_name)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(default_content)
        
        # Load file in editor
        self.editor.openFile(file_path)
        self.filePathChanged.emit()

    def _get_default_content(self, button_name):
        if button_name == 'Generator':
            return '''#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;

int main() {
    // Your main code here
    
    return 0;
}'''
        elif button_name == 'Validator':
            return '''#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;

int main() {
    // Your validation code here
    // This should check if the output is correct
    
    return 0;
}'''
        elif button_name == 'Test Code':
            return '''#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;

int main() {
    // Your test code here
    
    return 0;
}'''
        return ""

    def _handle_text_changed(self, modified):
        """Handle text changes in the editor"""
        if self.current_button:
            self.current_button.setProperty("hasUnsavedChanges", modified)
            self.current_button.style().polish(self.current_button)

    def handle_file_saved(self):
        """Handle file saved event"""
        if self.current_button:
            self.current_button.setProperty("hasUnsavedChanges", False)
            self.current_button.style().polish(self.current_button)
            
        # Emit signal that file content has changed
        self.filePathChanged.emit()

    def compile_and_run_code(self):
        """Compile and run the current code"""
        current_file = self.editor.currentFilePath
        if current_file and current_file.endswith('.cpp'):
            self.compiler_runner.compile_and_run(current_file)
