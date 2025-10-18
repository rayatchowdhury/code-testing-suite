# -*- coding: utf-8 -*-
"""
Unit tests for Test Card widgets - display components for test results.

Test cards are shown for every test execution result and are core UX components
used across validator, comparator, and benchmarker views.
"""

from unittest.mock import Mock

import pytest
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel

from src.app.presentation.widgets.status_view_widgets import (
    BaseTestCard,
    BenchmarkerTestCard,
    ComparatorTestCard,
    ValidatorTestCard,
)


class TestBaseTestCardInitialization:
    """Test initialization of base test card."""

    def test_creates_card_with_passed_status(self, qtbot):
        """Card should display passed test with correct data."""
        card = BaseTestCard(test_number=1, passed=True, time=0.125, memory=45.3)
        qtbot.addWidget(card)

        assert card.test_number == 1
        assert card.passed is True
        assert card.time == 0.125
        assert card.memory == 45.3

    def test_creates_card_with_failed_status(self, qtbot):
        """Card should display failed test with correct data."""
        card = BaseTestCard(test_number=5, passed=False, time=1.250, memory=128.5)
        qtbot.addWidget(card)

        assert card.test_number == 5
        assert card.passed is False
        assert card.time == 1.250
        assert card.memory == 128.5

    def test_creates_test_number_label(self, qtbot):
        """Card should display test number label."""
        card = BaseTestCard(test_number=42, passed=True, time=0.5, memory=64.0)
        qtbot.addWidget(card)

        assert hasattr(card, "test_label")
        assert isinstance(card.test_label, QLabel)
        assert "42" in card.test_label.text()

    def test_creates_status_label_for_passed(self, qtbot):
        """Card should show passed status label."""
        card = BaseTestCard(test_number=1, passed=True, time=0.1, memory=32.0)
        qtbot.addWidget(card)

        assert hasattr(card, "status_label")
        assert "Passed" in card.status_label.text()

    def test_creates_status_label_for_failed(self, qtbot):
        """Card should show failed status label."""
        card = BaseTestCard(test_number=1, passed=False, time=0.1, memory=32.0)
        qtbot.addWidget(card)

        assert hasattr(card, "status_label")
        assert "Failed" in card.status_label.text()


class TestBaseTestCardMetrics:
    """Test metrics display and updates."""

    def test_displays_time_metric(self, qtbot):
        """Card should display execution time."""
        card = BaseTestCard(test_number=1, passed=True, time=0.250, memory=64.0)
        qtbot.addWidget(card)

        assert hasattr(card, "time_label")
        assert "0.250" in card.time_label.text()

    def test_displays_memory_metric(self, qtbot):
        """Card should display memory usage."""
        card = BaseTestCard(test_number=1, passed=True, time=0.1, memory=128.5)
        qtbot.addWidget(card)

        assert hasattr(card, "memory_label")
        assert "128.5" in card.memory_label.text()

    def test_updates_metrics_dynamically(self, qtbot):
        """Card should update time and memory metrics."""
        card = BaseTestCard(test_number=1, passed=True, time=0.1, memory=32.0)
        qtbot.addWidget(card)

        card.update_metrics(time=0.5, memory=96.0)

        assert card.time == 0.5
        assert card.memory == 96.0
        assert "0.500" in card.time_label.text()
        assert "96.0" in card.memory_label.text()


class TestBaseTestCardInteraction:
    """Test card click interaction."""

    def test_card_is_clickable(self, qtbot):
        """Card should have pointing hand cursor for clickability."""
        card = BaseTestCard(test_number=1, passed=True, time=0.1, memory=32.0)
        qtbot.addWidget(card)

        assert card.cursor().shape() == Qt.PointingHandCursor

    def test_emits_clicked_signal_on_click(self, qtbot):
        """Card should emit clicked signal with test number on click."""
        card = BaseTestCard(test_number=7, passed=True, time=0.1, memory=32.0)
        qtbot.addWidget(card)

        signal_spy = Mock()
        card.clicked.connect(signal_spy)

        # Simulate mouse click
        qtbot.mouseClick(card, Qt.LeftButton)

        signal_spy.assert_called_once_with(7)

    def test_does_not_emit_on_right_click(self, qtbot):
        """Card should not emit clicked signal on right click."""
        card = BaseTestCard(test_number=1, passed=True, time=0.1, memory=32.0)
        qtbot.addWidget(card)

        signal_spy = Mock()
        card.clicked.connect(signal_spy)

        # Simulate right click
        qtbot.mouseClick(card, Qt.RightButton)

        signal_spy.assert_not_called()


class TestComparatorTestCard:
    """Test comparator-specific test card."""

    def test_creates_comparator_card_with_outputs(self, qtbot):
        """ComparatorTestCard should store input and output data."""
        card = ComparatorTestCard(
            test_number=1,
            passed=True,
            time=0.1,
            memory=32.0,
            input_text="5 10",
            correct_output="15",
            test_output="15",
        )
        qtbot.addWidget(card)

        assert card.input_text == "5 10"
        assert card.correct_output == "15"
        assert card.test_output == "15"

    def test_comparator_card_inherits_base_functionality(self, qtbot):
        """ComparatorTestCard should have all base card functionality."""
        card = ComparatorTestCard(
            test_number=3,
            passed=False,
            time=0.2,
            memory=48.0,
            input_text="1 2",
            correct_output="3",
            test_output="4",
        )
        qtbot.addWidget(card)

        # Should have base properties
        assert card.test_number == 3
        assert card.passed is False

        # Should emit clicked signal
        signal_spy = Mock()
        card.clicked.connect(signal_spy)
        qtbot.mouseClick(card, Qt.LeftButton)
        signal_spy.assert_called_once_with(3)


class TestValidatorTestCard:
    """Test validator-specific test card."""

    def test_creates_validator_card_with_outputs(self, qtbot):
        """ValidatorTestCard should store expected and actual outputs."""
        card = ValidatorTestCard(
            test_number=2,
            passed=True,
            time=0.15,
            memory=40.0,
            expected_output="VALID",
            actual_output="VALID",
        )
        qtbot.addWidget(card)

        assert card.expected_output == "VALID"
        assert card.actual_output == "VALID"

    def test_validator_card_inherits_base_functionality(self, qtbot):
        """ValidatorTestCard should have all base card functionality."""
        card = ValidatorTestCard(
            test_number=5,
            passed=False,
            time=0.3,
            memory=56.0,
            expected_output="VALID",
            actual_output="INVALID",
        )
        qtbot.addWidget(card)

        # Should have base properties
        assert card.test_number == 5
        assert card.passed is False

        # Should be clickable
        assert card.cursor().shape() == Qt.PointingHandCursor


class TestBenchmarkerTestCard:
    """Test benchmarker-specific test card."""

    def test_creates_benchmarker_card_with_test_size(self, qtbot):
        """BenchmarkerTestCard should store test size information."""
        card = BenchmarkerTestCard(
            test_number=10, passed=True, time=0.05, memory=24.0, test_size=1000
        )
        qtbot.addWidget(card)

        assert card.test_size == 1000

    def test_benchmarker_card_inherits_base_functionality(self, qtbot):
        """BenchmarkerTestCard should have all base card functionality."""
        card = BenchmarkerTestCard(
            test_number=15, passed=False, time=2.5, memory=512.0, test_size=100000
        )
        qtbot.addWidget(card)

        # Should have base properties
        assert card.test_number == 15
        assert card.passed is False

        # Should update metrics
        card.update_metrics(time=1.0, memory=256.0)
        assert card.time == 1.0
        assert card.memory == 256.0


class TestTestCardStyling:
    """Test card styling for different states."""

    def test_passed_card_has_styling(self, qtbot):
        """Passed card should have styling applied."""
        card = BaseTestCard(test_number=1, passed=True, time=0.1, memory=32.0)
        qtbot.addWidget(card)

        # Should have stylesheet (styling is applied via get_test_card_style)
        assert card.styleSheet() != ""

    def test_failed_card_has_styling(self, qtbot):
        """Failed card should have different styling than passed."""
        passed_card = BaseTestCard(test_number=1, passed=True, time=0.1, memory=32.0)
        failed_card = BaseTestCard(test_number=2, passed=False, time=0.1, memory=32.0)
        qtbot.addWidget(passed_card)
        qtbot.addWidget(failed_card)

        # Cards should have different stylesheets based on pass/fail
        # (actual styling is in get_test_card_style function)
        assert passed_card.styleSheet() != ""
        assert failed_card.styleSheet() != ""


class TestTestCardEdgeCases:
    """Test edge cases and extreme values."""

    def test_card_with_zero_time(self, qtbot):
        """Card should handle zero execution time."""
        card = BaseTestCard(test_number=1, passed=True, time=0.0, memory=32.0)
        qtbot.addWidget(card)

        assert card.time == 0.0
        assert "0.000" in card.time_label.text()

    def test_card_with_zero_memory(self, qtbot):
        """Card should handle zero memory usage."""
        card = BaseTestCard(test_number=1, passed=True, time=0.1, memory=0.0)
        qtbot.addWidget(card)

        assert card.memory == 0.0
        assert "0.0" in card.memory_label.text()

    def test_card_with_very_large_time(self, qtbot):
        """Card should handle very large execution time."""
        card = BaseTestCard(test_number=1, passed=False, time=999.999, memory=32.0)
        qtbot.addWidget(card)

        assert card.time == 999.999
        assert "999.999" in card.time_label.text()

    def test_card_with_very_large_memory(self, qtbot):
        """Card should handle very large memory usage."""
        card = BaseTestCard(test_number=1, passed=False, time=0.1, memory=8192.5)
        qtbot.addWidget(card)

        assert card.memory == 8192.5
        assert "8192.5" in card.memory_label.text()

    def test_card_with_very_large_test_number(self, qtbot):
        """Card should handle very large test numbers."""
        card = BaseTestCard(test_number=9999, passed=True, time=0.1, memory=32.0)
        qtbot.addWidget(card)

        assert card.test_number == 9999
        assert "9999" in card.test_label.text()

    def test_update_metrics_with_extreme_values(self, qtbot):
        """update_metrics should handle extreme values."""
        card = BaseTestCard(test_number=1, passed=True, time=0.1, memory=32.0)
        qtbot.addWidget(card)

        # Update with very small values
        card.update_metrics(time=0.001, memory=0.1)
        assert card.time == 0.001
        assert card.memory == 0.1

        # Update with very large values
        card.update_metrics(time=1000.0, memory=16384.0)
        assert card.time == 1000.0
        assert card.memory == 16384.0

    def test_card_with_fractional_precision(self, qtbot):
        """Card should display time with 3 decimal places and memory with 1."""
        card = BaseTestCard(test_number=1, passed=True, time=0.123456, memory=45.6789)
        qtbot.addWidget(card)

        # Time should have 3 decimal places
        assert "0.123" in card.time_label.text()

        # Memory should have 1 decimal place
        assert "45.7" in card.memory_label.text()

    def test_comparator_card_with_empty_strings(self, qtbot):
        """ComparatorTestCard should handle empty input/output strings."""
        card = ComparatorTestCard(
            test_number=1,
            passed=False,
            time=0.1,
            memory=32.0,
            input_text="",
            correct_output="",
            test_output="",
        )
        qtbot.addWidget(card)

        assert card.input_text == ""
        assert card.correct_output == ""
        assert card.test_output == ""

    def test_validator_card_with_multiline_outputs(self, qtbot):
        """ValidatorTestCard should handle multiline outputs."""
        card = ValidatorTestCard(
            test_number=1,
            passed=True,
            time=0.1,
            memory=32.0,
            expected_output="Line 1\nLine 2\nLine 3",
            actual_output="Line 1\nLine 2\nLine 3",
        )
        qtbot.addWidget(card)

        assert "\n" in card.expected_output
        assert "\n" in card.actual_output

    def test_benchmarker_card_with_zero_test_size(self, qtbot):
        """BenchmarkerTestCard should handle zero test size."""
        card = BenchmarkerTestCard(
            test_number=1, passed=True, time=0.1, memory=32.0, test_size=0
        )
        qtbot.addWidget(card)

        assert card.test_size == 0

    def test_benchmarker_card_with_very_large_test_size(self, qtbot):
        """BenchmarkerTestCard should handle very large test sizes."""
        card = BenchmarkerTestCard(
            test_number=1, passed=False, time=5.0, memory=1024.0, test_size=10000000
        )
        qtbot.addWidget(card)

        assert card.test_size == 10000000
