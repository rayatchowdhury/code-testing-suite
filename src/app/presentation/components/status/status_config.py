"""
Status view configuration model.

Configuration for customizing status views.
"""

from dataclasses import dataclass
from typing import Type, Dict


@dataclass
class StatusViewConfig:
    """
    Configuration for status views.
    
    Enables configuration-driven customization of status views
    instead of inheritance.
    
    Attributes:
        test_type: Type of test ("benchmark", "validation", "comparison")
        card_class: Test card widget class
        dialog_class: Test detail dialog class
        runner_attribute: Attribute name on parent window for runner
        runner_worker_attribute: Attribute name on runner for workers
        result_signature: Signature of on_test_completed kwargs
    
    Example:
        config = StatusViewConfig(
            test_type="benchmark",
            card_class=BenchmarkerTestCard,
            dialog_class=BenchmarkerDetailDialog,
            runner_attribute="benchmarker",
            runner_worker_attribute="workers",
            result_signature={"test_name": str, "result": "BenchmarkResult"}
        )
    """
    test_type: str
    card_class: Type
    dialog_class: Type
    runner_attribute: str
    runner_worker_attribute: str = "workers"
    result_signature: Dict = None
    
    def __post_init__(self):
        """Initialize defaults."""
        if self.result_signature is None:
            self.result_signature = {}
