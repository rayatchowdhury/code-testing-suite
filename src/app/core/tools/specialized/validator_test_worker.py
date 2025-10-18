"""
ValidatorTestWorker - Specialized worker for 3-stage validation testing.

This worker implements the 3-stage validation process:
1. Generator → produces test input
2. Test solution → processes input to produce output
3. Validator → checks if test output is correct

Maintains exact signal signatures and behavior from the original inline implementation.
"""

import os
import subprocess
import tempfile
import time
from typing import Any, Dict, Optional

import psutil
from PySide6.QtCore import Signal

# Import base worker with shared functionality
from src.app.core.tools.specialized.base_test_worker import BaseTestWorker


class ValidatorTestWorker(BaseTestWorker):
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
        # Call base class initialization - handles common setup
        super().__init__(
            workspace_dir=workspace_dir,
            executables=executables,
            test_count=test_count,
            max_workers=max_workers,
            execution_commands=execution_commands
        )
    
    def _calculate_optimal_workers(self) -> int:
        """
        Override: Use default max workers (8) for validator testing.
        
        Validator tests run 3 processes per test (generator, test, validator),
        so we use the default maximum of 8 workers.
        
        Returns:
            Optimal worker count for validator testing (minimum 1, maximum 8)
        """
        import multiprocessing
        return min(8, max(1, multiprocessing.cpu_count() - 1))

    def _emit_test_completed(self, test_result: Dict[str, Any]) -> None:
        """
        Emit the testCompleted signal with validator-specific parameters.
        
        Required by BaseTestWorker to handle specialized signal emission.
        
        Args:
            test_result: Dictionary containing test result data
        """
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

            # Issue #7: Read output in thread to prevent pipe deadlock
            # Generator produces output with no input, so we must read concurrently
            stdout_data = []
            stderr_data = []
            
            def read_stdout():
                stdout_data.append(generator_process.stdout.read())
            
            def read_stderr():
                stderr_data.append(generator_process.stderr.read())
            
            import threading
            stdout_thread = threading.Thread(target=read_stdout, daemon=True)
            stderr_thread = threading.Thread(target=read_stderr, daemon=True)
            stdout_thread.start()
            stderr_thread.start()

            # Track generator memory while output is being read in background
            try:
                proc = psutil.Process(generator_process.pid)
                while generator_process.poll() is None and self.is_running:  # Issue #7
                    mem_mb = proc.memory_info().rss / (1024 * 1024)
                    peak_memory_mb = max(peak_memory_mb, mem_mb)
                    time.sleep(0.01)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass

            # Issue #7: If stopped, kill process and return None
            if not self.is_running:
                try:
                    generator_process.kill()
                    generator_process.wait(timeout=1)
                except:
                    pass
                return None

            # Wait for output reading threads to complete
            stdout_thread.join(timeout=10)
            stderr_thread.join(timeout=1)
            generator_process.wait(timeout=1)
            
            generator_stdout = stdout_data[0] if stdout_data else ""
            generator_stderr = stderr_data[0] if stderr_data else ""
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
            test_process.stdin.close()  # Issue #7: Close stdin to signal EOF

            # Issue #7: Read output in thread to prevent pipe deadlock
            test_stdout_data = []
            test_stderr_data = []
            
            def read_test_stdout():
                test_stdout_data.append(test_process.stdout.read())
            
            def read_test_stderr():
                test_stderr_data.append(test_process.stderr.read())
            
            test_stdout_thread = threading.Thread(target=read_test_stdout, daemon=True)
            test_stderr_thread = threading.Thread(target=read_test_stderr, daemon=True)
            test_stdout_thread.start()
            test_stderr_thread.start()

            # Track test solution memory while output is being read in background
            try:
                proc = psutil.Process(test_process.pid)
                while test_process.poll() is None and self.is_running:  # Issue #7
                    mem_mb = proc.memory_info().rss / (1024 * 1024)
                    peak_memory_mb = max(peak_memory_mb, mem_mb)
                    time.sleep(0.01)
                    
                    # TIMEOUT CHECK: Kill process if running too long (30s default)
                    if time.time() - test_start > 30.0:
                        test_process.kill()
                        test_process.wait()
                        return self._create_error_result(
                            test_number,
                            "Test solution timeout (>30s)",
                            "Timeout",
                            -1,
                            generator_time,
                            30.0,
                            0,
                            peak_memory_mb,
                        )
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass

            # Issue #7: If stopped, kill process and return None
            if not self.is_running:
                try:
                    test_process.kill()
                    test_process.wait(timeout=1)
                except:
                    pass
                return None

            # Wait for output reading threads to complete
            test_stdout_thread.join(timeout=30)
            test_stderr_thread.join(timeout=1)
            test_process.wait(timeout=1)
            
            test_stdout = test_stdout_data[0] if test_stdout_data else ""
            test_stderr = test_stderr_data[0] if test_stderr_data else ""
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
                    while validator_process.poll() is None and self.is_running:  # Issue #7
                        mem_mb = proc.memory_info().rss / (1024 * 1024)
                        peak_memory_mb = max(peak_memory_mb, mem_mb)
                        time.sleep(0.01)
                        
                        # TIMEOUT CHECK: Kill process if running too long (10s default for validator)
                        if time.time() - validator_start > 10.0:
                            validator_process.kill()
                            validator_process.wait()
                            return self._create_error_result(
                                test_number,
                                "Validator timeout (>10s)",
                                "Timeout",
                                -1,
                                generator_time,
                                test_time,
                                10.0,
                                peak_memory_mb,
                            )
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass

                # Issue #7: If stopped, kill process and return None
                if not self.is_running:
                    try:
                        validator_process.kill()
                        validator_process.wait(timeout=1)
                    except:
                        pass
                    return None

                validator_stdout, validator_stderr = validator_process.communicate(
                    timeout=10
                )
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
                        validator_stdout
                        or validator_stderr
                        or "Output doesn't match expected"
                    )
                    passed = False
                elif validator_exit_code == 2:
                    # Validation failed - presentation error
                    validation_message = "Presentation Error"
                    error_details = (
                        validator_stdout
                        or validator_stderr
                        or "Output format is incorrect"
                    )
                    passed = False
                else:
                    # Validator error
                    validation_message = "Validator Error"
                    error_details = f"Validator crashed with exit code {validator_exit_code}: {validator_stderr}"
                    passed = False

                # Issue #6: REMOVED synchronous disk I/O during test execution
                # Data is already stored in memory dictionary and database
                # self._save_test_io(test_number, input_text, test_output)

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
            error_msg = (
                f"Timeout in {e.cmd[0] if e.cmd else 'unknown'} after {e.timeout}s"
            )
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
