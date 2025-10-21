"""Tests for navigation router."""

import pytest
from unittest.mock import Mock, MagicMock
from PySide6.QtCore import QObject

from src.app.presentation.navigation.router import NavigationRouter


class TestNavigationRouter:
    """Test suite for NavigationRouter."""

    @pytest.fixture
    def mock_window_manager(self):
        """Create a mock window manager."""
        manager = Mock()
        manager.show_window = Mock(return_value=True)
        manager.current_window = "main"
        return manager

    @pytest.fixture
    def router(self, mock_window_manager):
        """Create a NavigationRouter with mock window manager."""
        return NavigationRouter(mock_window_manager)

    def test_initialization(self, mock_window_manager):
        """Test router initializes correctly."""
        router = NavigationRouter(mock_window_manager)
        
        assert router._window_manager == mock_window_manager
        assert router._history == []
        assert router._max_history_size == 50

    def test_navigate_to_success(self, router, mock_window_manager):
        """Test successful navigation to a window."""
        mock_window_manager.current_window = "main"
        
        result = router.navigate_to("benchmarker")
        
        assert result is True
        mock_window_manager.show_window.assert_called_once_with("benchmarker")
        assert router._history == ["main"]

    def test_navigate_to_failure(self, router, mock_window_manager):
        """Test failed navigation."""
        mock_window_manager.show_window.return_value = False
        mock_window_manager.current_window = "main"
        
        result = router.navigate_to("invalid_window")
        
        assert result is False
        assert router._history == []  # History not updated on failure

    def test_navigate_to_no_window_manager(self):
        """Test navigation without window manager."""
        router = NavigationRouter(None)
        
        result = router.navigate_to("benchmarker")
        
        assert result is False

    def test_navigate_to_with_kwargs(self, router, mock_window_manager):
        """Test navigation with keyword arguments."""
        result = router.navigate_to("results", result_id=123)
        
        assert result is True
        mock_window_manager.show_window.assert_called_once_with("results", result_id=123)

    def test_go_back_success(self, router, mock_window_manager):
        """Test successful back navigation."""
        # Navigate forward twice to build history
        mock_window_manager.current_window = "main"
        router.navigate_to("benchmarker")
        mock_window_manager.current_window = "benchmarker"
        router.navigate_to("results")
        
        # Now go back
        result = router.go_back()
        
        assert result is True
        assert mock_window_manager.show_window.call_args[0][0] == "benchmarker"
        assert len(router._history) == 1  # Only "main" remains in history

    def test_go_back_no_history(self, router):
        """Test go_back with no history."""
        result = router.go_back()
        
        assert result is False

    def test_go_back_navigation_failed(self, router, mock_window_manager):
        """Test go_back when navigation fails."""
        # Build history
        mock_window_manager.current_window = "main"
        router.navigate_to("benchmarker")
        
        # Make navigation fail
        mock_window_manager.show_window.return_value = False
        
        result = router.go_back()
        
        assert result is False
        # History should be restored
        assert router._history == ["main"]

    def test_can_go_back(self, router, mock_window_manager):
        """Test can_go_back method."""
        # Initially no history
        assert router.can_go_back() is False
        
        # Navigate to build history
        mock_window_manager.current_window = "main"
        router.navigate_to("benchmarker")
        
        # Now should be able to go back
        assert router.can_go_back() is True

    def test_current_window(self, router, mock_window_manager):
        """Test getting current window name."""
        mock_window_manager.current_window = "results"
        
        assert router.current_window() == "results"

    def test_current_window_no_manager(self):
        """Test current_window with no window manager."""
        router = NavigationRouter(None)
        
        assert router.current_window() is None

    def test_clear_history(self, router, mock_window_manager):
        """Test clearing navigation history."""
        # Build some history
        mock_window_manager.current_window = "main"
        router.navigate_to("benchmarker")
        router.navigate_to("results")
        
        assert len(router._history) > 0
        
        router.clear_history()
        
        assert router._history == []

    def test_get_history(self, router, mock_window_manager):
        """Test getting navigation history."""
        # Build history
        mock_window_manager.current_window = "main"
        router.navigate_to("benchmarker")
        mock_window_manager.current_window = "benchmarker"
        router.navigate_to("results")
        
        history = router.get_history()
        
        assert history == ["main", "benchmarker"]
        # Ensure it's a copy
        history.append("test")
        assert router._history == ["main", "benchmarker"]

    def test_no_duplicate_consecutive_history(self, router, mock_window_manager):
        """Test that consecutive duplicates are not added to history."""
        mock_window_manager.current_window = "main"
        router.navigate_to("benchmarker")
        mock_window_manager.current_window = "benchmarker"
        router.navigate_to("benchmarker")  # Same window again
        
        # Should only have "main" once
        assert router._history == ["main"]

    def test_history_trimming(self, router, mock_window_manager):
        """Test that history is trimmed when it exceeds max size."""
        router._max_history_size = 3
        
        # Navigate many times
        mock_window_manager.current_window = "main"
        for i in range(5):
            mock_window_manager.current_window = f"window{i}"
            router.navigate_to(f"window{i+1}")
        
        # History should be trimmed to max size
        assert len(router._history) <= 3

    def test_navigation_signals(self, router, mock_window_manager):
        """Test that navigation signals are emitted."""
        completed_spy = []
        failed_spy = []
        
        router.navigationCompleted.connect(lambda w: completed_spy.append(w))
        router.navigationFailed.connect(lambda w, e: failed_spy.append((w, e)))
        
        # Successful navigation
        router.navigate_to("benchmarker")
        assert "benchmarker" in completed_spy
        
        # Failed navigation
        mock_window_manager.show_window.return_value = False
        router.navigate_to("invalid")
        assert any("invalid" in item for item in failed_spy)

    def test_same_window_navigation_no_history(self, router, mock_window_manager):
        """Test navigating to same window doesn't add to history."""
        mock_window_manager.current_window = "main"
        router.navigate_to("main")
        
        assert router._history == []

    def test_exception_during_navigation(self, router, mock_window_manager):
        """Test that exceptions during navigation are handled."""
        mock_window_manager.show_window.side_effect = Exception("Test error")
        
        result = router.navigate_to("benchmarker")
        
        assert result is False
        assert router._history == []
