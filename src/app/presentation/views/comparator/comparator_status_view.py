"""
Comparator Status View

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
    ComparatorTestCard
)
from src.app.presentation.widgets.test_detail_view import ComparatorDetailDialog
from src.app.presentation.styles.components.status_view import STATUS_VIEW_CONTAINER_STYLE


class ComparatorStatusView(QWidget):
    """
    Comparator-specific status view.
    
    Responsibilities:
    - Translate comparator worker signals to TestResult
    - Create comparator-specific cards
    - Show comparator detail dialogs
    - Coordinate with presenter for UI updates
    """
    
    # Signals for window coordination
    stopRequested = Signal()
    backRequested = Signal()
    runRequested = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent
        self.test_type = TestType.COMPARATOR
        
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
            test_type="comparator"
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
        """
        Handle test completion notification (misleading name from base_test_worker).
        
        This is actually called AFTER a test completes, not when it starts.
        We use it to update worker activity visualization.
        """
        # Show this test is being "processed" by a worker
        self.presenter.mark_test_active(test_number)
    
    def on_worker_busy(self, worker_id: int, test_number: int):
        """Handle worker starting work on a test"""
        self.presenter.handle_worker_busy(worker_id, test_number)
    
    def on_worker_idle(self, worker_id: int):
        """Handle worker finishing work"""
        self.presenter.handle_worker_idle(worker_id)
    
    def on_test_completed(
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
        Handle test completion from worker.
        
        Translates worker signal to TestResult and delegates to presenter.
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
        
        # Store for detail view
        self.test_results[test_number] = result
        
        # Update UI through presenter
        self.presenter.handle_test_result(result)
        
        # Create and add card
        card = ComparatorTestCard(result)
        card.clicked.connect(self.show_test_detail)
        self.cards_section.add_card(card, result.passed)
    
    def on_all_tests_completed(self, all_passed: bool):
        """Handle test execution completion"""
        self.presenter.complete_execution()
        
        # Notify parent to enable save button
        if self.parent_window and hasattr(self.parent_window, "enable_save_button"):
            self.parent_window.enable_save_button()
    
    def show_test_detail(self, test_number: int):
        """Show detail dialog for test"""
        if test_number not in self.test_results:
            return
        
        result = self.test_results[test_number]
        data = result.data
        
        dialog = ComparatorDetailDialog(
            test_number=test_number,
            passed=result.passed,
            time=result.time,
            memory=result.memory,
            input_text=data['input_text'],
            correct_output=data['correct_output'],
            test_output=data['test_output'],
            parent=self
        )
        dialog.exec()
    
    def _get_worker_count(self) -> int:
        """Get worker count from parent"""
        worker = None
        if self.parent_window and hasattr(self.parent_window, 'comparator'):
            if hasattr(self.parent_window.comparator, 'get_current_worker'):
                worker = self.parent_window.comparator.get_current_worker()
        
        if worker and hasattr(worker, 'max_workers'):
            return worker.max_workers
        
        import multiprocessing
        return min(8, max(1, multiprocessing.cpu_count() - 1))
    
    def save_to_database(self):
        """Save results to database"""
        runner = None
        if hasattr(self, "runner"):
            runner = self.runner
        elif self.parent_window and hasattr(self.parent_window, "comparator"):
            runner = self.parent_window.comparator
        
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
