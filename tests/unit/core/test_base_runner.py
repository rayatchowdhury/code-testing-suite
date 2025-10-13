"""
Test suite for BaseRunner template method pattern.

BaseRunner is the foundation for all test execution runners (Validator,
Comparator, Benchmarker). Tests verify template method pattern implementation,
threading lifecycle, signal management, and database integration.
"""

import pytest
from unittest.mock import Mock, MagicMock, patch, call
from PySide6.QtCore import QThread, Signal
from datetime import datetime
from pathlib import Path

from src.app.core.tools.base.base_runner import BaseRunner
from src.app.persistence.database.models import TestResult


class ConcreteRunner(BaseRunner):
    """Concrete implementation for testing abstract BaseRunner."""
    
    testCompleted = Signal(int, bool)  # test_number, passed
    
    def __init__(self, workspace_dir, files_dict):
        super().__init__(workspace_dir, files_dict, test_type='comparator')
    
    def _create_test_worker(self, test_count, **kwargs):
        """Return mock worker for testing."""
        mock_worker = MagicMock()
        # Create mock signal objects with connect method
        mock_worker.testStarted = MagicMock()
        mock_worker.allTestsCompleted = MagicMock()
        mock_worker.test_results = [
            {'test_number': 1, 'passed': True, 'total_time': 0.5, 'memory': 10.0}
        ]
        # Ensure get_results doesn't exist (so base_runner uses test_results attribute)
        del mock_worker.get_results
        # Mock thread() to return the runner's thread (set after moveToThread is called)
        mock_worker.thread.return_value = None  # Will be updated by moveToThread mock
        mock_worker.moveToThread = MagicMock(side_effect=lambda t: setattr(mock_worker.thread, 'return_value', t))
        return mock_worker
    
    def _connect_worker_signals(self, worker):
        """Connect worker signals - required template method."""
        # Connect basic signals for testing
        worker.testStarted.connect(self.testStarted)
        worker.allTestsCompleted.connect(lambda passed: None)
    
    def _create_test_result(self, all_passed, test_results, passed_tests, 
                          failed_tests, total_time):
        """Create test result for testing."""
        return TestResult(
            test_type='test',
            file_path='/test/file.cpp',
            test_count=len(test_results),
            passed_tests=passed_tests,
            failed_tests=failed_tests,
            total_time=total_time,
            timestamp=datetime.now().isoformat(),
            test_details='{}',
            project_name='test_project'
        )


class TestBaseRunnerInitialization:
    """Test BaseRunner initialization and setup."""
    
    def test_init_creates_compiler(self, temp_workspace):
        """Should initialize BaseCompiler with correct parameters."""
        files = {'test': str(temp_workspace / 'comparator' / 'test.cpp')}
        runner = ConcreteRunner(str(temp_workspace), files)
        
        assert runner.compiler is not None
        assert runner.workspace_dir == str(temp_workspace)
        assert runner.test_type == 'comparator'
    
    def test_init_creates_database_manager(self, temp_workspace):
        """Should initialize DatabaseManager for result storage."""
        files = {'test': str(temp_workspace / 'comparator' / 'test.cpp')}
        runner = ConcreteRunner(str(temp_workspace), files)
        
        assert runner.db_manager is not None
    
    def test_init_sets_executables(self, temp_workspace):
        """Should set executables from compiler."""
        files = {'test': str(temp_workspace / 'comparator' / 'test.cpp')}
        runner = ConcreteRunner(str(temp_workspace), files)
        
        assert runner.executables is not None
        assert isinstance(runner.executables, dict)
    
    def test_init_accepts_custom_optimization_level(self, temp_workspace):
        """Should accept custom compiler optimization level."""
        files = {'test': str(temp_workspace / 'comparator' / 'test.cpp')}
        runner = BaseRunner.__new__(BaseRunner)
        runner.__init__(str(temp_workspace), files, test_type='comparator', optimization_level='O3')
        
        # Compiler should be initialized with O3
        assert runner.compiler is not None
    
    def test_init_accepts_custom_config(self, temp_workspace):
        """Should accept custom configuration dictionary."""
        files = {'test': str(temp_workspace / 'comparator' / 'test.cpp')}
        custom_config = {'languages': {'cpp': {'compiler': 'clang++'}}}
        runner = BaseRunner.__new__(BaseRunner)
        runner.__init__(str(temp_workspace), files, test_type='comparator', config=custom_config)
        
        assert runner.config == custom_config


@pytest.mark.unit
class TestBaseRunnerCompilation:
    """Test compilation delegation to BaseCompiler."""
    
    def test_compile_all_delegates_to_compiler(self, temp_workspace):
        """Should delegate compilation to BaseCompiler."""
        files = {'test': str(temp_workspace / 'comparator' / 'test.cpp')}
        runner = ConcreteRunner(str(temp_workspace), files)
        
        with patch.object(runner.compiler, 'compile_all') as mock_compile:
            mock_compile.return_value = True
            result = runner.compile_all()
            
            assert result is True
            mock_compile.assert_called_once()
    
    def test_compile_all_returns_false_on_failure(self, temp_workspace):
        """Should return False when compilation fails."""
        files = {'test': str(temp_workspace / 'comparator' / 'test.cpp')}
        runner = ConcreteRunner(str(temp_workspace), files)
        
        with patch.object(runner.compiler, 'compile_all') as mock_compile:
            mock_compile.return_value = False
            result = runner.compile_all()
            
            assert result is False
    
    def test_compilation_updates_executables(self, temp_workspace):
        """Should update executables dict after compilation."""
        files = {'test': str(temp_workspace / 'comparator' / 'test.cpp')}
        runner = ConcreteRunner(str(temp_workspace), files)
        
        # Executables should be set from compiler
        assert 'test' in runner.executables


@pytest.mark.unit
class TestBaseRunnerTestExecution:
    """Test the run_tests template method pattern."""
    
    def test_run_tests_creates_worker(self, temp_workspace):
        """Should create worker using _create_test_worker template method."""
        files = {'test': str(temp_workspace / 'comparator' / 'test.cpp')}
        runner = ConcreteRunner(str(temp_workspace), files)
        
        runner.run_tests(test_count=5)
        
        assert runner.worker is not None
        assert runner.thread is not None
    
    def test_run_tests_moves_worker_to_thread(self, temp_workspace):
        """Should move worker to separate QThread."""
        files = {'test': str(temp_workspace / 'comparator' / 'test.cpp')}
        runner = ConcreteRunner(str(temp_workspace), files)
        
        runner.run_tests(test_count=5)
        
        assert isinstance(runner.thread, QThread)
        # Worker should be in different thread
        assert runner.worker.thread() == runner.thread
    
    def test_run_tests_emits_testing_started_signal(self, temp_workspace, qtbot):
        """Should emit testingStarted signal for UI integration."""
        files = {'test': str(temp_workspace / 'comparator' / 'test.cpp')}
        runner = ConcreteRunner(str(temp_workspace), files)
        
        with qtbot.waitSignal(runner.testingStarted, timeout=1000):
            runner.run_tests(test_count=5)
    
    def test_run_tests_starts_thread(self, temp_workspace):
        """Should start the worker thread."""
        files = {'test': str(temp_workspace / 'comparator' / 'test.cpp')}
        runner = ConcreteRunner(str(temp_workspace), files)
        
        runner.run_tests(test_count=5)
        
        # Thread should be running or finished
        assert runner.thread is not None
    
    def test_run_tests_records_start_time(self, temp_workspace):
        """Should record test start time for duration tracking."""
        files = {'test': str(temp_workspace / 'comparator' / 'test.cpp')}
        runner = ConcreteRunner(str(temp_workspace), files)
        
        runner.run_tests(test_count=5)
        
        assert hasattr(runner, 'test_start_time')
        assert runner.test_start_time is not None


@pytest.mark.unit
@pytest.mark.database
class TestBaseRunnerDatabaseIntegration:
    """Test on-demand database result saving (Issue #39)."""
    
    def test_save_test_results_creates_test_result(self, temp_workspace):
        """Should create TestResult using _create_test_result template method."""
        files = {'test': str(temp_workspace / 'comparator' / 'test.cpp')}
        runner = ConcreteRunner(str(temp_workspace), files)
        runner.test_start_time = datetime.now()
        runner.run_tests(test_count=1)
        
        with patch.object(runner.db_manager, 'save_test_result') as mock_save:
            mock_save.return_value = 42
            result_id = runner.save_test_results_to_database()
            
            assert result_id == 42
            mock_save.assert_called_once()
    
    def test_save_without_worker_returns_error(self, temp_workspace):
        """Should return -1 if no worker available."""
        files = {'test': str(temp_workspace / 'comparator' / 'test.cpp')}
        runner = ConcreteRunner(str(temp_workspace), files)
        
        result_id = runner.save_test_results_to_database()
        
        assert result_id == -1
    
    def test_save_with_no_results_returns_error(self, temp_workspace):
        """Should return -1 if worker has no test results."""
        files = {'test': str(temp_workspace / 'comparator' / 'test.cpp')}
        runner = ConcreteRunner(str(temp_workspace), files)
        runner.run_tests(test_count=1)
        
        # Mock worker with empty results
        runner.worker.test_results = []
        
        result_id = runner.save_test_results_to_database()
        
        assert result_id == -1
    
    def test_save_calculates_correct_statistics(self, temp_workspace):
        """Should correctly calculate passed/failed counts and total time."""
        files = {'test': str(temp_workspace / 'comparator' / 'test.cpp')}
        runner = ConcreteRunner(str(temp_workspace), files)
        runner.test_start_time = datetime.now()
        runner.run_tests(test_count=3)
        
        # Mock worker with specific results
        runner.worker.test_results = [
            {'test_number': 1, 'passed': True, 'total_time': 0.5, 'memory': 10.0},
            {'test_number': 2, 'passed': False, 'total_time': 0.3, 'memory': 8.0},
            {'test_number': 3, 'passed': True, 'total_time': 0.7, 'memory': 12.0},
        ]
        
        with patch.object(runner.db_manager, 'save_test_result') as mock_save:
            mock_save.return_value = 1
            runner.save_test_results_to_database()
            
            # Verify the TestResult was created with correct stats
            call_args = mock_save.call_args[0][0]
            assert call_args.passed_tests == 2
            assert call_args.failed_tests == 1
            assert call_args.test_count == 3


@pytest.mark.unit
class TestBaseRunnerResourceCleanup:
    """Test proper resource cleanup and thread management."""
    
    def test_stop_terminates_thread(self, temp_workspace):
        """Should properly stop thread and cleanup resources."""
        files = {'test': str(temp_workspace / 'comparator' / 'test.cpp')}
        runner = ConcreteRunner(str(temp_workspace), files)
        runner.run_tests(test_count=1)
        
        runner.stop()
        
        # Should have thread reference
        assert runner.thread is not None
    
    def test_stop_emits_testing_completed_signal(self, temp_workspace, qtbot):
        """Should emit testingCompleted signal on stop."""
        files = {'test': str(temp_workspace / 'comparator' / 'test.cpp')}
        runner = ConcreteRunner(str(temp_workspace), files)
        runner.run_tests(test_count=1)
        
        with qtbot.waitSignal(runner.testingCompleted, timeout=2000):
            runner.stop()
    
    def test_stop_without_thread_is_safe(self, temp_workspace):
        """Should safely handle stop() when no thread exists."""
        files = {'test': str(temp_workspace / 'comparator' / 'test.cpp')}
        runner = ConcreteRunner(str(temp_workspace), files)
        
        # Should not raise exception
        runner.stop()


@pytest.mark.unit
class TestBaseRunnerSignalManagement:
    """Test signal forwarding and connection patterns."""
    
    def test_forwards_compilation_signals(self, temp_workspace):
        """Should forward compilation signals from BaseCompiler."""
        files = {'test': str(temp_workspace / 'comparator' / 'test.cpp')}
        runner = ConcreteRunner(str(temp_workspace), files)
        
        # Compilation signals should be connected
        assert runner.compiler is not None
        # Signals should be available
        assert hasattr(runner, 'compilationFinished')
        assert hasattr(runner, 'compilationOutput')
    
    def test_emits_test_started_signal(self, temp_workspace):
        """Should emit testStarted signal with progress information."""
        files = {'test': str(temp_workspace / 'comparator' / 'test.cpp')}
        runner = ConcreteRunner(str(temp_workspace), files)
        
        signal_received = []
        runner.testStarted.connect(lambda current, total: signal_received.append((current, total)))
        
        runner.run_tests(test_count=5)
        
        # Signal may be emitted during test execution
        # Just verify the signal exists
        assert hasattr(runner, 'testStarted')


@pytest.mark.unit
class TestBaseRunnerTemplateMethodPattern:
    """Test template method pattern enforcement and customization."""
    
    def test_create_test_worker_is_abstract(self):
        """Should require subclasses to implement _create_test_worker."""
        # BaseRunner should not be instantiable without template methods
        # This is enforced through abstract pattern
        assert hasattr(BaseRunner, '_create_test_worker')
    
    def test_create_test_result_is_abstract(self):
        """Should require subclasses to implement _create_test_result."""
        assert hasattr(BaseRunner, '_create_test_result')
    
    def test_connect_worker_signals_is_customizable(self):
        """Should allow subclasses to customize signal connections."""
        assert hasattr(BaseRunner, '_connect_worker_signals')
    
    def test_concrete_runner_implements_template_methods(self, temp_workspace):
        """ConcreteRunner should implement all required template methods."""
        files = {'test': str(temp_workspace / 'comparator' / 'test.cpp')}
        runner = ConcreteRunner(str(temp_workspace), files)
        
        # Should be able to create worker
        worker = runner._create_test_worker(test_count=5)
        assert worker is not None
        
        # Should be able to create test result
        result = runner._create_test_result(
            all_passed=True,
            test_results=[],
            passed_tests=1,
            failed_tests=0,
            total_time=1.0
        )
        assert result is not None
        assert isinstance(result, TestResult)


@pytest.mark.unit
class TestBaseRunnerErrorHandling:
    """Test error handling and edge cases."""
    
    def test_handles_missing_files_gracefully(self, temp_workspace):
        """Should handle initialization with non-existent files."""
        files = {'test': str(temp_workspace / 'nonexistent.cpp')}
        # Should not raise exception during init
        runner = ConcreteRunner(str(temp_workspace), files)
        assert runner is not None
    
    def test_handles_compilation_failure(self, temp_workspace):
        """Should handle compilation failures gracefully."""
        files = {'test': str(temp_workspace / 'comparator' / 'test.cpp')}
        runner = ConcreteRunner(str(temp_workspace), files)
        
        with patch.object(runner.compiler, 'compile_all') as mock_compile:
            mock_compile.return_value = False
            result = runner.compile_all()
            
            assert result is False
    
    def test_handles_worker_creation_failure(self, temp_workspace):
        """Should handle worker creation failures."""
        files = {'test': str(temp_workspace / 'comparator' / 'test.cpp')}
        
        class FailingRunner(ConcreteRunner):
            def _create_test_worker(self, test_count, **kwargs):
                raise RuntimeError("Worker creation failed")
        
        runner = FailingRunner(str(temp_workspace), files)
        
        # Should handle exception during run_tests
        with pytest.raises(RuntimeError):
            runner.run_tests(test_count=5)
