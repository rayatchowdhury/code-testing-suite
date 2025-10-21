# this is the default display area for the application which contains the default display area class
from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget

from src.app.presentation.styles.style import DISPLAY_AREA_STYLE

class DisplayArea(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("display_area")
        self.setStyleSheet(DISPLAY_AREA_STYLE)

        self.layout = QVBoxLayout(self)  # Store as property, not method
        self.layout.setContentsMargins(0, 0, 0, 0)

    def set_content(self, widget):
        # Clear previous content
        while self.layout.count():
            item = self.layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        # Add new content
        self.layout.addWidget(widget)
