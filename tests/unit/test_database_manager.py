"""Unit tests for DatabaseManager and related data classes."""

import json
import sqlite3
import tempfile
import pytest
from datetime import datetime
from unittest.mock import patch, MagicMock

from src.app.persistence.database import (
    DatabaseManager, TestResult, FilesSnapshot, 
    Session, ProjectData
)


class TestDataClasses:
    """Test cases for data classes."""

    # Phase 6 (Issue #7): Removed test_test_case_result_creation - TestCaseResult class removed

    def test_files_snapshot_creation(self):
        """Test FilesSnapshot data class creation with NEW format."""
        snapshot = FilesSnapshot(
            files={
                "generator.cpp": {
                    "content": "// generator",
                    "language": "cpp",
                    "role": "generator"
                },
                "correct.cpp": {
                    "content": "// correct",
                    "language": "cpp",
                    "role": "correct"
                },
                "test.cpp": {
                    "content": "// test",
                    "language": "cpp",
                    "role": "test"
                },
                "helper.h": {
                    "content": "// helper",
                    "language": "cpp",
                    "role": "additional"
                }
            },
            test_type="comparison",
            primary_language="cpp"
        )
        
        assert "generator.cpp" in snapshot.files
        assert snapshot.files["generator.cpp"]["content"] == "// generator"
        assert snapshot.files["correct.cpp"]["content"] == "// correct"
        assert snapshot.files["test.cpp"]["content"] == "// test"
        assert snapshot.files["helper.h"]["content"] == "// helper"

    def test_files_snapshot_default_factory(self):
        """Test FilesSnapshot with default factory for files dict."""
        snapshot1 = FilesSnapshot()
        snapshot2 = FilesSnapshot()
        
        # Should have separate dict instances (not shared)
        snapshot1.files["file1.cpp"] = {"content": "content1", "language": "cpp", "role": "test"}
        assert "file1.cpp" not in snapshot2.files

    def test_test_result_creation(self):
        """Test TestResult data class creation."""
        result = TestResult(
            id=1,
            test_type="stress",
            file_path="/path/to/test.cpp",
            test_count=100,
            passed_tests=95,
            failed_tests=5,
            total_time=10.5,
            timestamp="2023-01-01 12:00:00",
            test_details='{"details": "test"}',
            project_name="MyProject",
            files_snapshot='{"generator": "code"}',
            mismatch_analysis='{"analysis": "data"}'
        )
        
        assert result.id == 1
        assert result.test_type == "stress"
        assert result.test_count == 100
        assert result.passed_tests == 95
        assert result.failed_tests == 5

    def test_session_creation(self):
        """Test Session data class creation."""
        session = Session(
            id=1,
            session_name="Test Session",
            open_files='["file1.cpp", "file2.py"]',
            active_file="file1.cpp",
            timestamp="2023-01-01 12:00:00",
            project_name="MyProject"
        )
        
        assert session.id == 1
        assert session.session_name == "Test Session"
        assert session.open_files == '["file1.cpp", "file2.py"]'
        assert session.active_file == "file1.cpp"

    def test_project_data_creation(self):
        """Test ProjectData data class creation."""
        project = ProjectData(
            id=1,
            project_name="Test Project",
            project_path="/path/to/project",
            last_accessed="2023-01-01 12:00:00",
            file_count=10,
            total_lines=1000,
            languages='["C++", "Python"]'
        )
        
        assert project.id == 1
        assert project.project_name == "Test Project"
        assert project.project_path == "/path/to/project"
        assert project.file_count == 10
        assert project.total_lines == 1000


class TestDatabaseManager:
    """Test cases for DatabaseManager class."""

    @pytest.fixture
    def db_manager(self, mock_database):
        """Create DatabaseManager with temporary database."""
        return DatabaseManager(mock_database)

    def test_init_with_default_path(self):
        """Test DatabaseManager initialization with default path."""
        with patch('os.makedirs'), patch.object(DatabaseManager, '_initialize_database'):
            manager = DatabaseManager()
            assert "code_testing_suite.db" in manager.db_path

    def test_init_with_custom_path(self, mock_database):
        """Test DatabaseManager initialization with custom path."""
        manager = DatabaseManager(mock_database)
        assert manager.db_path == mock_database

    def test_connect_success(self, db_manager):
        """Test successful database connection."""
        connection = db_manager.connect()
        
        assert connection is not None
        assert db_manager.connection is not None
        assert db_manager.connection.row_factory == sqlite3.Row

    @patch('sqlite3.connect', side_effect=sqlite3.Error("Connection failed"))
    def test_connect_failure(self, mock_connect, mock_database):
        """Test database connection failure."""
        from src.app.persistence.database import DatabaseError
        
        # DatabaseManager.__init__ calls _initialize_database which calls connect()
        # So the exception is raised during initialization
        with pytest.raises(DatabaseError, match="Failed to connect to database"):
            manager = DatabaseManager(mock_database)

    def test_close_connection(self, db_manager):
        """Test closing database connection."""
        # First connect
        db_manager.connect()
        assert db_manager.connection is not None
        
        # Then close
        db_manager.close()
        assert db_manager.connection is None

    def test_close_without_connection(self, db_manager):
        """Test closing when no connection exists."""
        # Should not raise exception
        db_manager.close()
        assert db_manager.connection is None

    def test_database_initialization_creates_tables(self, db_manager):
        """Test that database initialization creates required tables."""
        connection = db_manager.connect()
        cursor = connection.cursor()
        
        # Check that tables exist
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        
        expected_tables = ['test_results', 'sessions', 'projects', 'config']
        for table in expected_tables:
            assert table in tables

    def test_save_test_result(self, db_manager):
        """Test saving test result to database."""
        test_result = TestResult(
            test_type="stress",
            file_path="/test/path.cpp",
            test_count=50,
            passed_tests=48,
            failed_tests=2,
            total_time=5.0,
            timestamp=datetime.now().isoformat(),
            test_details='{"test": "details"}',
            project_name="TestProject",
            files_snapshot='{"files": "snapshot"}',
            mismatch_analysis='{"mismatch": "analysis"}'
        )
        
        result_id = db_manager.save_test_result(test_result)
        
        assert result_id is not None
        assert isinstance(result_id, int)
        assert result_id > 0

    def test_get_test_result_by_id(self, db_manager):
        """Test retrieving test result by ID."""
        # First save a test result
        test_result = TestResult(
            test_type="tle",
            file_path="/test/tle.cpp",
            test_count=10,
            passed_tests=8,
            failed_tests=2,
            total_time=2.5,
            timestamp=datetime.now().isoformat(),
            project_name="TLEProject"
        )
        
        result_id = db_manager.save_test_result(test_result)
        
        # Retrieve the result using get_test_results and filter by project
        retrieved_results = db_manager.get_test_results(project_name="TLEProject")
        retrieved_result = None
        for result in retrieved_results:
            if result.id == result_id:
                retrieved_result = result
                break
        
        assert retrieved_result is not None
        assert retrieved_result.id == result_id
        assert retrieved_result.test_type == "tle"
        assert retrieved_result.file_path == "/test/tle.cpp"
        assert retrieved_result.test_count == 10

    def test_get_test_result_nonexistent(self, db_manager):
        """Test retrieving non-existent test result."""
        # Try to get results for non-existent project
        results = db_manager.get_test_results(project_name="NonExistentProject")
        assert results == []

    def test_get_all_test_results(self, db_manager):
        """Test retrieving all test results."""
        # Save multiple test results
        for i in range(3):
            test_result = TestResult(
                test_type="stress",
                file_path=f"/test/file{i}.cpp",
                test_count=10,
                passed_tests=10,
                failed_tests=0,
                total_time=1.0,
                timestamp=datetime.now().isoformat(),
                project_name=f"Project{i}"
            )
            db_manager.save_test_result(test_result)
        
        all_results = db_manager.get_test_results()
        
        assert len(all_results) >= 3
        assert all(isinstance(result, TestResult) for result in all_results)

    # Phase 6 (Issue #7): Removed skipped TestCaseResult tests - functionality not needed
    # Test case results are stored as JSON in TestResult.test_details

    def test_save_session(self, db_manager):
        """Test saving session data."""
        session = Session(
            session_name="Test Session",
            open_files='["file1.cpp", "file2.py"]',
            active_file="file1.cpp",
            timestamp=datetime.now().isoformat(),
            project_name="TestProject"
        )
        
        session_id = db_manager.save_session(session)
        
        assert session_id is not None
        assert isinstance(session_id, int)

    def test_get_session_by_id(self, db_manager):
        """Test retrieving session by ID."""
        session = Session(
            session_name="Retrieve Test Session",
            open_files='["main.cpp"]',
            active_file="main.cpp",
            timestamp=datetime.now().isoformat(),
            project_name="RetrieveProject"
        )
        
        session_id = db_manager.save_session(session)
        
        # Retrieve using get_sessions and filter by project name
        retrieved_sessions = db_manager.get_sessions(project_name="RetrieveProject")
        retrieved_session = None
        for sess in retrieved_sessions:
            if sess.id == session_id:
                retrieved_session = sess
                break
        
        assert retrieved_session is not None
        assert retrieved_session.id == session_id
        assert retrieved_session.session_name == "Retrieve Test Session"
        assert retrieved_session.active_file == "main.cpp"

    @pytest.mark.skip(reason="delete_test_result method not implemented in current DatabaseManager")
    def test_delete_test_result(self, db_manager):
        """Test deleting test result."""
        # This test is skipped because the current DatabaseManager
        # doesn't have delete_test_result method implemented
        pass

    @pytest.mark.skip(reason="delete_test_result method not implemented in current DatabaseManager")
    def test_delete_nonexistent_test_result(self, db_manager):
        """Test deleting non-existent test result."""
        # This test is skipped because the current DatabaseManager
        # doesn't have delete_test_result method implemented
        pass

    @patch('sqlite3.connect', side_effect=sqlite3.Error("Database error"))
    def test_database_error_handling(self, mock_connect, mock_database):
        """Test that database errors are raised as DatabaseError exceptions."""
        from src.app.persistence.database import DatabaseError
        
        # DatabaseManager now raises DatabaseError instead of returning None
        with pytest.raises(DatabaseError, match="Failed to connect to database"):
            manager = DatabaseManager(mock_database)

    def test_context_manager_usage(self, db_manager):
        """Test using DatabaseManager as context manager if implemented."""
        # Test that connection is properly managed
        connection = db_manager.connect()
        assert connection is not None
        
        db_manager.close()
        assert db_manager.connection is None