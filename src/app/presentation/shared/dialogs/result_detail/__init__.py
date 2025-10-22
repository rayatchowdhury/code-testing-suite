"""
Result Detail Dialog Package

Phase 4: Results Detail Consolidation
Unified dialog for displaying detailed test results.
"""

from .view import DetailedResultDialog
from .viewmodel import DetailedResultViewModel

# Aliases for backward compatibility
ResultDetailDialog = DetailedResultDialog
ResultDetailViewModel = DetailedResultViewModel

__all__ = ["DetailedResultDialog", "DetailedResultViewModel", "ResultDetailDialog", "ResultDetailViewModel"]
