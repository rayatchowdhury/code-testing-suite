
# -*- coding: utf-8 -*-

from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QSlider, QHBoxLayout, QLineEdit
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QIntValidator
from src.app.presentation.styles.style import MATERIAL_COLORS
from src.app.presentation.styles.components.test_view_styles import (
    TEST_VIEW_SLIDER_STYLE,
    TEST_VIEW_SLIDER_VALUE_LABEL_STYLE
)

class TestCountSlider(QWidget):
    valueChanged = Signal(int)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 4, 12, 4)  # Match sidebar button margins
        
        # Slider and input container
        slider_container = QHBoxLayout()
        slider_container.setSpacing(0)  # No gap between slider and input
        slider_container.setContentsMargins(0, 0, 0, 0)  # Remove any additional margins
        
        # Create slider
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setMinimum(1)
        self.slider.setMaximum(500)  # Keep validator's higher range
        self.slider.setValue(10)
        self.slider.setStyleSheet(TEST_VIEW_SLIDER_STYLE)
        
        # Editable input field instead of just a label
        self.value_input = QLineEdit("10")
        self.value_input.setValidator(QIntValidator(1, 500))
        self.value_input.setFixedWidth(50)  # Compact width for numbers
        self.value_input.setAlignment(Qt.AlignCenter)
        
        # Add widgets to layouts
        slider_container.addWidget(self.slider)
        slider_container.addWidget(self.value_input)
        
        layout.addLayout(slider_container)
        
        # Connect signals for two-way binding
        self.slider.valueChanged.connect(self._on_slider_changed)
        self.value_input.textChanged.connect(self._on_input_changed)
        
        # Setup input field styling
        self._setup_input_styles()
    
    def _setup_input_styles(self):
        """Style the input field to match the limits input design"""
        input_style = f"""
            QLineEdit {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                           stop:0 rgba(20, 24, 28, 0.8),
                           stop:1 rgba(14, 17, 20, 0.8));
                border: 1px solid {MATERIAL_COLORS['outline']};
                border-radius: 8px;
                color: {MATERIAL_COLORS['text_primary']};
                padding: 6px 8px;
                font-size: 12px;
                font-weight: 500;
                selection-background-color: {MATERIAL_COLORS['primary']}40;
                selection-color: {MATERIAL_COLORS['on_primary']};
            }}
            
            QLineEdit:hover {{
                border: 1px solid {MATERIAL_COLORS['primary']};
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                           stop:0 {MATERIAL_COLORS['primary']}10,
                           stop:1 rgba(255, 255, 255, 0.08));
            }}
            
            QLineEdit:focus {{
                border: 2px solid {MATERIAL_COLORS['primary']};
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                           stop:0 {MATERIAL_COLORS['primary']}15,
                           stop:1 rgba(255, 255, 255, 0.08));
                outline: none;
            }}
        """
        self.value_input.setStyleSheet(input_style)
    
    def _on_slider_changed(self, value):
        """Update input field when slider changes"""
        self.value_input.setText(str(value))
        self.valueChanged.emit(value)
    
    def _on_input_changed(self, text):
        """Update slider when input field changes"""
        try:
            if text and text.isdigit():
                value = int(text)
                if 1 <= value <= 500:  # Valid range for validator
                    # Block signals to prevent recursive updates
                    self.slider.blockSignals(True)
                    self.slider.setValue(value)
                    self.slider.blockSignals(False)
                    self.valueChanged.emit(value)
        except ValueError:
            pass
    
    def value(self):
        return self.slider.value()
    
    def set_value(self, value):
        """Set the value programmatically"""
        if 1 <= value <= 500:
            self.slider.setValue(value)
            self.value_input.setText(str(value))
