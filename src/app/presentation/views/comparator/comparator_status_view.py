"""
Comparator-specific status view.

Extends BaseStatusView to show comparison test execution with test cards
displaying input, expected output, and actual output.
"""

from src.app.presentation.widgets.unified_status_view import BaseStatusView
from src.app.presentation.widgets.test_cards import ComparatorTestCard
from src.app.presentation.widgets.test_detail_view import ComparatorDetailDialog


class ComparatorStatusView(BaseStatusView):
    """
    Status view for comparator tests.
    
    Shows execution progress with cards for each test, displaying:
    - Test number and pass/fail status
    - Time and memory metrics (placeholders for now, Phase 4 will add actual tracking)
    - Input data
    - Expected output vs actual output
    
    Clicking a card shows detailed comparison in a dialog.
    """
    
    def __init__(self, parent=None):
        """
        Initialize comparator status view.
        
        Args:
            parent: Parent widget
        """
        super().__init__('comparator', parent)
        
        # Store test data for detail views
        self.test_data = {}  # {test_number: {input, correct, actual, time, memory}}
        
    def on_test_completed(self, test_number: int, passed: bool, 
                         input_text: str, correct_output: str, test_output: str,
                         time: float = 0.0, memory: float = 0.0):
        """
        Handle comparator test completion.
        
        Args:
            test_number: Test case number (1-indexed)
            passed: Whether test passed
            input_text: Test input
            correct_output: Expected output
            test_output: Actual program output
            time: Execution time in seconds (default 0.0 for Phase 3, Phase 4 will provide actual)
            memory: Memory usage in MB (default 0.0 for Phase 3, Phase 4 will provide actual)
        """
        # Update counters and progress (base class)
        super().on_test_completed(test_number, passed,
                                 time=time, memory=memory,
                                 input_text=input_text,
                                 correct_output=correct_output,
                                 test_output=test_output)
        
        # Store test data for detail view
        self.test_data[test_number] = {
            'passed': passed,
            'input_text': input_text,
            'correct_output': correct_output,
            'test_output': test_output,
            'time': time,
            'memory': memory
        }
        
        # Create comparator-specific card
        card = ComparatorTestCard(
            test_number=test_number,
            passed=passed,
            time=time,
            memory=memory,
            input_text=input_text,
            correct_output=correct_output,
            test_output=test_output
        )
        
        # Add card to section (will trigger layout switch on first failure)
        self.add_test_card(card)
        
    def show_test_detail(self, test_number: int):
        """
        Show detail view for a comparator test.
        
        Args:
            test_number: Test case number to show details for
        """
        if test_number not in self.test_data:
            return
        
        data = self.test_data[test_number]
        
        # Create and show detail dialog
        dialog = ComparatorDetailDialog(
            test_number=test_number,
            passed=data['passed'],
            time=data['time'],
            memory=data['memory'],
            input_text=data['input_text'],
            correct_output=data['correct_output'],
            test_output=data['test_output'],
            parent=self
        )
        
        dialog.exec()
