"""
Thread-safe singleton database connection manager.

Fixes issues:
- #1: Multiple DatabaseManager instances
- #3: No thread safety
- #2: Connection lifecycle anti-pattern

Created in Phase 2 refactoring.
"""

import logging
import os
import sqlite3
import threading
from contextlib import contextmanager
from pathlib import Path
from typing import Optional

from src.app.shared.constants import USER_DATA_DIR

from .exceptions import ConnectionError, DatabaseError

logger = logging.getLogger(__name__)


class DatabaseConnection:
    """
    Singleton database connection manager with thread safety.

    Features:
    - Singleton pattern (one instance per process)
    - Thread-safe operations (threading.Lock)
    - Context manager support
    - Auto-creates database and tables
    - Transaction management with automatic rollback

    Usage:
        db = DatabaseConnection()
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM test_results")
    """

    _instance: Optional["DatabaseConnection"] = None
    _lock = threading.Lock()  # For singleton creation
    _connection_lock = threading.Lock()  # For database operations

    def __new__(cls, db_path: str = None):
        """Ensure only one instance exists (singleton)."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:  # Double-check locking
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self, db_path: str = None):
        """Initialize connection manager (only once)."""
        # Thread-safe initialization check
        with self._lock:
            if self._initialized:
                return

            if db_path is None:
                os.makedirs(USER_DATA_DIR, exist_ok=True)
                db_path = os.path.join(USER_DATA_DIR, "code_testing_suite.db")

            self.db_path = db_path
            self._connection: Optional[sqlite3.Connection] = None
            self._init_database()
            self._initialized = True

            logger.info(f"DatabaseConnection initialized (singleton): {self.db_path}")

    def _init_database(self):
        """Create database and tables if they don't exist."""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # Drop unused tables from old architecture
            cursor.execute("DROP TABLE IF EXISTS projects")
            cursor.execute("DROP TABLE IF EXISTS config")
            logger.info("Dropped unused tables: projects, config")

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

            conn.commit()
            logger.info("Database tables initialized")

    @contextmanager
    def get_connection(self):
        """
        Thread-safe connection context manager.

        Provides automatic transaction management:
        - Commits on success
        - Rolls back on error
        - Thread-safe with lock

        Usage:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(...)

        Raises:
            ConnectionError: If connection fails
            DatabaseError: If operation fails
        """
        with self._connection_lock:
            if self._connection is None:
                try:
                    self._connection = sqlite3.connect(
                        self.db_path, check_same_thread=False  # Allow multi-threading
                    )
                    self._connection.row_factory = sqlite3.Row
                except sqlite3.Error as e:
                    raise ConnectionError(f"Failed to connect: {e}") from e

            try:
                yield self._connection
            except sqlite3.DatabaseError as e:
                # Corrupted database raises DatabaseError, convert to ConnectionError
                self._connection.rollback()
                logger.error(f"Transaction rolled back (corrupted database): {e}")
                raise ConnectionError(
                    f"Database operation failed (corrupted database): {e}"
                ) from e
            except Exception as e:
                self._connection.rollback()
                logger.error(f"Transaction rolled back: {e}")
                raise DatabaseError(f"Database operation failed: {e}") from e
            else:
                self._connection.commit()

    def close(self):
        """Close the connection."""
        with self._connection_lock:
            if self._connection:
                self._connection.close()
                self._connection = None
                logger.info("Database connection closed")

    @classmethod
    def reset_instance(cls):
        """Reset singleton (for testing only)."""
        with cls._lock:
            if cls._instance:
                cls._instance.close()
                cls._instance = None
            # Reset _initialized flag
            cls._instance = None


# Convenience function for backward compatibility
def get_db_connection() -> DatabaseConnection:
    """Get database connection instance (singleton)."""
    return DatabaseConnection()
