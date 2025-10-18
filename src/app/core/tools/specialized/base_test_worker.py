"""
Base test worker for parallel test execution.

This module provides the foundational worker class that all specialized test workers
(Benchmark, Comparison, Validator) inherit from to eliminate code duplication.

Key features:
- Thread-safe state management with locks (Issue #7 fix)
- Parallel test execution using ThreadPoolExecutor
- Template method pattern for _run_single_test()
- Async output reading helpers to prevent pipe deadlocks
- Consistent error handling and result management
"""

import multiprocessing
import threading
from abc import ABCMeta, abstractmethod
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any, Dict, List, Optional, Tuple

from PySide6.QtCore import QObject, Signal, Slot


# Resolve metaclass conflict between QObject and ABC
class QObjectABCMeta(type(QObject), ABCMeta):
    """Combined metaclass for QObject and ABC to avoid metaclass conflict."""
    pass


class BaseTestWorker(QObject, metaclass=QObjectABCMeta):
    """
    Base worker class for parallel test execution.
    
    Provides common functionality for all test workers:
    - Thread-safe is_running state management
    - Parallel test execution with ThreadPoolExecutor
    - Standardized signal emissions
    - Abstract _run_single_test() for specialization
    
    Signals:
        testStarted: Emitted when a test begins (completed_count, total_count)
        testCompleted: Emitted when a test finishes (implementation-specific params)
        allTestsCompleted: Emitted when all tests finish (all_passed: bool)
    """
    
    # Base signals - specialized workers add their own testCompleted signature
    testStarted = Signal(int, int)  # completed_count, total_count
    allTestsCompleted = Signal(bool)  # all_passed
    
    def __init__(
        self,
        workspace_dir: str,
        executables: Dict[str, str],
        test_count: int = 1,
        max_workers: Optional[int] = None,
        execution_commands: Optional[Dict[str, List[str]]] = None
    ):
        """
        Initialize base test worker.
        
        Args:
            workspace_dir: Path to workspace directory
            executables: Dictionary mapping language to executable path
            test_count: Number of tests to run
            max_workers: Maximum parallel workers (None = auto-calculate)
            execution_commands: Custom execution commands per language
        """
        super().__init__()
        
        # Core attributes
        self.workspace_dir = workspace_dir
        self.executables = executables
        self.test_count = test_count
        
        # Thread-safe state management (Issue #7)
        self._is_running = True
        self._state_lock = threading.Lock()
        
        # Thread-safe results storage
        self.test_results: List[Dict[str, Any]] = []
        self._results_lock = threading.Lock()
        
        # Calculate optimal worker count (subclasses can override)
        if max_workers is not None:
            self.max_workers = max_workers
        else:
            self.max_workers = self._calculate_optimal_workers()
        
        # Multi-language support
        if execution_commands:
            self.execution_commands = execution_commands
        else:
            # Default: wrap executable in list
            self.execution_commands = {k: [v] for k, v in executables.items()}
    
    @property
    def is_running(self) -> bool:
        """
        Thread-safe read of running state.
        
        Issue #7 fix: Uses lock to prevent race conditions during stop().
        """
        with self._state_lock:
            return self._is_running
    
    @is_running.setter
    def is_running(self, value: bool) -> None:
        """
        Thread-safe write of running state.
        
        Issue #7 fix: Uses lock to prevent race conditions during stop().
        """
        with self._state_lock:
            self._is_running = value
    
    def _calculate_optimal_workers(self) -> int:
        """
        Calculate optimal number of parallel workers.
        
        Default implementation uses CPU count - 1, capped at 8.
        Subclasses can override for specific needs (e.g., benchmark uses 4).
        
        Returns:
            Optimal worker count (minimum 1)
        """
        return min(8, max(1, multiprocessing.cpu_count() - 1))
    
    @Slot()
    def run_tests(self) -> None:
        """
        Run all tests in parallel using ThreadPoolExecutor.
        
        Template method pattern: calls abstract _run_single_test() for each test.
        Handles parallel execution, cancellation, result collection, and signal emissions.
        """
        all_passed = True
        completed_tests = 0
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all tests
            future_to_test = {
                executor.submit(self._run_single_test, i): i
                for i in range(1, self.test_count + 1)
            }
            
            # Process results as they complete
            for future in as_completed(future_to_test):
                # Check if stop() was called
                if not self.is_running:
                    # Cancel remaining tests
                    for f in future_to_test:
                        f.cancel()
                    break
                
                test_number = future_to_test[future]
                completed_tests += 1
                
                try:
                    test_result = future.result()
                    
                    if test_result:
                        # Store result thread-safely
                        with self._results_lock:
                            self.test_results.append(test_result)
                        
                        # Emit progress signal
                        self.testStarted.emit(completed_tests, self.test_count)
                        
                        # Subclasses emit their own testCompleted signal here
                        self._emit_test_completed(test_result)
                        
                        # Track overall pass/fail
                        if not test_result.get("passed", False):
                            all_passed = False
                
                except Exception as e:
                    # Handle unexpected errors
                    print(f"Error running test {test_number}: {e}")
                    all_passed = False
        
        # Emit completion signal
        self.allTestsCompleted.emit(all_passed)
    
    @abstractmethod
    def _run_single_test(self, test_number: int) -> Dict[str, Any]:
        """
        Run a single test.
        
        Abstract method that subclasses must implement with their specific test logic.
        
        Args:
            test_number: Test number to run
        
        Returns:
            Dictionary containing test results (must include 'passed' key)
        """
        raise NotImplementedError("Subclasses must implement _run_single_test()")
    
    @abstractmethod
    def _emit_test_completed(self, test_result: Dict[str, Any]) -> None:
        """
        Emit test completed signal.
        
        Abstract method for subclasses to emit their custom testCompleted signal
        with implementation-specific parameters.
        
        Args:
            test_result: Test result dictionary
        """
        raise NotImplementedError("Subclasses must implement _emit_test_completed()")
    
    def stop(self) -> None:
        """
        Stop the worker and cancel any running tests.
        
        Issue #7 fix: Thread-safe stop using property setter with lock.
        """
        self.is_running = False
    
    def get_test_results(self) -> List[Dict[str, Any]]:
        """
        Get thread-safe copy of test results.
        
        Returns:
            Copy of test results list for safe access from other threads
        """
        with self._results_lock:
            return self.test_results.copy()
    
    # ==================== Async Output Reading Helpers ====================
    # These methods eliminate 9x duplication of thread-based pipe reading
    
    @staticmethod
    def _create_async_output_reader(process) -> Tuple[threading.Thread, threading.Thread, List, List]:
        """
        Create background threads to read process stdout/stderr asynchronously.
        
        Issue #7 fix: Prevents pipe deadlocks when output exceeds pipe buffer (65KB).
        Reading in separate threads ensures pipes never block the main thread.
        
        Args:
            process: subprocess.Popen object with stdout/stderr pipes
        
        Returns:
            Tuple of (stdout_thread, stderr_thread, stdout_data, stderr_data)
            where data lists will contain the output strings once threads complete
        """
        stdout_data = []
        stderr_data = []
        
        def read_stdout():
            try:
                stdout_data.append(process.stdout.read())
            except Exception:
                stdout_data.append("")
        
        def read_stderr():
            try:
                stderr_data.append(process.stderr.read())
            except Exception:
                stderr_data.append("")
        
        stdout_thread = threading.Thread(target=read_stdout, daemon=True)
        stderr_thread = threading.Thread(target=read_stderr, daemon=True)
        
        return stdout_thread, stderr_thread, stdout_data, stderr_data
    
    @staticmethod
    def _wait_for_process_output(
        stdout_thread: threading.Thread,
        stderr_thread: threading.Thread,
        stdout_data: List,
        stderr_data: List,
        process,
        timeout_stdout: float = 30.0,
        timeout_stderr: float = 1.0
    ) -> Tuple[str, str]:
        """
        Wait for async output reader threads to complete and return results.
        
        Waits for both threads to finish reading, then waits for process to exit.
        Returns empty strings if threads timeout or data is unavailable.
        
        Args:
            stdout_thread: Thread reading stdout
            stderr_thread: Thread reading stderr
            stdout_data: List that will contain stdout string
            stderr_data: List that will contain stderr string
            process: Process to wait for
            timeout_stdout: Timeout for stdout thread (seconds)
            timeout_stderr: Timeout for stderr thread (seconds)
        
        Returns:
            Tuple of (stdout, stderr) strings
        """
        # Wait for output reading to complete
        stdout_thread.join(timeout=timeout_stdout)
        stderr_thread.join(timeout=timeout_stderr)
        
        # Wait for process to exit
        try:
            process.wait(timeout=1.0)
        except Exception:
            pass  # Process may still be running, that's ok
        
        # Extract results from data lists
        stdout = stdout_data[0] if stdout_data else ""
        stderr = stderr_data[0] if stderr_data else ""
        
        return stdout, stderr
