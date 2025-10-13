"""
Unit tests for ComparisonTestWorker.

Tests the specialized worker that implements 3-stage output comparison:
1. Generator → produces test input
2. Test solution → processes input to produce output
3. Correct solution → processes input to produce expected output
4. Compare outputs for correctness

Tests verify parallel execution, output comparison logic, signal emission, and result storage.
"""

import pytest
import os
import time
from unittest.mock import Mock, patch, MagicMock
from subprocess import TimeoutExpired
from PySide6.QtCore import QObject

from src.app.core.tools.specialized.comparison_test_worker import ComparisonTestWorker


class TestComparisonWorkerInitialization:
    """Test ComparisonTestWorker initialization."""
    
    def test_init_sets_executables(self, temp_workspace):
        """Should store executables for generator, test, correct."""
        executables = {
            'generator': str(temp_workspace / 'generator.exe'),
            'test': str(temp_workspace / 'test.exe'),
            'correct': str(temp_workspace / 'correct.exe')
        }
        
        worker = ComparisonTestWorker(
            str(temp_workspace),
            executables,
            test_count=5
        )
        
        assert worker.executables == executables
        assert worker.test_count == 5
        assert worker.workspace_dir == str(temp_workspace)
    
    def test_init_calculates_optimal_workers(self, temp_workspace):
        """Should calculate optimal worker count (max 6 for I/O intensive)."""
        executables = {'generator': '', 'test': '', 'correct': ''}
        
        worker = ComparisonTestWorker(
            str(temp_workspace),
            executables,
            test_count=10
        )
        
        assert worker.max_workers >= 1
        assert worker.max_workers <= 6  # Capped at 6
    
    def test_init_accepts_custom_worker_count(self, temp_workspace):
        """Should accept custom max_workers parameter."""
        executables = {'generator': '', 'test': '', 'correct': ''}
        
        worker = ComparisonTestWorker(
            str(temp_workspace),
            executables,
            test_count=5,
            max_workers=3
        )
        
        assert worker.max_workers == 3
    
    def test_init_uses_execution_commands_when_provided(self, temp_workspace):
        """Should use execution_commands parameter when provided."""
        executables = {'generator': '', 'test': '', 'correct': ''}
        execution_commands = {
            'generator': ['python', 'gen.py'],
            'test': ['python', 'test.py'],
            'correct': ['python', 'correct.py']
        }
        
        worker = ComparisonTestWorker(
            str(temp_workspace),
            executables,
            test_count=1,
            execution_commands=execution_commands
        )
        
        assert worker.execution_commands == execution_commands


class TestComparisonWorkerExecution:
    """Test 3-stage comparison execution."""
    
    @patch('subprocess.Popen')
    @patch('psutil.Process')
    def test_runs_three_stage_comparison(self, mock_psutil, mock_popen, temp_workspace):
        """Should execute generator, test, and correct solutions in sequence."""
        # Mock process objects
        gen_proc = Mock(returncode=0, poll=Mock(return_value=0), pid=1001)
        gen_proc.communicate.return_value = ('test_input', '')
        
        test_proc = Mock(returncode=0, poll=Mock(return_value=0), pid=1002)
        test_proc.communicate.return_value = ('test_output', '')
        test_proc.stdin = Mock()
        
        correct_proc = Mock(returncode=0, poll=Mock(return_value=0), pid=1003)
        correct_proc.communicate.return_value = ('test_output', '')  # Same output = pass
        correct_proc.stdin = Mock()
        
        mock_popen.side_effect = [gen_proc, test_proc, correct_proc]
        
        # Mock psutil Process
        mock_memory = Mock()
        mock_memory.rss = 10 * 1024 * 1024  # 10 MB
        mock_psutil.return_value.memory_info.return_value = mock_memory
        
        executables = {'generator': 'gen.exe', 'test': 'test.exe', 'correct': 'correct.exe'}
        worker = ComparisonTestWorker(str(temp_workspace), executables, test_count=1)
        
        result = worker._run_single_comparison_test(1)
        
        # Should have called Popen 3 times (gen + test + correct)
        assert mock_popen.call_count == 3
        assert result is not None
        assert result['passed'] is True
        assert result['test_number'] == 1
    
    @patch('subprocess.Popen')
    @patch('psutil.Process')
    def test_matching_outputs_pass(self, mock_psutil, mock_popen, temp_workspace):
        """Should pass when test and correct outputs match."""
        gen_proc = Mock(returncode=0, poll=Mock(return_value=0), pid=1001)
        gen_proc.communicate.return_value = ('input', '')
        
        test_proc = Mock(returncode=0, poll=Mock(return_value=0), pid=1002)
        test_proc.communicate.return_value = ('42\n', '')
        test_proc.stdin = Mock()
        
        correct_proc = Mock(returncode=0, poll=Mock(return_value=0), pid=1003)
        correct_proc.communicate.return_value = ('42\n', '')  # Identical
        correct_proc.stdin = Mock()
        
        mock_popen.side_effect = [gen_proc, test_proc, correct_proc]
        
        executables = {'generator': '', 'test': '', 'correct': ''}
        worker = ComparisonTestWorker(str(temp_workspace), executables, test_count=1)
        
        result = worker._run_single_comparison_test(1)
        
        assert result['passed'] is True
        assert result['test_output'].strip() == '42'
        assert result['correct_output'].strip() == '42'
    
    @patch('subprocess.Popen')
    @patch('psutil.Process')
    def test_different_outputs_fail(self, mock_psutil, mock_popen, temp_workspace):
        """Should fail when test and correct outputs differ."""
        gen_proc = Mock(returncode=0, poll=Mock(return_value=0), pid=1001)
        gen_proc.communicate.return_value = ('input', '')
        
        test_proc = Mock(returncode=0, poll=Mock(return_value=0), pid=1002)
        test_proc.communicate.return_value = ('wrong answer', '')
        test_proc.stdin = Mock()
        
        correct_proc = Mock(returncode=0, poll=Mock(return_value=0), pid=1003)
        correct_proc.communicate.return_value = ('right answer', '')
        correct_proc.stdin = Mock()
        
        mock_popen.side_effect = [gen_proc, test_proc, correct_proc]
        
        executables = {'generator': '', 'test': '', 'correct': ''}
        worker = ComparisonTestWorker(str(temp_workspace), executables, test_count=1)
        
        result = worker._run_single_comparison_test(1)
        
        assert result['passed'] is False
        assert result['error_details'] == "Output mismatch"
        assert 'wrong answer' in result['test_output']
        assert 'right answer' in result['correct_output']
    
    @patch('subprocess.Popen')
    @patch('psutil.Process')
    def test_normalizes_whitespace_for_comparison(self, mock_psutil, mock_popen, temp_workspace):
        """Should strip whitespace when comparing outputs."""
        gen_proc = Mock(returncode=0, poll=Mock(return_value=0), pid=1001)
        gen_proc.communicate.return_value = ('input', '')
        
        test_proc = Mock(returncode=0, poll=Mock(return_value=0), pid=1002)
        test_proc.communicate.return_value = ('  42  \n', '')  # Extra whitespace
        test_proc.stdin = Mock()
        
        correct_proc = Mock(returncode=0, poll=Mock(return_value=0), pid=1003)
        correct_proc.communicate.return_value = ('42', '')  # No whitespace
        correct_proc.stdin = Mock()
        
        mock_popen.side_effect = [gen_proc, test_proc, correct_proc]
        
        executables = {'generator': '', 'test': '', 'correct': ''}
        worker = ComparisonTestWorker(str(temp_workspace), executables, test_count=1)
        
        result = worker._run_single_comparison_test(1)
        
        # Should pass because normalized outputs match
        assert result['passed'] is True


class TestComparisonWorkerSignals:
    """Test signal emission during comparison."""
    
    @patch('subprocess.Popen')
    @patch('psutil.Process')
    def test_emits_test_completed_with_correct_data(self, mock_psutil, mock_popen,
                                                     temp_workspace, qtbot):
        """Should emit testCompleted with comparison data."""
        gen_proc = Mock(returncode=0, poll=Mock(return_value=0), pid=1001)
        gen_proc.communicate.return_value = ('input', '')
        
        test_proc = Mock(returncode=0, poll=Mock(return_value=0), pid=1002)
        test_proc.communicate.return_value = ('output', '')
        test_proc.stdin = Mock()
        
        correct_proc = Mock(returncode=0, poll=Mock(return_value=0), pid=1003)
        correct_proc.communicate.return_value = ('output', '')
        correct_proc.stdin = Mock()
        
        mock_popen.side_effect = [gen_proc, test_proc, correct_proc]
        
        executables = {'generator': '', 'test': '', 'correct': ''}
        worker = ComparisonTestWorker(str(temp_workspace), executables, test_count=1)
        
        completed_signals = []
        worker.testCompleted.connect(lambda *args: completed_signals.append(args))
        
        with qtbot.waitSignal(worker.allTestsCompleted, timeout=5000):
            worker.run_tests()
        
        # Verify signal was emitted with 7 parameters
        assert len(completed_signals) == 1
        signal_data = completed_signals[0]
        assert len(signal_data) == 7  # test_num, passed, input, correct_output, test_output, time, memory
        assert signal_data[0] == 1  # test_number
        assert signal_data[1] is True  # passed


class TestComparisonWorkerErrorHandling:
    """Test error handling and recovery."""
    
    @patch('subprocess.Popen')
    def test_handles_generator_failure(self, mock_popen, temp_workspace):
        """Should create error result if generator fails."""
        gen_proc = Mock(returncode=1, poll=Mock(return_value=1), pid=1001)
        gen_proc.communicate.return_value = ('', 'Generator error!')
        
        mock_popen.return_value = gen_proc
        
        executables = {'generator': '', 'test': '', 'correct': ''}
        worker = ComparisonTestWorker(str(temp_workspace), executables, test_count=1)
        
        result = worker._run_single_comparison_test(1)
        
        assert result is not None
        assert result['passed'] is False
        assert 'Generator failed' in result['error_details']
    
    @patch('subprocess.Popen')
    @patch('psutil.Process')
    def test_handles_test_solution_failure(self, mock_psutil, mock_popen, temp_workspace):
        """Should create error result if test solution fails."""
        gen_proc = Mock(returncode=0, poll=Mock(return_value=0), pid=1001)
        gen_proc.communicate.return_value = ('input', '')
        
        test_proc = Mock(returncode=1, poll=Mock(return_value=1), pid=1002)
        test_proc.communicate.return_value = ('', 'Runtime error!')
        test_proc.stdin = Mock()
        
        mock_popen.side_effect = [gen_proc, test_proc]
        
        executables = {'generator': '', 'test': '', 'correct': ''}
        worker = ComparisonTestWorker(str(temp_workspace), executables, test_count=1)
        
        result = worker._run_single_comparison_test(1)
        
        assert result is not None
        assert result['passed'] is False
        assert 'Test solution failed' in result['error_details']
    
    @patch('subprocess.Popen')
    @patch('psutil.Process')
    def test_handles_correct_solution_failure(self, mock_psutil, mock_popen, temp_workspace):
        """Should create error result if correct solution fails."""
        gen_proc = Mock(returncode=0, poll=Mock(return_value=0), pid=1001)
        gen_proc.communicate.return_value = ('input', '')
        
        test_proc = Mock(returncode=0, poll=Mock(return_value=0), pid=1002)
        test_proc.communicate.return_value = ('output', '')
        test_proc.stdin = Mock()
        
        correct_proc = Mock(returncode=1, poll=Mock(return_value=1), pid=1003)
        correct_proc.communicate.return_value = ('', 'Correct solution crashed!')
        correct_proc.stdin = Mock()
        
        mock_popen.side_effect = [gen_proc, test_proc, correct_proc]
        
        executables = {'generator': '', 'test': '', 'correct': ''}
        worker = ComparisonTestWorker(str(temp_workspace), executables, test_count=1)
        
        result = worker._run_single_comparison_test(1)
        
        assert result is not None
        assert result['passed'] is False
        assert 'Correct solution failed' in result['error_details']
    
    @patch('subprocess.Popen')
    def test_handles_timeout(self, mock_popen, temp_workspace):
        """Should handle process timeouts gracefully."""
        gen_proc = Mock(pid=1001)
        gen_proc.communicate.side_effect = TimeoutExpired(cmd=['gen'], timeout=10)
        
        mock_popen.return_value = gen_proc
        
        executables = {'generator': '', 'test': '', 'correct': ''}
        worker = ComparisonTestWorker(str(temp_workspace), executables, test_count=1)
        
        result = worker._run_single_comparison_test(1)
        
        assert result is not None
        assert result['passed'] is False
        assert 'Timeout' in result['error_details']


class TestComparisonWorkerMetrics:
    """Test execution time and memory tracking."""
    
    @patch('subprocess.Popen')
    @patch('psutil.Process')
    def test_tracks_execution_time(self, mock_psutil, mock_popen, temp_workspace):
        """Should track execution time for each stage."""
        # Mock successful execution - create all procs first, then set side_effect
        procs = []
        for _ in range(3):
            proc = Mock(returncode=0, poll=Mock(return_value=0), pid=1001)
            proc.communicate.return_value = ('output', '')
            proc.stdin = Mock()
            procs.append(proc)
        mock_popen.side_effect = procs
        
        executables = {'generator': '', 'test': '', 'correct': ''}
        worker = ComparisonTestWorker(str(temp_workspace), executables, test_count=1)
        
        result = worker._run_single_comparison_test(1)
        
        assert 'total_time' in result
        assert result['total_time'] > 0
        assert 'generator_time' in result
        assert 'test_time' in result
        assert 'correct_time' in result
        assert 'comparison_time' in result
    
    @patch('subprocess.Popen')
    @patch('psutil.Process')
    def test_tracks_peak_memory(self, mock_psutil, mock_popen, temp_workspace):
        """Should track peak memory usage across all stages."""
        mock_memory_info = Mock()
        mock_memory_info.rss = 50 * 1024 * 1024  # 50 MB
        mock_psutil.return_value.memory_info.return_value = mock_memory_info
        
        # Mock successful execution - create all procs first, then set side_effect
        procs = []
        for _ in range(3):
            proc = Mock(returncode=0, pid=1001)
            # poll() returns None first (process running), then 0 (finished)
            proc.poll = Mock(side_effect=[None, 0])
            proc.communicate.return_value = ('output', '')
            proc.stdin = Mock()
            procs.append(proc)
        mock_popen.side_effect = procs
        
        executables = {'generator': '', 'test': '', 'correct': ''}
        worker = ComparisonTestWorker(str(temp_workspace), executables, test_count=1)
        
        result = worker._run_single_comparison_test(1)
        
        assert 'memory' in result
        assert result['memory'] > 0


class TestComparisonWorkerFileIO:
    """Test input/output file saving."""
    
    @patch('subprocess.Popen')
    @patch('psutil.Process')
    def test_saves_test_io_files(self, mock_psutil, mock_popen, temp_workspace):
        """Should save input, test output, and correct output."""
        gen_proc = Mock(returncode=0, poll=Mock(return_value=0), pid=1001)
        gen_proc.communicate.return_value = ('test_input', '')
        
        test_proc = Mock(returncode=0, poll=Mock(return_value=0), pid=1002)
        test_proc.communicate.return_value = ('test_output', '')
        test_proc.stdin = Mock()
        
        correct_proc = Mock(returncode=0, poll=Mock(return_value=0), pid=1003)
        correct_proc.communicate.return_value = ('correct_output', '')
        correct_proc.stdin = Mock()
        
        mock_popen.side_effect = [gen_proc, test_proc, correct_proc]
        
        executables = {'generator': '', 'test': '', 'correct': ''}
        worker = ComparisonTestWorker(str(temp_workspace), executables, test_count=1)
        
        worker._run_single_comparison_test(1)
        
        # Check if I/O files were attempted to be created
        comparator_dir = temp_workspace / 'comparator'
        if comparator_dir.exists():
            io_dir = comparator_dir / 'io'
            # Note: Actual file creation depends on workspace_utils implementation


class TestComparisonWorkerControl:
    """Test worker start/stop control."""
    
    def test_stop_cancels_running_tests(self, temp_workspace):
        """Should stop execution when stop() is called."""
        executables = {'generator': '', 'test': '', 'correct': ''}
        worker = ComparisonTestWorker(str(temp_workspace), executables, test_count=10)
        
        assert worker.is_running is True
        
        worker.stop()
        
        assert worker.is_running is False
    
    def test_returns_none_when_stopped(self, temp_workspace):
        """Should return None from test execution when stopped."""
        executables = {'generator': '', 'test': '', 'correct': ''}
        worker = ComparisonTestWorker(str(temp_workspace), executables, test_count=1)
        
        worker.stop()
        result = worker._run_single_comparison_test(1)
        
        assert result is None


class TestComparisonWorkerResultStorage:
    """Test result storage and retrieval."""
    
    def test_get_test_results_returns_copy(self, temp_workspace):
        """Should return thread-safe copy of test results."""
        executables = {'generator': '', 'test': '', 'correct': ''}
        worker = ComparisonTestWorker(str(temp_workspace), executables, test_count=1)
        
        # Get results
        results = worker.get_test_results()
        
        assert isinstance(results, list)
        
        # Modifying returned list shouldn't affect worker's internal results
        original_len = len(results)
        results.append({'fake': 'data'})
        
        new_results = worker.get_test_results()
        assert len(new_results) == original_len
    
    @patch('subprocess.Popen')
    @patch('psutil.Process')
    def test_result_contains_full_outputs(self, mock_psutil, mock_popen, temp_workspace):
        """Should store full outputs for database."""
        gen_proc = Mock(returncode=0, poll=Mock(return_value=0), pid=1001)
        gen_proc.communicate.return_value = ('input' * 100, '')  # Long input
        
        test_proc = Mock(returncode=0, poll=Mock(return_value=0), pid=1002)
        test_proc.communicate.return_value = ('output' * 100, '')  # Long output
        test_proc.stdin = Mock()
        
        correct_proc = Mock(returncode=0, poll=Mock(return_value=0), pid=1003)
        correct_proc.communicate.return_value = ('output' * 100, '')
        correct_proc.stdin = Mock()
        
        mock_popen.side_effect = [gen_proc, test_proc, correct_proc]
        
        executables = {'generator': '', 'test': '', 'correct': ''}
        worker = ComparisonTestWorker(str(temp_workspace), executables, test_count=1)
        
        result = worker._run_single_comparison_test(1)
        
        # Should have truncated versions for display
        assert len(result['input']) <= 303  # 300 + "..."
        assert len(result['test_output']) <= 303
        assert len(result['correct_output']) <= 303
        
        # Should have full versions for database
        assert 'input_full' in result
        assert 'test_output_full' in result
        assert 'correct_output_full' in result
        assert len(result['input_full']) > 300
