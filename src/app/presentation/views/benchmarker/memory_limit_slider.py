from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QSlider, QHBoxLayout
from PySide6.QtCore import Qt, Signal
from src.app.presentation.styles.style import MATERIAL_COLORS
from src.app.presentation.styles.components.test_view_styles import TEST_VIEW_SLIDER_STYLE, TEST_VIEW_SLIDER_VALUE_LABEL_STYLE

class MemoryLimitSlider(QWidget):
    valueChanged = Signal(int)  # Memory limit in MB
    
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 4, 8, 4)
        
        # Slider and value display container
        slider_container = QHBoxLayout()
        
        # Create slider (values represent MB directly)
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setMinimum(1)      # 1MB minimum
        self.slider.setMaximum(2048)   # 2048MB (2GB) maximum
        self.slider.setValue(256)      # 256MB default
        self.slider.setStyleSheet(TEST_VIEW_SLIDER_STYLE)
        
        # Value label showing MB
        self.value_label = QLabel("256")
        self.value_label.setStyleSheet(TEST_VIEW_SLIDER_VALUE_LABEL_STYLE)
        
        slider_container.addWidget(self.slider)
        slider_container.addWidget(self.value_label)
        
        layout.addLayout(slider_container)
        
        self.slider.valueChanged.connect(self._on_value_changed)
    
    def _on_value_changed(self, value):
        self.value_label.setText(f"{value}")  # Display raw MB
        self.valueChanged.emit(value)
    
    def value(self):
        return self.slider.value()  # Return raw MB
