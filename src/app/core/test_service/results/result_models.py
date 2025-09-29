"""
Result Models - Data models for test and compilation results.
"""

from typing import Optional, List
from dataclasses import dataclass
from pathlib import Path
from datetime import datetime


@dataclass
class CompilationResult:
    """Result of compilation operation."""
    success: bool
    executable_path: Optional[Path] = None
    output: str = ""
    error: str = ""
    compilation_time: float = 0.0
    cached: bool = False


@dataclass  
class TestResult:
    """Result of single test execution."""
    test_number: int
    passed: bool
    input_data: str = ""
    expected_output: str = ""
    actual_output: str = ""
    execution_time: float = 0.0
    memory_used: int = 0
    error_message: str = ""
    timestamp: datetime = None


@dataclass
class TestSummary:
    """Summary of test execution batch."""
    total_tests: int
    passed_tests: int
    failed_tests: int
    total_time: float
    average_time: float
    max_memory: int
    test_results: List[TestResult]