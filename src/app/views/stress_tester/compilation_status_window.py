
# -*- coding: utf-8 -*-

from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QProgressBar, QPushButton
from PySide6.QtCore import Qt
from ...styles.style import MATERIAL_COLORS
from ...styles.constants.status_colors import ERROR_COLOR_HEX
from ...styles.components.stress_tester import (
    COMPILATION_STATUS_DIALOG_STYLE,
    COMPILATION_STATUS_LABEL_STYLE,
    COMPILATION_PROGRESS_BAR_STYLE,
    COMPILATION_DETAIL_LABEL_STYLE,
    COMPILATION_CLOSE_BUTTON_STYLE,
    get_compilation_status_style
)

class CompilationStatusWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Compilation Status")
        self.setFixedSize(400, 150)
        self.setWindowFlag(Qt.WindowContextHelpButtonHint, False)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        
        self.status_label = QLabel("Compiling...")
        self.status_label.setStyleSheet(COMPILATION_STATUS_LABEL_STYLE)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 3)  # 3 files to compile
        self.progress_bar.setValue(0)
        self.progress_bar.setStyleSheet(COMPILATION_PROGRESS_BAR_STYLE)
        
        self.detail_label = QLabel("")
        self.detail_label.setStyleSheet(COMPILATION_DETAIL_LABEL_STYLE)
        self.detail_label.setWordWrap(True)
        
        self.close_button = QPushButton("Close")
        self.close_button.setVisible(False)
        self.close_button.clicked.connect(self.accept)
        self.close_button.setStyleSheet(COMPILATION_CLOSE_BUTTON_STYLE)
        
        layout.addWidget(self.status_label)
        layout.addWidget(self.progress_bar)
        layout.addWidget(self.detail_label)
        layout.addWidget(self.close_button, alignment=Qt.AlignCenter)
        
        self.setStyleSheet(COMPILATION_STATUS_DIALOG_STYLE)

    def update_status(self, file_name, success, message=""):
        if success:
            self.progress_bar.setValue(self.progress_bar.value() + 1)
        
        if message:
            self.detail_label.setText(message)
            
        if file_name == 'test' or not success:
            self.status_label.setText("Compilation Complete" if success else "Compilation Failed")
            self.close_button.setVisible(True)
            if success:
                self.status_label.setStyleSheet(get_compilation_status_style(True))
            else:
                self.status_label.setStyleSheet(get_compilation_status_style(False))