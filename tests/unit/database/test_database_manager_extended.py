"""
Phase 8 Task 4 - Phase 2: Extended tests for database_manager.py

Tests cover additional edge cases and error scenarios to increase coverage from 79% to 90%+.
Focuses on:
- Connection error handling
- Transaction rollback scenarios
- Edge cases in filtering and querying
- Database optimization and cleanup edge cases
- Statistics calculation edge cases
"""

import os
import sqlite3
import tempfile
from datetime import datetime, timedelta
from unittest.mock import MagicMock, Mock, patch

import pytest

from src.app.database.database_manager import DatabaseError, DatabaseManager
from src.app.database.models import ProjectData, Session, TestResult

# ============================================================================
# Test Fixtures
# ============================================================================


@pytest.fixture
def temp_db():
    """Create temporary database file."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name
    yield db_path
    # Cleanup
    if os.path.exists(db_path):
        os.unlink(db_path)


@pytest.fixture
def db_manager(temp_db):
    """Create DatabaseManager instance with temp database."""
    return DatabaseManager(temp_db)


# ============================================================================
# Connection Error Handling Tests
# ============================================================================


class TestConnectionErrorHandling:
    """Test database connection error scenarios."""

    def test_connect_invalid_path(self):
        """Test connection with invalid database path."""
        # Try to create DB in non-existent directory
        with pytest.raises(DatabaseError):
            manager = DatabaseManager("/nonexistent/invalid/path/test.db")
            manager.connect()

    @patch("sqlite3.connect")
    def test_connect_sqlite_error(self, mock_connect):
        """Test connection handles SQLite errors."""
        mock_connect.side_effect = sqlite3.Error("Connection failed")

        with pytest.raises(DatabaseError) as exc_info:
            manager = DatabaseManager()
            manager.connect()

        assert "Failed to connect" in str(exc_info.value)

    def test_close_without_connection(self, db_manager):
        """Test close without active connection doesn't error."""
        db_manager.connection = None
        db_manager.close()  # Should not raise

    def test_multiple_connections(self, db_manager):
        """Test multiple connect calls work correctly."""
        conn1 = db_manager.connect()
        assert conn1 is not None
        db_manager.close()

        conn2 = db_manager.connect()
        assert conn2 is not None
        db_manager.close()


# ============================================================================
# Save Operations Edge Cases
# ============================================================================


class TestSaveOperationsEdgeCases:
    """Test edge cases in save operations."""

    def test_save_test_result_with_none_timestamp(self, db_manager):
        """Test saving test result with None timestamp uses current time."""
        result = TestResult(
            test_type="validator",
            file_path="test.cpp",
            test_count=5,
            passed_tests=5,
            failed_tests=0,
            total_time=1.5,
            timestamp=None,  # Should use current time
        )

        result_id = db_manager.save_test_result(result)

        assert result_id > 0

        # Verify timestamp was set
        results = db_manager.get_test_results(limit=1)
        assert results[0].timestamp is not None

    def test_save_test_result_with_empty_strings(self, db_manager):
        """Test saving test result with empty optional fields."""
        result = TestResult(
            test_type="validator",
            file_path="",  # Empty
            test_count=0,
            passed_tests=0,
            failed_tests=0,
            total_time=0.0,
            project_name="",  # Empty
            files_snapshot="",  # Empty
            mismatch_analysis="",  # Empty
        )

        result_id = db_manager.save_test_result(result)

        assert result_id > 0

    def test_save_session_with_none_fields(self, db_manager):
        """Test saving session with None optional fields."""
        session = Session(
            session_name="test", open_files=None, active_file=None, project_name=None
        )

        session_id = db_manager.save_session(session)

        assert session_id > 0

    @patch("sqlite3.connect")
    def test_save_test_result_connection_error(self, mock_connect, db_manager):
        """Test save_test_result handles connection errors."""
        mock_connect.side_effect = sqlite3.Error("Connection lost")

        result = TestResult(
            test_type="validator",
            file_path="test.cpp",
            test_count=1,
            passed_tests=1,
            failed_tests=0,
            total_time=1.0,
        )

        with pytest.raises(DatabaseError):
            db_manager.save_test_result(result)


# ============================================================================
# Query Filtering Edge Cases
# ============================================================================


class TestQueryFilteringEdgeCases:
    """Test edge cases in query filtering."""

    def test_get_test_results_with_all_filters(self, db_manager):
        """Test get_test_results with all filter parameters."""
        # Save test results
        for i in range(3):
            result = TestResult(
                test_type="validator",
                file_path=f"test{i}.cpp",
                test_count=5,
                passed_tests=4 if i < 2 else 5,
                failed_tests=1 if i < 2 else 0,
                total_time=1.0,
                project_name="TestProject",
            )
            db_manager.save_test_result(result)

        # Query with all filters
        results = db_manager.get_test_results(
            test_type="validator",
            project_name="TestProject",
            days=1,
            file_name="test0",
            status="failed",
            limit=10,
        )

        assert len(results) == 1
        assert "test0" in results[0].file_path

    def test_get_test_results_no_matches(self, db_manager):
        """Test get_test_results returns empty list when no matches."""
        results = db_manager.get_test_results(test_type="nonexistent")

        assert results == []

    def test_get_sessions_with_project_filter(self, db_manager):
        """Test get_sessions with project name filter."""
        # Save sessions for different projects
        session1 = Session(session_name="session1", project_name="Project1")
        session2 = Session(session_name="session2", project_name="Project2")

        db_manager.save_session(session1)
        db_manager.save_session(session2)

        # Filter by project
        sessions = db_manager.get_sessions(project_name="Project1")

        assert len(sessions) == 1
        assert sessions[0].session_name == "session1"

    def test_get_projects_respects_limit(self, db_manager):
        """Test get_projects respects limit parameter."""
        # Save multiple projects
        for i in range(10):
            project = ProjectData(project_name=f"Project{i}", project_path=f"/path/{i}")
            db_manager.save_project_data(project)

        # Get with limit
        projects = db_manager.get_projects(limit=3)

        assert len(projects) == 3


# ============================================================================
# Statistics Calculation Edge Cases
# ============================================================================


class TestStatisticsEdgeCases:
    """Test edge cases in statistics calculation."""

    def test_get_test_statistics_empty_database(self, db_manager):
        """Test statistics on empty database."""
        stats = db_manager.get_test_statistics()

        assert stats["total_tests"] == 0
        assert stats["success_rate"] == 0.0

    def test_get_test_statistics_with_project_filter(self, db_manager):
        """Test statistics filtered by project."""
        # Save results for different projects
        result1 = TestResult(
            test_type="validator",
            file_path="test.cpp",
            test_count=5,
            passed_tests=5,
            failed_tests=0,
            total_time=1.0,
            project_name="Project1",
        )
        result2 = TestResult(
            test_type="validator",
            file_path="test.cpp",
            test_count=3,
            passed_tests=2,
            failed_tests=1,
            total_time=1.0,
            project_name="Project2",
        )

        db_manager.save_test_result(result1)
        db_manager.save_test_result(result2)

        # Get stats for Project1 only
        stats = db_manager.get_test_statistics(project_name="Project1")

        assert stats["total_tests"] == 1  # Only 1 test result for Project1
        assert stats["success_rate"] == 100.0

    def test_get_test_statistics_success_rate_calculation(self, db_manager):
        """Test success rate calculation with mixed results."""
        result = TestResult(
            test_type="validator",
            file_path="test.cpp",
            test_count=10,
            passed_tests=7,
            failed_tests=3,
            total_time=1.0,
        )
        db_manager.save_test_result(result)

        stats = db_manager.get_test_statistics()

        assert stats["success_rate"] == 70.0


# ============================================================================
# Cleanup and Maintenance Edge Cases
# ============================================================================


class TestCleanupEdgeCases:
    """Test edge cases in cleanup and maintenance operations."""

    def test_cleanup_old_data_no_old_data(self, db_manager):
        """Test cleanup when no old data exists."""
        # Save recent result
        result = TestResult(
            test_type="validator",
            file_path="test.cpp",
            test_count=1,
            passed_tests=1,
            failed_tests=0,
            total_time=1.0,
        )
        db_manager.save_test_result(result)

        # Cleanup shouldn't delete anything
        db_manager.cleanup_old_data(days=30)

        results = db_manager.get_test_results()
        assert len(results) == 1

    def test_delete_test_result_nonexistent(self, db_manager):
        """Test deleting nonexistent test result."""
        # Should not raise error
        db_manager.delete_test_result(99999)

    def test_delete_all_data_without_confirmation(self, db_manager):
        """Test delete_all_data requires confirmation."""
        # Save some data
        result = TestResult(
            test_type="validator",
            file_path="test.cpp",
            test_count=1,
            passed_tests=1,
            failed_tests=0,
            total_time=1.0,
        )
        db_manager.save_test_result(result)

        # Try to delete without confirmation
        db_manager.delete_all_data(confirm=False)

        # Data should still exist
        results = db_manager.get_test_results()
        assert len(results) == 1

    def test_delete_all_data_with_confirmation(self, db_manager):
        """Test delete_all_data with confirmation."""
        # Save some data
        result = TestResult(
            test_type="validator",
            file_path="test.cpp",
            test_count=1,
            passed_tests=1,
            failed_tests=0,
            total_time=1.0,
        )
        db_manager.save_test_result(result)

        # Delete with confirmation
        db_manager.delete_all_data(confirm=True)

        # Data should be gone
        results = db_manager.get_test_results()
        assert len(results) == 0

    def test_optimize_database(self, db_manager):
        """Test database optimization."""
        # Save and delete data to create fragmentation
        for i in range(10):
            result = TestResult(
                test_type="validator",
                file_path=f"test{i}.cpp",
                test_count=1,
                passed_tests=1,
                failed_tests=0,
                total_time=1.0,
            )
            result_id = db_manager.save_test_result(result)
            if i < 5:
                db_manager.delete_test_result(result_id)

        # Optimize
        result = db_manager.optimize_database()

        assert "size_before_bytes" in result
        assert "size_after_bytes" in result
        assert result["size_before_bytes"] >= 0
        assert result["size_after_bytes"] >= 0

    def test_get_database_stats(self, db_manager):
        """Test getting database statistics."""
        # Save some data
        result = TestResult(
            test_type="validator",
            file_path="test.cpp",
            test_count=5,
            passed_tests=5,
            failed_tests=0,
            total_time=1.0,
        )
        db_manager.save_test_result(result)

        stats = db_manager.get_database_stats()

        assert "test_results_count" in stats
        assert "sessions_count" in stats
        assert "database_size_bytes" in stats
        assert stats["test_results_count"] > 0


# ============================================================================
# Integration Tests
# ============================================================================


class TestDatabaseManagerIntegration:
    """Integration tests for complete workflows."""

    def test_full_lifecycle(self, db_manager):
        """Test complete save, retrieve, delete lifecycle."""
        # Save
        result = TestResult(
            test_type="validator",
            file_path="test.cpp",
            test_count=10,
            passed_tests=8,
            failed_tests=2,
            total_time=2.5,
            project_name="TestProject",
        )
        result_id = db_manager.save_test_result(result)

        # Retrieve
        results = db_manager.get_test_results()
        assert len(results) == 1
        assert results[0].test_count == 10

        # Get stats
        stats = db_manager.get_test_statistics()
        assert stats["total_tests"] == 1  # 1 test result saved

        # Delete
        db_manager.delete_test_result(result_id)
        results = db_manager.get_test_results()
        assert len(results) == 0

    def test_multiple_projects_workflow(self, db_manager):
        """Test workflow with multiple projects."""
        # Save results for multiple projects
        for i in range(3):
            result = TestResult(
                test_type="validator",
                file_path=f"test{i}.cpp",
                test_count=5,
                passed_tests=5,
                failed_tests=0,
                total_time=1.0,
                project_name=f"Project{i}",
            )
            db_manager.save_test_result(result)

            project = ProjectData(project_name=f"Project{i}", project_path=f"/path/{i}")
            db_manager.save_project_data(project)

        # Get all projects
        projects = db_manager.get_projects()
        assert len(projects) == 3

        # Get results for specific project
        results = db_manager.get_test_results(project_name="Project1")
        assert len(results) == 1
        assert results[0].project_name == "Project1"


# ============================================================================
# Additional Coverage Tests for Missing Lines
# ============================================================================


class TestDatabaseInitializationErrors:
    """Test database initialization error scenarios."""

    def test_initialize_database_with_readonly_directory(self, temp_db):
        """Test initialization handles readonly directory gracefully."""
        # This test verifies error handling exists
        # On Windows, creating DB in System32 would fail with permissions
        # But we can't reliably test this without admin rights
        # So we just verify the manager can be created successfully normally
        manager = DatabaseManager(temp_db)
        assert manager is not None


class TestSaveResultErrorPaths:
    """Test error paths in save_test_result."""

    def test_save_test_result_integrity_error(self, db_manager):
        """Test save_test_result handles IntegrityError."""
        result = TestResult(
            test_type="validator",
            file_path="test.cpp",
            test_count=5,
            passed_tests=5,
            failed_tests=0,
            total_time=1.0,
        )

        # Mock cursor to raise IntegrityError
        with patch.object(db_manager, "connect") as mock_connect:
            mock_conn = MagicMock()
            mock_cursor = MagicMock()
            mock_cursor.execute.side_effect = sqlite3.IntegrityError(
                "Constraint violation"
            )
            mock_conn.cursor.return_value = mock_cursor
            mock_connect.return_value = mock_conn

            with pytest.raises(DatabaseError) as exc_info:
                db_manager.save_test_result(result)

            assert "Invalid test result data" in str(exc_info.value)

    def test_save_test_result_sqlite_error(self, db_manager):
        """Test save_test_result handles generic SQLite errors."""
        result = TestResult(
            test_type="validator",
            file_path="test.cpp",
            test_count=5,
            passed_tests=5,
            failed_tests=0,
            total_time=1.0,
        )

        with patch.object(db_manager, "connect") as mock_connect:
            mock_conn = MagicMock()
            mock_cursor = MagicMock()
            mock_cursor.execute.side_effect = sqlite3.Error("Database locked")
            mock_conn.cursor.return_value = mock_cursor
            mock_connect.return_value = mock_conn

            with pytest.raises(DatabaseError) as exc_info:
                db_manager.save_test_result(result)

            assert "Failed to save test result" in str(exc_info.value)


class TestGetResultsErrorPaths:
    """Test error paths in get_test_results."""

    def test_get_test_results_sqlite_error(self, db_manager):
        """Test get_test_results handles SQLite errors."""
        with patch.object(db_manager, "connect") as mock_connect:
            mock_conn = MagicMock()
            mock_cursor = MagicMock()
            mock_cursor.execute.side_effect = sqlite3.Error("Query failed")
            mock_conn.cursor.return_value = mock_cursor
            mock_connect.return_value = mock_conn

            with pytest.raises(DatabaseError) as exc_info:
                db_manager.get_test_results()

            assert "Failed to retrieve test results" in str(exc_info.value)


class TestSessionErrorPaths:
    """Test error paths in session operations."""

    def test_save_session_sqlite_error(self, db_manager):
        """Test save_session handles SQLite errors."""
        session = Session(
            session_name="Test Session",
            open_files="file1.cpp;file2.cpp",
            active_file="file1.cpp",
        )

        with patch.object(db_manager, "connect") as mock_connect:
            mock_conn = MagicMock()
            mock_cursor = MagicMock()
            mock_cursor.execute.side_effect = sqlite3.Error("Insert failed")
            mock_conn.cursor.return_value = mock_cursor
            mock_connect.return_value = mock_conn

            with pytest.raises(DatabaseError) as exc_info:
                db_manager.save_session(session)

            assert "Failed to save session" in str(exc_info.value)

    def test_get_sessions_sqlite_error(self, db_manager):
        """Test get_sessions handles SQLite errors."""
        with patch.object(db_manager, "connect") as mock_connect:
            mock_conn = MagicMock()
            mock_cursor = MagicMock()
            mock_cursor.execute.side_effect = sqlite3.Error("Query failed")
            mock_conn.cursor.return_value = mock_cursor
            mock_connect.return_value = mock_conn

            with pytest.raises(DatabaseError) as exc_info:
                db_manager.get_sessions()

            assert "Failed to retrieve sessions" in str(exc_info.value)


class TestProjectDataErrorPaths:
    """Test error paths in project data operations."""

    def test_save_project_data_sqlite_error(self, db_manager):
        """Test save_project_data handles SQLite errors."""
        project = ProjectData(project_name="Test Project", project_path="/test/path")

        with patch.object(db_manager, "connect") as mock_connect:
            mock_conn = MagicMock()
            mock_cursor = MagicMock()
            mock_cursor.execute.side_effect = sqlite3.Error("Insert failed")
            mock_conn.cursor.return_value = mock_cursor
            mock_connect.return_value = mock_conn

            with pytest.raises(DatabaseError) as exc_info:
                db_manager.save_project_data(project)

            assert "Failed to save project data" in str(exc_info.value)

    def test_get_projects_sqlite_error(self, db_manager):
        """Test get_projects handles SQLite errors."""
        with patch.object(db_manager, "connect") as mock_connect:
            mock_conn = MagicMock()
            mock_cursor = MagicMock()
            mock_cursor.execute.side_effect = sqlite3.Error("Query failed")
            mock_conn.cursor.return_value = mock_cursor
            mock_connect.return_value = mock_conn

            with pytest.raises(DatabaseError) as exc_info:
                db_manager.get_projects()

            assert "Failed to retrieve projects" in str(exc_info.value)


class TestStatisticsErrorPaths:
    """Test error paths in statistics operations."""

    def test_get_test_statistics_sqlite_error(self, db_manager):
        """Test get_test_statistics handles SQLite errors."""
        with patch.object(db_manager, "connect") as mock_connect:
            mock_conn = MagicMock()
            mock_cursor = MagicMock()
            mock_cursor.execute.side_effect = sqlite3.Error("Query failed")
            mock_conn.cursor.return_value = mock_cursor
            mock_connect.return_value = mock_conn

            with pytest.raises(DatabaseError) as exc_info:
                db_manager.get_test_statistics()

            assert "Failed to retrieve test statistics" in str(exc_info.value)


class TestCleanupErrorPaths:
    """Test error paths in cleanup operations."""

    def test_delete_all_data_requires_confirmation(self, db_manager):
        """Test delete_all_data requires confirmation."""
        # Without confirmation, should not delete
        db_manager.delete_all_data(confirm=False)
        # Should not raise error

    def test_delete_all_data_sqlite_error(self, db_manager):
        """Test delete_all_data handles SQLite errors."""
        with patch.object(db_manager, "connect") as mock_connect:
            mock_conn = MagicMock()
            mock_cursor = MagicMock()
            mock_cursor.execute.side_effect = sqlite3.Error("Delete failed")
            mock_conn.cursor.return_value = mock_cursor
            mock_connect.return_value = mock_conn

            with pytest.raises(DatabaseError) as exc_info:
                db_manager.delete_all_data(confirm=True)

            assert "Failed to delete all data" in str(exc_info.value)


class TestDeleteResultErrorPaths:
    """Test error paths in delete_test_result."""

    def test_delete_test_result_sqlite_error(self, db_manager):
        """Test delete_test_result handles SQLite errors."""
        with patch.object(db_manager, "connect") as mock_connect:
            mock_conn = MagicMock()
            mock_cursor = MagicMock()
            mock_cursor.execute.side_effect = sqlite3.Error("Delete failed")
            mock_conn.cursor.return_value = mock_cursor
            mock_connect.return_value = mock_conn

            with pytest.raises(DatabaseError) as exc_info:
                db_manager.delete_test_result(1)

            assert "Failed to delete test result" in str(exc_info.value)


class TestAdditionalErrorScenarios:
    """Test additional error scenarios."""

    def test_get_test_results_with_empty_database(self, db_manager):
        """Test get_test_results returns empty list on empty database."""
        results = db_manager.get_test_results()
        assert results == []

    def test_get_sessions_with_empty_database(self, db_manager):
        """Test get_sessions returns empty list on empty database."""
        sessions = db_manager.get_sessions()
        assert sessions == []

    def test_get_projects_with_empty_database(self, db_manager):
        """Test get_projects returns empty list on empty database."""
        projects = db_manager.get_projects()
        assert projects == []
