"""
BenchmarkTestWorker - Specialized worker for benchmarking and performance monitoring.

This worker implements the 2-stage benchmark testing process:
1. Generator → produces test input
2. Test solution → processes input while monitoring time and memory usage

Maintains exact signal signatures and behavior from the original inline implementation.
"""

import multiprocessing
import os
import subprocess
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any, Dict, Optional

import psutil
from PySide6.QtCore import QObject, Signal, Slot

# Import path helpers for nested I/O file organization
from src.app.shared.constants.paths import (
    get_input_file_path,
    get_inputs_dir,
    get_output_file_path,
    get_outputs_dir,
)
from src.app.shared.utils.workspace_utils import ensure_test_type_directory


class BenchmarkTestWorker(QObject):
    """
    Specialized worker for benchmarking with performance monitoring.

    This class extracts and consolidates the BenchmarkTestWorker functionality
    from benchmarker.py while maintaining exact signal compatibility.
    """

    # Updated signal signatures to include input/output data
    testStarted = Signal(int, int)  # current test, total tests
    testCompleted = Signal(
        str, int, bool, float, float, bool, str, str, int
    )  # test name, test number, passed, execution time, memory used, memory passed, input_data, output_data, test_size
    allTestsCompleted = Signal(bool)  # True if all passed

    def __init__(
        self,
        workspace_dir: str,
        executables: Dict[str, str],
        time_limit: float,
        memory_limit: int,
        test_count: int = 1,
        max_workers: Optional[int] = None,
        execution_commands: Optional[Dict[str, list]] = None,
    ):
        """
        Initialize the TLE test worker.

        Args:
            workspace_dir: Directory containing test files and executables
            executables: Dictionary with 'generator' and 'test' executable paths (legacy)
            time_limit: Time limit in milliseconds
            memory_limit: Memory limit in MB
            test_count: Number of tests to run
            max_workers: Maximum number of parallel workers (auto-detected if None)
            execution_commands: Dictionary with 'generator' and 'test' execution command lists
                              (e.g., ['python', 'gen.py'] or ['./test.exe']). If provided, overrides executables.
        """
        super().__init__()
        self.workspace_dir = workspace_dir
        self.executables = executables
        self.time_limit = time_limit / 1000.0  # Convert ms to seconds
        self.memory_limit = memory_limit  # MB
        self.test_count = test_count
        self.is_running = True
        self.test_results = []  # Store detailed test results
        # Use reasonable default for benchmarking (less workers due to memory monitoring overhead)
        self.max_workers = max_workers or min(
            4, max(1, multiprocessing.cpu_count() - 1)
        )
        self._results_lock = threading.Lock()  # Thread-safe results access

        # Multi-language support: use execution commands if provided, otherwise fall back to executable paths
        if execution_commands:
            self.execution_commands = execution_commands
        else:
            # Legacy mode: convert executable paths to command lists
            self.execution_commands = {k: [v] for k, v in executables.items()}

    def _save_test_io(self, test_number: int, input_data: str, output_data: str):
        """
        Save test input and output to nested directories.

        Args:
            test_number: The test number
            input_data: The generated input data
            output_data: The test output data
        """
        try:
            # Ensure nested directory structure exists
            ensure_test_type_directory(self.workspace_dir, "benchmarker")

            # Get full paths for input and output files
            input_file = get_input_file_path(
                self.workspace_dir, "benchmarker", f"input_{test_number}.txt"
            )
            output_file = get_output_file_path(
                self.workspace_dir, "benchmarker", f"output_{test_number}.txt"
            )

            # Save input file
            with open(input_file, "w", encoding="utf-8") as f:
                f.write(input_data)

            # Save output file
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(output_data)

        except Exception as e:
            # Don't fail the test if file saving fails, just log the error
            print(f"Warning: Failed to save I/O files for test {test_number}: {e}")

    @Slot()
    def run_tests(self):
        """Run TLE tests in parallel with memory and time monitoring"""
        all_passed = True
        completed_tests = 0

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all test jobs
            future_to_test = {
                executor.submit(self._run_single_benchmark_test, i): i
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

                        # Emit signals for UI updates
                        self.testStarted.emit(completed_tests, self.test_count)
                        self.testCompleted.emit(
                            test_result["test_name"],
                            test_result["test_number"],
                            test_result["passed"],
                            test_result["execution_time"],
                            test_result["memory_used"],
                            test_result["memory_passed"],
                            test_result.get("input", ""),
                            test_result.get("output", ""),
                            test_result.get("test_size", 0),
                        )

                        if not test_result["passed"]:
                            all_passed = False

                except Exception as e:
                    # Handle any unexpected errors
                    error_result = self._create_error_result(
                        test_number, f"Execution error: {str(e)}"
                    )
                    with self._results_lock:
                        self.test_results.append(error_result)
                    self.testCompleted.emit(
                        f"Test {completed_tests}",
                        error_result["test_number"],
                        False,
                        0.0,
                        0.0,
                        False,
                        "",
                        "",
                        0,
                    )
                    all_passed = False

        self.allTestsCompleted.emit(all_passed)

    def _run_single_benchmark_test(self, test_number: int) -> Optional[Dict[str, Any]]:
        """
        Run a single TLE test with memory and time monitoring.

        This implements the 2-stage TLE testing process:
        1. Generator → produces test input
        2. Test solution → processes input while monitoring performance

        Args:
            test_number: The test number to run

        Returns:
            Dictionary with test result details, or None if cancelled
        """
        if not self.is_running:
            return None

        try:
            # Stage 1: Generate test input
            generator_start = time.time()

            # Use numeric constant for CREATE_NO_WINDOW (0x08000000) to avoid
            # AttributeError on non-Windows platforms during testing
            generator_result = subprocess.run(
                self.execution_commands["generator"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                creationflags=0x08000000 if os.name == "nt" else 0,
                timeout=10,
                text=True,
            )

            generator_time = time.time() - generator_start

            if generator_result.returncode != 0:
                error_msg = f"Generator failed: {generator_result.stderr}"
                return self._create_error_result(test_number, error_msg)

            # Get generated input
            input_text = generator_result.stdout

            # Stage 2: Run test with performance monitoring
            test_start = time.time()

            # Start the test process
            # Use numeric constant for CREATE_NO_WINDOW (0x08000000) to avoid
            # AttributeError on non-Windows platforms during testing
            process = subprocess.Popen(
                self.execution_commands["test"],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                creationflags=0x08000000 if os.name == "nt" else 0,
                text=True,
            )

            # Monitor memory usage
            max_memory_used = 0
            memory_limit_exceeded = False

            try:
                # Get psutil process object for memory monitoring
                ps_process = psutil.Process(process.pid)

                # Write input to process (non-blocking)
                if input_text:
                    process.stdin.write(input_text)
                    process.stdin.flush()

                # Monitor memory usage while process runs
                while process.poll() is None:
                    try:
                        memory_info = ps_process.memory_info()
                        memory_used_mb = memory_info.rss / (1024 * 1024)  # Convert to MB
                        max_memory_used = max(max_memory_used, memory_used_mb)
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        # Process finished
                        break

                    # Small sleep to avoid busy-waiting
                    time.sleep(0.001)

                    # Check if time limit exceeded during monitoring
                    if time.time() - test_start > self.time_limit:
                        process.kill()
                        process.wait()
                        test_time = time.time() - test_start

                        # Calculate test size
                        test_size = (
                            len(input_text.strip().split("\n"))
                            if input_text.strip()
                            else 0
                        )

                        return {
                            "test_name": f"Test {test_number}",
                            "test_number": test_number,
                            "passed": False,
                            "execution_time": test_time,
                            "memory_used": max_memory_used,
                            "memory_passed": max_memory_used <= self.memory_limit,
                            "error_details": f"Time Limit Exceeded ({self.time_limit:.2f}s)",
                            "generator_time": generator_time,
                            "input": input_text,
                            "output": "",
                            "test_size": test_size,
                        }

                # Get final memory reading
                try:
                    memory_info = ps_process.memory_info()
                    memory_used_mb = memory_info.rss / (1024 * 1024)  # Convert to MB
                    max_memory_used = max(max_memory_used, memory_used_mb)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    # Process finished, use last known memory usage
                    pass

                # Close stdin and get output
                process.stdin.close()
                stdout, stderr = process.communicate(timeout=5)

            except (psutil.NoSuchProcess, psutil.AccessDenied, Exception) as e:
                # Handle any errors during memory monitoring
                # Process may have terminated unexpectedly
                try:
                    stdout, stderr = process.communicate(timeout=1)
                except subprocess.TimeoutExpired:
                    process.kill()
                    stdout, stderr = process.communicate()

            test_time = time.time() - test_start

            # Check if memory limit was exceeded
            memory_passed = max_memory_used <= self.memory_limit
            if not memory_passed:
                memory_limit_exceeded = True

            # Check process result
            if process.returncode != 0:
                error_msg = f"Test solution failed with exit code {process.returncode}: {stderr}"
                return self._create_error_result(
                    test_number, error_msg, test_time, max_memory_used
                )

            # Check if both time and memory limits were respected
            time_passed = test_time <= self.time_limit
            overall_passed = time_passed and memory_passed and process.returncode == 0

            # Save I/O files to nested directories
            self._save_test_io(test_number, input_text, stdout)

            # Calculate test size (number of input lines)
            test_size = len(input_text.strip().split("\n")) if input_text.strip() else 0

            return {
                "test_name": f"Test {test_number}",
                "test_number": test_number,
                "passed": overall_passed,
                "execution_time": test_time,
                "memory_used": max_memory_used,
                "memory_passed": memory_passed,
                "time_passed": time_passed,
                "error_details": self._get_error_details(
                    time_passed, memory_passed, process.returncode
                ),
                "generator_time": generator_time,
                "input": input_text,  # Store full input
                "output": stdout if stdout else "",  # Store full output
                "test_size": test_size,
            }

        except Exception as e:
            error_msg = f"Unexpected error in test {test_number}: {str(e)}"
            return self._create_error_result(test_number, error_msg)

    def _get_error_details(
        self, time_passed: bool, memory_passed: bool, exit_code: int
    ) -> str:
        """Generate appropriate error details based on test results."""
        if exit_code != 0:
            return f"Runtime Error (exit code {exit_code})"
        elif not time_passed and not memory_passed:
            return f"Time Limit Exceeded ({self.time_limit:.2f}s) & Memory Limit Exceeded ({self.memory_limit}MB)"
        elif not time_passed:
            return f"Time Limit Exceeded ({self.time_limit:.2f}s)"
        elif not memory_passed:
            return f"Memory Limit Exceeded ({self.memory_limit}MB)"
        else:
            return "Accepted"

    def _create_error_result(
        self,
        test_number: int,
        error_msg: str,
        execution_time: float = 0.0,
        memory_used: float = 0.0,
    ) -> Dict[str, Any]:
        """Create a standardized error result dictionary."""
        return {
            "test_name": f"Test {test_number}",
            "test_number": test_number,
            "passed": False,
            "execution_time": execution_time,
            "memory_used": memory_used,
            "memory_passed": memory_used <= self.memory_limit,
            "time_passed": execution_time <= self.time_limit,
            "error_details": error_msg,
            "generator_time": 0.0,
            "input": "",
            "output": "",
            "test_size": 0,
        }

    def stop(self):
        """Stop the worker and cancel any running tests."""
        self.is_running = False

    def get_test_results(self) -> list:
        """Get thread-safe copy of test results for database storage."""
        with self._results_lock:
            return self.test_results.copy()
