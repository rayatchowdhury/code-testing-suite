"""
Benchmarker Status View

Thin adapter that:
1. Creates presenter with widgets
2. Translates worker signals to TestResult
3. Handles domain-specific detail views
"""

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QWidget, QVBoxLayout, QMessageBox

from src.app.presentation.widgets.status_view import (
    TestResult,
    TestType,
    StatusViewPresenter,
    StatusHeaderSection,
    PerformancePanelSection,
    VisualProgressBarSection,
    TestResultsCardsSection,
    BenchmarkerTestCard
)
from src.app.presentation.widgets.test_detail_view import BenchmarkerDetailDialog
from src.app.presentation.styles.components.status_view import STATUS_VIEW_CONTAINER_STYLE


class BenchmarkerStatusView(QWidget):
    """
    Benchmarker-specific status view.
    
    Responsibilities:
    - Translate benchmarker worker signals to TestResult
    - Create benchmarker-specific cards with performance metrics
    - Show benchmarker detail dialogs with input/output
    - Coordinate with presenter for UI updates
    """
    
    # Signals for window coordination
    stopRequested = Signal()
    backRequested = Signal()
    runRequested = Signal()
    
    def __init__(self, time_limit_ms: float, memory_limit_mb: int, parent=None):
        super().__init__(parent)
        self.setObjectName("status_view_container")
        self.parent_window = parent
        self.test_type = TestType.BENCHMARKER
        
        # Store limits for detail views
        self.time_limit_ms = time_limit_ms
        self.memory_limit_mb = memory_limit_mb
        
        # Store results for detail views
        self.test_results = {}  # {test_number: TestResult}
        
        self._setup_ui()
        self.setStyleSheet(STATUS_VIEW_CONTAINER_STYLE)
    
    def _setup_ui(self):
        """Create UI with presenter pattern"""
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
            test_type="benchmarker"
        )
        
        # Add to layout
        layout.addWidget(self.header)
        layout.addWidget(self.performance)
        layout.addWidget(self.progress_bar)
        layout.addWidget(self.cards_section, stretch=1)
    
    def on_tests_started(self, total: int):
        """Handle test execution start"""
        # Get worker count
        max_workers = self._get_worker_count()
        
        # Initialize presenter
        self.presenter.start_test_execution(total, max_workers)
        
        # Clear stored results
        self.test_results.clear()
    
    def on_test_running(self, test_number: int, total: int):
        """Handle test being processed (misleading name - actually called after completion)"""
        self.presenter.mark_test_active(test_number)
    
    def on_worker_busy(self, worker_id: int, test_number: int):
        """Handle worker starting work on a test"""
        self.presenter.handle_worker_busy(worker_id, test_number)
    
    def on_worker_idle(self, worker_id: int):
        """Handle worker finishing work"""
        self.presenter.handle_worker_idle(worker_id)
    
    def on_test_completed(
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
        Handle test completion from worker.
        
        Translates benchmarker worker signal (9 params) to TestResult.
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
        
        # Store for detail view
        self.test_results[test_number] = result
        
        # Update UI through presenter
        self.presenter.handle_test_result(result)
        
        # Create and add card
        card = BenchmarkerTestCard(result)
        card.clicked.connect(self.show_test_detail)
        self.cards_section.add_card(card, result.passed)
    
    def on_all_tests_completed(self):
        """Handle test execution completion"""
        self.presenter.complete_execution()
        
        # Notify parent to enable save button
        if self.parent_window and hasattr(self.parent_window, "enable_save_button"):
            self.parent_window.enable_save_button()
    
    def show_test_detail(self, test_number: int):
        """Show detail dialog with input/output sections"""
        if test_number not in self.test_results:
            return
        
        result = self.test_results[test_number]
        data = result.data
        
        dialog = BenchmarkerDetailDialog(
            test_number=test_number,
            passed=result.passed,
            time=result.time,
            memory=result.memory,
            test_size=data.get('test_size', 0),
            input_data=data.get('input_data', ''),
            output_data=data.get('output_data', ''),
            parent=self
        )
        dialog.exec()
    
    def _get_worker_count(self) -> int:
        """Get worker count from parent"""
        worker = None
        if self.parent_window and hasattr(self.parent_window, 'benchmarker'):
            if hasattr(self.parent_window.benchmarker, 'get_current_worker'):
                worker = self.parent_window.benchmarker.get_current_worker()
        
        if worker and hasattr(worker, 'max_workers'):
            return worker.max_workers
        
        import multiprocessing
        return min(8, max(1, multiprocessing.cpu_count() - 1))
    
    def save_to_database(self):
        """Save results to database"""
        runner = None
        if hasattr(self, "runner"):
            runner = self.runner
        elif self.parent_window and hasattr(self.parent_window, "benchmarker"):
            runner = self.parent_window.benchmarker
        
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
        """Set runner for saving"""
        self.runner = runner
    
    def is_tests_running(self) -> bool:
        """Check if tests are running"""
        return self.presenter.is_running()
