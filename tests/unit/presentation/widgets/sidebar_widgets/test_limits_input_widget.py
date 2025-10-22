# -*- coding: utf-8 -*-
"""
Unit tests for LimitsInputWidget - sidebar widget for time/memory limit inputs.

This widget is used across all test windows (validator, comparator, benchmarker)
to provide consistent input for execution constraints.
"""

from unittest.mock import Mock

import pytest
from PySide6.QtCore import Qt
from PySide6.QtGui import QValidator
from PySide6.QtWidgets import QGroupBox, QLineEdit

from src.app.presentation.shared.components.sidebar.limits_input import (
    LimitsInputWidget,
)


class TestLimitsInputWidgetInitialization:
    """Test proper initialization of the LimitsInputWidget."""

    def test_creates_widget_with_default_values(self, qtbot):
        """Widget should initialize with default time (1000ms) and memory (256MB) values."""
        widget = LimitsInputWidget()
        qtbot.addWidget(widget)

        assert widget.time_input.text() == "1000"
        assert widget.memory_input.text() == "256"

    def test_creates_time_and_memory_input_fields(self, qtbot):
        """Widget should have QLineEdit fields for time and memory inputs."""
        widget = LimitsInputWidget()
        qtbot.addWidget(widget)

        assert isinstance(widget.time_input, QLineEdit)
        assert isinstance(widget.memory_input, QLineEdit)
        assert widget.time_input.placeholderText() == "1000"
        assert widget.memory_input.placeholderText() == "256"

    def test_creates_titled_group_boxes(self, qtbot):
        """Widget should use QGroupBox containers with "Time" and "Memory" titles."""
        widget = LimitsInputWidget()
        qtbot.addWidget(widget)

        assert isinstance(widget.time_group, QGroupBox)
        assert isinstance(widget.memory_group, QGroupBox)
        assert widget.time_group.title() == "Time"
        assert widget.memory_group.title() == "Memory"

    def test_creates_visual_divider(self, qtbot):
        """Widget should have a divider between time and memory sections."""
        widget = LimitsInputWidget()
        qtbot.addWidget(widget)

        assert hasattr(widget, "divider")
        assert widget.divider.width() == 1


class TestLimitsInputWidgetValidation:
    """Test input validation for time and memory limits."""

    def test_time_input_has_correct_validator(self, qtbot):
        """Time input should accept values between 10 and 60000 ms."""
        widget = LimitsInputWidget()
        qtbot.addWidget(widget)

        validator = widget.time_input.validator()
        assert validator is not None
        assert validator.bottom() == 10
        assert validator.top() == 60000

    def test_memory_input_has_correct_validator(self, qtbot):
        """Memory input should accept values between 1 and 8192 MB."""
        widget = LimitsInputWidget()
        qtbot.addWidget(widget)

        validator = widget.memory_input.validator()
        assert validator is not None
        assert validator.bottom() == 1
        assert validator.top() == 8192

    def test_validator_enforces_time_range(self, qtbot):
        """Time input validator should enforce range constraints."""
        widget = LimitsInputWidget()
        qtbot.addWidget(widget)

        validator = widget.time_input.validator()

        # Test below minimum - validator should reject
        state, text, pos = validator.validate("5", 0)
        assert state != QValidator.Acceptable

        # Test above maximum - validator should reject
        state, text, pos = validator.validate("100000", 0)
        assert state != QValidator.Acceptable

        # Test valid value - validator should accept
        state, text, pos = validator.validate("1000", 0)
        assert state == QValidator.Acceptable

    def test_validator_enforces_memory_range(self, qtbot):
        """Memory input validator should enforce range constraints."""
        widget = LimitsInputWidget()
        qtbot.addWidget(widget)

        validator = widget.memory_input.validator()

        # Test below minimum - validator should reject
        state, text, pos = validator.validate("0", 0)
        assert state != QValidator.Acceptable

        # Test above maximum - validator should reject
        state, text, pos = validator.validate("10000", 0)
        assert state != QValidator.Acceptable

        # Test valid value - validator should accept
        state, text, pos = validator.validate("256", 0)
        assert state == QValidator.Acceptable


class TestLimitsInputWidgetSignals:
    """Test signal emission for value changes."""

    def test_emits_time_limit_changed_signal(self, qtbot):
        """Widget should emit timeLimitChanged signal when time value changes."""
        widget = LimitsInputWidget()
        qtbot.addWidget(widget)

        signal_spy = Mock()
        widget.timeLimitChanged.connect(signal_spy)

        # Change to valid value
        widget.time_input.setText("2000")

        # Signal should be emitted with the new value
        signal_spy.assert_called_once_with(2000)

    def test_emits_memory_limit_changed_signal(self, qtbot):
        """Widget should emit memoryLimitChanged signal when memory value changes."""
        widget = LimitsInputWidget()
        qtbot.addWidget(widget)

        signal_spy = Mock()
        widget.memoryLimitChanged.connect(signal_spy)

        # Change to valid value
        widget.memory_input.setText("512")

        # Signal should be emitted with the new value
        signal_spy.assert_called_once_with(512)

    def test_does_not_emit_signal_for_invalid_time(self, qtbot):
        """Widget should not emit signal for invalid time values."""
        widget = LimitsInputWidget()
        qtbot.addWidget(widget)

        signal_spy = Mock()
        widget.timeLimitChanged.connect(signal_spy)

        # Try to set invalid value (below minimum)
        widget.time_input.setText("5")

        # Signal should not be emitted
        signal_spy.assert_not_called()

    def test_does_not_emit_signal_for_invalid_memory(self, qtbot):
        """Widget should not emit signal for invalid memory values."""
        widget = LimitsInputWidget()
        qtbot.addWidget(widget)

        signal_spy = Mock()
        widget.memoryLimitChanged.connect(signal_spy)

        # Try to set invalid value (below minimum)
        widget.memory_input.setText("0")

        # Signal should not be emitted
        signal_spy.assert_not_called()


class TestLimitsInputWidgetGettersSetters:
    """Test getter and setter methods."""

    def test_get_time_limit_returns_current_value(self, qtbot):
        """get_time_limit() should return the current time limit value."""
        widget = LimitsInputWidget()
        qtbot.addWidget(widget)

        widget.time_input.setText("3000")
        assert widget.get_time_limit() == 3000

    def test_get_memory_limit_returns_current_value(self, qtbot):
        """get_memory_limit() should return the current memory limit value."""
        widget = LimitsInputWidget()
        qtbot.addWidget(widget)

        widget.memory_input.setText("1024")
        assert widget.get_memory_limit() == 1024

    def test_get_time_limit_returns_default_on_empty(self, qtbot):
        """get_time_limit() should return default (1000) when input is empty."""
        widget = LimitsInputWidget()
        qtbot.addWidget(widget)

        widget.time_input.setText("")
        assert widget.get_time_limit() == 1000

    def test_get_memory_limit_returns_default_on_empty(self, qtbot):
        """get_memory_limit() should return default (256) when input is empty."""
        widget = LimitsInputWidget()
        qtbot.addWidget(widget)

        widget.memory_input.setText("")
        assert widget.get_memory_limit() == 256

    def test_set_time_limit_updates_input(self, qtbot):
        """set_time_limit() should update the time input field."""
        widget = LimitsInputWidget()
        qtbot.addWidget(widget)

        widget.set_time_limit(5000)
        assert widget.time_input.text() == "5000"

    def test_set_memory_limit_updates_input(self, qtbot):
        """set_memory_limit() should update the memory input field."""
        widget = LimitsInputWidget()
        qtbot.addWidget(widget)

        widget.set_memory_limit(2048)
        assert widget.memory_input.text() == "2048"

    def test_getter_handles_invalid_text_gracefully(self, qtbot):
        """Getters should return defaults when text is invalid."""
        widget = LimitsInputWidget()
        qtbot.addWidget(widget)

        # Manually set invalid text (bypassing validator)
        widget.time_input.blockSignals(True)
        widget.time_input.setText("invalid")
        widget.time_input.blockSignals(False)

        assert widget.get_time_limit() == 1000  # Should return default


class TestLimitsInputWidgetEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_accepts_minimum_time_limit(self, qtbot):
        """Widget should accept minimum time limit (10ms)."""
        widget = LimitsInputWidget()
        qtbot.addWidget(widget)

        widget.time_input.setText("10")
        assert widget.get_time_limit() == 10

    def test_accepts_maximum_time_limit(self, qtbot):
        """Widget should accept maximum time limit (60000ms)."""
        widget = LimitsInputWidget()
        qtbot.addWidget(widget)

        widget.time_input.setText("60000")
        assert widget.get_time_limit() == 60000

    def test_accepts_minimum_memory_limit(self, qtbot):
        """Widget should accept minimum memory limit (1MB)."""
        widget = LimitsInputWidget()
        qtbot.addWidget(widget)

        widget.memory_input.setText("1")
        assert widget.get_memory_limit() == 1

    def test_accepts_maximum_memory_limit(self, qtbot):
        """Widget should accept maximum memory limit (8192MB)."""
        widget = LimitsInputWidget()
        qtbot.addWidget(widget)

        widget.memory_input.setText("8192")
        assert widget.get_memory_limit() == 8192


class TestLimitsInputWidgetExceptionHandling:
    """Test exception handling in validation methods."""

    def test_on_time_changed_handles_non_digit_text(self, qtbot):
        """_on_time_changed should handle non-digit text gracefully."""
        widget = LimitsInputWidget()
        qtbot.addWidget(widget)

        signal_spy = Mock()
        widget.timeLimitChanged.connect(signal_spy)

        # Simulate invalid text that passes the validator but causes ValueError
        # This tests the ValueError exception path on line 172
        widget._on_time_changed("abc")

        # Signal should not be emitted
        signal_spy.assert_not_called()

    def test_on_time_changed_handles_empty_text(self, qtbot):
        """_on_time_changed should handle empty text gracefully."""
        widget = LimitsInputWidget()
        qtbot.addWidget(widget)

        signal_spy = Mock()
        widget.timeLimitChanged.connect(signal_spy)

        # Test empty string
        widget._on_time_changed("")

        # Signal should not be emitted for empty text
        signal_spy.assert_not_called()

    def test_on_memory_changed_handles_non_digit_text(self, qtbot):
        """_on_memory_changed should handle non-digit text gracefully."""
        widget = LimitsInputWidget()
        qtbot.addWidget(widget)

        signal_spy = Mock()
        widget.memoryLimitChanged.connect(signal_spy)

        # This tests the ValueError exception path on line 182
        widget._on_memory_changed("xyz")

        # Signal should not be emitted
        signal_spy.assert_not_called()

    def test_on_memory_changed_handles_empty_text(self, qtbot):
        """_on_memory_changed should handle empty text gracefully."""
        widget = LimitsInputWidget()
        qtbot.addWidget(widget)

        signal_spy = Mock()
        widget.memoryLimitChanged.connect(signal_spy)

        # Test empty string
        widget._on_memory_changed("")

        # Signal should not be emitted for empty text
        signal_spy.assert_not_called()

    def test_get_time_limit_handles_value_error(self, qtbot):
        """get_time_limit should return default on ValueError."""
        widget = LimitsInputWidget()
        qtbot.addWidget(widget)

        # Manually set invalid text that can't be converted to int
        # This tests the ValueError exception path on line 196
        widget.time_input.blockSignals(True)
        widget.time_input.setText("not_a_number")
        widget.time_input.blockSignals(False)

        # Should return default value 1000
        assert widget.get_time_limit() == 1000

    def test_get_memory_limit_handles_value_error(self, qtbot):
        """get_memory_limit should return default on ValueError."""
        widget = LimitsInputWidget()
        qtbot.addWidget(widget)

        # Manually set invalid text that can't be converted to int
        # This tests the ValueError exception path
        widget.memory_input.blockSignals(True)
        widget.memory_input.setText("invalid_value")
        widget.memory_input.blockSignals(False)

        # Should return default value 256
        assert widget.get_memory_limit() == 256

    def test_on_time_changed_rejects_out_of_range_low(self, qtbot):
        """_on_time_changed should not emit signal for values below 10."""
        widget = LimitsInputWidget()
        qtbot.addWidget(widget)

        signal_spy = Mock()
        widget.timeLimitChanged.connect(signal_spy)

        # Value below minimum
        widget._on_time_changed("5")

        signal_spy.assert_not_called()

    def test_on_time_changed_rejects_out_of_range_high(self, qtbot):
        """_on_time_changed should not emit signal for values above 60000."""
        widget = LimitsInputWidget()
        qtbot.addWidget(widget)

        signal_spy = Mock()
        widget.timeLimitChanged.connect(signal_spy)

        # Value above maximum
        widget._on_time_changed("70000")

        signal_spy.assert_not_called()

    def test_on_memory_changed_rejects_out_of_range_low(self, qtbot):
        """_on_memory_changed should not emit signal for values below 1."""
        widget = LimitsInputWidget()
        qtbot.addWidget(widget)

        signal_spy = Mock()
        widget.memoryLimitChanged.connect(signal_spy)

        # Value below minimum
        widget._on_memory_changed("0")

        signal_spy.assert_not_called()

    def test_on_memory_changed_rejects_out_of_range_high(self, qtbot):
        """_on_memory_changed should not emit signal for values above 8192."""
        widget = LimitsInputWidget()
        qtbot.addWidget(widget)

        signal_spy = Mock()
        widget.memoryLimitChanged.connect(signal_spy)

        # Value above maximum
        widget._on_memory_changed("10000")

        signal_spy.assert_not_called()


class TestLimitsInputWidgetSetterMethods:
    """Test setter methods for time and memory limits."""

    def test_set_time_limit_with_various_values(self, qtbot):
        """set_time_limit should correctly set different time values."""
        widget = LimitsInputWidget()
        qtbot.addWidget(widget)

        test_values = [10, 100, 1000, 5000, 30000, 60000]
        for value in test_values:
            widget.set_time_limit(value)
            assert widget.time_input.text() == str(value)
            assert widget.get_time_limit() == value

    def test_set_memory_limit_with_various_values(self, qtbot):
        """set_memory_limit should correctly set different memory values."""
        widget = LimitsInputWidget()
        qtbot.addWidget(widget)

        test_values = [1, 64, 128, 256, 512, 1024, 4096, 8192]
        for value in test_values:
            widget.set_memory_limit(value)
            assert widget.memory_input.text() == str(value)
            assert widget.get_memory_limit() == value

    def test_set_time_limit_emits_signal(self, qtbot):
        """set_time_limit should trigger timeLimitChanged signal."""
        widget = LimitsInputWidget()
        qtbot.addWidget(widget)

        signal_spy = Mock()
        widget.timeLimitChanged.connect(signal_spy)

        widget.set_time_limit(3000)

        signal_spy.assert_called_once_with(3000)

    def test_set_memory_limit_emits_signal(self, qtbot):
        """set_memory_limit should trigger memoryLimitChanged signal."""
        widget = LimitsInputWidget()
        qtbot.addWidget(widget)

        signal_spy = Mock()
        widget.memoryLimitChanged.connect(signal_spy)

        widget.set_memory_limit(1024)

        signal_spy.assert_called_once_with(1024)
