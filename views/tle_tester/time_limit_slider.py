from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QSlider, QHBoxLayout
from PySide6.QtCore import Qt, Signal
from styles.style import MATERIAL_COLORS

class TimeLimitSlider(QWidget):
    valueChanged = Signal(int)  # Changed to int for milliseconds
    
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 4, 8, 4)
        
        # Slider and value display container
        slider_container = QHBoxLayout()
        
        # Create slider (values represent milliseconds directly)
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setMinimum(10)     # 10ms minimum
        self.slider.setMaximum(5000)   # 5000ms (5 seconds) maximum
        self.slider.setValue(1000)     # 1000ms (1 second) default
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
        
        # Value label showing milliseconds
        self.value_label = QLabel("1000")
        self.value_label.setStyleSheet(f"""
            color: {MATERIAL_COLORS['on_surface']};
            font-size: 13px;
            padding: 0 8px;
            min-width: 36px;
        """)
        
        slider_container.addWidget(self.slider)
        slider_container.addWidget(self.value_label)
        
        layout.addLayout(slider_container)
        
        self.slider.valueChanged.connect(self._on_value_changed)
    
    def _on_value_changed(self, value):
        self.value_label.setText(f"{value}")  # Display raw milliseconds
        self.valueChanged.emit(value)
    
    def value(self):
        return self.slider.value()  # Return raw milliseconds