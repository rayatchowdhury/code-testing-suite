"""Test base repository functionality.

Tests for the abstract BaseRepository class using a concrete test implementation.

Phase 4: Create Base Repository
"""

import pytest
import tempfile
import os
import sqlite3
from typing import List, Optional

from src.app.persistence.database.repositories.base_repository import BaseRepository
from src.app.persistence.database.connection import DatabaseConnection
from src.app.persistence.database.exceptions import RepositoryError


# ============================================================================
# Test Fixtures and Helpers
# ============================================================================

class DummyEntity:
    """Test entity for repository testing."""
    
    def __init__(self, id: Optional[int] = None, name: str = "", value: int = 0):
        self.id = id
        self.name = name
        self.value = value
    
    def __eq__(self, other):
        """Equality comparison for testing."""
        if not isinstance(other, DummyEntity):
            return False
        return (self.id == other.id and 
                self.name == other.name and 
                self.value == other.value)
    
    def __repr__(self):
        return f"DummyEntity(id={self.id}, name={self.name}, value={self.value})"


class DummyRepository(BaseRepository[DummyEntity]):
    """Concrete repository implementation for testing BaseRepository."""
    
    def __init__(self):
        super().__init__()
        self._create_test_table()
    
    def _create_test_table(self):
        """Create test table for dummy entities."""
        with self.db.get_connection() as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS dummy_entities (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    value INTEGER NOT NULL
                )
            ''')
    
    def save(self, entity: DummyEntity) -> int:
        """Save dummy entity."""
        if entity.id is None:
            # Insert new entity
            query = "INSERT INTO dummy_entities (name, value) VALUES (?, ?)"
            cursor = self._execute_query(query, (entity.name, entity.value))
            return cursor.lastrowid
        else:
            # Update existing entity
            query = "UPDATE dummy_entities SET name = ?, value = ? WHERE id = ?"
            self._execute_query(query, (entity.name, entity.value, entity.id))
            return entity.id
    
    def get_by_id(self, id: int) -> Optional[DummyEntity]:
        """Get dummy entity by ID."""
        query = "SELECT * FROM dummy_entities WHERE id = ?"
        row = self._execute_query(query, (id,), fetch_one=True)
        
        if row:
            return DummyEntity(id=row['id'], name=row['name'], value=row['value'])
        return None
    
    def get_all(self, limit: int = 100) -> List[DummyEntity]:
        """Get all dummy entities."""
        query = "SELECT * FROM dummy_entities LIMIT ?"
        cursor = self._execute_query(query, (limit,))
        
        return [
            DummyEntity(id=row['id'], name=row['name'], value=row['value'])
            for row in cursor.fetchall()
        ]
    
    def delete(self, id: int) -> bool:
        """Delete dummy entity by ID."""
        # Check if exists
        if not self.exists("dummy_entities", id):
            return False
        
        query = "DELETE FROM dummy_entities WHERE id = ?"
        self._execute_query(query, (id,))
        return True


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
    return DummyRepository()


# ============================================================================
# Test Cases
# ============================================================================

class TestBaseRepositoryInitialization:
    """Test repository initialization."""
    
    def test_repository_has_connection(self, repo):
        """Test repository has database connection."""
        assert isinstance(repo.db, DatabaseConnection)
    
    def test_repository_connection_is_singleton(self, repo):
        """Test repository uses singleton connection."""
        repo2 = DummyRepository()
        assert repo.db is repo2.db


class TestExecuteQuery:
    """Test _execute_query method."""
    
    def test_execute_simple_query(self, repo):
        """Test executing simple SELECT query."""
        result = repo._execute_query("SELECT 1", fetch_one=True)
        assert result[0] == 1
    
    def test_execute_query_with_params(self, repo):
        """Test query with parameters."""
        repo._execute_query(
            "INSERT INTO dummy_entities (name, value) VALUES (?, ?)",
            ("test", 42)
        )
        
        row = repo._execute_query(
            "SELECT * FROM dummy_entities WHERE name = ?",
            ("test",),
            fetch_one=True
        )
        
        assert row is not None
        assert row['name'] == "test"
        assert row['value'] == 42
    
    def test_execute_query_fetch_one(self, repo):
        """Test fetch_one parameter."""
        # Insert test data
        repo._execute_query(
            "INSERT INTO dummy_entities (name, value) VALUES (?, ?)",
            ("test1", 1)
        )
        repo._execute_query(
            "INSERT INTO dummy_entities (name, value) VALUES (?, ?)",
            ("test2", 2)
        )
        
        # Fetch one
        row = repo._execute_query(
            "SELECT * FROM dummy_entities",
            fetch_one=True
        )
        
        assert row is not None
        assert row['name'] == "test1"
    
    def test_execute_query_fetch_all(self, repo):
        """Test fetching multiple rows."""
        # Insert test data
        repo._execute_query(
            "INSERT INTO dummy_entities (name, value) VALUES (?, ?)",
            ("test1", 1)
        )
        repo._execute_query(
            "INSERT INTO dummy_entities (name, value) VALUES (?, ?)",
            ("test2", 2)
        )
        
        # Fetch all
        cursor = repo._execute_query("SELECT * FROM dummy_entities")
        rows = cursor.fetchall()
        
        assert len(rows) == 2
        assert rows[0]['name'] == "test1"
        assert rows[1]['name'] == "test2"
    
    def test_execute_query_error_handling(self, repo):
        """Test error handling for invalid query."""
        with pytest.raises(RepositoryError) as exc_info:
            repo._execute_query("SELECT * FROM nonexistent_table")
        
        assert "Database query failed" in str(exc_info.value)


class TestExecuteMany:
    """Test _execute_many method."""
    
    def test_execute_many_insert(self, repo):
        """Test bulk insert with execute_many."""
        params_list = [
            ("user1", 10),
            ("user2", 20),
            ("user3", 30),
        ]
        
        count = repo._execute_many(
            "INSERT INTO dummy_entities (name, value) VALUES (?, ?)",
            params_list
        )
        
        assert count == 3
        
        # Verify inserted
        cursor = repo._execute_query("SELECT * FROM dummy_entities ORDER BY id")
        rows = cursor.fetchall()
        
        assert len(rows) == 3
        assert rows[0]['name'] == "user1"
        assert rows[1]['name'] == "user2"
        assert rows[2]['name'] == "user3"
    
    def test_execute_many_error_handling(self, repo):
        """Test error handling in execute_many."""
        with pytest.raises(RepositoryError):
            repo._execute_many(
                "INSERT INTO nonexistent_table (col) VALUES (?)",
                [("val1",), ("val2",)]
            )


class TestCRUDOperations:
    """Test CRUD operations through concrete implementation."""
    
    def test_save_new_entity(self, repo):
        """Test saving new entity."""
        entity = DummyEntity(name="test", value=42)
        entity_id = repo.save(entity)
        
        assert entity_id > 0
    
    def test_save_and_retrieve(self, repo):
        """Test save and get_by_id."""
        entity = DummyEntity(name="test", value=42)
        entity_id = repo.save(entity)
        
        retrieved = repo.get_by_id(entity_id)
        
        assert retrieved is not None
        assert retrieved.id == entity_id
        assert retrieved.name == "test"
        assert retrieved.value == 42
    
    def test_save_update_existing(self, repo):
        """Test updating existing entity."""
        # Insert
        entity = DummyEntity(name="original", value=10)
        entity_id = repo.save(entity)
        
        # Update
        entity.id = entity_id
        entity.name = "updated"
        entity.value = 20
        updated_id = repo.save(entity)
        
        assert updated_id == entity_id
        
        # Verify
        retrieved = repo.get_by_id(entity_id)
        assert retrieved.name == "updated"
        assert retrieved.value == 20
    
    def test_get_by_id_not_found(self, repo):
        """Test get_by_id with non-existent ID."""
        result = repo.get_by_id(9999)
        assert result is None
    
    def test_get_all(self, repo):
        """Test get_all."""
        # Insert test data
        repo.save(DummyEntity(name="entity1", value=1))
        repo.save(DummyEntity(name="entity2", value=2))
        repo.save(DummyEntity(name="entity3", value=3))
        
        entities = repo.get_all()
        
        assert len(entities) == 3
        assert entities[0].name == "entity1"
        assert entities[1].name == "entity2"
        assert entities[2].name == "entity3"
    
    def test_get_all_with_limit(self, repo):
        """Test get_all with limit."""
        # Insert 5 entities
        for i in range(5):
            repo.save(DummyEntity(name=f"entity{i}", value=i))
        
        entities = repo.get_all(limit=3)
        
        assert len(entities) == 3
    
    def test_delete_existing(self, repo):
        """Test deleting existing entity."""
        entity = DummyEntity(name="test", value=42)
        entity_id = repo.save(entity)
        
        result = repo.delete(entity_id)
        
        assert result is True
        assert repo.get_by_id(entity_id) is None
    
    def test_delete_non_existent(self, repo):
        """Test deleting non-existent entity."""
        result = repo.delete(9999)
        assert result is False


class TestHelperMethods:
    """Test optional helper methods."""
    
    def test_count_all(self, repo):
        """Test count without filter."""
        repo.save(DummyEntity(name="entity1", value=1))
        repo.save(DummyEntity(name="entity2", value=2))
        
        count = repo.count("dummy_entities")
        assert count == 2
    
    def test_count_with_filter(self, repo):
        """Test count with WHERE clause."""
        repo.save(DummyEntity(name="apple", value=10))
        repo.save(DummyEntity(name="banana", value=20))
        repo.save(DummyEntity(name="apple", value=30))
        
        count = repo.count("dummy_entities", "name = ?", ("apple",))
        assert count == 2
    
    def test_exists_true(self, repo):
        """Test exists returns True for existing entity."""
        entity = DummyEntity(name="test", value=42)
        entity_id = repo.save(entity)
        
        assert repo.exists("dummy_entities", entity_id) is True
    
    def test_exists_false(self, repo):
        """Test exists returns False for non-existent entity."""
        assert repo.exists("dummy_entities", 9999) is False
