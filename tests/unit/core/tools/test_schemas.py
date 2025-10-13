"""
Tests for core.tools.schemas module

Phase 8 (Task 4): Comprehensive tests for TypedDict schemas
Testing data structure validation and type safety.
"""

import pytest
from typing import get_type_hints
from src.app.core.tools.schemas import (
    BaseTestDetail,
    ValidatorTestDetail,
    ComparisonTestDetail,
    BenchmarkTestDetail,
    TestDetail,
)


class TestBaseTestDetail:
    """Test BaseTestDetail schema structure"""

    def test_base_test_detail_has_required_fields(self):
        """BaseTestDetail should have all common fields"""
        # Arrange & Act
        hints = get_type_hints(BaseTestDetail)

        # Assert
        assert "test_number" in BaseTestDetail.__annotations__
        assert "passed" in BaseTestDetail.__annotations__
        assert "error_details" in BaseTestDetail.__annotations__
        assert "total_time" in BaseTestDetail.__annotations__
        assert "memory" in BaseTestDetail.__annotations__
        assert "status" in BaseTestDetail.__annotations__
        assert "test" in BaseTestDetail.__annotations__

    def test_base_test_detail_fields_are_optional(self):
        """BaseTestDetail fields should be optional (total=False)"""
        # Arrange & Act
        detail: BaseTestDetail = {}

        # Assert - should not raise error with empty dict
        assert isinstance(detail, dict)

    def test_base_test_detail_accepts_partial_data(self):
        """BaseTestDetail should accept partial data"""
        # Arrange & Act
        detail: BaseTestDetail = {
            "test_number": 1,
            "passed": True,
        }

        # Assert
        assert detail["test_number"] == 1
        assert detail["passed"] is True

    def test_base_test_detail_accepts_all_fields(self):
        """BaseTestDetail should accept all fields when provided"""
        # Arrange & Act
        detail: BaseTestDetail = {
            "test_number": 5,
            "passed": False,
            "error_details": "Runtime error",
            "total_time": 1.5,
            "memory": 256.0,
            "status": "fail",
            "test": 5,
        }

        # Assert
        assert detail["test_number"] == 5
        assert detail["passed"] is False
        assert detail["error_details"] == "Runtime error"
        assert detail["total_time"] == 1.5
        assert detail["memory"] == 256.0
        assert detail["status"] == "fail"
        assert detail["test"] == 5


class TestValidatorTestDetail:
    """Test ValidatorTestDetail schema structure"""

    def test_validator_test_detail_inherits_base_fields(self):
        """ValidatorTestDetail should have all BaseTestDetail fields"""
        # Arrange & Act
        annotations = ValidatorTestDetail.__annotations__

        # Assert
        assert "test_number" in annotations
        assert "passed" in annotations
        assert "status" in annotations

    def test_validator_test_detail_has_specific_fields(self):
        """ValidatorTestDetail should have validator-specific fields"""
        # Arrange & Act
        annotations = ValidatorTestDetail.__annotations__

        # Assert
        assert "input" in annotations
        assert "test_output" in annotations
        assert "validation_message" in annotations
        assert "validator_exit_code" in annotations
        assert "generator_time" in annotations
        assert "test_time" in annotations
        assert "validator_time" in annotations
        assert "output" in annotations
        assert "execution_time" in annotations

    def test_validator_test_detail_accepts_validator_data(self):
        """ValidatorTestDetail should accept complete validator data"""
        # Arrange & Act
        detail: ValidatorTestDetail = {
            "test_number": 1,
            "passed": True,
            "input": "5\n1 2 3 4 5",
            "test_output": "15",
            "validation_message": "Output is valid",
            "validator_exit_code": 0,
            "generator_time": 0.01,
            "test_time": 0.05,
            "validator_time": 0.02,
            "total_time": 0.08,
            "status": "pass",
        }

        # Assert
        assert detail["test_number"] == 1
        assert detail["passed"] is True
        assert detail["input"] == "5\n1 2 3 4 5"
        assert detail["test_output"] == "15"
        assert detail["validation_message"] == "Output is valid"
        assert detail["validator_exit_code"] == 0
        assert detail["generator_time"] == 0.01
        assert detail["test_time"] == 0.05
        assert detail["validator_time"] == 0.02

    def test_validator_test_detail_handles_alternative_naming(self):
        """ValidatorTestDetail should support alternative field names"""
        # Arrange & Act
        detail: ValidatorTestDetail = {
            "test": 2,  # Alternative to test_number
            "output": "result",  # Alternative to test_output
            "execution_time": 1.0,  # Alternative to total_time
        }

        # Assert
        assert detail["test"] == 2
        assert detail["output"] == "result"
        assert detail["execution_time"] == 1.0


class TestComparisonTestDetail:
    """Test ComparisonTestDetail schema structure"""

    def test_comparison_test_detail_inherits_base_fields(self):
        """ComparisonTestDetail should have all BaseTestDetail fields"""
        # Arrange & Act
        annotations = ComparisonTestDetail.__annotations__

        # Assert
        assert "test_number" in annotations
        assert "passed" in annotations
        assert "status" in annotations

    def test_comparison_test_detail_has_specific_fields(self):
        """ComparisonTestDetail should have comparison-specific fields"""
        # Arrange & Act
        annotations = ComparisonTestDetail.__annotations__

        # Assert
        assert "input" in annotations
        assert "test_output" in annotations
        assert "correct_output" in annotations
        assert "generator_time" in annotations
        assert "test_time" in annotations
        assert "correct_time" in annotations
        assert "comparison_time" in annotations
        assert "actual_output" in annotations
        assert "expected_output" in annotations

    def test_comparison_test_detail_accepts_comparison_data(self):
        """ComparisonTestDetail should accept complete comparison data"""
        # Arrange & Act
        detail: ComparisonTestDetail = {
            "test_number": 3,
            "passed": False,
            "input": "10\n5 3 8 1 9 2 7 4 6 10",
            "test_output": "55",
            "correct_output": "55",
            "generator_time": 0.01,
            "test_time": 0.1,
            "correct_time": 0.05,
            "comparison_time": 0.001,
            "status": "fail",
            "error_details": "Output mismatch",
        }

        # Assert
        assert detail["test_number"] == 3
        assert detail["passed"] is False
        assert detail["input"].startswith("10\n")
        assert detail["test_output"] == "55"
        assert detail["correct_output"] == "55"
        assert detail["generator_time"] == 0.01
        assert detail["test_time"] == 0.1
        assert detail["correct_time"] == 0.05
        assert detail["comparison_time"] == 0.001

    def test_comparison_test_detail_handles_output_alternatives(self):
        """ComparisonTestDetail should support alternative output field names"""
        # Arrange & Act
        detail: ComparisonTestDetail = {
            "actual_output": "result1",  # Alternative to test_output
            "expected_output": "result2",  # Alternative to correct_output
            "output": "result3",  # Another alternative
            "execution_time": 2.0,  # Alternative to total_time
        }

        # Assert
        assert detail["actual_output"] == "result1"
        assert detail["expected_output"] == "result2"
        assert detail["output"] == "result3"
        assert detail["execution_time"] == 2.0


class TestBenchmarkTestDetail:
    """Test BenchmarkTestDetail schema structure"""

    def test_benchmark_test_detail_inherits_base_fields(self):
        """BenchmarkTestDetail should have all BaseTestDetail fields"""
        # Arrange & Act
        annotations = BenchmarkTestDetail.__annotations__

        # Assert
        assert "test_number" in annotations
        assert "passed" in annotations
        assert "status" in annotations

    def test_benchmark_test_detail_has_specific_fields(self):
        """BenchmarkTestDetail should have benchmark-specific fields"""
        # Arrange & Act
        annotations = BenchmarkTestDetail.__annotations__

        # Assert
        assert "test_name" in annotations
        assert "execution_time" in annotations
        assert "memory_used" in annotations
        assert "memory_passed" in annotations
        assert "time_passed" in annotations
        assert "generator_time" in annotations
        assert "input" in annotations
        assert "output" in annotations
        assert "test_size" in annotations
        assert "error" in annotations
        assert "actual_output" in annotations

    def test_benchmark_test_detail_accepts_benchmark_data(self):
        """BenchmarkTestDetail should accept complete benchmark data"""
        # Arrange & Act
        detail: BenchmarkTestDetail = {
            "test_number": 5,
            "passed": True,
            "test_name": "Large Input Test",
            "execution_time": 0.95,
            "memory_used": 128.5,
            "memory_passed": True,
            "time_passed": True,
            "generator_time": 0.02,
            "input": "1000000\n...",
            "output": "result",
            "test_size": 1000000,
            "status": "pass",
        }

        # Assert
        assert detail["test_number"] == 5
        assert detail["passed"] is True
        assert detail["test_name"] == "Large Input Test"
        assert detail["execution_time"] == 0.95
        assert detail["memory_used"] == 128.5
        assert detail["memory_passed"] is True
        assert detail["time_passed"] is True
        assert detail["generator_time"] == 0.02
        assert detail["test_size"] == 1000000

    def test_benchmark_test_detail_handles_failed_benchmark(self):
        """BenchmarkTestDetail should handle failed benchmark tests"""
        # Arrange & Act
        detail: BenchmarkTestDetail = {
            "test_number": 6,
            "passed": False,
            "test_name": "Timeout Test",
            "execution_time": 2.5,
            "memory_used": 512.0,
            "memory_passed": False,
            "time_passed": False,
            "status": "fail",
            "error": "Time limit exceeded",
        }

        # Assert
        assert detail["passed"] is False
        assert detail["memory_passed"] is False
        assert detail["time_passed"] is False
        assert detail["error"] == "Time limit exceeded"


class TestTestDetailUnion:
    """Test TestDetail union type"""

    def test_test_detail_accepts_validator_type(self):
        """TestDetail should accept ValidatorTestDetail"""
        # Arrange
        validator_detail: ValidatorTestDetail = {
            "test_number": 1,
            "passed": True,
            "validation_message": "Valid",
        }

        # Act
        detail: TestDetail = validator_detail

        # Assert
        assert detail["test_number"] == 1
        assert "validation_message" in detail

    def test_test_detail_accepts_comparison_type(self):
        """TestDetail should accept ComparisonTestDetail"""
        # Arrange
        comparison_detail: ComparisonTestDetail = {
            "test_number": 2,
            "passed": True,
            "correct_output": "expected",
        }

        # Act
        detail: TestDetail = comparison_detail

        # Assert
        assert detail["test_number"] == 2
        assert "correct_output" in detail

    def test_test_detail_accepts_benchmark_type(self):
        """TestDetail should accept BenchmarkTestDetail"""
        # Arrange
        benchmark_detail: BenchmarkTestDetail = {
            "test_number": 3,
            "passed": True,
            "time_passed": True,
            "memory_passed": True,
        }

        # Act
        detail: TestDetail = benchmark_detail

        # Assert
        assert detail["test_number"] == 3
        assert "time_passed" in detail
        assert "memory_passed" in detail


class TestSchemaIntegration:
    """Integration tests for schema usage"""

    def test_schemas_handle_empty_dictionaries(self):
        """All schemas should handle empty dictionaries (total=False)"""
        # Arrange & Act & Assert
        base: BaseTestDetail = {}
        validator: ValidatorTestDetail = {}
        comparison: ComparisonTestDetail = {}
        benchmark: BenchmarkTestDetail = {}

        assert isinstance(base, dict)
        assert isinstance(validator, dict)
        assert isinstance(comparison, dict)
        assert isinstance(benchmark, dict)

    def test_schemas_handle_missing_optional_fields(self):
        """Schemas should work with minimal required data"""
        # Arrange & Act
        validator: ValidatorTestDetail = {"test_number": 1}
        comparison: ComparisonTestDetail = {"test_number": 2}
        benchmark: BenchmarkTestDetail = {"test_number": 3}

        # Assert
        assert validator.get("test_number") == 1
        assert comparison.get("test_number") == 2
        assert benchmark.get("test_number") == 3
        assert validator.get("passed") is None  # Optional field

    @pytest.mark.parametrize(
        "status_value",
        ["pass", "fail", "error", "timeout", "skip"],
    )
    def test_schemas_accept_various_status_values(self, status_value):
        """Schemas should accept various status values"""
        # Arrange & Act
        detail: BaseTestDetail = {
            "test_number": 1,
            "status": status_value,
        }

        # Assert
        assert detail["status"] == status_value

    @pytest.mark.parametrize(
        "time_value,memory_value",
        [
            (0.0, 0.0),
            (1.5, 128.0),
            (10.0, 1024.0),
            (0.001, 0.5),
        ],
    )
    def test_schemas_accept_various_numeric_values(self, time_value, memory_value):
        """Schemas should accept various numeric values for time and memory"""
        # Arrange & Act
        detail: BenchmarkTestDetail = {
            "execution_time": time_value,
            "memory_used": memory_value,
        }

        # Assert
        assert detail["execution_time"] == time_value
        assert detail["memory_used"] == memory_value

    def test_validator_detail_supports_multiline_input(self):
        """ValidatorTestDetail should handle multiline input strings"""
        # Arrange
        multiline_input = "3\nline1\nline2\nline3"

        # Act
        detail: ValidatorTestDetail = {
            "input": multiline_input,
            "test_output": "result",
        }

        # Assert
        assert detail["input"] == multiline_input
        assert "\n" in detail["input"]

    def test_comparison_detail_handles_large_outputs(self):
        """ComparisonTestDetail should handle large output strings"""
        # Arrange
        large_output = "output\n" * 1000

        # Act
        detail: ComparisonTestDetail = {
            "test_output": large_output,
            "correct_output": large_output,
        }

        # Assert
        assert len(detail["test_output"]) > 5000
        assert detail["test_output"] == detail["correct_output"]

    def test_benchmark_detail_handles_edge_case_values(self):
        """BenchmarkTestDetail should handle edge case numeric values"""
        # Arrange & Act
        detail: BenchmarkTestDetail = {
            "execution_time": 0.0,  # Instant execution
            "memory_used": 0.0,  # No memory
            "test_size": 0,  # Empty test
        }

        # Assert
        assert detail["execution_time"] == 0.0
        assert detail["memory_used"] == 0.0
        assert detail["test_size"] == 0

    def test_all_schemas_are_dict_compatible(self):
        """All schemas should be compatible with dict operations"""
        # Arrange
        details = [
            BaseTestDetail(test_number=1),
            ValidatorTestDetail(test_number=2, validation_message="OK"),
            ComparisonTestDetail(test_number=3, correct_output="expected"),
            BenchmarkTestDetail(test_number=4, time_passed=True),
        ]

        # Act & Assert
        for detail in details:
            assert isinstance(detail, dict)
            assert "test_number" in detail
            assert len(detail) > 0
            assert list(detail.keys())
            assert list(detail.values())
