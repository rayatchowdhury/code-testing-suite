from PySide6.QtWidgets import QWidget, QVBoxLayout, QSplitter, QHBoxLayout, QPushButton
from PySide6.QtCore import Qt, Signal
from widgets.display_area_widgets.editor import EditorWidget
from widgets.display_area_widgets.console import ConsoleOutput
from tools.tle_compiler_runner import TLECompilerRunner
from styles.style import MATERIAL_COLORS
from styles.components.code_editor_display_area import SPLITTER_STYLE, OUTER_PANEL_STYLE  # Add this line
import os

class TLETesterDisplay(QWidget):
    filePathChanged = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.workspace_dir = os.path.join(os.path.expanduser('~'), '.code_testing_suite', 'workspace')
        os.makedirs(self.workspace_dir, exist_ok=True)
        self._setup_ui()
        self._connect_signals()
        # Open generator file by default
        self._handle_file_button('Generator')

        self.compiler_runner = TLECompilerRunner(self.console)

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
        button_panel.setStyleSheet(f"""
            QWidget {{
                background-color: {MATERIAL_COLORS['surface_dim']};
                border-bottom: 1px solid {MATERIAL_COLORS['outline']};
            }}
        """)
        button_layout = QHBoxLayout(button_panel)
        button_layout.setContentsMargins(8, 8, 8, 8)
        button_layout.setSpacing(8)

        # Create file buttons with improved styling
        self.file_buttons = {}
        self.current_button = None  # Track active button
        
        # Only Generator and Test Code buttons
        for name in ['Generator', 'Test Code']:
            btn = QPushButton(name)
            btn.setMinimumHeight(36)
            btn.setProperty("isActive", False)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {MATERIAL_COLORS['surface_variant']};
                    border: none;
                    border-radius: 6px;
                    color: {MATERIAL_COLORS['on_surface']};
                    padding: 8px 16px;
                    font-weight: 500;
                }}
                QPushButton:hover {{
                    background-color: {MATERIAL_COLORS['primary_container']};
                }}
                QPushButton[isActive="true"] {{
                    background-color: {MATERIAL_COLORS['primary']};
                    color: {MATERIAL_COLORS['on_primary']};
                }}
            """)
            self.file_buttons[name] = btn
            button_layout.addWidget(btn)

        # Create editor
        self.editor = EditorWidget()

        # Create inner panel for content
        content_panel = QWidget()
        content_panel.setStyleSheet(f"background-color: {MATERIAL_COLORS['surface']};")
        content_layout = QVBoxLayout(content_panel)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)
        content_layout.addWidget(button_panel)
        content_layout.addWidget(self.editor)

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
        self.splitter.setCollapsible(1, True)
        self.splitter.setSizes([600, 250])

        # Add splitter to main layout
        main_layout.addWidget(self.splitter)

    def _connect_signals(self):
        for name, btn in self.file_buttons.items():
            btn.clicked.connect(lambda checked, n=name: self._handle_file_button(n))
        self.console.compile_run_btn.clicked.connect(self.compile_and_run_code)

    def _handle_file_button(self, button_text):
        # Update active button state
        if self.current_button:
            self.current_button.setProperty("isActive", False)
            self.current_button.style().unpolish(self.current_button)
            self.current_button.style().polish(self.current_button)
        
        clicked_button = self.file_buttons[button_text]
        clicked_button.setProperty("isActive", True)
        clicked_button.style().unpolish(clicked_button)
        clicked_button.style().polish(clicked_button)
        self.current_button = clicked_button

        file_map = {
            'Generator': 'generator.cpp',
            'Test Code': 'test.cpp'
        }
        
        file_path = os.path.join(self.workspace_dir, file_map[button_text])
        
        # Create file if it doesn't exist
        if not os.path.exists(file_path):
            with open(file_path, 'w') as f:
                f.write('// Add your code here\n')
        
        # Load file content
        with open(file_path, 'r') as f:
            content = f.read()
            
        self.editor.currentFilePath = file_path
        self.editor.codeEditor.setPlainText(content)
        self.editor.codeEditor._setup_syntax_highlighting(file_path)

    def compile_and_run_code(self):
        if not self.editor.currentFilePath:
            return

        self.console.compile_run_btn.setEnabled(False)
        
        def on_complete():
            self.console.compile_run_btn.setEnabled(True)
            self.compiler_runner.finished.disconnect(on_complete)
        
        self.compiler_runner.finished.connect(on_complete)
        self.compiler_runner.compile_and_run_code(self.editor.currentFilePath)