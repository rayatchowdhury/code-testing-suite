"""Test backward compatibility of DatabaseManager facade."""
import pytest
import tempfile
import os
from datetime import datetime, timedelta

from src.app.persistence.database import (
    DatabaseManager,
    TestResult,
    Session,
    FilesSnapshot,
    DatabaseConnection
)


@pytest.fixture
def temp_db():
    """Create temporary database for testing."""
    temp_db_file = tempfile.mktemp(suffix='.db')
    DatabaseConnection(temp_db_file)
    
    yield temp_db_file
    
    # Cleanup
    DatabaseConnection.reset_instance()
    if os.path.exists(temp_db_file):
        try:
            os.unlink(temp_db_file)
        except PermissionError:
            import time
            time.sleep(0.1)
            try:
                os.unlink(temp_db_file)
            except PermissionError:
                pass


@pytest.fixture
def db_manager(temp_db):
    """Create DatabaseManager with temp database."""
    return DatabaseManager(temp_db)


class TestBackwardCompatibility:
    """Test that old DatabaseManager API still works."""
    
    def test_imports_work(self):
        """Test that all old imports still work."""
        # These should all import without errors
        from src.app.persistence.database import DatabaseManager
        from src.app.persistence.database import TestResult
        from src.app.persistence.database import Session
        from src.app.persistence.database import FilesSnapshot
        
        assert DatabaseManager is not None
        assert TestResult is not None
        assert Session is not None
        assert FilesSnapshot is not None
    
    def test_database_manager_init(self, temp_db):
        """Test DatabaseManager initialization."""
        db = DatabaseManager(temp_db)
        
        assert db.db is not None
        assert db.test_repo is not None
        assert db.stats_service is not None
        assert db.maintenance_service is not None
        assert db.db_path == temp_db
    
    def test_save_and_get_test_results(self, db_manager):
        """Test save_test_result and get_test_results methods."""
        # Create test result
        result = TestResult(
            test_type="comparison",
            file_path="/test/file.cpp",
            test_count=10,
            passed_tests=8,
            failed_tests=2,
            total_time=5.5,
            timestamp=datetime.now().isoformat(),
            project_name="Test Project"
        )
        
        # Save using old API
        result_id = db_manager.save_test_result(result)
        assert result_id > 0
        
        # Get using old API
        results = db_manager.get_test_results()
        assert len(results) == 1
        assert results[0].test_type == "comparison"
        assert results[0].passed_tests == 8
    
    def test_get_test_results_with_filters(self, db_manager):
        """Test get_test_results with various filters."""
        # Add multiple test results
        for i in range(5):
            db_manager.save_test_result(TestResult(
                test_type="comparison" if i % 2 == 0 else "benchmark",
                file_path=f"/test/file{i}.cpp",
                test_count=10,
                passed_tests=10,
                failed_tests=0,
                total_time=1.0,
                timestamp=datetime.now().isoformat(),
                project_name=f"Project{i % 2}"
            ))
        
        # Filter by test type
        comparison_results = db_manager.get_test_results(test_type="comparison")
        assert len(comparison_results) == 3
        
        # Filter by project name
        project0_results = db_manager.get_test_results(project_name="Project0")
        assert len(project0_results) == 3
    
    def test_delete_test_result(self, db_manager):
        """Test delete_test_result method."""
        # Add a result
        result = TestResult(
            test_type="comparison",
            file_path="/test/file.cpp",
            test_count=1,
            passed_tests=1,
            failed_tests=0,
            total_time=1.0,
            timestamp=datetime.now().isoformat()
        )
        result_id = db_manager.save_test_result(result)
        
        # Delete it
        success = db_manager.delete_test_result(result_id)
        assert success is True
        
        # Verify it's gone
        results = db_manager.get_test_results()
        assert len(results) == 0
    
    def test_delete_all_data(self, db_manager):
        """Test delete_all_data method."""
        # Add multiple results
        for i in range(3):
            db_manager.save_test_result(TestResult(
                test_type="comparison",
                file_path=f"/test/file{i}.cpp",
                test_count=1,
                passed_tests=1,
                failed_tests=0,
                total_time=1.0,
                timestamp=datetime.now().isoformat()
            ))
        
        # Try without confirmation (should fail)
        success = db_manager.delete_all_data(confirm=False)
        assert success is False
        
        # With confirmation (should work)
        success = db_manager.delete_all_data(confirm=True)
        assert success is True
        
        # Verify all gone
        results = db_manager.get_test_results()
        assert len(results) == 0
    
    def test_get_database_stats(self, db_manager):
        """Test get_database_stats method."""
        # Add some data
        db_manager.save_test_result(TestResult(
            test_type="comparison",
            file_path="/test/file.cpp",
            test_count=10,
            passed_tests=8,
            failed_tests=2,
            total_time=5.5,
            timestamp=datetime.now().isoformat()
        ))
        
        # Get stats
        stats = db_manager.get_database_stats()
        
        assert "test_results_count" in stats
        assert stats["test_results_count"] == 1
        assert "database_size_bytes" in stats
        assert stats["database_size_bytes"] > 0
    
    def test_get_test_statistics(self, db_manager):
        """Test get_test_statistics method."""
        # Add results
        db_manager.save_test_result(TestResult(
            test_type="comparison",
            file_path="/test/file1.cpp",
            test_count=10,
            passed_tests=10,
            failed_tests=0,
            total_time=5.0,
            timestamp=datetime.now().isoformat(),
            project_name="ProjectA"
        ))
        
        db_manager.save_test_result(TestResult(
            test_type="benchmark",
            file_path="/test/file2.cpp",
            test_count=5,
            passed_tests=3,
            failed_tests=2,
            total_time=3.0,
            timestamp=datetime.now().isoformat(),
            project_name="ProjectB"
        ))
        
        # Get statistics
        stats = db_manager.get_test_statistics()
        
        assert stats["total_tests"] == 2
        assert "comparison" in stats["by_type"]
        assert "benchmark" in stats["by_type"]
        assert stats["success_rate"] > 0
    
    def test_cleanup_old_data(self, db_manager):
        """Test cleanup_old_data method."""
        # Add old and recent results
        db_manager.save_test_result(TestResult(
            test_type="comparison",
            file_path="/test/old.cpp",
            test_count=1,
            passed_tests=1,
            failed_tests=0,
            total_time=1.0,
            timestamp=(datetime.now() - timedelta(days=40)).isoformat()
        ))
        
        db_manager.save_test_result(TestResult(
            test_type="comparison",
            file_path="/test/recent.cpp",
            test_count=1,
            passed_tests=1,
            failed_tests=0,
            total_time=1.0,
            timestamp=datetime.now().isoformat()
        ))
        
        # Cleanup old data
        result = db_manager.cleanup_old_data(days=30)
        
        assert result["test_rows_deleted"] == 1
        
        # Verify only recent remains
        results = db_manager.get_test_results()
        assert len(results) == 1
        assert "recent" in results[0].file_path
    
    def test_optimize_database(self, db_manager):
        """Test optimize_database method."""
        # Add and delete some data to create optimization opportunity
        result_ids = []
        for i in range(10):
            result_id = db_manager.save_test_result(TestResult(
                test_type="comparison",
                file_path=f"/test/file{i}.cpp",
                test_count=1,
                passed_tests=1,
                failed_tests=0,
                total_time=1.0,
                timestamp=datetime.now().isoformat()
            ))
            result_ids.append(result_id)
        
        # Delete half
        for result_id in result_ids[:5]:
            db_manager.delete_test_result(result_id)
        
        # Optimize
        result = db_manager.optimize_database()
        
        assert "size_before_bytes" in result
        assert "size_after_bytes" in result
        assert "space_saved_bytes" in result
    
    def test_static_methods(self):
        """Test static methods work."""
        # Test analyze_output_mismatch
        analysis = DatabaseManager.analyze_output_mismatch("hello\nworld", "hello\ntest")
        
        assert "unified_diff" in analysis
        assert "line_differences" in analysis
        assert "summary" in analysis
        assert analysis["summary"]["total_line_differences"] == 1
    
    def test_not_implemented_methods(self, db_manager):
        """Test that not-yet-migrated methods raise NotImplementedError."""
        session = Session(
            timestamp=datetime.now().isoformat(),
            project_name="Test"
        )
        
        # These should raise NotImplementedError
        with pytest.raises(NotImplementedError):
            db_manager.save_session(session)
        
        with pytest.raises(NotImplementedError):
            db_manager.get_sessions()
        
        with pytest.raises(NotImplementedError):
            db_manager.save_project_data(None)
        
        with pytest.raises(NotImplementedError):
            db_manager.get_projects()
    
    def test_deprecated_methods(self, db_manager):
        """Test deprecated methods don't crash."""
        # connect/close should work but do nothing
        conn = db_manager.connect()
        db_manager.close()
        
        # migrate should return skipped status
        result = db_manager.migrate_old_results_to_new_format()
        assert result["status"] == "skipped"


class TestNewAPIAccessibility:
    """Test that new architecture is also accessible."""
    
    def test_can_import_repositories(self):
        """Test importing repositories directly."""
        from src.app.persistence.database import TestResultRepository
        from src.app.persistence.database import BaseRepository
        
        assert TestResultRepository is not None
        assert BaseRepository is not None
    
    def test_can_import_services(self):
        """Test importing services directly."""
        from src.app.persistence.database import FilesSnapshotService
        from src.app.persistence.database import DatabaseStatsService
        from src.app.persistence.database import DatabaseMaintenanceService
        
        assert FilesSnapshotService is not None
        assert DatabaseStatsService is not None
        assert DatabaseMaintenanceService is not None
    
    def test_can_import_connection(self):
        """Test importing connection directly."""
        from src.app.persistence.database import DatabaseConnection
        
        assert DatabaseConnection is not None
    
    def test_can_use_new_api_directly(self, temp_db):
        """Test using new architecture directly."""
        from src.app.persistence.database import TestResultRepository
        
        repo = TestResultRepository()
        
        result = TestResult(
            test_type="comparison",
            file_path="/test/file.cpp",
            test_count=10,
            passed_tests=10,
            failed_tests=0,
            total_time=5.0,
            timestamp=datetime.now().isoformat()
        )
        
        result_id = repo.save(result)
        assert result_id > 0
        
        retrieved = repo.get_by_id(result_id)
        assert retrieved is not None
        assert retrieved.test_type == "comparison"
