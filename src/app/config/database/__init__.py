"""Database configuration operations.

This module handles database-related configuration operations:
- Database statistics and cleanup
- Database operations for configuration dialog
- User confirmation dialogs for database operations
"""

from .database_operations import DatabaseOperations

__all__ = [
    'DatabaseOperations'
]
