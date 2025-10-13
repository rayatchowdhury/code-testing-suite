"""Database repositories.

This module contains repository classes for database operations.
Repositories provide a clean abstraction layer for CRUD operations.

Phase 4: Create Base Repository
Phase 5: Migrate TestResult Operations
"""

from .base_repository import BaseRepository
from .test_result_repository import TestResultRepository

__all__ = [
    "BaseRepository",
    "TestResultRepository",
]
