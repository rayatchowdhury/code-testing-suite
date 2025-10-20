"""
Protocol definitions for presentation layer components.

Protocols define interfaces that components must implement, enabling
type checking and dependency inversion.
"""

from typing import Protocol, runtime_checkable
from PySide6.QtCore import Signal


@runtime_checkable
class TestRunner(Protocol):
    """
    Protocol for test runner objects (Benchmarker, Validator, Comparator).
    
    All test runners must emit these signals and provide these methods
    to work with TestWindowBase.
    """
    
    # Signals
    compilationOutput: Signal
    testingStarted: Signal
    testingCompleted: Signal
    allTestsCompleted: Signal
    workerBusy: Signal
    workerIdle: Signal
    
    def save_test_results(self) -> bool:
        """Save test results to database. Returns True if successful."""
        ...
    
    def stop_testing(self) -> None:
        """Stop all running tests."""
        ...


@runtime_checkable  
class TestCard(Protocol):
    """
    Protocol for test result card widgets.
    
    Cards display individual test results in status views.
    """
    
    def update_status(self, status: str) -> None:
        """Update the test status (e.g., 'Running', 'Passed', 'Failed')."""
        ...
    
    def update_time(self, time: float) -> None:
        """Update the execution time display."""
        ...
    
    def set_result(self, result: object) -> None:
        """Set the complete test result object."""
        ...


@runtime_checkable
class TestDetailDialog(Protocol):
    """
    Protocol for test detail dialog windows.
    
    Dialogs show detailed information when a test card is clicked.
    """
    
    @staticmethod
    def show(test_result: object, parent=None) -> None:
        """Display the dialog with test result details."""
        ...


@runtime_checkable
class NavigationManager(Protocol):
    """
    Protocol for window navigation managers.
    
    Manages window lifecycle and navigation history.
    """
    
    def show_window(self, window_name: str, **kwargs) -> bool:
        """Show a window by name. Returns True if successful."""
        ...
    
    def go_back(self) -> bool:
        """Navigate to previous window. Returns True if successful."""
        ...
    
    def current_window_name(self) -> str:
        """Get the name of the currently displayed window."""
        ...
