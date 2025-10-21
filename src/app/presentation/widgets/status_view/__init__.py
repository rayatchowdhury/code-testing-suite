"""
Status View Module

Provides MVVM-based architecture for status views with proper separation:
- Models: Data structures (TestResult, TestExecutionState)
- ViewModel: Coordination logic (renamed from Presenter in Phase 3)
- Widgets: Pure UI components
- Cards: Domain-specific test result cards
- Presets: Configuration for different test types

Phase 3: Unified status view with preset-based configuration.
"""

from .models import TestResult, TestExecutionState, TestStatistics, TestType
from .viewmodel import StatusViewModel
from .presets import StatusViewPreset, BENCHMARKER_PRESET, COMPARATOR_PRESET, VALIDATOR_PRESET
from .view import StatusView
from .widgets import (
    StatusHeaderSection,
    PerformancePanelSection,
    VisualProgressBarSection,
    TestResultsCardsSection,
    BaseTestCard
)
from .cards import ComparatorTestCard, ValidatorTestCard, BenchmarkerTestCard

# Backward compatibility alias
StatusViewPresenter = StatusViewModel

__all__ = [
    # Models
    'TestResult',
    'TestExecutionState',
    'TestStatistics',
    'TestType',
    # ViewModel
    'StatusViewModel',
    'StatusViewPresenter',  # Backward compatibility
    # View
    'StatusView',
    # Presets
    'StatusViewPreset',
    'BENCHMARKER_PRESET',
    'COMPARATOR_PRESET',
    'VALIDATOR_PRESET',
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
