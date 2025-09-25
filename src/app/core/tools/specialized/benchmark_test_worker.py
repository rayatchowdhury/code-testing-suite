"""
BenchmarkTestWorker - Specialized worker for benchmarking and performance monitoring.

This worker implements the 2-stage benchmark testing process:
1. Generator → produces test input
2. Test solution → processes input while monitoring time and memory usage

Maintains exact signal signatures and behavior from the original inline implementation.
"""

import os
import time
import threading
import multiprocessing
import subprocess
import psutil
from typing import Dict, Any, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
from PySide6.QtCore import QObject, Signal, Slot


class BenchmarkTestWorker(QObject):
    """
    Specialized worker for benchmarking with performance monitoring.
    
    This class extracts and consolidates the BenchmarkTestWorker functionality
    from benchmarker.py while maintaining exact signal compatibility.
    """
    
    # Exact signal signatures from original BenchmarkTestWorker
    testStarted = Signal(int, int)  # current test, total tests
    testCompleted = Signal(str, int, bool, float, float, bool)  # test name, test number, passed, execution time, memory used, memory passed
    allTestsCompleted = Signal(bool)  # True if all passed

    def __init__(self, workspace_dir: str, executables: Dict[str, str], 
                 time_limit: float, memory_limit: int, test_count: int = 1,
                 max_workers: Optional[int] = None):
        """
        Initialize the TLE test worker.
        
        Args:
            workspace_dir: Directory containing test files and executables
            executables: Dictionary with 'generator' and 'test' executable paths
            time_limit: Time limit in milliseconds
            memory_limit: Memory limit in MB
            test_count: Number of tests to run
            max_workers: Maximum number of parallel workers (auto-detected if None)
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
        self.max_workers = max_workers or min(4, max(1, multiprocessing.cpu_count() - 1))
        self._results_lock = threading.Lock()  # Thread-safe results access

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
                            test_result['test_name'],
                            test_result['test_number'],
                            test_result['passed'],
                            test_result['execution_time'],
                            test_result['memory_used'],
                            test_result['memory_passed']
                        )
                        
                        if not test_result['passed']:
                            all_passed = False
                            
                except Exception as e:
                    # Handle any unexpected errors
                    error_result = self._create_error_result(test_number, f"Execution error: {str(e)}")
                    with self._results_lock:
                        self.test_results.append(error_result)
                    self.testCompleted.emit(
                        f"Test {completed_tests}",
                        error_result['test_number'],
                        False,
                        0.0,
                        0.0,
                        False
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
            
            generator_result = subprocess.run(
                [self.executables['generator']],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                creationflags=subprocess.CREATE_NO_WINDOW,
                timeout=10,
                text=True
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
            process = subprocess.Popen(
                [self.executables['test']],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                creationflags=subprocess.CREATE_NO_WINDOW,
                text=True
            )
            
            # Monitor memory usage
            max_memory_used = 0
            memory_limit_exceeded = False
            
            try:
                # Get psutil process object for memory monitoring
                ps_process = psutil.Process(process.pid)
                
                # Send input and start monitoring
                stdout, stderr = process.communicate(input=input_text, timeout=self.time_limit)
                
                # Get final memory usage
                try:
                    memory_info = ps_process.memory_info()
                    memory_used_mb = memory_info.rss / (1024 * 1024)  # Convert to MB
                    max_memory_used = max(max_memory_used, memory_used_mb)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    # Process finished, use last known memory usage
                    pass
                
            except subprocess.TimeoutExpired:
                # Time limit exceeded
                process.kill()
                process.wait()
                
                test_time = time.time() - test_start
                
                return {
                    'test_name': f"Test {test_number}",
                    'test_number': test_number,
                    'passed': False,
                    'execution_time': test_time,
                    'memory_used': max_memory_used,
                    'memory_passed': max_memory_used <= self.memory_limit,
                    'error_details': f"Time Limit Exceeded ({self.time_limit:.2f}s)",
                    'generator_time': generator_time,
                    'input': input_text.strip()[:200] + ("..." if len(input_text.strip()) > 200 else ""),
                    'output': ""
                }
            
            test_time = time.time() - test_start
            
            # Check if memory limit was exceeded
            memory_passed = max_memory_used <= self.memory_limit
            if not memory_passed:
                memory_limit_exceeded = True
            
            # Check process result
            if process.returncode != 0:
                error_msg = f"Test solution failed with exit code {process.returncode}: {stderr}"
                return self._create_error_result(test_number, error_msg, test_time, max_memory_used)
            
            # Check if both time and memory limits were respected
            time_passed = test_time <= self.time_limit
            overall_passed = time_passed and memory_passed and process.returncode == 0
            
            return {
                'test_name': f"Test {test_number}",
                'test_number': test_number,
                'passed': overall_passed,
                'execution_time': test_time,
                'memory_used': max_memory_used,
                'memory_passed': memory_passed,
                'time_passed': time_passed,
                'error_details': self._get_error_details(time_passed, memory_passed, process.returncode),
                'generator_time': generator_time,
                'input': input_text.strip()[:200] + ("..." if len(input_text.strip()) > 200 else ""),
                'output': stdout.strip()[:200] + ("..." if len(stdout.strip()) > 200 else "") if stdout else ""
            }
            
        except Exception as e:
            error_msg = f"Unexpected error in test {test_number}: {str(e)}"
            return self._create_error_result(test_number, error_msg)

    def _get_error_details(self, time_passed: bool, memory_passed: bool, exit_code: int) -> str:
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

    def _create_error_result(self, test_number: int, error_msg: str, 
                           execution_time: float = 0.0, memory_used: float = 0.0) -> Dict[str, Any]:
        """Create a standardized error result dictionary."""
        return {
            'test_name': f"Test {test_number}",
            'test_number': test_number,
            'passed': False,
            'execution_time': execution_time,
            'memory_used': memory_used,
            'memory_passed': memory_used <= self.memory_limit,
            'time_passed': execution_time <= self.time_limit,
            'error_details': error_msg,
            'generator_time': 0.0,
            'input': "",
            'output': ""
        }

    def stop(self):
        """Stop the worker and cancel any running tests."""
        self.is_running = False

    def get_test_results(self) -> list:
        """Get thread-safe copy of test results for database storage."""
        with self._results_lock:
            return self.test_results.copy()