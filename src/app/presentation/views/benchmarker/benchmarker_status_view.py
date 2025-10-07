"""
Benchmarker-specific status view.

Extends BaseStatusView to show benchmarker test execution with test cards
displaying performance metrics like execution time and memory usage against limits.
"""

from src.app.presentation.widgets.unified_status_view import BaseStatusView
from src.app.presentation.widgets.test_cards import BenchmarkerTestCard
from src.app.presentation.widgets.test_detail_view import BenchmarkerDetailDialog


class BenchmarkerStatusView(BaseStatusView):
    """
    Status view for benchmarker tests.
    
    Shows execution progress with cards for each test, displaying:
    - Test number and pass/fail status
    - Execution time vs time limit
    - Memory usage vs memory limit
    - Time limit exceeded indicator
    - Memory limit exceeded indicator
    
    Clicking a card shows detailed performance metrics in a dialog.
    """
    
    def __init__(self, time_limit_ms: float, memory_limit_mb: int, parent=None):
        """
        Initialize benchmarker status view.
        
        Args:
            time_limit_ms: Time limit in milliseconds
            memory_limit_mb: Memory limit in MB
            parent: Parent widget
        """
        super().__init__('benchmarker', parent)
        
        self.time_limit_ms = time_limit_ms
        self.memory_limit_mb = memory_limit_mb
        
        # Store test data for detail views
        self.test_data = {}  # {test_number: {test_name, time, memory, time_passed, memory_passed, input, output}}
        
    def on_test_completed(self, test_name: str, test_number: int, passed: bool,
                         execution_time: float, memory_used: float, memory_passed: bool,
                         input_data: str = "", output_data: str = "", test_size: int = 0):
        """
        Handle benchmarker test completion.
        
        Args:
            test_name: Test case name
            test_number: Test case number (1-indexed)
            passed: Whether test passed (both time and memory within limits)
            execution_time: Execution time in seconds
            memory_used: Memory usage in MB
            memory_passed: Whether memory limit was met
            input_data: Input data for the test
            output_data: Output data from the test
            test_size: Size of test input (number of lines)
        """
        # Update counters and progress (base class)
        # Convert time to milliseconds for display
        time_ms = execution_time * 1000
        super().on_test_completed(test_number, passed,
                                 time=execution_time, memory=memory_used,
                                 test_name=test_name,
                                 time_ms=time_ms,
                                 memory_passed=memory_passed)
        
        # Store test data for detail view
        self.test_data[test_number] = {
            'test_name': test_name,
            'passed': passed,
            'execution_time': execution_time,
            'time_ms': time_ms,
            'memory_used': memory_used,
            'time_passed': passed,  # In benchmarker, passed means time limit met
            'memory_passed': memory_passed,
            'time_limit_ms': self.time_limit_ms,
            'memory_limit_mb': self.memory_limit_mb,
            'input_data': input_data,
            'output_data': output_data,
            'test_size': test_size
        }
        
        # Create benchmarker-specific card
        card = BenchmarkerTestCard(
            test_number=test_number,
            passed=passed,
            time=execution_time,
            memory=memory_used,
            test_size=100  # Default test size for now (could be passed as parameter)
        )
        
        # Add card to section (will trigger layout switch on first failure)
        self.add_test_card(card)
        
    def show_test_detail(self, test_number: int):
        """
        Show detail view for a benchmarker test.
        
        Args:
            test_number: Test case number to show details for
        """
        if test_number not in self.test_data:
            return
        
        data = self.test_data[test_number]
        
        # Create and show detail dialog with input/output sections
        dialog = BenchmarkerDetailDialog(
            test_number=test_number,
            passed=data['passed'],
            time=data.get('execution_time', 0),
            memory=data.get('memory_used', 0),
            test_size=data.get('test_size', 0),
            input_data=data.get('input_data', ''),
            output_data=data.get('output_data', ''),
            parent=self
        )
        
        dialog.exec()
