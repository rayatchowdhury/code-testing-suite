"""Service for database statistics and analytics."""

import os
import logging
from typing import Dict, Optional

from ..connection import DatabaseConnection
from ..repositories.test_result_repository import TestResultRepository
from ..constants import SUCCESS_RATE_PERCENTAGE_MULTIPLIER

logger = logging.getLogger(__name__)


class DatabaseStatsService:
    """Service for database statistics."""

    def __init__(self):
        self.db = DatabaseConnection()
        self.test_repo = TestResultRepository()

    def get_database_stats(self) -> Dict:
        """
        Get comprehensive database statistics.

        Returns:
            Dict containing:
                - test_results_count: Number of test results
                - sessions_count: Number of sessions
                - oldest_test: Timestamp of oldest test
                - newest_test: Timestamp of newest test
                - oldest_session: Timestamp of oldest session
                - newest_session: Timestamp of newest session
                - database_size_bytes: Database file size in bytes
                - database_size_mb: Database file size in MB
        """
        with self.db.get_connection() as conn:
            cursor = conn.cursor()

            # Count records in each table
            cursor.execute("SELECT COUNT(*) as count FROM test_results")
            result = cursor.fetchone()
            test_results_count = dict(result)["count"] if result else 0

            cursor.execute("SELECT COUNT(*) as count FROM sessions")
            result = cursor.fetchone()
            sessions_count = dict(result)["count"] if result else 0

            # Get date range of data
            cursor.execute(
                "SELECT MIN(timestamp) as min_ts, MAX(timestamp) as max_ts FROM test_results"
            )
            result = cursor.fetchone()
            if result:
                row_dict = dict(result)
                oldest_test = row_dict["min_ts"] if row_dict["min_ts"] else "No data"
                newest_test = row_dict["max_ts"] if row_dict["max_ts"] else "No data"
            else:
                oldest_test = "No data"
                newest_test = "No data"

            cursor.execute(
                "SELECT MIN(timestamp) as min_ts, MAX(timestamp) as max_ts FROM sessions"
            )
            result = cursor.fetchone()
            if result:
                row_dict = dict(result)
                oldest_session = row_dict["min_ts"] if row_dict["min_ts"] else "No data"
                newest_session = row_dict["max_ts"] if row_dict["max_ts"] else "No data"
            else:
                oldest_session = "No data"
                newest_session = "No data"

            # Get database file size
            db_size = 0
            if os.path.exists(self.db.db_path):
                db_size = os.path.getsize(self.db.db_path)

            stats = {
                "test_results_count": test_results_count,
                "sessions_count": sessions_count,
                "oldest_test": oldest_test,
                "newest_test": newest_test,
                "oldest_session": oldest_session,
                "newest_session": newest_session,
                "database_size_bytes": db_size,
                "database_size_mb": (
                    round(db_size / (1024 * 1024), 2) if db_size > 0 else 0
                ),
            }

            logger.info(
                f"Database stats: {test_results_count} test results, {sessions_count} sessions, {stats['database_size_mb']} MB"
            )
            return stats

    def get_test_statistics(self, project_name: Optional[str] = None) -> Dict:
        """
        Get test statistics and analytics.

        Args:
            project_name: Optional project name to filter statistics

        Returns:
            Dict containing:
                - total_tests: Total number of tests
                - by_type: Test count breakdown by test type
                - success_rate: Overall success rate percentage
        """
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            conn.row_factory = lambda cursor, row: {
                col[0]: row[idx] for idx, col in enumerate(cursor.description)
            }
            cursor = conn.cursor()

            stats = {}

            # Basic counts
            base_query = "SELECT COUNT(*) as count FROM test_results"
            if project_name:
                base_query += " WHERE project_name = ?"
                params = (project_name,)
            else:
                params = ()

            cursor.execute(base_query, params)
            stats["total_tests"] = cursor.fetchone()["count"]

            # Test type breakdown
            type_query = "SELECT test_type, COUNT(*) as count FROM test_results"
            if project_name:
                type_query += " WHERE project_name = ?"
            type_query += " GROUP BY test_type"

            cursor.execute(type_query, params)
            stats["by_type"] = {
                row["test_type"]: row["count"] for row in cursor.fetchall()
            }

            # Success rate
            success_query = """
                SELECT 
                    SUM(passed_tests) as total_passed,
                    SUM(test_count) as total_attempted
                FROM test_results
            """
            if project_name:
                success_query += " WHERE project_name = ?"

            cursor.execute(success_query, params)
            result = cursor.fetchone()
            if result and result["total_attempted"] and result["total_attempted"] > 0:
                stats["success_rate"] = (
                    result["total_passed"] / result["total_attempted"]
                ) * SUCCESS_RATE_PERCENTAGE_MULTIPLIER
            else:
                stats["success_rate"] = 0

            logger.info(
                f"Retrieved test statistics (project={project_name}, total_tests={stats.get('total_tests', 0)})"
            )
            return stats
