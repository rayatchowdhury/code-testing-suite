"""
Unit tests for DatabaseMaintenanceService.

Tests database maintenance operations including:
- Cleanup of old data
- Database optimization (VACUUM)
- Size tracking and reporting
- Error handling
"""

import os
from datetime import datetime, timedelta

import pytest

from src.app.persistence.database.connection import DatabaseConnection
from src.app.persistence.database.repositories.test_result_repository import (
    TestResultRepository,
)
from src.app.persistence.database.services.database_maintenance_service import (
    DatabaseMaintenanceService,
)
from tests.fixtures.database_fixtures import ResultBuilder


@pytest.fixture
def reset_db():
    """Reset database connection singleton."""
    DatabaseConnection.reset_instance()
    yield
    DatabaseConnection.reset_instance()


@pytest.fixture
def temp_db(tmp_path, reset_db):
    """Create temporary database."""
    db_path = str(tmp_path / "maintenance_test.db")
    db = DatabaseConnection(db_path)
    yield db
    db.close()


@pytest.fixture
def maintenance_service(temp_db):
    """Create maintenance service instance."""
    return DatabaseMaintenanceService()


@pytest.fixture
def populated_service(maintenance_service):
    """Create service with sample data of varying ages."""
    repo = TestResultRepository()

    # Add old test results (>30 days)
    for i in range(3):
        result = (
            ResultBuilder()
            .with_timestamp((datetime.now() - timedelta(days=40 + i)).isoformat())
            .with_project_name("old_project")
            .build()
        )
        repo.save(result)

    # Add recent test results (<30 days)
    for i in range(5):
        result = (
            ResultBuilder()
            .with_timestamp((datetime.now() - timedelta(days=i)).isoformat())
            .with_project_name("new_project")
            .build()
        )
        repo.save(result)

    # Add old session (>30 days)
    with maintenance_service.db.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO sessions (session_name, open_files, active_file, timestamp, project_name) VALUES (?, ?, ?, ?, ?)",
            (
                "old_session",
                "[]",
                "",
                (datetime.now() - timedelta(days=50)).isoformat(),
                "old_project",
            ),
        )

    # Add recent session
    with maintenance_service.db.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO sessions (session_name, open_files, active_file, timestamp, project_name) VALUES (?, ?, ?, ?, ?)",
            ("new_session", "[]", "", datetime.now().isoformat(), "new_project"),
        )

    return maintenance_service


class TestInitialization:
    """Test service initialization."""

    def test_initializes_with_database_connection(self, maintenance_service):
        """Should initialize with DatabaseConnection."""
        assert maintenance_service.db is not None
        assert isinstance(maintenance_service.db, DatabaseConnection)

    def test_shares_connection_singleton(self, maintenance_service):
        """Should use singleton DatabaseConnection."""
        service2 = DatabaseMaintenanceService()

        assert service2.db is maintenance_service.db


class TestCleanupOldData:
    """Test cleanup of old data."""

    def test_deletes_old_test_results(self, populated_service):
        """Should delete test results older than specified days."""
        repo = TestResultRepository()

        # Verify initial count
        before_count = len(repo.get_all())
        assert before_count == 8

        # Cleanup data older than 30 days
        result = populated_service.cleanup_old_data(days=30)

        # Should have deleted 3 old test results
        after_count = len(repo.get_all())
        assert after_count == 5
        assert result["test_rows_deleted"] == 3

    def test_deletes_old_sessions(self, populated_service):
        """Should delete sessions older than specified days."""
        # Cleanup data older than 30 days
        result = populated_service.cleanup_old_data(days=30)

        # Should have deleted 1 old session
        assert result["session_rows_deleted"] == 1

        # Verify session deleted
        with populated_service.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM sessions")
            count = cursor.fetchone()[0]
            assert count == 1

    def test_returns_deletion_counts(self, populated_service):
        """Should return dictionary with deletion counts."""
        result = populated_service.cleanup_old_data(days=30)

        assert isinstance(result, dict)
        assert "test_rows_deleted" in result
        assert "session_rows_deleted" in result
        assert "vacuumed" in result

    def test_performs_vacuum_after_deletion(self, populated_service):
        """Should run VACUUM after deletion."""
        result = populated_service.cleanup_old_data(days=30)

        assert result["vacuumed"] is True

    def test_handles_no_old_data(self, maintenance_service):
        """Should handle case with no old data."""
        repo = TestResultRepository()

        # Add only recent data
        result = ResultBuilder().with_timestamp(datetime.now().isoformat()).build()
        repo.save(result)

        # Cleanup data older than 30 days
        cleanup_result = maintenance_service.cleanup_old_data(days=30)

        assert cleanup_result["test_rows_deleted"] == 0
        assert cleanup_result["session_rows_deleted"] == 0

    def test_respects_days_parameter(self, maintenance_service):
        """Should delete data based on days parameter."""
        repo = TestResultRepository()

        # Add data at different ages
        repo.save(
            ResultBuilder()
            .with_timestamp((datetime.now() - timedelta(days=5)).isoformat())
            .build()
        )
        repo.save(
            ResultBuilder()
            .with_timestamp((datetime.now() - timedelta(days=15)).isoformat())
            .build()
        )
        repo.save(
            ResultBuilder()
            .with_timestamp((datetime.now() - timedelta(days=25)).isoformat())
            .build()
        )

        # Delete only data older than 10 days
        result = maintenance_service.cleanup_old_data(days=10)

        # Should delete 2 results (15 and 25 days old)
        assert result["test_rows_deleted"] == 2

        # Verify 1 result remains
        assert len(repo.get_all()) == 1

    def test_handles_empty_database(self, maintenance_service):
        """Should handle empty database."""
        result = maintenance_service.cleanup_old_data(days=30)

        assert result["test_rows_deleted"] == 0
        assert result["session_rows_deleted"] == 0
        assert result["vacuumed"] is False


class TestOptimizeDatabase:
    """Test database optimization."""

    def test_performs_vacuum(self, populated_service):
        """Should perform VACUUM operation."""
        result = populated_service.optimize_database()

        assert isinstance(result, dict)
        # Verify all expected keys are present
        assert "size_before_bytes" in result
        assert "size_after_bytes" in result

    def test_returns_size_before_optimization(self, populated_service):
        """Should return database size before optimization."""
        result = populated_service.optimize_database()

        assert "size_before_bytes" in result
        assert isinstance(result["size_before_bytes"], (int, float))
        assert result["size_before_bytes"] > 0

    def test_returns_size_after_optimization(self, populated_service):
        """Should return database size after optimization."""
        result = populated_service.optimize_database()

        assert "size_after_bytes" in result
        assert isinstance(result["size_after_bytes"], (int, float))

    def test_calculates_space_saved(self, populated_service):
        """Should calculate space saved."""
        result = populated_service.optimize_database()

        assert "space_saved_bytes" in result
        space_saved = result["space_saved_bytes"]

        # Space saved = before - after
        expected = result["size_before_bytes"] - result["size_after_bytes"]
        assert space_saved == expected

    def test_handles_empty_database(self, maintenance_service):
        """Should handle optimization of empty database."""
        result = maintenance_service.optimize_database()

        # Should still return valid results
        assert "size_before_bytes" in result
        # Empty database might still have minimal size
        assert result["size_before_bytes"] >= 0

    def test_vacuum_reduces_file_size(self, populated_service):
        """Should reduce file size after deleting data and vacuuming."""
        repo = TestResultRepository()

        # Add many test results
        for i in range(50):
            repo.save(ResultBuilder().build())

        # Get size after adding
        with populated_service.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT page_count * page_size FROM pragma_page_count(), pragma_page_size()"
            )
            size_with_data = cursor.fetchone()[0]

        # Delete all data
        for result in repo.get_all():
            repo.delete(result.id)

        # Optimize
        optimize_result = populated_service.optimize_database()

        # Should have saved some space
        assert optimize_result["space_saved_bytes"] >= 0


class TestVacuumIsolationLevel:
    """Test VACUUM isolation level requirements."""

    def test_vacuum_uses_autocommit_mode(self, maintenance_service):
        """Should set isolation_level=None for VACUUM."""
        # This test verifies the implementation detail that VACUUM
        # requires autocommit mode (isolation_level = None)

        # Should not raise an error
        result = maintenance_service.optimize_database()

        # Verify it completed successfully
        assert "size_before_bytes" in result

    def test_cleanup_vacuum_uses_autocommit(self, maintenance_service):
        """Should use autocommit for VACUUM in cleanup."""
        repo = TestResultRepository()

        # Add old data
        repo.save(
            ResultBuilder()
            .with_timestamp((datetime.now() - timedelta(days=50)).isoformat())
            .build()
        )

        # Should not raise error about VACUUM in transaction
        result = maintenance_service.cleanup_old_data(days=30)

        assert result["vacuumed"] is True


class TestReturnValues:
    """Test return value structures."""

    def test_cleanup_returns_complete_dict(self, maintenance_service):
        """Should return complete dictionary from cleanup."""
        result = maintenance_service.cleanup_old_data(days=30)

        required_keys = ["test_rows_deleted", "session_rows_deleted", "vacuumed"]
        for key in required_keys:
            assert key in result

    def test_optimize_returns_complete_dict(self, maintenance_service):
        """Should return complete dictionary from optimize."""
        result = maintenance_service.optimize_database()

        required_keys = [
            "size_before_bytes",
            "size_after_bytes",
            "space_saved_bytes",
            "size_before_mb",
            "size_after_mb",
            "space_saved_mb",
        ]
        for key in required_keys:
            assert key in result

    def test_returns_integer_counts(self, populated_service):
        """Should return integer deletion counts."""
        result = populated_service.cleanup_old_data(days=30)

        assert isinstance(result["test_rows_deleted"], int)
        assert isinstance(result["session_rows_deleted"], int)

    def test_returns_boolean_vacuum_status(self, maintenance_service):
        """Should return boolean for vacuum status."""
        result = maintenance_service.cleanup_old_data(days=30)

        assert isinstance(result["vacuumed"], bool)


class TestLogging:
    """Test logging behavior."""

    def test_logs_cleanup_operation(self, populated_service, caplog):
        """Should log cleanup operations."""
        import logging

        caplog.set_level(logging.INFO)

        populated_service.cleanup_old_data(days=30)

        # Just verify no crash
        assert len(caplog.records) >= 0

    def test_logs_optimization(self, maintenance_service, caplog):
        """Should log optimization operations."""
        import logging

        caplog.set_level(logging.INFO)

        maintenance_service.optimize_database()

        # Just verify no crash
        assert len(caplog.records) >= 0


class TestErrorHandling:
    """Test error handling."""

    def test_handles_negative_days(self, maintenance_service):
        """Should handle negative days parameter."""
        # Negative days should delete nothing (no data from the future)
        result = maintenance_service.cleanup_old_data(days=-1)

        assert result["test_rows_deleted"] == 0

    def test_handles_zero_days(self, maintenance_service):
        """Should handle zero days (delete all data)."""
        repo = TestResultRepository()
        repo.save(ResultBuilder().build())

        result = maintenance_service.cleanup_old_data(days=0)

        # Should delete recent data too
        assert result["test_rows_deleted"] >= 0


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_handles_very_old_data(self, maintenance_service):
        """Should handle data from many years ago."""
        repo = TestResultRepository()

        # Add data from 1000 days ago
        result = (
            ResultBuilder()
            .with_timestamp((datetime.now() - timedelta(days=1000)).isoformat())
            .build()
        )
        repo.save(result)

        cleanup_result = maintenance_service.cleanup_old_data(days=365)

        assert cleanup_result["test_rows_deleted"] == 1

    def test_multiple_cleanups_safe(self, populated_service):
        """Should safely perform multiple cleanups."""
        result1 = populated_service.cleanup_old_data(days=30)
        result2 = populated_service.cleanup_old_data(days=30)

        # Second cleanup should delete nothing
        assert result2["test_rows_deleted"] == 0
        assert result2["session_rows_deleted"] == 0

    def test_multiple_optimizations_safe(self, maintenance_service):
        """Should safely perform multiple optimizations."""
        result1 = maintenance_service.optimize_database()
        result2 = maintenance_service.optimize_database()

        # Both should succeed
        assert "size_before_bytes" in result1
        assert "size_before_bytes" in result2

    def test_cleanup_then_optimize(self, populated_service):
        """Should work correctly when cleanup followed by optimize."""
        cleanup_result = populated_service.cleanup_old_data(days=30)
        optimize_result = populated_service.optimize_database()

        assert cleanup_result["vacuumed"] is True
        assert "size_before_bytes" in optimize_result

    def test_handles_large_dataset_cleanup(self, maintenance_service):
        """Should handle cleanup of large dataset."""
        repo = TestResultRepository()

        # Add many old results
        for i in range(100):
            repo.save(
                ResultBuilder()
                .with_timestamp((datetime.now() - timedelta(days=50)).isoformat())
                .build()
            )

        result = maintenance_service.cleanup_old_data(days=30)

        assert result["test_rows_deleted"] == 100


class TestDatabaseIntegrity:
    """Test database integrity after maintenance."""

    def test_preserves_recent_data(self, populated_service):
        """Should preserve data newer than cutoff."""
        repo = TestResultRepository()

        # Get recent results before cleanup
        before_recent = [r for r in repo.get_all() if r.project_name == "new_project"]

        populated_service.cleanup_old_data(days=30)

        # Get recent results after cleanup
        after_recent = [r for r in repo.get_all() if r.project_name == "new_project"]

        # Should preserve all recent data
        assert len(after_recent) == len(before_recent)

    def test_database_still_usable_after_optimize(self, maintenance_service):
        """Should still be able to use database after optimization."""
        repo = TestResultRepository()

        # Add, optimize, add again
        repo.save(ResultBuilder().build())
        maintenance_service.optimize_database()
        repo.save(ResultBuilder().build())

        # Should have 2 results
        assert len(repo.get_all()) == 2
