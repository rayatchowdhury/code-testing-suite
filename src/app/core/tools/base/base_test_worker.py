"""
BaseTestWorker - Consolidated parallel testing patterns for all tools.

This class consolidates the 400+ lines of duplicated worker patterns
from ValidatorTestWorker, BenchmarkTestWorker, and ComparisonTestWorker into a
single reusable base class with consistent parallel execution and error handling.
"""

import threading
import multiprocessing
from typing import Dict, Any, Optional, List
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from PySide6.QtCore import QObject, Signal, Slot
import logging

logger = logging.getLogger(__name__)


class BaseTestWorker(QObject):
    """
    Base worker class for parallel test execution.

    This class consolidates the common parallel testing patterns that were
    duplicated across ValidatorTestWorker, BenchmarkTestWorker, and ComparisonTestWorker,
    providing:
    - Parallel test execution with optimal worker count
    - Thread-safe result storage and signal emission
    - Consistent error handling and recovery
    - Template method pattern for test-specific logic
    - Progress tracking and cancellation support
    """

    # Common signals for all test workers
    testStarted = Signal(int, int)  # current test, total tests
    testCompleted = Signal(object)  # test result (flexible for different result types)
    allTestsCompleted = Signal(bool)  # True if all passed
    progressUpdated = Signal(str)  # Progress message

    def __init__(
        self,
        workspace_dir: str,
        executables: Dict[str, str],
        test_count: int,
        max_workers: Optional[int] = None,
    ):
        """
        Initialize the base test worker.

        Args:
            workspace_dir: Directory containing test files and executables
            executables: Dictionary mapping executable names to paths
            test_count: Number of tests to run
            max_workers: Maximum number of parallel workers (auto-detected if None)
        """
        super().__init__()
        self.workspace_dir = workspace_dir
        self.executables = executables
        self.test_count = test_count
        self.is_running = True
        self.test_results: List[Dict[str, Any]] = []

        # Calculate optimal worker count (can be customized by subclasses)
        self.max_workers = max_workers or self._calculate_optimal_workers()

        # Thread-safe result storage
        self._results_lock = threading.Lock()

        logger.debug(
            f"Initialized BaseTestWorker with {self.max_workers} workers for {test_count} tests"
        )

    def _calculate_optimal_workers(self) -> int:
        """
        Calculate optimal number of worker threads.

        Can be overridden by subclasses for specific optimization strategies.

        Returns:
            int: Optimal number of workers
        """
        # Conservative default: use CPU count - 1, min 1, max 8
        return min(8, max(1, multiprocessing.cpu_count() - 1))

    @Slot()
    def run_tests(self) -> None:
        """
        Run all tests in parallel using the template method pattern.

        This method consolidates the common parallel execution logic
        while allowing subclasses to customize individual test execution.
        """
        all_passed = True
        completed_tests = 0

        self.progressUpdated.emit(
            f"Starting {self.test_count} tests with {self.max_workers} workers..."
        )

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all test jobs
            future_to_test = {
                executor.submit(self._run_single_test_safe, i): i
                for i in range(1, self.test_count + 1)
            }

            # Process completed tests as they finish
            for future in as_completed(future_to_test):
                if not self.is_running:
                    # Cancel remaining futures if stopped
                    for f in future_to_test:
                        f.cancel()
                    break

                test_number = future_to_test[future]
                completed_tests += 1

                try:
                    test_result = future.result()
                    if test_result:  # Check if test wasn't cancelled
                        # Thread-safe result storage
                        with self._results_lock:
                            self.test_results.append(test_result)

                        # Emit progress signals
                        self.testStarted.emit(completed_tests, self.test_count)
                        self.testCompleted.emit(test_result)

                        # Update progress
                        self.progressUpdated.emit(
                            f"Completed test {completed_tests}/{self.test_count}"
                        )

                        # Check if test passed (result structure may vary by subclass)
                        if not self._test_passed(test_result):
                            all_passed = False
                            # Some test types stop on first failure
                            if self._should_stop_on_failure():
                                break

                except Exception as e:
                    # Handle any unexpected errors
                    error_result = self._create_error_result(
                        test_number, f"Execution error: {str(e)}"
                    )
                    with self._results_lock:
                        self.test_results.append(error_result)

                    self.testCompleted.emit(error_result)
                    all_passed = False

                    if self._should_stop_on_failure():
                        break

        self.progressUpdated.emit(f"Completed all tests. Passed: {all_passed}")
        self.allTestsCompleted.emit(all_passed)

    def _run_single_test_safe(self, test_number: int) -> Optional[Dict[str, Any]]:
        """
        Safely run a single test with error handling.

        Args:
            test_number: Test number to run

        Returns:
            Optional[Dict[str, Any]]: Test result or None if cancelled
        """
        if not self.is_running:
            return None

        try:
            return self._run_single_test(test_number)
        except Exception as e:
            logger.error(f"Error in test {test_number}: {e}")
            return self._create_error_result(test_number, str(e))

    def _run_single_test(self, test_number: int) -> Dict[str, Any]:
        """
        Run a single test - ABSTRACT METHOD to be implemented by subclasses.

        This is the template method that subclasses must implement to define
        their specific test execution logic.

        Args:
            test_number: Test number to run

        Returns:
            Dict[str, Any]: Test result with test-specific structure
        """
        raise NotImplementedError("Subclasses must implement _run_single_test()")

    def _test_passed(self, test_result: Dict[str, Any]) -> bool:
        """
        Determine if a test passed based on its result.

        Can be overridden by subclasses for different pass/fail criteria.

        Args:
            test_result: Result from _run_single_test()

        Returns:
            bool: True if test passed, False otherwise
        """
        return test_result.get("passed", False)

    def _should_stop_on_failure(self) -> bool:
        """
        Determine whether to stop testing on first failure.

        Can be overridden by subclasses. For example:
        - Stress testing: Stop on first failure
        - Validation testing: Continue to find all failures
        - TLE testing: Continue to measure all performance

        Returns:
            bool: True to stop on first failure, False to continue
        """
        return False  # Default: continue testing

    def _create_error_result(self, test_number: int, error_msg: str) -> Dict[str, Any]:
        """
        Create a standardized error result.

        Can be extended by subclasses to include test-specific error information.

        Args:
            test_number: Test that failed
            error_msg: Error message

        Returns:
            Dict[str, Any]: Standardized error result
        """
        return {
            "test_number": test_number,
            "passed": False,
            "error_details": error_msg,
            "timestamp": datetime.now().isoformat(),
            "error_type": "execution_error",
        }

    def get_results(self) -> List[Dict[str, Any]]:
        """
        Get all test results in a thread-safe manner.

        Returns:
            List[Dict[str, Any]]: List of all test results
        """
        with self._results_lock:
            return self.test_results.copy()

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get test execution statistics.

        Returns:
            Dict[str, Any]: Statistics including pass/fail counts, timing, etc.
        """
        with self._results_lock:
            if not self.test_results:
                return {
                    "total_tests": 0,
                    "passed_tests": 0,
                    "failed_tests": 0,
                    "pass_rate": 0.0,
                }

            passed_tests = sum(
                1 for result in self.test_results if self._test_passed(result)
            )
            failed_tests = len(self.test_results) - passed_tests

            # Calculate timing statistics if available
            execution_times = []
            for result in self.test_results:
                if "execution_time" in result:
                    execution_times.append(result["execution_time"])

            stats = {
                "total_tests": len(self.test_results),
                "passed_tests": passed_tests,
                "failed_tests": failed_tests,
                "pass_rate": (
                    (passed_tests / len(self.test_results)) * 100
                    if self.test_results
                    else 0.0
                ),
            }

            if execution_times:
                stats.update(
                    {
                        "avg_execution_time": sum(execution_times)
                        / len(execution_times),
                        "min_execution_time": min(execution_times),
                        "max_execution_time": max(execution_times),
                        "total_execution_time": sum(execution_times),
                    }
                )

            return stats

    def stop(self) -> None:
        """Stop the worker and cancel any running tests."""
        self.is_running = False
        self.progressUpdated.emit("Stopping tests...")
        logger.debug("BaseTestWorker stopped")

    def __del__(self):
        """Ensure cleanup on destruction."""
        try:
            self.stop()
        except RuntimeError:
            # Skip cleanup if Qt Signal objects are already deleted
            pass
