"""
ComparisonTestWorker - Specialized worker for 3-stage comparison testing with output comparison.

This worker implements the 3-stage comparison testing process:
1. Generator → produces test input
2. Test solution → processes input to produce output
3. Correct solution → processes same input to produce expected output
4. Compare outputs for correctness

Maintains exact signal signatures and behavior from the original inline implementation.
"""

import os
import subprocess
import time
from typing import Any, Dict, Optional

import psutil
from PySide6.QtCore import Signal

# Import base worker with shared functionality
from src.app.core.tools.specialized.base_test_worker import BaseTestWorker


class ComparisonTestWorker(BaseTestWorker):
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
        Override: Use more workers for comparison testing (6 vs 8).
        
        Comparison tests are I/O intensive (running 3 processes per test),
        so we use 6 workers as a balance between parallelism and system load.
        
        Returns:
            Optimal worker count for comparison testing (minimum 1, maximum 6)
        """
        import multiprocessing
        return min(6, max(1, multiprocessing.cpu_count() - 1))

    def _emit_test_completed(self, test_result: Dict[str, Any]) -> None:
        """
        Emit the testCompleted signal with comparison-specific parameters.
        
        Required by BaseTestWorker to handle specialized signal emission.
        
        Args:
            test_result: Dictionary containing test result data
        """
        self.testCompleted.emit(
            test_result["test_number"],
            test_result["passed"],
            test_result["input"],
            test_result["correct_output"],
            test_result["test_output"],
            test_result["total_time"],  # Total execution time
            test_result["memory"],  # Peak memory usage in MB
        )

    def _run_single_test(self, test_number: int) -> Optional[Dict[str, Any]]:
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
                pass  # Process finished or can't access

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
                            generator_time,
                            30.0,
                            peak_memory_mb=peak_memory_mb,
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
            correct_process.stdin.close()  # Issue #7: Close stdin to signal EOF

            # Issue #7: Read output in thread to prevent pipe deadlock
            correct_stdout_data = []
            correct_stderr_data = []
            
            def read_correct_stdout():
                correct_stdout_data.append(correct_process.stdout.read())
            
            def read_correct_stderr():
                correct_stderr_data.append(correct_process.stderr.read())
            
            correct_stdout_thread = threading.Thread(target=read_correct_stdout, daemon=True)
            correct_stderr_thread = threading.Thread(target=read_correct_stderr, daemon=True)
            correct_stdout_thread.start()
            correct_stderr_thread.start()

            # Track correct solution memory while output is being read in background
            try:
                proc = psutil.Process(correct_process.pid)
                while correct_process.poll() is None and self.is_running:  # Issue #7
                    mem_mb = proc.memory_info().rss / (1024 * 1024)
                    peak_memory_mb = max(peak_memory_mb, mem_mb)
                    time.sleep(0.01)
                    
                    # TIMEOUT CHECK: Kill process if running too long (30s default)
                    if time.time() - correct_start > 30.0:
                        correct_process.kill()
                        correct_process.wait()
                        return self._create_error_result(
                            test_number,
                            "Correct solution timeout (>30s)",
                            generator_time,
                            test_time,
                            30.0,
                            peak_memory_mb,
                        )
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass

            # Issue #7: If stopped, kill process and return None
            if not self.is_running:
                try:
                    correct_process.kill()
                    correct_process.wait(timeout=1)
                except:
                    pass
                return None

            # Wait for output reading threads to complete
            correct_stdout_thread.join(timeout=30)
            correct_stderr_thread.join(timeout=1)
            correct_process.wait(timeout=1)
            
            correct_stdout = correct_stdout_data[0] if correct_stdout_data else ""
            correct_stderr = correct_stderr_data[0] if correct_stderr_data else ""
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

            # Issue #6: REMOVED synchronous disk I/O during test execution
            # Data is already stored in memory dictionary and database
            # self._save_test_io(test_number, input_text, test_output, correct_output)

            # Calculate total time
            total_time = generator_time + test_time + correct_time + comparison_time

            # Create result with metrics
            return {
                "test_number": test_number,
                "passed": outputs_match,
                "input": input_text.strip()[:300]
                + (
                    "..." if len(input_text.strip()) > 300 else ""
                ),  # Truncate for display
                "test_output": test_output.strip()[:300]
                + (
                    "..." if len(test_output.strip()) > 300 else ""
                ),  # Truncate for display
                "correct_output": correct_output.strip()[:300]
                + (
                    "..." if len(correct_output.strip()) > 300 else ""
                ),  # Truncate for display
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
            error_msg = (
                f"Timeout in {e.cmd[0] if e.cmd else 'unknown'} after {e.timeout}s"
            )
            return self._create_error_result(
                test_number, error_msg, peak_memory_mb=peak_memory_mb
            )
        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            return self._create_error_result(
                test_number, error_msg, peak_memory_mb=peak_memory_mb
            )

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
