"""
Database exceptions.

Custom exception classes for database operations.
Created in Phase 2 refactoring.
"""


class DatabaseError(Exception):
    """Base exception for database operations."""
    pass


class ConnectionError(DatabaseError):
    """Connection-related errors."""
    pass


class RepositoryError(DatabaseError):
    """Repository operation errors."""
    pass


class ValidationError(DatabaseError):
    """Data validation errors."""
    pass
