# -*- coding: utf-8 -*-
"""
Unit tests for Console widget - output display core functions.

Tests focus on core functionality: output display, formatting, clearing, and ANSI color handling.
Full widget integration is tested elsewhere.
"""

from unittest.mock import Mock, patch

import pytest
from PySide6.QtGui import QColor, QTextCursor
from PySide6.QtWidgets import QPlainTextEdit

from src.app.presentation.widgets.display_area_widgets.console import ConsoleOutput


class TestConsoleInitialization:
    """Test console widget initialization."""

    def test_creates_console_widget(self, qtbot):
        """Console should initialize with output and input areas."""
        console = ConsoleOutput()
        qtbot.addWidget(console)

        assert hasattr(console, "output")
        assert hasattr(console, "input")
        assert isinstance(console.output, QPlainTextEdit)
        assert isinstance(console.input, QPlainTextEdit)

    def test_output_is_readonly(self, qtbot):
        """Output area should be read-only."""
        console = ConsoleOutput()
        qtbot.addWidget(console)

        assert console.output.isReadOnly() is True

    def test_input_is_editable(self, qtbot):
        """Input area should be editable."""
        console = ConsoleOutput()
        qtbot.addWidget(console)

        assert console.input.isReadOnly() is False

    def test_has_compile_run_button(self, qtbot):
        """Console should have compile & run button."""
        console = ConsoleOutput()
        qtbot.addWidget(console)

        assert hasattr(console, "compile_run_btn")
        assert (
            "Compile" in console.compile_run_btn.text() or "Run" in console.compile_run_btn.text()
        )


class TestConsoleOutputDisplay:
    """Test output display functionality."""

    def test_displays_text_output(self, qtbot):
        """Console should display text in output area."""
        console = ConsoleOutput()
        qtbot.addWidget(console)

        console.displayOutput("Hello, World!")

        # Flush buffer to ensure text is displayed
        console.flush_buffer()

        output_text = console.output.toPlainText()
        assert "Hello, World!" in output_text

    def test_displays_multiple_lines(self, qtbot):
        """Console should display multiple lines of output."""
        console = ConsoleOutput()
        qtbot.addWidget(console)

        console.displayOutput("Line 1")
        console.displayOutput("Line 2")
        console.displayOutput("Line 3")
        console.flush_buffer()

        output_text = console.output.toPlainText()
        assert "Line 1" in output_text
        assert "Line 2" in output_text
        assert "Line 3" in output_text

    def test_handles_empty_output(self, qtbot):
        """Console should handle empty output gracefully."""
        console = ConsoleOutput()
        qtbot.addWidget(console)

        initial_text = console.output.toPlainText()
        console.displayOutput("")
        console.flush_buffer()

        # Should not crash and text should be unchanged
        assert console.output.toPlainText() == initial_text


class TestConsoleFormatting:
    """Test text formatting with color codes."""

    def test_has_text_formats(self, qtbot):
        """Console should have text format definitions."""
        console = ConsoleOutput()
        qtbot.addWidget(console)

        assert hasattr(console, "formats")
        assert "default" in console.formats

    def test_displays_formatted_text(self, qtbot):
        """Console should display text with formatting."""
        console = ConsoleOutput()
        qtbot.addWidget(console)

        console.displayOutput("Normal text", "default")
        console.flush_buffer()

        output_text = console.output.toPlainText()
        assert "Normal text" in output_text

    def test_uses_fallback_for_unknown_format(self, qtbot):
        """Console should use fallback format for unknown format types."""
        console = ConsoleOutput()
        qtbot.addWidget(console)

        # Should not crash with unknown format
        console.displayOutput("Unknown format", "nonexistent_format")
        console.flush_buffer()

        output_text = console.output.toPlainText()
        assert "Unknown format" in output_text


class TestConsoleClear:
    """Test console clearing functionality."""

    def test_clears_output_area(self, qtbot):
        """clear() should remove all text from output area."""
        console = ConsoleOutput()
        qtbot.addWidget(console)

        console.displayOutput("Some output")
        console.flush_buffer()
        assert len(console.output.toPlainText()) > 0

        console.clear()

        assert console.output.toPlainText() == ""

    def test_clears_input_area(self, qtbot):
        """clear() should remove all text from input area."""
        console = ConsoleOutput()
        qtbot.addWidget(console)

        console.input.setPlainText("Some input")
        assert len(console.input.toPlainText()) > 0

        console.clear()

        assert console.input.toPlainText() == ""

    def test_clears_text_buffer(self, qtbot):
        """clear() should clear pending text buffer."""
        console = ConsoleOutput()
        qtbot.addWidget(console)

        # Add text to buffer without flushing
        console.append_formatted("Buffered text", "default")
        assert len(console.text_buffer) > 0

        console.clear()

        assert len(console.text_buffer) == 0


class TestConsoleInputHandling:
    """Test input handling and submission."""

    def test_emits_input_submitted_signal(self, qtbot):
        """Console should emit signal when input is submitted."""
        console = ConsoleOutput()
        qtbot.addWidget(console)

        signal_spy = Mock()
        console.inputSubmitted.connect(signal_spy)

        # Simulate user entering text and pressing Enter
        console.input.setPlainText("test input\n")
        console._handle_text_change()

        signal_spy.assert_called_once()
        args = signal_spy.call_args[0]
        assert "test input" in args[0]

    def test_request_input_sets_placeholder(self, qtbot):
        """requestInput() should set placeholder text."""
        console = ConsoleOutput()
        qtbot.addWidget(console)

        console.requestInput()

        placeholder = console.input.placeholderText()
        assert "waiting" in placeholder.lower() or "input" in placeholder.lower()

    def test_request_input_clears_input_field(self, qtbot):
        """requestInput() should clear input field."""
        console = ConsoleOutput()
        qtbot.addWidget(console)

        console.input.setPlainText("old text")
        console.requestInput()

        assert console.input.toPlainText() == ""


class TestConsoleBuffering:
    """Test text buffering for performance."""

    def test_buffers_text_before_display(self, qtbot):
        """Console should buffer text for batch processing."""
        console = ConsoleOutput()
        qtbot.addWidget(console)

        console.append_formatted("Buffered text", "default")

        # Text should be in buffer
        assert len(console.text_buffer) > 0
        assert console.text_buffer[0][0] == "Buffered text"

    def test_flush_buffer_displays_text(self, qtbot):
        """flush_buffer() should display buffered text."""
        console = ConsoleOutput()
        qtbot.addWidget(console)

        console.append_formatted("Test output", "default")
        assert len(console.text_buffer) > 0

        console.flush_buffer()

        output_text = console.output.toPlainText()
        assert "Test output" in output_text

    def test_flush_buffer_processes_batches(self, qtbot):
        """flush_buffer() should process text in batches."""
        console = ConsoleOutput()
        qtbot.addWidget(console)

        # Add many items to buffer
        for i in range(15):
            console.append_formatted(f"Line {i}", "default")

        assert len(console.text_buffer) == 15

        # Flush once - should process up to 10 items
        console.flush_buffer()

        # Should have remaining items
        assert len(console.text_buffer) <= 5
