from PySide6.QtWidgets import (QWidget, QVBoxLayout, QSplitter, QHBoxLayout, 
                              QTabWidget, QPushButton, QMessageBox)
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtCore import Qt, Signal, QUrl
import os

from widgets.display_area_widgets.editor import EditorWidget
from widgets.display_area_widgets.console import ConsoleOutput 
from widgets.display_area_widgets.ai_panel import AIPanel
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
    filePathChanged = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.has_editor = False
        self._setup_ui()
        self._connect_signals()
        self.show_welcome_screen()

    def _setup_ui(self):
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Create splitter
        self.splitter = QSplitter(Qt.Horizontal)
        self.splitter.setStyleSheet(SPLITTER_STYLE)
        self.splitter.setChildrenCollapsible(False)  # Prevent panels from collapsing
        self.splitter.setHandleWidth(0)  # Add this line to hide the splitter handle

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

        # Create welcome screen web view
        self.welcome_view = QWebEngineView()
        self.welcome_view.setStyleSheet("background: transparent;")
        
        # Initialize but don't show tab widget yet
        self.tab_widget = self._create_tab_widget()
        self.tab_widget.hide()

        # Modify left panel to stack welcome view and tab widget
        left_layout.addWidget(self.welcome_view)
        left_layout.addWidget(self.tab_widget)

        # Add inner panel to outer panel
        outer_layout.addWidget(left_panel)

        # Simplified console setup - no more container wrapper needed
        self.console = ConsoleOutput()
        self.console.setMinimumWidth(200)
        
        # Add panels to splitter (back to 2-panel layout)
        self.splitter.addWidget(outer_panel)
        self.splitter.addWidget(self.console)

        # Configure splitter
        self.splitter.setCollapsible(0, False)  # Left panel (editor) not collapsible
        self.splitter.setCollapsible(1, True)   # Right panel (console) collapsible
        
        # Set initial sizes (editor: 70%, console: 30%)
        self.splitter.setSizes([700, 300])

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
        """Add a new editor tab and show editor"""
        if not self.has_editor:
            self.show_editor()
            
        new_tab = EditorTab()
        index = self.tab_widget.addTab(new_tab, title)
        self.tab_widget.setCurrentWidget(new_tab)
        
        # Initialize AI panel if enabled
        ai_panel = new_tab.editor.get_ai_panel()
        
        # Combine signal connections
        editor = new_tab.editor
        doc = editor.codeEditor.document()
        
        def update_title():
            self.updateTabTitle(index)
            self.filePathChanged.emit()
        
        doc.modificationChanged.connect(lambda _: update_title())
        editor.filePathChanged.connect(update_title)
        
        self.updateTabTitle(index)
        return new_tab

    def updateTabTitle(self, index, deleted=False):
        """Update tab title and tooltip based on file state"""
        tab = self.tab_widget.widget(index)
        if not tab:
            return
            
        editor = tab.editor
        if not editor:
            return

        # Set tooltip to show full path
        tooltip = editor.currentFilePath or "Untitled"
        self.tab_widget.setTabToolTip(index, tooltip)

        if deleted:
            title = f"[Deleted] {os.path.basename(editor.currentFilePath)}"
        else:
            # Get base title
            if editor.currentFilePath:
                if not os.path.exists(editor.currentFilePath):
                    title = f"[Deleted] {os.path.basename(editor.currentFilePath)}"
                else:
                    title = os.path.basename(editor.currentFilePath)
            else:
                title = "Untitled"

            # Add modification indicator
            if editor.codeEditor.document().isModified():
                title += " *"

        self.tab_widget.setTabText(index, title)

    def close_tab(self, index):
        """Close tab with save check"""
        tab = self.tab_widget.widget(index)
        if not tab or not tab.editor.codeEditor.document().isModified():
            self._remove_tab(index)
            return
            
        reply = QMessageBox.question(
            self, 'Save Changes?',
            f'Save changes to {self.tab_widget.tabText(index)}?',
            QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel
        )
        
        if reply == QMessageBox.Save and tab.editor.saveFile():
            self._remove_tab(index)
        elif reply == QMessageBox.Discard:
            self._remove_tab(index)

    def _remove_tab(self, index):
        """Handle tab removal and UI updates"""
        self.tab_widget.removeTab(index)
        if self.tab_widget.count() == 0:
            self.show_welcome_screen()
        self.filePathChanged.emit()
        
    @property
    def editor(self):
        """Get the current editor widget"""
        current_tab = self.tab_widget.currentWidget()
        return current_tab.editor if current_tab else None

    def compile_and_run_code(self):
        current_tab = self.tab_widget.currentWidget()
        if not current_tab or not current_tab.editor.currentFilePath:
            if current_tab:
                current_tab.editor.saveFile()
            return

        self.console.compile_run_btn.setEnabled(False)
        
        def on_complete():
            self.console.compile_run_btn.setEnabled(True)
            self.compiler_runner.finished.disconnect(on_complete)
        
        self.compiler_runner.finished.connect(on_complete)
        self.compiler_runner.compile_and_run_code(current_tab.editor.currentFilePath)

    def save_editor_state(self):
        """Save the state of opened files"""
        if not self.has_editor:
            return  # Don't save state if welcome screen is showing
            
        # Rest of save_editor_state implementation should be restored here
        # ...existing save_editor_state code...

    def getCurrentEditor(self):
        """Get the current editor widget with safety checks"""
        if not self.has_editor:
            return None
            
        current_tab = self.tab_widget.currentWidget()
        if not current_tab or not hasattr(current_tab, 'editor'):
            return None
            
        return current_tab.editor

    def isCurrentFileModified(self):
        """Check if current file has unsaved changes"""
        if not self.has_editor:
            return False
            
        editor = self.getCurrentEditor()
        if not editor:
            return False
            
        # Consider both document modifications and new unsaved files
        return (editor.codeEditor.document().isModified() or 
                (not editor.currentFilePath and editor.codeEditor.toPlainText().strip()))

    def show_welcome_screen(self):
        """Show the welcome screen and hide editor"""
        self.has_editor = False
        current_dir = os.path.dirname(os.path.abspath(__file__))
        welcome_path = os.path.join(current_dir, 'editor_welcome.html')
        self.welcome_view.setUrl(QUrl.fromLocalFile(welcome_path))
        self.welcome_view.show()
        self.tab_widget.hide()
        self.console.compile_run_btn.setEnabled(False)
        self.new_tab_button.hide()

    def show_editor(self):
        """Show the editor and hide welcome screen"""
        self.has_editor = True
        self.welcome_view.hide()
        self.tab_widget.show()
        self.console.compile_run_btn.setEnabled(True)
        self.new_tab_button.show()
