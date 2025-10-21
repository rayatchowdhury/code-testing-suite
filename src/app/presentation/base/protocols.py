"""
Protocol definitions for presentation layer components.

Protocols define interfaces that components must implement, enabling
type checking and dependency inversion.

Analysis completed from:
- src/app/core/tools/benchmarker.py
- src/app/core/tools/base/base_runner.py  
- src/app/presentation/views/benchmarker/benchmarker_window.py
- src/app/presentation/widgets/status_view/widgets.py
- src/app/presentation/widgets/status_view/cards.py
"""

from typing import Protocol, runtime_checkable, Optional
from PySide6.QtCore import Signal

@runtime_checkable
class TestRunner(Protocol):
    """
    Protocol for test runner objects (Benchmarker, Validator, Comparator).
    
    All test runners inherit from BaseRunner and must emit these signals
    and provide these methods to work with TestWindowBase.
    
    Analyzed from:
    - Benchmarker (inherits BaseRunner + adds testCompleted)
    - Validator (inherits BaseRunner + adds testCompleted)
    - Comparator (inherits BaseRunner + adds testCompleted)
    
    All runners inherit these signals from BaseRunner:
    - compilationFinished(bool)
    - compilationOutput(str, str) 
    - testStarted(int, int)
    - allTestsCompleted(bool)
    - testingStarted()
    - testingCompleted()
    
    Each runner adds its own testCompleted signal with runner-specific signature.
    """
    
    # Signals (from BaseRunner)
    compilationOutput: Signal  # Signal(str, str) - message, type
    compilationFinished: Signal  # Signal(bool) - success
    testingStarted: Signal  # Signal() - test execution begins
    testingCompleted: Signal  # Signal() - test execution ends
    testStarted: Signal  # Signal(int, int) - current, total
    allTestsCompleted: Signal  # Signal(bool) - all_passed
    
    # testCompleted varies by runner - not included in protocol
    # Benchmarker: Signal(str, int, bool, float, float, bool, str, str, int)
    # Validator: Signal(str, int, bool, float, float, bool, str, str)
    # Comparator: Signal(str, int, bool, float, float, bool, str, str, str, str)
    
    # Required Methods
    def compile_all(self) -> bool:
        """Compile all source files. Returns True if compilation started."""
        ...
    
    def run_tests(self, test_count: int, **kwargs) -> None:
        """
        Run tests with specified count.
        
        Args:
            test_count: Number of tests to run
            **kwargs: Runner-specific arguments
        """
        ...
    
    def stop(self) -> None:
        """Stop all running tests and workers."""
        ...


@runtime_checkable  
class TestCard(Protocol):
    """
    Protocol for test result card widgets.
    
    Cards display individual test results in status views.
    Analyzed from: BaseTestCard and domain-specific cards.
    
    All test cards inherit from BaseTestCard which provides:
    - Test number, passed/failed status
    - Time and memory display
    - Click handling for detail view
    """
    
    # Signals
    clicked: Signal  # Signal(int) - test_number
    
    # Attributes
    test_number: int
    passed: bool
    time: float
    memory: float
    
    def mousePressEvent(self, event) -> None:
        """
        Handle mouse click to show test details.
        
        Emits clicked signal with test_number.
        """
        ...


@runtime_checkable
class TestDetailDialog(Protocol):
    """
    Protocol for test detail dialog windows.
    
    Dialogs show detailed information when a test card is clicked.
    Analyzed from: BenchmarkerDetailDialog, ValidatorDetailDialog, etc.
    
    All detail dialogs use static show() method for display.
    """
    
    @staticmethod
    def show(test_result: object, parent=None) -> None:
        """
        Display the dialog with test result details.
        
        Args:
            test_result: TestResult object with test data
            parent: Parent widget for dialog
        """
        ...


@runtime_checkable
class NavigationManager(Protocol):
    """
    Protocol for window navigation managers.
    
    Manages window lifecycle and navigation history.
    Implemented by: WindowManager in window_management.py
    """
    
    def show_window(self, window_name: str, **kwargs) -> bool:
        """
        Show a window by name.
        
        Args:
            window_name: Name of window to show
            **kwargs: Window initialization arguments
            
        Returns:
            True if successful
        """
        ...
    
    def go_back(self) -> bool:
        """
        Navigate to previous window in history.
        
        Returns:
            True if successful
        """
        ...
    
    def current_window_name(self) -> Optional[str]:
        """
        Get the name of the currently displayed window.
        
        Returns:
            Window name or None if no window active
        """
        ...
