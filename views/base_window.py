from PySide6.QtWidgets import QWidget, QHBoxLayout, QSplitter
from PySide6.QtCore import Qt, QTimer
from views.config.config_view import ConfigView  # Add this import

class SidebarWindowBase(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        
        # Set default window size
        self.resize(1200, 800)  # Default size for all windows
        
        # Create main layout
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Create splitter
        self.splitter = QSplitter(Qt.Horizontal)
        layout.addWidget(self.splitter)
        
        # Style the splitter
        self.splitter.setStyleSheet("""
            QSplitter::handle {
                background-color: #333333;
                width: 2px;
            }
            QSplitter::handle:hover {
                background-color: #0096C7;
            }
        """)
        
        self.has_unsaved_changes = False

    def setup_splitter(self, sidebar, content):
        # Add widgets to splitter
        self.splitter.addWidget(sidebar)
        self.splitter.addWidget(content)
        
        # Set initial sizes (25% sidebar, 75% content)
        total_width = self.width()
        self.splitter.setSizes([int(total_width * 0.25), int(total_width * 0.75)])
        
        # Set minimum widths
        sidebar.setMinimumWidth(250)
        content.setMinimumWidth(600)

    def cleanup(self):
        """Clean up resources before window is destroyed"""
        pass

    def save_state(self):
        """Save window state before hiding"""
        pass

    def restore_state(self):
        """Restore window state when shown"""
        pass

    def can_close(self):
        """Check if window can be closed"""
        return not self.has_unsaved_changes

    def handle_button_click(self, button_text):
        if button_text == 'Back':
            if self.can_close():
                self.parent.window_manager.show_window('main')
        elif button_text == 'Options':
            config_dialog = ConfigView(self)
            config_dialog.exec()