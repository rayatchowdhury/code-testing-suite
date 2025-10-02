"""
Unit tests for comparison test worker time and memory tracking.

Tests Phase 4 implementation: Time/Memory Tracking
"""

import os
import sys
import tempfile
import pytest
from pathlib import Path
from PySide6.QtCore import QCoreApplication

from src.app.core.tools.specialized.comparison_test_worker import ComparisonTestWorker


@pytest.fixture
def temp_workspace(tmp_path):
    """Create temporary workspace with test executables"""
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    
    # Create simple Python scripts for testing
    
    # Generator: outputs test input
    generator = workspace / "generator.py"
    generator.write_text("""
import sys
print("5 3")  # Simple test input
sys.exit(0)
""")
    
    # Test solution: adds two numbers
    test_solution = workspace / "test.py"
    test_solution.write_text("""
import sys
a, b = map(int, input().split())
print(a + b)
sys.exit(0)
""")
    
    # Correct solution: adds two numbers correctly
    correct_solution = workspace / "correct.py"
    correct_solution.write_text("""
import sys
a, b = map(int, input().split())
print(a + b)
sys.exit(0)
""")
    
    return workspace


@pytest.fixture
def worker(temp_workspace):
    """Create ComparisonTestWorker with test executables"""
    python_exe = sys.executable
    
    execution_commands = {
        'generator': [python_exe, str(temp_workspace / "generator.py")],
        'test': [python_exe, str(temp_workspace / "test.py")],
        'correct': [python_exe, str(temp_workspace / "correct.py")]
    }
    
    worker = ComparisonTestWorker(
        workspace_dir=str(temp_workspace),
        executables={},  # Not used when execution_commands is provided
        test_count=3,
        max_workers=1,
        execution_commands=execution_commands
    )
    
    return worker


class TestTimeTracking:
    """Test execution time tracking"""
    
    def test_time_tracking_positive_values(self, worker, qtbot):
        """Test that time tracking produces positive values"""
        results = []
        
        def on_test_completed(test_num, passed, inp, correct, actual, time, memory):
            results.append({
                'test_number': test_num,
                'time': time,
                'memory': memory
            })
        
        worker.testCompleted.connect(on_test_completed)
        
        # Run single test
        result = worker._run_single_comparison_test(1)
        
        assert result is not None
        assert result['total_time'] > 0.0, "Total time should be positive"
        assert result['generator_time'] >= 0.0, "Generator time should be non-negative"
        assert result['test_time'] >= 0.0, "Test time should be non-negative"
        assert result['correct_time'] >= 0.0, "Correct time should be non-negative"
    
    def test_total_time_sum(self, worker):
        """Test that total_time equals sum of stage times"""
        result = worker._run_single_comparison_test(1)
        
        assert result is not None
        
        expected_total = (
            result['generator_time'] +
            result['test_time'] +
            result['correct_time'] +
            result['comparison_time']
        )
        
        # Allow small floating point error
        assert abs(result['total_time'] - expected_total) < 0.001
    
    def test_time_tracking_in_signal(self, worker, qtbot):
        """Test that time values are emitted in signal"""
        results = []
        
        def on_test_completed(test_num, passed, inp, correct, actual, time, memory):
            results.append({'time': time})
        
        worker.testCompleted.connect(on_test_completed)
        
        # Run tests
        with qtbot.waitSignal(worker.allTestsCompleted, timeout=10000):
            worker.run_tests()
        
        # Check all results have positive time
        assert len(results) == 3, "Should have 3 test results"
        for result in results:
            assert result['time'] > 0.0, f"Time should be positive: {result['time']}"


class TestMemoryTracking:
    """Test memory usage tracking"""
    
    def test_memory_tracking_non_negative(self, worker):
        """Test that memory tracking produces non-negative values"""
        result = worker._run_single_comparison_test(1)
        
        assert result is not None
        assert result['memory'] >= 0.0, "Memory should be non-negative"
    
    def test_memory_tracking_reasonable_range(self, worker):
        """Test that memory values are in reasonable range (0-1000 MB)"""
        result = worker._run_single_comparison_test(1)
        
        assert result is not None
        assert 0.0 <= result['memory'] <= 1000.0, (
            f"Memory should be in reasonable range: {result['memory']} MB"
        )
    
    def test_memory_tracking_in_signal(self, worker, qtbot):
        """Test that memory values are emitted in signal"""
        results = []
        
        def on_test_completed(test_num, passed, inp, correct, actual, time, memory):
            results.append({'memory': memory})
        
        worker.testCompleted.connect(on_test_completed)
        
        # Run tests
        with qtbot.waitSignal(worker.allTestsCompleted, timeout=10000):
            worker.run_tests()
        
        # Check all results have non-negative memory
        assert len(results) == 3, "Should have 3 test results"
        for result in results:
            assert result['memory'] >= 0.0, f"Memory should be non-negative: {result['memory']}"


class TestErrorHandling:
    """Test error handling with partial metrics"""
    
    def test_error_result_has_zero_metrics(self, temp_workspace):
        """Test that error results have zero/minimal metrics"""
        python_exe = sys.executable
        
        # Create failing generator
        bad_generator = temp_workspace / "bad_gen.py"
        bad_generator.write_text("""
import sys
sys.exit(1)  # Fail immediately
""")
        
        execution_commands = {
            'generator': [python_exe, str(bad_generator)],
            'test': [python_exe, str(temp_workspace / "test.py")],
            'correct': [python_exe, str(temp_workspace / "correct.py")]
        }
        
        worker = ComparisonTestWorker(
            workspace_dir=str(temp_workspace),
            executables={},
            test_count=1,
            max_workers=1,
            execution_commands=execution_commands
        )
        
        result = worker._run_single_comparison_test(1)
        
        assert result is not None
        assert not result['passed'], "Test should fail"
        assert result['generator_time'] >= 0.0, "Generator time should be tracked"
        assert result['test_time'] == 0.0, "Test time should be zero (didn't run)"
        assert result['correct_time'] == 0.0, "Correct time should be zero (didn't run)"
        assert result['memory'] >= 0.0, "Memory should be non-negative"
    
    def test_partial_execution_metrics(self, temp_workspace):
        """Test metrics when test fails but generator succeeds"""
        python_exe = sys.executable
        
        # Create failing test solution
        bad_test = temp_workspace / "bad_test.py"
        bad_test.write_text("""
import sys
sys.exit(1)  # Fail immediately
""")
        
        execution_commands = {
            'generator': [python_exe, str(temp_workspace / "generator.py")],
            'test': [python_exe, str(bad_test)],
            'correct': [python_exe, str(temp_workspace / "correct.py")]
        }
        
        worker = ComparisonTestWorker(
            workspace_dir=str(temp_workspace),
            executables={},
            test_count=1,
            max_workers=1,
            execution_commands=execution_commands
        )
        
        result = worker._run_single_comparison_test(1)
        
        assert result is not None
        assert not result['passed'], "Test should fail"
        assert result['generator_time'] > 0.0, "Generator time should be tracked"
        assert result['test_time'] >= 0.0, "Test time should be tracked (even if failed)"
        assert result['correct_time'] == 0.0, "Correct didn't run"
        assert result['memory'] >= 0.0, "Memory should track what ran"


class TestSignalSignature:
    """Test that signal signature matches expected format"""
    
    def test_signal_has_seven_parameters(self, worker, qtbot):
        """Test that testCompleted signal emits 7 parameters"""
        signal_params = []
        
        def capture_signal(*args):
            signal_params.append(args)
        
        worker.testCompleted.connect(capture_signal)
        
        # Run one test
        with qtbot.waitSignal(worker.allTestsCompleted, timeout=10000):
            worker.run_tests()
        
        # Check signal parameters
        assert len(signal_params) > 0, "Should have received signals"
        
        first_signal = signal_params[0]
        assert len(first_signal) == 7, f"Signal should have 7 parameters, got {len(first_signal)}"
        
        # Check parameter types
        test_num, passed, inp, correct, actual, time, memory = first_signal
        assert isinstance(test_num, int), "test_number should be int"
        assert isinstance(passed, bool), "passed should be bool"
        assert isinstance(inp, str), "input should be str"
        assert isinstance(correct, str), "correct_output should be str"
        assert isinstance(actual, str), "test_output should be str"
        assert isinstance(time, float), "time should be float"
        assert isinstance(memory, float), "memory should be float"
    
    def test_signal_values_valid(self, worker, qtbot):
        """Test that signal values are valid and reasonable"""
        signal_params = []
        
        def capture_signal(*args):
            signal_params.append(args)
        
        worker.testCompleted.connect(capture_signal)
        
        # Run tests
        with qtbot.waitSignal(worker.allTestsCompleted, timeout=10000):
            worker.run_tests()
        
        # Validate each signal
        for test_num, passed, inp, correct, actual, time, memory in signal_params:
            assert test_num >= 1, "Test number should be positive"
            assert time >= 0.0, "Time should be non-negative"
            assert memory >= 0.0, "Memory should be non-negative"
            
            # If test passed, should have output
            if passed:
                assert inp.strip(), "Input should not be empty"
                assert correct.strip(), "Correct output should not be empty"
                assert actual.strip(), "Test output should not be empty"
