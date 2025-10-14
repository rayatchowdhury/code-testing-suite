"""
Database persistence layer.

Refactored architecture with backward compatibility.
"""

# Constants
from . import constants

# Connection
from .connection import DatabaseConnection

# Exceptions
from .exceptions import ConnectionError as DBConnectionError
from .exceptions import (
    DatabaseError,
    RepositoryError,
    ValidationError,
)

# Models
from .models import FilesSnapshot, ProjectData, Session, TestResult

# Repositories
from .repositories import BaseRepository, TestResultRepository

# Services
from .services import (
    DatabaseMaintenanceService,
    DatabaseStatsService,
    FilesSnapshotService,
)


# Backward-compatible facade
class DatabaseManager:
    """
    Backward-compatible facade for old code.

    Delegates to new architecture but maintains old API.
    This allows existing code to continue working while
    new code can use repositories and services directly.
    """

    def __init__(self, db_path: str = None):
        """
        Initialize with new architecture.

        Args:
            db_path: Optional database path (uses default if None)
        """
        self.db = DatabaseConnection(db_path) if db_path else DatabaseConnection()
        self.test_repo = TestResultRepository()
        self.stats_service = DatabaseStatsService()
        self.maintenance_service = DatabaseMaintenanceService()
        # Store db_path for compatibility
        self.db_path = self.db.db_path
        self.connection = None  # For backward compatibility

    # Connection management (for backward compatibility)
    def connect(self):
        """Get connection (deprecated - use context manager)."""
        return self.db._connection

    def close(self):
        """Close connection (deprecated - handled automatically)."""
        pass  # Connection is managed by singleton

    # TestResult operations - delegate to repository
    def save_test_result(self, result: TestResult) -> int:
        """Save test result."""
        return self.test_repo.save(result)

    def get_test_results(
        self,
        test_type: str = None,
        project_name: str = None,
        days: int = None,
        file_name: str = None,
        status: str = None,
        limit: int = 100,
    ):
        """Get test results with filters."""
        return self.test_repo.get_all(
            test_type=test_type,
            project_name=project_name,
            days=days,
            file_name=file_name,
            status=status,
            limit=limit,
        )

    def delete_test_result(self, result_id: int) -> bool:
        """Delete test result by ID."""
        return self.test_repo.delete(result_id)

    def delete_all_data(self, confirm: bool = False) -> bool:
        """Delete all test results (requires confirmation)."""
        return self.test_repo.delete_all(confirm=confirm)

    # Session operations - stub for backward compatibility
    def save_session(self, session: Session) -> int:
        """Save session (stub - not yet implemented)."""
        raise NotImplementedError("Session repository not yet migrated")

    def get_sessions(self, project_name: str = None, limit: int = 100):
        """Get sessions (stub - not yet implemented)."""
        raise NotImplementedError("Session repository not yet migrated")

    # Project operations - stub for backward compatibility
    def save_project_data(self, project: ProjectData) -> int:
        """Save project data (stub - not yet implemented)."""
        raise NotImplementedError("Project repository not yet migrated")

    def get_projects(self, limit: int = 100):
        """Get projects (stub - not yet implemented)."""
        raise NotImplementedError("Project repository not yet migrated")

    # Statistics - delegate to service
    def get_database_stats(self):
        """Get database statistics."""
        return self.stats_service.get_database_stats()

    def get_test_statistics(self, project_name: str = None):
        """Get test statistics and analytics."""
        return self.stats_service.get_test_statistics(project_name=project_name)

    # Maintenance - delegate to service
    def cleanup_old_data(self, days: int = None):
        """Clean up old data."""
        if days is None:
            days = constants.DEFAULT_CLEANUP_DAYS
        return self.maintenance_service.cleanup_old_data(days=days)

    def optimize_database(self):
        """Optimize database by running VACUUM."""
        return self.maintenance_service.optimize_database()

    # Migration (deprecated - no longer needed)
    def migrate_old_results_to_new_format(self, dry_run: bool = False):
        """Migration (deprecated - no longer needed)."""
        return {"status": "skipped", "message": "Migration no longer needed"}

    # Static methods - delegate to service
    @staticmethod
    def create_files_snapshot(
        workspace_dir: str, test_type: str = constants.TEST_TYPE_COMPARISON
    ):
        """Create files snapshot."""
        return FilesSnapshotService.create_snapshot(workspace_dir, test_type)

    @staticmethod
    def analyze_output_mismatch(expected: str, actual: str):
        """Analyze output mismatch."""
        return FilesSnapshotService.analyze_output_mismatch(expected, actual)


__all__ = [
    # Models
    "FilesSnapshot",
    "TestResult",
    "Session",
    "ProjectData",
    # Connection
    "DatabaseConnection",
    # Repositories
    "BaseRepository",
    "TestResultRepository",
    # Services
    "FilesSnapshotService",
    "DatabaseStatsService",
    "DatabaseMaintenanceService",
    # Exceptions
    "DatabaseError",
    "DBConnectionError",
    "RepositoryError",
    "ValidationError",
    # Constants module
    "constants",
    # Backward compatibility
    "DatabaseManager",
]
