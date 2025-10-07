"""Test TestResult repository.

Comprehensive tests for TestResultRepository covering all CRUD operations,
filtering, edge cases, and error handling.

Phase 5: Migrate TestResult Operations
"""

import pytest
import tempfile
import os
from datetime import datetime, timedelta

from src.app.persistence.database.repositories.test_result_repository import TestResultRepository
from src.app.persistence.database.models import TestResult
from src.app.persistence.database.connection import DatabaseConnection
from src.app.persistence.database.constants import STATUS_PASSED, STATUS_FAILED


# ============================================================================
# Test Fixtures
# ============================================================================

@pytest.fixture
def temp_db():
    """Create temporary database for testing."""
    temp_file = tempfile.mktemp(suffix='.db')
    DatabaseConnection(temp_file)
    
    yield temp_file
    
    # Cleanup
    try:
        os.unlink(temp_file)
    except PermissionError:
        pass  # Windows may hold lock
    DatabaseConnection.reset_instance()


@pytest.fixture
def repo(temp_db):
    """Create test repository with temp database."""
    return TestResultRepository()


# ============================================================================
# Test Cases
# ============================================================================

class TestSaveAndRetrieve:
    """Test save and retrieve operations."""
    
    def test_save_new_result(self, repo):
        """Test saving a new test result."""
        result = TestResult(
            test_type="comparison",
            file_path="/test/solution.cpp",
            test_count=10,
            passed_tests=8,
            failed_tests=2,
            total_time=5.5,
            timestamp=datetime.now().isoformat(),
            project_name="Test Project"
        )
        
        result_id = repo.save(result)
        
        assert result_id > 0
        assert isinstance(result_id, int)
    
    def test_save_with_automatic_timestamp(self, repo):
        """Test that timestamp is automatically set if None."""
        result = TestResult(
            test_type="comparison",
            file_path="/test/solution.cpp",
            test_count=1,
            passed_tests=1,
            failed_tests=0,
            total_time=1.0,
            timestamp=None  # Will be set automatically
        )
        
        result_id = repo.save(result)
        retrieved = repo.get_by_id(result_id)
        
        assert retrieved.timestamp is not None
        assert len(retrieved.timestamp) > 0
    
    def test_save_and_get_by_id(self, repo):
        """Test saving and retrieving by ID."""
        result = TestResult(
            test_type="comparison",
            file_path="/test/file.cpp",
            test_count=10,
            passed_tests=8,
            failed_tests=2,
            total_time=5.5,
            timestamp=datetime.now().isoformat(),
            project_name="Test Project",
            test_details="Some details",
            files_snapshot="{}",
            mismatch_analysis="No mismatch"
        )
        
        # Save
        result_id = repo.save(result)
        
        # Retrieve
        retrieved = repo.get_by_id(result_id)
        
        assert retrieved is not None
        assert retrieved.id == result_id
        assert retrieved.test_type == "comparison"
        assert retrieved.file_path == "/test/file.cpp"
        assert retrieved.test_count == 10
        assert retrieved.passed_tests == 8
        assert retrieved.failed_tests == 2
        assert retrieved.total_time == 5.5
        assert retrieved.project_name == "Test Project"
        assert retrieved.test_details == "Some details"
        assert retrieved.files_snapshot == "{}"
        assert retrieved.mismatch_analysis == "No mismatch"
    
    def test_get_by_id_not_found(self, repo):
        """Test get_by_id with non-existent ID."""
        result = repo.get_by_id(9999)
        assert result is None
    
    def test_save_with_optional_fields_empty(self, repo):
        """Test saving result with optional fields as None."""
        result = TestResult(
            test_type="benchmark",
            file_path="/test/perf.cpp",
            test_count=5,
            passed_tests=5,
            failed_tests=0,
            total_time=10.0,
            timestamp=datetime.now().isoformat(),
            project_name=None,
            test_details=None,
            files_snapshot=None,
            mismatch_analysis=None
        )
        
        result_id = repo.save(result)
        retrieved = repo.get_by_id(result_id)
        
        assert retrieved.project_name == ""
        assert retrieved.test_details == ""
        assert retrieved.files_snapshot == ""
        assert retrieved.mismatch_analysis == ""


class TestGetAllWithFilters:
    """Test get_all with various filters."""
    
    @pytest.fixture(autouse=True)
    def setup_test_data(self, repo):
        """Create test data for filtering tests."""
        # Create diverse test results
        test_data = [
            # Comparison tests
            TestResult(
                test_type="comparison",
                file_path="/project1/solution.cpp",
                test_count=10,
                passed_tests=10,
                failed_tests=0,
                total_time=5.0,
                timestamp=(datetime.now() - timedelta(days=1)).isoformat(),
                project_name="Project1"
            ),
            TestResult(
                test_type="comparison",
                file_path="/project1/solution2.cpp",
                test_count=10,
                passed_tests=8,
                failed_tests=2,
                total_time=6.0,
                timestamp=(datetime.now() - timedelta(days=2)).isoformat(),
                project_name="Project1"
            ),
            # Benchmark tests
            TestResult(
                test_type="benchmark",
                file_path="/project2/fast.cpp",
                test_count=5,
                passed_tests=5,
                failed_tests=0,
                total_time=2.0,
                timestamp=(datetime.now() - timedelta(days=3)).isoformat(),
                project_name="Project2"
            ),
            TestResult(
                test_type="benchmark",
                file_path="/project2/slow.cpp",
                test_count=5,
                passed_tests=3,
                failed_tests=2,
                total_time=8.0,
                timestamp=(datetime.now() - timedelta(days=10)).isoformat(),
                project_name="Project2"
            ),
            # Validator test
            TestResult(
                test_type="validator",
                file_path="/project3/checker.py",
                test_count=20,
                passed_tests=20,
                failed_tests=0,
                total_time=3.0,
                timestamp=(datetime.now() - timedelta(days=5)).isoformat(),
                project_name="Project3"
            ),
        ]
        
        for data in test_data:
            repo.save(data)
    
    def test_get_all_no_filters(self, repo):
        """Test get_all without filters."""
        results = repo.get_all()
        assert len(results) == 5
    
    def test_filter_by_test_type(self, repo):
        """Test filtering by test type."""
        comparison_results = repo.get_all(test_type="comparison")
        assert len(comparison_results) == 2
        assert all(r.test_type == "comparison" for r in comparison_results)
        
        benchmark_results = repo.get_all(test_type="benchmark")
        assert len(benchmark_results) == 2
        assert all(r.test_type == "benchmark" for r in benchmark_results)
        
        validator_results = repo.get_all(test_type="validator")
        assert len(validator_results) == 1
        assert validator_results[0].test_type == "validator"
    
    def test_filter_by_project_name(self, repo):
        """Test filtering by project name."""
        project1_results = repo.get_all(project_name="Project1")
        assert len(project1_results) == 2
        assert all("Project1" in r.project_name for r in project1_results)
        
        project2_results = repo.get_all(project_name="Project2")
        assert len(project2_results) == 2
        assert all("Project2" in r.project_name for r in project2_results)
    
    def test_filter_by_project_name_partial(self, repo):
        """Test project name filter with partial match."""
        # Should match "Project1", "Project2", "Project3"
        all_projects = repo.get_all(project_name="Project")
        assert len(all_projects) == 5
    
    def test_filter_by_days(self, repo):
        """Test filtering by days."""
        # Last 7 days (should get 4 results, excluding the 10-day old one)
        recent_results = repo.get_all(days=7)
        assert len(recent_results) == 4
        
        # Last 2 days (should get 2 results)
        very_recent = repo.get_all(days=2)
        assert len(very_recent) == 2
        
        # Last 1 day (should get 1 result)
        today = repo.get_all(days=1)
        assert len(today) == 1
    
    def test_filter_by_file_name(self, repo):
        """Test filtering by file name."""
        cpp_files = repo.get_all(file_name=".cpp")
        assert len(cpp_files) == 4
        assert all(".cpp" in r.file_path for r in cpp_files)
        
        py_files = repo.get_all(file_name=".py")
        assert len(py_files) == 1
        assert ".py" in py_files[0].file_path
        
        solution_files = repo.get_all(file_name="solution")
        assert len(solution_files) == 2
    
    def test_filter_by_status_passed(self, repo):
        """Test filtering by passed status."""
        passed_results = repo.get_all(status=STATUS_PASSED)
        assert len(passed_results) == 3
        assert all(r.passed_tests == r.test_count for r in passed_results)
        assert all(r.failed_tests == 0 for r in passed_results)
    
    def test_filter_by_status_failed(self, repo):
        """Test filtering by failed status."""
        failed_results = repo.get_all(status=STATUS_FAILED)
        assert len(failed_results) == 2
        assert all(r.failed_tests > 0 for r in failed_results)
    
    def test_combined_filters(self, repo):
        """Test combining multiple filters."""
        # Comparison tests from Project1 that passed
        results = repo.get_all(
            test_type="comparison",
            project_name="Project1",
            status=STATUS_PASSED
        )
        assert len(results) == 1
        assert results[0].test_type == "comparison"
        assert "Project1" in results[0].project_name
        assert results[0].passed_tests == results[0].test_count
        
        # Recent benchmark tests
        results = repo.get_all(
            test_type="benchmark",
            days=7
        )
        assert len(results) == 1
    
    def test_filter_with_limit(self, repo):
        """Test limit parameter."""
        results = repo.get_all(limit=3)
        assert len(results) == 3
        
        results = repo.get_all(limit=1)
        assert len(results) == 1
    
    def test_results_ordered_by_timestamp(self, repo):
        """Test that results are ordered by timestamp (newest first)."""
        results = repo.get_all()
        
        # Check that timestamps are in descending order
        for i in range(len(results) - 1):
            assert results[i].timestamp >= results[i + 1].timestamp


class TestDeleteOperations:
    """Test delete operations."""
    
    def test_delete_existing_result(self, repo):
        """Test deleting an existing result."""
        result = TestResult(
            test_type="comparison",
            file_path="/test/file.cpp",
            test_count=1,
            passed_tests=1,
            failed_tests=0,
            total_time=1.0,
            timestamp=datetime.now().isoformat()
        )
        
        result_id = repo.save(result)
        
        # Delete
        success = repo.delete(result_id)
        assert success is True
        
        # Verify deleted
        retrieved = repo.get_by_id(result_id)
        assert retrieved is None
    
    def test_delete_non_existent_result(self, repo):
        """Test deleting non-existent result."""
        success = repo.delete(9999)
        assert success is False
    
    def test_delete_all_without_confirm(self, repo):
        """Test delete_all without confirmation."""
        # Save some results
        for i in range(3):
            repo.save(TestResult(
                test_type="comparison",
                file_path=f"/test/file{i}.cpp",
                test_count=1,
                passed_tests=1,
                failed_tests=0,
                total_time=1.0,
                timestamp=datetime.now().isoformat()
            ))
        
        # Try to delete without confirmation
        success = repo.delete_all(confirm=False)
        assert success is False
        
        # Verify nothing was deleted
        results = repo.get_all()
        assert len(results) == 3
    
    def test_delete_all_with_confirm(self, repo):
        """Test delete_all with confirmation."""
        # Save some results
        for i in range(3):
            repo.save(TestResult(
                test_type="comparison",
                file_path=f"/test/file{i}.cpp",
                test_count=1,
                passed_tests=1,
                failed_tests=0,
                total_time=1.0,
                timestamp=datetime.now().isoformat()
            ))
        
        # Delete with confirmation
        success = repo.delete_all(confirm=True)
        assert success is True
        
        # Verify all deleted
        results = repo.get_all()
        assert len(results) == 0


class TestConvenienceMethods:
    """Test convenience methods."""
    
    def test_get_by_project(self, repo):
        """Test get_by_project convenience method."""
        # Save results for different projects
        repo.save(TestResult(
            test_type="comparison",
            file_path="/test/file1.cpp",
            test_count=1,
            passed_tests=1,
            failed_tests=0,
            total_time=1.0,
            timestamp=datetime.now().isoformat(),
            project_name="ProjectA"
        ))
        repo.save(TestResult(
            test_type="comparison",
            file_path="/test/file2.cpp",
            test_count=1,
            passed_tests=1,
            failed_tests=0,
            total_time=1.0,
            timestamp=datetime.now().isoformat(),
            project_name="ProjectB"
        ))
        
        results = repo.get_by_project("ProjectA")
        assert len(results) == 1
        assert "ProjectA" in results[0].project_name
    
    def test_get_recent(self, repo):
        """Test get_recent convenience method."""
        # Save old and new results
        repo.save(TestResult(
            test_type="comparison",
            file_path="/test/old.cpp",
            test_count=1,
            passed_tests=1,
            failed_tests=0,
            total_time=1.0,
            timestamp=(datetime.now() - timedelta(days=10)).isoformat()
        ))
        repo.save(TestResult(
            test_type="comparison",
            file_path="/test/new.cpp",
            test_count=1,
            passed_tests=1,
            failed_tests=0,
            total_time=1.0,
            timestamp=datetime.now().isoformat()
        ))
        
        recent = repo.get_recent(days=7)
        assert len(recent) == 1
        assert "new.cpp" in recent[0].file_path
    
    def test_count_by_status_passed(self, repo):
        """Test count_by_status for passed tests."""
        # Save passed and failed results
        repo.save(TestResult(
            test_type="comparison",
            file_path="/test/file1.cpp",
            test_count=10,
            passed_tests=10,
            failed_tests=0,
            total_time=1.0,
            timestamp=datetime.now().isoformat()
        ))
        repo.save(TestResult(
            test_type="comparison",
            file_path="/test/file2.cpp",
            test_count=10,
            passed_tests=8,
            failed_tests=2,
            total_time=1.0,
            timestamp=datetime.now().isoformat()
        ))
        
        count = repo.count_by_status(STATUS_PASSED)
        assert count == 1
    
    def test_count_by_status_failed(self, repo):
        """Test count_by_status for failed tests."""
        # Save passed and failed results
        repo.save(TestResult(
            test_type="comparison",
            file_path="/test/file1.cpp",
            test_count=10,
            passed_tests=10,
            failed_tests=0,
            total_time=1.0,
            timestamp=datetime.now().isoformat()
        ))
        repo.save(TestResult(
            test_type="comparison",
            file_path="/test/file2.cpp",
            test_count=10,
            passed_tests=8,
            failed_tests=2,
            total_time=1.0,
            timestamp=datetime.now().isoformat()
        ))
        
        count = repo.count_by_status(STATUS_FAILED)
        assert count == 1


class TestEdgeCases:
    """Test edge cases and error conditions."""
    
    def test_get_all_empty_database(self, repo):
        """Test get_all on empty database."""
        results = repo.get_all()
        assert results == []
        assert isinstance(results, list)
    
    def test_filter_with_no_matches(self, repo):
        """Test filtering with no matches."""
        repo.save(TestResult(
            test_type="comparison",
            file_path="/test/file.cpp",
            test_count=1,
            passed_tests=1,
            failed_tests=0,
            total_time=1.0,
            timestamp=datetime.now().isoformat(),
            project_name="ProjectA"
        ))
        
        # Filter that matches nothing
        results = repo.get_all(project_name="NonExistentProject")
        assert results == []
    
    def test_save_with_very_long_strings(self, repo):
        """Test saving result with very long strings."""
        long_details = "x" * 10000
        
        result = TestResult(
            test_type="comparison",
            file_path="/test/file.cpp",
            test_count=1,
            passed_tests=1,
            failed_tests=0,
            total_time=1.0,
            timestamp=datetime.now().isoformat(),
            test_details=long_details
        )
        
        result_id = repo.save(result)
        retrieved = repo.get_by_id(result_id)
        
        assert retrieved.test_details == long_details
    
    def test_save_with_special_characters(self, repo):
        """Test saving result with special characters."""
        result = TestResult(
            test_type="comparison",
            file_path="/test/file with spaces & special 'chars\".cpp",
            test_count=1,
            passed_tests=1,
            failed_tests=0,
            total_time=1.0,
            timestamp=datetime.now().isoformat(),
            project_name="Project's \"Name\""
        )
        
        result_id = repo.save(result)
        retrieved = repo.get_by_id(result_id)
        
        assert retrieved.file_path == "/test/file with spaces & special 'chars\".cpp"
        assert retrieved.project_name == "Project's \"Name\""
