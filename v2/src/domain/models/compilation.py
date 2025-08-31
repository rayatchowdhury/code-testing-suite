# TODO: Extract compilation result models from v1 tools
"""
Compilation Domain Models

Core data structures for compilation operations, extracted from v1 tools.
"""
from dataclasses import dataclass
from enum import Enum
from typing import Optional
from pathlib import Path

class CompilationStatus(Enum):
    """Status of a compilation operation"""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress" 
    SUCCESS = "success"
    FAILED = "failed"
    CANCELLED = "cancelled"

class TestResult(Enum):
    """Result of a test execution"""
    PASSED = "passed"
    FAILED = "failed"
    TIMEOUT = "timeout"
    ERROR = "error"

@dataclass
class CompilationResult:
    """Result of compiling a single file"""
    file_path: Path
    status: CompilationStatus
    output: str = ""
    error_output: str = ""
    execution_time: float = 0.0
    executable_path: Optional[Path] = None

@dataclass
class TestCase:
    """A single test case for stress testing"""
    test_number: int
    input_data: str
    expected_output: str
    actual_output: str = ""
    result: TestResult = TestResult.FAILED
    execution_time: float = 0.0

@dataclass
class StressTestResult:
    """Result of a stress testing session"""
    total_tests: int
    passed_tests: int
    failed_tests: int
    test_cases: list[TestCase]
    all_passed: bool = False
    total_time: float = 0.0

@dataclass
class TLETestResult:
    """Result of a time-limit exceeded test"""
    test_name: str
    passed: bool
    execution_time: float
    time_limit: float
    output: str = ""
