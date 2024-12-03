from PySide6.QtWidgets import (QWidget, QHBoxLayout, QVBoxLayout, 
                              QPushButton, QTabWidget, QSplitter, QLabel)
from PySide6.QtCore import Signal, Qt
import os
from widgets.display_area_widgets.editor import EditorWidget
from widgets.display_area_widgets.console import ConsoleOutput
from styles.style import MATERIAL_COLORS
from views.code_editor.code_editor_compiler_runner import CompilerRunner

SPLITTER_STYLE = """
QSplitter::handle {
    background-color: #CCCCCC;
}
"""

class EditorTab(QWidget):
    def __init__(self):
        super().__init__()
        self.editor = EditorWidget()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.editor)

class CodeEditorDisplay(QWidget):
    saveRequested = Signal()
    
    def __init__(self):
        super().__init__()
        self._setup_ui()
        self._connect_signals()
        self.add_new_tab()

    def _setup_ui(self):
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Create splitter
        self.splitter = QSplitter(Qt.Horizontal)
        self.splitter.setStyleSheet(SPLITTER_STYLE)

        # Left panel setup
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(0)

        # Tab widget setup
        self.tab_widget = self._create_tab_widget()
        left_layout.addWidget(self.tab_widget)

        # Right panel setup with title
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(0)

        # Add console title
        console_title = QLabel("Console")
        console_title.setFixedHeight(36)  # Match tab height
        console_title.setAlignment(Qt.AlignCenter)  # Center align the text
        console_title.setStyleSheet(f"""
            QLabel {{
                background: {MATERIAL_COLORS['surface_variant']};
                color: {MATERIAL_COLORS['text_primary']};
                font-weight: bold;
                font-family: 'Segoe UI';
                font-size: 13px;
                border-bottom: 1px solid {MATERIAL_COLORS['outline_variant']};
            }}
        """)
        right_layout.addWidget(console_title)

        # Console setup
        self.console = ConsoleOutput()
        right_layout.addWidget(self.console)

        # Button layout setup - Create a container for single button
        button_container = QWidget()
        button_container.setFixedHeight(40)
        button_container.setStyleSheet(f"""
            QWidget {{
                background: {MATERIAL_COLORS['surface_variant']};
                border-top: 1px solid {MATERIAL_COLORS['outline_variant']};
            }}
        """)
        button_layout = QHBoxLayout(button_container)
        button_layout.setContentsMargins(0, 0, 0, 0)

        # Create single compile & run button
        self.compile_run_btn = QPushButton("Compile && Run")  # Note: && for proper & display
        self.compile_run_btn.setFlat(True)
        self.compile_run_btn.setFixedHeight(40)
        self.compile_run_btn.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                color: {MATERIAL_COLORS['text_primary']};
                border: none;
                font-weight: bold;
                font-family: 'Segoe UI';
            }}
            QPushButton:hover {{
                background: rgba(255, 255, 255, 0.1);
            }}
            QPushButton:pressed {{
                background: rgba(255, 255, 255, 0.15);
            }}
            QPushButton:disabled {{
                color: {MATERIAL_COLORS['text_disabled']};
            }}
        """)
        button_layout.addWidget(self.compile_run_btn)
        right_layout.addWidget(button_container)

        # Add panels to splitter
        self.splitter.addWidget(left_panel)
        self.splitter.addWidget(right_panel)
        
        # Set initial sizes (3:1 ratio)
        self.splitter.setSizes([8, 3])
        self.splitter.setStyleSheet(MATERIAL_COLORS['splitter_style'])

        # Add splitter to main layout
        main_layout.addWidget(self.splitter)

        # Initialize compiler
        self.compiler_runner = CompilerRunner(self.console)

    def _create_tab_widget(self):
        tab_widget = QTabWidget()
        tab_widget.setTabsClosable(True)
        tab_widget.tabCloseRequested.connect(self.close_tab)
        
        # Add new tab button
        self.new_tab_button = QPushButton("+")
        self.new_tab_button.setObjectName("new_tab_button")
        tab_widget.setCornerWidget(self.new_tab_button, Qt.TopLeftCorner)
        
        tab_widget.setStyleSheet(self._get_tab_style())
        return tab_widget

    def _create_button_layout(self):
        layout = QHBoxLayout()
        layout.setContentsMargins(6, 4, 6, 6)  # Reduced vertical padding
        layout.setSpacing(6)  # Slightly reduced spacing
        
        self.compile_btn = QPushButton("Compile")
        self.run_btn = QPushButton("Run")
        
        button_style = f"""
            QPushButton {{
                background-color: {MATERIAL_COLORS['primary_container']};
                color: {MATERIAL_COLORS['on_primary_container']};
                border: none;
                border-radius: 4px;
                padding: 4px 16px;  # Reduced vertical padding
                font-weight: bold;
                font-family: 'Segoe UI';
                min-width: 80px;
                min-height: 24px;  # Reduced height
            }}
            QPushButton:hover {{
                background-color: {MATERIAL_COLORS['primary']};
                color: {MATERIAL_COLORS['on_primary']};
            }}
            QPushButton:pressed {{
                background-color: {MATERIAL_COLORS['primary_dark']};
                padding: 7px 19px 5px 21px;
            }}
            QPushButton:disabled {{
                background-color: {MATERIAL_COLORS['surface_variant']};
                color: {MATERIAL_COLORS['text_secondary']};
            }}
        """
        
        for btn in (self.compile_btn, self.run_btn):
            btn.setStyleSheet(button_style)
            layout.addWidget(btn)
        
        layout.addStretch()
        return layout

    def _connect_signals(self):
        self.new_tab_button.clicked.connect(lambda: self.add_new_tab())
        self.compile_run_btn.clicked.connect(self.compile_and_run_code)

    def _get_tab_style(self):
        return f"""
            QTabWidget::pane {{
                border: none;
                background: {MATERIAL_COLORS['surface']};
            }}
            QTabBar {{
                background: {MATERIAL_COLORS['surface_variant']};
            }}
            QTabBar::tab {{
                background: {MATERIAL_COLORS['surface']};
                color: {MATERIAL_COLORS['text_secondary']};
                padding: 8px 16px;
                border: none;
                border-right: 1px solid {MATERIAL_COLORS['outline_variant']};
                min-width: 100px;
                max-width: 200px;
                font-family: 'Segoe UI';
                font-size: 12px;
            }}
            QTabBar::tab:selected {{
                background: {MATERIAL_COLORS['surface_variant']};
                color: {MATERIAL_COLORS['text_primary']};
                border-bottom: 2px solid {MATERIAL_COLORS['primary']};
            }}
            QTabBar::tab:hover {{
                background: {MATERIAL_COLORS['surface_bright']};
                color: {MATERIAL_COLORS['text_primary']};
            }}
            QTabBar::close-button {{
                image: url(resources/icons/close.png);
                subcontrol-position: right;
            }}
            QTabBar::close-button:hover {{
                background: {MATERIAL_COLORS['error_container']};
                border-radius: 2px;
            }}
            QPushButton#new_tab_button {{
                background: {MATERIAL_COLORS['primary_container']};
                color: {MATERIAL_COLORS['on_primary_container']};
                border: none;
                padding: 8px;
                font-size: 20px;
                font-weight: bold;
                min-width: 36px;
                max-width: 36px;
            }}
            QPushButton#new_tab_button:hover {{
                background: {MATERIAL_COLORS['primary']};
                color: {MATERIAL_COLORS['on_primary']};
            }}
            QPushButton#new_tab_button:pressed {{
                background: {MATERIAL_COLORS['primary_dark']};
                color: {MATERIAL_COLORS['on_primary']};
            }}
        """

    def add_new_tab(self, title="Untitled"):
        """Add a new editor tab"""
        new_tab = EditorTab()
        index = self.tab_widget.addTab(new_tab, title)
        self.tab_widget.setCurrentWidget(new_tab)
        
        # Connect signals for file state changes
        new_tab.editor.codeEditor.document().modificationChanged.connect(
            lambda modified: self.updateTabTitle(index)
        )
        new_tab.editor.codeEditor.textChanged.connect(
            lambda: self.updateTabTitle(index)
        )
        
        # Update title immediately
        self.updateTabTitle(index)
        return new_tab

    def updateTabTitle(self, index):
        """Update tab title based on file state"""
        tab = self.tab_widget.widget(index)
        if not tab:
            return
            
        editor = tab.editor
        if not editor:
            return

        # Get base title
        if editor.currentFilePath:
            title = os.path.basename(editor.currentFilePath)
        else:
            title = "Untitled"

        # Add modification indicator
        if editor.codeEditor.document().isModified():
            title += " *"

        self.tab_widget.setTabText(index, title)

    def close_tab(self, index):
        """Close the specified tab"""
        if self.tab_widget.count() > 1:  # Keep at least one tab open
            self.tab_widget.removeTab(index)
        
    @property
    def editor(self):
        """Get the current editor widget"""
        current_tab = self.tab_widget.currentWidget()
        return current_tab.editor if current_tab else None

    def compile_and_run_code(self):
        current_tab = self.tab_widget.currentWidget()
        if not current_tab or not current_tab.editor.currentFilePath:
            self.saveRequested.emit()
            return

        self.compile_run_btn.setEnabled(False)
        
        def on_complete():
            self.compile_run_btn.setEnabled(True)
            self.compiler_runner.finished.disconnect(on_complete)
        
        self.compiler_runner.finished.connect(on_complete)
        self.compiler_runner.compile_and_run_code(current_tab.editor.currentFilePath)

    def getCurrentEditor(self):
        """Get the current editor widget"""
        current_tab = self.tab_widget.currentWidget()
        return current_tab.editor if current_tab else None

    def isCurrentFileModified(self):
        editor = self.getCurrentEditor()
        return editor.codeEditor.document().isModified() if editor else False
