from PySide6.QtWidgets import QWidget, QHBoxLayout, QSplitter
from PySide6.QtCore import Qt

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

    def handle_button_click(self, button_text):
        if button_text == 'Back':
            if hasattr(self.parent, 'return_to_main'):
                self.parent.return_to_main()
            else:
                print("Warning: Parent window does not implement return_to_main()")