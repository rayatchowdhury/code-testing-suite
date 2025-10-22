"""
Phase 8 Task 4 - Phase 2: Tests for base_repository.py

Tests cover:
- BaseRepository abstract interface
- Query execution with error handling
- Bulk operations
- Connection management
- Helper methods (count, exists)
- Error wrapping and logging
"""

import sqlite3
from typing import List, Optional
from unittest.mock import MagicMock, Mock, patch

import pytest

from src.app.database.connection import DatabaseConnection
from src.app.database.exceptions import DatabaseError as DBError
from src.app.database.exceptions import RepositoryError
from src.app.database.repositories.base_repository import BaseRepository

# ============================================================================
# Test Implementation of BaseRepository
# ============================================================================


class SampleEntity:
    """Simple test entity (renamed to avoid pytest collection)."""

    def __init__(self, id=None, name=None):
        self.id = id
        self.name = name


class ConcreteRepository(BaseRepository[SampleEntity]):
    """Concrete implementation of BaseRepository for testing."""

    def save(self, entity: SampleEntity) -> int:
        """Save entity to database."""
        if entity.id is None:
            # Insert new entity
            cursor = self._execute_query(
                "INSERT INTO test_entities (name) VALUES (?)", (entity.name,)
            )
            return cursor.lastrowid
        else:
            # Update existing
            self._execute_query(
                "UPDATE test_entities SET name = ? WHERE id = ?",
                (entity.name, entity.id),
            )
            return entity.id

    def get_by_id(self, id: int) -> Optional[SampleEntity]:
        """Get entity by ID."""
        row = self._execute_query(
            "SELECT id, name FROM test_entities WHERE id = ?", (id,), fetch_one=True
        )
        if row:
            return SampleEntity(id=row["id"], name=row["name"])
        return None

    def get_all(self, limit: int = 100) -> List[SampleEntity]:
        """Get all entities."""
        cursor = self._execute_query(
            f"SELECT id, name FROM test_entities LIMIT ?", (limit,)
        )
        return [
            SampleEntity(id=row["id"], name=row["name"]) for row in cursor.fetchall()
        ]

    def delete(self, id: int) -> bool:
        """Delete entity by ID."""
        cursor = self._execute_query("DELETE FROM test_entities WHERE id = ?", (id,))
        return cursor.rowcount > 0


# ============================================================================
# Test Fixtures
# ============================================================================


@pytest.fixture
def mock_db_connection():
    """Mock DatabaseConnection."""
    mock_conn = Mock(spec=DatabaseConnection)
    mock_context = MagicMock()
    mock_cursor = MagicMock(spec=sqlite3.Cursor)

    # Setup context manager
    mock_context.__enter__ = MagicMock(return_value=MagicMock())
    mock_context.__enter__.return_value.cursor = MagicMock(return_value=mock_cursor)
    mock_context.__exit__ = MagicMock(return_value=False)

    mock_conn.get_connection.return_value = mock_context

    return mock_conn, mock_cursor


@pytest.fixture
def repository(mock_db_connection):
    """Create concrete repository with mocked connection."""
    mock_conn, _ = mock_db_connection
    repo = ConcreteRepository()
    repo.db = mock_conn
    return repo


# ============================================================================
# Initialization Tests
# ============================================================================


class TestBaseRepositoryInitialization:
    """Test BaseRepository initialization."""

    def test_init_creates_db_connection(self):
        """Test initialization creates DatabaseConnection."""
        repo = ConcreteRepository()

        assert repo.db is not None
        assert isinstance(repo.db, DatabaseConnection)


# ============================================================================
# Query Execution Tests
# ============================================================================


class TestQueryExecution:
    """Test _execute_query method."""

    def test_execute_query_fetch_all(self, repository, mock_db_connection):
        """Test executing query that fetches all results."""
        _, mock_cursor = mock_db_connection
        mock_cursor.fetchall.return_value = [
            {"id": 1, "name": "test1"},
            {"id": 2, "name": "test2"},
        ]

        cursor = repository._execute_query("SELECT * FROM test_entities")
        results = cursor.fetchall()

        assert len(results) == 2
        mock_cursor.execute.assert_called_once()

    def test_execute_query_fetch_one(self, repository, mock_db_connection):
        """Test executing query that fetches one result."""
        _, mock_cursor = mock_db_connection
        mock_cursor.fetchone.return_value = {"id": 1, "name": "test1"}

        result = repository._execute_query(
            "SELECT * FROM test_entities WHERE id = ?", (1,), fetch_one=True
        )

        assert result is not None
        assert result["id"] == 1
        mock_cursor.execute.assert_called_once_with(
            "SELECT * FROM test_entities WHERE id = ?", (1,)
        )

    def test_execute_query_with_params(self, repository, mock_db_connection):
        """Test executing query with parameters."""
        _, mock_cursor = mock_db_connection

        repository._execute_query(
            "INSERT INTO test_entities (name) VALUES (?)", ("test",)
        )

        mock_cursor.execute.assert_called_once_with(
            "INSERT INTO test_entities (name) VALUES (?)", ("test",)
        )

    def test_execute_query_database_error(self, repository, mock_db_connection):
        """Test query execution handles DatabaseError."""
        mock_conn, _ = mock_db_connection
        mock_conn.get_connection.side_effect = DBError("Connection failed")

        with pytest.raises(RepositoryError) as exc_info:
            repository._execute_query("SELECT * FROM test_entities")

        assert "Database query failed" in str(exc_info.value)

    def test_execute_query_sqlite_error(self, repository, mock_db_connection):
        """Test query execution handles SQLite errors."""
        _, mock_cursor = mock_db_connection
        mock_cursor.execute.side_effect = sqlite3.Error("SQL error")

        with pytest.raises(RepositoryError) as exc_info:
            repository._execute_query("INVALID SQL")

        assert "Database query failed" in str(exc_info.value)

    def test_execute_query_unexpected_error(self, repository, mock_db_connection):
        """Test query execution handles unexpected errors."""
        _, mock_cursor = mock_db_connection
        mock_cursor.execute.side_effect = ValueError("Unexpected error")

        with pytest.raises(RepositoryError) as exc_info:
            repository._execute_query("SELECT * FROM test_entities")

        assert "Unexpected error" in str(exc_info.value)

    def test_execute_query_long_query_truncation(self, repository, mock_db_connection):
        """Test long queries are truncated in error messages."""
        _, mock_cursor = mock_db_connection
        mock_cursor.execute.side_effect = sqlite3.Error("SQL error")

        long_query = "SELECT * FROM test_entities WHERE " + "x = ? AND " * 50

        with pytest.raises(RepositoryError):
            repository._execute_query(long_query, tuple(range(50)))


# ============================================================================
# Bulk Operations Tests
# ============================================================================


class TestBulkOperations:
    """Test _execute_many method."""

    def test_execute_many_success(self, repository, mock_db_connection):
        """Test bulk insert with multiple parameters."""
        _, mock_cursor = mock_db_connection
        mock_cursor.rowcount = 3

        params_list = [("test1",), ("test2",), ("test3",)]

        count = repository._execute_many(
            "INSERT INTO test_entities (name) VALUES (?)", params_list
        )

        assert count == 3
        mock_cursor.executemany.assert_called_once()

    def test_execute_many_empty_list(self, repository, mock_db_connection):
        """Test bulk operation with empty list."""
        _, mock_cursor = mock_db_connection
        mock_cursor.rowcount = 0

        count = repository._execute_many(
            "INSERT INTO test_entities (name) VALUES (?)", []
        )

        assert count == 0

    def test_execute_many_database_error(self, repository, mock_db_connection):
        """Test bulk operation handles DatabaseError."""
        mock_conn, _ = mock_db_connection
        mock_conn.get_connection.side_effect = DBError("Connection failed")

        with pytest.raises(RepositoryError) as exc_info:
            repository._execute_many(
                "INSERT INTO test_entities (name) VALUES (?)", [("test",)]
            )

        assert "Bulk query failed" in str(exc_info.value)

    def test_execute_many_sqlite_error(self, repository, mock_db_connection):
        """Test bulk operation handles SQLite errors."""
        _, mock_cursor = mock_db_connection
        mock_cursor.executemany.side_effect = sqlite3.Error("SQL error")

        with pytest.raises(RepositoryError) as exc_info:
            repository._execute_many(
                "INSERT INTO test_entities (name) VALUES (?)", [("test",)]
            )

        assert "Bulk query failed" in str(exc_info.value)


# ============================================================================
# Helper Methods Tests
# ============================================================================


class TestHelperMethods:
    """Test helper methods (count, exists)."""

    def test_count_without_filter(self, repository, mock_db_connection):
        """Test count without filter."""
        _, mock_cursor = mock_db_connection
        mock_cursor.fetchone.return_value = (5,)

        count = repository.count("test_entities")

        assert count == 5
        mock_cursor.execute.assert_called_once()

    def test_count_with_filter(self, repository, mock_db_connection):
        """Test count with WHERE clause."""
        _, mock_cursor = mock_db_connection
        mock_cursor.fetchone.return_value = (3,)

        count = repository.count("test_entities", "name LIKE ?", ("test%",))

        assert count == 3

    def test_count_empty_table(self, repository, mock_db_connection):
        """Test count on empty table."""
        _, mock_cursor = mock_db_connection
        mock_cursor.fetchone.return_value = (0,)

        count = repository.count("test_entities")

        assert count == 0

    def test_count_none_result(self, repository, mock_db_connection):
        """Test count returns 0 when query returns None."""
        _, mock_cursor = mock_db_connection
        mock_cursor.fetchone.return_value = None

        count = repository.count("test_entities")

        assert count == 0

    def test_exists_true(self, repository, mock_db_connection):
        """Test exists returns True when entity exists."""
        _, mock_cursor = mock_db_connection
        mock_cursor.fetchone.return_value = (1,)

        exists = repository.exists("test_entities", 1)

        assert exists is True

    def test_exists_false(self, repository, mock_db_connection):
        """Test exists returns False when entity doesn't exist."""
        _, mock_cursor = mock_db_connection
        mock_cursor.fetchone.return_value = None

        exists = repository.exists("test_entities", 999)

        assert exists is False


# ============================================================================
# Abstract Methods Tests
# ============================================================================


class TestAbstractMethods:
    """Test that abstract methods must be implemented."""

    def test_save_implementation(self, repository, mock_db_connection):
        """Test save method is implemented."""
        _, mock_cursor = mock_db_connection
        mock_cursor.lastrowid = 1

        entity = SampleEntity(name="test")
        result_id = repository.save(entity)

        assert result_id == 1

    def test_get_by_id_implementation(self, repository, mock_db_connection):
        """Test get_by_id method is implemented."""
        _, mock_cursor = mock_db_connection
        mock_cursor.fetchone.return_value = {"id": 1, "name": "test"}

        entity = repository.get_by_id(1)

        assert entity is not None
        assert entity.id == 1

    def test_get_all_implementation(self, repository, mock_db_connection):
        """Test get_all method is implemented."""
        _, mock_cursor = mock_db_connection
        mock_cursor.fetchall.return_value = [
            {"id": 1, "name": "test1"},
            {"id": 2, "name": "test2"},
        ]

        entities = repository.get_all()

        assert len(entities) == 2

    def test_delete_implementation(self, repository, mock_db_connection):
        """Test delete method is implemented."""
        _, mock_cursor = mock_db_connection
        mock_cursor.rowcount = 1

        result = repository.delete(1)

        assert result is True

    def test_delete_not_found(self, repository, mock_db_connection):
        """Test delete returns False when entity not found."""
        _, mock_cursor = mock_db_connection
        mock_cursor.rowcount = 0

        result = repository.delete(999)

        assert result is False


# ============================================================================
# Integration Tests
# ============================================================================


class TestBaseRepositoryIntegration:
    """Integration tests for BaseRepository."""

    def test_cannot_instantiate_abstract_class(self):
        """Test that BaseRepository cannot be instantiated directly."""
        with pytest.raises(TypeError):
            BaseRepository()

    def test_concrete_implementation_workflow(self, repository, mock_db_connection):
        """Test complete workflow with concrete implementation."""
        _, mock_cursor = mock_db_connection

        # Save
        mock_cursor.lastrowid = 1
        entity = SampleEntity(name="test")
        entity_id = repository.save(entity)
        assert entity_id == 1

        # Get by ID
        mock_cursor.fetchone.return_value = {"id": 1, "name": "test"}
        retrieved = repository.get_by_id(entity_id)
        assert retrieved is not None
        assert retrieved.name == "test"

        # Update
        retrieved.name = "updated"
        mock_cursor.lastrowid = 1
        updated_id = repository.save(retrieved)
        assert updated_id == entity_id

        # Count
        mock_cursor.fetchone.return_value = (1,)
        count = repository.count("test_entities")
        assert count == 1

        # Exists
        mock_cursor.fetchone.return_value = (1,)
        exists = repository.exists("test_entities", entity_id)
        assert exists is True

        # Delete
        mock_cursor.rowcount = 1
        deleted = repository.delete(entity_id)
        assert deleted is True
