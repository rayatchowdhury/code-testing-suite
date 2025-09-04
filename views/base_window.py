from PySide6.QtWidgets import QWidget, QHBoxLayout, QSplitter, QPushButton
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from config import ConfigView
from widgets.sidebar import Sidebar  # Add this import
from widgets.display_area import DisplayArea  # Add this import
from styles.style import SPLITTER_STYLE  # Add this import

class SidebarWindowBase(QWidget):
    def __init__(self, parent=None, title=None):
        super().__init__(parent)
        self.parent = parent
        self.has_unsaved_changes = False
        
        # Setup layout
        self.setLayout(QHBoxLayout())
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.layout().setSpacing(0)
        
        # Create splitter
        self.splitter = QSplitter(Qt.Horizontal)
        self.splitter.setStyleSheet(SPLITTER_STYLE)  # Add this line
        self.layout().addWidget(self.splitter)
        
        # Initialize sidebar and display area if title is provided
        if title:
            self.init_sidebar(title)

    def init_sidebar(self, title):
        """Initialize sidebar with title and common features"""
        self.sidebar = Sidebar(title)
        self.display_area = DisplayArea()
        
        back_btn, options_btn = self.create_footer_buttons()
        self.sidebar.add_help_button()
        self.sidebar.add_footer_divider()
        self.sidebar.setup_horizontal_footer_buttons(back_btn, options_btn)
        
        self.setup_splitter(self.sidebar, self.display_area)
        self.sidebar.button_clicked.connect(self.handle_button_click)

    def create_footer_buttons(self):
        back_btn = QPushButton("Back")
        back_btn.setObjectName("back_button")
        back_btn.clicked.connect(lambda: self.handle_button_click("Back"))
        
        options_btn = QPushButton("⚙️")
        options_btn.setObjectName("back_button")
        options_btn.setFont(QFont('Segoe UI', 14))
        options_btn.clicked.connect(lambda: self.handle_button_click("Options"))
        
        return back_btn, options_btn

    def setup_splitter(self, sidebar, content):
        self.splitter.addWidget(sidebar)
        self.splitter.addWidget(content)
        sidebar.setMinimumWidth(250)
        content.setMinimumWidth(600)
        self.update_splitter_sizes()

    def update_splitter_sizes(self):
        """Update splitter sizes to maintain proper proportions"""
        total_width = self.width()
        if total_width > 0:
            self.splitter.setSizes([250, 850])

    def resizeEvent(self, event):
        """Handle resize events to maintain splitter proportions"""
        super().resizeEvent(event)
        self.update_splitter_sizes()

    def cleanup(self): pass
    def save_state(self): pass
    def restore_state(self): pass
    def can_close(self): return not self.has_unsaved_changes

    def handle_button_click(self, button_text):
        if button_text == 'Back':
            if self.can_close():
                if not self.parent.window_manager.go_back():
                    self.parent.window_manager.show_window('main')
        elif button_text == 'Options':
            config_dialog = ConfigView(self)
            config_dialog.configSaved.connect(self._on_config_changed)
            config_dialog.exec()

    def _on_config_changed(self, config):
        """Handle configuration changes - refresh AI panels"""
        if hasattr(self, 'refresh_ai_panels'):
            self.refresh_ai_panels()