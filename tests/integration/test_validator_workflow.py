"""
Integration tests for validator workflow.

Tests the complete validator workflow:
1. Compile generator, test solution, and validator
2. Run 3-stage validation tests (generator → test → validator)
3. Track verdicts (Accepted, Wrong Answer, Presentation Error)
4. Save results to database
5. Verify validation analysis

Uses code fixtures from tests/fixtures/code_samples.py for maintainability.
"""

import pytest
import json
import time
from pathlib import Path
from PySide6.QtCore import QCoreApplication
from src.app.core.tools.validator import ValidatorRunner
from src.app.persistence.database import DatabaseManager
from tests.fixtures.code_samples import CPP_VALIDATOR_SET


@pytest.fixture
def cpp_validator_workspace(tmp_path):
    """Create C++ workspace for validator tests using code fixtures."""
    workspace = tmp_path / "cpp_validator"
    validator_dir = workspace / "validator"
    validator_dir.mkdir(parents=True)

    # Use fixture code samples
    (validator_dir / "generator.cpp").write_text(CPP_VALIDATOR_SET["generator"])
    (validator_dir / "test.cpp").write_text(CPP_VALIDATOR_SET["test"])

    # Validator that reads from files (takes 2 args: input_file output_file)
    validator_code = """
#include <iostream>
#include <fstream>
#include <vector>
#include <sstream>
using namespace std;

int main(int argc, char* argv[]) {
    if (argc != 3) {
        cerr << "Usage: validator <input_file> <output_file>" << endl;
        return 3;  // Validator Error
    }
    
    // Read output file (test solution's output)
    ifstream output_file(argv[2]);
    string line;
    getline(output_file, line);
    output_file.close();
    
    // Parse integers from output
    istringstream iss(line);
    vector<int> nums;
    int num;
    while (iss >> num) {
        nums.push_back(num);
    }
    
    // Check if sorted ascending
    for (size_t i = 1; i < nums.size(); i++) {
        if (nums[i] < nums[i-1]) {
            return 1;  // Wrong Answer
        }
    }
    
    return 0;  // Accepted
}
"""
    (validator_dir / "validator.cpp").write_text(validator_code.strip())

    return workspace


@pytest.fixture
def cpp_wrong_answer_workspace(tmp_path):
    """Create workspace with test solution that produces wrong answers."""
    workspace = tmp_path / "cpp_wa"
    validator_dir = workspace / "validator"
    validator_dir.mkdir(parents=True)

    # Use simple generator
    (validator_dir / "generator.cpp").write_text(CPP_VALIDATOR_SET["generator"])

    # Test solution that doesn't sort (wrong answer)
    (validator_dir / "test.cpp").write_text(
        """
#include <iostream>
using namespace std;

int main() {
    int n;
    cin >> n;
    
    int arr[1000];
    for (int i = 0; i < n; i++) {
        cin >> arr[i];
    }
    
    // WRONG: not sorting - just output as-is
    for (int i = 0; i < n; i++) {
        cout << arr[i];
        if (i < n - 1) cout << " ";
    }
    cout << endl;
    
    return 0;
}
""".strip()
    )

    # Validator that reads from files (takes 2 args: input_file output_file)
    validator_code = """
#include <iostream>
#include <fstream>
#include <vector>
#include <sstream>
using namespace std;

int main(int argc, char* argv[]) {
    if (argc != 3) {
        cerr << "Usage: validator <input_file> <output_file>" << endl;
        return 3;  // Validator Error
    }
    
    // Read output file (test solution's output)
    ifstream output_file(argv[2]);
    string line;
    getline(output_file, line);
    output_file.close();
    
    // Parse integers from output
    istringstream iss(line);
    vector<int> nums;
    int num;
    while (iss >> num) {
        nums.push_back(num);
    }
    
    // Check if sorted ascending
    for (size_t i = 1; i < nums.size(); i++) {
        if (nums[i] < nums[i-1]) {
            return 1;  // Wrong Answer
        }
    }
    
    return 0;  // Accepted
}
"""
    (validator_dir / "validator.cpp").write_text(validator_code.strip())

    return workspace


@pytest.fixture
def temp_db(tmp_path):
    """Create a temporary database for testing."""
    import uuid

    db_path = tmp_path / f"test_validator_{uuid.uuid4().hex}.db"
    db_manager = DatabaseManager(str(db_path))
    yield db_manager
    db_manager.close()


class TestBasicValidation:
    """Test basic validation functionality."""

    def test_basic_validation_workflow(self, cpp_validator_workspace, qtbot):
        """Test complete validation workflow with Accepted verdicts."""
        validator = ValidatorRunner(str(cpp_validator_workspace))

        # Compile first
        compilation_done = []
        validator.compilationFinished.connect(
            lambda success: compilation_done.append(success)
        )
        validator.compile_all()
        qtbot.waitUntil(lambda: len(compilation_done) > 0, timeout=30000)
        assert compilation_done[0] is True, "Compilation should succeed"

        # Track test completion
        completed_tests = []
        all_tests_done = []

        def on_test_completed(
            test_num,
            passed,
            input_data,
            test_output,
            validation_message,
            error_details,
            validator_exit_code,
            exec_time,
            memory,
        ):
            completed_tests.append(
                {
                    "test_num": test_num,
                    "passed": passed,
                    "validation_message": validation_message,
                    "validator_exit_code": validator_exit_code,
                    "input_data": input_data,
                    "test_output": test_output,
                    "error_details": error_details,
                    "exec_time": exec_time,
                    "memory": memory,
                }
            )

        def on_all_tests_completed(all_passed):
            all_tests_done.append(all_passed)

        validator.testCompleted.connect(on_test_completed)
        validator.allTestsCompleted.connect(on_all_tests_completed)

        # Run 5 validation tests
        validator.run_validation_test(test_count=5)

        # Wait for completion
        qtbot.waitUntil(lambda: len(all_tests_done) > 0, timeout=30000)

        # Verify results
        assert len(completed_tests) == 5, "Should complete 5 tests"
        assert all_tests_done[0] is True, "All tests should pass"

        # Verify each test has "Correct" verdict
        for test in completed_tests:
            assert test["passed"] is True, f"Test {test['test_num']} should pass"
            assert (
                test["validation_message"] == "Correct"
            ), "Should have Correct verdict"
            assert (
                test["validator_exit_code"] == 0
            ), "Exit code should be 0 for Accepted"
            assert test["input_data"], "Should have input data"
            assert test["test_output"], "Should have output data"
            assert test["exec_time"] > 0, "Should track execution time"
            assert test["memory"] >= 0, "Should track memory usage"

    def test_detects_wrong_answer(self, cpp_wrong_answer_workspace, qtbot):
        """Test that Wrong Answer verdicts are properly detected."""
        validator = ValidatorRunner(str(cpp_wrong_answer_workspace))

        # Compile first
        compilation_done = []
        validator.compilationFinished.connect(
            lambda success: compilation_done.append(success)
        )
        validator.compile_all()
        qtbot.waitUntil(lambda: len(compilation_done) > 0, timeout=30000)

        completed_tests = []
        all_tests_done = []

        def on_test_completed(
            test_num,
            passed,
            input_data,
            test_output,
            validation_message,
            error_details,
            validator_exit_code,
            exec_time,
            memory,
        ):
            completed_tests.append(
                {
                    "passed": passed,
                    "validation_message": validation_message,
                    "validator_exit_code": validator_exit_code,
                }
            )

        validator.testCompleted.connect(on_test_completed)
        validator.allTestsCompleted.connect(
            lambda passed: all_tests_done.append(passed)
        )

        # Run tests
        validator.run_validation_test(test_count=3)
        qtbot.waitUntil(lambda: len(all_tests_done) > 0, timeout=30000)

        # All tests should fail with Wrong Answer (unsorted input → unsorted output → WA)
        assert all_tests_done[0] is False, "Tests should fail with wrong answers"
        assert len(completed_tests) == 3

        for test in completed_tests:
            assert test["passed"] is False, "Test should fail"
            assert (
                test["validation_message"] == "Wrong Answer"
            ), "Should detect wrong answer"
            assert test["validator_exit_code"] == 1, "Exit code should be 1 for WA"


class TestDatabaseIntegration:
    """Test database persistence for validation results."""

    def test_saves_validation_results(self, cpp_validator_workspace, temp_db, qtbot):
        """Test that validation results are saved to database correctly."""
        validator = ValidatorRunner(str(cpp_validator_workspace))
        validator.db_manager = temp_db

        # Compile first
        compilation_done = []
        validator.compilationFinished.connect(
            lambda success: compilation_done.append(success)
        )
        validator.compile_all()
        qtbot.waitUntil(lambda: len(compilation_done) > 0, timeout=30000)

        all_tests_done = []
        validator.allTestsCompleted.connect(
            lambda passed: all_tests_done.append(passed)
        )

        # Run validation tests
        validator.run_validation_test(test_count=5)
        qtbot.waitUntil(lambda: len(all_tests_done) > 0, timeout=30000)

        # Save to database
        result_id = validator.save_test_results_to_database()
        assert result_id is not None, "Should return result ID"

        # Retrieve from database
        results = temp_db.get_test_results(limit=1)
        assert len(results) == 1, "Should have one saved result"

        result = results[0]
        assert result.test_type == "validator"
        assert result.test_count == 5
        assert result.passed_tests == 5
        assert result.failed_tests == 0

    def test_saves_validation_analysis(self, cpp_validator_workspace, temp_db, qtbot):
        """Test that validation analysis is saved correctly."""
        validator = ValidatorRunner(str(cpp_validator_workspace))
        validator.db_manager = temp_db

        # Compile first
        compilation_done = []
        validator.compilationFinished.connect(
            lambda success: compilation_done.append(success)
        )
        validator.compile_all()
        qtbot.waitUntil(lambda: len(compilation_done) > 0, timeout=30000)

        all_tests_done = []
        validator.allTestsCompleted.connect(
            lambda passed: all_tests_done.append(passed)
        )

        validator.run_validation_test(test_count=5)
        qtbot.waitUntil(lambda: len(all_tests_done) > 0, timeout=30000)

        result_id = validator.save_test_results_to_database()

        # Retrieve and verify validation analysis
        results = temp_db.get_test_results(limit=1)
        result = results[0]
        assert result.mismatch_analysis is not None

        analysis = json.loads(result.mismatch_analysis)
        assert "test_count" in analysis
        assert "validation_summary" in analysis
        assert "execution_times" in analysis

        # Verify validation summary
        summary = analysis["validation_summary"]
        assert summary["correct_outputs"] == 5
        assert summary["wrong_answers"] == 0
        assert summary["presentation_errors"] == 0
        assert summary["validator_errors"] == 0

        # Verify execution times
        times = analysis["execution_times"]
        assert "avg_generator" in times
        assert "avg_test" in times
        assert "avg_validator" in times
        assert times["avg_generator"] >= 0
        assert times["avg_test"] >= 0
        assert times["avg_validator"] >= 0

    def test_saves_wrong_answer_analysis(
        self, cpp_wrong_answer_workspace, temp_db, qtbot
    ):
        """Test that wrong answer analysis is saved correctly."""
        validator = ValidatorRunner(str(cpp_wrong_answer_workspace))
        validator.db_manager = temp_db

        # Compile first
        compilation_done = []
        validator.compilationFinished.connect(
            lambda success: compilation_done.append(success)
        )
        validator.compile_all()
        qtbot.waitUntil(lambda: len(compilation_done) > 0, timeout=30000)

        all_tests_done = []
        validator.allTestsCompleted.connect(
            lambda passed: all_tests_done.append(passed)
        )

        validator.run_validation_test(test_count=3)
        qtbot.waitUntil(lambda: len(all_tests_done) > 0, timeout=30000)

        result_id = validator.save_test_results_to_database()

        # Retrieve and verify
        results = temp_db.get_test_results(limit=1)
        result = results[0]

        assert result.test_count == 3
        assert result.passed_tests == 0
        assert result.failed_tests == 3

        analysis = json.loads(result.mismatch_analysis)
        summary = analysis["validation_summary"]
        assert summary["correct_outputs"] == 0
        assert summary["wrong_answers"] == 3

    def test_saves_files_snapshot(self, cpp_validator_workspace, temp_db, qtbot):
        """Test that files snapshot is saved correctly."""
        validator = ValidatorRunner(str(cpp_validator_workspace))
        validator.db_manager = temp_db

        # Compile first
        compilation_done = []
        validator.compilationFinished.connect(
            lambda success: compilation_done.append(success)
        )
        validator.compile_all()
        qtbot.waitUntil(lambda: len(compilation_done) > 0, timeout=30000)

        all_tests_done = []
        validator.allTestsCompleted.connect(
            lambda passed: all_tests_done.append(passed)
        )

        validator.run_validation_test(test_count=2)
        qtbot.waitUntil(lambda: len(all_tests_done) > 0, timeout=30000)

        result_id = validator.save_test_results_to_database()
        results = temp_db.get_test_results(limit=1)
        result = results[0]

        # Verify files snapshot exists (may be empty for test workspaces)
        assert result.files_snapshot is not None
        snapshot = json.loads(result.files_snapshot)
        assert isinstance(snapshot, dict), "Snapshot should be a dictionary"
        assert "test_type" in snapshot, "Snapshot should have test_type"
        assert snapshot["test_type"] == "validation", "Should be validation type"


class TestMetricsTracking:
    """Test execution metrics tracking."""

    def test_tracks_execution_times(self, cpp_validator_workspace, qtbot):
        """Test that execution times are tracked for all 3 stages."""
        validator = ValidatorRunner(str(cpp_validator_workspace))

        # Compile first
        compilation_done = []
        validator.compilationFinished.connect(
            lambda success: compilation_done.append(success)
        )
        validator.compile_all()
        qtbot.waitUntil(lambda: len(compilation_done) > 0, timeout=30000)

        completed_tests = []
        all_tests_done = []

        def on_test_completed(
            test_num,
            passed,
            input_data,
            test_output,
            validation_message,
            error_details,
            validator_exit_code,
            exec_time,
            memory,
        ):
            completed_tests.append(
                {
                    "exec_time": exec_time,
                    "memory": memory,
                }
            )

        validator.testCompleted.connect(on_test_completed)
        validator.allTestsCompleted.connect(lambda p: all_tests_done.append(p))

        validator.run_validation_test(test_count=5)
        qtbot.waitUntil(lambda: len(all_tests_done) > 0, timeout=30000)

        # Verify all tests have execution times
        assert len(completed_tests) == 5
        for test in completed_tests:
            assert test["exec_time"] > 0, "Should track total execution time"
            assert test["memory"] >= 0, "Should track memory (can be 0 for fast tests)"

    def test_tracks_memory_usage(self, cpp_validator_workspace, qtbot):
        """Test that memory usage is tracked."""
        validator = ValidatorRunner(str(cpp_validator_workspace))

        # Compile first
        compilation_done = []
        validator.compilationFinished.connect(
            lambda success: compilation_done.append(success)
        )
        validator.compile_all()
        qtbot.waitUntil(lambda: len(compilation_done) > 0, timeout=30000)

        completed_tests = []
        all_tests_done = []

        def on_test_completed(
            test_num,
            passed,
            input_data,
            test_output,
            validation_message,
            error_details,
            validator_exit_code,
            exec_time,
            memory,
        ):
            completed_tests.append({"memory": memory})

        validator.testCompleted.connect(on_test_completed)
        validator.allTestsCompleted.connect(lambda p: all_tests_done.append(p))

        validator.run_validation_test(test_count=3)
        qtbot.waitUntil(lambda: len(all_tests_done) > 0, timeout=30000)

        # Verify memory tracking
        for test in completed_tests:
            assert test["memory"] >= 0, "Should track memory usage"


class TestIOFileManagement:
    """Test I/O file saving functionality."""

    def test_saves_io_files(self, cpp_validator_workspace, qtbot):
        """Test that input and output files are saved correctly."""
        validator = ValidatorRunner(str(cpp_validator_workspace))

        # Compile first
        compilation_done = []
        validator.compilationFinished.connect(
            lambda success: compilation_done.append(success)
        )
        validator.compile_all()
        qtbot.waitUntil(lambda: len(compilation_done) > 0, timeout=30000)

        all_tests_done = []
        validator.allTestsCompleted.connect(lambda p: all_tests_done.append(p))

        validator.run_validation_test(test_count=3)
        qtbot.waitUntil(lambda: len(all_tests_done) > 0, timeout=30000)

        # Verify I/O files are created in nested structure
        workspace = Path(cpp_validator_workspace)
        validator_dir = workspace / "validator"
        inputs_dir = validator_dir / "inputs"
        outputs_dir = validator_dir / "outputs"

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

    def test_parallel_execution(self, cpp_validator_workspace, qtbot):
        """Test that multiple tests run in parallel."""
        validator = ValidatorRunner(str(cpp_validator_workspace))

        # Compile first
        compilation_done = []
        validator.compilationFinished.connect(
            lambda success: compilation_done.append(success)
        )
        validator.compile_all()
        qtbot.waitUntil(lambda: len(compilation_done) > 0, timeout=30000)

        all_tests_done = []
        start_time = time.time()

        validator.allTestsCompleted.connect(lambda p: all_tests_done.append(p))

        # Run 10 tests - should be faster in parallel than sequential
        validator.run_validation_test(test_count=10, max_workers=4)
        qtbot.waitUntil(lambda: len(all_tests_done) > 0, timeout=30000)

        total_time = time.time() - start_time

        # With parallel execution, should complete in reasonable time
        assert (
            total_time < 15.0
        ), f"Parallel execution should complete quickly (took {total_time:.2f}s)"


class TestErrorHandling:
    """Test error handling scenarios."""

    def test_compilation_failure(self, tmp_path, qtbot):
        """Test handling of compilation failures."""
        workspace = tmp_path / "cpp_bad"
        validator_dir = workspace / "validator"
        validator_dir.mkdir(parents=True)

        # Invalid C++ code
        (validator_dir / "generator.cpp").write_text(
            """
#include <iostream>
int main() {
    SYNTAX ERROR HERE!!!
    return 0;
}
"""
        )

        (validator_dir / "test.cpp").write_text(
            """
#include <iostream>
int main() {
    std::cout << "test" << std::endl;
    return 0;
}
"""
        )

        (validator_dir / "validator.cpp").write_text(
            """
#include <iostream>
int main() {
    return 0;
}
"""
        )

        validator = ValidatorRunner(str(workspace))

        compilation_results = []
        validator.compilationFinished.connect(
            lambda success: compilation_results.append(success)
        )

        validator.compile_all()
        qtbot.waitUntil(lambda: len(compilation_results) > 0, timeout=30000)

        # Should detect compilation failure
        assert compilation_results[0] is False, "Should detect compilation failure"

    def test_generator_runtime_error(self, tmp_path, qtbot):
        """Test handling of generator runtime errors."""
        workspace = tmp_path / "cpp_gen_error"
        validator_dir = workspace / "validator"
        validator_dir.mkdir(parents=True)

        # Generator that crashes
        (validator_dir / "generator.cpp").write_text(
            """
#include <iostream>
#include <cstdlib>
int main() {
    std::abort();  // Crash immediately
    return 0;
}
"""
        )

        (validator_dir / "test.cpp").write_text(
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

        (validator_dir / "validator.cpp").write_text(
            """
#include <iostream>
int main() {
    return 0;
}
"""
        )

        validator = ValidatorRunner(str(workspace))

        # Compile first
        compilation_done = []
        validator.compilationFinished.connect(
            lambda success: compilation_done.append(success)
        )
        validator.compile_all()
        qtbot.waitUntil(lambda: len(compilation_done) > 0, timeout=30000)

        completed_tests = []
        all_tests_done = []

        def on_test_completed(
            test_num,
            passed,
            input_data,
            test_output,
            validation_message,
            error_details,
            validator_exit_code,
            exec_time,
            memory,
        ):
            completed_tests.append(passed)

        validator.testCompleted.connect(on_test_completed)
        validator.allTestsCompleted.connect(lambda p: all_tests_done.append(p))

        validator.run_validation_test(test_count=2)
        qtbot.waitUntil(lambda: len(all_tests_done) > 0, timeout=30000)

        # Tests should fail due to generator error
        assert all_tests_done[0] is False, "Should fail when generator crashes"
        assert all(not passed for passed in completed_tests), "All tests should fail"

    def test_test_solution_runtime_error(self, tmp_path, qtbot):
        """Test handling of test solution runtime errors."""
        workspace = tmp_path / "cpp_test_error"
        validator_dir = workspace / "validator"
        validator_dir.mkdir(parents=True)

        # Working generator
        (validator_dir / "generator.cpp").write_text(CPP_VALIDATOR_SET["generator"])

        # Test solution that crashes
        (validator_dir / "test.cpp").write_text(
            """
#include <iostream>
#include <cstdlib>
int main() {
    std::abort();  // Crash
    return 0;
}
"""
        )

        # Working validator
        (validator_dir / "validator.cpp").write_text(CPP_VALIDATOR_SET["validator"])

        validator = ValidatorRunner(str(workspace))

        # Compile first
        compilation_done = []
        validator.compilationFinished.connect(
            lambda success: compilation_done.append(success)
        )
        validator.compile_all()
        qtbot.waitUntil(lambda: len(compilation_done) > 0, timeout=30000)

        completed_tests = []
        all_tests_done = []

        def on_test_completed(
            test_num,
            passed,
            input_data,
            test_output,
            validation_message,
            error_details,
            validator_exit_code,
            exec_time,
            memory,
        ):
            completed_tests.append(
                {"passed": passed, "validation_message": validation_message}
            )

        validator.testCompleted.connect(on_test_completed)
        validator.allTestsCompleted.connect(lambda p: all_tests_done.append(p))

        validator.run_validation_test(test_count=2)
        qtbot.waitUntil(lambda: len(all_tests_done) > 0, timeout=30000)

        # Tests should fail
        assert all_tests_done[0] is False, "Should fail when test solution crashes"
        for test in completed_tests:
            assert test["passed"] is False, "Tests should fail"


class TestCompleteWorkflow:
    """Test complete end-to-end workflow."""

    def test_complete_validation_workflow(
        self, cpp_validator_workspace, temp_db, qtbot
    ):
        """Test full workflow: compile → run → save → retrieve → verify."""
        validator = ValidatorRunner(str(cpp_validator_workspace))
        validator.db_manager = temp_db

        # Track all signals
        compilation_done = []
        completed_tests = []
        all_tests_done = []

        def on_compilation_finished(success):
            compilation_done.append(success)

        def on_test_completed(
            test_num,
            passed,
            input_data,
            test_output,
            validation_message,
            error_details,
            validator_exit_code,
            exec_time,
            memory,
        ):
            completed_tests.append(
                {
                    "test_num": test_num,
                    "passed": passed,
                    "validation_message": validation_message,
                    "validator_exit_code": validator_exit_code,
                    "exec_time": exec_time,
                    "memory": memory,
                }
            )

        def on_all_tests_completed(all_passed):
            all_tests_done.append(all_passed)

        validator.compilationFinished.connect(on_compilation_finished)
        validator.testCompleted.connect(on_test_completed)
        validator.allTestsCompleted.connect(on_all_tests_completed)

        # Compile first
        validator.compile_all()
        qtbot.waitUntil(lambda: len(compilation_done) > 0, timeout=30000)

        # Verify compilation
        assert len(compilation_done) > 0, "Should emit compilation signal"
        assert compilation_done[0] is True, "Compilation should succeed"

        # Run validation tests
        validator.run_validation_test(test_count=5)

        # Wait for completion
        qtbot.waitUntil(lambda: len(all_tests_done) > 0, timeout=30000)

        # Verify test execution
        assert len(completed_tests) == 5, "Should run 5 tests"
        assert all(t["passed"] for t in completed_tests), "All tests should pass"
        assert all_tests_done[0] is True, "All tests should pass"

        # Verify all verdicts are "Correct"
        for test in completed_tests:
            assert test["validation_message"] == "Correct"
            assert test["validator_exit_code"] == 0
            assert test["exec_time"] > 0
            assert test["memory"] >= 0

        # Save to database
        result_id = validator.save_test_results_to_database()
        assert result_id is not None

        # Retrieve and verify
        results = temp_db.get_test_results(limit=1)
        result = results[0]
        assert result is not None
        assert result.test_type == "validator"
        assert result.test_count == 5
        assert result.passed_tests == 5
        assert result.failed_tests == 0

        # Verify test details
        test_details = json.loads(result.test_details)
        assert len(test_details) == 5
        for detail in test_details:
            assert detail["passed"] is True
            assert detail["validation_message"] == "Correct"
            assert detail["validator_exit_code"] == 0
            assert detail["total_time"] > 0
            assert detail["memory"] >= 0

        # Verify validation analysis
        analysis = json.loads(result.mismatch_analysis)
        assert analysis["test_count"] == 5
        assert analysis["validation_summary"]["correct_outputs"] == 5
        assert analysis["validation_summary"]["wrong_answers"] == 0
        assert analysis["execution_times"]["avg_generator"] >= 0
        assert analysis["execution_times"]["avg_test"] >= 0
        assert analysis["execution_times"]["avg_validator"] >= 0

        # Verify files snapshot
        snapshot = json.loads(result.files_snapshot)
        assert "test_type" in snapshot
        assert snapshot["test_type"] == "validation"

        # Verify I/O files were created
        workspace = Path(cpp_validator_workspace)
        inputs_dir = workspace / "validator" / "inputs"
        outputs_dir = workspace / "validator" / "outputs"

        for i in range(1, 6):
            assert (inputs_dir / f"input_{i}.txt").exists()
            assert (outputs_dir / f"output_{i}.txt").exists()
