"""
ComparisonTestWorker - Specialized worker for 3-stage comparison testing with output comparison.

This worker implements the 3-stage comparison testing process:
1. Generator → produces test input
2. Test solution → processes input to produce output
3. Correct solution → processes same input to produce expected output
4. Compare outputs for correctness

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
from src.app.shared.constants.paths import get_input_file_path, get_output_file_path
from src.app.shared.utils.workspace_utils import ensure_test_type_directory


class ComparisonTestWorker(QObject):
    """
    Specialized worker for comparison testing with output comparison.

    This class extracts and consolidates the ComparisonTestWorker functionality
    from comparator.py while maintaining exact signal compatibility.
    """

    # Exact signal signatures from original ComparisonTestWorker
    testStarted = Signal(int, int)  # current test, total tests
    testCompleted = Signal(
        int, bool, str, str, str, float, float
    )  # test number, passed, input, correct output, test output, time, memory
    allTestsCompleted = Signal(bool)  # True if all passed

    def __init__(
        self,
        workspace_dir: str,
        executables: Dict[str, str],
        test_count: int,
        max_workers: Optional[int] = None,
        execution_commands: Optional[Dict[str, list]] = None,
    ):
        """
        Initialize the comparison test worker.

        Args:
            workspace_dir: Directory containing test files and executables
            executables: Dictionary with 'generator', 'test', 'correct' executable paths (legacy)
            test_count: Number of tests to run
            max_workers: Maximum number of parallel workers (auto-detected if None)
            execution_commands: Dictionary with 'generator', 'test', 'correct' execution command lists
                              (e.g., ['python', 'gen.py'] or ['./test.exe']). If provided, overrides executables.
        """
        super().__init__()
        self.workspace_dir = workspace_dir
        self.executables = executables
        self.test_count = test_count
        self.is_running = True  # Flag to control the worker loop
        self.test_results = []  # Store detailed test results for database
        # Use reasonable default: CPU cores - 1, min 1, max 6 (comparison testing can be I/O intensive)
        self.max_workers = max_workers or min(6, max(1, multiprocessing.cpu_count() - 1))
        self._results_lock = threading.Lock()  # Thread-safe results access

        # Multi-language support: use execution commands if provided, otherwise fall back to executable paths
        if execution_commands:
            self.execution_commands = execution_commands
        else:
            # Legacy mode: convert executable paths to command lists
            self.execution_commands = {k: [v] for k, v in executables.items()}

    def _save_test_io(
        self, test_number: int, input_data: str, test_output: str, correct_output: str
    ):
        """
        Save test input and outputs to nested directories.

        Args:
            test_number: The test number
            input_data: The generated input data
            test_output: The test solution output
            correct_output: The correct solution output
        """
        try:
            # Ensure nested directory structure exists
            ensure_test_type_directory(self.workspace_dir, "comparator")

            # Get full paths for input and output files
            input_file = get_input_file_path(
                self.workspace_dir, "comparator", f"input_{test_number}.txt"
            )
            test_output_file = get_output_file_path(
                self.workspace_dir, "comparator", f"output_{test_number}.txt"
            )
            correct_output_file = get_output_file_path(
                self.workspace_dir, "comparator", f"correct_output_{test_number}.txt"
            )

            # Save input file
            with open(input_file, "w", encoding="utf-8") as f:
                f.write(input_data)

            # Save test output file
            with open(test_output_file, "w", encoding="utf-8") as f:
                f.write(test_output)

            # Save correct output file
            with open(correct_output_file, "w", encoding="utf-8") as f:
                f.write(correct_output)

        except Exception as e:
            # Don't fail the test if file saving fails, just log the error
            print(f"Warning: Failed to save I/O files for test {test_number}: {e}")

    @Slot()
    def run_tests(self):
        """Run comparison tests in parallel with optimized I/O"""
        all_passed = True
        completed_tests = 0

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all test jobs
            future_to_test = {
                executor.submit(self._run_single_comparison_test, i): i
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

                        # Emit signals for UI updates with time and memory metrics
                        self.testStarted.emit(completed_tests, self.test_count)
                        self.testCompleted.emit(
                            test_result["test_number"],
                            test_result["passed"],
                            test_result["input"],
                            test_result["correct_output"],
                            test_result["test_output"],
                            test_result["total_time"],  # Total execution time
                            test_result["memory"],  # Peak memory usage in MB
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
                        error_result["test_number"],
                        False,
                        "",
                        "",
                        error_result["error_details"],
                        error_result["total_time"],
                        error_result["memory"],
                    )
                    all_passed = False

        self.allTestsCompleted.emit(all_passed)

    def _run_single_comparison_test(self, test_number: int) -> Optional[Dict[str, Any]]:
        """
        Run a single comparison test with output comparison and metrics tracking.

        This implements the 3-stage stress testing process:
        1. Generator → produces test input
        2. Test solution → processes input to produce output
        3. Correct solution → processes input to produce expected output
        4. Compare outputs for correctness

        Tracks execution time and peak memory usage for each stage.

        Args:
            test_number: The test number to run

        Returns:
            Dictionary with test result details, or None if cancelled
        """
        if not self.is_running:
            return None

        try:
            peak_memory_mb = 0.0

            # Stage 1: Generate test input
            generator_start = time.time()

            # Use numeric constant for CREATE_NO_WINDOW (0x08000000) to avoid
            # AttributeError on non-Windows platforms during testing
            generator_process = subprocess.Popen(
                self.execution_commands["generator"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                creationflags=0x08000000 if os.name == "nt" else 0,
                text=True,
            )

            # Track generator memory
            try:
                proc = psutil.Process(generator_process.pid)
                while generator_process.poll() is None:
                    mem_mb = proc.memory_info().rss / (1024 * 1024)
                    peak_memory_mb = max(peak_memory_mb, mem_mb)
                    time.sleep(0.01)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass  # Process finished or can't access

            generator_stdout, generator_stderr = generator_process.communicate(timeout=10)
            generator_time = time.time() - generator_start

            if generator_process.returncode != 0:
                error_msg = f"Generator failed: {generator_stderr}"
                return self._create_error_result(
                    test_number,
                    error_msg,
                    generator_time,
                    peak_memory_mb=peak_memory_mb,
                )

            # Get generated input
            input_text = generator_stdout

            # Stage 2: Run test solution
            test_start = time.time()

            # Use numeric constant for CREATE_NO_WINDOW (0x08000000) to avoid
            # AttributeError on non-Windows platforms during testing
            test_process = subprocess.Popen(
                self.execution_commands["test"],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                creationflags=0x08000000 if os.name == "nt" else 0,
                text=True,
            )

            # Write input to process (non-blocking)
            if input_text:
                test_process.stdin.write(input_text)
                test_process.stdin.flush()

            # Track test solution memory
            try:
                proc = psutil.Process(test_process.pid)
                while test_process.poll() is None:
                    mem_mb = proc.memory_info().rss / (1024 * 1024)
                    peak_memory_mb = max(peak_memory_mb, mem_mb)
                    time.sleep(0.01)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass

            # Get output - close stdin safely before communicate
            try:
                if test_process.stdin:
                    test_process.stdin.close()
            except Exception:
                pass  # Ignore if already closed

            test_stdout, test_stderr = test_process.communicate(timeout=30)
            test_time = time.time() - test_start

            if test_process.returncode != 0:
                error_msg = f"Test solution failed: {test_stderr}"
                return self._create_error_result(
                    test_number,
                    error_msg,
                    generator_time,
                    test_time,
                    peak_memory_mb=peak_memory_mb,
                )

            # Get test output
            test_output = test_stdout

            # Stage 3: Run correct solution
            correct_start = time.time()

            # Use numeric constant for CREATE_NO_WINDOW (0x08000000) to avoid
            # AttributeError on non-Windows platforms during testing
            correct_process = subprocess.Popen(
                self.execution_commands["correct"],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                creationflags=0x08000000 if os.name == "nt" else 0,
                text=True,
            )

            # Write input to process (non-blocking)
            if input_text:
                correct_process.stdin.write(input_text)
                correct_process.stdin.flush()

            # Track correct solution memory
            try:
                proc = psutil.Process(correct_process.pid)
                while correct_process.poll() is None:
                    mem_mb = proc.memory_info().rss / (1024 * 1024)
                    peak_memory_mb = max(peak_memory_mb, mem_mb)
                    time.sleep(0.01)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass

            # Get output - close stdin safely before communicate
            try:
                if correct_process.stdin:
                    correct_process.stdin.close()
            except Exception:
                pass  # Ignore if already closed

            correct_stdout, correct_stderr = correct_process.communicate(timeout=30)
            correct_time = time.time() - correct_start

            if correct_process.returncode != 0:
                error_msg = f"Correct solution failed: {correct_stderr}"
                return self._create_error_result(
                    test_number,
                    error_msg,
                    generator_time,
                    test_time,
                    correct_time,
                    peak_memory_mb,
                )

            # Get correct output
            correct_output = correct_stdout

            # Stage 4: Compare outputs
            comparison_start = time.time()

            # Normalize outputs for comparison (strip whitespace)
            test_output_normalized = test_output.strip()
            correct_output_normalized = correct_output.strip()

            # Check if outputs match
            outputs_match = test_output_normalized == correct_output_normalized

            comparison_time = time.time() - comparison_start

            # Save I/O files to nested directories
            self._save_test_io(test_number, input_text, test_output, correct_output)

            # Calculate total time
            total_time = generator_time + test_time + correct_time + comparison_time

            # Create result with metrics
            return {
                "test_number": test_number,
                "passed": outputs_match,
                "input": input_text.strip()[:300]
                + ("..." if len(input_text.strip()) > 300 else ""),  # Truncate for display
                "test_output": test_output.strip()[:300]
                + ("..." if len(test_output.strip()) > 300 else ""),  # Truncate for display
                "correct_output": correct_output.strip()[:300]
                + ("..." if len(correct_output.strip()) > 300 else ""),  # Truncate for display
                "generator_time": generator_time,
                "test_time": test_time,
                "correct_time": correct_time,
                "comparison_time": comparison_time,
                "total_time": total_time,
                "memory": peak_memory_mb,  # Peak memory in MB
                "error_details": "" if outputs_match else "Output mismatch",
                "test_output_full": test_output,  # Full output for database
                "correct_output_full": correct_output,  # Full output for database
                "input_full": input_text,  # Full input for database
            }

        except subprocess.TimeoutExpired as e:
            error_msg = f"Timeout in {e.cmd[0] if e.cmd else 'unknown'} after {e.timeout}s"
            return self._create_error_result(test_number, error_msg, peak_memory_mb=peak_memory_mb)
        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            return self._create_error_result(test_number, error_msg, peak_memory_mb=peak_memory_mb)

    def _create_error_result(
        self,
        test_number: int,
        error_msg: str,
        generator_time: float = 0.0,
        test_time: float = 0.0,
        correct_time: float = 0.0,
        peak_memory_mb: float = 0.0,
    ) -> Dict[str, Any]:
        """Create a standardized error result dictionary."""
        return {
            "test_number": test_number,
            "passed": False,
            "input": "",
            "test_output": "",
            "correct_output": "",
            "generator_time": generator_time,
            "test_time": test_time,
            "correct_time": correct_time,
            "comparison_time": 0.0,
            "total_time": generator_time + test_time + correct_time,
            "memory": peak_memory_mb,
            "error_details": error_msg,
            "test_output_full": "",
            "correct_output_full": "",
            "input_full": "",
        }

    def stop(self):
        """Stop the worker and cancel any running tests."""
        self.is_running = False

    def get_test_results(self) -> list:
        """Get thread-safe copy of test results for database storage."""
        with self._results_lock:
            return self.test_results.copy()
