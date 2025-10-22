"""
Tests for core.tools.base.base_test_worker module

Phase 8 (Task 4): Comprehensive tests for BaseTestWorker
Testing parallel test execution, thread safety, and template method pattern.
"""

import time
from unittest.mock import MagicMock, Mock, patch

import pytest
from PySide6.QtCore import QObject, Signal

from src.app.core.tools.specialized.base_test_worker import BaseTestWorker


class ConcreteTestWorker(BaseTestWorker):
    """Concrete implementation of BaseTestWorker for testing."""

    def __init__(self, *args, test_delay=0.0, fail_on_test=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.test_delay = test_delay
        self.fail_on_test = fail_on_test
        self.tests_executed = []

    def _run_single_test(self, test_number: int):
        """Implement the abstract method."""
        self.tests_executed.append(test_number)

        # Simulate test execution
        if self.test_delay > 0:
            time.sleep(self.test_delay)

        # Simulate failure if specified
        if self.fail_on_test and test_number == self.fail_on_test:
            return {
                "test_number": test_number,
                "passed": False,
                "error_details": f"Test {test_number} failed",
            }

        return {
            "test_number": test_number,
            "passed": True,
            "execution_time": self.test_delay,
        }


class StopOnFailureWorker(ConcreteTestWorker):
    """Worker that stops on first failure."""

    def _should_stop_on_failure(self):
        return True


class TestBaseTestWorkerInitialization:
    """Test BaseTestWorker initialization."""

    def test_init_sets_workspace_dir(self, tmp_path):
        """Should initialize with workspace directory."""
        workspace = str(tmp_path)
        worker = ConcreteTestWorker(workspace, {}, 10)

        assert worker.workspace_dir == workspace

    def test_init_sets_executables(self):
        """Should initialize with executables dictionary."""
        executables = {"test": "test.exe", "generator": "gen.exe"}
        worker = ConcreteTestWorker("/workspace", executables, 10)

        assert worker.executables == executables

    def test_init_sets_test_count(self):
        """Should initialize with test count."""
        worker = ConcreteTestWorker("/workspace", {}, 25)

        assert worker.test_count == 25

    def test_init_sets_is_running_true(self):
        """Should initialize with is_running=True."""
        worker = ConcreteTestWorker("/workspace", {}, 10)

        assert worker.is_running is True

    def test_init_creates_empty_results_list(self):
        """Should initialize with empty test_results list."""
        worker = ConcreteTestWorker("/workspace", {}, 10)

        assert worker.test_results == []

    def test_init_sets_max_workers_auto(self):
        """Should auto-calculate max_workers when not specified."""
        worker = ConcreteTestWorker("/workspace", {}, 10)

        assert worker.max_workers > 0
        assert worker.max_workers <= 8

    def test_init_uses_custom_max_workers(self):
        """Should use custom max_workers when specified."""
        worker = ConcreteTestWorker("/workspace", {}, 10, max_workers=4)

        assert worker.max_workers == 4

    def test_init_creates_results_lock(self):
        """Should create thread-safe results lock."""
        worker = ConcreteTestWorker("/workspace", {}, 10)

        assert hasattr(worker, "_results_lock")


class TestCalculateOptimalWorkers:
    """Test optimal worker calculation."""

    def test_calculate_optimal_workers_returns_positive(self):
        """Should return positive number of workers."""
        worker = ConcreteTestWorker("/workspace", {}, 10)
        optimal = worker._calculate_optimal_workers()

        assert optimal > 0

    def test_calculate_optimal_workers_max_8(self):
        """Should cap workers at 8."""
        worker = ConcreteTestWorker("/workspace", {}, 10)
        optimal = worker._calculate_optimal_workers()

        assert optimal <= 8

    @patch("multiprocessing.cpu_count", return_value=16)
    def test_calculate_optimal_workers_with_many_cpus(self, mock_cpu_count):
        """Should cap at 8 even with many CPUs."""
        worker = ConcreteTestWorker("/workspace", {}, 10)
        optimal = worker._calculate_optimal_workers()

        assert optimal == 8

    @patch("multiprocessing.cpu_count", return_value=2)
    def test_calculate_optimal_workers_with_few_cpus(self, mock_cpu_count):
        """Should use at least 1 worker."""
        worker = ConcreteTestWorker("/workspace", {}, 10)
        optimal = worker._calculate_optimal_workers()

        assert optimal >= 1


class TestRunTests:
    """Test parallel test execution."""

    def test_run_tests_executes_all_tests(self):
        """Should execute all tests."""
        worker = ConcreteTestWorker("/workspace", {}, 5)
        worker.run_tests()

        assert len(worker.tests_executed) == 5
        assert set(worker.tests_executed) == {1, 2, 3, 4, 5}

    def test_run_tests_emits_progress_signals(self, qtbot):
        """Should emit progress signals during execution."""
        worker = ConcreteTestWorker("/workspace", {}, 3)

        with qtbot.waitSignals([worker.progressUpdated] * 2, timeout=2000):
            worker.run_tests()

    def test_run_tests_emits_all_tests_completed(self, qtbot):
        """Should emit allTestsCompleted signal."""
        worker = ConcreteTestWorker("/workspace", {}, 3)

        with qtbot.waitSignal(worker.allTestsCompleted, timeout=2000):
            worker.run_tests()

    def test_run_tests_stores_results(self):
        """Should store all test results."""
        worker = ConcreteTestWorker("/workspace", {}, 5)
        worker.run_tests()

        results = worker.get_results()
        assert len(results) == 5
        assert all("test_number" in r for r in results)

    def test_run_tests_with_failure(self):
        """Should continue running tests after failure."""
        worker = ConcreteTestWorker("/workspace", {}, 5, fail_on_test=3)
        worker.run_tests()

        results = worker.get_results()
        assert len(results) == 5
        # Find the failed test (test 3) - order may vary due to parallelism
        failed_test = next((r for r in results if r["test_number"] == 3), None)
        assert failed_test is not None
        assert not failed_test["passed"]

    def test_run_tests_emits_test_completed_signals(self, qtbot):
        """Should emit testCompleted for each test."""
        worker = ConcreteTestWorker("/workspace", {}, 3)

        signals = []
        worker.testCompleted.connect(lambda r: signals.append(r))

        worker.run_tests()

        assert len(signals) == 3

    def test_run_tests_respects_is_running_flag(self):
        """Should stop if is_running becomes False."""
        worker = ConcreteTestWorker("/workspace", {}, 20, test_delay=0.05)

        # Stop after a short delay
        def stop_worker():
            time.sleep(0.1)
            worker.stop()

        import threading

        stop_thread = threading.Thread(target=stop_worker)
        stop_thread.start()

        worker.run_tests()
        stop_thread.join()

        # Should have executed fewer than all tests
        assert len(worker.tests_executed) < 20


class TestRunSingleTestSafe:
    """Test safe single test execution."""

    def test_run_single_test_safe_returns_result(self):
        """Should return test result on success."""
        worker = ConcreteTestWorker("/workspace", {}, 10)
        result = worker._run_single_test_safe(5)

        assert result is not None
        assert result["test_number"] == 5

    def test_run_single_test_safe_returns_none_when_stopped(self):
        """Should return None when worker is stopped."""
        worker = ConcreteTestWorker("/workspace", {}, 10)
        worker.is_running = False

        result = worker._run_single_test_safe(5)

        assert result is None

    def test_run_single_test_safe_handles_exceptions(self):
        """Should handle exceptions and return error result."""
        worker = ConcreteTestWorker("/workspace", {}, 10)

        # Mock _run_single_test to raise exception
        worker._run_single_test = Mock(side_effect=ValueError("Test error"))

        result = worker._run_single_test_safe(5)

        assert result is not None
        assert result["passed"] is False
        assert "error_details" in result


class TestTestPassed:
    """Test pass/fail determination."""

    def test_test_passed_returns_true_for_passing_test(self):
        """Should return True for passing test."""
        worker = ConcreteTestWorker("/workspace", {}, 10)
        result = {"passed": True}

        assert worker._test_passed(result) is True

    def test_test_passed_returns_false_for_failing_test(self):
        """Should return False for failing test."""
        worker = ConcreteTestWorker("/workspace", {}, 10)
        result = {"passed": False}

        assert worker._test_passed(result) is False

    def test_test_passed_returns_false_for_missing_key(self):
        """Should return False when 'passed' key missing."""
        worker = ConcreteTestWorker("/workspace", {}, 10)
        result = {"test_number": 1}

        assert worker._test_passed(result) is False


class TestShouldStopOnFailure:
    """Test stop-on-failure behavior."""

    def test_should_stop_on_failure_default_false(self):
        """Should return False by default."""
        worker = ConcreteTestWorker("/workspace", {}, 10)

        assert worker._should_stop_on_failure() is False

    def test_should_stop_on_failure_can_be_overridden(self):
        """Should allow subclasses to override."""
        worker = StopOnFailureWorker("/workspace", {}, 10, fail_on_test=2)

        assert worker._should_stop_on_failure() is True

    def test_stop_on_failure_stops_execution(self):
        """Should stop execution on first failure when enabled."""
        worker = StopOnFailureWorker("/workspace", {}, 10, fail_on_test=2)
        worker.run_tests()

        # Should stop after test 2 fails, but parallel execution means some tests
        # may have already started, so we just verify it didn't run ALL tests
        results = worker.get_results()
        assert len(results) < 10  # Should not complete all 10 tests
        # Verify the failure was detected
        failed_test = next((r for r in results if r["test_number"] == 2), None)
        assert failed_test is not None
        assert not failed_test["passed"]


class TestCreateErrorResult:
    """Test error result creation."""

    def test_create_error_result_includes_test_number(self):
        """Should include test number in error result."""
        worker = ConcreteTestWorker("/workspace", {}, 10)
        result = worker._create_error_result(5, "Error message")

        assert result["test_number"] == 5

    def test_create_error_result_sets_passed_false(self):
        """Should set passed=False in error result."""
        worker = ConcreteTestWorker("/workspace", {}, 10)
        result = worker._create_error_result(5, "Error message")

        assert result["passed"] is False

    def test_create_error_result_includes_error_message(self):
        """Should include error message in result."""
        worker = ConcreteTestWorker("/workspace", {}, 10)
        result = worker._create_error_result(5, "Custom error")

        assert result["error_details"] == "Custom error"

    def test_create_error_result_includes_timestamp(self):
        """Should include timestamp in error result."""
        worker = ConcreteTestWorker("/workspace", {}, 10)
        result = worker._create_error_result(5, "Error")

        assert "timestamp" in result

    def test_create_error_result_includes_error_type(self):
        """Should include error_type in result."""
        worker = ConcreteTestWorker("/workspace", {}, 10)
        result = worker._create_error_result(5, "Error")

        assert result["error_type"] == "execution_error"


class TestGetResults:
    """Test results retrieval."""

    def test_get_results_returns_copy(self):
        """Should return copy of results, not original."""
        worker = ConcreteTestWorker("/workspace", {}, 3)
        worker.run_tests()

        results1 = worker.get_results()
        results2 = worker.get_results()

        # Modify one copy
        results1.append({"test": "modified"})

        # Other copy should be unaffected
        assert len(results2) == 3

    def test_get_results_is_thread_safe(self):
        """Should be thread-safe."""
        worker = ConcreteTestWorker("/workspace", {}, 10)
        worker.run_tests()

        # Multiple threads getting results shouldn't cause issues
        import threading

        results_list = []

        def get_results():
            results_list.append(worker.get_results())

        threads = [threading.Thread(target=get_results) for _ in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # All threads should get valid results
        assert all(len(r) == 10 for r in results_list)


class TestGetStatistics:
    """Test statistics calculation."""

    def test_get_statistics_with_no_results(self):
        """Should return zero statistics with no results."""
        worker = ConcreteTestWorker("/workspace", {}, 10)
        stats = worker.get_statistics()

        assert stats["total_tests"] == 0
        assert stats["passed_tests"] == 0
        assert stats["failed_tests"] == 0
        assert stats["pass_rate"] == 0.0

    def test_get_statistics_with_all_passing(self):
        """Should calculate statistics for all passing tests."""
        worker = ConcreteTestWorker("/workspace", {}, 5)
        worker.run_tests()

        stats = worker.get_statistics()

        assert stats["total_tests"] == 5
        assert stats["passed_tests"] == 5
        assert stats["failed_tests"] == 0
        assert stats["pass_rate"] == 100.0

    def test_get_statistics_with_failures(self):
        """Should calculate statistics with failures."""
        worker = ConcreteTestWorker("/workspace", {}, 10, fail_on_test=5)
        worker.run_tests()

        stats = worker.get_statistics()

        assert stats["total_tests"] == 10
        assert stats["passed_tests"] == 9
        assert stats["failed_tests"] == 1
        assert stats["pass_rate"] == 90.0

    def test_get_statistics_includes_timing(self):
        """Should include timing statistics when available."""
        worker = ConcreteTestWorker("/workspace", {}, 3, test_delay=0.01)
        worker.run_tests()

        stats = worker.get_statistics()

        assert "avg_execution_time" in stats
        assert "min_execution_time" in stats
        assert "max_execution_time" in stats
        assert "total_execution_time" in stats

    def test_get_statistics_calculates_timing_correctly(self):
        """Should calculate timing statistics correctly."""
        worker = ConcreteTestWorker("/workspace", {}, 3, test_delay=0.01)
        worker.run_tests()

        stats = worker.get_statistics()

        assert stats["avg_execution_time"] > 0
        assert stats["min_execution_time"] <= stats["avg_execution_time"]
        assert stats["max_execution_time"] >= stats["avg_execution_time"]
        assert stats["total_execution_time"] > 0


class TestStopWorker:
    """Test worker stopping."""

    def test_stop_sets_is_running_false(self):
        """Should set is_running to False."""
        worker = ConcreteTestWorker("/workspace", {}, 10)
        worker.stop()

        assert worker.is_running is False

    def test_stop_emits_progress_signal(self, qtbot):
        """Should emit progress signal when stopping."""
        worker = ConcreteTestWorker("/workspace", {}, 10)

        with qtbot.waitSignal(worker.progressUpdated, timeout=1000):
            worker.stop()

    def test_stop_during_execution_cancels_tests(self):
        """Should cancel remaining tests when stopped."""
        worker = ConcreteTestWorker("/workspace", {}, 50, test_delay=0.05)

        # Start execution in thread
        import threading

        exec_thread = threading.Thread(target=worker.run_tests)
        exec_thread.start()

        # Stop after short delay
        time.sleep(0.1)
        worker.stop()
        exec_thread.join(timeout=2)

        # Should have executed fewer than all tests
        assert len(worker.tests_executed) < 50


class TestAbstractMethod:
    """Test abstract method enforcement."""

    def test_base_class_cannot_run_single_test_directly(self):
        """Should raise NotImplementedError when not overridden."""
        worker = BaseTestWorker("/workspace", {}, 10)

        with pytest.raises(NotImplementedError):
            worker._run_single_test(1)


class TestThreadSafety:
    """Test thread-safety of worker."""

    def test_results_storage_is_thread_safe(self):
        """Should safely store results from multiple threads."""
        worker = ConcreteTestWorker("/workspace", {}, 20)
        worker.run_tests()

        results = worker.get_results()

        # All results should be stored without corruption
        assert len(results) == 20
        test_numbers = [r["test_number"] for r in results]
        assert len(set(test_numbers)) == 20  # No duplicates

    def test_concurrent_result_access_is_safe(self):
        """Should handle concurrent result access safely."""
        worker = ConcreteTestWorker("/workspace", {}, 10)
        worker.run_tests()

        # Multiple threads accessing results
        import threading

        access_results = []

        def access_results_repeatedly():
            for _ in range(100):
                results = worker.get_results()
                access_results.append(len(results))

        threads = [threading.Thread(target=access_results_repeatedly) for _ in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # All accesses should return consistent results
        assert all(count == 10 for count in access_results)


class TestSignalEmission:
    """Test Qt signal emission."""

    def test_test_started_signal_emits_correct_data(self, qtbot):
        """Should emit test number and total with testStarted."""
        worker = ConcreteTestWorker("/workspace", {}, 3)

        signals = []
        worker.testStarted.connect(
            lambda current, total: signals.append((current, total))
        )

        worker.run_tests()

        assert len(signals) == 3
        assert all(total == 3 for _, total in signals)

    def test_test_completed_signal_includes_result(self, qtbot):
        """Should emit test result with testCompleted."""
        worker = ConcreteTestWorker("/workspace", {}, 2)

        results = []
        worker.testCompleted.connect(lambda r: results.append(r))

        worker.run_tests()

        assert len(results) == 2
        assert all("test_number" in r for r in results)

    def test_all_tests_completed_signal_indicates_success(self, qtbot):
        """Should emit True when all tests pass."""
        worker = ConcreteTestWorker("/workspace", {}, 3)

        result_holder = []
        worker.allTestsCompleted.connect(lambda passed: result_holder.append(passed))

        worker.run_tests()

        assert len(result_holder) == 1
        assert result_holder[0] is True

    def test_all_tests_completed_signal_indicates_failure(self, qtbot):
        """Should emit False when any test fails."""
        worker = ConcreteTestWorker("/workspace", {}, 5, fail_on_test=3)

        result_holder = []
        worker.allTestsCompleted.connect(lambda passed: result_holder.append(passed))

        worker.run_tests()

        assert len(result_holder) == 1
        assert result_holder[0] is False
