"""
BaseRunner - Consolidated runner patterns for all tools.

This class consolidates the 300+ lines of duplicated runner boilerplate
from ValidatorRunner, Benchmarker, and Comparator into a single reusable
base class with consistent threading, database integration, and lifecycle management.
"""

import os
import json
from typing import Dict, Any
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
    
    def __init__(self, workspace_dir: str, files_dict: Dict[str, str], 
                 test_type: str, optimization_level: str = 'O2'):
        """
        Initialize the base runner.
        
        Args:
            workspace_dir: Directory containing source files and executables
            files_dict: Dictionary mapping file keys to source file paths
            test_type: Type of test for database storage ('validator', 'stress', 'tle')
            optimization_level: Compiler optimization level
        """
        super().__init__()
        self.workspace_dir = workspace_dir
        self.files = files_dict
        self.test_type = test_type
        
        # Create executables dict from files dict
        self.executables = {
            key: os.path.join(workspace_dir, f"{key}.exe")
            for key in files_dict.keys()
        }
        
        # Initialize compiler
        self.compiler = BaseCompiler(
            workspace_dir=workspace_dir,
            files_dict=files_dict,
            optimization_level=optimization_level
        )
        
        # Connect compiler signals
        self.compiler.compilationFinished.connect(self.compilationFinished)
        self.compiler.compilationOutput.connect(self.compilationOutput)
        
        # Database integration
        self.db_manager = DatabaseManager()
        
        # Thread and worker management
        self.worker = None
        self.thread = None
        self.status_window = None
        
        # Test execution tracking
        self.test_start_time = None
        self.test_count = 0
        
        logger.debug(f"Initialized BaseRunner for {test_type} tests in {workspace_dir}")
    
    def compile_all(self) -> bool:
        """
        Compile all required files using the BaseCompiler.
        
        Returns:
            bool: True if compilation started successfully
        """
        # Set up status window if available
        status_window = self._create_compilation_status_window()
        if status_window:
            self.compiler.status_window = status_window
        
        return self.compiler.compile_all()
    
    def _create_compilation_status_window(self):
        """
        Create compilation status window - can be overridden by subclasses.
        
        Returns:
            Optional status window instance
        """
        # Import here to avoid circular dependencies
        try:
            from src.app.presentation.views.comparator.compilation_status_window import CompilationStatusWindow
            return CompilationStatusWindow()
        except ImportError:
            logger.warning("CompilationStatusWindow not available")
            return None
    
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
        
        # Create status window
        self.status_window = self._create_test_status_window()
        if self.status_window:
            self.status_window.show()
        
        # Create worker and thread
        self.worker = self._create_test_worker(test_count, **kwargs)
        self.thread = QThread()
        
        # Move worker to thread
        self.worker.moveToThread(self.thread)
        
        # Connect worker signals to status window
        if self.status_window:
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
        if self.thread and self.thread.isRunning():
            self.thread.quit()
            if not self.thread.wait(3000):  # Wait up to 3 seconds
                self.thread.terminate()
                self.thread.wait(1000)
        
        # Close status window
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
        self.stop()