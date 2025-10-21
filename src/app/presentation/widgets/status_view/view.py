"""
Unified Status View

Single, preset-based status view that replaces per-tool status views.
Configurable through StatusViewPreset for benchmarker, comparator, and validator.

Phase 3: Status View Unification
- Replaces BenchmarkerStatusView, ComparatorStatusView, ValidatorStatusView
- Configuration-driven UI setup via presets
- Eliminates ~485 lines of duplicate code
"""

from typing import Dict, Any, Optional
from PySide6.QtWidgets import QWidget, QVBoxLayout, QMessageBox
from PySide6.QtCore import Signal

from .models import TestResult
from .viewmodel import StatusViewModel
from .presets import StatusViewPreset
from .widgets import (
    StatusHeaderSection,
    PerformancePanelSection,
    VisualProgressBarSection,
    TestResultsCardsSection
)
from .cards import ComparatorTestCard, ValidatorTestCard, BenchmarkerTestCard
from src.app.presentation.design_system.styles.components.status_view import STATUS_VIEW_CONTAINER_STYLE


class StatusView(QWidget):
    """
    Unified status view for all test types.
    
    Configured via StatusViewPreset to display appropriate UI elements
    and handle test type-specific behavior.
    
    Responsibilities:
    - UI setup based on preset configuration
    - Translate test worker signals to TestResult
    - Create test type-specific cards
    - Show test type-specific detail dialogs
    - Coordinate with viewmodel for state management
    
    Replaces:
    - BenchmarkerStatusView (~195 lines)
    - ComparatorStatusView (~65 lines)  
    - ValidatorStatusView (~65 lines)
    Total: ~325 lines → ~200 lines (38% reduction)
    """
    
    # Signals for window coordination
    stopRequested = Signal()
    backRequested = Signal()
    runRequested = Signal()
    
    def __init__(self, preset: StatusViewPreset, parent=None):
        """
        Initialize status view with configuration preset.
        
        Args:
            preset: Configuration preset (BENCHMARKER_PRESET, COMPARATOR_PRESET, VALIDATOR_PRESET)
            parent: Parent widget (test window)
        """
        super().__init__(parent)
        self.setObjectName("status_view_container")
        self.parent_window = parent
        self.preset = preset
        self.test_type = preset.test_type
        
        # Store results for detail views
        self.test_results: Dict[int, TestResult] = {}
        
        # Runner reference (set via set_runner or from parent)
        self.runner = None
        
        # Store benchmarker-specific limits (if applicable)
        self.time_limit_ms: Optional[float] = None
        self.memory_limit_mb: Optional[int] = None
        
        # Setup UI
        self._setup_ui()
        self.setStyleSheet(STATUS_VIEW_CONTAINER_STYLE)
    
    def _setup_ui(self):
        """Create UI with preset-based configuration."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Create widgets
        self.header = StatusHeaderSection()
        self.performance = PerformancePanelSection()
        self.progress_bar = VisualProgressBarSection()
        self.cards_section = TestResultsCardsSection()
        
        # Create viewmodel
        self.viewmodel = StatusViewModel(
            header=self.header,
            performance=self.performance,
            progress_bar=self.progress_bar,
            cards_section=self.cards_section,
            preset=self.preset
        )
        
        # Add to layout
        layout.addWidget(self.header)
        
        # Conditionally add performance panel based on preset
        if self.preset.show_performance_panel:
            layout.addWidget(self.performance)
        
        layout.addWidget(self.progress_bar)
        layout.addWidget(self.cards_section, stretch=1)
    
    # ===== Test Lifecycle Methods =====
    
    def on_tests_started(self, total: int):
        """Handle test execution start."""
        # Get worker count
        max_workers = self._get_worker_count()
        
        # Initialize viewmodel
        self.viewmodel.start_test_execution(total, max_workers)
        
        # Clear stored results
        self.test_results.clear()
    
    def on_test_running(self, test_number: int, total: int):
        """Handle test being processed (backward compatibility)."""
        self.viewmodel.mark_test_active(test_number)
    
    def on_worker_busy(self, worker_id: int, test_number: int):
        """Handle worker starting work on a test."""
        if self.preset.show_worker_status:
            self.viewmodel.handle_worker_busy(worker_id, test_number)
    
    def on_worker_idle(self, worker_id: int):
        """Handle worker finishing work."""
        if self.preset.show_worker_status:
            self.viewmodel.handle_worker_idle(worker_id)
    
    def on_all_tests_completed(self):
        """Handle test execution completion."""
        self.viewmodel.complete_execution()
        
        # Notify parent to enable save button
        if self.parent_window and hasattr(self.parent_window, "enable_save_button"):
            self.parent_window.enable_save_button()
    
    # ===== Test Completion Dispatcher =====
    
    def on_test_completed(self, *args, **kwargs):
        """
        Generic test completion handler - dispatches to type-specific handler.
        
        This method provides backward compatibility with worker signal connections
        that expect a single on_test_completed method.
        """
        if self.test_type == "benchmarker":
            return self.on_benchmarker_test_completed(*args, **kwargs)
        elif self.test_type == "comparator":
            return self.on_comparator_test_completed(*args, **kwargs)
        elif self.test_type == "validator":
            return self.on_validator_test_completed(*args, **kwargs)
    
    # ===== Test Type-Specific Completion Handlers =====
    
    def on_benchmarker_test_completed(
        self,
        test_name: str,
        test_number: int,
        passed: bool,
        execution_time: float,
        memory_used: float,
        memory_passed: bool,
        input_data: str = "",
        output_data: str = "",
        test_size: int = 0
    ):
        """
        Handle benchmarker test completion.
        
        Args:
            test_name: Name of test
            test_number: Test number
            passed: Whether test passed
            execution_time: Execution time in seconds
            memory_used: Memory used in MB
            memory_passed: Whether memory limit was satisfied
            input_data: Test input
            output_data: Test output
            test_size: Size of test input
        """
        # Create TestResult
        result = TestResult.from_benchmarker(
            test_name=test_name,
            test_number=test_number,
            passed=passed,
            execution_time=execution_time,
            memory_used=memory_used,
            memory_passed=memory_passed,
            input_data=input_data,
            output_data=output_data,
            test_size=test_size
        )
        
        self._handle_test_completion(result, BenchmarkerTestCard)
    
    def on_comparator_test_completed(
        self,
        test_number: int,
        passed: bool,
        input_text: str,
        correct_output: str,
        test_output: str,
        time: float = 0.0,
        memory: float = 0.0
    ):
        """
        Handle comparator test completion.
        
        Args:
            test_number: Test number
            passed: Whether test passed
            input_text: Test input
            correct_output: Expected output
            test_output: Actual output
            time: Execution time in seconds
            memory: Memory used in MB
        """
        # Create TestResult
        result = TestResult.from_comparator(
            test_number=test_number,
            passed=passed,
            input_text=input_text,
            correct_output=correct_output,
            test_output=test_output,
            time=time,
            memory=memory
        )
        
        self._handle_test_completion(result, ComparatorTestCard)
    
    def on_validator_test_completed(
        self,
        test_number: int,
        passed: bool,
        input_data: str,
        test_output: str,
        validation_message: str,
        error_details: str,
        validator_exit_code: int,
        time: float = 0.0,
        memory: float = 0.0
    ):
        """
        Handle validator test completion.
        
        Args:
            test_number: Test number
            passed: Whether test passed
            input_data: Test input
            test_output: Test output
            validation_message: Validation message
            error_details: Error details if validation failed
            validator_exit_code: Validator exit code
            time: Execution time in seconds
            memory: Memory used in MB
        """
        # Create TestResult
        result = TestResult.from_validator(
            test_number=test_number,
            passed=passed,
            input_data=input_data,
            test_output=test_output,
            validation_message=validation_message,
            error_details=error_details,
            validator_exit_code=validator_exit_code,
            time=time,
            memory=memory
        )
        
        self._handle_test_completion(result, ValidatorTestCard)
    
    def _handle_test_completion(self, result: TestResult, card_class):
        """
        Common test completion handling.
        
        Args:
            result: TestResult object
            card_class: Card class to instantiate (BenchmarkerTestCard, etc.)
        """
        # Store for detail view
        self.test_results[result.test_number] = result
        
        # Update UI through viewmodel
        self.viewmodel.handle_test_result(result)
        
        # Create and add card
        card = card_class(result)
        card.clicked.connect(self.show_test_detail)
        self.cards_section.add_card(card, result.passed)
    
    # ===== Detail View Methods =====
    
    def show_test_detail(self, test_number: int):
        """
        Show detail dialog for test.
        
        Dialog type is determined by preset configuration.
        
        Args:
            test_number: Test number to show details for
        """
        if test_number not in self.test_results:
            return
        
        result = self.test_results[test_number]
        data = result.data
        
        # Import appropriate dialog based on preset
        dialog_module = "src.app.presentation.widgets.test_detail_view"
        dialog_class_name = self.preset.detail_dialog_class_name
        
        # Dynamically import dialog class
        import importlib
        module = importlib.import_module(dialog_module)
        dialog_class = getattr(module, dialog_class_name)
        
        # Create dialog with test type-specific parameters
        if self.test_type == "benchmarker":
            dialog = dialog_class(
                test_number=test_number,
                passed=result.passed,
                time=result.time,
                memory=result.memory,
                test_size=data.get('test_size', 0),
                input_data=data.get('input_data', ''),
                output_data=data.get('output_data', ''),
                parent=self
            )
        elif self.test_type == "comparator":
            dialog = dialog_class(
                test_number=test_number,
                passed=result.passed,
                time=result.time,
                memory=result.memory,
                input_text=data['input_text'],
                correct_output=data['correct_output'],
                test_output=data['test_output'],
                parent=self
            )
        elif self.test_type == "validator":
            dialog = dialog_class(
                test_number=test_number,
                passed=result.passed,
                time=result.time,
                memory=result.memory,
                input_data=data.get('input_data', 'No input data'),
                test_output=data.get('test_output', 'No output'),
                validation_message=data.get('validation_message', 'Unknown'),
                error_details=data.get('error_details', ''),
                validator_exit_code=data.get('validator_exit_code', -1),
                parent=self
            )
        
        dialog.exec()
    
    # ===== Helper Methods =====
    
    def _get_worker_count(self) -> int:
        """Get worker count from parent."""
        import multiprocessing
        
        runner_attr = self.preset.runner_attribute
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
            runner_attr = self.preset.runner_attribute
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
    
    def set_benchmarker_limits(self, time_limit_ms: float, memory_limit_mb: int):
        """Set benchmarker-specific limits (for detail views)."""
        self.time_limit_ms = time_limit_ms
        self.memory_limit_mb = memory_limit_mb
    
    def is_tests_running(self) -> bool:
        """Check if tests are running."""
        return self.viewmodel.is_running()
