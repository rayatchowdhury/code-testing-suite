"""
Phase 8 Task 4 - Phase 2: Tests for database_operations.py

Tests cover:
- Database statistics refresh and display
- Old data cleanup with confirmations
- Delete all data with double confirmation
- Database optimization
- Error handling for all operations
"""

from unittest.mock import Mock, call, patch

import pytest
from PySide6.QtWidgets import QMessageBox

from src.app.core.config.database.database_operations import DatabaseOperations

# ============================================================================
# Test Fixtures
# ============================================================================


@pytest.fixture
def mock_parent_dialog():
    """Create a mock parent dialog."""
    parent = Mock()
    parent.db_stats_label = Mock()
    return parent


@pytest.fixture
def mock_database_manager():
    """Create a mock database manager with default stats."""
    manager = Mock()
    manager.get_database_stats.return_value = {
        "test_results_count": 1000,
        "sessions_count": 50,
        "database_size_mb": 25.5,
        "oldest_test": "2024-01-01",
        "newest_test": "2024-12-31",
        "oldest_session": "2024-01-15",
        "newest_session": "2024-12-20",
    }
    manager.cleanup_old_data.return_value = True
    manager.delete_all_data.return_value = True
    manager.optimize_database.return_value = {
        "space_saved_mb": 5.2,
        "size_before_mb": 25.5,
        "size_after_mb": 20.3,
    }
    return manager


@pytest.fixture
def db_operations(mock_parent_dialog, mock_database_manager):
    """Create DatabaseOperations instance for testing."""
    return DatabaseOperations(mock_parent_dialog, mock_database_manager)


# ============================================================================
# Initialization Tests
# ============================================================================


class TestInitialization:
    """Test DatabaseOperations initialization."""

    def test_stores_parent_and_manager(self, mock_parent_dialog, mock_database_manager):
        """Test initialization stores references."""
        db_ops = DatabaseOperations(mock_parent_dialog, mock_database_manager)
        assert db_ops.parent == mock_parent_dialog
        assert db_ops.database_manager == mock_database_manager


# ============================================================================
# Refresh Stats Tests
# ============================================================================


class TestRefreshDatabaseStats:
    """Test refresh_database_stats method."""

    def test_displays_formatted_stats(self, db_operations, mock_parent_dialog):
        """Test successful stats display."""
        db_operations.refresh_database_stats()

        mock_parent_dialog.db_stats_label.setText.assert_called_once()
        stats_text = mock_parent_dialog.db_stats_label.setText.call_args[0][0]
        assert "1,000" in stats_text
        assert "25.5 MB" in stats_text

    def test_handles_no_stats(self, db_operations, mock_database_manager, mock_parent_dialog):
        """Test handles None stats."""
        mock_database_manager.get_database_stats.return_value = None

        db_operations.refresh_database_stats()

        error_text = mock_parent_dialog.db_stats_label.setText.call_args[0][0]
        assert "Could not retrieve" in error_text

    def test_handles_exception(self, db_operations, mock_database_manager, mock_parent_dialog):
        """Test handles exception gracefully."""
        mock_database_manager.get_database_stats.side_effect = Exception("DB Error")

        db_operations.refresh_database_stats()

        error_text = mock_parent_dialog.db_stats_label.setText.call_args[0][0]
        assert "Error retrieving stats" in error_text


# ============================================================================
# Cleanup Tests
# ============================================================================


class TestCleanupOldData:
    """Test cleanup_old_data method."""

    @patch("src.app.core.config.database.database_operations.QMessageBox.question")
    def test_user_cancels(self, mock_question, db_operations, mock_database_manager):
        """Test cleanup cancelled by user."""
        mock_question.return_value = QMessageBox.No

        db_operations.cleanup_old_data()

        mock_database_manager.cleanup_old_data.assert_not_called()

    @patch("src.app.core.config.database.database_operations.QMessageBox.information")
    @patch("src.app.core.config.database.database_operations.QMessageBox.question")
    def test_cleanup_executes(self, mock_question, mock_info, db_operations, mock_database_manager):
        """Test cleanup executes when confirmed."""
        mock_question.return_value = QMessageBox.Yes
        mock_database_manager.get_database_stats.side_effect = [
            {
                "test_results_count": 1000,
                "sessions_count": 50,
                "database_size_mb": 25.5,
                "oldest_test": "2024-01-01",
                "newest_test": "2024-12-31",
                "oldest_session": "2024-01-15",
                "newest_session": "2024-12-20",
            },
            {
                "test_results_count": 800,
                "sessions_count": 40,
                "database_size_mb": 20.0,
                "oldest_test": "2024-06-01",
                "newest_test": "2024-12-31",
                "oldest_session": "2024-06-15",
                "newest_session": "2024-12-20",
            },
            {
                "test_results_count": 800,
                "sessions_count": 40,
                "database_size_mb": 20.0,
                "oldest_test": "2024-06-01",
                "newest_test": "2024-12-31",
                "oldest_session": "2024-06-15",
                "newest_session": "2024-12-20",
            },
        ]

        db_operations.cleanup_old_data()

        mock_database_manager.cleanup_old_data.assert_called_once_with(30)
        mock_info.assert_called_once()

    @patch("src.app.core.config.database.database_operations.QMessageBox.warning")
    def test_handles_no_stats(self, mock_warning, db_operations, mock_database_manager):
        """Test handles missing stats."""
        mock_database_manager.get_database_stats.return_value = None

        db_operations.cleanup_old_data()

        mock_warning.assert_called_once()
        mock_database_manager.cleanup_old_data.assert_not_called()


# ============================================================================
# Delete All Data Tests
# ============================================================================


class TestDeleteAllData:
    """Test delete_all_data method."""

    @patch("src.app.core.config.database.database_operations.QMessageBox.warning")
    def test_first_confirmation_cancelled(self, mock_warning, db_operations, mock_database_manager):
        """Test delete cancelled at first confirmation."""
        mock_warning.return_value = QMessageBox.No

        db_operations.delete_all_data()

        mock_database_manager.delete_all_data.assert_not_called()

    @patch("src.app.core.config.database.database_operations.QInputDialog.getText")
    @patch("src.app.core.config.database.database_operations.QMessageBox.information")
    @patch("src.app.core.config.database.database_operations.QMessageBox.warning")
    def test_wrong_confirmation_text(
        self, mock_warning, mock_info, mock_input, db_operations, mock_database_manager
    ):
        """Test delete cancelled with wrong text."""
        mock_warning.return_value = QMessageBox.Yes
        mock_input.return_value = ("WRONG", True)

        db_operations.delete_all_data()

        mock_info.assert_called_once()
        mock_database_manager.delete_all_data.assert_not_called()

    @patch("src.app.core.config.database.database_operations.QInputDialog.getText")
    @patch("src.app.core.config.database.database_operations.QMessageBox.information")
    @patch("src.app.core.config.database.database_operations.QMessageBox.warning")
    def test_successful_delete(
        self, mock_warning, mock_info, mock_input, db_operations, mock_database_manager
    ):
        """Test successful deletion with correct confirmation."""
        mock_warning.return_value = QMessageBox.Yes
        mock_input.return_value = ("DELETE ALL", True)
        mock_database_manager.delete_all_data.return_value = True
        mock_database_manager.get_database_stats.side_effect = [
            {
                "test_results_count": 1000,
                "sessions_count": 50,
                "database_size_mb": 25.5,
                "oldest_test": "2024-01-01",
                "newest_test": "2024-12-31",
                "oldest_session": "2024-01-15",
                "newest_session": "2024-12-20",
            },
            {
                "test_results_count": 0,
                "sessions_count": 0,
                "database_size_mb": 0.0,
                "oldest_test": "N/A",
                "newest_test": "N/A",
                "oldest_session": "N/A",
                "newest_session": "N/A",
            },
        ]

        db_operations.delete_all_data()

        mock_database_manager.delete_all_data.assert_called_once_with(confirm=True)
        assert mock_info.call_count == 1  # Success message

    @patch("src.app.core.config.database.database_operations.QMessageBox.information")
    def test_empty_database(self, mock_info, db_operations, mock_database_manager):
        """Test delete when database is empty."""
        mock_database_manager.get_database_stats.return_value = {
            "test_results_count": 0,
            "sessions_count": 0,
            "database_size_mb": 0.0,
            "oldest_test": "N/A",
            "newest_test": "N/A",
            "oldest_session": "N/A",
            "newest_session": "N/A",
        }

        db_operations.delete_all_data()

        mock_info.assert_called_once()
        info_call = mock_info.call_args[0]
        assert "No Data" in info_call[1]


# ============================================================================
# Optimize Database Tests
# ============================================================================


class TestOptimizeDatabase:
    """Test optimize_database method."""

    @patch("src.app.core.config.database.database_operations.QMessageBox.question")
    def test_user_cancels(self, mock_question, db_operations, mock_database_manager):
        """Test optimization cancelled by user."""
        mock_question.return_value = QMessageBox.No

        db_operations.optimize_database()

        mock_database_manager.optimize_database.assert_not_called()

    @patch("src.app.core.config.database.database_operations.QMessageBox.information")
    @patch("src.app.core.config.database.database_operations.QMessageBox.question")
    def test_successful_optimization(
        self, mock_question, mock_info, db_operations, mock_database_manager
    ):
        """Test successful optimization with space saved."""
        mock_question.return_value = QMessageBox.Yes
        mock_database_manager.get_database_stats.side_effect = [
            {
                "test_results_count": 1000,
                "sessions_count": 50,
                "database_size_mb": 25.5,
                "oldest_test": "2024-01-01",
                "newest_test": "2024-12-31",
                "oldest_session": "2024-01-15",
                "newest_session": "2024-12-20",
            },
            {
                "test_results_count": 1000,
                "sessions_count": 50,
                "database_size_mb": 20.3,
                "oldest_test": "2024-01-01",
                "newest_test": "2024-12-31",
                "oldest_session": "2024-01-15",
                "newest_session": "2024-12-20",
            },
        ]

        db_operations.optimize_database()

        mock_database_manager.optimize_database.assert_called_once()
        mock_info.assert_called_once()
        info_text = mock_info.call_args[0][2]
        assert "5.2 MB" in info_text  # space saved

    @patch("src.app.core.config.database.database_operations.QMessageBox.information")
    @patch("src.app.core.config.database.database_operations.QMessageBox.question")
    def test_already_optimized(
        self, mock_question, mock_info, db_operations, mock_database_manager
    ):
        """Test optimization when no space to reclaim."""
        mock_question.return_value = QMessageBox.Yes
        mock_database_manager.optimize_database.return_value = {
            "space_saved_mb": 0.005,
            "size_before_mb": 20.3,
            "size_after_mb": 20.295,
        }
        mock_database_manager.get_database_stats.side_effect = [
            {
                "test_results_count": 1000,
                "sessions_count": 50,
                "database_size_mb": 20.3,
                "oldest_test": "2024-01-01",
                "newest_test": "2024-12-31",
                "oldest_session": "2024-01-15",
                "newest_session": "2024-12-20",
            },
            {
                "test_results_count": 1000,
                "sessions_count": 50,
                "database_size_mb": 20.295,
                "oldest_test": "2024-01-01",
                "newest_test": "2024-12-31",
                "oldest_session": "2024-01-15",
                "newest_session": "2024-12-20",
            },
        ]

        db_operations.optimize_database()

        info_text = mock_info.call_args[0][2]
        assert "already optimized" in info_text


# ============================================================================
# Error Handling Tests
# ============================================================================


class TestErrorHandling:
    """Test error handling across all methods."""

    @patch("src.app.core.config.database.database_operations.QMessageBox.critical")
    def test_cleanup_exception(self, mock_critical, db_operations, mock_database_manager):
        """Test cleanup handles exceptions."""
        mock_database_manager.get_database_stats.side_effect = Exception("DB Error")

        db_operations.cleanup_old_data()

        mock_critical.assert_called_once()

    @patch("src.app.core.config.database.database_operations.QMessageBox.critical")
    def test_delete_exception(self, mock_critical, db_operations, mock_database_manager):
        """Test delete_all_data handles exceptions."""
        mock_database_manager.get_database_stats.side_effect = Exception("DB Error")

        db_operations.delete_all_data()

        mock_critical.assert_called_once()

    @patch("src.app.core.config.database.database_operations.QMessageBox.critical")
    def test_optimize_exception(self, mock_critical, db_operations, mock_database_manager):
        """Test optimize_database handles exceptions."""
        mock_database_manager.get_database_stats.side_effect = Exception("DB Error")

        db_operations.optimize_database()

        mock_critical.assert_called_once()


# ============================================================================
# Integration Tests
# ============================================================================


class TestIntegration:
    """Integration tests for full workflows."""

    def test_refresh_called_after_cleanup(self, db_operations, mock_parent_dialog):
        """Test stats refresh after cleanup."""
        with patch("src.app.core.config.database.database_operations.QMessageBox.information"):
            with patch(
                "src.app.core.config.database.database_operations.QMessageBox.question",
                return_value=QMessageBox.Yes,
            ):
                db_operations.cleanup_old_data()

        # Verify refresh was called
        assert mock_parent_dialog.db_stats_label.setText.called

    def test_multiple_operations_workflow(self, db_operations, mock_database_manager):
        """Test sequence of operations."""
        # Refresh
        db_operations.refresh_database_stats()

        # Cleanup
        with patch("src.app.core.config.database.database_operations.QMessageBox.information"):
            with patch(
                "src.app.core.config.database.database_operations.QMessageBox.question",
                return_value=QMessageBox.Yes,
            ):
                db_operations.cleanup_old_data()

        # Optimize
        with patch("src.app.core.config.database.database_operations.QMessageBox.information"):
            with patch(
                "src.app.core.config.database.database_operations.QMessageBox.question",
                return_value=QMessageBox.Yes,
            ):
                db_operations.optimize_database()

        # Verify all operations called
        assert mock_database_manager.get_database_stats.called
        assert mock_database_manager.cleanup_old_data.called
        assert mock_database_manager.optimize_database.called
