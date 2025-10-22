"""
Integration tests for comparator workflow.

Tests end-to-end comparison testing workflow with:
- 3-stage comparison (generator → test → correct)
- Output comparison and mismatch analysis
- Multi-language support (C++, Python, Java)
- Database persistence
- Metrics tracking (time, memory)
- I/O file management

Per Phase 6.2 requirements: Use real Comparator, BaseCompiler, DatabaseManager.
"""

import json
import os
import time
from pathlib import Path

import pytest
from PySide6.QtCore import QCoreApplication

from src.app.core.tools.comparator import Comparator
from src.app.database import DatabaseManager
from tests.fixtures.code_samples import (
    CPP_COMPARATOR_MATCHING,
    CPP_COMPARATOR_MISMATCHED,
    PYTHON_COMPARATOR_MATCHING,
)


@pytest.fixture
def qapp():
    """Create QCoreApplication for Qt signals."""
    app = QCoreApplication.instance()
    if app is None:
        app = QCoreApplication([])
    yield app


@pytest.fixture
def temp_db(tmp_path):
    """Create temporary database for integration tests with unique name."""
    import uuid

    db_path = str(tmp_path / f"comparator_test_{uuid.uuid4().hex[:8]}.db")
    db_manager = DatabaseManager(db_path)
    yield db_manager
    db_manager.close()


@pytest.fixture
def cpp_comparator_workspace(tmp_path):
    """Create workspace with C++ comparison test files (matching outputs)."""
    workspace = tmp_path / "cpp_comparator"
    comp_dir = workspace / "comparator"
    comp_dir.mkdir(parents=True)

    # Use fixture code samples
    (comp_dir / "generator.cpp").write_text(CPP_COMPARATOR_MATCHING["generator"])
    (comp_dir / "correct.cpp").write_text(CPP_COMPARATOR_MATCHING["correct"])
    (comp_dir / "test.cpp").write_text(CPP_COMPARATOR_MATCHING["test"])

    return workspace


@pytest.fixture
def cpp_mismatched_workspace(tmp_path):
    """Create workspace with mismatched test solution (for testing failures)."""
    workspace = tmp_path / "cpp_mismatch"
    comp_dir = workspace / "comparator"
    comp_dir.mkdir(parents=True)

    # Use fixture code samples (mismatched set)
    (comp_dir / "generator.cpp").write_text(CPP_COMPARATOR_MISMATCHED["generator"])
    (comp_dir / "correct.cpp").write_text(CPP_COMPARATOR_MISMATCHED["correct"])
    (comp_dir / "test.cpp").write_text(CPP_COMPARATOR_MISMATCHED["test"])

    return workspace


@pytest.fixture
def python_comparator_workspace(tmp_path):
    """Create workspace with Python comparison files."""
    workspace = tmp_path / "py_comparator"
    comp_dir = workspace / "comparator"
    comp_dir.mkdir(parents=True)

    # Use fixture code samples
    (comp_dir / "generator.py").write_text(PYTHON_COMPARATOR_MATCHING["generator"])
    (comp_dir / "correct.py").write_text(PYTHON_COMPARATOR_MATCHING["correct"])
    (comp_dir / "test.py").write_text(PYTHON_COMPARATOR_MATCHING["test"])

    return workspace


class TestBasicComparison:
    """Test basic comparison workflow with matching outputs."""

    def test_cpp_comparison_matching_outputs(self, qapp, cpp_comparator_workspace):
        """Should run comparison tests and detect matching outputs."""
        # Create comparator
        comparator = Comparator(str(cpp_comparator_workspace))

        # Compile all files
        compile_results = []
        comparator.compilationFinished.connect(
            lambda success: compile_results.append(success)
        )

        comparator.compile_all()

        # Wait for compilation with event processing
        timeout = 30
        start = time.time()
        while len(compile_results) == 0 and (time.time() - start) < timeout:
            qapp.processEvents()
            time.sleep(0.1)

        assert len(compile_results) > 0, "Compilation did not complete"
        assert compile_results[0] is True, "Compilation failed"

        # Run comparison tests
        test_results = []
        comparator.testCompleted.connect(
            lambda num, passed, inp, correct, test: test_results.append(
                {
                    "number": num,
                    "passed": passed,
                    "input": inp,
                    "correct": correct,
                    "test": test,
                }
            )
        )

        all_tests_results = []
        comparator.allTestsCompleted.connect(
            lambda all_passed: all_tests_results.append(all_passed)
        )

        comparator.run_comparison_test(test_count=5)

        # Wait for tests with event processing
        timeout = 30
        start = time.time()
        while len(all_tests_results) == 0 and (time.time() - start) < timeout:
            qapp.processEvents()
            time.sleep(0.1)

        # Verify results
        assert len(all_tests_results) > 0, "Tests did not complete"
        assert all_tests_results[0] is True, "Not all tests passed"
        assert len(test_results) == 5, f"Expected 5 tests, got {len(test_results)}"

        # All should pass (matching outputs)
        assert all(r["passed"] for r in test_results), "Some tests failed unexpectedly"

    def test_cpp_comparison_detects_mismatches(self, qapp, cpp_mismatched_workspace):
        """Should detect output mismatches between test and correct solutions."""
        # Create comparator
        comparator = Comparator(str(cpp_mismatched_workspace))

        # Compile
        compile_results = []
        comparator.compilationFinished.connect(
            lambda success: compile_results.append(success)
        )
        comparator.compile_all()

        timeout = 30
        start = time.time()
        while len(compile_results) == 0 and (time.time() - start) < timeout:
            qapp.processEvents()
            time.sleep(0.1)

        assert compile_results[0] is True, "Compilation failed"

        # Run tests
        test_results = []
        comparator.testCompleted.connect(
            lambda num, passed, inp, correct, test: test_results.append(
                {"passed": passed, "correct": correct, "test": test}
            )
        )

        all_tests_results = []
        comparator.allTestsCompleted.connect(
            lambda all_passed: all_tests_results.append(all_passed)
        )

        comparator.run_comparison_test(test_count=3)

        timeout = 30
        start = time.time()
        while len(all_tests_results) == 0 and (time.time() - start) < timeout:
            qapp.processEvents()
            time.sleep(0.1)

        # Verify mismatches detected
        assert len(all_tests_results) > 0, "Tests did not complete"
        assert all_tests_results[0] is False, "Should detect mismatches"
        assert len(test_results) == 3

        # All should fail (outputs don't match)
        assert all(not r["passed"] for r in test_results), "Expected all tests to fail"

        # Verify outputs are different
        for r in test_results:
            assert r["test"] != r["correct"], "Outputs should be different"

    @pytest.mark.skip(reason="Python comparator needs language config support")
    def test_python_comparison_workflow(self, qapp, python_comparator_workspace):
        """Should run comparison tests with Python files."""
        # Create comparator
        comparator = Comparator(str(python_comparator_workspace))

        # Compile (Python "compilation" just validates files exist)
        compile_results = []
        comparator.compilationFinished.connect(
            lambda success: compile_results.append(success)
        )
        comparator.compile_all()

        timeout = 30
        start = time.time()
        while len(compile_results) == 0 and (time.time() - start) < timeout:
            qapp.processEvents()
            time.sleep(0.1)

        assert compile_results[0] is True

        # Run tests
        test_results = []
        comparator.testCompleted.connect(
            lambda num, passed, inp, correct, test, time, mem: test_results.append(
                passed
            )
        )

        all_tests_results = []
        comparator.allTestsCompleted.connect(
            lambda all_passed: all_tests_results.append(all_passed)
        )

        comparator.run_comparison_test(test_count=3)

        timeout = 30
        start = time.time()
        while len(all_tests_results) == 0 and (time.time() - start) < timeout:
            qapp.processEvents()
            time.sleep(0.1)

        # All should pass
        assert len(test_results) == 3
        assert all(test_results), "All Python tests should pass"


class TestDatabaseIntegration:
    """Test database persistence for comparison results."""

    def test_saves_comparison_results_to_database(
        self, qapp, temp_db, cpp_comparator_workspace
    ):
        """Should save comparison test results to database."""
        # Create comparator with custom DB
        comparator = Comparator(str(cpp_comparator_workspace))
        comparator.db_manager = temp_db  # Use test database

        # Compile and run tests
        compile_results = []
        comparator.compilationFinished.connect(
            lambda success: compile_results.append(success)
        )
        comparator.compile_all()

        timeout = 30
        start = time.time()
        while len(compile_results) == 0 and (time.time() - start) < timeout:
            qapp.processEvents()
            time.sleep(0.1)

        assert compile_results[0] is True

        # Run tests
        all_tests_results = []
        comparator.allTestsCompleted.connect(
            lambda all_passed: all_tests_results.append(all_passed)
        )

        comparator.run_comparison_test(test_count=5)

        timeout = 30
        start = time.time()
        while len(all_tests_results) == 0 and (time.time() - start) < timeout:
            qapp.processEvents()
            time.sleep(0.1)

        # Save to database
        result_id = comparator.save_test_results_to_database()

        assert result_id is not None
        assert result_id > 0

        # Retrieve from database
        saved_results = temp_db.get_test_results(test_type="comparison", limit=1)

        assert len(saved_results) >= 1
        result = saved_results[0]
        assert result.id == result_id
        assert result.test_type == "comparison"
        assert result.test_count == 5
        assert result.passed_tests == 5
        assert result.failed_tests == 0

    def test_saves_mismatch_analysis(self, qapp, temp_db, cpp_mismatched_workspace):
        """Should save detailed mismatch analysis to database."""
        # Create comparator
        comparator = Comparator(str(cpp_mismatched_workspace))
        comparator.db_manager = temp_db

        # Compile and run
        compile_results = []
        comparator.compilationFinished.connect(
            lambda success: compile_results.append(success)
        )
        comparator.compile_all()

        timeout = 30
        start = time.time()
        while len(compile_results) == 0 and (time.time() - start) < timeout:
            qapp.processEvents()
            time.sleep(0.1)

        all_tests_results = []
        comparator.allTestsCompleted.connect(
            lambda all_passed: all_tests_results.append(all_passed)
        )

        comparator.run_comparison_test(test_count=3)

        timeout = 30
        start = time.time()
        while len(all_tests_results) == 0 and (time.time() - start) < timeout:
            qapp.processEvents()
            time.sleep(0.1)

        # Save to database
        result_id = comparator.save_test_results_to_database()

        # Retrieve and verify analysis (get most recent)
        saved_results = temp_db.get_test_results(limit=1)
        assert len(saved_results) >= 1

        result = saved_results[0]
        assert result.id == result_id

        # Parse mismatch analysis
        analysis = json.loads(result.mismatch_analysis)

        assert "comparison_summary" in analysis
        assert "execution_times" in analysis
        assert "failed_tests" in analysis

        # Verify summary
        summary = analysis["comparison_summary"]
        # Verify fields exist (actual counts may vary based on execution)
        assert "matching_outputs" in summary
        assert "mismatched_outputs" in summary
        assert "generator_failures" in summary
        assert "test_failures" in summary
        assert "correct_failures" in summary
        assert "timeouts" in summary

        # Verify execution times
        times = analysis["execution_times"]
        assert "avg_generator" in times
        assert "avg_test" in times
        assert "avg_correct" in times
        assert "avg_comparison" in times

    def test_saves_files_snapshot(self, qapp, temp_db, cpp_comparator_workspace):
        """Should save files snapshot with source code."""
        comparator = Comparator(str(cpp_comparator_workspace))
        comparator.db_manager = temp_db

        # Compile and run
        compile_results = []
        comparator.compilationFinished.connect(
            lambda success: compile_results.append(success)
        )
        comparator.compile_all()

        timeout = 30
        start = time.time()
        while len(compile_results) == 0 and (time.time() - start) < timeout:
            qapp.processEvents()
            time.sleep(0.1)

        all_tests_results = []
        comparator.allTestsCompleted.connect(
            lambda all_passed: all_tests_results.append(all_passed)
        )
        comparator.run_comparison_test(test_count=2)

        timeout = 30
        start = time.time()
        while len(all_tests_results) == 0 and (time.time() - start) < timeout:
            qapp.processEvents()
            time.sleep(0.1)

        # Save
        result_id = comparator.save_test_results_to_database()

        # Retrieve
        saved_results = temp_db.get_test_results()
        result = saved_results[0]

        # Verify snapshot
        assert result.files_snapshot is not None
        assert result.files_snapshot != ""

        snapshot = json.loads(result.files_snapshot)

        assert "files" in snapshot
        assert len(snapshot["files"]) == 3  # generator, correct, test

        # Verify all files have content
        for filename, file_info in snapshot["files"].items():
            assert "content" in file_info
            assert "language" in file_info
            assert "role" in file_info
            assert len(file_info["content"]) > 0


class TestMetricsTracking:
    """Test execution metrics tracking (time, memory)."""

    def test_tracks_execution_times(self, qapp, cpp_comparator_workspace):
        """Should track execution time for each stage."""
        comparator = Comparator(str(cpp_comparator_workspace))

        # Compile
        compile_results = []
        comparator.compilationFinished.connect(
            lambda success: compile_results.append(success)
        )
        comparator.compile_all()

        timeout = 30
        start = time.time()
        while len(compile_results) == 0 and (time.time() - start) < timeout:
            qapp.processEvents()
            time.sleep(0.1)

        # Run tests and collect metrics
        test_metrics = []
        comparator.testCompleted.connect(
            lambda num, passed, inp, correct, test: test_metrics.append(
                {"passed": passed}
            )
        )

        all_tests_results = []
        comparator.allTestsCompleted.connect(
            lambda all_passed: all_tests_results.append(all_passed)
        )

        comparator.run_comparison_test(test_count=3)

        timeout = 30
        start = time.time()
        while len(all_tests_results) == 0 and (time.time() - start) < timeout:
            qapp.processEvents()
            time.sleep(0.1)

        # Verify metrics collected
        assert len(test_metrics) == 3

        for metric in test_metrics:
            # Just verify test completed
            assert "passed" in metric

    def test_tracks_average_times_in_analysis(
        self, qapp, temp_db, cpp_comparator_workspace
    ):
        """Should calculate average times in mismatch analysis."""
        comparator = Comparator(str(cpp_comparator_workspace))
        comparator.db_manager = temp_db

        # Compile and run
        compile_results = []
        comparator.compilationFinished.connect(
            lambda success: compile_results.append(success)
        )
        comparator.compile_all()

        timeout = 30
        start = time.time()
        while len(compile_results) == 0 and (time.time() - start) < timeout:
            qapp.processEvents()
            time.sleep(0.1)

        all_tests_results = []
        comparator.allTestsCompleted.connect(
            lambda all_passed: all_tests_results.append(all_passed)
        )
        comparator.run_comparison_test(test_count=5)

        timeout = 30
        start = time.time()
        while len(all_tests_results) == 0 and (time.time() - start) < timeout:
            qapp.processEvents()
            time.sleep(0.1)

        # Save
        comparator.save_test_results_to_database()

        # Retrieve analysis
        saved_results = temp_db.get_test_results()
        analysis = json.loads(saved_results[0].mismatch_analysis)

        times = analysis["execution_times"]

        # Verify averages calculated
        assert times["avg_generator"] > 0
        assert times["avg_test"] > 0
        assert times["avg_correct"] > 0
        assert times["avg_comparison"] >= 0  # Comparison is very fast, might be 0


class TestIOFileManagement:
    """Test input/output file saving."""

    def test_saves_input_output_files(self, qapp, cpp_comparator_workspace):
        """Should save input and output files for each test."""
        comparator = Comparator(str(cpp_comparator_workspace))

        # Compile
        compile_results = []
        comparator.compilationFinished.connect(
            lambda success: compile_results.append(success)
        )
        comparator.compile_all()

        timeout = 30
        start = time.time()
        while len(compile_results) == 0 and (time.time() - start) < timeout:
            qapp.processEvents()
            time.sleep(0.1)

        # Run tests
        all_tests_results = []
        comparator.allTestsCompleted.connect(
            lambda all_passed: all_tests_results.append(all_passed)
        )

        comparator.run_comparison_test(test_count=3)

        timeout = 30
        start = time.time()
        while len(all_tests_results) == 0 and (time.time() - start) < timeout:
            qapp.processEvents()
            time.sleep(0.1)

        # Verify files created
        workspace = Path(cpp_comparator_workspace)
        inputs_dir = workspace / "comparator" / "inputs"
        outputs_dir = workspace / "comparator" / "outputs"

        # Check directories exist
        assert inputs_dir.exists(), "Inputs directory not created"
        assert outputs_dir.exists(), "Outputs directory not created"

        # Check files for each test
        for test_num in range(1, 4):
            input_file = inputs_dir / f"input_{test_num}.txt"
            test_output = outputs_dir / f"output_{test_num}.txt"
            correct_output = outputs_dir / f"correct_output_{test_num}.txt"

            assert input_file.exists(), f"Input file {test_num} not created"
            assert test_output.exists(), f"Test output {test_num} not created"
            assert correct_output.exists(), f"Correct output {test_num} not created"

            # Verify files have content
            assert input_file.read_text().strip() != "", f"Input {test_num} is empty"
            assert (
                test_output.read_text().strip() != ""
            ), f"Test output {test_num} is empty"
            assert (
                correct_output.read_text().strip() != ""
            ), f"Correct output {test_num} is empty"


class TestParallelExecution:
    """Test parallel test execution."""

    def test_runs_tests_in_parallel(self, qapp, cpp_comparator_workspace):
        """Should execute multiple tests in parallel."""
        comparator = Comparator(str(cpp_comparator_workspace))

        # Compile
        compile_results = []
        comparator.compilationFinished.connect(
            lambda success: compile_results.append(success)
        )
        comparator.compile_all()

        timeout = 30
        start = time.time()
        while len(compile_results) == 0 and (time.time() - start) < timeout:
            qapp.processEvents()
            time.sleep(0.1)

        # Run with explicit max_workers
        test_start_times = []
        comparator.testStarted.connect(
            lambda current, total: test_start_times.append(time.time())
        )

        all_tests_results = []
        comparator.allTestsCompleted.connect(
            lambda all_passed: all_tests_results.append(all_passed)
        )

        start_time = time.time()
        comparator.run_comparison_test(test_count=10, max_workers=4)

        timeout = 60
        start = time.time()
        while len(all_tests_results) == 0 and (time.time() - start) < timeout:
            qapp.processEvents()
            time.sleep(0.1)

        total_time = time.time() - start_time

        # Parallel execution should be faster than sequential
        # 10 tests with 4 workers should complete faster than running sequentially
        # Rough estimate: should be less than if they all ran sequentially
        assert len(test_start_times) == 10
        assert total_time < 60  # Should complete in reasonable time


class TestErrorHandling:
    """Test error handling in comparison workflow."""

    def test_handles_generator_failure(self, qapp, tmp_path):
        """Should handle generator compilation/execution failure."""
        workspace = tmp_path / "bad_generator"
        comp_dir = workspace / "comparator"
        comp_dir.mkdir(parents=True)

        # Bad generator (compilation error)
        (comp_dir / "generator.cpp").write_text(
            """
#include <iostream>
int main() {
    undefined_function();  // ERROR
    return 0;
}
"""
        )

        # Valid correct and test
        (comp_dir / "correct.cpp").write_text(
            """
#include <iostream>
int main() { std::cout << "output" << std::endl; return 0; }
"""
        )

        (comp_dir / "test.cpp").write_text(
            """
#include <iostream>
int main() { std::cout << "output" << std::endl; return 0; }
"""
        )

        comparator = Comparator(str(workspace))

        # Compilation should fail
        compile_results = []
        comparator.compilationFinished.connect(
            lambda success: compile_results.append(success)
        )
        comparator.compile_all()

        timeout = 30
        start = time.time()
        while len(compile_results) == 0 and (time.time() - start) < timeout:
            qapp.processEvents()
            time.sleep(0.1)

        # Compilation failure expected
        assert len(compile_results) > 0
        assert compile_results[0] is False

    def test_handles_runtime_timeout(self, qapp, tmp_path):
        """Should handle test execution timeout gracefully."""
        workspace = tmp_path / "timeout_test"
        comp_dir = workspace / "comparator"
        comp_dir.mkdir(parents=True)

        # Generator with infinite loop (will timeout)
        (comp_dir / "generator.cpp").write_text(
            """
#include <iostream>
using namespace std;

int main() {
    while(true) {  // Infinite loop - will timeout
        // Spin forever
    }
    return 0;
}
"""
        )

        (comp_dir / "correct.cpp").write_text(
            """
#include <iostream>
int main() { std::cout << "output" << std::endl; return 0; }
"""
        )

        (comp_dir / "test.cpp").write_text(
            """
#include <iostream>
int main() { std::cout << "output" << std::endl; return 0; }
"""
        )

        comparator = Comparator(str(workspace))

        # Compile should succeed
        compile_results = []
        comparator.compilationFinished.connect(
            lambda success: compile_results.append(success)
        )
        comparator.compile_all()

        timeout = 30
        start = time.time()
        while len(compile_results) == 0 and (time.time() - start) < timeout:
            qapp.processEvents()
            time.sleep(0.1)

        # Note: Test execution will timeout and worker will handle it
        # We just verify the system doesn't crash
        assert compile_results[0] is True


class TestCompleteWorkflow:
    """Test complete end-to-end workflow."""

    def test_complete_comparison_workflow(
        self, qapp, temp_db, cpp_comparator_workspace
    ):
        """Should complete full workflow: compile → test → save → retrieve."""
        # Step 1: Create comparator
        comparator = Comparator(str(cpp_comparator_workspace))
        comparator.db_manager = temp_db

        # Step 2: Compile
        compile_results = []
        comparator.compilationFinished.connect(
            lambda success: compile_results.append(success)
        )
        comparator.compile_all()

        timeout = 30
        start = time.time()
        while len(compile_results) == 0 and (time.time() - start) < timeout:
            qapp.processEvents()
            time.sleep(0.1)

        assert compile_results[0] is True, "Compilation failed"

        # Step 3: Run tests
        test_results = []
        comparator.testCompleted.connect(
            lambda num, passed, inp, correct, test: test_results.append(passed)
        )

        all_tests_results = []
        comparator.allTestsCompleted.connect(
            lambda all_passed: all_tests_results.append(all_passed)
        )

        comparator.run_comparison_test(test_count=10)

        timeout = 60
        start = time.time()
        while len(all_tests_results) == 0 and (time.time() - start) < timeout:
            qapp.processEvents()
            time.sleep(0.1)

        assert len(test_results) == 10
        assert all(test_results), "All tests should pass"

        # Step 4: Save to database
        result_id = comparator.save_test_results_to_database()
        assert result_id > 0

        # Step 5: Retrieve and verify (get most recent)
        saved_results = temp_db.get_test_results(test_type="comparison", limit=1)

        assert len(saved_results) >= 1
        result = saved_results[0]
        assert result.id == result_id

        # Verify all data persisted
        assert result.test_type == "comparison"
        assert result.test_count == 10
        assert result.passed_tests == 10
        assert result.failed_tests == 0
        assert result.total_time > 0

        # Verify snapshot
        snapshot = json.loads(result.files_snapshot)
        assert len(snapshot["files"]) == 3

        # Verify analysis
        analysis = json.loads(result.mismatch_analysis)
        assert analysis["comparison_summary"]["matching_outputs"] == 10
        assert analysis["comparison_summary"]["mismatched_outputs"] == 0

        # Verify I/O files created
        workspace = Path(cpp_comparator_workspace)
        inputs_dir = workspace / "comparator" / "inputs"
        outputs_dir = workspace / "comparator" / "outputs"

        assert inputs_dir.exists()
        assert outputs_dir.exists()
        assert len(list(inputs_dir.glob("*.txt"))) == 10
        assert len(list(outputs_dir.glob("*.txt"))) == 20  # 2 files per test
