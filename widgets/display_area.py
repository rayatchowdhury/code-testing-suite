#this is the default display area for the application which contains the default display area class
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from styles.style import DISPLAY_AREA_STYLE

class DisplayArea(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("display_area")
        self.setStyleSheet(DISPLAY_AREA_STYLE)
        
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(20, 20, 20, 20)
    
    def set_content(self, widget):
        # Clear previous content
        while self.layout.count():
            item = self.layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        # Add new content
        self.layout.addWidget(widget)