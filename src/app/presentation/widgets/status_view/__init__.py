"""
Status View Module

Provides presenter-based architecture for status views with proper separation:
- Models: Data structures (TestResult, TestExecutionState)
- Presenter: Coordination logic
- Widgets: Pure UI components
- Cards: Domain-specific test result cards
"""

from .models import TestResult, TestExecutionState, TestStatistics, TestType
from .presenter import StatusViewPresenter
from .widgets import (
    StatusHeaderSection,
    PerformancePanelSection,
    VisualProgressBarSection,
    TestResultsCardsSection,
    BaseTestCard
)
from .cards import ComparatorTestCard, ValidatorTestCard, BenchmarkerTestCard

__all__ = [
    # Models
    'TestResult',
    'TestExecutionState',
    'TestStatistics',
    'TestType',
    # Presenter
    'StatusViewPresenter',
    # Widgets
    'StatusHeaderSection',
    'PerformancePanelSection',
    'VisualProgressBarSection',
    'TestResultsCardsSection',
    'BaseTestCard',
    # Cards
    'ComparatorTestCard',
    'ValidatorTestCard',
    'BenchmarkerTestCard',
]
