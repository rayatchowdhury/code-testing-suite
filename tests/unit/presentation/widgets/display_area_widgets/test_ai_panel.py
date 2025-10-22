# -*- coding: utf-8 -*-
"""
Unit tests for AIPanel widget - AI code assistance panel core functions.

Tests focus on panel initialization, button creation, signal emission, and enable/disable functionality.
API integration is mocked as it depends on external services.
"""

from unittest.mock import MagicMock, Mock, patch

import pytest
from PySide6.QtWidgets import QLineEdit, QPushButton

from src.app.presentation.shared.components.editor.ai_panel import (
    AIActionButton,
    AICustomCommandInput,
    AIPanel,
)


class TestAIActionButton:
    """Test custom AI action button widget."""

    def test_creates_action_button(self, qtbot):
        """AIActionButton should initialize with text."""
        button = AIActionButton("Test Action")
        qtbot.addWidget(button)

        assert button.text() == "Test Action"

    def test_has_fixed_height(self, qtbot):
        """Button should have fixed height for consistency."""
        button = AIActionButton("Action")
        qtbot.addWidget(button)

        assert button.height() <= 24  # Should have compact height


class TestAICustomCommandInput:
    """Test custom command input widget."""

    def test_creates_input_widget(self, qtbot):
        """Custom command input should have text input field."""
        widget = AICustomCommandInput()
        qtbot.addWidget(widget)

        assert hasattr(widget, "input")
        assert isinstance(widget.input, QLineEdit)

    def test_has_placeholder_text(self, qtbot):
        """Input should have placeholder text."""
        widget = AICustomCommandInput()
        qtbot.addWidget(widget)

        placeholder = widget.input.placeholderText()
        assert len(placeholder) > 0
        assert "command" in placeholder.lower()

    def test_emits_signal_on_submit(self, qtbot):
        """Widget should emit signal when command is submitted."""
        widget = AICustomCommandInput()
        qtbot.addWidget(widget)

        signal_spy = Mock()
        widget.commandSubmitted.connect(signal_spy)

        widget.input.setText("custom command")
        widget._handle_submit()

        signal_spy.assert_called_once_with("custom command")

    def test_clears_input_after_submit(self, qtbot):
        """Input should be cleared after submission."""
        widget = AICustomCommandInput()
        qtbot.addWidget(widget)

        widget.input.setText("command")
        widget._handle_submit()

        assert widget.input.text() == ""

    def test_ignores_empty_command(self, qtbot):
        """Widget should not emit signal for empty commands."""
        widget = AICustomCommandInput()
        qtbot.addWidget(widget)

        signal_spy = Mock()
        widget.commandSubmitted.connect(signal_spy)

        widget.input.setText("   ")  # Whitespace only
        widget._handle_submit()

        signal_spy.assert_not_called()


@patch(
    "src.app.presentation.shared.components.console.ai_panel.AIPanel._should_show_ai_panel"
)
class TestAIPanelInitialization:
    """Test AI panel initialization."""

    def test_creates_panel_with_editor_type(self, mock_show, qtbot):
        """Panel should initialize with editor type."""
        mock_show.return_value = True

        panel = AIPanel(panel_type="editor")
        qtbot.addWidget(panel)

        assert panel.panel_type == "editor"

    def test_creates_panel_with_other_type(self, mock_show, qtbot):
        """Panel should initialize with other panel types."""
        mock_show.return_value = True

        panel = AIPanel(panel_type="generator")
        qtbot.addWidget(panel)

        assert panel.panel_type == "generator"

    def test_creates_action_buttons(self, mock_show, qtbot):
        """Panel should create action buttons."""
        mock_show.return_value = True

        panel = AIPanel()
        qtbot.addWidget(panel)

        assert hasattr(panel, "action_buttons")
        assert isinstance(panel.action_buttons, dict)

    def test_creates_custom_command_input(self, mock_show, qtbot):
        """Panel should create custom command input."""
        mock_show.return_value = True

        panel = AIPanel()
        qtbot.addWidget(panel)

        assert hasattr(panel, "custom_command")
        assert isinstance(panel.custom_command, AICustomCommandInput)


@patch(
    "src.app.presentation.shared.components.console.ai_panel.AIPanel._should_show_ai_panel"
)
class TestAIPanelButtons:
    """Test AI panel button creation and configuration."""

    def test_has_analysis_button(self, mock_show, qtbot):
        """Panel should have analysis button."""
        mock_show.return_value = True

        panel = AIPanel()
        qtbot.addWidget(panel)

        assert "analysis" in panel.action_buttons

    def test_has_issues_button(self, mock_show, qtbot):
        """Panel should have issues button."""
        mock_show.return_value = True

        panel = AIPanel()
        qtbot.addWidget(panel)

        assert "issues" in panel.action_buttons

    def test_has_tips_button(self, mock_show, qtbot):
        """Panel should have tips button."""
        mock_show.return_value = True

        panel = AIPanel()
        qtbot.addWidget(panel)

        assert "tips" in panel.action_buttons

    def test_editor_panel_has_document_button(self, mock_show, qtbot):
        """Editor panel should have document button."""
        mock_show.return_value = True

        panel = AIPanel(panel_type="editor")
        qtbot.addWidget(panel)

        assert "document" in panel.action_buttons

    def test_other_panel_has_generate_button(self, mock_show, qtbot):
        """Non-editor panel should have generate button."""
        mock_show.return_value = True

        panel = AIPanel(panel_type="generator")
        qtbot.addWidget(panel)

        assert "generate" in panel.action_buttons


@patch(
    "src.app.presentation.shared.components.console.ai_panel.AIPanel._should_show_ai_panel"
)
class TestAIPanelSignals:
    """Test AI panel signal emission."""

    def test_emits_analysis_requested_signal(self, mock_show, qtbot):
        """Panel should emit analysisRequested signal."""
        mock_show.return_value = True

        panel = AIPanel()
        qtbot.addWidget(panel)

        signal_spy = Mock()
        panel.analysisRequested.connect(signal_spy)

        # Simulate button click
        panel._emit_with_current_code(panel.analysisRequested)

        signal_spy.assert_called_once()

    def test_emits_issues_requested_signal(self, mock_show, qtbot):
        """Panel should emit issuesRequested signal."""
        mock_show.return_value = True

        panel = AIPanel()
        qtbot.addWidget(panel)

        signal_spy = Mock()
        panel.issuesRequested.connect(signal_spy)

        panel._emit_with_current_code(panel.issuesRequested)

        signal_spy.assert_called_once()

    def test_emits_tips_requested_signal(self, mock_show, qtbot):
        """Panel should emit tipsRequested signal."""
        mock_show.return_value = True

        panel = AIPanel()
        qtbot.addWidget(panel)

        signal_spy = Mock()
        panel.tipsRequested.connect(signal_spy)

        panel._emit_with_current_code(panel.tipsRequested)

        signal_spy.assert_called_once()

    def test_emits_custom_command_with_text(self, mock_show, qtbot):
        """Panel should emit customCommandRequested with command text."""
        mock_show.return_value = True

        panel = AIPanel()
        qtbot.addWidget(panel)

        signal_spy = Mock()
        panel.customCommandRequested.connect(signal_spy)

        panel._emit_custom_command_with_current_code("test command")

        signal_spy.assert_called_once()
        args = signal_spy.call_args[0]
        assert args[0] == "test command"


@patch(
    "src.app.presentation.shared.components.console.ai_panel.AIPanel._should_show_ai_panel"
)
class TestAIPanelEnableDisable:
    """Test enabling and disabling AI panel."""

    def test_disables_all_buttons(self, mock_show, qtbot):
        """set_enabled(False) should disable all action buttons."""
        mock_show.return_value = True

        panel = AIPanel()
        qtbot.addWidget(panel)

        panel.set_enabled(False)

        for btn in panel.action_buttons.values():
            assert btn.isEnabled() is False

    def test_enables_all_buttons(self, mock_show, qtbot):
        """set_enabled(True) should enable all action buttons."""
        mock_show.return_value = True

        panel = AIPanel()
        qtbot.addWidget(panel)

        panel.set_enabled(False)  # First disable
        panel.set_enabled(True)  # Then enable

        for btn in panel.action_buttons.values():
            assert btn.isEnabled() is True

    def test_disables_custom_command_input(self, mock_show, qtbot):
        """set_enabled(False) should disable custom command input."""
        mock_show.return_value = True

        panel = AIPanel()
        qtbot.addWidget(panel)

        panel.set_enabled(False)

        assert panel.custom_command.input.isEnabled() is False

    def test_enables_custom_command_input(self, mock_show, qtbot):
        """set_enabled(True) should enable custom command input."""
        mock_show.return_value = True

        panel = AIPanel()
        qtbot.addWidget(panel)

        panel.set_enabled(False)
        panel.set_enabled(True)

        assert panel.custom_command.input.isEnabled() is True


@patch(
    "src.app.presentation.shared.components.console.ai_panel.AIPanel._should_show_ai_panel"
)
class TestAIPanelTypeChange:
    """Test changing panel type."""

    def test_changes_panel_type(self, mock_show, qtbot):
        """set_panel_type should update panel type."""
        mock_show.return_value = True

        panel = AIPanel(panel_type="editor")
        qtbot.addWidget(panel)

        panel.set_panel_type("generator")

        assert panel.panel_type == "generator"

    def test_recreates_ui_on_type_change(self, mock_show, qtbot):
        """Changing panel type should recreate UI with new buttons."""
        mock_show.return_value = True

        panel = AIPanel(panel_type="editor")
        qtbot.addWidget(panel)

        # Editor should have document button
        assert "document" in panel.action_buttons

        # Change to generator type
        panel.set_panel_type("generator")

        # Should now have generate button
        assert "generate" in panel.action_buttons
