"""
BenchmarkTestWorker - Specialized worker for benchmarking and performance monitoring.

This worker implements the 2-stage benchmark testing process:
1. Generator → produces test input
2. Test solution → processes input while monitoring time and memory usage

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


class BenchmarkTestWorker(BaseTestWorker):
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
        # Call base class initialization - handles common setup
        super().__init__(
            workspace_dir=workspace_dir,
            executables=executables,
            test_count=test_count,
            max_workers=max_workers,
            execution_commands=execution_commands
        )
        
        # Benchmark-specific attributes
        self.time_limit = time_limit / 1000.0  # Convert ms to seconds
        self.memory_limit = memory_limit  # MB
    
    def _calculate_optimal_workers(self) -> int:
        """
        Override: Use fewer workers for benchmarking due to memory monitoring overhead.
        
        Benchmark tests continuously monitor memory usage which adds CPU overhead,
        so we use fewer parallel workers (4 vs 8) to avoid overwhelming the system.
        
        Returns:
            Optimal worker count for benchmarking (minimum 1, maximum 4)
        """
        import multiprocessing
        return min(4, max(1, multiprocessing.cpu_count() - 1))
    
    def _emit_test_completed(self, test_result: Dict[str, Any]) -> None:
        """
        Emit the testCompleted signal with benchmark-specific parameters.
        
        Required by BaseTestWorker to handle specialized signal emission.
        
        Args:
            test_result: Dictionary containing test result data
        """
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
    
    def _run_single_test(self, test_number: int) -> Optional[Dict[str, Any]]:
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
                    process.stdin.close()  # Issue #7: Close stdin to signal EOF

                # Issue #7: Read output in thread to prevent pipe deadlock
                stdout_data = []
                stderr_data = []
                
                def read_stdout():
                    stdout_data.append(process.stdout.read())
                
                def read_stderr():
                    stderr_data.append(process.stderr.read())
                
                import threading
                stdout_thread = threading.Thread(target=read_stdout, daemon=True)
                stderr_thread = threading.Thread(target=read_stderr, daemon=True)
                stdout_thread.start()
                stderr_thread.start()

                # Monitor memory usage while process runs (output being read in background)
                while process.poll() is None and self.is_running:  # Issue #7: Check is_running
                    try:
                        memory_info = ps_process.memory_info()
                        memory_used_mb = memory_info.rss / (
                            1024 * 1024
                        )  # Convert to MB
                        max_memory_used = max(max_memory_used, memory_used_mb)
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        # Process finished
                        break

                    # Small sleep to avoid busy-waiting (Issue #5: optimized from 0.001 to 0.01)
                    time.sleep(0.01)

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

                # Issue #7: If stopped, kill process and return None
                if not self.is_running:
                    try:
                        process.kill()
                        process.wait(timeout=1)
                    except:
                        pass
                    return None

                # Wait for output reading threads to complete
                stdout_thread.join(timeout=5)
                stderr_thread.join(timeout=1)
                process.wait(timeout=1)
                
                stdout = stdout_data[0] if stdout_data else ""
                stderr = stderr_data[0] if stderr_data else ""

            except (psutil.NoSuchProcess, psutil.AccessDenied, Exception) as e:
                # Handle any errors during memory monitoring
                # Process may have terminated unexpectedly
                # Output reading threads should still complete
                try:
                    stdout_thread.join(timeout=1)
                    stderr_thread.join(timeout=0.5)
                    process.wait(timeout=0.5)
                except:
                    process.kill()
                    process.wait()
                
                stdout = stdout_data[0] if stdout_data else ""
                stderr = stderr_data[0] if stderr_data else ""

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

            # Issue #6: REMOVED synchronous disk I/O during test execution
            # Data is already stored in memory dictionary and database
            # self._save_test_io(test_number, input_text, stdout)

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
        if not time_passed and not memory_passed:
            return f"Time Limit Exceeded ({self.time_limit:.2f}s) & Memory Limit Exceeded ({self.memory_limit}MB)"
        if not time_passed:
            return f"Time Limit Exceeded ({self.time_limit:.2f}s)"
        if not memory_passed:
            return f"Memory Limit Exceeded ({self.memory_limit}MB)"

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
