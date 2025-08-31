
from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QFrame
from PySide6.QtCore import Qt
from styles.constants.colors import MATERIAL_COLORS

class ErrorDialog(QDialog):
    def __init__(self, title, message, details=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("⚠️ " + title)
        self.setModal(True)
        self.setFixedWidth(450)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Error icon and message
        message_frame = QFrame()
        message_frame.setObjectName("error_frame")
        message_layout = QVBoxLayout(message_frame)
        message_layout.setSpacing(15)
        
        icon_label = QLabel("⚠️")
        icon_label.setAlignment(Qt.AlignCenter)
        icon_label.setStyleSheet("font-size: 48px; margin: 10px;")
        
        error_label = QLabel(message)
        error_label.setWordWrap(True)
        error_label.setAlignment(Qt.AlignCenter)
        error_label.setStyleSheet(f"""
            color: {MATERIAL_COLORS['error']};
            font-size: 14px;
            font-weight: 500;
            font-family: 'Segoe UI', system-ui;
            margin: 5px;
        """)
        
        message_layout.addWidget(icon_label)
        message_layout.addWidget(error_label)
        
        # Details section if provided
        if details:
            details_label = QLabel(details)
            details_label.setWordWrap(True)
            details_label.setAlignment(Qt.AlignCenter)
            details_label.setStyleSheet(f"""
                color: {MATERIAL_COLORS['on_surface_variant']};
                font-size: 12px;
                font-family: 'Segoe UI', system-ui;
                margin: 5px;
            """)
            message_layout.addWidget(details_label)
        
        # OK button
        ok_button = QPushButton("OK")
        ok_button.setFixedWidth(120)
        ok_button.setObjectName("error_button")
        ok_button.clicked.connect(self.accept)
        
        layout.addWidget(message_frame)
        layout.addWidget(ok_button, alignment=Qt.AlignCenter)
        
        self.setStyleSheet(f"""
            QDialog {{
                background: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1,
                    stop:0 rgba(22, 22, 24, 0.98),
                    stop:0.3 rgba(26, 26, 28, 0.95),
                    stop:0.7 rgba(22, 22, 24, 0.98),
                    stop:1 rgba(26, 26, 28, 0.95));
                border: 2px solid {MATERIAL_COLORS['error']}40;
                border-radius: 12px;
                font-family: 'Segoe UI', system-ui;
            }}
            #error_frame {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                           stop:0 rgba(255, 107, 107, 0.05),
                           stop:1 rgba(255, 107, 107, 0.02));
                border: 1px solid {MATERIAL_COLORS['error']}20;
                border-radius: 12px;
                padding: 20px;
            }}
            QPushButton#error_button {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                           stop:0 {MATERIAL_COLORS['error']},
                           stop:1 {MATERIAL_COLORS['error']}CC);
                border: 1px solid {MATERIAL_COLORS['error']};
                color: white;
                padding: 10px 20px;
                border-radius: 8px;
                font-weight: 600;
                font-size: 13px;
                font-family: 'Segoe UI', system-ui;
            }}
            QPushButton#error_button:hover {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                           stop:0 {MATERIAL_COLORS['error']}E6,
                           stop:1 {MATERIAL_COLORS['error']}B3);
                border: 1px solid {MATERIAL_COLORS['error']}E6;
            }}
            QPushButton#error_button:pressed {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                           stop:0 {MATERIAL_COLORS['error']}CC,
                           stop:1 {MATERIAL_COLORS['error']}99);
            }}
        """)