"""
Base class for status views (Benchmarker, Validator, Comparator).

StatusViewBase consolidates ~150 lines of duplicated code from status views,
using configuration-driven design for customization.
"""

from abc import abstractmethod
from typing import Type, Dict, Any
from PySide6.QtWidgets import QWidget, QVBoxLayout, QMessageBox
from PySide6.QtCore import Signal
from .protocols import TestCard, TestDetailDialog


class StatusViewBase(QWidget):
    """
    Base class for all test status views.
    
    Extracts ~150 lines of duplicated code into shared implementation.
    Uses StatusViewPresenter for state management and widget coordination.
    
    Responsibilities:
    - UI setup delegation to presenter
    - Test lifecycle event handling
    - Worker coordination
    - Database save operations
    - Runner access abstraction
    
    Template Methods (must override):
    - _get_runner_attribute_name(): Return runner attribute name
    - _get_card_class(): Return test card class
    - _get_detail_dialog_class(): Return detail dialog class
    - on_test_completed(): Handle test completion (signature varies)
    - show_test_detail(): Show detail dialog (data varies)
    
    Shared Methods (150 lines extracted):
    - _setup_ui()
    - on_tests_started()
    - on_test_running()
    - on_worker_busy()
    - on_worker_idle()
    - on_all_tests_completed()
    - _get_worker_count()
    - save_to_database()
    - set_runner()
    - is_tests_running()
    
    Usage:
        class BenchmarkerStatusView(StatusViewBase):
            def __init__(self, time_limit_ms, memory_limit_mb, parent=None):
                super().__init__(parent, test_type="benchmarker")
                self.time_limit_ms = time_limit_ms
                self.memory_limit_mb = memory_limit_mb
            
            def _get_runner_attribute_name(self):
                return "benchmarker"
            
            def _get_card_class(self):
                return BenchmarkerTestCard
    """
    
    # Signals for window coordination
    stopRequested = Signal()
    backRequested = Signal()
    runRequested = Signal()
    
    def __init__(self, parent=None, test_type: str = "comparator"):
        """
        Initialize StatusViewBase.
        
        Args:
            parent: Parent widget (test window)
            test_type: Type of test ("benchmarker", "validator", "comparator")
        """
        super().__init__(parent)
        self.setObjectName("status_view_container")
        self.parent_window = parent
        self.test_type = test_type
        
        # Store results for detail views
        self.test_results: Dict[int, Any] = {}
        
        # Runner reference (set via set_runner or from parent)
        self.runner = None
        
        # Setup UI using presenter pattern
        self._setup_ui()
        
        # Apply styling
        from src.app.presentation.styles.components.status_view import STATUS_VIEW_CONTAINER_STYLE
        self.setStyleSheet(STATUS_VIEW_CONTAINER_STYLE)
    
    # ===== TEMPLATE METHODS (must override) =====
    
    @abstractmethod
    def _get_runner_attribute_name(self) -> str:
        """
        Get the attribute name for the runner on parent window.
        
        Returns:
            "benchmarker", "validator_runner", or "comparator"
        """
        pass
    
    @abstractmethod
    def _get_card_class(self) -> Type:
        """
        Get the test card class.
        
        Returns:
            BenchmarkerTestCard, ValidatorTestCard, or ComparatorTestCard
        """
        pass
    
    @abstractmethod
    def _get_detail_dialog_class(self) -> Type[TestDetailDialog]:
        """
        Get the dialog class for showing test details.
        
        Returns:
            Dialog class (protocol-compliant)
        """
        pass
    
    @abstractmethod
    def on_test_completed(self, *args, **kwargs):
        """
        Handle individual test completion.
        
        Signature varies by test type:
        - Benchmarker: (test_name, test_number, passed, execution_time, memory_used, ...)
        - Validator: (test_number, passed, input_data, test_output, ...)
        - Comparator: (test_number, passed, input_text, correct_output, ...)
        
        Must:
        1. Create TestResult
        2. Store in self.test_results
        3. Call self.presenter.handle_test_result(result)
        4. Create card and add to cards_section
        """
        pass
    
    @abstractmethod
    def show_test_detail(self, test_number: int):
        """
        Show detail dialog for test.
        
        Args:
            test_number: Test number to show details for
        """
        pass
    
    # ===== SHARED IMPLEMENTATION (150 lines extracted) =====
    
    def _setup_ui(self):
        """Create UI with presenter pattern."""
        from src.app.presentation.widgets.status_view import (
            StatusViewPresenter,
            StatusHeaderSection,
            PerformancePanelSection,
            VisualProgressBarSection,
            TestResultsCardsSection
        )
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Create widgets
        self.header = StatusHeaderSection()
        self.performance = PerformancePanelSection()
        self.progress_bar = VisualProgressBarSection()
        self.cards_section = TestResultsCardsSection()
        
        # Create presenter
        self.presenter = StatusViewPresenter(
            header=self.header,
            performance=self.performance,
            progress_bar=self.progress_bar,
            cards_section=self.cards_section,
            test_type=self.test_type
        )
        
        # Add to layout
        layout.addWidget(self.header)
        layout.addWidget(self.performance)
        layout.addWidget(self.progress_bar)
        layout.addWidget(self.cards_section, stretch=1)
    
    def on_tests_started(self, total: int):
        """Handle test execution start."""
        # Get worker count
        max_workers = self._get_worker_count()
        
        # Initialize presenter
        self.presenter.start_test_execution(total, max_workers)
        
        # Clear stored results
        self.test_results.clear()
    
    def on_test_running(self, test_number: int, total: int):
        """Handle test being processed (misleading name - actually called after completion)."""
        self.presenter.mark_test_active(test_number)
    
    def on_worker_busy(self, worker_id: int, test_number: int):
        """Handle worker starting work on a test."""
        self.presenter.handle_worker_busy(worker_id, test_number)
    
    def on_worker_idle(self, worker_id: int):
        """Handle worker finishing work."""
        self.presenter.handle_worker_idle(worker_id)
    
    def on_all_tests_completed(self, all_passed: bool):
        """Handle test execution completion."""
        self.presenter.complete_execution()
        
        # Notify parent to enable save button
        if self.parent_window and hasattr(self.parent_window, "enable_save_button"):
            self.parent_window.enable_save_button()
    
    def _get_worker_count(self) -> int:
        """Get worker count from parent."""
        import multiprocessing
        
        runner_attr = self._get_runner_attribute_name()
        worker = None
        
        if self.parent_window and hasattr(self.parent_window, runner_attr):
            runner = getattr(self.parent_window, runner_attr)
            if hasattr(runner, 'get_current_worker'):
                worker = runner.get_current_worker()
        
        if worker and hasattr(worker, 'max_workers'):
            return worker.max_workers
        
        return min(8, max(1, multiprocessing.cpu_count() - 1))
    
    def save_to_database(self):
        """Save results to database."""
        runner = None
        
        # Try to get runner from self.runner first
        if hasattr(self, "runner") and self.runner:
            runner = self.runner
        # Otherwise get from parent window
        elif self.parent_window:
            runner_attr = self._get_runner_attribute_name()
            if hasattr(self.parent_window, runner_attr):
                runner = getattr(self.parent_window, runner_attr)
        
        if not runner:
            QMessageBox.critical(self, "Error", "Runner not found")
            return -1
        
        try:
            result_id = runner.save_test_results_to_database()
            if result_id > 0:
                QMessageBox.information(
                    self, "Success",
                    f"Results saved!\nDatabase ID: {result_id}"
                )
                if self.parent_window and hasattr(self.parent_window, "mark_results_saved"):
                    self.parent_window.mark_results_saved()
            else:
                QMessageBox.critical(self, "Error", "Failed to save")
            return result_id
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error saving: {e}")
            return -1
    
    def set_runner(self, runner):
        """Set runner for saving."""
        self.runner = runner
    
    def is_tests_running(self) -> bool:
        """Check if tests are running."""
        return self.presenter.is_running()
