"""
ValidatorTestWorker - Specialized worker for 3-stage validation testing.

This worker implements the 3-stage validation process:
1. Generator → produces test input
2. Test solution → processes input to produce output
3. Validator → checks if test output is correct

Maintains exact signal signatures and behavior from the original inline implementation.
"""

import multiprocessing
import os
import subprocess
import tempfile
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any, Dict, Optional

import psutil
from PySide6.QtCore import QObject, Signal, Slot

# Import path helpers for nested I/O file organization
from src.app.shared.constants.paths import get_input_file_path, get_output_file_path
from src.app.shared.utils.workspace_utils import ensure_test_type_directory


class ValidatorTestWorker(QObject):
    """
    Specialized worker for validation testing with 3-stage execution.

    This class extracts and consolidates the ValidatorTestWorker functionality
    from validator_runner.py while maintaining exact signal compatibility.
    """

    # Exact signal signatures from original ValidatorTestWorker
    testStarted = Signal(int, int)  # current test, total tests
    testCompleted = Signal(
        int, bool, str, str, str, str, int, float, float
    )  # test number, passed, input, test_output, validation_message, error_details, validator_exit_code, time, memory
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
        Initialize the validator test worker.

        Args:
            workspace_dir: Directory containing test files and executables
            executables: Dictionary with 'generator', 'test', 'validator' executable paths (legacy)
            test_count: Number of tests to run
            max_workers: Maximum number of parallel workers (auto-detected if None)
            execution_commands: Dictionary with 'generator', 'test', 'validator' execution command lists
                              (e.g., ['python', 'gen.py'] or ['./test.exe']). If provided, overrides executables.
        """
        super().__init__()
        self.workspace_dir = workspace_dir
        self.executables = executables
        self.test_count = test_count
        self.is_running = True  # Flag to control the worker loop
        self.test_results = []  # Store detailed test results for database
        # Use reasonable default: CPU cores - 1, min 1, max 8 (to avoid overwhelming system)
        self.max_workers = max_workers or min(8, max(1, multiprocessing.cpu_count() - 1))
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
            output_data: The test solution output data
        """
        try:
            # Ensure nested directory structure exists
            ensure_test_type_directory(self.workspace_dir, "validator")

            # Get full paths for input and output files
            input_file = get_input_file_path(
                self.workspace_dir, "validator", f"input_{test_number}.txt"
            )
            output_file = get_output_file_path(
                self.workspace_dir, "validator", f"output_{test_number}.txt"
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
        """Run validation tests in parallel without blocking the main thread"""
        all_passed = True
        completed_tests = 0

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all test jobs
            future_to_test = {
                executor.submit(self._run_single_test, i): i for i in range(1, self.test_count + 1)
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
                            test_result["test_output"],
                            test_result["validation_message"],
                            test_result["error_details"],
                            test_result["validator_exit_code"],
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
                        "Execution Error",
                        str(e),
                        -3,
                        error_result["total_time"],
                        error_result["memory"],
                    )
                    all_passed = False

        self.allTestsCompleted.emit(all_passed)

    def _run_single_test(self, test_number: int) -> Optional[Dict[str, Any]]:
        """
        Run a single validation test with metrics tracking.

        This implements the 3-stage validation process:
        1. Generator → produces test input
        2. Test solution → processes input to produce output
        3. Validator → checks if test output is correct

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

            # Stage 1: Run generator with memory tracking
            generator_start = time.time()

            try:
                # Use numeric constant for CREATE_NO_WINDOW (0x08000000) to avoid
                # AttributeError on non-Windows platforms during testing
                generator_process = subprocess.Popen(
                    self.execution_commands["generator"],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    creationflags=0x08000000 if os.name == "nt" else 0,
                    text=True,
                )
            except Exception as e:
                return self._create_error_result(
                    test_number,
                    f"Failed to start generator: {e}",
                    "Generator failed",
                    -1,
                    0,
                    0,
                    0,
                    0,
                )

            # Track generator memory
            try:
                proc = psutil.Process(generator_process.pid)
                while generator_process.poll() is None:
                    mem_mb = proc.memory_info().rss / (1024 * 1024)
                    peak_memory_mb = max(peak_memory_mb, mem_mb)
                    time.sleep(0.01)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass

            generator_stdout, generator_stderr = generator_process.communicate(timeout=10)
            generator_time = time.time() - generator_start

            if generator_process.returncode != 0:
                error_msg = f"Generator failed: {generator_stderr}"
                return self._create_error_result(
                    test_number,
                    error_msg,
                    "Generator failed",
                    -1,
                    generator_time,
                    0,
                    0,
                    peak_memory_mb,
                )

            # Get generated input data
            input_text = generator_stdout

            # Stage 2: Run test solution with memory tracking
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

            # Get output - communicate() will handle closing stdin automatically
            test_stdout, test_stderr = test_process.communicate(timeout=30)
            test_time = time.time() - test_start

            if test_process.returncode != 0:
                error_msg = f"Test solution failed: {test_stderr}"
                return self._create_error_result(
                    test_number,
                    error_msg,
                    "Test solution failed",
                    -1,
                    generator_time,
                    test_time,
                    0,
                    peak_memory_mb,
                )

            # Get test output
            test_output = test_stdout

            # Stage 3: Run validator - use temporary files
            validator_start = time.time()

            # Create temporary files for validator
            with tempfile.NamedTemporaryFile(
                mode="w+", suffix=".txt", delete=False, dir=None, prefix="vld_in_"
            ) as input_temp:
                input_temp.write(input_text)
                input_temp.flush()
                os.fsync(input_temp.fileno())
                input_temp_path = input_temp.name

            with tempfile.NamedTemporaryFile(
                mode="w+", suffix=".txt", delete=False, dir=None, prefix="vld_out_"
            ) as output_temp:
                output_temp.write(test_output)
                output_temp.flush()
                os.fsync(output_temp.fileno())
                output_temp_path = output_temp.name

            try:
                # Build validator command with file arguments
                validator_command = self.execution_commands["validator"] + [
                    input_temp_path,
                    output_temp_path,
                ]

                # Use numeric constant for CREATE_NO_WINDOW (0x08000000) to avoid
                # AttributeError on non-Windows platforms during testing
                validator_process = subprocess.Popen(
                    validator_command,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    creationflags=0x08000000 if os.name == "nt" else 0,
                    text=True,
                )

                # Track validator memory
                try:
                    proc = psutil.Process(validator_process.pid)
                    while validator_process.poll() is None:
                        mem_mb = proc.memory_info().rss / (1024 * 1024)
                        peak_memory_mb = max(peak_memory_mb, mem_mb)
                        time.sleep(0.01)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass

                validator_stdout, validator_stderr = validator_process.communicate(timeout=10)
                validator_time = time.time() - validator_start
                validator_exit_code = validator_process.returncode

                # Interpret validator exit code
                if validator_exit_code == 0:
                    # Validation passed
                    validation_message = "Correct"
                    error_details = ""
                    passed = True
                elif validator_exit_code == 1:
                    # Validation failed - wrong answer
                    validation_message = "Wrong Answer"
                    error_details = (
                        validator_stdout or validator_stderr or "Output doesn't match expected"
                    )
                    passed = False
                elif validator_exit_code == 2:
                    # Validation failed - presentation error
                    validation_message = "Presentation Error"
                    error_details = (
                        validator_stdout or validator_stderr or "Output format is incorrect"
                    )
                    passed = False
                else:
                    # Validator error
                    validation_message = "Validator Error"
                    error_details = f"Validator crashed with exit code {validator_exit_code}: {validator_stderr}"
                    passed = False

                # Save I/O files to nested directories
                self._save_test_io(test_number, input_text, test_output)

                # Calculate total time
                total_time = generator_time + test_time + validator_time

                # Create successful test result with metrics
                return {
                    "test_number": test_number,
                    "passed": passed,
                    "input": input_text.strip()[:500]
                    + ("..." if len(input_text.strip()) > 500 else ""),
                    "test_output": test_output.strip()[:500]
                    + ("..." if len(test_output.strip()) > 500 else ""),
                    "validation_message": validation_message,
                    "error_details": error_details,
                    "validator_exit_code": validator_exit_code,
                    "generator_time": generator_time,
                    "test_time": test_time,
                    "validator_time": validator_time,
                    "total_time": total_time,
                    "memory": peak_memory_mb,  # Peak memory in MB
                }

            finally:
                # Clean up temporary files
                try:
                    os.unlink(input_temp_path)
                    os.unlink(output_temp_path)
                except OSError:
                    pass

        except subprocess.TimeoutExpired as e:
            error_msg = f"Timeout in {e.cmd[0] if e.cmd else 'unknown'} after {e.timeout}s"
            return self._create_error_result(
                test_number, error_msg, "Timeout", -2, peak_memory_mb=peak_memory_mb
            )
        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            return self._create_error_result(
                test_number,
                error_msg,
                "Execution Error",
                -3,
                peak_memory_mb=peak_memory_mb,
            )

    def _create_error_result(
        self,
        test_number: int,
        error_msg: str,
        validation_message: str = "Error",
        validator_exit_code: int = -1,
        generator_time: float = 0,
        test_time: float = 0,
        validator_time: float = 0,
        peak_memory_mb: float = 0.0,
    ) -> Dict[str, Any]:
        """Create a standardized error result dictionary."""
        return {
            "test_number": test_number,
            "passed": False,
            "input": "",
            "test_output": "",
            "validation_message": validation_message,
            "error_details": error_msg,
            "validator_exit_code": validator_exit_code,
            "generator_time": generator_time,
            "test_time": test_time,
            "validator_time": validator_time,
            "total_time": generator_time + test_time + validator_time,
            "memory": peak_memory_mb,
        }

    def stop(self):
        """Stop the worker and cancel any running tests."""
        self.is_running = False

    def get_test_results(self) -> list:
        """Get thread-safe copy of test results for database storage."""
        with self._results_lock:
            return self.test_results.copy()
