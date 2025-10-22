# -*- coding: utf-8 -*-
"""
Unit tests for BaseWindow (SidebarWindowBase) - foundation window class.

Tests focus on initialization, sidebar setup, splitter configuration, navigation,
and cleanup functionality.
"""

from unittest.mock import MagicMock, Mock, patch

import pytest
from PySide6.QtCore import Signal
from PySide6.QtWidgets import QPushButton, QSplitter, QWidget

from src.app.presentation.base.window import SidebarWindowBase


class TestBaseWindowInitialization:
    """Test base window initialization."""

    def test_creates_base_window(self, qtbot):
        """BaseWindow should initialize without title."""
        window = SidebarWindowBase()
        qtbot.addWidget(window)

        assert window is not None
        assert isinstance(window, QWidget)

    def test_creates_splitter(self, qtbot):
        """BaseWindow should create splitter for layout."""
        window = SidebarWindowBase()
        qtbot.addWidget(window)

        assert hasattr(window, "splitter")
        assert isinstance(window.splitter, QSplitter)

    def test_has_no_unsaved_changes_initially(self, qtbot):
        """BaseWindow should have no unsaved changes initially."""
        window = SidebarWindowBase()
        qtbot.addWidget(window)

        assert window.has_unsaved_changes is False

    def test_can_close_when_no_unsaved_changes(self, qtbot):
        """can_close() should return True when no unsaved changes."""
        window = SidebarWindowBase()
        qtbot.addWidget(window)

        assert window.can_close() is True

    def test_cannot_close_with_unsaved_changes(self, qtbot):
        """can_close() should return False when there are unsaved changes."""
        window = SidebarWindowBase()
        qtbot.addWidget(window)

        window.has_unsaved_changes = True

        assert window.can_close() is False


class TestBaseWindowFooterButtons:
    """Test footer button creation."""

    def test_creates_footer_buttons(self, qtbot):
        """create_footer_buttons should return back and options buttons."""
        window = SidebarWindowBase()
        qtbot.addWidget(window)

        back_btn, options_btn = window.create_footer_buttons()

        assert isinstance(back_btn, QPushButton)
        assert isinstance(options_btn, QPushButton)
        assert "Back" in back_btn.text()

    def test_back_button_has_correct_text(self, qtbot):
        """Back button should have 'Back' text."""
        window = SidebarWindowBase()
        qtbot.addWidget(window)

        back_btn, _ = window.create_footer_buttons()

        assert back_btn.text() == "Back"

    def test_options_button_has_settings_icon(self, qtbot):
        """Options button should have settings icon."""
        window = SidebarWindowBase()
        qtbot.addWidget(window)

        _, options_btn = window.create_footer_buttons()

        assert "⚙" in options_btn.text()


@patch("src.app.presentation.shared.components.sidebar.Sidebar")
@patch("src.app.presentation.shared.components.layout.DisplayArea")
class TestBaseWindowWithSidebar:
    """Test base window with sidebar initialization."""

    def test_initializes_sidebar_with_title(
        self, mock_display_class, mock_sidebar_class, qtbot
    ):
        """BaseWindow should initialize sidebar when title is provided."""

        # Create a mock sidebar that is also a QWidget
        class MockSidebar(QWidget):
            button_clicked = Signal(str)

            def add_help_button(self):
                pass

            def add_footer_divider(self):
                pass

            def setup_horizontal_footer_buttons(self, btn1, btn2):
                pass

        mock_sidebar = MockSidebar()
        mock_display = QWidget()

        mock_sidebar_class.return_value = mock_sidebar
        mock_display_class.return_value = mock_display

        window = SidebarWindowBase(title="Test Window")
        qtbot.addWidget(window)

        assert hasattr(window, "sidebar")
        assert hasattr(window, "display_area")

        # Verify that Sidebar and DisplayArea were instantiated
        mock_sidebar_class.assert_called_once_with("Test Window")
        mock_display_class.assert_called_once()


@patch("src.app.presentation.shared.components.sidebar.Sidebar")
@patch("src.app.presentation.shared.components.layout.DisplayArea")
class TestBaseWindowSplitter:
    """Test splitter setup and configuration."""

    def test_setup_splitter_adds_widgets(
        self, mock_display_class, mock_sidebar_class, qtbot
    ):
        """setup_splitter should add sidebar and content to splitter."""
        window = SidebarWindowBase()
        qtbot.addWidget(window)

        # Create real widget instances
        sidebar_widget = QWidget()
        display_widget = QWidget()

        window.setup_splitter(sidebar_widget, display_widget)

        # Splitter should have 2 widgets
        assert window.splitter.count() == 2

    def test_sidebar_has_minimum_width(
        self, mock_display_class, mock_sidebar_class, qtbot
    ):
        """Sidebar should have minimum width constraint."""
        window = SidebarWindowBase()
        qtbot.addWidget(window)

        sidebar_widget = QWidget()
        display_widget = QWidget()

        window.setup_splitter(sidebar_widget, display_widget)

        # Check sidebar minimum width
        assert sidebar_widget.minimumWidth() == 250

    def test_content_has_minimum_width(
        self, mock_display_class, mock_sidebar_class, qtbot
    ):
        """Content area should have minimum width constraint."""
        window = SidebarWindowBase()
        qtbot.addWidget(window)

        sidebar_widget = QWidget()
        display_widget = QWidget()

        window.setup_splitter(sidebar_widget, display_widget)

        # Check content minimum width
        assert display_widget.minimumWidth() == 600


class TestBaseWindowNavigation:
    """Test navigation and button handling."""

    def test_handles_back_button_click(self, qtbot):
        """handle_button_click should process back button."""
        # Create mock parent with window_manager as attribute
        mock_parent = QWidget()
        mock_parent.window_manager = Mock()
        mock_parent.window_manager.go_back.return_value = True

        window = SidebarWindowBase(parent=mock_parent)
        qtbot.addWidget(window)

        window.handle_button_click("Back")

        # Should call go_back on window manager
        mock_parent.window_manager.go_back.assert_called_once()

    def test_back_button_shows_main_when_no_history(self, qtbot):
        """Back button should show main window when no history."""
        mock_parent = QWidget()
        mock_parent.window_manager = Mock()
        mock_parent.window_manager.go_back.return_value = False  # No history

        window = SidebarWindowBase(parent=mock_parent)
        qtbot.addWidget(window)

        window.handle_button_click("Back")

        # Should show main window
        mock_parent.window_manager.show_window.assert_called_once_with("main")

    def test_back_button_blocked_by_unsaved_changes(self, qtbot):
        """Back button should be blocked when there are unsaved changes."""
        mock_parent = QWidget()
        mock_parent.window_manager = Mock()

        window = SidebarWindowBase(parent=mock_parent)
        qtbot.addWidget(window)
        window.has_unsaved_changes = True

        window.handle_button_click("Back")

        # Should not call window manager when unsaved changes exist
        mock_parent.window_manager.go_back.assert_not_called()


class TestBaseWindowCleanup:
    """Test cleanup functionality."""

    def test_cleanup_can_be_called(self, qtbot):
        """cleanup() should be callable without errors."""
        window = SidebarWindowBase()
        qtbot.addWidget(window)

        # Should not raise exception
        window.cleanup()

    def test_cleanup_can_be_overridden(self, qtbot):
        """Subclasses should be able to override cleanup."""

        class TestWindow(SidebarWindowBase):
            def __init__(self):
                super().__init__()
                self.cleaned_up = False

            def cleanup(self):
                self.cleaned_up = True

        window = TestWindow()
        qtbot.addWidget(window)

        window.cleanup()

        assert window.cleaned_up is True


class TestBaseWindowStateManagement:
    """Test UI state management methods."""

    def test_has_switch_to_test_mode_method(self, qtbot):
        """BaseWindow should have _switch_to_test_mode method."""
        window = SidebarWindowBase()
        qtbot.addWidget(window)

        assert hasattr(window, "_switch_to_test_mode")
        assert callable(window._switch_to_test_mode)

    def test_switch_to_test_mode_can_be_called(self, qtbot):
        """_switch_to_test_mode should be callable (default no-op)."""
        window = SidebarWindowBase()
        qtbot.addWidget(window)

        # Should not raise exception
        window._switch_to_test_mode()

    def test_switch_to_test_mode_can_be_overridden(self, qtbot):
        """Subclasses should be able to override _switch_to_test_mode."""

        class TestWindow(SidebarWindowBase):
            def __init__(self):
                super().__init__()
                self.test_mode = False

            def _switch_to_test_mode(self):
                self.test_mode = True

        window = TestWindow()
        qtbot.addWidget(window)

        window._switch_to_test_mode()

        assert window.test_mode is True
