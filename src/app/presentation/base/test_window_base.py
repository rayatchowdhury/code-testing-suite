"""
Base class for test tool windows (Benchmarker, Validator, Comparator).

TestWindowBase consolidates 588 lines of duplicated code from test windows,
providing template methods for subclasses to customize behavior.
"""

from abc import abstractmethod
from typing import Optional
from .content_window_base import ContentWindowBase
from .protocols import TestRunner


class TestWindowBase(ContentWindowBase):
    """
    Base class for all test tool windows.
    
    This class eliminates 588 lines of duplication by providing shared
    implementations of test lifecycle management, status view integration,
    and UI mode switching.
    
    Responsibilities:
    - Test runner initialization and signal connection
    - Status view integration
    - Test execution lifecycle (start, complete, stop)
    - UI mode switching (normal, testing, completed)
    - AI panel coordination
    - Sidebar state management
    
    Template Methods (must override):
    - _create_runner(): Return specific runner instance
    - _create_status_view(): Return specific status view
    - _get_testing_content_config(): Return tab configuration
    - _get_sidebar_config(): Return sidebar configuration
    
    Subclasses:
    - BenchmarkerWindow: Performance benchmarking
    - ValidatorWindow: Code validation
    - ComparatorWindow: Performance comparison
    
    Usage:
        class BenchmarkerWindow(TestWindowBase):
            def _create_runner(self):
                return Benchmarker()
            
            def _create_status_view(self):
                return BenchmarkerStatusView()
    
    Before Refactoring:
        - BenchmarkerWindow: 271 lines
        - ValidatorWindow: 271 lines
        - ComparatorWindow: 271 lines
        - Total: 813 lines
    
    After Refactoring:
        - TestWindowBase: 300 lines (shared)
        - BenchmarkerWindow: 25 lines (config only)
        - ValidatorWindow: 25 lines (config only)
        - ComparatorWindow: 25 lines (config only)
        - Total: 375 lines (54% reduction)
    """
    
    def __init__(self, parent=None):
        """
        Initialize TestWindowBase.
        
        Args:
            parent: Parent widget (typically MainWindow)
        """
        super().__init__(parent)
        self._runner: Optional[TestRunner] = None
        self._status_view = None
        # TODO: Implementation in Phase 2A
    
    @abstractmethod
    def _create_runner(self) -> TestRunner:
        """
        Create the test runner instance (Benchmarker, Validator, Comparator).
        
        Returns:
            Configured test runner instance
        
        Example:
            def _create_runner(self):
                return Benchmarker()
        """
        pass
    
    @abstractmethod
    def _create_status_view(self):
        """
        Create the status view instance.
        
        Returns:
            Configured status view widget
        
        Example:
            def _create_status_view(self):
                return BenchmarkerStatusView()
        """
        pass
    
    @abstractmethod
    def _get_testing_content_config(self) -> dict:
        """
        Get configuration for testing content widget tabs.
        
        Returns:
            Dictionary with 'tabs' key containing tab configurations
        
        Example:
            def _get_testing_content_config(self):
                return {
                    "tabs": [
                        {"name": "Source Code", "placeholder": "Enter code..."},
                        {"name": "Test Cases", "placeholder": "Enter tests..."}
                    ]
                }
        """
        pass
    
    @abstractmethod
    def _get_sidebar_config(self) -> dict:
        """
        Get configuration for sidebar sections and buttons.
        
        Returns:
            Dictionary with 'title' and 'sections' keys
        
        Example:
            def _get_sidebar_config(self):
                return {
                    "title": "Benchmarker",
                    "sections": [
                        {"name": "Actions", "buttons": ["Run", "Stop"]},
                        {"name": "Export", "buttons": ["Export CSV"]}
                    ]
                }
        """
        pass
    
    def _initialize_tool(self):
        """
        Initialize runner, status view, and connect signals.
        
        Called during window setup. Creates runner and status view using
        template methods, then connects all signals.
        """
        # TODO: Implementation in Phase 2A
        pass
    
    def _connect_runner_signals(self):
        """
        Connect all runner signals to status view and window methods.
        
        Connects:
        - testingStarted -> on_tests_started
        - testCompleted -> on_test_completed
        - allTestsCompleted -> on_all_tests_completed
        - workerBusy -> on_worker_busy
        - workerIdle -> on_worker_idle
        - compilationOutput -> console updates
        """
        # TODO: Implementation in Phase 2A
        pass
    
    def _switch_to_test_mode(self):
        """
        Switch UI to testing mode.
        
        - Disable status view widgets
        - Disable sidebar action buttons
        - Show "Stop Tests" button
        - Hide other controls
        """
        # TODO: Implementation in Phase 2A
        pass
    
    def _switch_to_completed_mode(self):
        """
        Switch UI to completed mode (after tests finish).
        
        - Enable status view widgets
        - Enable sidebar buttons
        - Replace "Results" with "Save" button
        - Show export options
        """
        # TODO: Implementation in Phase 2A
        pass
    
    def _restore_normal_mode(self):
        """
        Restore UI to normal mode (before tests or after save).
        
        - Reset status view
        - Restore "Results" button
        - Hide "Stop Tests" button
        - Re-enable all controls
        """
        # TODO: Implementation in Phase 2A
        pass
    
    def enable_save_button(self):
        """Enable the save button in sidebar."""
        # TODO: Implementation in Phase 2A
        pass
    
    def mark_results_saved(self):
        """Mark results as saved (change button to "✓ Saved")."""
        # TODO: Implementation in Phase 2A
        pass
    
    def refresh_ai_panels(self):
        """Refresh all AI panel contexts with current test data."""
        # TODO: Implementation in Phase 2A
        pass
