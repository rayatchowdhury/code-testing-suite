"""
Unit tests for BenchmarkTestWorker.

Tests the specialized worker that implements performance benchmarking:
1. Generator → produces test input
2. Test solution → processes input while monitoring time and memory

Tests verify time limit enforcement, memory limit tracking, parallel execution,
signal emission, and performance metrics collection.
"""

import pytest
import os
from unittest.mock import Mock, patch, MagicMock
from subprocess import TimeoutExpired
from PySide6.QtCore import QObject

from src.app.core.tools.specialized.benchmark_test_worker import BenchmarkTestWorker


class TestBenchmarkWorkerInitialization:
    """Test BenchmarkTestWorker initialization."""

    def test_init_sets_limits(self, temp_workspace):
        """Should store time and memory limits."""
        executables = {
            "generator": str(temp_workspace / "generator.exe"),
            "test": str(temp_workspace / "test.exe"),
        }

        worker = BenchmarkTestWorker(
            str(temp_workspace),
            executables,
            time_limit=1000,  # 1000ms
            memory_limit=256,  # 256MB
            test_count=5,
        )

        assert worker.executables == executables
        assert worker.time_limit == 1.0  # Converted to seconds
        assert worker.memory_limit == 256
        assert worker.test_count == 5

    def test_init_calculates_optimal_workers(self, temp_workspace):
        """Should calculate optimal worker count (max 4 for benchmarking)."""
        executables = {"generator": "", "test": ""}

        worker = BenchmarkTestWorker(
            str(temp_workspace),
            executables,
            time_limit=1000,
            memory_limit=256,
            test_count=10,
        )

        assert worker.max_workers >= 1
        assert worker.max_workers <= 4  # Capped at 4 for memory monitoring

    def test_converts_time_limit_to_seconds(self, temp_workspace):
        """Should convert time limit from milliseconds to seconds."""
        executables = {"generator": "", "test": ""}

        worker = BenchmarkTestWorker(
            str(temp_workspace),
            executables,
            time_limit=2500,  # 2500ms
            memory_limit=128,
        )

        assert worker.time_limit == 2.5  # 2.5 seconds


class TestBenchmarkWorkerExecution:
    """Test benchmark execution with monitoring."""

    @patch("subprocess.Popen")
    @patch("subprocess.run")
    @patch("psutil.Process")
    def test_runs_generator_and_test(
        self, mock_psutil, mock_run, mock_popen, temp_workspace
    ):
        """Should execute generator and test solution."""
        # Mock generator execution (subprocess.run)
        gen_result = Mock(returncode=0, stdout="test_input", stderr="")
        mock_run.return_value = gen_result

        # Mock test execution (subprocess.Popen)
        test_proc = Mock(returncode=0, poll=Mock(return_value=0), pid=1002)
        test_proc.communicate.return_value = ("test_output", "")
        test_proc.stdin = Mock()
        mock_popen.return_value = test_proc

        # Mock memory within limits
        mock_memory = Mock()
        mock_memory.rss = 50 * 1024 * 1024  # 50 MB
        mock_psutil.return_value.memory_info.return_value = mock_memory

        executables = {"generator": "gen.exe", "test": "test.exe"}
        worker = BenchmarkTestWorker(
            str(temp_workspace),
            executables,
            time_limit=5000,  # 5 seconds
            memory_limit=256,  # 256 MB
            test_count=1,
        )

        result = worker._run_single_benchmark_test(1)

        assert mock_run.call_count == 1  # Generator execution
        assert mock_popen.call_count == 1  # Test execution
        assert result is not None
        assert result["test_number"] == 1

    @patch("subprocess.Popen")
    @patch("subprocess.run")
    @patch("psutil.Process")
    def test_passes_when_within_limits(
        self, mock_psutil, mock_run, mock_popen, temp_workspace
    ):
        """Should pass when execution is within time and memory limits."""
        # Mock generator execution (subprocess.run)
        gen_result = Mock(returncode=0, stdout="input", stderr="")
        mock_run.return_value = gen_result

        # Mock test execution (subprocess.Popen)
        test_proc = Mock(returncode=0, poll=Mock(return_value=0), pid=1002)
        test_proc.communicate.return_value = ("output", "")
        test_proc.stdin = Mock()
        mock_popen.return_value = test_proc

        # Memory well within limit
        mock_memory = Mock()
        mock_memory.rss = 50 * 1024 * 1024  # 50 MB (< 256 MB limit)
        mock_psutil.return_value.memory_info.return_value = mock_memory

        executables = {"generator": "", "test": ""}
        worker = BenchmarkTestWorker(
            str(temp_workspace),
            executables,
            time_limit=5000,
            memory_limit=256,
            test_count=1,
        )

        result = worker._run_single_benchmark_test(1)

        assert result["passed"] is True
        assert result["memory_passed"] is True

    @patch("subprocess.Popen")
    @patch("subprocess.run")
    @patch("psutil.Process")
    def test_fails_on_memory_limit_exceeded(
        self, mock_psutil, mock_run, mock_popen, temp_workspace
    ):
        """Should fail when memory usage exceeds limit."""
        # Mock generator execution (subprocess.run)
        gen_result = Mock(returncode=0, stdout="input", stderr="")
        mock_run.return_value = gen_result

        # Mock test execution (subprocess.Popen)
        test_proc = Mock(returncode=0, poll=Mock(return_value=0), pid=1002)
        test_proc.communicate.return_value = ("output", "")
        test_proc.stdin = Mock()
        mock_popen.return_value = test_proc

        # Memory exceeds limit
        mock_memory = Mock()
        mock_memory.rss = 300 * 1024 * 1024  # 300 MB (> 256 MB limit)
        mock_psutil.return_value.memory_info.return_value = mock_memory

        executables = {"generator": "", "test": ""}
        worker = BenchmarkTestWorker(
            str(temp_workspace),
            executables,
            time_limit=5000,
            memory_limit=256,
            test_count=1,
        )

        result = worker._run_single_benchmark_test(1)

        assert result["memory_passed"] is False


class TestBenchmarkWorkerSignals:
    """Test signal emission during benchmarking."""

    @patch("subprocess.Popen")
    @patch("psutil.Process")
    def test_emits_test_completed_with_metrics(
        self, mock_psutil, mock_popen, temp_workspace, qtbot
    ):
        """Should emit testCompleted with performance metrics."""
        gen_proc = Mock(returncode=0, poll=Mock(return_value=0), pid=1001)
        gen_proc.communicate.return_value = ("input", "")

        test_proc = Mock(returncode=0, poll=Mock(return_value=0), pid=1002)
        test_proc.communicate.return_value = ("output", "")
        test_proc.stdin = Mock()

        mock_popen.side_effect = [gen_proc, test_proc]

        mock_memory = Mock()
        mock_memory.rss = 10 * 1024 * 1024
        mock_psutil.return_value.memory_info.return_value = mock_memory

        executables = {"generator": "", "test": ""}
        worker = BenchmarkTestWorker(
            str(temp_workspace),
            executables,
            time_limit=1000,
            memory_limit=256,
            test_count=1,
        )

        completed_signals = []
        worker.testCompleted.connect(lambda *args: completed_signals.append(args))

        with qtbot.waitSignal(worker.allTestsCompleted, timeout=5000):
            worker.run_tests()

        # Verify signal was emitted with 9 parameters
        assert len(completed_signals) == 1
        signal_data = completed_signals[0]
        assert (
            len(signal_data) == 9
        )  # test_name, test_num, passed, time, memory, memory_passed, input, output, test_size


class TestBenchmarkWorkerErrorHandling:
    """Test error handling and recovery."""

    @patch("subprocess.Popen")
    def test_handles_generator_failure(self, mock_popen, temp_workspace):
        """Should create error result if generator fails."""
        gen_proc = Mock(returncode=1, poll=Mock(return_value=1), pid=1001)
        gen_proc.communicate.return_value = ("", "Generator error!")

        mock_popen.return_value = gen_proc

        executables = {"generator": "", "test": ""}
        worker = BenchmarkTestWorker(
            str(temp_workspace),
            executables,
            time_limit=1000,
            memory_limit=256,
            test_count=1,
        )

        result = worker._run_single_benchmark_test(1)

        assert result is not None
        assert result["passed"] is False

    @patch("subprocess.Popen")
    @patch("psutil.Process")
    def test_handles_test_solution_failure(
        self, mock_psutil, mock_popen, temp_workspace
    ):
        """Should create error result if test solution fails."""
        gen_proc = Mock(returncode=0, poll=Mock(return_value=0), pid=1001)
        gen_proc.communicate.return_value = ("input", "")

        test_proc = Mock(returncode=1, poll=Mock(return_value=1), pid=1002)
        test_proc.communicate.return_value = ("", "Runtime error!")
        test_proc.stdin = Mock()

        mock_popen.side_effect = [gen_proc, test_proc]

        executables = {"generator": "", "test": ""}
        worker = BenchmarkTestWorker(
            str(temp_workspace),
            executables,
            time_limit=1000,
            memory_limit=256,
            test_count=1,
        )

        result = worker._run_single_benchmark_test(1)

        assert result is not None
        assert result["passed"] is False


class TestBenchmarkWorkerMetrics:
    """Test performance metrics tracking."""

    @patch("subprocess.Popen")
    @patch("psutil.Process")
    def test_tracks_execution_time(self, mock_psutil, mock_popen, temp_workspace):
        """Should track execution time accurately."""
        gen_proc = Mock(returncode=0, poll=Mock(return_value=0), pid=1001)
        gen_proc.communicate.return_value = ("input", "")

        test_proc = Mock(returncode=0, poll=Mock(return_value=0), pid=1002)
        test_proc.communicate.return_value = ("output", "")
        test_proc.stdin = Mock()

        mock_popen.side_effect = [gen_proc, test_proc]

        mock_memory = Mock()
        mock_memory.rss = 10 * 1024 * 1024
        mock_psutil.return_value.memory_info.return_value = mock_memory

        executables = {"generator": "", "test": ""}
        worker = BenchmarkTestWorker(
            str(temp_workspace),
            executables,
            time_limit=1000,
            memory_limit=256,
            test_count=1,
        )

        result = worker._run_single_benchmark_test(1)

        assert "execution_time" in result
        assert result["execution_time"] >= 0

    @patch("subprocess.Popen")
    @patch("subprocess.run")
    @patch("psutil.Process")
    def test_tracks_peak_memory(
        self, mock_psutil, mock_run, mock_popen, temp_workspace
    ):
        """Should track peak memory usage."""
        # Mock generator execution (subprocess.run)
        gen_result = Mock(returncode=0, stdout="input", stderr="")
        mock_run.return_value = gen_result

        # Mock test execution (subprocess.Popen)
        test_proc = Mock(returncode=0, poll=Mock(return_value=0), pid=1002)
        test_proc.communicate.return_value = ("output", "")
        test_proc.stdin = Mock()
        mock_popen.return_value = test_proc

        mock_memory = Mock()
        mock_memory.rss = 100 * 1024 * 1024  # 100 MB
        mock_psutil.return_value.memory_info.return_value = mock_memory

        executables = {"generator": "", "test": ""}
        worker = BenchmarkTestWorker(
            str(temp_workspace),
            executables,
            time_limit=1000,
            memory_limit=256,
            test_count=1,
        )

        result = worker._run_single_benchmark_test(1)

        assert "memory_used" in result
        assert result["memory_used"] > 0


class TestBenchmarkWorkerControl:
    """Test worker start/stop control."""

    def test_stop_cancels_running_tests(self, temp_workspace):
        """Should stop execution when stop() is called."""
        executables = {"generator": "", "test": ""}
        worker = BenchmarkTestWorker(
            str(temp_workspace),
            executables,
            time_limit=1000,
            memory_limit=256,
            test_count=10,
        )

        assert worker.is_running is True

        worker.stop()

        assert worker.is_running is False

    def test_returns_none_when_stopped(self, temp_workspace):
        """Should return None when stopped."""
        executables = {"generator": "", "test": ""}
        worker = BenchmarkTestWorker(
            str(temp_workspace),
            executables,
            time_limit=1000,
            memory_limit=256,
            test_count=1,
        )

        worker.stop()
        result = worker._run_single_benchmark_test(1)

        assert result is None


class TestBenchmarkWorkerResultStorage:
    """Test result storage and retrieval."""

    def test_get_test_results_returns_copy(self, temp_workspace):
        """Should return thread-safe copy of test results."""
        executables = {"generator": "", "test": ""}
        worker = BenchmarkTestWorker(
            str(temp_workspace),
            executables,
            time_limit=1000,
            memory_limit=256,
            test_count=1,
        )

        results = worker.get_test_results()

        assert isinstance(results, list)

        # Modifying returned list shouldn't affect worker's internal results
        original_len = len(results)
        results.append({"fake": "data"})

        new_results = worker.get_test_results()
        assert len(new_results) == original_len
