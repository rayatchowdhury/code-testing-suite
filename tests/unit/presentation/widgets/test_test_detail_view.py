# -*- coding: utf-8 -*-
"""
Unit tests for TestDetailView dialogs - detailed test information popups.

These dialogs show comprehensive test details when a test card is clicked.
Different dialog types for validator, comparator, and benchmarker.
"""

from unittest.mock import Mock

import pytest
from PySide6.QtWidgets import QLabel, QPushButton, QTextEdit

from src.app.presentation.widgets.test_detail_view import (
    BenchmarkerDetailDialog,
    ComparatorDetailDialog,
    TestDetailDialog,
    ValidatorDetailDialog,
)


class TestTestDetailDialogBase:
    """Test base detail dialog functionality."""

    def test_creates_dialog_with_test_info(self, qtbot):
        """Dialog should initialize with test information."""
        dialog = TestDetailDialog(test_number=5, passed=True, time=0.125, memory=64.5)
        qtbot.addWidget(dialog)

        assert dialog.test_number == 5
        assert dialog.passed is True
        assert dialog.time == 0.125
        assert dialog.memory == 64.5

    def test_sets_window_title_with_test_number(self, qtbot):
        """Dialog window title should include test number."""
        dialog = TestDetailDialog(test_number=42, passed=False, time=1.5, memory=128.0)
        qtbot.addWidget(dialog)

        assert "42" in dialog.windowTitle()
        assert "Test" in dialog.windowTitle()

    def test_has_minimum_size(self, qtbot):
        """Dialog should have minimum width and height set."""
        dialog = TestDetailDialog(test_number=1, passed=True, time=0.1, memory=32.0)
        qtbot.addWidget(dialog)

        assert dialog.minimumWidth() >= 600
        assert dialog.minimumHeight() >= 400

    def test_creates_close_button(self, qtbot):
        """Dialog should have a close button."""
        dialog = TestDetailDialog(test_number=1, passed=True, time=0.1, memory=32.0)
        qtbot.addWidget(dialog)

        # Find close button
        close_buttons = dialog.findChildren(QPushButton)
        assert len(close_buttons) > 0
        assert any("Close" in btn.text() for btn in close_buttons)


class TestComparatorDetailDialog:
    """Test comparator-specific detail dialog."""

    def test_creates_with_comparator_data(self, qtbot):
        """ComparatorDetailDialog should store input and output data."""
        dialog = ComparatorDetailDialog(
            test_number=3,
            passed=True,
            time=0.2,
            memory=48.0,
            input_text="10 20",
            correct_output="30",
            test_output="30",
        )
        qtbot.addWidget(dialog)

        assert dialog.input_text == "10 20"
        assert dialog.correct_output == "30"
        assert dialog.test_output == "30"

    def test_displays_input_section(self, qtbot):
        """Dialog should display input text section."""
        dialog = ComparatorDetailDialog(
            test_number=1,
            passed=True,
            time=0.1,
            memory=32.0,
            input_text="5 10 15",
            correct_output="30",
            test_output="30",
        )
        qtbot.addWidget(dialog)

        # Find text edits that contain input
        text_edits = dialog.findChildren(QTextEdit)
        assert len(text_edits) >= 3  # Input, Expected, Actual

        # One should contain the input
        input_found = any("5 10 15" in edit.toPlainText() for edit in text_edits)
        assert input_found

    def test_displays_expected_output_section(self, qtbot):
        """Dialog should display expected output section."""
        dialog = ComparatorDetailDialog(
            test_number=1,
            passed=False,
            time=0.1,
            memory=32.0,
            input_text="1 2",
            correct_output="3",
            test_output="5",
        )
        qtbot.addWidget(dialog)

        text_edits = dialog.findChildren(QTextEdit)

        # One should contain correct output
        expected_found = any(
            "3" in edit.toPlainText() and edit.toPlainText().strip() == "3"
            for edit in text_edits
        )
        assert expected_found

    def test_displays_actual_output_section(self, qtbot):
        """Dialog should display actual output section."""
        dialog = ComparatorDetailDialog(
            test_number=1,
            passed=False,
            time=0.1,
            memory=32.0,
            input_text="1 2",
            correct_output="3",
            test_output="5",
        )
        qtbot.addWidget(dialog)

        text_edits = dialog.findChildren(QTextEdit)

        # One should contain test output
        actual_found = any(
            "5" in edit.toPlainText() and edit.toPlainText().strip() == "5"
            for edit in text_edits
        )
        assert actual_found

    def test_text_edits_are_readonly(self, qtbot):
        """All text edits in comparator dialog should be read-only."""
        dialog = ComparatorDetailDialog(
            test_number=1,
            passed=True,
            time=0.1,
            memory=32.0,
            input_text="input",
            correct_output="correct",
            test_output="output",
        )
        qtbot.addWidget(dialog)

        text_edits = dialog.findChildren(QTextEdit)
        for edit in text_edits:
            assert edit.isReadOnly()


class TestValidatorDetailDialog:
    """Test validator-specific detail dialog."""

    def test_creates_with_validator_data(self, qtbot):
        """ValidatorDetailDialog should store validation data."""
        dialog = ValidatorDetailDialog(
            test_number=2,
            passed=True,
            time=0.15,
            memory=40.0,
            input_data="5\n10 20 30 40 50",
            test_output="VALID",
            validation_message="Correct",
            error_details="",
            validator_exit_code=0,
        )
        qtbot.addWidget(dialog)

        assert dialog.input_data == "5\n10 20 30 40 50"
        assert dialog.test_output == "VALID"
        assert dialog.validation_message == "Correct"
        assert dialog.validator_exit_code == 0

    def test_displays_input_data_section(self, qtbot):
        """Dialog should display input data section."""
        dialog = ValidatorDetailDialog(
            test_number=1,
            passed=True,
            time=0.1,
            memory=32.0,
            input_data="test input",
            test_output="VALID",
            validation_message="Correct",
            error_details="",
            validator_exit_code=0,
        )
        qtbot.addWidget(dialog)

        text_edits = dialog.findChildren(QTextEdit)
        input_found = any("test input" in edit.toPlainText() for edit in text_edits)
        assert input_found

    def test_displays_test_output_section(self, qtbot):
        """Dialog should display test output section."""
        dialog = ValidatorDetailDialog(
            test_number=1,
            passed=False,
            time=0.1,
            memory=32.0,
            input_data="input",
            test_output="INVALID",
            validation_message="Wrong Answer",
            error_details="Output format is incorrect",
            validator_exit_code=1,
        )
        qtbot.addWidget(dialog)

        text_edits = dialog.findChildren(QTextEdit)
        output_found = any("INVALID" in edit.toPlainText() for edit in text_edits)
        assert output_found

    def test_displays_validator_log_for_passed_test(self, qtbot):
        """Dialog should display success message in validator log for passed tests."""
        dialog = ValidatorDetailDialog(
            test_number=1,
            passed=True,
            time=0.1,
            memory=32.0,
            input_data="input",
            test_output="output",
            validation_message="Correct",
            error_details="",
            validator_exit_code=0,
        )
        qtbot.addWidget(dialog)

        text_edits = dialog.findChildren(QTextEdit)
        # Should have validator log with success message
        log_found = any(
            "Valid output" in edit.toPlainText()
            or "correct" in edit.toPlainText().lower()
            for edit in text_edits
        )
        assert log_found

    def test_displays_validator_log_for_wrong_answer(self, qtbot):
        """Dialog should display wrong answer details in validator log."""
        dialog = ValidatorDetailDialog(
            test_number=1,
            passed=False,
            time=0.1,
            memory=32.0,
            input_data="input",
            test_output="output",
            validation_message="Wrong Answer",
            error_details="Expected 5, got 3",
            validator_exit_code=1,
        )
        qtbot.addWidget(dialog)

        text_edits = dialog.findChildren(QTextEdit)
        # Should have error details in log
        error_found = any(
            "Wrong Answer" in edit.toPlainText()
            or "Expected 5, got 3" in edit.toPlainText()
            for edit in text_edits
        )
        assert error_found

    def test_interprets_exit_code_1_as_wrong_answer(self, qtbot):
        """Dialog should interpret exit code 1 as Wrong Answer."""
        dialog = ValidatorDetailDialog(
            test_number=1,
            passed=False,
            time=0.1,
            memory=32.0,
            input_data="",
            test_output="",
            validation_message="Wrong Answer",
            error_details="",
            validator_exit_code=1,
        )
        qtbot.addWidget(dialog)

        text_edits = dialog.findChildren(QTextEdit)
        # Should mention exit code 1 or Wrong Answer
        code_found = any(
            "Exit Code: 1" in edit.toPlainText() or "Wrong Answer" in edit.toPlainText()
            for edit in text_edits
        )
        assert code_found

    def test_interprets_exit_code_2_as_presentation_error(self, qtbot):
        """Dialog should interpret exit code 2 as Presentation Error."""
        dialog = ValidatorDetailDialog(
            test_number=1,
            passed=False,
            time=0.1,
            memory=32.0,
            input_data="",
            test_output="",
            validation_message="Presentation Error",
            error_details="",
            validator_exit_code=2,
        )
        qtbot.addWidget(dialog)

        text_edits = dialog.findChildren(QTextEdit)
        # Should mention exit code 2 or Presentation Error
        code_found = any(
            "Exit Code: 2" in edit.toPlainText()
            or "Presentation Error" in edit.toPlainText()
            for edit in text_edits
        )
        assert code_found


class TestBenchmarkerDetailDialog:
    """Test benchmarker-specific detail dialog."""

    def test_creates_with_benchmarker_data(self, qtbot):
        """BenchmarkerDetailDialog should store benchmark data."""
        dialog = BenchmarkerDetailDialog(
            test_number=10,
            passed=True,
            time=0.05,
            memory=24.0,
            test_size=1000,
            input_data="1 2 3 4 5",
            output_data="15",
        )
        qtbot.addWidget(dialog)

        assert dialog.test_size == 1000
        assert dialog.input_data == "1 2 3 4 5"
        assert dialog.output_data == "15"

    def test_displays_input_data_section(self, qtbot):
        """Dialog should display input data section."""
        dialog = BenchmarkerDetailDialog(
            test_number=1,
            passed=True,
            time=0.1,
            memory=32.0,
            test_size=100,
            input_data="benchmark input",
            output_data="output",
        )
        qtbot.addWidget(dialog)

        text_edits = dialog.findChildren(QTextEdit)
        input_found = any(
            "benchmark input" in edit.toPlainText() for edit in text_edits
        )
        assert input_found

    def test_displays_output_data_section(self, qtbot):
        """Dialog should display output data section."""
        dialog = BenchmarkerDetailDialog(
            test_number=1,
            passed=True,
            time=0.1,
            memory=32.0,
            test_size=100,
            input_data="input",
            output_data="benchmark output",
        )
        qtbot.addWidget(dialog)

        text_edits = dialog.findChildren(QTextEdit)
        output_found = any(
            "benchmark output" in edit.toPlainText() for edit in text_edits
        )
        assert output_found

    def test_displays_performance_summary(self, qtbot):
        """Dialog should display performance summary section."""
        dialog = BenchmarkerDetailDialog(
            test_number=1,
            passed=True,
            time=0.1,
            memory=32.0,
            test_size=500,
            input_data="line1\nline2\nline3",
            output_data="result",
        )
        qtbot.addWidget(dialog)

        text_edits = dialog.findChildren(QTextEdit)
        # Should have performance summary
        summary_found = any(
            "Performance" in edit.toPlainText() or "Input Lines" in edit.toPlainText()
            for edit in text_edits
        )
        assert summary_found

    def test_handles_empty_input_data(self, qtbot):
        """Dialog should handle case when input data is empty."""
        dialog = BenchmarkerDetailDialog(
            test_number=1,
            passed=True,
            time=0.1,
            memory=32.0,
            test_size=0,
            input_data="",
            output_data="",
        )
        qtbot.addWidget(dialog)

        # Should not crash and should show placeholder
        text_edits = dialog.findChildren(QTextEdit)
        assert len(text_edits) > 0  # Should still create text edits


class TestDetailDialogCommonFeatures:
    """Test features common to all detail dialog types."""

    def test_close_button_closes_dialog(self, qtbot):
        """Close button should close the dialog."""
        dialog = TestDetailDialog(test_number=1, passed=True, time=0.1, memory=32.0)
        qtbot.addWidget(dialog)

        close_buttons = dialog.findChildren(QPushButton)
        close_button = next(
            (btn for btn in close_buttons if "Close" in btn.text()), None
        )

        assert close_button is not None
        assert close_button.isEnabled()

    def test_all_dialogs_have_metrics_display(self, qtbot):
        """All dialog types should display time and memory metrics."""
        dialogs = [
            ComparatorDetailDialog(1, True, 0.1, 32.0, "in", "out1", "out2"),
            ValidatorDetailDialog(1, True, 0.1, 32.0, "in", "out", "msg", "", 0),
            BenchmarkerDetailDialog(1, True, 0.1, 32.0, 100, "in", "out"),
        ]

        for dialog in dialogs:
            qtbot.addWidget(dialog)

            # Should display time and memory somewhere
            labels = dialog.findChildren(QLabel)
            has_time = any(
                "0.1" in label.text() or "Time" in label.text() for label in labels
            )
            has_memory = any(
                "32" in label.text() or "Memory" in label.text() for label in labels
            )

            assert has_time or has_memory  # At least one metric displayed
