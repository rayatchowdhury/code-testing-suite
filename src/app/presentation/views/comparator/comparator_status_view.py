"""
Comparator Status View - migrated to StatusViewBase.

Reduced from 215 lines to ~60 lines following Phase 3C migration pattern.
Inherits common status view behavior from StatusViewBase.

NOTE: Comparator uses 'comparator' attribute (same pattern as benchmarker)
"""

from src.app.presentation.base.status_view_base import StatusViewBase
from src.app.presentation.widgets.status_view import TestResult, ComparatorTestCard
from src.app.presentation.widgets.test_detail_view import ComparatorDetailDialog


class ComparatorStatusView(StatusViewBase):
    """
    Comparator-specific status view.
    
    Responsibilities:
    - Translate comparator worker signals to TestResult
    - Create comparator-specific cards
    - Show comparator detail dialogs
    """
    
    def __init__(self, parent=None):
        super().__init__(parent, test_type="comparator")
    
    # ===== Template Methods (Required by StatusViewBase) =====
    
    def _get_runner_attribute_name(self) -> str:
        """Return 'comparator' (same pattern as benchmarker)"""
        return "comparator"
    
    def _get_card_class(self):
        """Return ComparatorTestCard class."""
        return ComparatorTestCard
    
    def _get_detail_dialog_class(self):
        """Return ComparatorDetailDialog class."""
        return ComparatorDetailDialog
    
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
        
        Translates comparator worker signal (7 params) to TestResult.
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
    
    def show_test_detail(self, test_number: int):
        """Show detail dialog for test."""
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
