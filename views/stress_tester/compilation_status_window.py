
from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QProgressBar, QPushButton
from PySide6.QtCore import Qt
from styles.style import MATERIAL_COLORS

class CompilationStatusWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Compilation Status")
        self.setFixedSize(400, 150)
        self.setWindowFlag(Qt.WindowContextHelpButtonHint, False)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        
        self.status_label = QLabel("Compiling...")
        self.status_label.setStyleSheet(f"""
            color: {MATERIAL_COLORS['on_surface']};
            font-size: 14px;
            font-weight: bold;
        """)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 3)  # 3 files to compile
        self.progress_bar.setValue(0)
        self.progress_bar.setStyleSheet(f"""
            QProgressBar {{
                border: none;
                background: {MATERIAL_COLORS['surface_variant']};
                height: 6px;
                border-radius: 3px;
            }}
            QProgressBar::chunk {{
                background: {MATERIAL_COLORS['primary']};
                border-radius: 3px;
            }}
        """)
        
        self.detail_label = QLabel("")
        self.detail_label.setStyleSheet(f"color: {MATERIAL_COLORS['text_secondary']};")
        self.detail_label.setWordWrap(True)
        
        self.close_button = QPushButton("Close")
        self.close_button.setVisible(False)
        self.close_button.clicked.connect(self.accept)
        self.close_button.setStyleSheet(f"""
            QPushButton {{
                background: {MATERIAL_COLORS['primary']};
                border: none;
                border-radius: 4px;
                color: {MATERIAL_COLORS['on_primary']};
                padding: 8px 16px;
            }}
            QPushButton:hover {{
                background: {MATERIAL_COLORS['primary_container']};
            }}
        """)
        
        layout.addWidget(self.status_label)
        layout.addWidget(self.progress_bar)
        layout.addWidget(self.detail_label)
        layout.addWidget(self.close_button, alignment=Qt.AlignCenter)
        
        self.setStyleSheet(f"""
            QDialog {{
                background: {MATERIAL_COLORS['surface']};
                border: 1px solid {MATERIAL_COLORS['outline']};
                border-radius: 8px;
            }}
        """)

    def update_status(self, file_name, success, message=""):
        if success:
            self.progress_bar.setValue(self.progress_bar.value() + 1)
        
        if message:
            self.detail_label.setText(message)
            
        if file_name == 'test' or not success:
            self.status_label.setText("Compilation Complete" if success else "Compilation Failed")
            self.close_button.setVisible(True)
            if success:
                self.status_label.setStyleSheet(f"color: {MATERIAL_COLORS['primary']};")
            else:
                self.status_label.setStyleSheet("color: #ff4444;")