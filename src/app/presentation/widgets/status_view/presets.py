"""
Status View Presets

Configuration-driven status view setup for different test types.
Eliminates per-tool status view subclasses by using preset-based configuration.

Phase 3: Status View Unification
"""

from dataclasses import dataclass
from typing import List


@dataclass
class StatusViewPreset:
    """
    Configuration for status view UI and behavior.
    
    Defines what UI elements to show and how to configure them
    based on test type (benchmarker, comparator, validator).
    """
    stages: List[str]
    """Pipeline stages to display in worker status (e.g., ['generate', 'execute', 'validate'])"""
    
    metrics: List[str]
    """Metrics to display in cards (e.g., ['Time', 'Memory', 'Pass Rate'])"""
    
    show_worker_status: bool
    """Whether to show the performance panel with worker status bars"""
    
    show_performance_panel: bool
    """Whether to show performance metrics (speed, workers active)"""
    
    test_type: str
    """Test type identifier ('benchmarker', 'validator', 'comparator')"""
    
    runner_attribute: str
    """Name of runner attribute on parent window (e.g., 'benchmarker', 'validator_runner')"""
    
    card_class_name: str
    """Name of test card class to use (e.g., 'BenchmarkerTestCard')"""
    
    detail_dialog_class_name: str
    """Name of detail dialog class to use (e.g., 'BenchmarkerDetailDialog')"""


# Benchmarker Preset
BENCHMARKER_PRESET = StatusViewPreset(
    stages=["generate", "benchmark"],
    metrics=["Time Limit", "Memory Limit", "Pass Rate"],
    show_worker_status=True,
    show_performance_panel=True,
    test_type="benchmarker",
    runner_attribute="benchmarker",
    card_class_name="BenchmarkerTestCard",
    detail_dialog_class_name="BenchmarkerDetailDialog"
)

# Comparator Preset
COMPARATOR_PRESET = StatusViewPreset(
    stages=["generate", "correct", "evaluate"],
    metrics=["Pass Rate", "Diff Count"],
    show_worker_status=False,
    show_performance_panel=False,
    test_type="comparator",
    runner_attribute="comparator",
    card_class_name="ComparatorTestCard",
    detail_dialog_class_name="ComparatorDetailDialog"
)

# Validator Preset
VALIDATOR_PRESET = StatusViewPreset(
    stages=["generate", "execute", "validate"],
    metrics=["Pass Rate", "Validation Errors"],
    show_worker_status=False,
    show_performance_panel=False,
    test_type="validator",
    runner_attribute="validator_runner",
    card_class_name="ValidatorTestCard",
    detail_dialog_class_name="ValidatorDetailDialog"
)
