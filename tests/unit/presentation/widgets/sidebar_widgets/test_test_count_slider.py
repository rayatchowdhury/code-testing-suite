# -*- coding: utf-8 -*-
"""
Unit tests for TestCountSlider - sidebar widget for test count selection.

This widget provides a slider with editable input for selecting number of test cases,
used across all test windows (validator, comparator, benchmarker).
"""

from unittest.mock import Mock

import pytest
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLineEdit, QSlider

from src.app.presentation.widgets.sidebar.test_count_slider import (
    TestCountSlider,
)


class TestTestCountSliderInitialization:
    """Test proper initialization of the TestCountSlider widget."""

    def test_creates_widget_with_default_mode(self, qtbot):
        """Widget should initialize with validator mode by default."""
        widget = TestCountSlider()
        qtbot.addWidget(widget)

        assert widget.mode == "validator"
        assert widget.slider.value() == 50  # Default for validator

    def test_creates_widget_with_comparator_mode(self, qtbot):
        """Widget should initialize with comparator mode when specified."""
        widget = TestCountSlider(mode="comparator")
        qtbot.addWidget(widget)

        assert widget.mode == "comparator"
        assert widget.slider.value() == 50  # Default for comparator

    def test_creates_widget_with_benchmarker_mode(self, qtbot):
        """Widget should initialize with benchmarker mode when specified."""
        widget = TestCountSlider(mode="benchmarker")
        qtbot.addWidget(widget)

        assert widget.mode == "benchmarker"
        assert widget.slider.value() == 50  # Default for benchmarker

    def test_creates_horizontal_slider(self, qtbot):
        """Widget should contain a horizontal QSlider."""
        widget = TestCountSlider()
        qtbot.addWidget(widget)

        assert isinstance(widget.slider, QSlider)
        assert widget.slider.orientation() == Qt.Horizontal

    def test_creates_editable_value_input(self, qtbot):
        """Widget should contain an editable QLineEdit for direct value entry."""
        widget = TestCountSlider()
        qtbot.addWidget(widget)

        assert isinstance(widget.value_input, QLineEdit)
        assert widget.value_input.text() == "50"  # Should match slider default
        assert widget.value_input.alignment() == Qt.AlignCenter


class TestTestCountSliderRange:
    """Test slider range configuration for different modes."""

    def test_validator_mode_has_correct_range(self, qtbot):
        """Validator mode should have range 1-999."""
        widget = TestCountSlider(mode="validator")
        qtbot.addWidget(widget)

        assert widget.slider.minimum() == 1
        assert widget.slider.maximum() == 999
        assert widget.get_range() == (1, 999)

    def test_comparator_mode_has_correct_range(self, qtbot):
        """Comparator mode should have range 1-999."""
        widget = TestCountSlider(mode="comparator")
        qtbot.addWidget(widget)

        assert widget.slider.minimum() == 1
        assert widget.slider.maximum() == 999
        assert widget.get_range() == (1, 999)

    def test_benchmarker_mode_has_correct_range(self, qtbot):
        """Benchmarker mode should have range 1-999."""
        widget = TestCountSlider(mode="benchmarker")
        qtbot.addWidget(widget)

        assert widget.slider.minimum() == 1
        assert widget.slider.maximum() == 999
        assert widget.get_range() == (1, 999)

    def test_can_set_custom_range(self, qtbot):
        """Widget should allow setting custom range dynamically."""
        widget = TestCountSlider()
        qtbot.addWidget(widget)

        widget.set_range(10, 500)

        assert widget.slider.minimum() == 10
        assert widget.slider.maximum() == 500
        assert widget.get_range() == (10, 500)


class TestTestCountSliderValueManagement:
    """Test value getting, setting, and synchronization."""

    def test_value_returns_current_slider_value(self, qtbot):
        """value() should return the current slider value."""
        widget = TestCountSlider()
        qtbot.addWidget(widget)

        widget.slider.setValue(100)
        assert widget.value() == 100

    def test_set_value_updates_slider_and_input(self, qtbot):
        """set_value() should update both slider and input field."""
        widget = TestCountSlider()
        qtbot.addWidget(widget)

        widget.set_value(250)

        assert widget.slider.value() == 250
        assert widget.value_input.text() == "250"

    def test_set_value_respects_range_limits(self, qtbot):
        """set_value() should only accept values within current range."""
        widget = TestCountSlider()
        qtbot.addWidget(widget)

        # Try to set value above maximum (999)
        initial_value = widget.value()
        widget.set_value(1500)

        # Value should not change (outside range)
        assert widget.value() == initial_value

    def test_range_change_adjusts_out_of_bounds_value(self, qtbot):
        """Changing range should adjust value if it's now out of bounds."""
        widget = TestCountSlider()
        qtbot.addWidget(widget)

        widget.set_value(800)  # Set to high value
        assert widget.value() == 800

        # Reduce maximum to 500
        widget.set_range(1, 500)

        # Value should be capped at new maximum
        assert widget.value() == 500
        assert widget.value_input.text() == "500"


class TestTestCountSliderSignals:
    """Test signal emission for value changes."""

    def test_emits_value_changed_on_slider_move(self, qtbot):
        """Widget should emit valueChanged signal when slider is moved."""
        widget = TestCountSlider()
        qtbot.addWidget(widget)

        signal_spy = Mock()
        widget.valueChanged.connect(signal_spy)

        widget.slider.setValue(200)

        # Signal is emitted twice - once from slider, once from input sync
        # Just verify it was called with correct value
        assert signal_spy.call_count >= 1
        signal_spy.assert_any_call(200)

    def test_emits_value_changed_on_input_edit(self, qtbot):
        """Widget should emit valueChanged signal when input field is edited."""
        widget = TestCountSlider()
        qtbot.addWidget(widget)

        signal_spy = Mock()
        widget.valueChanged.connect(signal_spy)

        widget.value_input.setText("300")

        # Should emit signal with new value
        signal_spy.assert_called_with(300)

    def test_slider_and_input_stay_synchronized(self, qtbot):
        """Slider and input field should stay synchronized during changes."""
        widget = TestCountSlider()
        qtbot.addWidget(widget)

        # Change slider
        widget.slider.setValue(150)
        assert widget.value_input.text() == "150"

        # Change input
        widget.value_input.setText("75")
        assert widget.slider.value() == 75


class TestTestCountSliderInputValidation:
    """Test input field validation."""

    def test_input_field_has_validator(self, qtbot):
        """Input field should have a validator matching slider range."""
        widget = TestCountSlider()
        qtbot.addWidget(widget)

        validator = widget.value_input.validator()
        assert validator is not None
        assert validator.bottom() == 1
        assert validator.top() == 999

    def test_validator_updates_with_range_change(self, qtbot):
        """Input validator should update when slider range changes."""
        widget = TestCountSlider()
        qtbot.addWidget(widget)

        widget.set_range(10, 200)

        validator = widget.value_input.validator()
        assert validator.bottom() == 10
        assert validator.top() == 200

    def test_input_rejects_out_of_range_values(self, qtbot):
        """Input field should not update slider for out-of-range values."""
        widget = TestCountSlider()
        qtbot.addWidget(widget)

        initial_slider_value = widget.slider.value()

        # Try to enter value above maximum
        widget.value_input.setText("2000")

        # Slider should not change (value is outside range)
        assert widget.slider.value() == initial_slider_value


class TestTestCountSliderEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_accepts_minimum_value(self, qtbot):
        """Widget should accept minimum value (1)."""
        widget = TestCountSlider()
        qtbot.addWidget(widget)

        widget.set_value(1)
        assert widget.value() == 1
        assert widget.value_input.text() == "1"

    def test_accepts_maximum_value(self, qtbot):
        """Widget should accept maximum value (999)."""
        widget = TestCountSlider()
        qtbot.addWidget(widget)

        widget.set_value(999)
        assert widget.value() == 999
        assert widget.value_input.text() == "999"

    def test_handles_empty_input_gracefully(self, qtbot):
        """Widget should handle empty input without crashing."""
        widget = TestCountSlider()
        qtbot.addWidget(widget)

        initial_value = widget.value()

        # Clear input
        widget.value_input.setText("")

        # Should not crash; slider keeps its value
        assert widget.slider.value() == initial_value
