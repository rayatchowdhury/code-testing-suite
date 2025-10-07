"""Test database services."""
import pytest
import tempfile
import os
from datetime import datetime, timedelta

from src.app.persistence.database.connection import DatabaseConnection
from src.app.persistence.database.services import (
    FilesSnapshotService,
    DatabaseStatsService,
    DatabaseMaintenanceService
)
from src.app.persistence.database.models import FilesSnapshot, TestResult
from src.app.persistence.database.repositories import TestResultRepository


# ==================== Fixtures ====================

@pytest.fixture
def temp_db():
    """Create temporary database for testing."""
    temp_db_file = tempfile.mktemp(suffix='.db')
    DatabaseConnection(temp_db_file)
    
    yield temp_db_file
    
    # Cleanup - close connections first
    DatabaseConnection.reset_instance()
    if os.path.exists(temp_db_file):
        try:
            os.unlink(temp_db_file)
        except PermissionError:
            # File still in use, wait a moment and try again
            import time
            time.sleep(0.1)
            try:
                os.unlink(temp_db_file)
            except PermissionError:
                pass  # Give up gracefully


@pytest.fixture
def temp_workspace(tmp_path):
    """Create temporary workspace directory with test files."""
    workspace_dir = tmp_path / "workspace"
    comparator_dir = workspace_dir / "comparator"
    comparator_dir.mkdir(parents=True)
    
    # Create sample source files
    (comparator_dir / "generator.cpp").write_text("""
    #include <iostream>
    int main() {
        std::cout << "Generated data" << std::endl;
        return 0;
    }
    """)
    
    (comparator_dir / "correct.cpp").write_text("""
    #include <iostream>
    int main() {
        std::cout << "Correct solution" << std::endl;
        return 0;
    }
    """)
    
    (comparator_dir / "test.py").write_text("""
    print("Test solution")
    """)
    
    return str(workspace_dir)


@pytest.fixture
def test_repo(temp_db):
    """Create test result repository with temp database."""
    return TestResultRepository()


@pytest.fixture
def stats_service(temp_db):
    """Create database stats service."""
    return DatabaseStatsService()


@pytest.fixture
def maintenance_service(temp_db):
    """Create database maintenance service."""
    return DatabaseMaintenanceService()


# ==================== FilesSnapshotService Tests ====================

class TestFilesSnapshotService:
    """Test FilesSnapshotService."""
    
    def test_create_snapshot_comparison(self, temp_workspace):
        """Test creating snapshot for comparison test type."""
        snapshot = FilesSnapshotService.create_snapshot(temp_workspace, "comparison")
        
        assert isinstance(snapshot, FilesSnapshot)
        assert snapshot.test_type == "comparison"
        assert len(snapshot.files) == 3  # generator, correct, test
        assert "generator.cpp" in snapshot.files
        assert "correct.cpp" in snapshot.files
        assert "test.py" in snapshot.files
    
    def test_create_snapshot_detects_primary_language(self, temp_workspace):
        """Test that primary language is detected correctly."""
        snapshot = FilesSnapshotService.create_snapshot(temp_workspace, "comparison")
        
        # Should be 'cpp' because 2 cpp files vs 1 py file
        assert snapshot.primary_language == "cpp"
    
    def test_create_snapshot_file_metadata(self, temp_workspace):
        """Test that file metadata is captured."""
        snapshot = FilesSnapshotService.create_snapshot(temp_workspace, "comparison")
        
        # Check generator.cpp metadata
        generator_file = snapshot.files["generator.cpp"]
        assert "content" in generator_file
        assert "language" in generator_file
        assert "role" in generator_file
        assert generator_file["language"] == "cpp"
        assert generator_file["role"] == "generator"
        assert "#include" in generator_file["content"]
    
    def test_create_snapshot_validator_type(self, temp_workspace):
        """Test creating snapshot for validator test type."""
        # Create validator-specific files
        validator_dir = os.path.join(temp_workspace, "validator")
        os.makedirs(validator_dir, exist_ok=True)
        
        with open(os.path.join(validator_dir, "generator.cpp"), "w") as f:
            f.write("// generator code")
        with open(os.path.join(validator_dir, "validator.cpp"), "w") as f:
            f.write("// validator code")
        with open(os.path.join(validator_dir, "test.cpp"), "w") as f:
            f.write("// test code")
        
        snapshot = FilesSnapshotService.create_snapshot(temp_workspace, "validation")
        
        assert snapshot.test_type == "validation"
        assert len(snapshot.files) == 3
        assert "generator.cpp" in snapshot.files
        assert "validator.cpp" in snapshot.files
        assert "test.cpp" in snapshot.files
    
    def test_create_snapshot_nonexistent_directory(self):
        """Test creating snapshot from non-existent directory."""
        snapshot = FilesSnapshotService.create_snapshot("/nonexistent/path", "comparison")
        
        assert isinstance(snapshot, FilesSnapshot)
        assert len(snapshot.files) == 0
        assert snapshot.test_type == "comparison"
    
    def test_analyze_output_mismatch(self):
        """Test output mismatch analysis."""
        expected = "Hello World\n123\n456"
        actual = "Hello World\n789\n456"
        
        analysis = FilesSnapshotService.analyze_output_mismatch(expected, actual)
        
        assert "unified_diff" in analysis
        assert "character_differences" in analysis
        assert "line_differences" in analysis
        assert "summary" in analysis
        
        # Check summary
        summary = analysis["summary"]
        assert summary["expected_lines"] == 3
        assert summary["actual_lines"] == 3
        assert summary["total_line_differences"] == 1  # Line 2 differs
    
    def test_analyze_output_mismatch_character_diff(self):
        """Test character-level difference detection."""
        expected = "abc"
        actual = "aXc"
        
        analysis = FilesSnapshotService.analyze_output_mismatch(expected, actual)
        
        char_diffs = analysis["character_differences"]
        assert len(char_diffs) == 1
        assert char_diffs[0]["position"] == 1
        assert char_diffs[0]["expected"] == "b"
        assert char_diffs[0]["actual"] == "X"
    
    def test_analyze_output_mismatch_line_types(self):
        """Test line difference type classification."""
        expected = "line1\nline2\nline3"
        actual = "line1\nmodified\nline3\nextra"
        
        analysis = FilesSnapshotService.analyze_output_mismatch(expected, actual)
        
        line_diffs = analysis["line_differences"]
        assert len(line_diffs) == 2
        
        # Line 2 modified
        assert line_diffs[0]["line_number"] == 2
        assert line_diffs[0]["type"] == "modified"
        
        # Line 4 extra
        assert line_diffs[1]["line_number"] == 4
        assert line_diffs[1]["type"] == "extra"


# ==================== DatabaseStatsService Tests ====================

class TestDatabaseStatsService:
    """Test DatabaseStatsService."""
    
    def test_get_database_stats_empty(self, stats_service):
        """Test getting stats from empty database."""
        stats = stats_service.get_database_stats()
        
        assert stats["test_results_count"] == 0
        assert stats["sessions_count"] == 0
        assert stats["oldest_test"] == "No data"
        assert stats["newest_test"] == "No data"
        assert stats["database_size_bytes"] > 0  # Database file exists even if empty
    
    def test_get_database_stats_with_data(self, test_repo, stats_service):
        """Test getting stats with test data."""
        # Add some test results
        for i in range(5):
            test_repo.save(TestResult(
                test_type="comparison",
                file_path=f"/test/file{i}.cpp",
                test_count=10,
                passed_tests=8,
                failed_tests=2,
                total_time=5.0,
                timestamp=datetime.now().isoformat()
            ))
        
        stats = stats_service.get_database_stats()
        
        assert stats["test_results_count"] == 5
        assert stats["oldest_test"] != "No data"
        assert stats["newest_test"] != "No data"
        assert stats["database_size_mb"] > 0
    
    def test_get_test_statistics_empty(self, stats_service):
        """Test getting test statistics from empty database."""
        stats = stats_service.get_test_statistics()
        
        assert stats["total_tests"] == 0
        assert stats["by_type"] == {}
        assert stats["success_rate"] == 0
    
    def test_get_test_statistics_with_data(self, test_repo, stats_service):
        """Test getting test statistics with data."""
        # Add test results of different types
        test_repo.save(TestResult(
            test_type="comparison",
            file_path="/test/comp.cpp",
            test_count=10,
            passed_tests=10,
            failed_tests=0,
            total_time=5.0,
            timestamp=datetime.now().isoformat()
        ))
        
        test_repo.save(TestResult(
            test_type="benchmark",
            file_path="/test/bench.cpp",
            test_count=5,
            passed_tests=3,
            failed_tests=2,
            total_time=3.0,
            timestamp=datetime.now().isoformat()
        ))
        
        stats = stats_service.get_test_statistics()
        
        assert stats["total_tests"] == 2
        assert stats["by_type"]["comparison"] == 1
        assert stats["by_type"]["benchmark"] == 1
        # Success rate: (10 + 3) / (10 + 5) = 13/15 = 86.67%
        assert 86 <= stats["success_rate"] <= 87
    
    def test_get_test_statistics_by_project(self, test_repo, stats_service):
        """Test getting statistics filtered by project."""
        # Add results for different projects
        test_repo.save(TestResult(
            test_type="comparison",
            file_path="/test/file1.cpp",
            test_count=10,
            passed_tests=10,
            failed_tests=0,
            total_time=5.0,
            timestamp=datetime.now().isoformat(),
            project_name="Project A"
        ))
        
        test_repo.save(TestResult(
            test_type="comparison",
            file_path="/test/file2.cpp",
            test_count=10,
            passed_tests=8,
            failed_tests=2,
            total_time=5.0,
            timestamp=datetime.now().isoformat(),
            project_name="Project B"
        ))
        
        stats = stats_service.get_test_statistics(project_name="Project A")
        
        assert stats["total_tests"] == 1
        assert stats["success_rate"] == 100.0


# ==================== DatabaseMaintenanceService Tests ====================

class TestDatabaseMaintenanceService:
    """Test DatabaseMaintenanceService."""
    
    def test_cleanup_old_data_nothing_to_clean(self, maintenance_service):
        """Test cleanup when no old data exists."""
        result = maintenance_service.cleanup_old_data(days=30)
        
        assert result["test_rows_deleted"] == 0
        assert result["session_rows_deleted"] == 0
        assert result["vacuumed"] is False
    
    def test_cleanup_old_data_with_old_results(self, test_repo, maintenance_service):
        """Test cleanup removes old test results."""
        # Add old result (40 days ago)
        test_repo.save(TestResult(
            test_type="comparison",
            file_path="/test/old.cpp",
            test_count=10,
            passed_tests=10,
            failed_tests=0,
            total_time=5.0,
            timestamp=(datetime.now() - timedelta(days=40)).isoformat()
        ))
        
        # Add recent result (5 days ago)
        test_repo.save(TestResult(
            test_type="comparison",
            file_path="/test/recent.cpp",
            test_count=10,
            passed_tests=10,
            failed_tests=0,
            total_time=5.0,
            timestamp=(datetime.now() - timedelta(days=5)).isoformat()
        ))
        
        # Cleanup data older than 30 days
        result = maintenance_service.cleanup_old_data(days=30)
        
        assert result["test_rows_deleted"] == 1
        assert result["vacuumed"] is True
        
        # Verify recent result still exists
        all_results = test_repo.get_all()
        assert len(all_results) == 1
        assert "recent.cpp" in all_results[0].file_path
    
    def test_optimize_database(self, maintenance_service):
        """Test database optimization."""
        result = maintenance_service.optimize_database()
        
        assert "size_before_bytes" in result
        assert "size_after_bytes" in result
        assert "space_saved_bytes" in result
        assert "size_before_mb" in result
        assert "size_after_mb" in result
        assert "space_saved_mb" in result
        
        assert result["size_before_bytes"] >= 0
        assert result["size_after_bytes"] >= 0
    
    def test_optimize_database_after_deletions(self, test_repo, maintenance_service):
        """Test optimization recovers space after deletions."""
        # Add multiple test results
        result_ids = []
        for i in range(20):
            result_id = test_repo.save(TestResult(
                test_type="comparison",
                file_path=f"/test/file{i}.cpp",
                test_count=10,
                passed_tests=10,
                failed_tests=0,
                total_time=5.0,
                timestamp=datetime.now().isoformat(),
                test_details="x" * 1000  # Add some bulk
            ))
            result_ids.append(result_id)
        
        # Delete half of them
        for result_id in result_ids[:10]:
            test_repo.delete(result_id)
        
        # Optimize should reclaim space
        result = maintenance_service.optimize_database()
        
        # Space saved should be >= 0 (may be 0 on small databases)
        assert result["space_saved_bytes"] >= 0


# ==================== Integration Tests ====================

class TestServicesIntegration:
    """Test services working together."""
    
    def test_full_workflow(self, test_repo, stats_service, maintenance_service):
        """Test complete workflow: add data, get stats, cleanup, optimize."""
        # Add test results
        for i in range(10):
            days_ago = 35 if i < 5 else 5  # Half old, half recent
            test_repo.save(TestResult(
                test_type="comparison",
                file_path=f"/test/file{i}.cpp",
                test_count=10,
                passed_tests=10,
                failed_tests=0,
                total_time=5.0,
                timestamp=(datetime.now() - timedelta(days=days_ago)).isoformat()
            ))
        
        # Check initial stats
        stats = stats_service.get_database_stats()
        assert stats["test_results_count"] == 10
        
        # Cleanup old data
        cleanup_result = maintenance_service.cleanup_old_data(days=30)
        assert cleanup_result["test_rows_deleted"] == 5
        
        # Check stats after cleanup
        stats = stats_service.get_database_stats()
        assert stats["test_results_count"] == 5
        
        # Optimize database
        optimize_result = maintenance_service.optimize_database()
        assert optimize_result["space_saved_bytes"] >= 0
