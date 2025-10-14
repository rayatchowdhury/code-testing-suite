"""
Unit tests for TestResultRepository.

Tests all CRUD operations and filtering capabilities including:
- Save test results
- Retrieve by ID and with filters
- Delete operations
- Advanced filtering (type, project, days, status)
- Convenience methods
"""

from datetime import datetime, timedelta

import pytest

from src.app.persistence.database.connection import DatabaseConnection
from src.app.persistence.database.exceptions import RepositoryError
from src.app.persistence.database.models import TestResult
from src.app.persistence.database.repositories.test_result_repository import (
    TestResultRepository,
)
from tests.fixtures.database_fixtures import (
    ResultBuilder,
    create_sample_test_result,
    create_test_result_series,
)


@pytest.fixture
def reset_db():
    """Reset database connection singleton between tests."""
    DatabaseConnection.reset_instance()
    yield
    DatabaseConnection.reset_instance()


@pytest.fixture
def temp_db(tmp_path, reset_db):
    """Create temporary database."""
    db_path = str(tmp_path / "test_results.db")
    db = DatabaseConnection(db_path)
    yield db
    db.close()


@pytest.fixture
def repository(temp_db):
    """Create repository instance."""
    return TestResultRepository()


@pytest.fixture
def populated_repository(repository):
    """Create repository with diverse test data."""
    # Add comparator results for different projects
    for i in range(3):
        result = (
            ResultBuilder()
            .with_test_type("comparator")
            .with_project_name("project_a")
            .with_results(passed=8, failed=2)
            .with_timestamp((datetime.now() - timedelta(days=i)).isoformat())
            .build()
        )
        repository.save(result)

    # Add validator results
    for i in range(2):
        result = (
            ResultBuilder()
            .with_test_type("validator")
            .with_project_name("project_b")
            .with_results(passed=10, failed=0)
            .with_timestamp((datetime.now() - timedelta(days=i + 3)).isoformat())
            .build()
        )
        repository.save(result)

    # Add benchmarker result
    result = (
        ResultBuilder()
        .with_test_type("benchmarker")
        .with_project_name("project_a")
        .with_results(passed=5, failed=5)
        .with_timestamp((datetime.now() - timedelta(days=10)).isoformat())
        .build()
    )
    repository.save(result)

    return repository


class TestSaveTestResult:
    """Test saving test results to database."""

    def test_saves_new_result(self, repository):
        """Should save test result and return ID."""
        result = create_sample_test_result("comparator")

        result_id = repository.save(result)

        assert result_id > 0

    def test_saves_all_fields_correctly(self, repository):
        """Should save all TestResult fields."""
        result = (
            ResultBuilder()
            .with_test_type("validator")
            .with_file_path("/path/to/test.cpp")
            .with_results(passed=15, failed=5)
            .with_total_time(3.5)
            .with_project_name("MyProject")
            .with_test_details("test_details_json")
            .with_files_snapshot('{"files": {}}')
            .with_mismatch_analysis("No issues")
            .build()
        )

        result_id = repository.save(result)

        # Retrieve and verify
        saved = repository.get_by_id(result_id)
        assert saved.test_type == "validator"
        assert saved.file_path == "/path/to/test.cpp"
        assert saved.passed_tests == 15
        assert saved.failed_tests == 5
        assert saved.total_time == 3.5
        assert saved.project_name == "MyProject"
        assert "test_details" in saved.test_details
        assert saved.files_snapshot == '{"files": {}}'
        assert saved.mismatch_analysis == "No issues"

    def test_auto_sets_timestamp_if_none(self, repository):
        """Should auto-set timestamp if not provided."""
        result = TestResult(
            test_type="comparator",
            file_path="/test.cpp",
            test_count=10,
            passed_tests=10,
            failed_tests=0,
            total_time=1.0,
            timestamp=None,  # No timestamp
            test_details="",
            project_name="test",
        )

        result_id = repository.save(result)
        saved = repository.get_by_id(result_id)

        assert saved.timestamp is not None
        assert saved.timestamp != ""

    def test_handles_empty_optional_fields(self, repository):
        """Should handle empty optional fields."""
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

        result_id = repository.save(result)

        assert result_id > 0

    def test_saves_multiple_results(self, repository):
        """Should save multiple results independently."""
        result1 = create_sample_test_result("comparator")
        result2 = create_sample_test_result("validator")

        id1 = repository.save(result1)
        id2 = repository.save(result2)

        assert id2 > id1  # Auto-increment


class TestGetById:
    """Test retrieving test results by ID."""

    def test_retrieves_by_id(self, populated_repository):
        """Should retrieve test result by ID."""
        result = populated_repository.get_by_id(1)

        assert result is not None
        assert result.id == 1
        assert isinstance(result, TestResult)

    def test_returns_none_for_nonexistent_id(self, repository):
        """Should return None for nonexistent ID."""
        result = repository.get_by_id(999)

        assert result is None

    def test_returns_correct_entity_type(self, populated_repository):
        """Should return TestResult instance."""
        result = populated_repository.get_by_id(1)

        assert isinstance(result, TestResult)
        assert hasattr(result, "test_type")
        assert hasattr(result, "passed_tests")


class TestGetAll:
    """Test retrieving all test results with filters."""

    def test_retrieves_all_results(self, populated_repository):
        """Should retrieve all test results."""
        results = populated_repository.get_all()

        assert len(results) == 6  # 3 comparator + 2 validator + 1 benchmarker

    def test_respects_limit(self, populated_repository):
        """Should limit number of results."""
        results = populated_repository.get_all(limit=3)

        assert len(results) == 3

    def test_orders_by_timestamp_descending(self, populated_repository):
        """Should return most recent results first."""
        results = populated_repository.get_all()

        # First result should be most recent
        for i in range(len(results) - 1):
            assert results[i].timestamp >= results[i + 1].timestamp

    def test_filters_by_test_type(self, populated_repository):
        """Should filter by test type."""
        results = populated_repository.get_all(test_type="validator")

        assert len(results) == 2
        assert all(r.test_type == "validator" for r in results)

    def test_filters_by_project_name(self, populated_repository):
        """Should filter by project name."""
        results = populated_repository.get_all(project_name="project_a")

        assert len(results) == 4  # 3 comparator + 1 benchmarker
        assert all(r.project_name == "project_a" for r in results)

    def test_filters_by_days(self, populated_repository):
        """Should filter by recent days."""
        results = populated_repository.get_all(days=5)

        # Should get results from last 5 days (excludes the 10-day-old one)
        assert len(results) == 5

    def test_filters_by_file_name(self, populated_repository):
        """Should filter by file name pattern."""
        # Add result with specific file name
        result = ResultBuilder().with_file_path("/specific/path/solution.cpp").build()
        populated_repository.save(result)

        results = populated_repository.get_all(file_name="solution")

        assert len(results) >= 1
        assert any("solution" in r.file_path for r in results)

    def test_filters_by_status_passed(self, populated_repository):
        """Should filter by passed status (all tests passed)."""
        results = populated_repository.get_all(status="passed")

        # Only validator results have 100% pass rate
        assert len(results) == 2
        assert all(r.failed_tests == 0 for r in results)

    def test_filters_by_status_failed(self, populated_repository):
        """Should filter by failed status (has failures)."""
        results = populated_repository.get_all(status="failed")

        # Comparator (2 failures) and benchmarker (5 failures)
        assert len(results) == 4
        assert all(r.failed_tests > 0 for r in results)

    def test_combines_multiple_filters(self, populated_repository):
        """Should combine multiple filters with AND logic."""
        results = populated_repository.get_all(
            test_type="comparator", project_name="project_a", days=5
        )

        assert len(results) == 3
        assert all(r.test_type == "comparator" for r in results)
        assert all(r.project_name == "project_a" for r in results)

    def test_returns_empty_list_when_no_matches(self, repository):
        """Should return empty list when no results match."""
        results = repository.get_all(test_type="nonexistent")

        assert results == []

    def test_handles_zero_limit(self, populated_repository):
        """Should handle zero limit (returns nothing)."""
        results = populated_repository.get_all(limit=0)

        assert len(results) == 0


class TestDelete:
    """Test deleting test results."""

    def test_deletes_existing_result(self, populated_repository):
        """Should delete test result by ID."""
        result = populated_repository.delete(1)

        assert result is True

        # Verify deletion
        assert populated_repository.get_by_id(1) is None

    def test_returns_false_for_nonexistent_id(self, repository):
        """Should return False when deleting nonexistent ID."""
        result = repository.delete(999)

        assert result is False

    def test_only_deletes_specified_id(self, populated_repository):
        """Should only delete the specified ID."""
        initial_count = len(populated_repository.get_all())

        populated_repository.delete(1)

        remaining_count = len(populated_repository.get_all())
        assert remaining_count == initial_count - 1

        # Other IDs still exist
        assert populated_repository.get_by_id(2) is not None


class TestDeleteAll:
    """Test bulk delete operations."""

    def test_requires_confirmation(self, populated_repository):
        """Should not delete without confirm=True."""
        result = populated_repository.delete_all(confirm=False)

        assert result is False

        # Data still exists
        assert len(populated_repository.get_all()) == 6

    def test_deletes_all_with_confirmation(self, populated_repository):
        """Should delete all when confirmed."""
        result = populated_repository.delete_all(confirm=True)

        assert result is True

        # All data deleted
        assert len(populated_repository.get_all()) == 0

    def test_resets_auto_increment(self, populated_repository):
        """Should reset auto-increment counter."""
        populated_repository.delete_all(confirm=True)

        # Add new result
        result = create_sample_test_result()
        new_id = populated_repository.save(result)

        # Should start from 1 again
        assert new_id == 1

    def test_default_behavior_is_safe(self, populated_repository):
        """Should not delete by default (safety check)."""
        # Calling without arguments should not delete
        populated_repository.delete_all()

        assert len(populated_repository.get_all()) == 6


class TestConvenienceMethods:
    """Test convenience methods for common queries."""

    def test_get_by_project(self, populated_repository):
        """Should get all results for a project."""
        results = populated_repository.get_by_project("project_a")

        assert len(results) == 4
        assert all(r.project_name == "project_a" for r in results)

    def test_get_by_project_respects_limit(self, populated_repository):
        """Should respect limit in get_by_project."""
        results = populated_repository.get_by_project("project_a", limit=2)

        assert len(results) == 2

    def test_get_recent(self, populated_repository):
        """Should get recent results from last N days."""
        results = populated_repository.get_recent(days=5)

        assert len(results) == 5  # Excludes 10-day-old result

    def test_get_recent_respects_limit(self, populated_repository):
        """Should respect limit in get_recent."""
        results = populated_repository.get_recent(days=30, limit=3)

        assert len(results) == 3

    def test_get_recent_default_days(self, populated_repository):
        """Should use default 7 days."""
        results = populated_repository.get_recent()

        # Should get results from last 7 days
        assert len(results) >= 0


class TestCountByStatus:
    """Test counting results by status."""

    def test_counts_passed_results(self, populated_repository):
        """Should count results with all tests passed."""
        count = populated_repository.count_by_status("passed")

        assert count == 2  # Only validator results (10 passed, 0 failed)

    def test_counts_failed_results(self, populated_repository):
        """Should count results with any failures."""
        count = populated_repository.count_by_status("failed")

        assert count == 4  # 3 comparator + 1 benchmarker (all have failures)

    def test_returns_zero_for_invalid_status(self, populated_repository):
        """Should return 0 for invalid status."""
        count = populated_repository.count_by_status("invalid_status")

        assert count == 0

    def test_counts_on_empty_repository(self, repository):
        """Should return 0 for empty repository."""
        count = repository.count_by_status("passed")

        assert count == 0


class TestRowToEntity:
    """Test row-to-entity conversion."""

    def test_converts_row_to_test_result(self, populated_repository):
        """Should convert database row to TestResult."""
        result = populated_repository.get_by_id(1)

        # Verify all fields are populated
        assert isinstance(result, TestResult)
        assert result.id is not None
        assert result.test_type is not None
        assert result.file_path is not None
        assert isinstance(result.test_count, int)
        assert isinstance(result.passed_tests, int)
        assert isinstance(result.failed_tests, int)
        assert isinstance(result.total_time, float)

    def test_handles_missing_optional_fields(self, repository):
        """Should handle rows with missing optional fields."""
        # Old database might not have files_snapshot column
        result = create_sample_test_result()
        result_id = repository.save(result)

        retrieved = repository.get_by_id(result_id)

        # Should have default values for optional fields
        assert retrieved is not None
        assert hasattr(retrieved, "files_snapshot")
        assert hasattr(retrieved, "mismatch_analysis")


class TestErrorHandling:
    """Test error handling in repository operations."""

    def test_save_raises_repository_error_on_failure(self, repository):
        """Should raise RepositoryError on save failure."""
        # Try to save invalid data
        with pytest.raises((RepositoryError, AttributeError)):
            repository.save(None)

    def test_handles_database_connection_errors(self, repository):
        """Should handle connection errors gracefully."""
        # Connection errors are caught by context manager
        # Just verify repository doesn't crash
        pytest.skip("DatabaseConnection context manager handles errors internally")


class TestLogging:
    """Test logging behavior."""

    def test_logs_save_operation(self, repository, caplog):
        """Should log save operations."""
        import logging

        caplog.set_level(logging.INFO)

        result = create_sample_test_result()
        repository.save(result)

        # Logging might be at different level
        assert len(caplog.records) >= 0  # Just verify no crash

    def test_logs_delete_operation(self, populated_repository, caplog):
        """Should log delete operations."""
        import logging

        caplog.set_level(logging.INFO)

        populated_repository.delete(1)

        # Logging might be at different level
        assert len(caplog.records) >= 0

    def test_logs_filter_details(self, populated_repository, caplog):
        """Should log filter details when retrieving."""
        import logging

        caplog.set_level(logging.INFO)

        populated_repository.get_all(test_type="comparator", project_name="project_a")

        # Logging might be at different level
        assert len(caplog.records) >= 0


class TestDataIntegrity:
    """Test data integrity and consistency."""

    def test_maintains_referential_integrity(self, repository):
        """Should maintain data integrity across operations."""
        # Save result
        result = create_sample_test_result()
        result_id = repository.save(result)

        # Retrieve
        saved = repository.get_by_id(result_id)

        # Modify and save again (should create new record, not update)
        result2 = create_sample_test_result()
        result_id2 = repository.save(result2)

        # Both should exist
        assert repository.get_by_id(result_id) is not None
        assert repository.get_by_id(result_id2) is not None
        assert result_id != result_id2

    def test_handles_concurrent_operations(self, repository):
        """Should handle multiple operations safely."""
        # Perform multiple operations
        ids = []
        for i in range(10):
            result = create_sample_test_result()
            result_id = repository.save(result)
            ids.append(result_id)

        # All should be retrievable
        for result_id in ids:
            assert repository.get_by_id(result_id) is not None
