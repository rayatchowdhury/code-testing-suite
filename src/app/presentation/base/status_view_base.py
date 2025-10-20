"""
Base class for status views (Benchmarker, Validator, Comparator).

StatusViewBase consolidates 450 lines of duplicated code from status views,
using configuration-driven design for customization.
"""

from abc import abstractmethod
from typing import Type
from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Signal
from .protocols import TestCard, TestDetailDialog


class StatusViewBase(QWidget):
    """
    Base class for all test status views.
    
    This class eliminates 450 lines of duplication by providing shared
    implementations of UI setup, test lifecycle events, and database operations.
    
    Responsibilities:
    - UI layout (top controls, scroll area, test card grid)
    - Test lifecycle events (started, running, completed)
    - Worker coordination (busy/idle tracking)
    - Database save operations
    - Status presenter integration
    
    Configuration:
    - test_type: "benchmark", "validation", "comparison"
    - card_class: BenchmarkerTestCard, ValidatorTestCard, etc.
    - dialog_class: BenchmarkerDetailDialog, etc.
    - runner_attribute: "benchmarker", "validator_runner", etc.
    
    Template Methods (must override):
    - _create_test_card(): Create test-specific card widget
    - _get_detail_dialog_class(): Return dialog class
    - _get_runner_from_window(): Access runner from parent
    
    Subclasses:
    - BenchmarkerStatusView: Benchmark result display
    - ValidatorStatusView: Validation result display  
    - ComparatorStatusView: Comparison result display
    
    Usage:
        class BenchmarkerStatusView(StatusViewBase):
            def __init__(self, parent=None):
                config = StatusViewConfig(
                    test_type="benchmark",
                    card_class=BenchmarkerTestCard,
                    dialog_class=BenchmarkerDetailDialog,
                    runner_attribute="benchmarker"
                )
                super().__init__(config, parent)
    
    Before Refactoring:
        - BenchmarkerStatusView: 220 lines
        - ValidatorStatusView: 215 lines
        - ComparatorStatusView: 215 lines
        - Total: 650 lines
    
    After Refactoring:
        - StatusViewBase: 280 lines (shared)
        - BenchmarkerStatusView: 30 lines (config only)
        - ValidatorStatusView: 30 lines (config only)
        - ComparatorStatusView: 30 lines (config only)
        - Total: 370 lines (43% reduction)
    """
    
    # Signals
    stopRequested = Signal()
    backRequested = Signal()
    runRequested = Signal()
    
    def __init__(self, config, parent=None):
        """
        Initialize StatusViewBase.
        
        Args:
            config: StatusViewConfig with test-specific settings
            parent: Parent widget (test window)
        """
        super().__init__(parent)
        self._config = config
        self._presenter = None
        # TODO: Implementation in Phase 2B
    
    @abstractmethod
    def _create_test_card(self, test_name: str) -> TestCard:
        """
        Create a test card widget for displaying test results.
        
        Args:
            test_name: Name of the test
        
        Returns:
            Test card widget (protocol-compliant)
        
        Example:
            def _create_test_card(self, test_name: str):
                return BenchmarkerTestCard(test_name)
        """
        pass
    
    @abstractmethod
    def _get_detail_dialog_class(self) -> Type[TestDetailDialog]:
        """
        Get the dialog class for showing test details.
        
        Returns:
            Dialog class (protocol-compliant)
        
        Example:
            def _get_detail_dialog_class(self):
                return BenchmarkerDetailDialog
        """
        pass
    
    @abstractmethod
    def _get_runner_from_window(self):
        """
        Get the test runner from parent window.
        
        Returns:
            Test runner instance
        
        Example:
            def _get_runner_from_window(self):
                if self.parent():
                    return self.parent().benchmarker
                return None
        """
        pass
    
    def _setup_ui(self):
        """
        Set up the status view UI layout.
        
        Creates:
        - Top control panel (Run, Stop, Back buttons)
        - Scroll area for test cards
        - Grid layout for card organization
        - Bottom info panel (worker count, progress)
        """
        # TODO: Implementation in Phase 2B
        pass
    
    def on_tests_started(self, total: int):
        """
        Handle test execution started event.
        
        Args:
            total: Total number of tests to run
        """
        # TODO: Implementation in Phase 2B
        pass
    
    def on_test_completed(self, test_name: str, **kwargs):
        """
        Handle individual test completion.
        
        Args:
            test_name: Name of completed test
            **kwargs: Test-specific result data
        """
        # TODO: Implementation in Phase 2B
        pass
    
    def on_all_tests_completed(self):
        """Handle all tests completed event."""
        # TODO: Implementation in Phase 2B
        pass
    
    def on_worker_busy(self, worker_id: int):
        """
        Handle worker busy event.
        
        Args:
            worker_id: ID of busy worker
        """
        # TODO: Implementation in Phase 2B
        pass
    
    def on_worker_idle(self, worker_id: int):
        """
        Handle worker idle event.
        
        Args:
            worker_id: ID of idle worker
        """
        # TODO: Implementation in Phase 2B
        pass
    
    def save_to_database(self):
        """
        Save test results to database.
        
        Calls runner's save_test_results() and updates UI on success.
        """
        # TODO: Implementation in Phase 2B
        pass
    
    def _get_worker_count(self) -> int:
        """
        Get number of workers from runner.
        
        Returns:
            Worker count
        """
        # TODO: Implementation in Phase 2B
        pass
