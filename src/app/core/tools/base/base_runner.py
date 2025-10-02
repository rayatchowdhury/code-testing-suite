"""
BaseRunner - Consolidated runner patterns for all tools.

This class consolidates the 300+ lines of duplicated runner boilerplate
from ValidatorRunner, Benchmarker, and Comparator into a single reusable
base class with consistent threading, database integration, and lifecycle management.
"""

import os
import json
from typing import Dict, Any, Optional
from datetime import datetime
from PySide6.QtCore import QObject, Signal, QThread
from src.app.core.tools.base.base_compiler import BaseCompiler
from src.app.persistence.database import DatabaseManager, TestResult
import logging

logger = logging.getLogger(__name__)


class BaseRunner(QObject):
    """
    Abstract base class for all test runners in the Code Testing Suite.
    
    This class consolidates the common runner patterns that were duplicated
    across ValidatorRunner, Benchmarker, and Comparator, providing standardized:
    
    - **Compilation Integration**: BaseCompiler usage with status windows
    - **Threading Patterns**: Worker/thread creation and lifecycle management  
    - **Database Integration**: Template method pattern for test result storage
    - **Signal Management**: Consistent signal forwarding and connections
    - **Resource Cleanup**: Proper cleanup of threads, processes, and windows
    
    ## Template Method Pattern
    
    This class implements the Template Method pattern to provide consistent
    behavior while allowing specialization:
    
    1. **_create_test_worker()** - Subclasses create their specialized worker
    2. **_create_test_result()** - Subclasses build test-specific result objects
    3. **_create_test_status_window()** - Subclasses create appropriate status windows
    4. **_connect_worker_signals()** - Subclasses connect runner-specific signals
    
    ## Usage Example
    
    ```python
    class MyRunner(BaseRunner):
        def __init__(self, workspace_dir):
            files = {'test': os.path.join(workspace_dir, 'test.cpp')}
            super().__init__(workspace_dir, files, test_type='my_test')
        
        def _create_test_worker(self, test_count, **kwargs):
            return MyTestWorker(self.workspace_dir, self.executables, test_count)
        
        def _create_test_result(self, all_passed, test_results, ...):
            # Create MyTestResult with test-specific analysis
            return TestResult(...)
    ```
    
    ## Architecture Benefits
    
    - **Code Reduction**: Eliminates ~200 lines of duplicate patterns per runner
    - **Consistency**: All runners follow same initialization/lifecycle patterns  
    - **Maintainability**: Common bugs fixed once in base class
    - **Extensibility**: New runners easily inherit established patterns
    - **Testing**: Base functionality can be tested independently
    """
    
    # Common signals for all runners
    compilationFinished = Signal(bool)  # True if successful, False if failed
    compilationOutput = Signal(str, str)  # (message, type)
    testStarted = Signal(int, int)  # current test, total tests
    allTestsCompleted = Signal(bool)  # True if all passed
    
    # UI state change signals (for clean separation of concerns)
    testingStarted = Signal()  # Emitted when test execution begins (UI can switch to test mode)
    testingCompleted = Signal()  # Emitted when test execution ends (UI can restore normal mode)
    
    def __init__(self, workspace_dir: str, files_dict: Dict[str, str], 
                 test_type: str, optimization_level: str = 'O2', config: Optional[Dict[str, Any]] = None):
        """
        Initialize the base runner with multi-language support.
        
        Args:
            workspace_dir: Directory containing source files and executables
            files_dict: Dictionary mapping file keys to source file paths
            test_type: Type of test for database storage ('validator', 'stress', 'tle')
            optimization_level: Compiler optimization level
            config: Optional configuration dictionary with language settings
        """
        super().__init__()
        self.workspace_dir = workspace_dir
        self.files = files_dict
        self.test_type = test_type  # Used for both database tracking and file organization
        self.config = config or {}
        
        # Initialize compiler with config for multi-language support and nested structure
        self.compiler = BaseCompiler(
            workspace_dir=workspace_dir,
            files_dict=files_dict,
            optimization_level=optimization_level,
            config=self.config,
            test_type=test_type  # Pass test_type for nested file structure
        )
        
        # Executables will be set by compiler based on detected languages
        self.executables = self.compiler.executables
        
        # Connect compiler signals
        self.compiler.compilationFinished.connect(self.compilationFinished)
        self.compiler.compilationOutput.connect(self.compilationOutput)
        
        # Database integration
        self.db_manager = DatabaseManager()
        
        # Thread and worker management
        self.worker = None
        self.thread = None
        self.status_window = None
        
        # Display area integration (for unified status view)
        self.parent_window = None
        self.status_view = None  # Unified status view widget (not dialog)
        self.original_display_content = None  # For restoring display area
        
        # Test execution tracking
        self.test_start_time = None
        self.test_count = 0
        
        logger.debug(f"Initialized BaseRunner for {test_type} tests in {workspace_dir}")
    
    def set_parent_window(self, window):
        """
        Set parent window for display area integration.
        
        This enables the unified status view pattern where test execution
        status is embedded in the display area instead of a popup dialog.
        
        Args:
            window: Parent window (ComparatorWindow, ValidatorWindow, etc.)
                   Must have a display_area attribute with set_content() method
        """
        self.parent_window = window
        logger.debug(f"Set parent window for {self.test_type} runner")
    
    def compile_all(self) -> bool:
        """
        Compile all required files using the BaseCompiler.
        
        Returns:
            bool: True if compilation started successfully
        """
        return self.compiler.compile_all()
    
    def run_tests(self, test_count: int, **kwargs) -> None:
        """
        Run tests using threading and worker pattern - TEMPLATE METHOD.
        
        This method implements the Template Method pattern, providing the common
        infrastructure for test execution while allowing subclasses to specialize
        worker creation and result processing.
        
        ## Execution Flow:
        
        1. **Initialize**: Set test_count, start_time, create status window
        2. **Create Worker**: Call _create_test_worker() template method
        3. **Setup Threading**: Create QThread and move worker to thread
        4. **Connect Signals**: Connect worker signals to status window and external listeners
        5. **Database Integration**: Connect worker completion to _save_test_results()
        6. **Start Execution**: Start thread and begin test execution
        
        ## Template Methods Called:
        
        - **_create_test_worker()**: Subclass creates specialized worker instance
        - **_create_test_status_window()**: Subclass creates appropriate status window
        - **_connect_worker_signals()**: Subclass connects runner-specific signals
        
        Args:
            test_count: Number of tests to execute
            **kwargs: Additional test-specific parameters passed to _create_test_worker()
            
        Example:
            ```python
            # ValidatorRunner usage
            runner.run_tests(10, max_workers=4)
            
            # Benchmarker usage  
            runner.run_tests(5, time_limit=1000, memory_limit=256, max_workers=2)
            ```
        """
        self.test_count = test_count
        self.test_start_time = datetime.now()
        
        # Try creating unified status view first (if parent window is set)
        if hasattr(self, 'parent_window') and self.parent_window:
            self.status_view = self._create_test_status_window()
            
            if self.status_view:
                # Connect status view signals
                if hasattr(self.status_view, 'stopRequested'):
                    self.status_view.stopRequested.connect(self.stop)
                if hasattr(self.status_view, 'backRequested'):
                    self.status_view.backRequested.connect(self._handle_back_request)
                
                # Integrate into display area
                self._integrate_status_view()
                
                # Notify view that tests are starting
                if hasattr(self.status_view, 'on_tests_started'):
                    self.status_view.on_tests_started(test_count)
        else:
            # Fallback to old dialog-based status window
            self.status_window = self._create_test_status_window()
            if self.status_window:
                self.status_window.show()
        
        # Create worker and thread
        self.worker = self._create_test_worker(test_count, **kwargs)
        self.thread = QThread()
        
        # Move worker to thread
        self.worker.moveToThread(self.thread)
        
        # Connect worker signals to status view OR status window
        if self.status_view:
            self._connect_worker_to_status_view(self.worker, self.status_view)
        elif self.status_window:
            self._connect_worker_to_status_window(self.worker, self.status_window)
        
        # Connect worker signals to external listeners
        self._connect_worker_signals(self.worker)
        
        # Connect database saving
        self.worker.allTestsCompleted.connect(self._save_test_results)
        
        # Set up thread lifecycle
        self.thread.started.connect(self.worker.run_tests)
        self.worker.allTestsCompleted.connect(self.thread.quit)
        self.worker.allTestsCompleted.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        
        # Start the thread
        self.thread.start()
        
        logger.debug(f"Started {test_count} {self.test_type} tests")
    
    def _create_test_worker(self, test_count: int, **kwargs):
        """
        Create the appropriate test worker - ABSTRACT METHOD.
        
        Must be implemented by subclasses to create their specific worker type.
        
        Args:
            test_count: Number of tests to run
            **kwargs: Additional test-specific parameters
            
        Returns:
            Test worker instance
        """
        raise NotImplementedError("Subclasses must implement _create_test_worker()")
    
    def _create_test_status_window(self):
        """
        Create test status window - can be overridden by subclasses.
        
        Returns:
            Optional status window instance
        """
        # Default implementation - subclasses should override
        return None
    
    def _connect_worker_to_status_window(self, worker, status_window):
        """
        Connect worker signals to status window.
        
        Can be overridden by subclasses for specific signal connections.
        
        Args:
            worker: Test worker instance
            status_window: Status window instance
        """
        # Default connections - subclasses can override
        if hasattr(worker, 'testStarted') and hasattr(status_window, 'show_test_running'):
            worker.testStarted.connect(status_window.show_test_running)
        
        if hasattr(worker, 'testCompleted') and hasattr(status_window, 'show_test_complete'):
            worker.testCompleted.connect(status_window.show_test_complete)
        
        if hasattr(worker, 'allTestsCompleted') and hasattr(status_window, 'show_all_passed'):
            worker.allTestsCompleted.connect(status_window.show_all_passed)
    
    def _connect_worker_to_status_view(self, worker, status_view):
        """
        Connect worker signals to unified status view.
        
        Args:
            worker: Test worker instance
            status_view: Unified status view widget instance
        """
        # Connect to view lifecycle methods
        if hasattr(worker, 'testStarted') and hasattr(status_view, 'on_test_running'):
            worker.testStarted.connect(status_view.on_test_running)
        
        if hasattr(worker, 'testCompleted') and hasattr(status_view, 'on_test_completed'):
            worker.testCompleted.connect(status_view.on_test_completed)
        
        if hasattr(worker, 'allTestsCompleted') and hasattr(status_view, 'on_all_tests_completed'):
            worker.allTestsCompleted.connect(status_view.on_all_tests_completed)
    
    def _integrate_status_view(self):
        """Integrate status view into parent window's display area and update sidebar"""
        if not hasattr(self, 'parent_window') or not self.parent_window:
            logger.warning("Cannot integrate status view: no parent window set")
            return
        
        if not hasattr(self.parent_window, 'display_area'):
            logger.warning("Cannot integrate status view: parent window has no display_area")
            return
        
        # Store original content for restoration (only if not already stored)
        # This prevents storing a status view as "original" when running tests again
        try:
            # Use layout() method to get the layout (Qt's built-in method)
            layout = self.parent_window.display_area.layout()
            if layout and layout.count() > 0:
                current_widget = layout.itemAt(0).widget()
                
                # Only store as original if we don't have one yet
                # This preserves the FIRST original content (test window) across multiple runs
                if not hasattr(self, 'original_display_content') or self.original_display_content is None:
                    self.original_display_content = current_widget
                    logger.debug("Stored original display content for first time")
                
                # Remove current widget from layout (could be old status view or original content)
                if current_widget:
                    layout.removeWidget(current_widget)
                    current_widget.setParent(None)  # Detach from parent
                    current_widget.hide()  # Hide it
        except Exception as e:
            logger.warning(f"Error storing original content: {e}")
            if not hasattr(self, 'original_display_content'):
                self.original_display_content = None
        
        # Add status view to display area
        if self.status_view:
            self.parent_window.display_area.layout().addWidget(self.status_view)
            logger.debug(f"Integrated status view into display area")
        else:
            logger.warning("Display area has no set_content method")
        
        # Emit signal for UI to switch to test mode (clean separation of concerns)
        try:
            self.testingStarted.emit()
            logger.debug("Emitted testingStarted signal")
        except (RuntimeError, AttributeError):
            # Signal not initialized (e.g., in tests with __new__ without __init__)
            pass
    
    def _handle_back_request(self):
        """Handle back button from status view - restore original display and sidebar"""
        if hasattr(self, 'parent_window') and self.parent_window and self.original_display_content:
            # Remove status view from layout
            layout = self.parent_window.display_area.layout()
            if layout and self.status_view:
                layout.removeWidget(self.status_view)
                self.status_view.setParent(None)
                self.status_view.hide()
            
            # Restore original display content
            # Note: We keep the reference to original_display_content so it can be reused
            # if tests are run again from the restored test window
            if self.original_display_content:
                self.parent_window.display_area.layout().addWidget(self.original_display_content)
                self.original_display_content.show()  # Show the restored widget
                logger.debug("Restored original display content (kept reference for future runs)")
            
            # Emit signal for UI to restore normal mode (clean separation of concerns)
            try:
                self.testingCompleted.emit()
                logger.debug("Emitted testingCompleted signal")
            except (RuntimeError, AttributeError):
                # Signal not initialized (e.g., in tests with __new__ without __init__)
                pass
    
    def _connect_worker_signals(self, worker):
        """
        Connect worker signals to external listeners.
        
        Args:
            worker: Test worker instance
        """
        # Forward signals to external listeners
        if hasattr(worker, 'testStarted'):
            worker.testStarted.connect(self.testStarted)
        
        if hasattr(worker, 'allTestsCompleted'):
            worker.allTestsCompleted.connect(self.allTestsCompleted)
    
    def _save_test_results(self, all_passed: bool) -> None:
        """
        Save test results to database using template method pattern.
        
        Args:
            all_passed: Whether all tests passed
        """
        if not hasattr(self, 'worker') or not self.worker:
            logger.warning("No worker available for result saving")
            return
        
        try:
            # Get test results from worker
            test_results = []
            if hasattr(self.worker, 'get_results'):
                test_results = self.worker.get_results()
            elif hasattr(self.worker, 'test_results'):
                test_results = getattr(self.worker, 'test_results', [])
            
            # Calculate statistics
            total_time = (datetime.now() - self.test_start_time).total_seconds()
            passed_tests = sum(1 for result in test_results if result.get('passed', False))
            failed_tests = len(test_results) - passed_tests
            
            # Create test result object using template method
            test_result = self._create_test_result(
                all_passed=all_passed,
                test_results=test_results,
                passed_tests=passed_tests,
                failed_tests=failed_tests,
                total_time=total_time
            )
            
            # Save to database
            result_id = self.db_manager.save_test_result(test_result)
            if result_id > 0:
                logger.info(f"Test results saved to database with ID: {result_id}")
            else:
                logger.error("Failed to save test results to database")
                
        except Exception as e:
            logger.error(f"Error saving test results: {e}")
        finally:
            # Emit signal for UI to restore normal mode (clean separation of concerns)
            try:
                self.testingCompleted.emit()
                logger.debug("Emitted testingCompleted signal after test completion")
            except (RuntimeError, AttributeError):
                # Signal not initialized (e.g., in tests with __new__ without __init__)
                pass
    
    def _create_test_result(self, all_passed: bool, test_results: list, 
                           passed_tests: int, failed_tests: int, total_time: float) -> TestResult:
        """
        Create test result object - ABSTRACT METHOD.
        
        Must be implemented by subclasses to create their specific test result format.
        
        Args:
            all_passed: Whether all tests passed
            test_results: List of individual test results
            passed_tests: Number of passed tests
            failed_tests: Number of failed tests
            total_time: Total execution time
            
        Returns:
            TestResult: Database test result object
        """
        raise NotImplementedError("Subclasses must implement _create_test_result()")
    
    def _get_test_file_path(self) -> str:
        """
        Get the primary test file path for database storage.
        
        Returns:
            str: Path to the main test file
        """
        # Default: use 'test' file if available, otherwise first file
        if 'test' in self.files:
            return self.files['test']
        elif self.files:
            return next(iter(self.files.values()))
        else:
            return ""
    
    def _create_files_snapshot(self) -> Dict[str, Any]:
        """
        Create a snapshot of workspace files for database storage.
        
        Returns:
            Dict[str, Any]: Files snapshot
        """
        return DatabaseManager.create_files_snapshot(self.workspace_dir).__dict__
    
    def stop(self) -> None:
        """Stop any running processes and clean up resources."""
        # Stop compilation
        if hasattr(self, 'compiler') and self.compiler:
            self.compiler.stop()
        
        # Stop worker
        if self.worker and hasattr(self.worker, 'stop'):
            self.worker.stop()
        
        # Clean up thread
        try:
            if self.thread and hasattr(self.thread, 'isRunning') and self.thread.isRunning():
                self.thread.quit()
                if not self.thread.wait(3000):  # Wait up to 3 seconds
                    self.thread.terminate()
                    self.thread.wait(1000)
        except RuntimeError:
            # Handle case where Qt objects are already deleted
            pass
        
        # Restore display area if using unified status view
        if hasattr(self, 'status_view') and self.status_view:
            self._handle_back_request()
            self.status_view = None
        
        # Close status window (old dialog pattern)
        if self.status_window:
            self.status_window.close()
        
        logger.debug(f"Stopped {self.test_type} runner")
    
    def get_workspace_files(self) -> Dict[str, str]:
        """
        Get current workspace files.
        
        Returns:
            Dict[str, str]: Dictionary of file keys to paths
        """
        return self.files.copy()
    
    def get_executables(self) -> Dict[str, str]:
        """
        Get current executable files.
        
        Returns:
            Dict[str, str]: Dictionary of executable keys to paths
        """
        return self.executables.copy()
    
    def is_compiled(self) -> bool:
        """
        Check if all required files are compiled and up-to-date.
        
        Returns:
            bool: True if all executables exist and are current
        """
        for key in self.files:
            if self.compiler._needs_recompilation(key):
                return False
        return True
    
    def __del__(self):
        """Ensure proper cleanup on destruction."""
        try:
            self.stop()
        except RuntimeError:
            # Skip cleanup if Qt objects are already deleted
            pass