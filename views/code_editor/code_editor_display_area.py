from PySide6.QtWidgets import QWidget, QVBoxLayout, QSplitter, QHBoxLayout, QTabWidget, QPushButton
import os
from PySide6.QtCore import Qt, Signal
from widgets.display_area_widgets.editor import EditorWidget
from widgets.display_area_widgets.console import ConsoleOutput
from tools.compiler_runner import CompilerRunner
from styles.style import MATERIAL_COLORS
from styles.components.code_editor_display_area import SPLITTER_STYLE, OUTER_PANEL_STYLE
from styles.components.editor import get_tab_style

class EditorTab(QWidget):
    def __init__(self):
        super().__init__()
        self.editor = EditorWidget()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.editor)

class CodeEditorDisplay(QWidget):
    saveRequested = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
        self._connect_signals()
        self.add_new_tab()

        # Update compiler runner instantiation if it exists
        if hasattr(self, 'compiler_runner'):
            self.compiler_runner = CompilerRunner(self.console)

    def _setup_ui(self):
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Create splitter
        self.splitter = QSplitter(Qt.Horizontal)
        self.splitter.setStyleSheet(SPLITTER_STYLE)
        self.splitter.setChildrenCollapsible(False)  # Prevent panels from collapsing
        self.splitter.setHandleWidth(2)  # Set a small handle width

        # Create outer panel with ultra-dim gradient
        outer_panel = QWidget()
        outer_panel.setMinimumWidth(400)  # Set minimum width for editor panel
        outer_panel.setStyleSheet(OUTER_PANEL_STYLE)
        outer_layout = QVBoxLayout(outer_panel)
        outer_layout.setContentsMargins(3, 3, 3, 3)  # Increased margins slightly
        outer_layout.setSpacing(0)

        # Create inner panel for content
        left_panel = QWidget()
        left_panel.setStyleSheet(f"""
          background-color: {MATERIAL_COLORS['surface']};
        """)
        
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(0)

        # Add tab widget to inner panel
        self.tab_widget = self._create_tab_widget()
        left_layout.addWidget(self.tab_widget)

        # Add inner panel to outer panel
        outer_layout.addWidget(left_panel)

        # Simplified console setup - no more container wrapper needed
        self.console = ConsoleOutput()
        self.console.setMinimumWidth(200)
        
        # Add panels to splitter
        self.splitter.addWidget(outer_panel)
        self.splitter.addWidget(self.console)  # Add console directly

        # Configure splitter
        self.splitter.setCollapsible(0, False)  # Left panel (editor) not collapsible
        self.splitter.setCollapsible(1, True)   # Right panel (console) collapsible
        
        # Set initial sizes using ratio (approximately 73% to 27%)
        total_width = self.width() or 1100  # fallback width if widget not sized yet
        self.splitter.setSizes([600, 250])

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

    def _connect_signals(self):
        self.new_tab_button.clicked.connect(lambda: self.add_new_tab())
        self.console.compile_run_btn.clicked.connect(self.compile_and_run_code)

    def _get_tab_style(self):
        return get_tab_style()

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

        self.console.compile_run_btn.setEnabled(False)
        
        def on_complete():
            self.console.compile_run_btn.setEnabled(True)
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
