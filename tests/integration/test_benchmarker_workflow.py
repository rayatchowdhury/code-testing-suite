"""
Integration tests for benchmarker workflow.

Tests the complete benchmarker workflow:
1. Compile generator and test solution
2. Run benchmark tests with time/memory monitoring
3. Track performance metrics
4. Save results to database
5. Verify performance analysis

Uses code fixtures from tests/fixtures/code_samples.py for maintainability.
"""

import json
import time
from pathlib import Path

import pytest
from PySide6.QtCore import QCoreApplication

from src.app.core.tools.benchmarker import Benchmarker
from src.app.database import DatabaseManager
from tests.fixtures.code_samples import CPP_BENCHMARKER_SET


@pytest.fixture
def cpp_benchmarker_workspace(tmp_path):
    """Create C++ workspace for benchmarker tests using code fixtures."""
    workspace = tmp_path / "cpp_benchmark"
    workspace.mkdir()

    # Use fixture code samples
    (workspace / "generator.cpp").write_text(CPP_BENCHMARKER_SET["generator"])
    (workspace / "test.cpp").write_text(CPP_BENCHMARKER_SET["test"])

    return workspace


@pytest.fixture
def temp_db(tmp_path):
    """Create a temporary database for testing."""
    import uuid

    db_path = tmp_path / f"test_benchmarker_{uuid.uuid4().hex}.db"
    db_manager = DatabaseManager(str(db_path))
    yield db_manager
    db_manager.close()


class TestBasicBenchmarking:
    """Test basic benchmarking functionality."""

    def test_basic_benchmark_workflow(self, cpp_benchmarker_workspace, qtbot):
        """Test complete benchmark workflow with time/memory monitoring."""
        benchmarker = Benchmarker(str(cpp_benchmarker_workspace))

        # Compile first
        compilation_done = []
        benchmarker.compilationFinished.connect(
            lambda success: compilation_done.append(success)
        )
        benchmarker.compile_all()
        qtbot.waitUntil(lambda: len(compilation_done) > 0, timeout=30000)
        assert compilation_done[0] is True, "Compilation should succeed"

        # Track test completion
        completed_tests = []
        all_tests_done = []

        def on_test_completed(
            test_name,
            test_num,
            passed,
            exec_time,
            memory,
            memory_passed,
            input_data,
            output_data,
            test_size,
        ):
            completed_tests.append(
                {
                    "test_name": test_name,
                    "test_num": test_num,
                    "passed": passed,
                    "exec_time": exec_time,
                    "memory": memory,
                    "memory_passed": memory_passed,
                    "input_data": input_data,
                    "output_data": output_data,
                    "test_size": test_size,
                }
            )

        def on_all_tests_completed(all_passed):
            all_tests_done.append(all_passed)

        benchmarker.testCompleted.connect(on_test_completed)
        benchmarker.allTestsCompleted.connect(on_all_tests_completed)

        # Run 3 benchmark tests with 2 second time limit and 256MB memory limit
        benchmarker.run_benchmark_test(test_count=3, time_limit=2000, memory_limit=256)

        # Wait for completion
        qtbot.waitUntil(lambda: len(all_tests_done) > 0, timeout=30000)

        # Verify results
        assert len(completed_tests) == 3, "Should complete 3 tests"

        # Debug: Print test results if failing
        if not all_tests_done[0]:
            print("\n=== Test Results ===")
            for test in completed_tests:
                print(
                    f"Test {test['test_num']}: passed={test['passed']}, exec_time={test['exec_time']}, memory={test['memory']}"
                )

        assert all_tests_done[0] is True, "All tests should pass with reasonable limits"

        # Verify each test has required data
        for test in completed_tests:
            assert test["passed"] is True, f"Test {test['test_num']} should pass"
            assert test["exec_time"] > 0, "Execution time should be tracked"
            assert test["exec_time"] < 2.0, "Execution time should be under time limit"
            assert (
                test["memory"] >= 0
            ), "Memory usage should be tracked (can be 0 for very fast tests)"
            assert test["memory_passed"] is True, "Memory should be within limit"
            assert test["input_data"], "Should have input data"
            assert test["output_data"], "Should have output data"

    def test_time_limit_detection(self, cpp_benchmarker_workspace, qtbot):
        """Test that time limit exceeded is properly detected."""
        benchmarker = Benchmarker(str(cpp_benchmarker_workspace))

        # Compile first
        compilation_done = []
        benchmarker.compilationFinished.connect(
            lambda success: compilation_done.append(success)
        )
        benchmarker.compile_all()
        qtbot.waitUntil(lambda: len(compilation_done) > 0, timeout=30000)

        completed_tests = []
        all_tests_done = []

        def on_test_completed(
            test_name,
            test_num,
            passed,
            exec_time,
            memory,
            memory_passed,
            input_data,
            output_data,
            test_size,
        ):
            completed_tests.append(
                {
                    "passed": passed,
                    "exec_time": exec_time,
                }
            )

        def on_all_tests_completed(all_passed):
            all_tests_done.append(all_passed)

        benchmarker.testCompleted.connect(on_test_completed)
        benchmarker.allTestsCompleted.connect(on_all_tests_completed)

        # Run with very tight time limit (1ms - should cause TLE)
        benchmarker.run_benchmark_test(test_count=2, time_limit=1, memory_limit=256)

        # Wait for completion
        qtbot.waitUntil(lambda: len(all_tests_done) > 0, timeout=30000)

        # At least one test should fail due to time limit
        assert all_tests_done[0] is False, "Tests should fail with 1ms time limit"
        assert any(not t["passed"] for t in completed_tests), "Some tests should fail"


class TestDatabaseIntegration:
    """Test database persistence for benchmark results."""

    def test_saves_benchmark_results(self, cpp_benchmarker_workspace, temp_db, qtbot):
        """Test that benchmark results are saved to database correctly."""
        benchmarker = Benchmarker(str(cpp_benchmarker_workspace))
        benchmarker.db_manager = temp_db

        # Compile first
        compilation_done = []
        benchmarker.compilationFinished.connect(
            lambda success: compilation_done.append(success)
        )
        benchmarker.compile_all()
        qtbot.waitUntil(lambda: len(compilation_done) > 0, timeout=30000)

        all_tests_done = []
        benchmarker.allTestsCompleted.connect(
            lambda passed: all_tests_done.append(passed)
        )

        # Run benchmark tests
        benchmarker.run_benchmark_test(test_count=3, time_limit=2000, memory_limit=256)
        qtbot.waitUntil(lambda: len(all_tests_done) > 0, timeout=30000)

        # Save to database
        result_id = benchmarker.save_test_results_to_database()
        assert result_id is not None, "Should return result ID"

        # Retrieve from database using DatabaseManager API
        results = temp_db.get_test_results(limit=1)
        assert len(results) == 1, "Should have one saved result"

        result = results[0]
        assert result.test_type == "benchmark"
        assert result.test_count == 3
        assert result.passed_tests == 3
        assert result.failed_tests == 0

    def test_saves_performance_analysis(
        self, cpp_benchmarker_workspace, temp_db, qtbot
    ):
        """Test that performance analysis is saved correctly."""
        benchmarker = Benchmarker(str(cpp_benchmarker_workspace))
        benchmarker.db_manager = temp_db

        # Compile first
        compilation_done = []
        benchmarker.compilationFinished.connect(
            lambda success: compilation_done.append(success)
        )
        benchmarker.compile_all()
        qtbot.waitUntil(lambda: len(compilation_done) > 0, timeout=30000)

        all_tests_done = []
        benchmarker.allTestsCompleted.connect(
            lambda passed: all_tests_done.append(passed)
        )

        benchmarker.run_benchmark_test(test_count=5, time_limit=2000, memory_limit=256)
        qtbot.waitUntil(lambda: len(all_tests_done) > 0, timeout=30000)

        result_id = benchmarker.save_test_results_to_database()

        # Retrieve and verify performance analysis using DatabaseManager API
        results = temp_db.get_test_results(limit=1)
        result = results[0]
        assert result.mismatch_analysis is not None

        analysis = json.loads(result.mismatch_analysis)
        assert "test_count" in analysis
        assert "time_limit_ms" in analysis
        assert "memory_limit_mb" in analysis
        assert "performance_summary" in analysis
        assert "performance_metrics" in analysis

        # Verify performance summary
        summary = analysis["performance_summary"]
        assert summary["accepted"] == 5
        assert summary["time_limit_exceeded"] == 0
        assert summary["memory_limit_exceeded"] == 0

        # Verify performance metrics
        metrics = analysis["performance_metrics"]
        assert "avg_execution_time" in metrics
        assert "max_execution_time" in metrics
        assert "avg_memory_usage" in metrics
        assert "max_memory_usage" in metrics
        assert metrics["avg_execution_time"] > 0
        assert metrics["max_execution_time"] >= metrics["avg_execution_time"]

    def test_saves_files_snapshot(self, cpp_benchmarker_workspace, temp_db, qtbot):
        """Test that files snapshot is saved correctly."""
        benchmarker = Benchmarker(str(cpp_benchmarker_workspace))
        benchmarker.db_manager = temp_db

        # Compile first
        compilation_done = []
        benchmarker.compilationFinished.connect(
            lambda success: compilation_done.append(success)
        )
        benchmarker.compile_all()
        qtbot.waitUntil(lambda: len(compilation_done) > 0, timeout=30000)

        all_tests_done = []
        benchmarker.allTestsCompleted.connect(
            lambda passed: all_tests_done.append(passed)
        )

        benchmarker.run_benchmark_test(test_count=2, time_limit=2000, memory_limit=256)
        qtbot.waitUntil(lambda: len(all_tests_done) > 0, timeout=30000)

        result_id = benchmarker.save_test_results_to_database()
        results = temp_db.get_test_results(limit=1)
        result = results[0]

        # Verify files snapshot exists (may be empty for test workspaces)
        assert result.files_snapshot is not None
        snapshot = json.loads(result.files_snapshot)
        assert isinstance(snapshot, dict), "Snapshot should be a dictionary"
        assert "test_type" in snapshot, "Snapshot should have test_type"
        assert snapshot["test_type"] == "benchmark", "Should be benchmark type"


class TestMetricsTracking:
    """Test performance metrics tracking."""

    def test_tracks_execution_times(self, cpp_benchmarker_workspace, qtbot):
        """Test that execution times are tracked accurately."""
        benchmarker = Benchmarker(str(cpp_benchmarker_workspace))

        # Compile first
        compilation_done = []
        benchmarker.compilationFinished.connect(
            lambda success: compilation_done.append(success)
        )
        benchmarker.compile_all()
        qtbot.waitUntil(lambda: len(compilation_done) > 0, timeout=30000)

        completed_tests = []
        all_tests_done = []

        def on_test_completed(
            test_name,
            test_num,
            passed,
            exec_time,
            memory,
            memory_passed,
            input_data,
            output_data,
            test_size,
        ):
            completed_tests.append(
                {
                    "exec_time": exec_time,
                    "memory": memory,
                }
            )

        benchmarker.testCompleted.connect(on_test_completed)
        benchmarker.allTestsCompleted.connect(lambda p: all_tests_done.append(p))

        benchmarker.run_benchmark_test(test_count=5, time_limit=2000, memory_limit=256)
        qtbot.waitUntil(lambda: len(all_tests_done) > 0, timeout=30000)

        # Verify all tests have execution times
        assert len(completed_tests) == 5
        for test in completed_tests:
            assert test["exec_time"] > 0, "Should track execution time"
            assert test["exec_time"] < 2.0, "Should be under time limit"
            assert test["memory"] >= 0, "Should track memory (can be 0 for fast tests)"

    def test_tracks_memory_usage(self, cpp_benchmarker_workspace, qtbot):
        """Test that memory usage is tracked."""
        benchmarker = Benchmarker(str(cpp_benchmarker_workspace))

        # Compile first
        compilation_done = []
        benchmarker.compilationFinished.connect(
            lambda success: compilation_done.append(success)
        )
        benchmarker.compile_all()
        qtbot.waitUntil(lambda: len(compilation_done) > 0, timeout=30000)

        completed_tests = []
        all_tests_done = []

        def on_test_completed(
            test_name,
            test_num,
            passed,
            exec_time,
            memory,
            memory_passed,
            input_data,
            output_data,
            test_size,
        ):
            completed_tests.append(
                {
                    "memory": memory,
                    "memory_passed": memory_passed,
                }
            )

        benchmarker.testCompleted.connect(on_test_completed)
        benchmarker.allTestsCompleted.connect(lambda p: all_tests_done.append(p))

        benchmarker.run_benchmark_test(test_count=3, time_limit=2000, memory_limit=256)
        qtbot.waitUntil(lambda: len(all_tests_done) > 0, timeout=30000)

        # Verify memory tracking
        for test in completed_tests:
            assert (
                test["memory"] >= 0
            ), "Should track memory (may be 0 for very fast tests)"
            assert test["memory_passed"] is True, "Should pass memory limit"


class TestIOFileManagement:
    """Test I/O file saving functionality."""

    def test_saves_io_files(self, cpp_benchmarker_workspace, qtbot):
        """Test that input and output files are saved correctly."""
        benchmarker = Benchmarker(str(cpp_benchmarker_workspace))

        # Compile first
        compilation_done = []
        benchmarker.compilationFinished.connect(
            lambda success: compilation_done.append(success)
        )
        benchmarker.compile_all()
        qtbot.waitUntil(lambda: len(compilation_done) > 0, timeout=30000)

        all_tests_done = []
        benchmarker.allTestsCompleted.connect(lambda p: all_tests_done.append(p))

        benchmarker.run_benchmark_test(test_count=3, time_limit=2000, memory_limit=256)
        qtbot.waitUntil(lambda: len(all_tests_done) > 0, timeout=30000)

        # Verify I/O files are created in nested structure
        workspace = Path(cpp_benchmarker_workspace)
        benchmarker_dir = workspace / "benchmarker"
        inputs_dir = benchmarker_dir / "inputs"
        outputs_dir = benchmarker_dir / "outputs"

        assert inputs_dir.exists(), "Inputs directory should exist"
        assert outputs_dir.exists(), "Outputs directory should exist"

        # Verify files for each test
        for i in range(1, 4):
            input_file = inputs_dir / f"input_{i}.txt"
            output_file = outputs_dir / f"output_{i}.txt"

            assert input_file.exists(), f"Input file {i} should exist"
            assert output_file.exists(), f"Output file {i} should exist"
            assert input_file.stat().st_size > 0, f"Input file {i} should have content"
            assert (
                output_file.stat().st_size > 0
            ), f"Output file {i} should have content"


class TestParallelExecution:
    """Test parallel test execution."""

    def test_parallel_execution(self, cpp_benchmarker_workspace, qtbot):
        """Test that multiple tests run in parallel."""
        benchmarker = Benchmarker(str(cpp_benchmarker_workspace))

        # Compile first
        compilation_done = []
        benchmarker.compilationFinished.connect(
            lambda success: compilation_done.append(success)
        )
        benchmarker.compile_all()
        qtbot.waitUntil(lambda: len(compilation_done) > 0, timeout=30000)

        all_tests_done = []
        start_time = time.time()

        benchmarker.allTestsCompleted.connect(lambda p: all_tests_done.append(p))

        # Run 10 tests - should be faster in parallel than sequential
        benchmarker.run_benchmark_test(
            test_count=10, time_limit=2000, memory_limit=256, max_workers=4
        )
        qtbot.waitUntil(lambda: len(all_tests_done) > 0, timeout=30000)

        total_time = time.time() - start_time

        # With 10 tests running in parallel with 4 workers, should be much faster
        # than 10 * single_test_time (sequential execution)
        # Even conservatively, parallel should be at least 2x faster
        assert (
            total_time < 15.0
        ), f"Parallel execution should complete in reasonable time (took {total_time:.2f}s)"


class TestErrorHandling:
    """Test error handling scenarios."""

    def test_compilation_failure(self, tmp_path, qtbot):
        """Test handling of compilation failures."""
        workspace = tmp_path / "cpp_bad"
        workspace.mkdir()

        # Invalid C++ code
        (workspace / "generator.cpp").write_text(
            """
#include <iostream>
int main() {
    SYNTAX ERROR HERE!!!
    return 0;
}
"""
        )

        (workspace / "test.cpp").write_text(
            """
#include <iostream>
int main() {
    std::cout << "test" << std::endl;
    return 0;
}
"""
        )

        benchmarker = Benchmarker(str(workspace))

        compilation_results = []
        benchmarker.compilationFinished.connect(
            lambda success: compilation_results.append(success)
        )

        benchmarker.compile_all()
        qtbot.waitUntil(lambda: len(compilation_results) > 0, timeout=30000)

        # Should detect compilation failure
        assert compilation_results[0] is False, "Should detect compilation failure"

    def test_generator_runtime_error(self, tmp_path, qtbot):
        """Test handling of generator runtime errors."""
        workspace = tmp_path / "cpp_gen_error"
        workspace.mkdir()

        # Generator that crashes
        (workspace / "generator.cpp").write_text(
            """
#include <iostream>
#include <cstdlib>
int main() {
    std::abort();  // Crash immediately
    return 0;
}
"""
        )

        (workspace / "test.cpp").write_text(
            """
#include <iostream>
int main() {
    int n;
    std::cin >> n;
    std::cout << n << std::endl;
    return 0;
}
"""
        )

        benchmarker = Benchmarker(str(workspace))

        # Compile first
        compilation_done = []
        benchmarker.compilationFinished.connect(
            lambda success: compilation_done.append(success)
        )
        benchmarker.compile_all()
        qtbot.waitUntil(lambda: len(compilation_done) > 0, timeout=30000)

        completed_tests = []
        all_tests_done = []

        def on_test_completed(
            test_name,
            test_num,
            passed,
            exec_time,
            memory,
            memory_passed,
            input_data,
            output_data,
            test_size,
        ):
            completed_tests.append(passed)

        benchmarker.testCompleted.connect(on_test_completed)
        benchmarker.allTestsCompleted.connect(lambda p: all_tests_done.append(p))

        benchmarker.run_benchmark_test(test_count=2, time_limit=2000, memory_limit=256)
        qtbot.waitUntil(lambda: len(all_tests_done) > 0, timeout=30000)

        # Tests should fail due to generator error
        assert all_tests_done[0] is False, "Should fail when generator crashes"
        assert all(not passed for passed in completed_tests), "All tests should fail"


class TestCompleteWorkflow:
    """Test complete end-to-end workflow."""

    def test_complete_benchmark_workflow(
        self, cpp_benchmarker_workspace, temp_db, qtbot
    ):
        """Test full workflow: compile → run → save → retrieve → verify."""
        benchmarker = Benchmarker(str(cpp_benchmarker_workspace))
        benchmarker.db_manager = temp_db

        # Track all signals
        compilation_done = []
        completed_tests = []
        all_tests_done = []

        def on_compilation_finished(success):
            compilation_done.append(success)

        def on_test_completed(
            test_name,
            test_num,
            passed,
            exec_time,
            memory,
            memory_passed,
            input_data,
            output_data,
            test_size,
        ):
            completed_tests.append(
                {
                    "test_num": test_num,
                    "passed": passed,
                    "exec_time": exec_time,
                    "memory": memory,
                }
            )

        def on_all_tests_completed(all_passed):
            all_tests_done.append(all_passed)

        benchmarker.compilationFinished.connect(on_compilation_finished)
        benchmarker.testCompleted.connect(on_test_completed)
        benchmarker.allTestsCompleted.connect(on_all_tests_completed)

        # Compile first
        benchmarker.compile_all()
        qtbot.waitUntil(lambda: len(compilation_done) > 0, timeout=30000)

        # Verify compilation
        assert len(compilation_done) > 0, "Should emit compilation signal"
        assert compilation_done[0] is True, "Compilation should succeed"

        # Run benchmark tests
        benchmarker.run_benchmark_test(test_count=5, time_limit=2000, memory_limit=256)

        # Wait for completion
        qtbot.waitUntil(lambda: len(all_tests_done) > 0, timeout=30000)

        # Verify test execution
        assert len(completed_tests) == 5, "Should run 5 tests"
        assert all(t["passed"] for t in completed_tests), "All tests should pass"
        assert all_tests_done[0] is True, "All tests should pass"

        # Save to database
        result_id = benchmarker.save_test_results_to_database()
        assert result_id is not None

        # Retrieve and verify using DatabaseManager API
        results = temp_db.get_test_results(limit=1)
        result = results[0]
        assert result is not None
        assert result.test_type == "benchmark"
        assert result.test_count == 5
        assert result.passed_tests == 5
        assert result.failed_tests == 0

        # Verify test details
        test_details = json.loads(result.test_details)
        assert len(test_details) == 5
        for detail in test_details:
            assert detail["passed"] is True
            assert detail["execution_time"] > 0
            assert detail["memory_used"] >= 0

        # Verify performance analysis
        analysis = json.loads(result.mismatch_analysis)
        assert analysis["test_count"] == 5
        assert analysis["time_limit_ms"] == 2000
        assert analysis["memory_limit_mb"] == 256
        assert analysis["performance_summary"]["accepted"] == 5
        assert analysis["performance_metrics"]["avg_execution_time"] > 0

        # Verify files snapshot
        snapshot = json.loads(result.files_snapshot)
        assert (
            "files" in snapshot or "generator.cpp" in snapshot
        ), "Should have files in snapshot"
        files_dict = snapshot.get("files", snapshot)  # Support both old and new format
        # Just verify snapshot exists and has the expected structure
        assert (
            "test_type" in snapshot or len(files_dict) > 0
        ), "Should have valid snapshot structure"

        # Verify I/O files were created
        workspace = Path(cpp_benchmarker_workspace)
        inputs_dir = workspace / "benchmarker" / "inputs"
        outputs_dir = workspace / "benchmarker" / "outputs"

        for i in range(1, 6):
            assert (inputs_dir / f"input_{i}.txt").exists()
            assert (outputs_dir / f"output_{i}.txt").exists()
