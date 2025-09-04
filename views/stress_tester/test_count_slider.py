
# -*- coding: utf-8 -*-

from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QSlider, QHBoxLayout
from PySide6.QtCore import Qt, Signal
from styles.style import MATERIAL_COLORS

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
        self.slider.setStyleSheet(f"""
            QSlider::groove:horizontal {{
                border: none;
                height: 4px;
                background: {MATERIAL_COLORS['surface_variant']};
                margin: 0px;
                border-radius: 2px;
            }}
            QSlider::handle:horizontal {{
                background: {MATERIAL_COLORS['primary']};
                border: none;
                width: 16px;
                height: 16px;
                margin: -6px 0;
                border-radius: 8px;
            }}
            QSlider::handle:horizontal:hover {{
                background: {MATERIAL_COLORS['primary_container']};
            }}
            QSlider::sub-page:horizontal {{
                background: {MATERIAL_COLORS['primary']};
                border-radius: 2px;
            }}
        """)
        
        # Value label
        self.value_label = QLabel("10")
        self.value_label.setStyleSheet(f"""
            color: {MATERIAL_COLORS['on_surface']};
            font-size: 13px;
            padding: 0 8px;
            min-width: 28px;
        """)
        
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