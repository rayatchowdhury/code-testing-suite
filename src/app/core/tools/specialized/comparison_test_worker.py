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
import time
import threading
import multiprocessing
import subprocess
from typing import Dict, Any, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
from PySide6.QtCore import QObject, Signal, Slot


class ComparisonTestWorker(QObject):
    """
    Specialized worker for comparison testing with output comparison.
    
    This class extracts and consolidates the ComparisonTestWorker functionality
    from comparator.py while maintaining exact signal compatibility.
    """
    
    # Exact signal signatures from original ComparisonTestWorker
    testStarted = Signal(int, int)  # current test, total tests
    testCompleted = Signal(int, bool, str, str, str)  # test number, passed, input, correct output, test output
    allTestsCompleted = Signal(bool)  # True if all passed

    def __init__(self, workspace_dir: str, executables: Dict[str, str], 
                 test_count: int, max_workers: Optional[int] = None):
        """
        Initialize the comparison test worker.
        
        Args:
            workspace_dir: Directory containing test files and executables
            executables: Dictionary with 'generator', 'test', 'correct' executable paths
            test_count: Number of tests to run
            max_workers: Maximum number of parallel workers (auto-detected if None)
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
                        
                        # Emit signals for UI updates
                        self.testStarted.emit(completed_tests, self.test_count)
                        self.testCompleted.emit(
                            test_result['test_number'],
                            test_result['passed'],
                            test_result['input'],
                            test_result['correct_output'],
                            test_result['test_output']
                        )
                        
                        if not test_result['passed']:
                            all_passed = False
                            
                except Exception as e:
                    # Handle any unexpected errors
                    error_result = self._create_error_result(test_number, f"Execution error: {str(e)}")
                    with self._results_lock:
                        self.test_results.append(error_result)
                    self.testCompleted.emit(
                        error_result['test_number'],
                        False,
                        "",
                        "",
                        error_result['error_details']
                    )
                    all_passed = False

        self.allTestsCompleted.emit(all_passed)

    def _run_single_comparison_test(self, test_number: int) -> Optional[Dict[str, Any]]:
        """
        Run a single comparison test with output comparison.
        
        This implements the 3-stage stress testing process:
        1. Generator → produces test input
        2. Test solution → processes input to produce output
        3. Correct solution → processes input to produce expected output
        4. Compare outputs for correctness
        
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
                return self._create_error_result(test_number, error_msg, generator_time)
            
            # Get generated input
            input_text = generator_result.stdout
            
            # Stage 2: Run test solution
            test_start = time.time()
            
            test_result = subprocess.run(
                [self.executables['test']],
                input=input_text,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                creationflags=subprocess.CREATE_NO_WINDOW,
                timeout=30,
                text=True
            )
            
            test_time = time.time() - test_start
            
            if test_result.returncode != 0:
                error_msg = f"Test solution failed: {test_result.stderr}"
                return self._create_error_result(test_number, error_msg, generator_time, test_time)
            
            # Get test output
            test_output = test_result.stdout
            
            # Stage 3: Run correct solution
            correct_start = time.time()
            
            correct_result = subprocess.run(
                [self.executables['correct']],
                input=input_text,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                creationflags=subprocess.CREATE_NO_WINDOW,
                timeout=30,
                text=True
            )
            
            correct_time = time.time() - correct_start
            
            if correct_result.returncode != 0:
                error_msg = f"Correct solution failed: {correct_result.stderr}"
                return self._create_error_result(test_number, error_msg, generator_time, test_time, correct_time)
            
            # Get correct output
            correct_output = correct_result.stdout
            
            # Stage 4: Compare outputs
            comparison_start = time.time()
            
            # Normalize outputs for comparison (strip whitespace)
            test_output_normalized = test_output.strip()
            correct_output_normalized = correct_output.strip()
            
            # Check if outputs match
            outputs_match = test_output_normalized == correct_output_normalized
            
            comparison_time = time.time() - comparison_start
            
            # Create result
            return {
                'test_number': test_number,
                'passed': outputs_match,
                'input': input_text.strip()[:300] + ("..." if len(input_text.strip()) > 300 else ""),  # Truncate for display
                'test_output': test_output.strip()[:300] + ("..." if len(test_output.strip()) > 300 else ""),  # Truncate for display
                'correct_output': correct_output.strip()[:300] + ("..." if len(correct_output.strip()) > 300 else ""),  # Truncate for display
                'generator_time': generator_time,
                'test_time': test_time,
                'correct_time': correct_time,
                'comparison_time': comparison_time,
                'total_time': generator_time + test_time + correct_time + comparison_time,
                'error_details': "" if outputs_match else "Output mismatch",
                'test_output_full': test_output,  # Full output for database
                'correct_output_full': correct_output,  # Full output for database
                'input_full': input_text  # Full input for database
            }
            
        except subprocess.TimeoutExpired as e:
            error_msg = f"Timeout in {e.cmd[0] if e.cmd else 'unknown'} after {e.timeout}s"
            return self._create_error_result(test_number, error_msg)
        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            return self._create_error_result(test_number, error_msg)

    def _create_error_result(self, test_number: int, error_msg: str, 
                           generator_time: float = 0.0, test_time: float = 0.0, 
                           correct_time: float = 0.0) -> Dict[str, Any]:
        """Create a standardized error result dictionary."""
        return {
            'test_number': test_number,
            'passed': False,
            'input': "",
            'test_output': "",
            'correct_output': "",
            'generator_time': generator_time,
            'test_time': test_time,
            'correct_time': correct_time,
            'comparison_time': 0.0,
            'total_time': generator_time + test_time + correct_time,
            'error_details': error_msg,
            'test_output_full': "",
            'correct_output_full': "",
            'input_full': ""
        }

    def stop(self):
        """Stop the worker and cancel any running tests."""
        self.is_running = False

    def get_test_results(self) -> list:
        """Get thread-safe copy of test results for database storage."""
        with self._results_lock:
            return self.test_results.copy()