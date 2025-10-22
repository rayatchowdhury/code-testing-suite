"""Status view components."""

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
    'TestResult', 
    'TestExecutionState', 
    'TestStatistics', 
    'TestType',
    'StatusViewModel', 
    'StatusViewPresenter',
    'StatusView', 
    'StatusViewPreset',
    'BENCHMARKER_PRESET', 
    'COMPARATOR_PRESET', 
    'VALIDATOR_PRESET',
    'StatusHeaderSection', 
    'PerformancePanelSection', 
    'VisualProgressBarSection',
    'TestResultsCardsSection', 
    'BaseTestCard',
    'ComparatorTestCard', 
    'ValidatorTestCard', 
    'BenchmarkerTestCard',
]
