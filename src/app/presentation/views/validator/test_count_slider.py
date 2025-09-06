
# -*- coding: utf-8 -*-

from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QSlider, QHBoxLayout
from PySide6.QtCore import Qt, Signal
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
        layout.setContentsMargins(8, 4, 8, 4)
        
        # Header
        
        # Slider and value display container
        slider_container = QHBoxLayout()
        
        # Create slider
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setMinimum(1)
        self.slider.setMaximum(500)
        self.slider.setValue(10)
        self.slider.setStyleSheet(TEST_VIEW_SLIDER_STYLE)
        
        # Value label
        self.value_label = QLabel("10")
        self.value_label.setStyleSheet(TEST_VIEW_SLIDER_VALUE_LABEL_STYLE)
        
        # Add widgets to layouts
        slider_container.addWidget(self.slider)
        slider_container.addWidget(self.value_label)
        
        layout.addLayout(slider_container)
        
        # Connect signals
        self.slider.valueChanged.connect(self._on_value_changed)
    
    def _on_value_changed(self, value):
        self.value_label.setText(str(value))
        self.valueChanged.emit(value)
    
    def value(self):
        return self.slider.value()
