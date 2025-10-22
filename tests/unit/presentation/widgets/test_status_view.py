"""
Unit tests for UnifiedStatusView base widget.

Tests status view creation, progress tracking, test card management, and signal emission.
"""

from unittest.mock import MagicMock, Mock

import pytest
from PySide6.QtWidgets import QMessageBox

from src.app.presentation.shared.components.status_view import BaseStatusView


@pytest.fixture
def status_view(qtbot):
    """Create BaseStatusView widget for testing."""
    widget = BaseStatusView("comparator")
    qtbot.addWidget(widget)
    return widget


class TestStatusViewInitialization:
    """Test status view initialization."""

    def test_creates_with_test_type(self, status_view):
        """Should initialize with test type."""
        assert status_view.test_type == "comparator"

    def test_initializes_test_state(self, status_view):
        """Should initialize test state counters."""
        assert status_view.tests_running is False
        assert status_view.total_tests == 0
        assert status_view.completed_tests == 0
        assert status_view.passed_tests == 0
        assert status_view.failed_tests == 0

    def test_has_progress_section(self, status_view):
        """Should have progress section widget."""
        assert status_view.progress_section is not None

    def test_has_cards_section(self, status_view):
        """Should have cards section widget."""
        assert status_view.cards_section is not None


class TestStatusViewTestLifecycle:
    """Test test execution lifecycle."""

    def test_on_tests_started_resets_state(self, status_view):
        """Should reset state when tests start."""
        # Set some initial state
        status_view.completed_tests = 5
        status_view.passed_tests = 3

        status_view.on_tests_started(total=10)

        assert status_view.tests_running is True
        assert status_view.total_tests == 10
        assert status_view.completed_tests == 0
        assert status_view.passed_tests == 0
        assert status_view.failed_tests == 0

    def test_on_test_running_updates_progress(self, status_view):
        """Should update progress when test is running."""
        status_view.on_tests_started(10)

        # Should not raise errors
        status_view.on_test_running(current=1, total=10)
        status_view.on_test_running(current=2, total=10)

    def test_on_test_completed_updates_counters(self, status_view):
        """Should update counters when test completes."""
        status_view.on_tests_started(10)

        # Complete a passing test
        status_view.on_test_completed(test_number=1, passed=True)

        assert status_view.completed_tests == 1
        assert status_view.passed_tests == 1
        assert status_view.failed_tests == 0

        # Complete a failing test
        status_view.on_test_completed(test_number=2, passed=False)

        assert status_view.completed_tests == 2
        assert status_view.passed_tests == 1
        assert status_view.failed_tests == 1

    def test_on_all_tests_completed_stops_running(self, status_view):
        """Should mark tests as not running when all complete."""
        status_view.on_tests_started(5)
        status_view.tests_running = True

        status_view.on_all_tests_completed(all_passed=True)

        assert status_view.tests_running is False

    def test_on_all_tests_completed_notifies_parent(self, status_view):
        """Should notify parent window to enable save button."""
        # Mock parent window
        mock_parent = Mock()
        status_view.parent_window = mock_parent

        status_view.on_all_tests_completed(all_passed=True)

        mock_parent.enable_save_button.assert_called_once()


class TestStatusViewSignals:
    """Test signal emission."""

    def test_emits_stop_requested_signal(self, status_view, qtbot):
        """Should emit stopRequested signal."""
        status_view.tests_running = True
        # Mock controls_panel which is set by subclasses
        status_view.controls_panel = Mock()

        with qtbot.waitSignal(status_view.stopRequested, timeout=1000):
            status_view._handle_stop()

    def test_emits_back_requested_signal(self, status_view, qtbot):
        """Should emit backRequested signal."""
        status_view.tests_running = False

        with qtbot.waitSignal(status_view.backRequested, timeout=1000):
            status_view._handle_back()


class TestStatusViewCardManagement:
    """Test card addition and management."""

    def test_adds_test_card(self, status_view, qtbot):
        """Should add test card to cards section."""
        # Create a real QWidget instead of Mock for Qt layout
        from PySide6.QtWidgets import QWidget

        card = QWidget()
        card.passed = True
        card.clicked = Mock()  # Mock the clicked signal
        qtbot.addWidget(card)

        status_view.add_test_card(card)

        # Card click signal should be connected
        card.clicked.connect.assert_called_once()

    def test_show_test_detail_base_implementation(self, status_view):
        """Base implementation should be a no-op (for override)."""
        # Should not raise error
        status_view.show_test_detail(test_number=1)


class TestStatusViewDatabaseSaving:
    """Test database saving functionality."""

    def test_save_to_database_with_runner(self, status_view, monkeypatch):
        """Should save results using runner."""
        # Mock runner
        mock_runner = Mock()
        mock_runner.save_test_results_to_database.return_value = 123
        status_view.runner = mock_runner

        # Mock QMessageBox
        mock_msgbox = Mock()
        monkeypatch.setattr("PySide6.QtWidgets.QMessageBox.information", mock_msgbox)

        result_id = status_view.save_to_database()

        assert result_id == 123
        mock_runner.save_test_results_to_database.assert_called_once()

    def test_save_to_database_without_runner(self, status_view, monkeypatch):
        """Should show error if runner not found."""
        # Mock QMessageBox
        mock_msgbox = Mock()
        monkeypatch.setattr("PySide6.QtWidgets.QMessageBox.critical", mock_msgbox)

        result_id = status_view.save_to_database()

        assert result_id == -1
        mock_msgbox.assert_called_once()

    def test_save_to_database_with_exception(self, status_view, monkeypatch):
        """Should handle exceptions during save."""
        # Mock runner that raises exception
        mock_runner = Mock()
        mock_runner.save_test_results_to_database.side_effect = Exception(
            "Database error"
        )
        status_view.runner = mock_runner

        # Mock QMessageBox
        mock_msgbox = Mock()
        monkeypatch.setattr("PySide6.QtWidgets.QMessageBox.critical", mock_msgbox)

        result_id = status_view.save_to_database()

        assert result_id == -1
        mock_msgbox.assert_called_once()

    def test_set_runner(self, status_view):
        """Should set runner instance."""
        mock_runner = Mock()

        status_view.set_runner(mock_runner)

        assert status_view.runner is mock_runner


class TestStatusViewState:
    """Test state management."""

    def test_is_tests_running_returns_correct_state(self, status_view):
        """Should return correct running state."""
        status_view.tests_running = False
        assert status_view.is_tests_running() is False

        status_view.tests_running = True
        assert status_view.is_tests_running() is True


class TestStatusViewProgressTracking:
    """Test progress tracking through multiple tests."""

    def test_tracks_progress_through_multiple_tests(self, status_view):
        """Should correctly track progress through test suite."""
        # Start 5 tests
        status_view.on_tests_started(5)
        assert status_view.total_tests == 5

        # Complete tests one by one
        for i in range(1, 6):
            passed = i % 2 == 0  # Even numbers pass
            status_view.on_test_completed(test_number=i, passed=passed)

            assert status_view.completed_tests == i

        # Final counts should be correct
        assert status_view.completed_tests == 5
        assert status_view.passed_tests == 2  # Tests 2, 4
        assert status_view.failed_tests == 3  # Tests 1, 3, 5

    def test_multiple_test_runs(self, status_view):
        """Should handle multiple test runs correctly."""
        # First run
        status_view.on_tests_started(3)
        status_view.on_test_completed(1, True)
        status_view.on_test_completed(2, True)
        status_view.on_test_completed(3, False)
        status_view.on_all_tests_completed(False)

        # Second run should reset
        status_view.on_tests_started(2)
        assert status_view.completed_tests == 0
        assert status_view.passed_tests == 0
        assert status_view.failed_tests == 0

        status_view.on_test_completed(1, True)
        status_view.on_test_completed(2, True)

        assert status_view.completed_tests == 2
        assert status_view.passed_tests == 2
        assert status_view.failed_tests == 0
