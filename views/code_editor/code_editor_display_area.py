from PySide6.QtWidgets import (QWidget, QHBoxLayout, QVBoxLayout, 
                              QPushButton, QTabWidget)
from PySide6.QtCore import Signal
import subprocess
import os
from widgets.display_area_widgets.editor import EditorWidget
from widgets.display_area_widgets.console import ConsoleOutput
from styles.style import MATERIAL_COLORS
from views.code_editor.code_editor_compiler_runner import CompilerRunner

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
        
        # Main horizontal layout
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Left side layout with tabs and buttons
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(0)

        # Tab widget
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabsClosable(True)
        self.tab_widget.tabCloseRequested.connect(self.close_tab)
        self.tab_widget.setStyleSheet(f"""
            QTabWidget::pane {{
                border: none;
            }}
            QTabBar::tab {{
                background: {MATERIAL_COLORS['surface']};
                color: {MATERIAL_COLORS['text_primary']};
                padding: 8px 12px;
                border: none;
                border-right: 1px solid {MATERIAL_COLORS['outline']};
            }}
            QTabBar::tab:selected {{
                background: {MATERIAL_COLORS['surface_variant']};
            }}
        """)
        left_layout.addWidget(self.tab_widget)

        # Add initial editor tab
        self.add_new_tab()

        # Button layout
        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(10, 5, 10, 5)
        
        # Create buttons
        self.compile_btn = QPushButton("Compile")
        self.run_btn = QPushButton("Run")
        
        # Style buttons
        for btn in (self.compile_btn, self.run_btn):
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {MATERIAL_COLORS['primary_container']};
                    color: {MATERIAL_COLORS['on_primary_container']};
                    border: none;
                    border-radius: 4px;
                    padding: 6px 16px;
                }}
                QPushButton:hover {{
                    background-color: {MATERIAL_COLORS['primary']};
                    color: {MATERIAL_COLORS['on_primary']};
                }}
            """)

        # Add buttons to layout
        button_layout.addWidget(self.compile_btn)
        button_layout.addWidget(self.run_btn)
        button_layout.addStretch()
        
        left_layout.addLayout(button_layout)
        
        # Add left panel to main layout
        main_layout.addWidget(left_panel, stretch=2)

        # Add console to main layout
        self.console = ConsoleOutput()
        main_layout.addWidget(self.console, stretch=1)

        # Initialize compiler runner
        self.compiler_runner = CompilerRunner(self.console)
        
        # Connect button signals
        self.compile_btn.clicked.connect(self.compile_code)
        self.run_btn.clicked.connect(self.run_code)

    def add_new_tab(self, title="Untitled"):
        """Add a new editor tab"""
        new_tab = EditorTab()
        self.tab_widget.addTab(new_tab, title)
        self.tab_widget.setCurrentWidget(new_tab)
        return new_tab

    def close_tab(self, index):
        """Close the specified tab"""
        if self.tab_widget.count() > 1:  # Keep at least one tab open
            self.tab_widget.removeTab(index)
        
    @property
    def editor(self):
        """Get the current editor widget"""
        current_tab = self.tab_widget.currentWidget()
        return current_tab.editor if current_tab else None

    def compile_code(self):
        current_tab = self.tab_widget.currentWidget()
        if not current_tab or not current_tab.editor.currentFilePath:
            self.saveRequested.emit()
            return

        self.compiler_runner.compile_code(current_tab.editor.currentFilePath)

    def run_code(self):
        current_tab = self.tab_widget.currentWidget()
        if not current_tab or not current_tab.editor.currentFilePath:
            self.compile_code()
            return

        self.compiler_runner.run_code(current_tab.editor.currentFilePath)

    def getCurrentEditor(self):
        current_tab = self.tab_widget.currentWidget()
        return current_tab.editor if current_tab else None

    def isCurrentFileModified(self):
        editor = self.getCurrentEditor()
        return editor.codeEditor.document().isModified() if editor else False
