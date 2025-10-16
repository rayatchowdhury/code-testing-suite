import difflib
import json
import logging
import os
import sqlite3
from datetime import datetime
from typing import Dict, List

from src.app.shared.constants import USER_DATA_DIR

# Import constants (Phase 3 refactoring)
from .constants import (
    DEFAULT_PROJECTS_LIMIT,
    DEFAULT_RESULTS_LIMIT,
    DEFAULT_SESSIONS_LIMIT,
    OLD_DATA_CLEANUP_DAYS,
    SUCCESS_RATE_PERCENTAGE_MULTIPLIER,
    TEST_TYPE_COMPARISON,
)

# Import models from separate module (Phase 1 refactoring)
from .models import FilesSnapshot, ProjectData, Session, TestResult

# Set up logger
logger = logging.getLogger(__name__)


class DatabaseError(Exception):
    """Custom exception for database operations"""


# Phase 6 (Issue #7): Removed TestCaseResult class - unused/dead code
# Individual test case results are now stored as JSON in TestResult.test_details


class DatabaseManager:
    """Manages SQLite database operations for the Code Testing Suite"""

    def __init__(self, db_path: str = None):
        if db_path is None:
            os.makedirs(USER_DATA_DIR, exist_ok=True)
            db_path = os.path.join(USER_DATA_DIR, "code_testing_suite.db")

        self.db_path = db_path
        self.connection = None
        self._initialize_database()

    def connect(self):
        """Establish database connection"""
        try:
            self.connection = sqlite3.connect(self.db_path)
            self.connection.row_factory = sqlite3.Row  # Enable column access by name
            logger.debug(f"Database connection established: {self.db_path}")
            return self.connection
        except sqlite3.Error as e:
            logger.error(f"Database connection error: {e}", exc_info=True)
            raise DatabaseError(f"Failed to connect to database: {e}") from e

    def close(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()
            self.connection = None

    def _initialize_database(self):
        """Create database tables if they don't exist"""
        connection = self.connect()
        if not connection:
            return

        try:
            cursor = connection.cursor()

            # Test Results table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS test_results (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    test_type TEXT NOT NULL,
                    file_path TEXT NOT NULL,
                    test_count INTEGER NOT NULL,
                    passed_tests INTEGER NOT NULL,
                    failed_tests INTEGER NOT NULL,
                    total_time REAL NOT NULL,
                    timestamp TEXT NOT NULL,
                    test_details TEXT,
                    project_name TEXT,
                    files_snapshot TEXT,
                    mismatch_analysis TEXT
                )
            """
            )

            # Migrate existing table to add new columns
            try:
                cursor.execute(
                    "ALTER TABLE test_results ADD COLUMN files_snapshot TEXT"
                )
            except sqlite3.OperationalError:
                pass  # Column already exists

            try:
                cursor.execute(
                    "ALTER TABLE test_results ADD COLUMN mismatch_analysis TEXT"
                )
            except sqlite3.OperationalError:
                pass  # Column already exists

            # Sessions table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_name TEXT NOT NULL,
                    open_files TEXT,
                    active_file TEXT,
                    timestamp TEXT NOT NULL,
                    project_name TEXT
                )
            """
            )

            # Projects table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS projects (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    project_name TEXT NOT NULL UNIQUE,
                    project_path TEXT NOT NULL,
                    last_accessed TEXT NOT NULL,
                    file_count INTEGER DEFAULT 0,
                    total_lines INTEGER DEFAULT 0,
                    languages TEXT
                )
            """
            )

            # Configuration table for database-stored settings
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS config (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
            """
            )

            connection.commit()
            logger.info("Database initialized successfully")

        except sqlite3.Error as e:
            logger.error(f"Database initialization error: {e}", exc_info=True)
            raise DatabaseError(f"Failed to initialize database: {e}") from e
        finally:
            self.close()

    def save_test_result(self, result: TestResult) -> int:
        """Save a test result to the database"""
        connection = self.connect()

        try:
            cursor = connection.cursor()
            cursor.execute(
                """
                INSERT INTO test_results 
                (test_type, file_path, test_count, passed_tests, failed_tests, 
                 total_time, timestamp, test_details, project_name, files_snapshot, mismatch_analysis)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    result.test_type,
                    result.file_path,
                    result.test_count,
                    result.passed_tests,
                    result.failed_tests,
                    result.total_time,
                    result.timestamp or datetime.now().isoformat(),
                    result.test_details,
                    result.project_name,
                    result.files_snapshot or "",
                    result.mismatch_analysis or "",
                ),
            )

            connection.commit()
            result_id = cursor.lastrowid
            logger.info(
                f"Saved test result #{result_id} (type={result.test_type}, project={result.project_name})"
            )
            return result_id

        except sqlite3.IntegrityError as e:
            logger.error(f"Integrity error saving test result: {e}", exc_info=True)
            raise DatabaseError(f"Invalid test result data: {e}") from e

        except sqlite3.Error as e:
            logger.error(f"Database error saving test result: {e}", exc_info=True)
            raise DatabaseError(f"Failed to save test result: {e}") from e

        finally:
            self.close()

    def get_test_results(
        self,
        test_type: str = None,
        project_name: str = None,
        days: int = None,
        file_name: str = None,
        status: str = None,
        limit: int = DEFAULT_RESULTS_LIMIT,
    ) -> List[TestResult]:
        """
        Retrieve test results from the database with efficient SQL filtering

        Phase 4 (Issue #10): Added SQL-based filtering for days, file_name, and status
        instead of post-processing in Python for better performance
        """
        connection = self.connect()

        try:
            cursor = connection.cursor()
            query = "SELECT * FROM test_results"
            params = []

            conditions = []
            if test_type:
                conditions.append("test_type = ?")
                params.append(test_type)
            if project_name:
                conditions.append("project_name LIKE ?")
                params.append(f"%{project_name}%")
            if days:
                # Phase 4 (Issue #10): SQL date filtering
                from datetime import timedelta

                cutoff = (datetime.now() - timedelta(days=days)).isoformat()
                conditions.append("timestamp >= ?")
                params.append(cutoff)
            if file_name:
                # Phase 4 (Issue #10): SQL file name filtering
                conditions.append("file_path LIKE ?")
                params.append(f"%{file_name}%")
            if status == "passed":
                # Phase 4 (Issue #10): SQL status filtering
                conditions.append("passed_tests = test_count")
            elif status == "failed":
                conditions.append("failed_tests > 0")

            if conditions:
                query += " WHERE " + " AND ".join(conditions)

            query += " ORDER BY timestamp DESC LIMIT ?"
            params.append(limit)

            cursor.execute(query, params)
            rows = cursor.fetchall()

            results = []
            for row in rows:
                result = TestResult(
                    id=row["id"],
                    test_type=row["test_type"],
                    file_path=row["file_path"],
                    test_count=row["test_count"],
                    passed_tests=row["passed_tests"],
                    failed_tests=row["failed_tests"],
                    total_time=row["total_time"],
                    timestamp=row["timestamp"],
                    test_details=row["test_details"],
                    project_name=row["project_name"],
                    files_snapshot=(
                        row["files_snapshot"] if "files_snapshot" in row.keys() else ""
                    ),
                    mismatch_analysis=(
                        row["mismatch_analysis"]
                        if "mismatch_analysis" in row.keys()
                        else ""
                    ),
                )
                results.append(result)

            logger.info(
                f"Retrieved {len(results)} test results (type={test_type}, project={project_name}, days={days}, file={file_name}, status={status}, limit={limit})"
            )
            return results

        except sqlite3.Error as e:
            logger.error(f"Error retrieving test results: {e}", exc_info=True)
            raise DatabaseError(f"Failed to retrieve test results: {e}") from e

        finally:
            self.close()

    def save_session(self, session: Session) -> int:
        """Save an editor session to the database"""
        connection = self.connect()

        try:
            cursor = connection.cursor()
            cursor.execute(
                """
                INSERT INTO sessions 
                (session_name, open_files, active_file, timestamp, project_name)
                VALUES (?, ?, ?, ?, ?)
            """,
                (
                    session.session_name,
                    session.open_files,
                    session.active_file,
                    session.timestamp or datetime.now().isoformat(),
                    session.project_name,
                ),
            )

            connection.commit()
            session_id = cursor.lastrowid
            logger.info(
                f"Saved session #{session_id} (name={session.session_name}, project={session.project_name})"
            )
            return session_id

        except sqlite3.Error as e:
            logger.error(f"Error saving session: {e}", exc_info=True)
            raise DatabaseError(f"Failed to save session: {e}") from e

        finally:
            self.close()

    def get_sessions(
        self, project_name: str = None, limit: int = DEFAULT_SESSIONS_LIMIT
    ) -> List[Session]:
        """Retrieve editor sessions from the database"""
        connection = self.connect()
        if not connection:
            return []

        try:
            cursor = connection.cursor()
            if project_name:
                cursor.execute(
                    """
                    SELECT * FROM sessions 
                    WHERE project_name = ? 
                    ORDER BY timestamp DESC 
                    LIMIT ?
                """,
                    (project_name, limit),
                )
            else:
                cursor.execute(
                    """
                    SELECT * FROM sessions 
                    ORDER BY timestamp DESC 
                    LIMIT ?
                """,
                    (limit,),
                )

            rows = cursor.fetchall()

            sessions = []
            for row in rows:
                session = Session(
                    id=row["id"],
                    session_name=row["session_name"],
                    open_files=row["open_files"],
                    active_file=row["active_file"],
                    timestamp=row["timestamp"],
                    project_name=row["project_name"],
                )
                sessions.append(session)

            logger.info(
                f"Retrieved {len(sessions)} sessions (project={project_name}, limit={limit})"
            )
            return sessions

        except sqlite3.Error as e:
            logger.error(f"Error retrieving sessions: {e}", exc_info=True)
            raise DatabaseError(f"Failed to retrieve sessions: {e}") from e

        finally:
            self.close()

    def save_project_data(self, project: ProjectData) -> int:
        """Save or update project data"""
        connection = self.connect()

        try:
            cursor = connection.cursor()
            cursor.execute(
                """
                INSERT OR REPLACE INTO projects 
                (project_name, project_path, last_accessed, file_count, total_lines, languages)
                VALUES (?, ?, ?, ?, ?, ?)
            """,
                (
                    project.project_name,
                    project.project_path,
                    project.last_accessed or datetime.now().isoformat(),
                    project.file_count,
                    project.total_lines,
                    project.languages,
                ),
            )

            connection.commit()
            project_id = cursor.lastrowid
            logger.info(
                f"Saved project data #{project_id} (name={project.project_name}, path={project.project_path})"
            )
            return project_id

        except sqlite3.Error as e:
            logger.error(f"Error saving project data: {e}", exc_info=True)
            raise DatabaseError(f"Failed to save project data: {e}") from e

        finally:
            self.close()

    def get_projects(self, limit: int = DEFAULT_PROJECTS_LIMIT) -> List[ProjectData]:
        """Retrieve project data from the database"""
        connection = self.connect()
        if not connection:
            return []

        try:
            cursor = connection.cursor()
            cursor.execute(
                """
                SELECT * FROM projects 
                ORDER BY last_accessed DESC 
                LIMIT ?
            """,
                (limit,),
            )

            rows = cursor.fetchall()

            projects = []
            for row in rows:
                project = ProjectData(
                    id=row["id"],
                    project_name=row["project_name"],
                    project_path=row["project_path"],
                    last_accessed=row["last_accessed"],
                    file_count=row["file_count"],
                    total_lines=row["total_lines"],
                    languages=row["languages"],
                )
                projects.append(project)

            logger.info(f"Retrieved {len(projects)} projects (limit={limit})")
            return projects

        except sqlite3.Error as e:
            logger.error(f"Error retrieving projects: {e}", exc_info=True)
            raise DatabaseError(f"Failed to retrieve projects: {e}") from e

        finally:
            self.close()

    def get_test_statistics(self, project_name: str = None) -> Dict:
        """Get test statistics and analytics"""
        connection = self.connect()
        if not connection:
            return {}

        try:
            cursor = connection.cursor()

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

        except sqlite3.Error as e:
            logger.error(f"Error getting test statistics: {e}", exc_info=True)
            raise DatabaseError(f"Failed to retrieve test statistics: {e}") from e

        finally:
            self.close()

    def cleanup_old_data(self, days: int = OLD_DATA_CLEANUP_DAYS):
        """Clean up old data to maintain database size"""
        connection = self.connect()

        try:
            cursor = connection.cursor()
            # Use timedelta for proper date arithmetic
            from datetime import timedelta

            cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()

            # Clean old test results
            cursor.execute(
                """
                DELETE FROM test_results 
                WHERE timestamp < ?
            """,
                (cutoff_date,),
            )
            test_rows_deleted = cursor.rowcount

            # Clean old sessions
            cursor.execute(
                """
                DELETE FROM sessions 
                WHERE timestamp < ?
            """,
                (cutoff_date,),
            )
            session_rows_deleted = cursor.rowcount

            connection.commit()

            # VACUUM the database to reclaim space after deletions
            if test_rows_deleted > 0 or session_rows_deleted > 0:
                cursor.execute("VACUUM")

            logger.info(
                f"Cleaned up old data (days={days}, test_results={test_rows_deleted}, sessions={session_rows_deleted}, database vacuumed)"
            )

        except sqlite3.Error as e:
            logger.error(f"Error cleaning up old data: {e}", exc_info=True)
            raise DatabaseError(f"Failed to cleanup old data: {e}") from e

        finally:
            self.close()

    def delete_test_result(self, result_id: int):
        """Delete a specific test result by ID

        Phase 4 (Issue #14): Individual test result deletion with CASCADE

        Args:
            result_id: The ID of the test result to delete

        Returns:
            bool: True if deletion was successful, False if result not found

        Raises:
            DatabaseError: If deletion fails due to database error
        """
        connection = self.connect()

        try:
            cursor = connection.cursor()

            # Check if result exists
            cursor.execute("SELECT id FROM test_results WHERE id = ?", (result_id,))
            if not cursor.fetchone():
                logger.warning(f"Test result ID {result_id} not found")
                return False

            # Delete the result (CASCADE will handle related records)
            cursor.execute("DELETE FROM test_results WHERE id = ?", (result_id,))

            connection.commit()
            logger.info(f"Deleted test result ID {result_id}")
            return True

        except sqlite3.Error as e:
            logger.error(
                f"Error deleting test result ID {result_id}: {e}", exc_info=True
            )
            raise DatabaseError(f"Failed to delete test result: {e}") from e

        finally:
            self.close()

    def delete_all_data(self, confirm: bool = False):
        """Delete all data from the database

        Args:
            confirm: Must be True to actually delete data (safety check)
        """
        if not confirm:
            logger.warning(
                "delete_all_data called without confirm=True, operation aborted"
            )
            return False

        connection = self.connect()

        try:
            cursor = connection.cursor()

            # Get count of records before deletion
            cursor.execute("SELECT COUNT(*) FROM test_results")
            test_results_count = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM sessions")
            sessions_count = cursor.fetchone()[0]

            # Delete all test results
            cursor.execute("DELETE FROM test_results")

            # Delete all sessions
            cursor.execute("DELETE FROM sessions")

            # Reset auto-increment counters
            cursor.execute("DELETE FROM sqlite_sequence WHERE name='test_results'")
            cursor.execute("DELETE FROM sqlite_sequence WHERE name='sessions'")

            connection.commit()

            # VACUUM the database to reclaim space
            # This shrinks the database file by removing deleted data
            cursor.execute("VACUUM")

            logger.warning(
                f"Deleted all database data: {test_results_count} test results, {sessions_count} sessions, ID counters reset, database vacuumed"
            )

            return True

        except sqlite3.Error as e:
            logger.error(f"Error deleting all data: {e}", exc_info=True)
            connection.rollback()
            raise DatabaseError(f"Failed to delete all data: {e}") from e

        finally:
            self.close()

    def migrate_old_results_to_new_format(self, dry_run: bool = False):
        """Migrate all old FilesSnapshot format results to new format.

        Iterates through all test results, detects old format (generator_code, correct_code, etc.),
        converts to new format using FilesSnapshot.from_json() with automatic migration,
        and updates the database.

        Args:
            dry_run: If True, only reports what would be migrated without making changes

        Returns:
            dict: Migration statistics
                - total_results: Total number of results in database
                - old_format_count: Number of results with old format
                - migrated_count: Number successfully migrated
                - failed_count: Number that failed migration
                - skipped_count: Number already in new format
                - failures: List of (result_id, error_message) tuples
        """
        connection = self.connect()

        try:
            cursor = connection.cursor()

            # Get all test results
            cursor.execute(
                'SELECT id, files_snapshot FROM test_results WHERE files_snapshot IS NOT NULL AND files_snapshot != ""'
            )
            all_results = cursor.fetchall()

            total_results = len(all_results)
            old_format_count = 0
            migrated_count = 0
            failed_count = 0
            skipped_count = 0
            failures = []

            logger.info(
                f"Starting FilesSnapshot migration - found {total_results} results with file data"
            )

            for result_id, files_snapshot_json in all_results:
                try:
                    # Parse the snapshot
                    snapshot_data = json.loads(files_snapshot_json)

                    # Detect format - old format has generator_code/correct_code keys
                    is_old_format = any(
                        key.endswith("_code") for key in snapshot_data.keys()
                    )

                    if not is_old_format:
                        # Already new format
                        skipped_count += 1
                        logger.debug(
                            f"Result #{result_id}: Already in new format, skipping"
                        )
                        continue

                    old_format_count += 1
                    logger.info(
                        f"Result #{result_id}: Detected old format, migrating..."
                    )

                    if dry_run:
                        logger.info(f"  [DRY RUN] Would migrate result #{result_id}")
                        migrated_count += 1
                        continue

                    # Use FilesSnapshot.from_json() to auto-migrate
                    snapshot = FilesSnapshot.from_json(files_snapshot_json)

                    # Convert back to new format JSON
                    new_json = snapshot.to_json()

                    # Update database
                    cursor.execute(
                        "UPDATE test_results SET files_snapshot = ? WHERE id = ?",
                        (new_json, result_id),
                    )

                    migrated_count += 1
                    logger.info(f"  ✓ Result #{result_id}: Successfully migrated")
                    logger.debug(f"    Old keys: {list(snapshot_data.keys())}")
                    logger.debug(f"    New files: {list(snapshot.files.keys())}")

                except json.JSONDecodeError as e:
                    failed_count += 1
                    error_msg = f"Invalid JSON: {str(e)}"
                    failures.append((result_id, error_msg))
                    logger.error(f"  ✗ Result #{result_id}: {error_msg}")

                except Exception as e:
                    failed_count += 1
                    error_msg = str(e)
                    failures.append((result_id, error_msg))
                    logger.error(
                        f"  ✗ Result #{result_id}: Migration failed - {error_msg}"
                    )

            if not dry_run and (migrated_count > 0 or failed_count > 0):
                connection.commit()
                logger.info(
                    f"Migration committed: {migrated_count} migrated, {failed_count} failed"
                )

            stats = {
                "total_results": total_results,
                "old_format_count": old_format_count,
                "migrated_count": migrated_count,
                "failed_count": failed_count,
                "skipped_count": skipped_count,
                "failures": failures,
            }

            # Log summary
            if dry_run:
                logger.info(f"\n{'='*60}")
                logger.info("MIGRATION DRY RUN SUMMARY")
                logger.info(f"{'='*60}")
            else:
                logger.info(f"\n{'='*60}")
                logger.info("MIGRATION COMPLETE")
                logger.info(f"{'='*60}")

            logger.info(f"Total results checked: {total_results}")
            logger.info(f"Old format detected: {old_format_count}")
            logger.info(f"Successfully migrated: {migrated_count}")
            logger.info(f"Already new format: {skipped_count}")
            logger.info(f"Failed: {failed_count}")

            if failures:
                logger.warning("\nFailed migrations:")
                for result_id, error in failures:
                    logger.warning(f"  - Result #{result_id}: {error}")

            logger.info(f"{'='*60}\n")

            return stats

        except sqlite3.Error as e:
            logger.error(f"Database error during migration: {e}", exc_info=True)
            connection.rollback()
            raise DatabaseError(f"Migration failed: {e}") from e

        finally:
            self.close()

    def optimize_database(self):
        """Optimize database by reclaiming unused space (VACUUM)

        This should be called after deleting large amounts of data.
        VACUUM rebuilds the database file, reclaiming space from deleted records.

        Returns:
            dict: Statistics before and after optimization (size reduction info)
        """
        connection = self.connect()

        try:
            # Get size before
            size_before = 0
            if os.path.exists(self.db_path):
                size_before = os.path.getsize(self.db_path)

            cursor = connection.cursor()

            # VACUUM to reclaim space
            cursor.execute("VACUUM")

            # Get size after
            size_after = 0
            if os.path.exists(self.db_path):
                size_after = os.path.getsize(self.db_path)

            space_saved = size_before - size_after
            space_saved_mb = space_saved / (1024 * 1024)

            logger.info(
                f"Database optimized: {size_before/1024/1024:.2f} MB → {size_after/1024/1024:.2f} MB (saved {space_saved_mb:.2f} MB)"
            )

            return {
                "size_before_bytes": size_before,
                "size_after_bytes": size_after,
                "space_saved_bytes": space_saved,
                "size_before_mb": round(size_before / (1024 * 1024), 2),
                "size_after_mb": round(size_after / (1024 * 1024), 2),
                "space_saved_mb": round(space_saved_mb, 2),
            }

        except sqlite3.Error as e:
            logger.error(f"Error optimizing database: {e}", exc_info=True)
            raise DatabaseError(f"Failed to optimize database: {e}") from e

        finally:
            self.close()

    def get_database_stats(self):
        """Get statistics about the database contents"""
        connection = self.connect()
        if not connection:
            return None

        try:
            cursor = connection.cursor()

            # Count records in each table
            cursor.execute("SELECT COUNT(*) FROM test_results")
            test_results_count = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM sessions")
            sessions_count = cursor.fetchone()[0]

            # Get date range of data
            cursor.execute("SELECT MIN(timestamp), MAX(timestamp) FROM test_results")
            result = cursor.fetchone()
            oldest_test = result[0] if result[0] else "No data"
            newest_test = result[1] if result[1] else "No data"

            cursor.execute("SELECT MIN(timestamp), MAX(timestamp) FROM sessions")
            result = cursor.fetchone()
            oldest_session = result[0] if result[0] else "No data"
            newest_session = result[1] if result[1] else "No data"

            # Get database file size
            db_size = 0
            if os.path.exists(self.db_path):
                db_size = os.path.getsize(self.db_path)
                db_size_mb = db_size / (1024 * 1024)  # Convert to MB

            stats = {
                "test_results_count": test_results_count,
                "sessions_count": sessions_count,
                "oldest_test": oldest_test,
                "newest_test": newest_test,
                "oldest_session": oldest_session,
                "newest_session": newest_session,
                "database_size_bytes": db_size,
                "database_size_mb": round(db_size_mb, 2) if db_size > 0 else 0,
            }

            logger.info(
                f"Database stats: {test_results_count} test results, {sessions_count} sessions, {stats['database_size_mb']} MB"
            )
            return stats

        except sqlite3.Error as e:
            logger.error(f"Error getting database stats: {e}", exc_info=True)
            raise DatabaseError(f"Failed to retrieve database stats: {e}") from e

        finally:
            self.close()

    @staticmethod
    def analyze_output_mismatch(expected: str, actual: str) -> Dict:
        """Analyze differences between expected and actual output"""
        expected_lines = expected.strip().split("\n")
        actual_lines = actual.strip().split("\n")

        # Generate unified diff
        diff = list(
            difflib.unified_diff(
                expected_lines,
                actual_lines,
                fromfile="Expected Output",
                tofile="Actual Output",
                lineterm="",
                n=3,
            )
        )

        # Character-by-character diff for precise analysis
        char_diff = []
        for i, (exp_char, act_char) in enumerate(zip(expected, actual)):
            if exp_char != act_char:
                char_diff.append(
                    {"position": i, "expected": exp_char, "actual": act_char}
                )

        # Line-by-line analysis
        line_analysis = []
        max_lines = max(len(expected_lines), len(actual_lines))

        for i in range(max_lines):
            exp_line = expected_lines[i] if i < len(expected_lines) else ""
            act_line = actual_lines[i] if i < len(actual_lines) else ""

            if exp_line != act_line:
                line_analysis.append(
                    {
                        "line_number": i + 1,
                        "expected": exp_line,
                        "actual": act_line,
                        "type": (
                            "modified"
                            if exp_line and act_line
                            else ("missing" if exp_line else "extra")
                        ),
                    }
                )

        return {
            "unified_diff": diff,
            "character_differences": char_diff,
            "line_differences": line_analysis,
            "summary": {
                "total_char_differences": len(char_diff),
                "total_line_differences": len(line_analysis),
                "expected_length": len(expected),
                "actual_length": len(actual),
                "expected_lines": len(expected_lines),
                "actual_lines": len(actual_lines),
            },
        }

    @staticmethod
    def create_files_snapshot(
        workspace_dir: str, test_type: str = TEST_TYPE_COMPARISON
    ) -> FilesSnapshot:
        """
        Create a snapshot of relevant files for the specified test type.

        NEW BEHAVIOR: Only saves files needed for the test type with full filenames and extensions.
        - Comparison/Comparator: generator, correct, test (3 files)
        - Validation/Validator: generator, validator, test (3 files)
        - Benchmark/Benchmarker: generator, test (2 files)

        Args:
            workspace_dir: Root workspace directory (~/.code_testing_suite/workspace)
            test_type: Test type ('comparison', 'validation', 'benchmark', or 'comparator', 'validator', 'benchmarker')

        Returns:
            FilesSnapshot: Snapshot with only relevant files, full filenames, and per-file metadata
        """
        # Normalize test type names
        test_type_map = {
            "comparison": "comparator",
            "comparator": "comparator",
            "validation": "validator",
            "validator": "validator",
            "benchmark": "benchmarker",
            "benchmarker": "benchmarker",
            "stress": "comparator",  # Legacy support
        }

        test_subdir = test_type_map.get(test_type.lower(), "comparator")
        normalized_test_type = {
            "comparator": "comparison",
            "validator": "validation",
            "benchmarker": "benchmark",
        }[test_subdir]

        snapshot = FilesSnapshot(test_type=normalized_test_type)

        # Define required files per test type
        required_roles = {
            "comparator": ["generator", "correct", "test"],
            "validator": ["generator", "validator", "test"],
            "benchmarker": ["generator", "test"],
        }

        required = required_roles.get(test_subdir, ["generator", "test"])
        test_type_dir = os.path.join(workspace_dir, test_subdir)

        try:
            if not os.path.exists(test_type_dir):
                logger.warning(f"Test type directory not found: {test_type_dir}")
                return snapshot

            # Track languages to determine primary
            language_counts = {"cpp": 0, "py": 0, "java": 0}

            # Track which roles have been filled (only one file per role)
            roles_found = set()

            # Read all source files in test type directory
            for filename in os.listdir(test_type_dir):
                filepath = os.path.join(test_type_dir, filename)

                # Skip directories (inputs/outputs)
                if os.path.isdir(filepath):
                    continue

                # Only process source code files
                if not filename.endswith((".cpp", ".h", ".py", ".java")):
                    continue

                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        content = f.read()

                    # Detect language from extension
                    if filename.endswith(".py"):
                        language = "py"
                    elif filename.endswith(".java"):
                        language = "java"
                    else:
                        language = "cpp"

                    # Determine file role
                    base_name = filename.split(".")[0].lower()
                    role = None

                    # Check if this is a required file (only if role not already found)
                    for req_role in required:
                        if req_role in base_name and req_role not in roles_found:
                            role = req_role
                            roles_found.add(req_role)
                            break

                    # Only add files that match required roles
                    if role is not None:
                        snapshot.files[filename] = {
                            "content": content,
                            "language": language,
                            "role": role,
                        }
                        language_counts[language] += 1

                except Exception as e:
                    logger.warning(f"Error reading file {filename}: {e}")

            # Determine primary language (most common)
            if language_counts:
                snapshot.primary_language = max(
                    language_counts, key=language_counts.get
                )

            logger.info(
                f"Created snapshot for {test_type} ({test_subdir}): {len(snapshot.files)} files, primary language: {snapshot.primary_language}"
            )

            return snapshot

        except Exception as e:
            logger.error(f"Error creating files snapshot: {e}", exc_info=True)
            return snapshot
