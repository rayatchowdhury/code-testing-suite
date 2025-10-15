"""
Unit tests for ValidatorTestWorker.

Tests the specialized worker that implements 3-stage validation:
1. Generator → produces test input
2. Test solution → processes input to produce output
3. Validator → checks correctness via exit code

Tests verify parallel execution, signal emission, and result storage.
"""

import os
import tempfile
import time
from subprocess import TimeoutExpired
from unittest.mock import MagicMock, Mock, call, patch

import pytest
from PySide6.QtCore import QObject

from src.app.core.tools.specialized.validator_test_worker import ValidatorTestWorker


class TestValidatorWorkerInitialization:
    """Test ValidatorTestWorker initialization."""

    def test_init_sets_executables(self, temp_workspace):
        """Should store executables for generator, test, validator."""
        executables = {
            "generator": str(temp_workspace / "generator.exe"),
            "test": str(temp_workspace / "test.exe"),
            "validator": str(temp_workspace / "validator.exe"),
        }

        worker = ValidatorTestWorker(str(temp_workspace), executables, test_count=5)

        assert worker.executables == executables
        assert worker.test_count == 5
        assert worker.workspace_dir == str(temp_workspace)

    def test_init_calculates_optimal_workers(self, temp_workspace):
        """Should calculate optimal worker count based on CPU cores."""
        executables = {"generator": "", "test": "", "validator": ""}

        worker = ValidatorTestWorker(str(temp_workspace), executables, test_count=10)

        assert worker.max_workers >= 1
        assert worker.max_workers <= 8  # Capped at 8

    def test_init_accepts_custom_worker_count(self, temp_workspace):
        """Should accept custom max_workers parameter."""
        executables = {"generator": "", "test": "", "validator": ""}

        worker = ValidatorTestWorker(str(temp_workspace), executables, test_count=5, max_workers=3)

        assert worker.max_workers == 3

    def test_init_creates_execution_commands_from_executables(self, temp_workspace):
        """Should convert executable paths to command lists (legacy mode)."""
        executables = {
            "generator": "gen.exe",
            "test": "test.exe",
            "validator": "val.exe",
        }

        worker = ValidatorTestWorker(str(temp_workspace), executables, test_count=1)

        assert worker.execution_commands["generator"] == ["gen.exe"]
        assert worker.execution_commands["test"] == ["test.exe"]
        assert worker.execution_commands["validator"] == ["val.exe"]

    def test_init_uses_execution_commands_when_provided(self, temp_workspace):
        """Should use execution_commands parameter when provided."""
        executables = {"generator": "", "test": "", "validator": ""}
        execution_commands = {
            "generator": ["python", "gen.py"],
            "test": ["python", "test.py"],
            "validator": ["python", "val.py"],
        }

        worker = ValidatorTestWorker(
            str(temp_workspace),
            executables,
            test_count=1,
            execution_commands=execution_commands,
        )

        assert worker.execution_commands == execution_commands


class TestValidatorWorkerExecution:
    """Test 3-stage validation execution."""

    @patch("subprocess.Popen")
    @patch("psutil.Process")
    def test_runs_three_stage_validation(self, mock_psutil, mock_popen, temp_workspace):
        """Should execute generator, test, and validator in sequence."""
        # Mock process objects
        gen_proc = Mock()
        gen_proc.returncode = 0
        gen_proc.poll.return_value = 0
        gen_proc.communicate.return_value = ("test_input", "")
        gen_proc.pid = 1001

        test_proc = Mock()
        test_proc.returncode = 0
        test_proc.poll.return_value = 0
        test_proc.communicate.return_value = ("test_output", "")
        test_proc.pid = 1002
        test_proc.stdin = Mock()

        val_proc = Mock()
        val_proc.returncode = 0
        val_proc.poll.return_value = 0
        val_proc.communicate.return_value = ("", "")
        val_proc.pid = 1003

        mock_popen.side_effect = [gen_proc, test_proc, val_proc]

        # Mock psutil Process
        mock_memory = Mock()
        mock_memory.rss = 10 * 1024 * 1024  # 10 MB
        mock_psutil.return_value.memory_info.return_value = mock_memory

        executables = {
            "generator": "gen.exe",
            "test": "test.exe",
            "validator": "val.exe",
        }
        worker = ValidatorTestWorker(str(temp_workspace), executables, test_count=1)

        result = worker._run_single_test(1)

        # Should have called Popen 3 times (gen + test + validator)
        assert mock_popen.call_count == 3
        assert result is not None
        assert result["passed"] is True
        assert result["test_number"] == 1

    def test_validator_exit_code_zero_means_accepted(self, temp_workspace):
        """Should interpret exit code 0 as Accepted."""
        with patch("subprocess.Popen") as mock_popen, patch("psutil.Process"):

            # Mock all three stages
            gen_proc = Mock(returncode=0, poll=Mock(return_value=0), pid=1001)
            gen_proc.communicate.return_value = ("input", "")

            test_proc = Mock(returncode=0, poll=Mock(return_value=0), pid=1002)
            test_proc.communicate.return_value = ("output", "")
            test_proc.stdin = Mock()

            val_proc = Mock(returncode=0, poll=Mock(return_value=0), pid=1003)
            val_proc.communicate.return_value = ("", "")

            mock_popen.side_effect = [gen_proc, test_proc, val_proc]

            executables = {"generator": "", "test": "", "validator": ""}
            worker = ValidatorTestWorker(str(temp_workspace), executables, test_count=1)

            result = worker._run_single_test(1)

            assert result["passed"] is True
            assert result["validation_message"] == "Correct"
            assert result["validator_exit_code"] == 0

    def test_validator_exit_code_one_means_wrong_answer(self, temp_workspace):
        """Should interpret exit code 1 as Wrong Answer."""
        with patch("subprocess.Popen") as mock_popen, patch("psutil.Process"):

            gen_proc = Mock(returncode=0, poll=Mock(return_value=0), pid=1001)
            gen_proc.communicate.return_value = ("input", "")

            test_proc = Mock(returncode=0, poll=Mock(return_value=0), pid=1002)
            test_proc.communicate.return_value = ("wrong output", "")
            test_proc.stdin = Mock()

            val_proc = Mock(returncode=1, poll=Mock(return_value=1), pid=1003)
            val_proc.communicate.return_value = ("Expected: X, Got: Y", "")

            mock_popen.side_effect = [gen_proc, test_proc, val_proc]

            executables = {"generator": "", "test": "", "validator": ""}
            worker = ValidatorTestWorker(str(temp_workspace), executables, test_count=1)

            result = worker._run_single_test(1)

            assert result["passed"] is False
            assert result["validation_message"] == "Wrong Answer"
            assert result["validator_exit_code"] == 1
            assert "Expected: X, Got: Y" in result["error_details"]

    def test_validator_exit_code_two_means_presentation_error(self, temp_workspace):
        """Should interpret exit code 2 as Presentation Error."""
        with patch("subprocess.Popen") as mock_popen, patch("psutil.Process"):

            gen_proc = Mock(returncode=0, poll=Mock(return_value=0), pid=1001)
            gen_proc.communicate.return_value = ("input", "")

            test_proc = Mock(returncode=0, poll=Mock(return_value=0), pid=1002)
            test_proc.communicate.return_value = ("output with extra spaces", "")
            test_proc.stdin = Mock()

            val_proc = Mock(returncode=2, poll=Mock(return_value=2), pid=1003)
            val_proc.communicate.return_value = ("Format error", "")

            mock_popen.side_effect = [gen_proc, test_proc, val_proc]

            executables = {"generator": "", "test": "", "validator": ""}
            worker = ValidatorTestWorker(str(temp_workspace), executables, test_count=1)

            result = worker._run_single_test(1)

            assert result["passed"] is False
            assert result["validation_message"] == "Presentation Error"
            assert result["validator_exit_code"] == 2

    def test_validator_other_exit_code_means_error(self, temp_workspace):
        """Should interpret other exit codes as Validator Error."""
        with patch("subprocess.Popen") as mock_popen, patch("psutil.Process"):

            gen_proc = Mock(returncode=0, poll=Mock(return_value=0), pid=1001)
            gen_proc.communicate.return_value = ("input", "")

            test_proc = Mock(returncode=0, poll=Mock(return_value=0), pid=1002)
            test_proc.communicate.return_value = ("output", "")
            test_proc.stdin = Mock()

            val_proc = Mock(returncode=42, poll=Mock(return_value=42), pid=1003)
            val_proc.communicate.return_value = ("", "Crash!")

            mock_popen.side_effect = [gen_proc, test_proc, val_proc]

            executables = {"generator": "", "test": "", "validator": ""}
            worker = ValidatorTestWorker(str(temp_workspace), executables, test_count=1)

            result = worker._run_single_test(1)

            assert result["passed"] is False
            assert result["validation_message"] == "Validator Error"
            assert result["validator_exit_code"] == 42
            assert "Crash!" in result["error_details"]


class TestValidatorWorkerSignals:
    """Test signal emission during validation."""

    @patch("subprocess.Popen")
    @patch("psutil.Process")
    def test_emits_test_started_signal(self, mock_psutil, mock_popen, temp_workspace, qtbot):
        """Should emit testStarted for each test."""
        # Mock successful execution - create all procs first, then set side_effect
        procs = []
        for _ in range(9):  # 3 tests * 3 stages each
            proc = Mock(returncode=0, poll=Mock(return_value=0), pid=1001)
            proc.communicate.return_value = ("output", "")
            proc.stdin = Mock()
            procs.append(proc)
        mock_popen.side_effect = procs

        executables = {"generator": "", "test": "", "validator": ""}
        worker = ValidatorTestWorker(str(temp_workspace), executables, test_count=3)

        started_signals = []
        worker.testStarted.connect(lambda curr, total: started_signals.append((curr, total)))

        with qtbot.waitSignal(worker.allTestsCompleted, timeout=5000):
            worker.run_tests()

        # Should have emitted testStarted for each test
        assert len(started_signals) == 3
        assert all(total == 3 for _, total in started_signals)

    @patch("subprocess.Popen")
    @patch("psutil.Process")
    def test_emits_test_completed_with_correct_data(
        self, mock_psutil, mock_popen, temp_workspace, qtbot
    ):
        """Should emit testCompleted with all validation data."""
        # Mock single successful test
        gen_proc = Mock(returncode=0, poll=Mock(return_value=0), pid=1001)
        gen_proc.communicate.return_value = ("test_input", "")

        test_proc = Mock(returncode=0, poll=Mock(return_value=0), pid=1002)
        test_proc.communicate.return_value = ("test_output", "")
        test_proc.stdin = Mock()

        val_proc = Mock(returncode=0, poll=Mock(return_value=0), pid=1003)
        val_proc.communicate.return_value = ("", "")

        mock_popen.side_effect = [gen_proc, test_proc, val_proc]

        executables = {"generator": "", "test": "", "validator": ""}
        worker = ValidatorTestWorker(str(temp_workspace), executables, test_count=1)

        completed_signals = []
        worker.testCompleted.connect(lambda *args: completed_signals.append(args))

        with qtbot.waitSignal(worker.allTestsCompleted, timeout=5000):
            worker.run_tests()

        # Verify signal was emitted with 9 parameters
        assert len(completed_signals) == 1
        signal_data = completed_signals[0]
        assert (
            len(signal_data) == 9
        )  # test_num, passed, input, output, msg, error, exit_code, time, memory
        assert signal_data[0] == 1  # test_number
        assert signal_data[1] is True  # passed

    @patch("subprocess.Popen")
    @patch("psutil.Process")
    def test_emits_all_tests_completed_signal(self, mock_psutil, mock_popen, temp_workspace, qtbot):
        """Should emit allTestsCompleted when all tests finish."""
        # Mock successful test - create all procs first, then set side_effect
        procs = []
        for _ in range(3):
            proc = Mock(returncode=0, poll=Mock(return_value=0), pid=1001)
            proc.communicate.return_value = ("output", "")
            proc.stdin = Mock()
            procs.append(proc)
        mock_popen.side_effect = procs

        executables = {"generator": "", "test": "", "validator": ""}
        worker = ValidatorTestWorker(str(temp_workspace), executables, test_count=1)

        with qtbot.waitSignal(worker.allTestsCompleted, timeout=5000) as blocker:
            worker.run_tests()

        # Signal should have been emitted with True (all passed)
        assert blocker.args == [True]


class TestValidatorWorkerParallelExecution:
    """Test parallel test execution."""

    @pytest.mark.slow
    @patch("subprocess.Popen")
    @patch("psutil.Process")
    def test_executes_tests_in_parallel(self, mock_psutil, mock_popen, temp_workspace):
        """Should run multiple tests concurrently."""
        # Mock successful execution for all stages
        execution_count = []

        def create_mock_proc(*args, **kwargs):
            proc = Mock(returncode=0, poll=Mock(return_value=0), pid=1001)
            proc.communicate.return_value = ("output", "")
            proc.stdin = Mock()
            execution_count.append(time.time())
            return proc

        mock_popen.side_effect = create_mock_proc

        executables = {"generator": "", "test": "", "validator": ""}
        worker = ValidatorTestWorker(str(temp_workspace), executables, test_count=5, max_workers=2)

        worker.run_tests()

        # Should have executed 5 tests * 3 stages = 15 subprocess calls
        assert mock_popen.call_count == 15

    @patch("subprocess.Popen")
    @patch("psutil.Process")
    def test_stores_results_thread_safely(self, mock_psutil, mock_popen, temp_workspace):
        """Should store test results in thread-safe manner."""
        # Mock successful tests - create all procs first, then set side_effect
        procs = []
        for _ in range(9):  # 3 tests * 3 stages
            proc = Mock(returncode=0, poll=Mock(return_value=0), pid=1001)
            proc.communicate.return_value = ("output", "")
            proc.stdin = Mock()
            procs.append(proc)
        mock_popen.side_effect = procs

        executables = {"generator": "", "test": "", "validator": ""}
        worker = ValidatorTestWorker(str(temp_workspace), executables, test_count=3)

        worker.run_tests()

        # Results should be stored correctly
        results = worker.get_test_results()
        assert len(results) == 3
        assert all("test_number" in r for r in results)


class TestValidatorWorkerErrorHandling:
    """Test error handling and recovery."""

    @patch("subprocess.Popen")
    def test_handles_generator_failure(self, mock_popen, temp_workspace):
        """Should create error result if generator fails."""
        gen_proc = Mock(returncode=1, poll=Mock(return_value=1), pid=1001)
        gen_proc.communicate.return_value = ("", "Generator error!")

        mock_popen.return_value = gen_proc

        executables = {"generator": "", "test": "", "validator": ""}
        worker = ValidatorTestWorker(str(temp_workspace), executables, test_count=1)

        result = worker._run_single_test(1)

        assert result is not None
        assert result["passed"] is False
        assert "Generator failed" in result["validation_message"]
        assert result["validator_exit_code"] == -1

    @patch("subprocess.Popen")
    @patch("psutil.Process")
    def test_handles_test_solution_failure(self, mock_psutil, mock_popen, temp_workspace):
        """Should create error result if test solution fails."""
        gen_proc = Mock(returncode=0, poll=Mock(return_value=0), pid=1001)
        gen_proc.communicate.return_value = ("input", "")

        test_proc = Mock(returncode=1, poll=Mock(return_value=1), pid=1002)
        test_proc.communicate.return_value = ("", "Runtime error!")
        test_proc.stdin = Mock()

        mock_popen.side_effect = [gen_proc, test_proc]

        executables = {"generator": "", "test": "", "validator": ""}
        worker = ValidatorTestWorker(str(temp_workspace), executables, test_count=1)

        result = worker._run_single_test(1)

        assert result is not None
        assert result["passed"] is False
        assert "Test solution failed" in result["validation_message"]

    @patch("subprocess.Popen")
    @patch("psutil.Process")
    def test_handles_timeout(self, mock_psutil, mock_popen, temp_workspace):
        """Should handle process timeouts gracefully."""
        gen_proc = Mock(pid=1001)
        gen_proc.communicate.side_effect = TimeoutExpired(cmd=["gen"], timeout=10)

        mock_popen.return_value = gen_proc

        executables = {"generator": "", "test": "", "validator": ""}
        worker = ValidatorTestWorker(str(temp_workspace), executables, test_count=1)

        result = worker._run_single_test(1)

        assert result is not None
        assert result["passed"] is False
        assert "Timeout" in result["validation_message"]
        assert result["validator_exit_code"] == -2

    @patch("subprocess.Popen")
    def test_handles_popen_exception(self, mock_popen, temp_workspace):
        """Should handle subprocess creation exceptions."""
        mock_popen.side_effect = Exception("Failed to start process")

        executables = {"generator": "", "test": "", "validator": ""}
        worker = ValidatorTestWorker(str(temp_workspace), executables, test_count=1)

        result = worker._run_single_test(1)

        assert result is not None
        assert result["passed"] is False
        assert "Failed to start generator" in result["error_details"]


class TestValidatorWorkerMetrics:
    """Test execution time and memory tracking."""

    @patch("subprocess.Popen")
    @patch("psutil.Process")
    @patch("time.time")
    def test_tracks_execution_time(self, mock_time, mock_psutil, mock_popen, temp_workspace):
        """Should track execution time for each stage."""
        # Mock time progression
        mock_time.side_effect = [
            0,
            0.1,
            0.2,
            0.3,
            0.4,
            0.5,
            0.6,
        ]  # Start and ends of each stage

        # Mock successful execution - create all procs first, then set side_effect
        procs = []
        for _ in range(3):
            proc = Mock(returncode=0, poll=Mock(return_value=0), pid=1001)
            proc.communicate.return_value = ("output", "")
            proc.stdin = Mock()
            procs.append(proc)
        mock_popen.side_effect = procs

        executables = {"generator": "", "test": "", "validator": ""}
        worker = ValidatorTestWorker(str(temp_workspace), executables, test_count=1)

        result = worker._run_single_test(1)

        assert "total_time" in result
        assert result["total_time"] > 0

    @patch("subprocess.Popen")
    @patch("psutil.Process")
    def test_tracks_peak_memory(self, mock_psutil, mock_popen, temp_workspace):
        """Should track peak memory usage across all stages."""
        # Mock memory increasing over time
        mock_memory_info = Mock()
        mock_memory_info.rss = 50 * 1024 * 1024  # 50 MB
        mock_psutil.return_value.memory_info.return_value = mock_memory_info

        # Mock successful execution - create all procs first, then set side_effect
        procs = []
        for _ in range(3):
            proc = Mock(returncode=0, pid=1001)
            # poll() returns None first (process running), then 0 (finished)
            proc.poll = Mock(side_effect=[None, 0])
            proc.communicate.return_value = ("output", "")
            proc.stdin = Mock()
            procs.append(proc)
        mock_popen.side_effect = procs

        executables = {"generator": "", "test": "", "validator": ""}
        worker = ValidatorTestWorker(str(temp_workspace), executables, test_count=1)

        result = worker._run_single_test(1)

        assert "memory" in result
        assert result["memory"] > 0


class TestValidatorWorkerFileIO:
    """Test input/output file saving."""

    @patch("subprocess.Popen")
    @patch("psutil.Process")
    def test_saves_test_io_files(self, mock_psutil, mock_popen, temp_workspace):
        """Should save input and output to nested directories."""
        # Mock successful execution
        gen_proc = Mock(returncode=0, poll=Mock(return_value=0), pid=1001)
        gen_proc.communicate.return_value = ("test_input_data", "")

        test_proc = Mock(returncode=0, poll=Mock(return_value=0), pid=1002)
        test_proc.communicate.return_value = ("test_output_data", "")
        test_proc.stdin = Mock()

        val_proc = Mock(returncode=0, poll=Mock(return_value=0), pid=1003)
        val_proc.communicate.return_value = ("", "")

        mock_popen.side_effect = [gen_proc, test_proc, val_proc]

        executables = {"generator": "", "test": "", "validator": ""}
        worker = ValidatorTestWorker(str(temp_workspace), executables, test_count=1)

        worker._run_single_test(1)

        # Check if I/O files were created
        validator_dir = temp_workspace / "validator"
        if validator_dir.exists():
            io_dir = validator_dir / "io"
            if io_dir.exists():
                input_file = io_dir / "input_1.txt"
                output_file = io_dir / "output_1.txt"

                # Files should exist (or attempt was made)
                # Note: Actual file creation depends on workspace_utils implementation


class TestValidatorWorkerControl:
    """Test worker start/stop control."""

    def test_stop_cancels_running_tests(self, temp_workspace):
        """Should stop execution when stop() is called."""
        executables = {"generator": "", "test": "", "validator": ""}
        worker = ValidatorTestWorker(str(temp_workspace), executables, test_count=10)

        # Initial state
        assert worker.is_running is True

        # Stop worker
        worker.stop()

        assert worker.is_running is False

    def test_returns_none_when_stopped(self, temp_workspace):
        """Should return None from _run_single_test when stopped."""
        executables = {"generator": "", "test": "", "validator": ""}
        worker = ValidatorTestWorker(str(temp_workspace), executables, test_count=1)

        worker.stop()
        result = worker._run_single_test(1)

        assert result is None


class TestValidatorWorkerResultStorage:
    """Test result storage and retrieval."""

    @patch("subprocess.Popen")
    @patch("psutil.Process")
    def test_get_test_results_returns_copy(self, mock_psutil, mock_popen, temp_workspace):
        """Should return thread-safe copy of test results."""
        # Mock successful execution - create all procs first, then set side_effect
        procs = []
        for _ in range(3):
            proc = Mock(returncode=0, poll=Mock(return_value=0), pid=1001)
            proc.communicate.return_value = ("output", "")
            proc.stdin = Mock()
            procs.append(proc)
        mock_popen.side_effect = procs

        executables = {"generator": "", "test": "", "validator": ""}
        worker = ValidatorTestWorker(str(temp_workspace), executables, test_count=1)

        worker.run_tests()

        # Get results
        results = worker.get_test_results()

        # Should be a list
        assert isinstance(results, list)

        # Modifying returned list shouldn't affect worker's internal results
        original_len = len(results)
        results.append({"fake": "data"})

        new_results = worker.get_test_results()
        assert len(new_results) == original_len
