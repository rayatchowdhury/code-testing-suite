"""Error dialog for configuration and other error messages."""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTextEdit, QFrame
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

from ...styles.constants.colors import MATERIAL_COLORS
from ...styles.components.config_ui import ERROR_DIALOG_STYLE


class ErrorDialog(QDialog):
    """A styled error dialog for displaying error messages with optional details."""
    
    def __init__(self, title, message, details=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setMinimumSize(400, 200)
        self.setMaximumWidth(600)
        self.setWindowFlag(Qt.WindowContextHelpButtonHint, False)
        
        self.title_text = title
        self.message_text = message
        self.details_text = details
        
        self._setup_ui()
        self._setup_styles()

    def _setup_ui(self):
        """Set up the UI components."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)

        # Title label
        title_label = QLabel(self.title_text)
        title_label.setObjectName("error_title")
        title_font = QFont()
        title_font.setBold(True)
        title_font.setPointSize(14)
        title_label.setFont(title_font)
        layout.addWidget(title_label)

        # Message label
        message_label = QLabel(self.message_text)
        message_label.setObjectName("error_message")
        message_label.setWordWrap(True)
        layout.addWidget(message_label)

        # Details section (if provided)
        if self.details_text:
            # Separator
            separator = QFrame()
            separator.setFrameShape(QFrame.HLine)
            separator.setObjectName("error_separator")
            layout.addWidget(separator)

            # Details label
            details_label = QLabel("Details:")
            details_label.setObjectName("error_details_label")
            details_font = QFont()
            details_font.setBold(True)
            details_label.setFont(details_font)
            layout.addWidget(details_label)

            # Details text
            details_text = QTextEdit()
            details_text.setObjectName("error_details")
            details_text.setPlainText(self.details_text)
            details_text.setReadOnly(True)
            details_text.setMaximumHeight(150)
            layout.addWidget(details_text)

        # Button layout
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        # OK button
        ok_button = QPushButton("OK")
        ok_button.setObjectName("error_ok_button")
        ok_button.setDefault(True)
        ok_button.clicked.connect(self.accept)
        button_layout.addWidget(ok_button)

        layout.addLayout(button_layout)

    def _setup_styles(self):
        """Apply styling to the dialog."""
        self.setStyleSheet(ERROR_DIALOG_STYLE)

    @staticmethod
    def show_error(title, message, details=None, parent=None):
        """Convenience method to show an error dialog."""
        dialog = ErrorDialog(title, message, details, parent)
        return dialog.exec()
