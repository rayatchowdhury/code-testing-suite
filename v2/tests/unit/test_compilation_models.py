"""
Unit tests for Compilation Domain Models

Tests the core data structures for compilation operations
"""
import pytest
from pathlib import Path
from domain.models.compilation import (
    CompilationStatus,
    CompilationResult,
    TestResult,
    TestCase,
    StressTestResult,
    TLETestResult
)

class TestCompilationModels:
    """Test compilation domain models"""
    
    def test_compilation_result_creation(self):
        """Test CompilationResult creation"""
        file_path = Path("test.cpp")
        result = CompilationResult(
            file_path=file_path,
            status=CompilationStatus.SUCCESS,
            output="Compilation successful",
            execution_time=1.5
        )
        
        assert result.file_path == file_path
        assert result.status == CompilationStatus.SUCCESS
        assert result.output == "Compilation successful"
        assert result.execution_time == 1.5
        assert result.error_output == ""
        assert result.executable_path is None
    
    def test_compilation_result_with_executable(self):
        """Test CompilationResult with executable path"""
        source_path = Path("test.cpp")
        exe_path = Path("test.exe")
        
        result = CompilationResult(
            file_path=source_path,
            status=CompilationStatus.SUCCESS,
            executable_path=exe_path
        )
        
        assert result.executable_path == exe_path
    
    def test_test_case_creation(self):
        """Test TestCase creation"""
        test_case = TestCase(
            test_number=1,
            input_data="5\n",
            expected_output="120\n",
            actual_output="120\n",
            result=TestResult.PASSED,
            execution_time=0.1
        )
        
        assert test_case.test_number == 1
        assert test_case.result == TestResult.PASSED
        assert test_case.execution_time == 0.1
    
    def test_stress_test_result_calculation(self):
        """Test StressTestResult calculations"""
        test_cases = [
            TestCase(1, "1", "1", "1", TestResult.PASSED),
            TestCase(2, "2", "4", "4", TestResult.PASSED),
            TestCase(3, "3", "9", "8", TestResult.FAILED),
        ]
        
        result = StressTestResult(
            total_tests=3,
            passed_tests=2,
            failed_tests=1,
            test_cases=test_cases,
            all_passed=False,
            total_time=0.5
        )
        
        assert result.total_tests == 3
        assert result.passed_tests == 2
        assert result.failed_tests == 1
        assert not result.all_passed
        assert len(result.test_cases) == 3
    
    def test_tle_test_result(self):
        """Test TLETestResult creation"""
        result = TLETestResult(
            test_name="Generator",
            passed=True,
            execution_time=0.8,
            time_limit=1.0,
            output="Generated successfully"
        )
        
        assert result.test_name == "Generator"
        assert result.passed
        assert result.execution_time == 0.8
        assert result.time_limit == 1.0
        assert result.output == "Generated successfully"
    
    def test_compilation_status_enum(self):
        """Test CompilationStatus enum values"""
        assert CompilationStatus.NOT_STARTED.value == "not_started"
        assert CompilationStatus.IN_PROGRESS.value == "in_progress"
        assert CompilationStatus.SUCCESS.value == "success"
        assert CompilationStatus.FAILED.value == "failed"
        assert CompilationStatus.CANCELLED.value == "cancelled"
    
    def test_test_result_enum(self):
        """Test TestResult enum values"""
        assert TestResult.PASSED.value == "passed"
        assert TestResult.FAILED.value == "failed"
        assert TestResult.TIMEOUT.value == "timeout"
        assert TestResult.ERROR.value == "error"
