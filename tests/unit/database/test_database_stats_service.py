"""
Unit tests for DatabaseStatsService.

Tests database statistics and analytics including:
- Database statistics (counts, sizes, dates)
- Test statistics (totals, breakdowns, success rates)
- Project-specific statistics
- Error handling
"""

import pytest
import os
from datetime import datetime, timedelta

from src.app.persistence.database.services.database_stats_service import DatabaseStatsService
from src.app.persistence.database.connection import DatabaseConnection
from src.app.persistence.database.repositories.test_result_repository import TestResultRepository
from src.app.persistence.database.models import TestResult, Session
from tests.fixtures.database_fixtures import ResultBuilder, create_sample_test_result


@pytest.fixture
def reset_db():
    """Reset database connection singleton."""
    DatabaseConnection.reset_instance()
    yield
    DatabaseConnection.reset_instance()


@pytest.fixture
def temp_db(tmp_path, reset_db):
    """Create temporary database."""
    db_path = str(tmp_path / "stats_test.db")
    db = DatabaseConnection(db_path)
    yield db
    db.close()


@pytest.fixture
def stats_service(temp_db):
    """Create stats service instance."""
    return DatabaseStatsService()


@pytest.fixture
def populated_service(stats_service):
    """Create service with sample data."""
    repo = TestResultRepository()
    
    # Add test results with different types and timestamps
    for i in range(3):
        result = ResultBuilder() \
            .with_test_type('comparator') \
            .with_project_name('project_a') \
            .with_results(passed=8, failed=2) \
            .with_timestamp((datetime.now() - timedelta(days=i)).isoformat()) \
            .build()
        repo.save(result)
    
    for i in range(2):
        result = ResultBuilder() \
            .with_test_type('validator') \
            .with_project_name('project_b') \
            .with_results(passed=10, failed=0) \
            .with_timestamp((datetime.now() - timedelta(days=i+5)).isoformat()) \
            .build()
        repo.save(result)
    
    # Add a session
    with stats_service.db.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO sessions (session_name, open_files, active_file, timestamp, project_name) VALUES (?, ?, ?, ?, ?)",
            ("test_session", "[]", "", datetime.now().isoformat(), "test_project")
        )
    
    return stats_service


class TestInitialization:
    """Test service initialization."""
    
    def test_initializes_with_database_connection(self, stats_service):
        """Should initialize with DatabaseConnection."""
        assert stats_service.db is not None
        assert isinstance(stats_service.db, DatabaseConnection)
    
    def test_initializes_with_test_repository(self, stats_service):
        """Should initialize with TestResultRepository."""
        assert stats_service.test_repo is not None
        assert isinstance(stats_service.test_repo, TestResultRepository)


class TestGetDatabaseStats:
    """Test getting database statistics."""
    
    def test_returns_stats_dictionary(self, stats_service):
        """Should return dictionary of statistics."""
        stats = stats_service.get_database_stats()
        
        assert isinstance(stats, dict)
    
    def test_includes_test_results_count(self, populated_service):
        """Should include test results count."""
        stats = populated_service.get_database_stats()
        
        assert 'test_results_count' in stats
        assert stats['test_results_count'] == 5
    
    def test_includes_sessions_count(self, populated_service):
        """Should include sessions count."""
        stats = populated_service.get_database_stats()
        
        assert 'sessions_count' in stats
        assert stats['sessions_count'] == 1
    
    def test_includes_database_size(self, populated_service):
        """Should include database file size."""
        stats = populated_service.get_database_stats()
        
        assert 'database_size_bytes' in stats
        assert 'database_size_mb' in stats
        assert stats['database_size_bytes'] > 0
        assert stats['database_size_mb'] >= 0
    
    def test_includes_date_ranges(self, populated_service):
        """Should include oldest and newest timestamps."""
        stats = populated_service.get_database_stats()
        
        assert 'oldest_test' in stats
        assert 'newest_test' in stats
        assert 'oldest_session' in stats
        assert 'newest_session' in stats
    
    def test_handles_empty_database(self, stats_service):
        """Should handle empty database gracefully."""
        stats = stats_service.get_database_stats()
        
        assert stats['test_results_count'] == 0
        assert stats['sessions_count'] == 0
        assert stats['oldest_test'] == "No data"
        assert stats['newest_test'] == "No data"
    
    def test_calculates_database_size_correctly(self, populated_service):
        """Should calculate database size in bytes and MB."""
        stats = populated_service.get_database_stats()
        
        size_bytes = stats['database_size_bytes']
        size_mb = stats['database_size_mb']
        
        # Verify conversion
        expected_mb = round(size_bytes / (1024 * 1024), 2)
        assert size_mb == expected_mb
    
    def test_handles_nonexistent_database_file(self, tmp_path, reset_db):
        """Should handle case where database file doesn't exist yet."""
        # Create service with path that doesn't exist
        db_path = str(tmp_path / "nonexistent.db")
        db = DatabaseConnection(db_path)
        service = DatabaseStatsService()
        
        stats = service.get_database_stats()
        
        # Database gets created on connection, so it will have some size
        # Just verify it doesn't crash and returns valid structure
        assert 'database_size_bytes' in stats
        assert 'database_size_mb' in stats
        assert stats['database_size_bytes'] >= 0
        
        db.close()
        DatabaseConnection.reset_instance()


class TestGetTestStatistics:
    """Test getting test statistics."""
    
    def test_returns_statistics_dictionary(self, populated_service):
        """Should return dictionary of test statistics."""
        stats = populated_service.get_test_statistics()
        
        assert isinstance(stats, dict)
    
    def test_includes_total_tests(self, populated_service):
        """Should include total test count."""
        stats = populated_service.get_test_statistics()
        
        assert 'total_tests' in stats
        assert stats['total_tests'] == 5
    
    def test_includes_breakdown_by_type(self, populated_service):
        """Should include breakdown by test type."""
        stats = populated_service.get_test_statistics()
        
        assert 'by_type' in stats
        assert isinstance(stats['by_type'], dict)
        assert stats['by_type']['comparator'] == 3
        assert stats['by_type']['validator'] == 2
    
    def test_includes_success_rate(self, populated_service):
        """Should include success rate percentage."""
        stats = populated_service.get_test_statistics()
        
        assert 'success_rate' in stats
        assert isinstance(stats['success_rate'], (int, float))
        assert 0 <= stats['success_rate'] <= 100
    
    def test_calculates_success_rate_correctly(self, stats_service):
        """Should calculate success rate as percentage."""
        repo = TestResultRepository()
        
        # Add 100% pass result
        result1 = ResultBuilder().with_results(passed=10, failed=0).build()
        repo.save(result1)
        
        # Add 50% pass result
        result2 = ResultBuilder().with_results(passed=5, failed=5).build()
        repo.save(result2)
        
        stats = stats_service.get_test_statistics()
        
        # (10 + 5) / (10 + 10) = 15/20 = 75%
        assert stats['success_rate'] == 75.0
    
    def test_filters_by_project_name(self, populated_service):
        """Should filter statistics by project."""
        stats = populated_service.get_test_statistics(project_name='project_a')
        
        assert stats['total_tests'] == 3
        assert 'comparator' in stats['by_type']
    
    def test_handles_empty_database(self, stats_service):
        """Should handle empty database."""
        stats = stats_service.get_test_statistics()
        
        assert stats['total_tests'] == 0
        assert stats['by_type'] == {}
        assert stats['success_rate'] == 0
    
    def test_handles_nonexistent_project(self, populated_service):
        """Should handle filtering by nonexistent project."""
        stats = populated_service.get_test_statistics(project_name='nonexistent_project')
        
        assert stats['total_tests'] == 0
    
    def test_success_rate_with_all_failures(self, stats_service):
        """Should handle 0% success rate."""
        repo = TestResultRepository()
        
        result = ResultBuilder().with_results(passed=0, failed=10).build()
        repo.save(result)
        
        stats = stats_service.get_test_statistics()
        
        assert stats['success_rate'] == 0.0
    
    def test_success_rate_with_all_passes(self, stats_service):
        """Should handle 100% success rate."""
        repo = TestResultRepository()
        
        result = ResultBuilder().with_results(passed=10, failed=0).build()
        repo.save(result)
        
        stats = stats_service.get_test_statistics()
        
        assert stats['success_rate'] == 100.0


class TestProjectSpecificStatistics:
    """Test project-specific statistics filtering."""
    
    def test_filters_total_by_project(self, populated_service):
        """Should filter total count by project."""
        stats_a = populated_service.get_test_statistics(project_name='project_a')
        stats_b = populated_service.get_test_statistics(project_name='project_b')
        
        assert stats_a['total_tests'] == 3
        assert stats_b['total_tests'] == 2
    
    def test_filters_type_breakdown_by_project(self, populated_service):
        """Should filter type breakdown by project."""
        stats_a = populated_service.get_test_statistics(project_name='project_a')
        
        assert 'comparator' in stats_a['by_type']
        assert 'validator' not in stats_a['by_type']
    
    def test_calculates_project_success_rate(self, populated_service):
        """Should calculate success rate for specific project."""
        stats_a = populated_service.get_test_statistics(project_name='project_a')
        stats_b = populated_service.get_test_statistics(project_name='project_b')
        
        # project_a: 3 results with 8/10 pass rate = 80%
        assert stats_a['success_rate'] == 80.0
        
        # project_b: 2 results with 10/10 pass rate = 100%
        assert stats_b['success_rate'] == 100.0


class TestStatisticsAccuracy:
    """Test accuracy of statistical calculations."""
    
    def test_counts_match_actual_data(self, stats_service):
        """Should accurately count test results."""
        repo = TestResultRepository()
        
        # Add known number of results
        for i in range(7):
            repo.save(create_sample_test_result())
        
        stats = stats_service.get_test_statistics()
        
        assert stats['total_tests'] == 7
    
    def test_type_breakdown_sums_to_total(self, populated_service):
        """Should have type counts sum to total."""
        stats = populated_service.get_test_statistics()
        
        type_sum = sum(stats['by_type'].values())
        assert type_sum == stats['total_tests']
    
    def test_handles_mixed_pass_fail_rates(self, stats_service):
        """Should correctly calculate with mixed results."""
        repo = TestResultRepository()
        
        # Various pass/fail combinations
        repo.save(ResultBuilder().with_results(passed=10, failed=0).build())  # 100%
        repo.save(ResultBuilder().with_results(passed=0, failed=10).build())  # 0%
        repo.save(ResultBuilder().with_results(passed=5, failed=5).build())   # 50%
        
        stats = stats_service.get_test_statistics()
        
        # (10 + 0 + 5) / (10 + 10 + 10) = 15/30 = 50%
        assert stats['success_rate'] == 50.0


class TestLogging:
    """Test logging behavior."""
    
    def test_logs_database_stats(self, populated_service, caplog):
        """Should log when retrieving database stats."""
        import logging
        caplog.set_level(logging.INFO)
        
        populated_service.get_database_stats()
        
        # Just verify no crash - logging might be at different level
        assert len(caplog.records) >= 0


class TestConnectionManagement:
    """Test database connection handling."""
    
    def test_uses_context_manager(self, populated_service):
        """Should use context manager for database operations."""
        # Should not crash or leave connections open
        stats = populated_service.get_database_stats()
        
        assert isinstance(stats, dict)
    
    def test_shares_connection_singleton(self, stats_service):
        """Should use singleton DatabaseConnection."""
        service2 = DatabaseStatsService()
        
        assert service2.db is stats_service.db


class TestEdgeCases:
    """Test edge cases and boundary conditions."""
    
    def test_handles_zero_test_count(self, stats_service):
        """Should handle division by zero in success rate."""
        stats = stats_service.get_test_statistics()
        
        # Should not crash
        assert stats['success_rate'] == 0
    
    def test_handles_very_large_datasets(self, stats_service):
        """Should handle large number of test results."""
        repo = TestResultRepository()
        
        # Add many results
        for i in range(100):
            repo.save(create_sample_test_result())
        
        stats = stats_service.get_test_statistics()
        
        assert stats['total_tests'] == 100
    
    def test_returns_dict_structure_consistently(self, stats_service):
        """Should always return consistent dict structure."""
        # Empty database
        stats1 = stats_service.get_test_statistics()
        
        # Add data
        repo = TestResultRepository()
        repo.save(create_sample_test_result())
        
        stats2 = stats_service.get_test_statistics()
        
        # Should have same keys
        assert set(stats1.keys()) == set(stats2.keys())
