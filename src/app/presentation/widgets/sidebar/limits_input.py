# -*- coding: utf-8 -*-
"""
Reusable LimitsInputWidget for the Code Testing Suite application.

This widget provides input fields for time and memory limits,
designed to be used across different views (benchmarker, validator, comparator).
"""

from PySide6.QtCore import Signal
from PySide6.QtGui import QIntValidator
from PySide6.QtWidgets import (
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QVBoxLayout,
    QWidget,
)

from src.app.presentation.styles.style import MATERIAL_COLORS
from src.app.presentation.styles.components.inputs.input_styles import (
    INPUT_GROUP_STYLE,
    INPUT_LINEEDIT_STYLE,
    INPUT_DIVIDER_STYLE,
)

class LimitsInputWidget(QWidget):
    """
    A reusable widget for inputting time and memory limits.

    Provides time limit input (10-60000ms) and memory limit input (1-8192MB)
    with modern grouped styling and validation.
    """

    timeLimitChanged = Signal(int)  # Time limit in ms
    memoryLimitChanged = Signal(int)  # Memory limit in MB

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.setup_styles()

    def setup_ui(self):
        """Setup the UI layout - clean and simple."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(
            12, 4, 12, 4
        )  # Match sidebar button margins exactly (4px 12px)
        main_layout.setSpacing(6)  # Reduced spacing from 8 to 6

        # Horizontal container for time and memory inputs
        inputs_layout = QHBoxLayout()
        inputs_layout.setSpacing(8)  # Reduced spacing between sections

        # Time limit section with titled border
        self.time_group = QGroupBox("Time")
        time_container = QVBoxLayout(self.time_group)
        time_container.setSpacing(4)
        time_container.setContentsMargins(8, 12, 8, 8)

        self.time_input = QLineEdit()
        self.time_input.setText("1000")
        self.time_input.setValidator(QIntValidator(10, 60000))
        self.time_input.setPlaceholderText("1000")
        # Remove fixed width to allow stretching

        time_container.addWidget(self.time_input)

        # Simple vertical divider aligned with input fields only
        divider = QWidget()
        divider.setFixedWidth(1)
        divider.setFixedHeight(50)  # Adjusted height for group boxes
        divider.setContentsMargins(0, 8, 0, 0)  # Align with group box content

        # Memory limit section with titled border
        self.memory_group = QGroupBox("Memory")
        memory_container = QVBoxLayout(self.memory_group)
        memory_container.setSpacing(4)
        memory_container.setContentsMargins(8, 12, 8, 8)

        self.memory_input = QLineEdit()
        self.memory_input.setText("256")
        self.memory_input.setValidator(QIntValidator(1, 8192))
        self.memory_input.setPlaceholderText("256")
        # Remove fixed width to allow stretching

        memory_container.addWidget(self.memory_input)

        # Add to horizontal layout
        inputs_layout.addWidget(self.time_group)
        inputs_layout.addWidget(divider)
        inputs_layout.addWidget(self.memory_group)

        # Add to main layout
        main_layout.addLayout(inputs_layout)

        # Store divider for styling
        self.divider = divider

        # Connect signals
        self.time_input.textChanged.connect(self._on_time_changed)
        self.memory_input.textChanged.connect(self._on_memory_changed)

    def setup_styles(self):
        """Apply consistent styling based on app design patterns."""

        # Main widget - subtle background matching sidebar sections
        self.setStyleSheet(
            """
            LimitsInputWidget {
                background: transparent;
            }
        """
        )

        # Group box styling - modern titled borders
        self.time_group.setStyleSheet(INPUT_GROUP_STYLE)
        self.memory_group.setStyleSheet(INPUT_GROUP_STYLE)

        # Input fields - using centralized style
        self.time_input.setStyleSheet(INPUT_LINEEDIT_STYLE)
        self.memory_input.setStyleSheet(INPUT_LINEEDIT_STYLE)

        # Simple divider - following sidebar divider pattern
        self.divider.setStyleSheet(INPUT_DIVIDER_STYLE)

    def _on_time_changed(self, text):
        """Handle time input change with validation feedback."""
        try:
            if text and text.isdigit():
                value = int(text)
                if 10 <= value <= 60000:
                    self.timeLimitChanged.emit(value)
        except ValueError:
            pass

    def _on_memory_changed(self, text):
        """Handle memory input change with validation feedback."""
        try:
            if text and text.isdigit():
                value = int(text)
                if 1 <= value <= 8192:
                    self.memoryLimitChanged.emit(value)
        except ValueError:
            pass

    def get_time_limit(self):
        """Get current time limit value."""
        try:
            return int(self.time_input.text()) if self.time_input.text() else 1000
        except ValueError:
            return 1000

    def get_memory_limit(self):
        """Get current memory limit value."""
        try:
            return int(self.memory_input.text()) if self.memory_input.text() else 256
        except ValueError:
            return 256

    def set_time_limit(self, value):
        """Set time limit value."""
        self.time_input.setText(str(value))

    def set_memory_limit(self, value):
        """Set memory limit value."""
        self.memory_input.setText(str(value))
