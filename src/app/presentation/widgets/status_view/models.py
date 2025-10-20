"""
Status View Data Models

Immutable data classes for test execution state and results.
These models provide clean interfaces between workers and presenters.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional
from enum import Enum


class TestType(Enum):
    """Test execution types"""
    COMPARATOR = "comparator"
    VALIDATOR = "validator"
    BENCHMARKER = "benchmarker"


@dataclass(frozen=True)
class TestResult:
    """
    Immutable test result from worker.
    
    Single source of truth for test completion data.
    Replaces inconsistent **kwargs passing in current implementation.
    """
    test_number: int
    passed: bool
    time: float  # seconds
    memory: float  # MB
    test_type: TestType
    
    # Type-specific data stored in flexible dict
    # Comparator: input_text, correct_output, test_output
    # Validator: input_data, test_output, validation_message, error_details, exit_code
    # Benchmarker: test_name, execution_time, memory_passed, input_data, output_data, test_size
    data: Dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def from_comparator(cls, test_number: int, passed: bool, 
                       input_text: str, correct_output: str, test_output: str,
                       time: float, memory: float) -> 'TestResult':
        """Create TestResult from comparator worker signal"""
        return cls(
            test_number=test_number,
            passed=passed,
            time=time,
            memory=memory,
            test_type=TestType.COMPARATOR,
            data={
                'input_text': input_text,
                'correct_output': correct_output,
                'test_output': test_output
            }
        )
    
    @classmethod
    def from_validator(cls, test_number: int, passed: bool,
                      input_data: str, test_output: str, validation_message: str,
                      error_details: str, validator_exit_code: int,
                      time: float, memory: float) -> 'TestResult':
        """Create TestResult from validator worker signal"""
        return cls(
            test_number=test_number,
            passed=passed,
            time=time,
            memory=memory,
            test_type=TestType.VALIDATOR,
            data={
                'input_data': input_data,
                'test_output': test_output,
                'validation_message': validation_message,
                'error_details': error_details,
                'validator_exit_code': validator_exit_code
            }
        )
    
    @classmethod
    def from_benchmarker(cls, test_name: str, test_number: int, passed: bool,
                        execution_time: float, memory_used: float, memory_passed: bool,
                        input_data: str, output_data: str, test_size: int) -> 'TestResult':
        """Create TestResult from benchmarker worker signal"""
        return cls(
            test_number=test_number,
            passed=passed,
            time=execution_time,
            memory=memory_used,
            test_type=TestType.BENCHMARKER,
            data={
                'test_name': test_name,
                'memory_passed': memory_passed,
                'input_data': input_data,
                'output_data': output_data,
                'test_size': test_size
            }
        )


@dataclass
class TestExecutionState:
    """
    Mutable state for test execution progress.
    
    Replaces scattered state variables in BaseStatusView.
    Single responsibility: track execution metrics.
    """
    total_tests: int = 0
    completed_tests: int = 0
    passed_tests: int = 0
    failed_tests: int = 0
    max_workers: int = 0
    is_running: bool = False
    start_time: Optional[float] = None
    
    def reset(self, total: int, workers: int) -> None:
        """Reset state for new test run"""
        self.total_tests = total
        self.completed_tests = 0
        self.passed_tests = 0
        self.failed_tests = 0
        self.max_workers = workers
        self.is_running = True
        import time
        self.start_time = time.time()
    
    def record_result(self, passed: bool) -> None:
        """Record a test completion"""
        self.completed_tests += 1
        if passed:
            self.passed_tests += 1
        else:
            self.failed_tests += 1
    
    def mark_complete(self) -> None:
        """Mark execution as complete"""
        self.is_running = False
    
    @property
    def progress_percentage(self) -> float:
        """Calculate progress percentage"""
        if self.total_tests == 0:
            return 0.0
        return (self.completed_tests / self.total_tests) * 100
    
    @property
    def elapsed_time(self) -> float:
        """Get elapsed time in seconds"""
        if self.start_time is None:
            return 0.0
        import time
        return time.time() - self.start_time
    
    @property
    def tests_per_second(self) -> float:
        """Calculate test execution speed"""
        elapsed = self.elapsed_time
        if elapsed == 0:
            return 0.0
        return self.completed_tests / elapsed
    
    @property
    def estimated_remaining_seconds(self) -> float:
        """Estimate remaining time"""
        if self.completed_tests == 0:
            return 0.0
        speed = self.tests_per_second
        if speed == 0:
            return 0.0
        return (self.total_tests - self.completed_tests) / speed


@dataclass
class TestStatistics:
    """Statistics snapshot for widget updates"""
    completed: int
    total: int
    passed: int
    failed: int
    progress_pct: float
    elapsed_seconds: float
    remaining_seconds: float
    tests_per_second: float
    workers_active: int
