"""
Type definitions for test result details

Phase 5 (Issue #5): TypedDict schemas for type safety
Provides structured types for different test result formats.
"""

from typing import TypedDict


class BaseTestDetail(TypedDict, total=False):
    """Base fields for all test types

    Common fields shared across all test result types.
    Using total=False to make all fields optional for flexibility.
    """

    test_number: int
    passed: bool
    error_details: str
    total_time: float
    memory: float
    status: str  # "pass" or "fail"
    test: int  # Test number (alternative naming)


class ValidatorTestDetail(BaseTestDetail, total=False):
    """Validator-specific test details

    Phase 5 (Issue #5): Type definition for validator test results.
    Includes input generation, test execution, and validation steps.
    """

    input: str
    test_output: str
    validation_message: str
    validator_exit_code: int
    generator_time: float
    test_time: float
    validator_time: float
    output: str  # Alternative naming for test_output
    execution_time: float  # Alternative naming for total_time


class ComparisonTestDetail(BaseTestDetail, total=False):
    """Comparison test details (formerly stress tests)

    Phase 5 (Issue #5): Type definition for comparison test results.
    Compares test solution output against correct solution output.
    """

    input: str
    test_output: str
    correct_output: str
    generator_time: float
    test_time: float
    correct_time: float
    comparison_time: float
    actual_output: str  # Alternative naming for test_output
    expected_output: str  # Alternative naming for correct_output
    output: str  # Another alternative
    execution_time: float  # Alternative naming


class BenchmarkTestDetail(BaseTestDetail, total=False):
    """Benchmark test details (formerly TLE tests)

    Phase 5 (Issue #5): Type definition for benchmark test results.
    Measures execution time and memory usage against thresholds.
    """

    test_name: str
    execution_time: float
    memory_used: float
    memory_passed: bool
    time_passed: bool
    generator_time: float
    input: str
    output: str
    test_size: int
    error: str  # Error message if test failed
    actual_output: str  # Output from test execution


# Type aliases for convenience
TestDetail = ValidatorTestDetail | ComparisonTestDetail | BenchmarkTestDetail
"""Union type for any test detail"""
