"""
Unit tests for DatabaseConnection singleton.

Tests singleton pattern, thread safety, and connection lifecycle management.
This tests the refactored architecture that fixes:
- Multiple DatabaseManager instances (#1)
- No thread safety (#3)
- Connection lifecycle anti-pattern (#2)
"""

import os
import sqlite3
import threading
import time
from pathlib import Path

import pytest

from src.app.persistence.database.connection import DatabaseConnection
from src.app.persistence.database.exceptions import ConnectionError, DatabaseError


@pytest.fixture
def temp_db(tmp_path):
    """Create temporary database for testing."""
    db_path = tmp_path / "test.db"
    yield str(db_path)
    # Cleanup: reset singleton after each test
    DatabaseConnection.reset_instance()


class TestDatabaseConnectionSingleton:
    """Test singleton pattern enforcement."""

    def test_returns_same_instance(self, temp_db):
        """Should return same instance on multiple calls."""
        conn1 = DatabaseConnection(temp_db)
        conn2 = DatabaseConnection(temp_db)

        assert conn1 is conn2

    def test_same_instance_with_different_paths(self, temp_db, tmp_path):
        """Should return same instance even with different path (singleton)."""
        conn1 = DatabaseConnection(temp_db)

        # Try to create with different path
        other_db = str(tmp_path / "other.db")
        conn2 = DatabaseConnection(other_db)

        # Should still be the same instance
        assert conn1 is conn2
        # Should keep original path
        assert conn1.db_path == temp_db

    def test_thread_safe_singleton(self, temp_db):
        """Should be thread-safe singleton creation."""
        instances = []

        def get_connection():
            instances.append(DatabaseConnection(temp_db))

        # Create 10 threads trying to get instance simultaneously
        threads = [threading.Thread(target=get_connection) for _ in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # All instances should be the same object
        assert len(instances) == 10
        assert all(inst is instances[0] for inst in instances)

    def test_reset_instance_allows_new_creation(self, temp_db, tmp_path):
        """Should allow new instance after reset (for testing)."""
        conn1 = DatabaseConnection(temp_db)
        original_id = id(conn1)

        DatabaseConnection.reset_instance()

        new_db = str(tmp_path / "new.db")
        conn2 = DatabaseConnection(new_db)

        # Should be a different instance
        assert id(conn2) != original_id
        assert conn2.db_path == new_db


class TestDatabaseConnectionInitialization:
    """Test database initialization."""

    def test_creates_database_file(self, temp_db):
        """Should create database file if it doesn't exist."""
        assert not os.path.exists(temp_db)

        db = DatabaseConnection(temp_db)

        assert os.path.exists(temp_db)

    def test_creates_required_tables(self, temp_db):
        """Should create required tables on initialization."""
        db = DatabaseConnection(temp_db)

        with db.get_connection() as conn:
            cursor = conn.cursor()

            # Check test_results table
            cursor.execute(
                """
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='test_results'
            """
            )
            assert cursor.fetchone() is not None

            # Check sessions table
            cursor.execute(
                """
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='sessions'
            """
            )
            assert cursor.fetchone() is not None

    def test_drops_unused_tables(self, temp_db):
        """Should drop old unused tables (projects, config)."""
        # Create database with old tables
        conn = sqlite3.connect(temp_db)
        conn.execute("CREATE TABLE projects (id INTEGER)")
        conn.execute("CREATE TABLE config (id INTEGER)")
        conn.commit()
        conn.close()

        # Initialize DatabaseConnection
        db = DatabaseConnection(temp_db)

        with db.get_connection() as conn:
            cursor = conn.cursor()

            # Old tables should be dropped
            cursor.execute(
                """
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='projects'
            """
            )
            assert cursor.fetchone() is None

            cursor.execute(
                """
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='config'
            """
            )
            assert cursor.fetchone() is None


class TestDatabaseConnectionContextManager:
    """Test context manager protocol."""

    def test_provides_connection_in_context(self, temp_db):
        """Should provide connection in context manager."""
        db = DatabaseConnection(temp_db)

        with db.get_connection() as conn:
            assert conn is not None
            assert isinstance(conn, sqlite3.Connection)

            # Should be able to execute queries
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            assert result[0] == 1

    def test_commits_transaction_on_success(self, temp_db):
        """Should commit transaction on successful exit."""
        db = DatabaseConnection(temp_db)

        # Insert data in transaction
        with db.get_connection() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS test_table (
                    id INTEGER PRIMARY KEY,
                    value TEXT
                )
            """
            )
            conn.execute("INSERT INTO test_table (value) VALUES (?)", ("test_value",))

        # Verify commit occurred by reading in new transaction
        with db.get_connection() as conn:
            cursor = conn.execute("SELECT value FROM test_table")
            result = cursor.fetchone()
            assert result[0] == "test_value"

    def test_rolls_back_on_exception(self, temp_db):
        """Should rollback transaction on exception."""
        db = DatabaseConnection(temp_db)

        # Create table first
        with db.get_connection() as conn:
            conn.execute(
                """
                CREATE TABLE test_table (id INTEGER PRIMARY KEY)
            """
            )

        # Try to insert with error
        try:
            with db.get_connection() as conn:
                conn.execute("INSERT INTO test_table (id) VALUES (1)")
                # Force an error
                raise Exception("Test error")
        except Exception:
            pass

        # Verify rollback occurred - table should be empty
        with db.get_connection() as conn:
            cursor = conn.execute("SELECT COUNT(*) FROM test_table")
            count = cursor.fetchone()[0]
            assert count == 0  # Insert was rolled back

    def test_raises_database_error_on_sql_error(self, temp_db):
        """Should raise DatabaseError on SQL errors."""
        db = DatabaseConnection(temp_db)

        with pytest.raises(DatabaseError):
            with db.get_connection() as conn:
                # Invalid SQL should raise error
                conn.execute("SELECT * FROM nonexistent_table")


class TestDatabaseConnectionThreadSafety:
    """Test thread-safe operations."""

    def test_concurrent_reads(self, temp_db):
        """Should handle concurrent read operations safely."""
        db = DatabaseConnection(temp_db)

        # Create test data
        with db.get_connection() as conn:
            conn.execute("CREATE TABLE test_table (id INTEGER, value TEXT)")
            for i in range(100):
                conn.execute("INSERT INTO test_table VALUES (?, ?)", (i, f"value_{i}"))

        results = []
        errors = []

        def read_data():
            try:
                with db.get_connection() as conn:
                    cursor = conn.execute("SELECT COUNT(*) FROM test_table")
                    count = cursor.fetchone()[0]
                    results.append(count)
            except Exception as e:
                errors.append(e)

        # 10 threads reading simultaneously
        threads = [threading.Thread(target=read_data) for _ in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # All reads should succeed
        assert len(errors) == 0
        assert len(results) == 10
        assert all(count == 100 for count in results)

    def test_concurrent_writes(self, temp_db):
        """Should handle concurrent write operations safely."""
        db = DatabaseConnection(temp_db)

        # Create test table
        with db.get_connection() as conn:
            conn.execute("CREATE TABLE test_table (id INTEGER PRIMARY KEY, thread_id INTEGER)")

        errors = []

        def write_data(thread_id):
            try:
                with db.get_connection() as conn:
                    # Each thread inserts its own record
                    conn.execute("INSERT INTO test_table (thread_id) VALUES (?)", (thread_id,))
            except Exception as e:
                errors.append(e)

        # 5 threads writing simultaneously
        threads = [threading.Thread(target=write_data, args=(i,)) for i in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # All writes should succeed (thread-safe)
        assert len(errors) == 0

        # Verify all records inserted
        with db.get_connection() as conn:
            cursor = conn.execute("SELECT COUNT(*) FROM test_table")
            count = cursor.fetchone()[0]
            assert count == 5


class TestDatabaseConnectionLifecycle:
    """Test connection lifecycle management."""

    def test_connection_reuse(self, temp_db):
        """Should reuse same connection across multiple context managers."""
        db = DatabaseConnection(temp_db)

        connection_ids = []

        for _ in range(5):
            with db.get_connection() as conn:
                connection_ids.append(id(conn))

        # Should reuse the same connection object
        assert all(conn_id == connection_ids[0] for conn_id in connection_ids)

    def test_close_connection(self, temp_db):
        """Should close connection properly."""
        db = DatabaseConnection(temp_db)

        # Use connection
        with db.get_connection() as conn:
            conn.execute("SELECT 1")

        # Close it
        db.close()

        # Internal connection should be None
        assert db._connection is None

    def test_row_factory_enabled(self, temp_db):
        """Should enable row_factory for dict-like access."""
        db = DatabaseConnection(temp_db)

        with db.get_connection() as conn:
            conn.execute("CREATE TABLE test_table (id INTEGER, name TEXT)")
            conn.execute("INSERT INTO test_table VALUES (1, 'test')")

            cursor = conn.execute("SELECT * FROM test_table")
            row = cursor.fetchone()

            # Should support dict-like access
            assert row["id"] == 1
            assert row["name"] == "test"


class TestDatabaseConnectionErrorHandling:
    """Test error handling scenarios."""

    def test_handles_invalid_path(self):
        """Should handle invalid database path gracefully."""
        # Try to create database in invalid location
        invalid_path = "/invalid/path/that/does/not/exist/test.db"

        # Should raise ConnectionError
        with pytest.raises(ConnectionError):
            db = DatabaseConnection(invalid_path)
            with db.get_connection() as conn:
                conn.execute("SELECT 1")

        # Reset for cleanup
        DatabaseConnection.reset_instance()

    def test_handles_corrupted_database(self, tmp_path):
        """Should handle corrupted database file."""
        db_path = tmp_path / "corrupted.db"

        # Create corrupted file
        db_path.write_text("This is not a valid SQLite database")

        with pytest.raises(ConnectionError):
            db = DatabaseConnection(str(db_path))
            with db.get_connection() as conn:
                conn.execute("SELECT 1")

        # Reset for cleanup
        DatabaseConnection.reset_instance()


class TestBackwardCompatibility:
    """Test backward compatibility functions."""

    def test_get_db_connection_function(self, temp_db):
        """Should support legacy get_db_connection() function."""
        from src.app.persistence.database.connection import get_db_connection

        # First, initialize with specific path
        DatabaseConnection(temp_db)

        # Legacy function should return same instance
        db = get_db_connection()

        assert isinstance(db, DatabaseConnection)
        assert db.db_path == temp_db
