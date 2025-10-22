"""Shared dialog components."""

from src.app.presentation.shared.dialogs.test_detail import (
    TestDetailDialog,
    ComparatorDetailDialog,
    ValidatorDetailDialog,
    BenchmarkerDetailDialog,
)
from src.app.presentation.shared.dialogs.result_detail import (
    DetailedResultDialog,
    DetailedResultViewModel,
)

# Aliases for backward compatibility
ResultDetailDialog = DetailedResultDialog
ResultDetailViewModel = DetailedResultViewModel

__all__ = [
    "TestDetailDialog",
    "ComparatorDetailDialog",
    "ValidatorDetailDialog",
    "BenchmarkerDetailDialog",
    "DetailedResultDialog",
    "DetailedResultViewModel",
    "ResultDetailDialog",
    "ResultDetailViewModel",
]
