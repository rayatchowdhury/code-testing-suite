# this is the default display area for the application which contains the default display area class
from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget

from src.app.presentation.shared.design_system.styles.style import DISPLAY_AREA_STYLE

class DisplayArea(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("display_area")
        self.setStyleSheet(DISPLAY_AREA_STYLE)

        self._layout = QVBoxLayout(self)  # Private - use set_content() API
        self._layout.setContentsMargins(0, 0, 0, 0)

    def set_content(self, widget):
        """Set display area content - properly clears old widgets first"""
        self.clear_content()
        self._layout.addWidget(widget)

    def swap_content(self, new_widget):
        """
        Swap content without deleting the old widget.
        Returns the old widget (if any) for caller to manage.
        Use case: Temporary status views that need to restore original content.
        """
        old_widget = None
        if self._layout.count() > 0:
            item = self._layout.takeAt(0)
            if item.widget():
                old_widget = item.widget()
                old_widget.setParent(None)
                old_widget.hide()
        
        self._layout.addWidget(new_widget)
        new_widget.show()
        return old_widget

    def clear_content(self):
        """Explicitly clear all content widgets"""
        while self._layout.count():
            item = self._layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

