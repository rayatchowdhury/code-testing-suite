"""
Test suite for Comparator class.

Tests verify the comparison testing workflow, including:
- Initialization with multi-language support and nested file structure
- Compiler flag configuration for comparison testing
- Worker creation with comparison-specific parameters
- Signal connections for test progress
- Test result creation with comparison analysis
- Public API methods (run_stress_test, run_comparison_test)
"""

import pytest
from unittest.mock import Mock, MagicMock, patch, call
from PySide6.QtCore import Signal
from datetime import datetime
import json

from src.app.core.tools.comparator import Comparator
from src.app.persistence.database.models import TestResult


@pytest.fixture
def comparator_files(temp_workspace):
    """Create comparator file paths for testing."""
    comparator_dir = temp_workspace / "comparator"
    comparator_dir.mkdir(parents=True, exist_ok=True)

    files = {
        "generator": str(comparator_dir / "generator.cpp"),
        "correct": str(comparator_dir / "correct.cpp"),
        "test": str(comparator_dir / "test.cpp"),
    }

    # Create test files
    for filepath in files.values():
        Path(filepath).write_text("int main() { return 0; }")

    return files


@pytest.fixture
def mock_compiler():
    """Create mock compiler for testing."""
    with patch("src.app.core.tools.base.base_runner.BaseCompiler") as mock:
        compiler_instance = MagicMock()
        compiler_instance.executables = {
            "generator": "/path/to/generator",
            "correct": "/path/to/correct",
            "test": "/path/to/test",
        }
        compiler_instance.get_execution_command.side_effect = lambda name: f"./{name}"
        mock.return_value = compiler_instance
        yield compiler_instance


@pytest.fixture
def mock_database():
    """Create mock database manager for testing."""
    with patch("src.app.core.tools.base.base_runner.DatabaseManager") as mock:
        db_instance = MagicMock()
        mock.return_value = db_instance
        yield db_instance


class TestComparatorInitialization:
    """Test Comparator initialization and setup."""

    def test_init_with_default_files(
        self, temp_workspace, mock_compiler, mock_database
    ):
        """Should initialize with default nested file structure."""
        with patch(
            "src.app.shared.constants.paths.get_workspace_file_path"
        ) as mock_path:
            mock_path.side_effect = (
                lambda workspace, test_type, filename: f"{workspace}/{test_type}/{filename}"
            )

            comparator = Comparator(str(temp_workspace))

            assert comparator.workspace_dir == str(temp_workspace)
            assert comparator.test_type == "comparison"
            # Verify get_workspace_file_path called for each file
            assert mock_path.call_count == 3

    def test_init_with_custom_files(
        self, temp_workspace, comparator_files, mock_compiler, mock_database
    ):
        """Should accept custom file paths."""
        comparator = Comparator(str(temp_workspace), files=comparator_files)

        assert comparator.workspace_dir == str(temp_workspace)
        assert comparator.test_type == "comparison"

    def test_init_with_config(
        self, temp_workspace, comparator_files, mock_compiler, mock_database
    ):
        """Should accept configuration dictionary."""
        config = {"language": "python", "timeout": 5.0, "max_memory": 512}

        comparator = Comparator(
            str(temp_workspace), files=comparator_files, config=config
        )

        assert comparator.workspace_dir == str(temp_workspace)

    def test_init_inherits_from_base_runner(
        self, temp_workspace, comparator_files, mock_compiler, mock_database
    ):
        """Should properly inherit from BaseRunner."""
        from src.app.core.tools.base.base_runner import BaseRunner

        comparator = Comparator(str(temp_workspace), files=comparator_files)

        assert isinstance(comparator, BaseRunner)

    def test_init_defines_test_completed_signal(
        self, temp_workspace, comparator_files, mock_compiler, mock_database
    ):
        """Should define comparison-specific testCompleted signal."""
        comparator = Comparator(str(temp_workspace), files=comparator_files)

        assert hasattr(comparator, "testCompleted")
        # Signal signature: test number, passed, input, correct output, test output
        assert isinstance(comparator.testCompleted, Signal)


class TestComparatorCompilerFlags:
    """Test comparison-specific compiler flags."""

    def test_get_compiler_flags_returns_optimization_flags(
        self, temp_workspace, comparator_files, mock_compiler, mock_database
    ):
        """Should return comparison-specific compiler optimization flags."""
        comparator = Comparator(str(temp_workspace), files=comparator_files)

        flags = comparator._get_compiler_flags()

        assert isinstance(flags, list)
        assert "-O2" in flags  # Level 2 optimization
        assert "-march=native" in flags  # CPU architecture optimization
        assert "-mtune=native" in flags  # CPU tuning
        assert "-pipe" in flags  # Use pipes
        assert "-std=c++17" in flags  # Modern C++
        assert "-Wall" in flags  # Warnings

    def test_get_compiler_flags_order_and_completeness(
        self, temp_workspace, comparator_files, mock_compiler, mock_database
    ):
        """Should return all required flags in correct order."""
        comparator = Comparator(str(temp_workspace), files=comparator_files)

        flags = comparator._get_compiler_flags()

        expected_flags = [
            "-O2",
            "-march=native",
            "-mtune=native",
            "-pipe",
            "-std=c++17",
            "-Wall",
        ]
        assert flags == expected_flags


class TestComparatorWorkerCreation:
    """Test comparison test worker creation."""

    @patch("src.app.core.tools.comparator.ComparisonTestWorker")
    def test_create_test_worker_returns_comparison_worker(
        self,
        mock_worker_class,
        temp_workspace,
        comparator_files,
        mock_compiler,
        mock_database,
    ):
        """Should create ComparisonTestWorker with correct parameters."""
        comparator = Comparator(str(temp_workspace), files=comparator_files)
        mock_compiler.get_execution_command.side_effect = lambda name: f"./{name}"

        worker = comparator._create_test_worker(test_count=10, max_workers=4)

        # Verify ComparisonTestWorker was instantiated
        mock_worker_class.assert_called_once()
        call_args = mock_worker_class.call_args

        # Check positional arguments
        assert call_args[0][0] == str(temp_workspace)  # workspace_dir
        assert call_args[0][2] == 10  # test_count
        assert call_args[0][3] == 4  # max_workers

        # Check execution_commands keyword argument
        assert "execution_commands" in call_args[1]
        execution_cmds = call_args[1]["execution_commands"]
        assert "generator" in execution_cmds
        assert "test" in execution_cmds
        assert "correct" in execution_cmds

    @patch("src.app.core.tools.comparator.ComparisonTestWorker")
    def test_create_test_worker_includes_execution_commands(
        self,
        mock_worker_class,
        temp_workspace,
        comparator_files,
        mock_compiler,
        mock_database,
    ):
        """Should pass execution commands from compiler."""
        comparator = Comparator(str(temp_workspace), files=comparator_files)
        mock_compiler.get_execution_command.side_effect = (
            lambda name: f"python {name}.py"
        )

        worker = comparator._create_test_worker(test_count=5)

        call_args = mock_worker_class.call_args
        execution_cmds = call_args[1]["execution_commands"]

        # Verify execution commands for all three files
        assert execution_cmds["generator"] == "python generator.py"
        assert execution_cmds["test"] == "python test.py"
        assert execution_cmds["correct"] == "python correct.py"

    @patch("src.app.core.tools.comparator.ComparisonTestWorker")
    def test_create_test_worker_with_default_max_workers(
        self,
        mock_worker_class,
        temp_workspace,
        comparator_files,
        mock_compiler,
        mock_database,
    ):
        """Should handle None max_workers parameter."""
        comparator = Comparator(str(temp_workspace), files=comparator_files)

        worker = comparator._create_test_worker(test_count=20, max_workers=None)

        call_args = mock_worker_class.call_args
        assert call_args[0][3] is None  # max_workers


class TestComparatorSignalConnections:
    """Test comparison-specific signal connections."""

    def test_connect_worker_signals_connects_test_completed(
        self, temp_workspace, comparator_files, mock_compiler, mock_database
    ):
        """Should connect comparison-specific testCompleted signal."""
        comparator = Comparator(str(temp_workspace), files=comparator_files)

        mock_worker = MagicMock()
        mock_worker.testCompleted = MagicMock()
        mock_worker.testStarted = MagicMock()
        mock_worker.allTestsCompleted = MagicMock()

        comparator._connect_worker_signals(mock_worker)

        # Verify testCompleted signal was connected
        mock_worker.testCompleted.connect.assert_called_once()

    def test_connect_worker_signals_calls_parent(
        self, temp_workspace, comparator_files, mock_compiler, mock_database
    ):
        """Should call parent BaseRunner signal connection."""
        comparator = Comparator(str(temp_workspace), files=comparator_files)

        mock_worker = MagicMock()
        mock_worker.testCompleted = MagicMock()
        mock_worker.testStarted = MagicMock()
        mock_worker.allTestsCompleted = MagicMock()

        # Check that super()._connect_worker_signals is called by verifying testStarted connection
        comparator._connect_worker_signals(mock_worker)

        # Parent should have connected testStarted signal
        mock_worker.testStarted.connect.assert_called()

    def test_connect_worker_signals_handles_missing_signal(
        self, temp_workspace, comparator_files, mock_compiler, mock_database
    ):
        """Should handle worker without testCompleted signal gracefully."""
        comparator = Comparator(str(temp_workspace), files=comparator_files)

        mock_worker = MagicMock()
        mock_worker.testStarted = MagicMock()
        mock_worker.allTestsCompleted = MagicMock()
        # No testCompleted attribute
        del mock_worker.testCompleted

        # Should not raise exception
        comparator._connect_worker_signals(mock_worker)


class TestComparatorResultCreation:
    """Test comparison test result creation and analysis."""

    def test_create_test_result_returns_test_result_object(
        self, temp_workspace, comparator_files, mock_compiler, mock_database
    ):
        """Should create TestResult object with comparison data."""
        comparator = Comparator(str(temp_workspace), files=comparator_files)
        comparator.test_count = 2  # Set test_count for analysis

        test_results = [
            {
                "test_number": 1,
                "passed": True,
                "generator_time": 0.1,
                "test_time": 0.2,
                "correct_time": 0.15,
                "comparison_time": 0.05,
            },
            {
                "test_number": 2,
                "passed": False,
                "error_details": "Output mismatch",
                "generator_time": 0.1,
                "test_time": 0.2,
                "correct_time": 0.15,
                "comparison_time": 0.05,
            },
        ]

        result = comparator._create_test_result(
            all_passed=False,
            test_results=test_results,
            passed_tests=1,
            failed_tests=1,
            total_time=1.5,
        )

        assert isinstance(result, TestResult)
        assert result.test_type == "comparison"
        assert result.test_count == 2
        assert result.passed_tests == 1
        assert result.failed_tests == 1
        assert result.total_time == 1.5

    def test_create_test_result_includes_comparison_summary(
        self, temp_workspace, comparator_files, mock_compiler, mock_database
    ):
        """Should include detailed comparison summary in mismatch_analysis."""
        comparator = Comparator(str(temp_workspace), files=comparator_files)
        comparator.test_count = 4  # Set test_count for analysis

        test_results = [
            {
                "test_number": 1,
                "passed": True,
                "generator_time": 0.1,
                "test_time": 0.2,
                "correct_time": 0.15,
                "comparison_time": 0.05,
            },
            {
                "test_number": 2,
                "passed": False,
                "generator_time": 0.1,
                "test_time": 0.2,
                "correct_time": 0.15,
                "comparison_time": 0.05,
            },  # Mismatch without error_details
            {
                "test_number": 3,
                "passed": False,
                "error_details": "Generator failed",
                "generator_time": 0,
                "test_time": 0,
                "correct_time": 0,
                "comparison_time": 0,
            },
            {
                "test_number": 4,
                "passed": False,
                "error_details": "Timeout",
                "generator_time": 0,
                "test_time": 0,
                "correct_time": 0,
                "comparison_time": 0,
            },
        ]

        result = comparator._create_test_result(
            all_passed=False,
            test_results=test_results,
            passed_tests=1,
            failed_tests=3,
            total_time=2.0,
        )

        analysis = json.loads(result.mismatch_analysis)

        assert "comparison_summary" in analysis
        summary = analysis["comparison_summary"]
        assert summary["matching_outputs"] == 1
        assert summary["mismatched_outputs"] == 1  # Only test 2 (no error_details)
        assert summary["generator_failures"] == 1
        assert summary["timeouts"] == 1

    def test_create_test_result_calculates_execution_times(
        self, temp_workspace, comparator_files, mock_compiler, mock_database
    ):
        """Should calculate average execution times."""
        comparator = Comparator(str(temp_workspace), files=comparator_files)
        comparator.test_count = 2  # Set test_count for analysis

        test_results = [
            {
                "test_number": 1,
                "passed": True,
                "generator_time": 0.1,
                "test_time": 0.3,
                "correct_time": 0.2,
                "comparison_time": 0.1,
            },
            {
                "test_number": 2,
                "passed": True,
                "generator_time": 0.2,
                "test_time": 0.4,
                "correct_time": 0.3,
                "comparison_time": 0.2,
            },
        ]

        result = comparator._create_test_result(
            all_passed=True,
            test_results=test_results,
            passed_tests=2,
            failed_tests=0,
            total_time=2.0,
        )

        analysis = json.loads(result.mismatch_analysis)

        assert "execution_times" in analysis
        times = analysis["execution_times"]
        assert pytest.approx(times["avg_generator"], 0.01) == 0.15  # (0.1 + 0.2) / 2
        assert pytest.approx(times["avg_test"], 0.01) == 0.35  # (0.3 + 0.4) / 2
        assert pytest.approx(times["avg_correct"], 0.01) == 0.25  # (0.2 + 0.3) / 2
        assert pytest.approx(times["avg_comparison"], 0.01) == 0.15  # (0.1 + 0.2) / 2

    def test_create_test_result_includes_failed_tests(
        self, temp_workspace, comparator_files, mock_compiler, mock_database
    ):
        """Should include details of failed tests."""
        comparator = Comparator(str(temp_workspace), files=comparator_files)

        test_results = [
            {
                "test_number": 1,
                "passed": True,
                "generator_time": 0.1,
                "test_time": 0.2,
                "correct_time": 0.15,
                "comparison_time": 0.05,
            },
            {
                "test_number": 2,
                "passed": False,
                "error_details": "Timeout",
                "generator_time": 0,
                "test_time": 0,
                "correct_time": 0,
                "comparison_time": 0,
            },
        ]

        result = comparator._create_test_result(
            all_passed=False,
            test_results=test_results,
            passed_tests=1,
            failed_tests=1,
            total_time=1.5,
        )

        analysis = json.loads(result.mismatch_analysis)

        assert "failed_tests" in analysis
        failed = analysis["failed_tests"]
        assert len(failed) == 1
        assert failed[0]["test_number"] == 2
        assert failed[0]["error_details"] == "Timeout"

    def test_create_test_result_creates_files_snapshot(
        self, temp_workspace, comparator_files, mock_compiler, mock_database
    ):
        """Should create snapshot of test files."""
        comparator = Comparator(str(temp_workspace), files=comparator_files)

        test_results = [
            {
                "test_number": 1,
                "passed": True,
                "generator_time": 0.1,
                "test_time": 0.2,
                "correct_time": 0.15,
                "comparison_time": 0.05,
            }
        ]

        result = comparator._create_test_result(
            all_passed=True,
            test_results=test_results,
            passed_tests=1,
            failed_tests=0,
            total_time=1.0,
        )

        assert result.files_snapshot is not None
        snapshot = json.loads(result.files_snapshot)
        assert isinstance(snapshot, dict)


class TestComparatorPublicAPI:
    """Test public API methods."""

    def test_run_stress_test_calls_base_run_tests(
        self, temp_workspace, comparator_files, mock_compiler, mock_database
    ):
        """Should call BaseRunner.run_tests with correct parameters."""
        comparator = Comparator(str(temp_workspace), files=comparator_files)

        with patch.object(comparator, "run_tests") as mock_run:
            comparator.run_stress_test(test_count=100, max_workers=8)

            mock_run.assert_called_once_with(100, max_workers=8)

    def test_run_stress_test_with_default_max_workers(
        self, temp_workspace, comparator_files, mock_compiler, mock_database
    ):
        """Should handle None max_workers."""
        comparator = Comparator(str(temp_workspace), files=comparator_files)

        with patch.object(comparator, "run_tests") as mock_run:
            comparator.run_stress_test(test_count=50)

            mock_run.assert_called_once_with(50, max_workers=None)

    def test_run_comparison_test_calls_base_run_tests(
        self, temp_workspace, comparator_files, mock_compiler, mock_database
    ):
        """Should call BaseRunner.run_tests with correct parameters."""
        comparator = Comparator(str(temp_workspace), files=comparator_files)

        with patch.object(comparator, "run_tests") as mock_run:
            comparator.run_comparison_test(test_count=200, max_workers=16)

            mock_run.assert_called_once_with(200, max_workers=16)

    def test_run_comparison_test_modern_api(
        self, temp_workspace, comparator_files, mock_compiler, mock_database
    ):
        """Should provide modern API alongside legacy run_stress_test."""
        comparator = Comparator(str(temp_workspace), files=comparator_files)

        with patch.object(comparator, "run_tests") as mock_run:
            comparator.run_comparison_test(test_count=75)

            mock_run.assert_called_once_with(75, max_workers=None)

    def test_backward_compatibility_with_stress_test(
        self, temp_workspace, comparator_files, mock_compiler, mock_database
    ):
        """Should maintain backward compatibility with run_stress_test API."""
        comparator = Comparator(str(temp_workspace), files=comparator_files)

        # Both methods should work identically
        with patch.object(comparator, "run_tests") as mock_run:
            comparator.run_stress_test(test_count=10, max_workers=2)
            call1 = mock_run.call_args

            mock_run.reset_mock()

            comparator.run_comparison_test(test_count=10, max_workers=2)
            call2 = mock_run.call_args

            assert call1 == call2


class TestComparatorEdgeCases:
    """Test edge cases and error handling."""

    def test_create_test_result_with_empty_results(
        self, temp_workspace, comparator_files, mock_compiler, mock_database
    ):
        """Should handle empty test results gracefully."""
        comparator = Comparator(str(temp_workspace), files=comparator_files)

        result = comparator._create_test_result(
            all_passed=True,
            test_results=[],
            passed_tests=0,
            failed_tests=0,
            total_time=0.0,
        )

        assert isinstance(result, TestResult)
        analysis = json.loads(result.mismatch_analysis)

        # Average times should be 0 for empty results
        assert analysis["execution_times"]["avg_generator"] == 0
        assert analysis["execution_times"]["avg_test"] == 0
        assert analysis["execution_times"]["avg_correct"] == 0

    def test_create_test_result_with_all_failures(
        self, temp_workspace, comparator_files, mock_compiler, mock_database
    ):
        """Should handle all tests failing."""
        comparator = Comparator(str(temp_workspace), files=comparator_files)

        test_results = [
            {
                "test_number": 1,
                "passed": False,
                "error_details": "Failed",
                "generator_time": 0,
                "test_time": 0,
                "correct_time": 0,
                "comparison_time": 0,
            },
            {
                "test_number": 2,
                "passed": False,
                "error_details": "Failed",
                "generator_time": 0,
                "test_time": 0,
                "correct_time": 0,
                "comparison_time": 0,
            },
        ]

        result = comparator._create_test_result(
            all_passed=False,
            test_results=test_results,
            passed_tests=0,
            failed_tests=2,
            total_time=1.0,
        )

        analysis = json.loads(result.mismatch_analysis)
        assert analysis["comparison_summary"]["matching_outputs"] == 0
        assert len(analysis["failed_tests"]) == 2


# Import Path for fixtures
from pathlib import Path
