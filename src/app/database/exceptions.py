"""
Database exceptions.

Custom exception classes for database operations.
Created in Phase 2 refactoring.
"""


class DatabaseError(Exception):
    """Base exception for database operations."""


class ConnectionError(DatabaseError):
    """Connection-related errors."""


class RepositoryError(DatabaseError):
    """Repository operation errors."""


class ValidationError(DatabaseError):
    """Data validation errors."""
