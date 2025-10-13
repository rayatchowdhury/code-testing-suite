"""Base repository with common CRUD patterns.

This module provides an abstract base class for all repositories,
encapsulating common database operations and patterns.

Phase 4: Create Base Repository
"""

from abc import ABC, abstractmethod
from typing import List, Optional, TypeVar, Generic, Any, Union
import logging
import sqlite3

from ..connection import DatabaseConnection
from ..exceptions import RepositoryError, DatabaseError as DBError

logger = logging.getLogger(__name__)

T = TypeVar("T")


class BaseRepository(ABC, Generic[T]):
    """
    Abstract base repository providing common database operations.

    All repositories inherit from this to get:
    - Connection management via singleton DatabaseConnection
    - Error handling with RepositoryError wrapping
    - Logging for all database operations
    - Common query execution patterns
    - Abstract CRUD interface

    Type Parameters:
        T: The entity type this repository manages (e.g., TestResult, Session)

    Example:
        class TestResultRepository(BaseRepository[TestResult]):
            def save(self, entity: TestResult) -> int:
                # Implementation
                pass
    """

    def __init__(self):
        """Initialize repository with singleton database connection."""
        self.db = DatabaseConnection()
        logger.debug(f"Initialized {self.__class__.__name__}")

    def _execute_query(
        self, query: str, params: tuple = (), fetch_one: bool = False
    ) -> Union[sqlite3.Cursor, sqlite3.Row, None]:
        """
        Execute SQL query with error handling and logging.

        This method provides a safe way to execute queries with:
        - Automatic connection management via context manager
        - Parameter binding to prevent SQL injection
        - Error wrapping with RepositoryError
        - Query logging (truncated for long queries)

        Args:
            query: SQL query string (use ? for parameters)
            params: Query parameters as tuple
            fetch_one: If True, return first row. If False, return cursor

        Returns:
            - If fetch_one=True: First row as sqlite3.Row or None
            - If fetch_one=False: sqlite3.Cursor for fetching results

        Raises:
            RepositoryError: If query execution fails

        Example:
            # Fetch one row
            row = self._execute_query("SELECT * FROM users WHERE id = ?", (1,), fetch_one=True)

            # Fetch multiple rows
            cursor = self._execute_query("SELECT * FROM users")
            for row in cursor.fetchall():
                print(row['name'])
        """
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, params)

                if fetch_one:
                    return cursor.fetchone()
                return cursor

        except DBError as e:
            # DatabaseError from connection context manager
            query_preview = query[:100] + "..." if len(query) > 100 else query
            logger.error(
                f"Query failed in {self.__class__.__name__}: {query_preview} | "
                f"Error: {e} | Params: {params}"
            )
            raise RepositoryError(
                f"Database query failed in {self.__class__.__name__}: {e}"
            ) from e
        except sqlite3.Error as e:
            # Direct SQLite error (shouldn't happen with context manager)
            query_preview = query[:100] + "..." if len(query) > 100 else query
            logger.error(
                f"Query failed in {self.__class__.__name__}: {query_preview} | "
                f"Error: {e} | Params: {params}"
            )
            raise RepositoryError(
                f"Database query failed in {self.__class__.__name__}: {e}"
            ) from e
        except Exception as e:
            logger.error(f"Unexpected error in {self.__class__.__name__}: {e}")
            raise RepositoryError(
                f"Unexpected error during query execution: {e}"
            ) from e

    def _execute_many(self, query: str, params_list: List[tuple]) -> int:
        """
        Execute query with multiple parameter sets (bulk insert/update).

        More efficient than calling _execute_query multiple times.

        Args:
            query: SQL query string
            params_list: List of parameter tuples

        Returns:
            Number of rows affected

        Raises:
            RepositoryError: If query execution fails

        Example:
            params = [
                ("user1", "email1@example.com"),
                ("user2", "email2@example.com"),
            ]
            count = self._execute_many(
                "INSERT INTO users (name, email) VALUES (?, ?)",
                params
            )
        """
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.executemany(query, params_list)
                return cursor.rowcount

        except DBError as e:
            # DatabaseError from connection context manager
            query_preview = query[:100] + "..." if len(query) > 100 else query
            logger.error(
                f"Bulk query failed in {self.__class__.__name__}: {query_preview} | "
                f"Error: {e} | Batch size: {len(params_list)}"
            )
            raise RepositoryError(
                f"Bulk query failed in {self.__class__.__name__}: {e}"
            ) from e
        except sqlite3.Error as e:
            # Direct SQLite error (shouldn't happen with context manager)
            query_preview = query[:100] + "..." if len(query) > 100 else query
            logger.error(
                f"Bulk query failed in {self.__class__.__name__}: {query_preview} | "
                f"Error: {e} | Batch size: {len(params_list)}"
            )
            raise RepositoryError(
                f"Bulk query failed in {self.__class__.__name__}: {e}"
            ) from e

    # ========================================================================
    # Abstract Methods - Must be implemented by subclasses
    # ========================================================================

    @abstractmethod
    def save(self, entity: T) -> int:
        """
        Save entity to database.

        For new entities (id=None), INSERT and return new ID.
        For existing entities, UPDATE and return existing ID.

        Args:
            entity: Entity to save

        Returns:
            Entity ID (newly created or existing)

        Raises:
            RepositoryError: If save fails
            ValidationError: If entity is invalid
        """
        pass

    @abstractmethod
    def get_by_id(self, id: int) -> Optional[T]:
        """
        Retrieve entity by ID.

        Args:
            id: Entity ID

        Returns:
            Entity if found, None otherwise

        Raises:
            RepositoryError: If query fails
        """
        pass

    @abstractmethod
    def get_all(self, limit: int = 100) -> List[T]:
        """
        Retrieve all entities with limit.

        Args:
            limit: Maximum number of entities to return

        Returns:
            List of entities (may be empty)

        Raises:
            RepositoryError: If query fails
        """
        pass

    @abstractmethod
    def delete(self, id: int) -> bool:
        """
        Delete entity by ID.

        Args:
            id: Entity ID to delete

        Returns:
            True if deleted, False if not found

        Raises:
            RepositoryError: If deletion fails
        """
        pass

    # ========================================================================
    # Optional Helper Methods - Can be overridden by subclasses
    # ========================================================================

    def count(self, table_name: str, where_clause: str = "", params: tuple = ()) -> int:
        """
        Count rows in table with optional filter.

        Args:
            table_name: Name of table
            where_clause: Optional WHERE clause (without "WHERE" keyword)
            params: Parameters for where clause

        Returns:
            Row count

        Example:
            count = self.count("test_results", "project_name = ?", ("MyProject",))
        """
        query = f"SELECT COUNT(*) FROM {table_name}"
        if where_clause:
            query += f" WHERE {where_clause}"

        row = self._execute_query(query, params, fetch_one=True)
        return row[0] if row else 0

    def exists(self, table_name: str, id: int) -> bool:
        """
        Check if entity with ID exists in table.

        Args:
            table_name: Name of table
            id: Entity ID

        Returns:
            True if exists, False otherwise
        """
        query = f"SELECT 1 FROM {table_name} WHERE id = ?"
        row = self._execute_query(query, (id,), fetch_one=True)
        return row is not None
