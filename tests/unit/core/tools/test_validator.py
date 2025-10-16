"""
Test suite for ValidatorRunner class.

Tests verify the validation testing workflow, including:
- Initialization with multi-language support and nested file structure
- Worker creation with validation-specific parameters
- Signal connections for validator progress
- Test result creation with validation exit code analysis
- Public API methods (run_validation_test)
"""

import json
from datetime import datetime
from pathlib import Path
from unittest.mock import MagicMock, Mock, call, patch

import pytest
from PySide6.QtCore import Signal

from src.app.core.tools.validator import ValidatorRunner
from src.app.persistence.database.models import TestResult


@pytest.fixture
def validator_files(temp_workspace):
    """Create validator file paths for testing."""
    validator_dir = temp_workspace / "validator"
    validator_dir.mkdir(parents=True, exist_ok=True)

    files = {
        "generator": str(validator_dir / "generator.cpp"),
        "test": str(validator_dir / "test.cpp"),
        "validator": str(validator_dir / "validator.cpp"),
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
            "test": "/path/to/test",
            "validator": "/path/to/validator",
        }
        compiler_instance.get_execution_command.side_effect = lambda name: f"./{name}"
        mock.return_value = compiler_instance
        yield compiler_instance


@pytest.fixture
def mock_database():
    """Create mock database manager for testing."""
    with patch("src.app.core.tools.base.base_runner.DatabaseManager") as mock:
        db_instance = MagicMock()

        # Mock create_files_snapshot to return a proper mock with to_json() method
        snapshot_mock = MagicMock()
        snapshot_mock.to_json.return_value = json.dumps(
            {"files": {}, "test_type": "validator", "primary_language": "cpp"}
        )
        mock.create_files_snapshot.return_value = snapshot_mock

        mock.return_value = db_instance
        yield db_instance


class TestValidatorInitialization:
    """Test ValidatorRunner initialization and setup."""

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

            validator = ValidatorRunner(str(temp_workspace))

            assert validator.workspace_dir == str(temp_workspace)
            assert validator.test_type == "validator"
            # Verify get_workspace_file_path called for each file
            assert mock_path.call_count == 3

    def test_init_with_custom_files(
        self, temp_workspace, validator_files, mock_compiler, mock_database
    ):
        """Should accept custom file paths."""
        validator = ValidatorRunner(str(temp_workspace), files=validator_files)

        assert validator.workspace_dir == str(temp_workspace)
        assert validator.test_type == "validator"

    def test_init_with_config(
        self, temp_workspace, validator_files, mock_compiler, mock_database
    ):
        """Should accept configuration dictionary."""
        config = {"language": "java", "timeout": 10.0, "max_memory": 1024}

        validator = ValidatorRunner(
            str(temp_workspace), files=validator_files, config=config
        )

        assert validator.workspace_dir == str(temp_workspace)

    def test_init_inherits_from_base_runner(
        self, temp_workspace, validator_files, mock_compiler, mock_database
    ):
        """Should properly inherit from BaseRunner."""
        from src.app.core.tools.base.base_runner import BaseRunner

        validator = ValidatorRunner(str(temp_workspace), files=validator_files)

        assert isinstance(validator, BaseRunner)

    def test_init_defines_test_completed_signal(
        self, temp_workspace, validator_files, mock_compiler, mock_database
    ):
        """Should define validation-specific testCompleted signal."""
        validator = ValidatorRunner(str(temp_workspace), files=validator_files)

        assert hasattr(validator, "testCompleted")
        # Signal signature: test number, passed, input, test_output, validation_message,
        # error_details, validator_exit_code, exec_time, memory
        assert isinstance(validator.testCompleted, Signal)


class TestValidatorWorkerCreation:
    """Test validation test worker creation."""

    @patch("src.app.core.tools.validator.ValidatorTestWorker")
    def test_create_test_worker_returns_validator_worker(
        self,
        mock_worker_class,
        temp_workspace,
        validator_files,
        mock_compiler,
        mock_database,
    ):
        """Should create ValidatorTestWorker with correct parameters."""
        validator = ValidatorRunner(str(temp_workspace), files=validator_files)
        mock_compiler.get_execution_command.side_effect = lambda name: f"./{name}"

        worker = validator._create_test_worker(test_count=20, max_workers=8)

        # Verify ValidatorTestWorker was instantiated
        mock_worker_class.assert_called_once()
        call_args = mock_worker_class.call_args

        # Check positional arguments
        assert call_args[0][0] == str(temp_workspace)  # workspace_dir
        assert call_args[0][2] == 20  # test_count
        assert call_args[0][3] == 8  # max_workers

        # Check execution_commands keyword argument
        assert "execution_commands" in call_args[1]
        execution_cmds = call_args[1]["execution_commands"]
        assert "generator" in execution_cmds
        assert "test" in execution_cmds
        assert "validator" in execution_cmds

    @patch("src.app.core.tools.validator.ValidatorTestWorker")
    def test_create_test_worker_includes_execution_commands(
        self,
        mock_worker_class,
        temp_workspace,
        validator_files,
        mock_compiler,
        mock_database,
    ):
        """Should pass execution commands from compiler."""
        validator = ValidatorRunner(str(temp_workspace), files=validator_files)
        mock_compiler.get_execution_command.side_effect = (
            lambda name: f"java {name}.class"
        )

        worker = validator._create_test_worker(test_count=15)

        call_args = mock_worker_class.call_args
        execution_cmds = call_args[1]["execution_commands"]

        # Verify execution commands for all three files
        assert execution_cmds["generator"] == "java generator.class"
        assert execution_cmds["test"] == "java test.class"
        assert execution_cmds["validator"] == "java validator.class"

    @patch("src.app.core.tools.validator.ValidatorTestWorker")
    def test_create_test_worker_with_default_max_workers(
        self,
        mock_worker_class,
        temp_workspace,
        validator_files,
        mock_compiler,
        mock_database,
    ):
        """Should handle None max_workers parameter."""
        validator = ValidatorRunner(str(temp_workspace), files=validator_files)

        worker = validator._create_test_worker(test_count=30, max_workers=None)

        call_args = mock_worker_class.call_args
        assert call_args[0][3] is None  # max_workers


class TestValidatorSignalConnections:
    """Test validation-specific signal connections."""

    def test_connect_worker_signals_connects_test_completed(
        self, temp_workspace, validator_files, mock_compiler, mock_database
    ):
        """Should connect validation-specific testCompleted signal."""
        validator = ValidatorRunner(str(temp_workspace), files=validator_files)

        mock_worker = MagicMock()
        mock_worker.testCompleted = MagicMock()
        mock_worker.testStarted = MagicMock()
        mock_worker.allTestsCompleted = MagicMock()

        validator._connect_worker_signals(mock_worker)

        # Verify testCompleted signal was connected
        mock_worker.testCompleted.connect.assert_called_once()

    def test_connect_worker_signals_calls_parent(
        self, temp_workspace, validator_files, mock_compiler, mock_database
    ):
        """Should call parent BaseRunner signal connection."""
        validator = ValidatorRunner(str(temp_workspace), files=validator_files)

        mock_worker = MagicMock()
        mock_worker.testCompleted = MagicMock()
        mock_worker.testStarted = MagicMock()
        mock_worker.allTestsCompleted = MagicMock()

        # Check that super()._connect_worker_signals is called by verifying testStarted connection
        validator._connect_worker_signals(mock_worker)

        # Parent should have connected testStarted signal
        mock_worker.testStarted.connect.assert_called()

    def test_connect_worker_signals_handles_missing_signal(
        self, temp_workspace, validator_files, mock_compiler, mock_database
    ):
        """Should handle worker without testCompleted signal gracefully."""
        validator = ValidatorRunner(str(temp_workspace), files=validator_files)

        mock_worker = MagicMock()
        mock_worker.testStarted = MagicMock()
        mock_worker.allTestsCompleted = MagicMock()
        # No testCompleted attribute
        del mock_worker.testCompleted

        # Should not raise exception
        validator._connect_worker_signals(mock_worker)


class TestValidatorResultCreation:
    """Test validation test result creation and analysis."""

    def test_create_test_result_returns_test_result_object(
        self, temp_workspace, validator_files, mock_compiler, mock_database
    ):
        """Should create TestResult object with validation data."""
        validator = ValidatorRunner(str(temp_workspace), files=validator_files)
        validator.test_count = 2  # Set test_count for analysis

        test_results = [
            {
                "test_number": 1,
                "passed": True,
                "validator_exit_code": 0,
                "generator_time": 0.1,
                "test_time": 0.2,
                "validator_time": 0.15,
            },
            {
                "test_number": 2,
                "passed": False,
                "validator_exit_code": 1,
                "generator_time": 0.1,
                "test_time": 0.2,
                "validator_time": 0.15,
            },
        ]

        result = validator._create_test_result(
            all_passed=False,
            test_results=test_results,
            passed_tests=1,
            failed_tests=1,
            total_time=2.0,
        )

        assert isinstance(result, TestResult)
        assert result.test_type == "validator"
        assert result.test_count == 2
        assert result.passed_tests == 1
        assert result.failed_tests == 1
        assert result.total_time == 2.0

    def test_create_test_result_includes_validation_summary(
        self, temp_workspace, validator_files, mock_compiler, mock_database
    ):
        """Should include detailed validation exit code summary."""
        validator = ValidatorRunner(str(temp_workspace), files=validator_files)
        validator.test_count = 6  # Set test_count for analysis

        test_results = [
            {
                "test_number": 1,
                "validator_exit_code": 0,
                "generator_time": 0.1,
                "test_time": 0.2,
                "validator_time": 0.1,
            },  # Correct
            {
                "test_number": 2,
                "validator_exit_code": 1,
                "generator_time": 0.1,
                "test_time": 0.2,
                "validator_time": 0.1,
            },  # Wrong Answer
            {
                "test_number": 3,
                "validator_exit_code": 2,
                "generator_time": 0.1,
                "test_time": 0.2,
                "validator_time": 0.1,
            },  # Presentation Error
            {
                "test_number": 4,
                "validator_exit_code": 5,
                "generator_time": 0.1,
                "test_time": 0.2,
                "validator_time": 0.1,
            },  # Validator Error
            {
                "test_number": 5,
                "validator_exit_code": -2,
                "generator_time": 0.1,
                "test_time": 0.2,
                "validator_time": 0,
            },  # Timeout
            {
                "test_number": 6,
                "validator_exit_code": -3,
                "generator_time": 0.1,
                "test_time": 0.2,
                "validator_time": 0,
            },  # System Error
        ]

        result = validator._create_test_result(
            all_passed=False,
            test_results=test_results,
            passed_tests=1,
            failed_tests=5,
            total_time=5.0,
        )

        analysis = json.loads(result.mismatch_analysis)

        assert "validation_summary" in analysis
        summary = analysis["validation_summary"]
        assert summary["correct_outputs"] == 1
        assert summary["wrong_answers"] == 1
        assert summary["presentation_errors"] == 1
        assert summary["validator_errors"] == 1
        assert summary["timeouts"] == 1
        assert summary["system_errors"] == 1

    def test_create_test_result_calculates_execution_times(
        self, temp_workspace, validator_files, mock_compiler, mock_database
    ):
        """Should calculate average execution times for validator workflow."""
        validator = ValidatorRunner(str(temp_workspace), files=validator_files)
        validator.test_count = 2  # Set test_count for analysis

        test_results = [
            {
                "test_number": 1,
                "passed": True,
                "validator_exit_code": 0,
                "generator_time": 0.1,
                "test_time": 0.3,
                "validator_time": 0.2,
            },
            {
                "test_number": 2,
                "passed": True,
                "validator_exit_code": 0,
                "generator_time": 0.2,
                "test_time": 0.4,
                "validator_time": 0.3,
            },
        ]

        result = validator._create_test_result(
            all_passed=True,
            test_results=test_results,
            passed_tests=2,
            failed_tests=0,
            total_time=2.5,
        )

        analysis = json.loads(result.mismatch_analysis)

        assert "execution_times" in analysis
        times = analysis["execution_times"]
        assert pytest.approx(times["avg_generator"], 0.01) == 0.15  # (0.1 + 0.2) / 2
        assert pytest.approx(times["avg_test"], 0.01) == 0.35  # (0.3 + 0.4) / 2
        assert pytest.approx(times["avg_validator"], 0.01) == 0.25  # (0.2 + 0.3) / 2

    def test_create_test_result_includes_failed_tests(
        self, temp_workspace, validator_files, mock_compiler, mock_database
    ):
        """Should include details of failed tests."""
        validator = ValidatorRunner(str(temp_workspace), files=validator_files)

        test_results = [
            {
                "test_number": 1,
                "passed": True,
                "validator_exit_code": 0,
                "generator_time": 0.1,
                "test_time": 0.2,
                "validator_time": 0.15,
            },
            {
                "test_number": 2,
                "passed": False,
                "validator_exit_code": 1,
                "error_details": "Wrong Answer",
                "generator_time": 0.1,
                "test_time": 0.2,
                "validator_time": 0.15,
            },
        ]

        result = validator._create_test_result(
            all_passed=False,
            test_results=test_results,
            passed_tests=1,
            failed_tests=1,
            total_time=2.0,
        )

        analysis = json.loads(result.mismatch_analysis)

        assert "failed_tests" in analysis
        failed = analysis["failed_tests"]
        assert len(failed) == 1
        assert failed[0]["test_number"] == 2
        assert failed[0]["validator_exit_code"] == 1

    def test_create_test_result_creates_files_snapshot(
        self, temp_workspace, validator_files, mock_compiler, mock_database
    ):
        """Should create snapshot of test files."""
        validator = ValidatorRunner(str(temp_workspace), files=validator_files)

        test_results = [
            {
                "test_number": 1,
                "passed": True,
                "validator_exit_code": 0,
                "generator_time": 0.1,
                "test_time": 0.2,
                "validator_time": 0.15,
            }
        ]

        result = validator._create_test_result(
            all_passed=True,
            test_results=test_results,
            passed_tests=1,
            failed_tests=0,
            total_time=1.5,
        )

        assert result.files_snapshot is not None
        snapshot = json.loads(result.files_snapshot)
        assert isinstance(snapshot, dict)


class TestValidatorPublicAPI:
    """Test public API methods."""

    def test_run_validation_test_calls_base_run_tests(
        self, temp_workspace, validator_files, mock_compiler, mock_database
    ):
        """Should call BaseRunner.run_tests with correct parameters."""
        validator = ValidatorRunner(str(temp_workspace), files=validator_files)

        with patch.object(validator, "run_tests") as mock_run:
            validator.run_validation_test(test_count=50, max_workers=4)

            mock_run.assert_called_once_with(50, max_workers=4)

    def test_run_validation_test_with_default_max_workers(
        self, temp_workspace, validator_files, mock_compiler, mock_database
    ):
        """Should handle None max_workers."""
        validator = ValidatorRunner(str(temp_workspace), files=validator_files)

        with patch.object(validator, "run_tests") as mock_run:
            validator.run_validation_test(test_count=100)

            mock_run.assert_called_once_with(100, max_workers=None)

    def test_run_validation_test_maintains_api_compatibility(
        self, temp_workspace, validator_files, mock_compiler, mock_database
    ):
        """Should maintain original API for backward compatibility."""
        validator = ValidatorRunner(str(temp_workspace), files=validator_files)

        # Should be able to call with just test_count
        with patch.object(validator, "run_tests") as mock_run:
            validator.run_validation_test(25)

            mock_run.assert_called_once_with(25, max_workers=None)


class TestValidatorExitCodes:
    """Test validator exit code interpretation."""

    def test_exit_code_0_correct_output(
        self, temp_workspace, validator_files, mock_compiler, mock_database
    ):
        """Should recognize exit code 0 as correct output."""
        validator = ValidatorRunner(str(temp_workspace), files=validator_files)

        test_results = [
            {
                "test_number": 1,
                "validator_exit_code": 0,
                "generator_time": 0.1,
                "test_time": 0.2,
                "validator_time": 0.1,
            }
        ]

        result = validator._create_test_result(
            all_passed=True,
            test_results=test_results,
            passed_tests=1,
            failed_tests=0,
            total_time=0.4,
        )

        analysis = json.loads(result.mismatch_analysis)
        assert analysis["validation_summary"]["correct_outputs"] == 1

    def test_exit_code_1_wrong_answer(
        self, temp_workspace, validator_files, mock_compiler, mock_database
    ):
        """Should recognize exit code 1 as wrong answer."""
        validator = ValidatorRunner(str(temp_workspace), files=validator_files)

        test_results = [
            {
                "test_number": 1,
                "validator_exit_code": 1,
                "generator_time": 0.1,
                "test_time": 0.2,
                "validator_time": 0.1,
            }
        ]

        result = validator._create_test_result(
            all_passed=False,
            test_results=test_results,
            passed_tests=0,
            failed_tests=1,
            total_time=0.4,
        )

        analysis = json.loads(result.mismatch_analysis)
        assert analysis["validation_summary"]["wrong_answers"] == 1

    def test_exit_code_2_presentation_error(
        self, temp_workspace, validator_files, mock_compiler, mock_database
    ):
        """Should recognize exit code 2 as presentation error."""
        validator = ValidatorRunner(str(temp_workspace), files=validator_files)

        test_results = [
            {
                "test_number": 1,
                "validator_exit_code": 2,
                "generator_time": 0.1,
                "test_time": 0.2,
                "validator_time": 0.1,
            }
        ]

        result = validator._create_test_result(
            all_passed=False,
            test_results=test_results,
            passed_tests=0,
            failed_tests=1,
            total_time=0.4,
        )

        analysis = json.loads(result.mismatch_analysis)
        assert analysis["validation_summary"]["presentation_errors"] == 1

    def test_exit_code_high_validator_error(
        self, temp_workspace, validator_files, mock_compiler, mock_database
    ):
        """Should recognize exit codes > 2 as validator errors."""
        validator = ValidatorRunner(str(temp_workspace), files=validator_files)

        test_results = [
            {
                "test_number": 1,
                "validator_exit_code": 3,
                "generator_time": 0.1,
                "test_time": 0.2,
                "validator_time": 0.1,
            },
            {
                "test_number": 2,
                "validator_exit_code": 5,
                "generator_time": 0.1,
                "test_time": 0.2,
                "validator_time": 0.1,
            },
        ]

        result = validator._create_test_result(
            all_passed=False,
            test_results=test_results,
            passed_tests=0,
            failed_tests=2,
            total_time=0.8,
        )

        analysis = json.loads(result.mismatch_analysis)
        assert analysis["validation_summary"]["validator_errors"] == 2

    def test_exit_code_negative_2_timeout(
        self, temp_workspace, validator_files, mock_compiler, mock_database
    ):
        """Should recognize exit code -2 as timeout."""
        validator = ValidatorRunner(str(temp_workspace), files=validator_files)

        test_results = [
            {
                "test_number": 1,
                "validator_exit_code": -2,
                "generator_time": 0.1,
                "test_time": 0.2,
                "validator_time": 0,
            }
        ]

        result = validator._create_test_result(
            all_passed=False,
            test_results=test_results,
            passed_tests=0,
            failed_tests=1,
            total_time=5.0,
        )

        analysis = json.loads(result.mismatch_analysis)
        assert analysis["validation_summary"]["timeouts"] == 1

    def test_exit_code_negative_3_system_error(
        self, temp_workspace, validator_files, mock_compiler, mock_database
    ):
        """Should recognize exit code -3 as system error."""
        validator = ValidatorRunner(str(temp_workspace), files=validator_files)

        test_results = [
            {
                "test_number": 1,
                "validator_exit_code": -3,
                "generator_time": 0.1,
                "test_time": 0.2,
                "validator_time": 0,
            }
        ]

        result = validator._create_test_result(
            all_passed=False,
            test_results=test_results,
            passed_tests=0,
            failed_tests=1,
            total_time=0.5,
        )

        analysis = json.loads(result.mismatch_analysis)
        assert analysis["validation_summary"]["system_errors"] == 1


class TestValidatorEdgeCases:
    """Test edge cases and error handling."""

    def test_create_test_result_with_empty_results(
        self, temp_workspace, validator_files, mock_compiler, mock_database
    ):
        """Should handle empty test results gracefully."""
        validator = ValidatorRunner(str(temp_workspace), files=validator_files)

        result = validator._create_test_result(
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
        assert analysis["execution_times"]["avg_validator"] == 0

    def test_create_test_result_with_all_failures(
        self, temp_workspace, validator_files, mock_compiler, mock_database
    ):
        """Should handle all tests failing."""
        validator = ValidatorRunner(str(temp_workspace), files=validator_files)

        test_results = [
            {
                "test_number": 1,
                "passed": False,
                "validator_exit_code": 1,
                "generator_time": 0.1,
                "test_time": 0.2,
                "validator_time": 0.15,
            },
            {
                "test_number": 2,
                "passed": False,
                "validator_exit_code": 2,
                "generator_time": 0.1,
                "test_time": 0.2,
                "validator_time": 0.15,
            },
        ]

        result = validator._create_test_result(
            all_passed=False,
            test_results=test_results,
            passed_tests=0,
            failed_tests=2,
            total_time=1.5,
        )

        analysis = json.loads(result.mismatch_analysis)
        assert analysis["validation_summary"]["correct_outputs"] == 0
        assert len(analysis["failed_tests"]) == 2

    def test_create_test_result_with_mixed_exit_codes(
        self, temp_workspace, validator_files, mock_compiler, mock_database
    ):
        """Should correctly categorize mixed validator exit codes."""
        validator = ValidatorRunner(str(temp_workspace), files=validator_files)

        test_results = [
            {
                "test_number": 1,
                "validator_exit_code": 0,
                "generator_time": 0.1,
                "test_time": 0.2,
                "validator_time": 0.1,
            },
            {
                "test_number": 2,
                "validator_exit_code": 1,
                "generator_time": 0.1,
                "test_time": 0.2,
                "validator_time": 0.1,
            },
            {
                "test_number": 3,
                "validator_exit_code": 2,
                "generator_time": 0.1,
                "test_time": 0.2,
                "validator_time": 0.1,
            },
            {
                "test_number": 4,
                "validator_exit_code": 0,
                "generator_time": 0.1,
                "test_time": 0.2,
                "validator_time": 0.1,
            },
        ]

        result = validator._create_test_result(
            all_passed=False,
            test_results=test_results,
            passed_tests=2,
            failed_tests=2,
            total_time=2.0,
        )

        analysis = json.loads(result.mismatch_analysis)
        summary = analysis["validation_summary"]

        assert summary["correct_outputs"] == 2
        assert summary["wrong_answers"] == 1
        assert summary["presentation_errors"] == 1
        assert summary["validator_errors"] == 0
        assert summary["timeouts"] == 0
        assert summary["system_errors"] == 0
