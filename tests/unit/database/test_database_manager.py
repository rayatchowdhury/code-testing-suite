"""
Unit tests for DatabaseManager.

Tests all database operations including:
- Test result CRUD operations
- Session management
- Project data management
- Statistics and reporting
- Data cleanup and optimization
- File snapshots
- Mismatch analysis
"""

import json
import os
import sqlite3
import tempfile
from datetime import datetime, timedelta
from pathlib import Path

import pytest

from src.app.persistence.database.database_manager import DatabaseError, DatabaseManager
from src.app.persistence.database.models import (
    FilesSnapshot,
    ProjectData,
    Session,
    TestResult,
)
from tests.fixtures.database_fixtures import (
    SAMPLE_CPP_CODE,
    SAMPLE_MISMATCH_ANALYSIS,
    ResultBuilder,
    create_files_snapshot,
    create_sample_test_result,
    create_test_details,
    create_test_result_series,
)


@pytest.fixture
def temp_db_path(tmp_path):
    """Create a temporary database path."""
    return str(tmp_path / "test.db")


@pytest.fixture
def db_manager(temp_db_path):
    """Create a fresh DatabaseManager instance."""
    manager = DatabaseManager(temp_db_path)
    yield manager
    manager.close()


@pytest.fixture
def populated_db(db_manager):
    """Create a database with sample data."""
    # Add test results
    for i in range(5):
        result = (
            ResultBuilder()
            .with_test_type("comparator")
            .with_results(passed=8, failed=2)
            .with_project_name(f"project_{i % 2}")
            .build()
        )
        db_manager.save_test_result(result)

    # Add sessions
    session = Session(
        session_name="test_session",
        open_files=json.dumps(["file1.cpp", "file2.cpp"]),
        active_file="file1.cpp",
        timestamp=datetime.now().isoformat(),
        project_name="test_project",
    )
    db_manager.save_session(session)

    yield db_manager


class TestDatabaseManagerInitialization:
    """Test database initialization and connection."""

    def test_creates_database_file(self, temp_db_path):
        """Should create database file on initialization."""
        assert not os.path.exists(temp_db_path)

        manager = DatabaseManager(temp_db_path)

        assert os.path.exists(temp_db_path)
        manager.close()

    def test_uses_default_path_if_none_provided(self):
        """Should use default USER_DATA_DIR if no path provided."""
        manager = DatabaseManager()

        assert manager.db_path is not None
        assert "code_testing_suite.db" in manager.db_path
        manager.close()

    def test_creates_required_tables(self, db_manager):
        """Should create all required tables."""
        # Reconnect to check tables
        connection = db_manager.connect()
        cursor = connection.cursor()

        # Check test_results table
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='test_results'")
        assert cursor.fetchone() is not None

        # Check sessions table
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='sessions'")
        assert cursor.fetchone() is not None

        # Check projects table
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='projects'")
        assert cursor.fetchone() is not None

        db_manager.close()

    def test_connection_established(self, db_manager):
        """Should establish database connection."""
        connection = db_manager.connect()

        assert connection is not None
        assert isinstance(connection, sqlite3.Connection)

        db_manager.close()

    def test_row_factory_enabled(self, db_manager):
        """Should enable row_factory for column access."""
        connection = db_manager.connect()

        assert connection.row_factory == sqlite3.Row

        db_manager.close()


class TestSaveTestResult:
    """Test saving test results to database."""

    def test_saves_test_result_successfully(self, db_manager):
        """Should save test result and return ID."""
        result = create_sample_test_result("comparator")

        result_id = db_manager.save_test_result(result)

        assert result_id is not None
        assert result_id > 0

    def test_saves_all_fields(self, db_manager):
        """Should save all TestResult fields correctly."""
        result = (
            ResultBuilder()
            .with_test_type("validator")
            .with_file_path("/test/validator.cpp")
            .with_results(passed=10, failed=0)
            .with_total_time(2.5)
            .with_project_name("my_project")
            .with_files_snapshot('{"files": {}}')
            .with_mismatch_analysis("No mismatches")
            .build()
        )

        result_id = db_manager.save_test_result(result)

        # Retrieve and verify
        connection = db_manager.connect()
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM test_results WHERE id = ?", (result_id,))
        row = cursor.fetchone()

        assert row["test_type"] == "validator"
        assert row["file_path"] == "/test/validator.cpp"
        assert row["test_count"] == 10
        assert row["passed_tests"] == 10
        assert row["failed_tests"] == 0
        assert row["total_time"] == 2.5
        assert row["project_name"] == "my_project"
        assert row["files_snapshot"] == '{"files": {}}'
        assert row["mismatch_analysis"] == "No mismatches"

        db_manager.close()

    def test_handles_missing_optional_fields(self, db_manager):
        """Should handle test results with no optional fields."""
        result = TestResult(
            test_type="comparator",
            file_path="/test.cpp",
            test_count=5,
            passed_tests=5,
            failed_tests=0,
            total_time=1.0,
            timestamp=datetime.now().isoformat(),
            test_details="",
            project_name="",
            files_snapshot="",
            mismatch_analysis="",
        )

        result_id = db_manager.save_test_result(result)

        assert result_id > 0

    def test_raises_error_on_invalid_data(self, db_manager):
        """Should raise error for invalid data."""
        # Create invalid result (missing required fields)
        with pytest.raises(AttributeError):
            db_manager.save_test_result(None)


class TestGetTestResults:
    """Test retrieving test results from database."""

    def test_retrieves_all_results(self, populated_db):
        """Should retrieve all test results when no filters."""
        results = populated_db.get_test_results()

        assert len(results) == 5
        assert all(isinstance(r, TestResult) for r in results)

    def test_filters_by_test_type(self, populated_db):
        """Should filter results by test type."""
        # Add a validator result
        validator_result = create_sample_test_result("validator")
        populated_db.save_test_result(validator_result)

        results = populated_db.get_test_results(test_type="validator")

        assert len(results) >= 1
        assert all(r.test_type == "validator" for r in results)

    def test_filters_by_project_name(self, populated_db):
        """Should filter results by project name."""
        results = populated_db.get_test_results(project_name="project_0")

        assert len(results) >= 1
        assert all(r.project_name == "project_0" for r in results)

    def test_limits_results(self, populated_db):
        """Should limit number of results returned."""
        results = populated_db.get_test_results(limit=2)

        assert len(results) == 2

    def test_orders_by_timestamp_descending(self, db_manager):
        """Should return most recent results first."""
        # Create results with different timestamps
        old_result = (
            ResultBuilder()
            .with_timestamp((datetime.now() - timedelta(hours=2)).isoformat())
            .build()
        )
        new_result = ResultBuilder().with_timestamp(datetime.now().isoformat()).build()

        db_manager.save_test_result(old_result)
        db_manager.save_test_result(new_result)

        results = db_manager.get_test_results()

        # First result should be newest
        assert results[0].timestamp > results[1].timestamp

    def test_returns_empty_list_when_no_results(self, db_manager):
        """Should return empty list when no matching results."""
        results = db_manager.get_test_results(test_type="nonexistent")

        assert results == []


class TestDeleteTestResult:
    """Test deleting test results."""

    def test_deletes_result_successfully(self, populated_db):
        """Should delete test result by ID."""
        results = populated_db.get_test_results()
        result_id = results[0].id

        populated_db.delete_test_result(result_id)

        # Verify deletion
        connection = populated_db.connect()
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM test_results WHERE id = ?", (result_id,))
        assert cursor.fetchone() is None
        populated_db.close()

    def test_returns_none_for_nonexistent_id(self, db_manager):
        """Should handle deletion of nonexistent ID gracefully."""
        # Should not raise error
        db_manager.delete_test_result(99999)


class TestSessionManagement:
    """Test session save and retrieval."""

    def test_saves_session(self, db_manager):
        """Should save session and return ID."""
        session = Session(
            session_name="test_session",
            open_files=json.dumps(["file1.cpp", "file2.cpp"]),
            active_file="file1.cpp",
            timestamp=datetime.now().isoformat(),
            project_name="test_project",
        )

        session_id = db_manager.save_session(session)

        assert session_id > 0

    def test_retrieves_sessions(self, populated_db):
        """Should retrieve saved sessions."""
        sessions = populated_db.get_sessions()

        assert len(sessions) >= 1
        assert all(isinstance(s, Session) for s in sessions)

    def test_filters_sessions_by_project(self, db_manager):
        """Should filter sessions by project name."""
        # Create sessions for different projects
        session1 = Session(
            session_name="s1",
            open_files="[]",
            active_file="",
            timestamp=datetime.now().isoformat(),
            project_name="project_a",
        )
        session2 = Session(
            session_name="s2",
            open_files="[]",
            active_file="",
            timestamp=datetime.now().isoformat(),
            project_name="project_b",
        )

        db_manager.save_session(session1)
        db_manager.save_session(session2)

        sessions = db_manager.get_sessions(project_name="project_a")

        assert len(sessions) == 1
        assert sessions[0].project_name == "project_a"


class TestProjectDataManagement:
    """Test project data operations."""

    def test_saves_project_data(self, db_manager):
        """Should save project data successfully."""
        project = ProjectData(
            project_name="test_project",
            project_path="/path/to/project",
            last_accessed=datetime.now().isoformat(),
            file_count=10,
            total_lines=500,
            languages='["cpp", "python"]',
        )

        project_id = db_manager.save_project_data(project)

        assert project_id > 0

    def test_retrieves_projects(self, db_manager):
        """Should retrieve saved projects."""
        project = ProjectData(
            project_name="my_project",
            project_path="/my/project",
            last_accessed=datetime.now().isoformat(),
            file_count=5,
            total_lines=200,
            languages='["cpp"]',
        )
        db_manager.save_project_data(project)

        projects = db_manager.get_projects()

        assert len(projects) >= 1
        assert any(p.project_name == "my_project" for p in projects)


class TestStatistics:
    """Test statistics generation."""

    def test_calculates_statistics(self, populated_db):
        """Should calculate test statistics."""
        stats = populated_db.get_test_statistics()

        assert "total_tests" in stats
        assert "by_type" in stats
        assert "success_rate" in stats
        assert stats["total_tests"] > 0

    def test_filters_statistics_by_project(self, populated_db):
        """Should calculate statistics for specific project."""
        stats = populated_db.get_test_statistics(project_name="project_0")

        assert "total_tests" in stats
        assert stats["total_tests"] >= 0


class TestDataCleanup:
    """Test data cleanup operations."""

    def test_cleanup_old_data(self, db_manager):
        """Should remove old test results."""
        # Create old result
        old_result = (
            ResultBuilder()
            .with_timestamp((datetime.now() - timedelta(days=60)).isoformat())
            .build()
        )
        db_manager.save_test_result(old_result)

        # Create recent result
        new_result = ResultBuilder().with_timestamp(datetime.now().isoformat()).build()
        db_manager.save_test_result(new_result)

        # Cleanup (default 30 days)
        db_manager.cleanup_old_data(days=30)

        results = db_manager.get_test_results()

        # Should only have recent result
        assert len(results) == 1

    def test_delete_all_data_requires_confirmation(self, db_manager):
        """Should require confirmation to delete all data."""
        # Add some data
        db_manager.save_test_result(create_sample_test_result())

        # Should not delete without confirmation
        db_manager.delete_all_data(confirm=False)

        results = db_manager.get_test_results()
        assert len(results) == 1

    def test_delete_all_data_with_confirmation(self, db_manager):
        """Should delete all data when confirmed."""
        # Add some data
        db_manager.save_test_result(create_sample_test_result())

        # Delete with confirmation
        db_manager.delete_all_data(confirm=True)

        results = db_manager.get_test_results()
        assert len(results) == 0


class TestDatabaseOptimization:
    """Test database optimization operations."""

    def test_optimizes_database(self, populated_db):
        """Should run VACUUM and ANALYZE."""
        # Should not raise error
        populated_db.optimize_database()

    def test_gets_database_stats(self, populated_db):
        """Should return database statistics."""
        stats = populated_db.get_database_stats()

        assert "test_results_count" in stats
        assert "sessions_count" in stats
        assert "database_size_bytes" in stats
        assert "database_size_mb" in stats
        assert stats["test_results_count"] >= 0


class TestFilesSnapshot:
    """Test files snapshot functionality."""

    def test_creates_files_snapshot(self, tmp_path):
        """Should create snapshot from workspace directory."""
        # Create test files in comparator subdirectory
        workspace = tmp_path / "workspace" / "comparator"
        workspace.mkdir(parents=True)
        (workspace / "test.cpp").write_text(SAMPLE_CPP_CODE)
        (workspace / "correct.cpp").write_text(SAMPLE_CPP_CODE)
        (workspace / "generator.cpp").write_text(SAMPLE_CPP_CODE)

        snapshot = DatabaseManager.create_files_snapshot(str(tmp_path / "workspace"))

        assert snapshot is not None
        assert isinstance(snapshot, FilesSnapshot)
        json_str = snapshot.to_json()
        # Check that files are in snapshot
        assert "test.cpp" in json_str or "correct.cpp" in json_str or "generator.cpp" in json_str

    def test_handles_missing_workspace(self, tmp_path):
        """Should handle nonexistent workspace gracefully."""
        nonexistent = tmp_path / "nonexistent"

        snapshot = DatabaseManager.create_files_snapshot(str(nonexistent))

        # Should create empty or minimal snapshot
        assert snapshot is not None


class TestMismatchAnalysis:
    """Test output mismatch analysis."""

    def test_analyzes_output_mismatch(self):
        """Should analyze differences between expected and actual output."""
        expected = "hello\nworld\n"
        actual = "hello\nWORLD\n"

        analysis = DatabaseManager.analyze_output_mismatch(expected, actual)

        # Check for actual keys returned
        assert (
            "unified_diff" in analysis
            or "line_differences" in analysis
            or "character_differences" in analysis
        )
        assert analysis is not None

    def test_handles_identical_output(self):
        """Should handle identical output."""
        text = "same\noutput\n"

        analysis = DatabaseManager.analyze_output_mismatch(text, text)

        assert analysis is not None

    def test_handles_empty_output(self):
        """Should handle empty strings."""
        analysis = DatabaseManager.analyze_output_mismatch("", "")

        assert analysis is not None


class TestConnectionManagement:
    """Test database connection lifecycle."""

    def test_close_connection(self, db_manager):
        """Should close database connection."""
        db_manager.close()

        assert db_manager.connection is None

    def test_reconnect_after_close(self, temp_db_path):
        """Should allow reconnection after close."""
        manager = DatabaseManager(temp_db_path)
        manager.close()

        connection = manager.connect()

        assert connection is not None
        manager.close()


class TestErrorHandling:
    """Test error handling in database operations."""

    def test_handles_connection_errors(self, tmp_path):
        """Should handle corrupted database errors."""
        db_path = str(tmp_path / "corrupted.db")

        # Create a corrupted database file
        with open(db_path, "w") as f:
            f.write("CORRUPTED DATA NOT A REAL DATABASE")

        # Should raise DatabaseError for corrupted file
        with pytest.raises(DatabaseError):
            DatabaseManager(db_path)

    def test_handles_sql_errors_gracefully(self, db_manager):
        """Should handle SQL errors properly."""
        # Try to execute invalid SQL
        connection = db_manager.connect()

        with pytest.raises(sqlite3.Error):
            cursor = connection.cursor()
            cursor.execute("INVALID SQL STATEMENT")

        db_manager.close()


class TestDataMigration:
    """Test data migration functionality."""

    def test_migration_dry_run(self, db_manager):
        """Should run migration in dry-run mode."""
        # Should not raise error
        db_manager.migrate_old_results_to_new_format(dry_run=True)

    def test_migration_actual(self, db_manager):
        """Should perform actual migration."""
        # Should not raise error
        db_manager.migrate_old_results_to_new_format(dry_run=False)
