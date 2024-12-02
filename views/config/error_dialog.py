
from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QFrame
from PySide6.QtCore import Qt

class ErrorDialog(QDialog):
    def __init__(self, title, message, details=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("⚠️ " + title)
        self.setModal(True)
        self.setFixedWidth(400)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        
        # Error icon and message
        message_frame = QFrame()
        message_frame.setObjectName("error_frame")
        message_layout = QVBoxLayout(message_frame)
        
        icon_label = QLabel("⚠️")
        icon_label.setAlignment(Qt.AlignCenter)
        icon_label.setStyleSheet("font-size: 48px;")
        
        error_label = QLabel(message)
        error_label.setWordWrap(True)
        error_label.setStyleSheet("color: #ff6b6b; font-size: 14px;")
        
        message_layout.addWidget(icon_label)
        message_layout.addWidget(error_label)
        
        # Details section if provided
        if details:
            details_label = QLabel(details)
            details_label.setWordWrap(True)
            details_label.setStyleSheet("color: #8b949e; font-size: 12px;")
            message_layout.addWidget(details_label)
        
        # OK button
        ok_button = QPushButton("OK")
        ok_button.setFixedWidth(100)
        ok_button.clicked.connect(self.accept)
        
        layout.addWidget(message_frame)
        layout.addWidget(ok_button, alignment=Qt.AlignCenter)
        
        self.setStyleSheet("""
            QDialog {
                background-color: #1e1e1e;
                border: 1px solid #333;
            }
            #error_frame {
                background-color: #2d2d2d;
                border-radius: 8px;
                padding: 20px;
            }
            QPushButton {
                background-color: #ff6b6b;
                border: none;
                color: white;
                padding: 8px 16px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #fa5252;
            }
        """)