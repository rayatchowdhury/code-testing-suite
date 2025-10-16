# -*- coding: utf-8 -*-
"""
Reusable TestCountSlider widget for the Code Testing Suite application.

This widget provides a slider interface for selecting the number of test cases,
with different default configurations for different use cases (validator, comparator, benchmarker).
"""

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QIntValidator
from PySide6.QtWidgets import QHBoxLayout, QLineEdit, QSlider, QVBoxLayout, QWidget

from src.app.presentation.styles.components.test_view_styles import (
    TEST_VIEW_SLIDER_STYLE,
)
from src.app.presentation.styles.style import MATERIAL_COLORS


class TestCountSlider(QWidget):
    """
    A reusable slider widget for selecting number of test cases.

    Supports different configurations for different contexts:
    - validator: Range (1-999), default 50
    - comparator: Range (1-999), default 50
    - benchmarker: Range (1-999), default 50
    """

    __test__ = False  # Prevent pytest collection
    valueChanged = Signal(int)

    def __init__(self, parent=None, mode="validator"):
        """
        Initialize the TestCountSlider.

        Args:
            parent: Parent widget
            mode: Configuration mode - "validator", "comparator", or "benchmarker"
        """
        super().__init__(parent)
        self.mode = mode

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 4, 12, 4)  # Match sidebar button margins

        # Slider and input container
        slider_container = QHBoxLayout()
        slider_container.setSpacing(0)  # No gap between slider and input
        slider_container.setContentsMargins(0, 0, 0, 0)  # Remove any additional margins

        # Create slider with mode-specific configuration
        self.slider = QSlider(Qt.Horizontal)
        self._configure_slider_for_mode()
        self.slider.setStyleSheet(TEST_VIEW_SLIDER_STYLE)

        # Editable input field instead of just a label
        self.value_input = QLineEdit(str(self.slider.value()))
        self.value_input.setValidator(
            QIntValidator(self.slider.minimum(), self.slider.maximum())
        )
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

    def _configure_slider_for_mode(self):
        """Configure slider ranges and defaults based on mode."""
        if self.mode == "validator":
            self.slider.setMinimum(1)
            self.slider.setMaximum(999)  # High range for comprehensive validation
            self.slider.setValue(50)  # Default 50 tests
        elif self.mode == "comparator":
            self.slider.setMinimum(1)
            self.slider.setMaximum(999)  # High range for comparison tests
            self.slider.setValue(50)  # Default 50 tests
        elif self.mode == "benchmarker":
            self.slider.setMinimum(1)
            self.slider.setMaximum(999)  # High range for performance tests
            self.slider.setValue(50)  # Default 50 tests
        else:
            # Default fallback configuration
            self.slider.setMinimum(1)
            self.slider.setMaximum(999)
            self.slider.setValue(50)

    def _setup_input_styles(self):
        """Style the input field to match the limits input design."""
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
        """Update input field when slider changes."""
        self.value_input.setText(str(value))
        self.valueChanged.emit(value)

    def _on_input_changed(self, text):
        """Update slider when input field changes."""
        try:
            if text and text.isdigit():
                value = int(text)
                if (
                    self.slider.minimum() <= value <= self.slider.maximum()
                ):  # Valid range
                    # Block signals to prevent recursive updates
                    self.slider.blockSignals(True)
                    self.slider.setValue(value)
                    self.slider.blockSignals(False)
                    self.valueChanged.emit(value)
        except ValueError:
            pass

    def value(self):
        """Get the current slider value."""
        return self.slider.value()

    def set_value(self, value):
        """Set the value programmatically."""
        if self.slider.minimum() <= value <= self.slider.maximum():
            self.slider.setValue(value)
            self.value_input.setText(str(value))

    def get_range(self):
        """Get the current slider range as (min, max) tuple."""
        return (self.slider.minimum(), self.slider.maximum())

    def set_range(self, minimum, maximum):
        """Set the slider range dynamically."""
        current_value = self.value()
        self.slider.setMinimum(minimum)
        self.slider.setMaximum(maximum)
        self.value_input.setValidator(QIntValidator(minimum, maximum))

        # Ensure current value is still in valid range
        if current_value < minimum:
            self.set_value(minimum)
        elif current_value > maximum:
            self.set_value(maximum)
