"""
Edge case tests for unified status views.

Tests error handling, boundary conditions, and edge cases to ensure
robust behavior under unusual circumstances.
"""

import pytest
from unittest.mock import Mock, patch
from PySide6.QtWidgets import QWidget

from src.app.presentation.views.comparator.comparator_status_view import ComparatorStatusView
from src.app.presentation.views.validator.validator_status_view import ValidatorStatusView
from src.app.presentation.views.benchmarker.benchmarker_status_view import BenchmarkerStatusView


class TestEmptyAndBoundary:
    """Test empty and boundary conditions"""
    
    def test_zero_tests(self, qtbot):
        """Test handling of zero tests"""
        view = ComparatorStatusView()
        qtbot.addWidget(view)
        
        view.on_tests_started(0)
        
        assert view.total_tests == 0
        assert view.completed_tests == 0
        assert view.passed_tests == 0
        assert view.failed_tests == 0
    
    def test_single_test(self, qtbot):
        """Test handling of single test"""
        view = ComparatorStatusView()
        qtbot.addWidget(view)
        
        view.on_tests_started(1)
        view.on_test_completed(1, True, "input", "output", "output", 0.1, 10.0)
        
        assert view.total_tests == 1
        assert view.completed_tests == 1
        assert view.passed_tests == 1
    
    def test_very_large_test_count(self, qtbot):
        """Test handling of very large test count"""
        view = ComparatorStatusView()
        qtbot.addWidget(view)
        
        view.on_tests_started(10000)
        
        assert view.total_tests == 10000
        assert view.completed_tests == 0
        
        # Complete a few tests
        for i in range(1, 6):
            view.on_test_completed(i, True, f"in{i}", f"out{i}", f"out{i}", 0.1, 10.0)
        
        assert view.completed_tests == 5
        assert view.passed_tests == 5
    
    def test_empty_strings(self, qtbot):
        """Test handling of empty string inputs"""
        view = ComparatorStatusView()
        qtbot.addWidget(view)
        
        view.on_tests_started(1)
        view.on_test_completed(1, False, "", "", "", 0.0, 0.0)
        
        assert view.completed_tests == 1
        assert view.failed_tests == 1
        assert 1 in view.test_data
    
    def test_very_long_strings(self, qtbot):
        """Test handling of very long string inputs"""
        view = ComparatorStatusView()
        qtbot.addWidget(view)
        
        long_string = "x" * 100000  # 100KB string
        
        view.on_tests_started(1)
        view.on_test_completed(1, False, long_string, long_string, "different", 0.1, 10.0)
        
        assert view.completed_tests == 1
        assert 1 in view.test_data
        assert view.test_data[1]['input_text'] == long_string


class TestSignalHandling:
    """Test signal handling edge cases"""
    
    def test_stop_when_not_running(self, qtbot):
        """Test stop signal when tests aren't running"""
        view = ComparatorStatusView()
        qtbot.addWidget(view)
        
        signal_received = []
        view.stopRequested.connect(lambda: signal_received.append(True))
        
        # Emit stop without starting tests (tests_running is False)
        view._handle_stop()
        
        # Should NOT emit signal when not running (intentional design)
        assert len(signal_received) == 0
        
        # Now start tests and try again
        view.on_tests_started(5)
        view._handle_stop()
        
        # Should emit signal when running
        assert len(signal_received) == 1
    
    def test_back_during_running_tests(self, qtbot):
        """Test back signal during running tests"""
        view = ComparatorStatusView()
        qtbot.addWidget(view)
        
        view.on_tests_started(10)
        view.is_running = True
        
        stop_received = []
        back_received = []
        view.stopRequested.connect(lambda: stop_received.append(True))
        view.backRequested.connect(lambda: back_received.append(True))
        
        # Try to go back while running - should show confirmation
        # (In actual UI this would show QMessageBox, but in test we just verify handler exists)
        assert hasattr(view, '_handle_back')
    
    def test_multiple_stop_signals(self, qtbot):
        """Test multiple rapid stop signals"""
        view = ComparatorStatusView()
        qtbot.addWidget(view)
        
        view.on_tests_started(10)
        
        signal_count = []
        view.stopRequested.connect(lambda: signal_count.append(True))
        
        # Emit stop multiple times rapidly
        view._handle_stop()
        
        # After first stop, tests_running is False, so subsequent stops won't emit
        view._handle_stop()
        view._handle_stop()
        
        # Should receive only one signal (intentional design to prevent duplicate stops)
        assert len(signal_count) == 1
    
    def test_disconnect_during_tests(self, qtbot):
        """Test signal disconnection doesn't crash"""
        view = ComparatorStatusView()
        qtbot.addWidget(view)
        
        callback = Mock()
        view.stopRequested.connect(callback)
        
        view.on_tests_started(5)
        
        # Disconnect signal
        view.stopRequested.disconnect(callback)
        
        # Should not crash
        view._handle_stop()
        
        # Callback should not have been called
        callback.assert_not_called()


class TestProgressTracking:
    """Test progress tracking edge cases"""
    
    def test_out_of_order_completion(self, qtbot):
        """Test tests completing out of order"""
        view = ComparatorStatusView()
        qtbot.addWidget(view)
        
        view.on_tests_started(5)
        
        # Complete tests out of order
        view.on_test_completed(3, True, "3", "3", "3", 0.1, 10.0)
        view.on_test_completed(1, True, "1", "1", "1", 0.1, 10.0)
        view.on_test_completed(5, False, "5", "5", "6", 0.1, 10.0)
        view.on_test_completed(2, True, "2", "2", "2", 0.1, 10.0)
        view.on_test_completed(4, True, "4", "4", "4", 0.1, 10.0)
        
        # All should be tracked
        assert view.completed_tests == 5
        assert view.passed_tests == 4
        assert view.failed_tests == 1
        
        # All test numbers should be in test_data
        for i in range(1, 6):
            assert i in view.test_data
    
    def test_duplicate_test_completion(self, qtbot):
        """Test same test completing multiple times (overwrite behavior)"""
        view = ComparatorStatusView()
        qtbot.addWidget(view)
        
        view.on_tests_started(3)
        
        # Complete test 1 twice
        view.on_test_completed(1, True, "1", "1", "1", 0.1, 10.0)
        view.on_test_completed(1, False, "1", "1", "2", 0.1, 10.0)  # Same test again
        
        # Should overwrite and count both times
        assert view.completed_tests == 2  # Both counted as completions
        assert 1 in view.test_data
    
    def test_test_number_exceeds_total(self, qtbot):
        """Test completing test with number > total"""
        view = ComparatorStatusView()
        qtbot.addWidget(view)
        
        view.on_tests_started(3)
        
        # Complete test 10 (exceeds total of 3)
        view.on_test_completed(10, True, "10", "10", "10", 0.1, 10.0)
        
        # Should still track it
        assert view.completed_tests == 1
        assert 10 in view.test_data


class TestExtremeMetrics:
    """Test extreme time and memory values"""
    
    def test_zero_time_and_memory(self, qtbot):
        """Test zero time and memory metrics"""
        view = ComparatorStatusView()
        qtbot.addWidget(view)
        
        view.on_tests_started(1)
        view.on_test_completed(1, True, "1", "1", "1", 0.0, 0.0)
        
        assert view.test_data[1]['time'] == 0.0
        assert view.test_data[1]['memory'] == 0.0
    
    def test_negative_metrics(self, qtbot):
        """Test negative time/memory values (should be handled gracefully)"""
        view = ComparatorStatusView()
        qtbot.addWidget(view)
        
        view.on_tests_started(1)
        # Pass negative values (shouldn't happen in real usage)
        view.on_test_completed(1, True, "1", "1", "1", -0.5, -10.0)
        
        # Should store them (validation is worker's job)
        assert 1 in view.test_data
    
    def test_very_large_time(self, qtbot):
        """Test very large execution time"""
        view = ComparatorStatusView()
        qtbot.addWidget(view)
        
        view.on_tests_started(1)
        view.on_test_completed(1, False, "1", "1", "1", 3600.0, 1000.0)  # 1 hour
        
        assert view.test_data[1]['time'] == 3600.0
        assert view.test_data[1]['memory'] == 1000.0
    
    def test_very_large_memory(self, qtbot):
        """Test very large memory usage"""
        view = ComparatorStatusView()
        qtbot.addWidget(view)
        
        view.on_tests_started(1)
        view.on_test_completed(1, False, "1", "1", "1", 0.1, 16384.0)  # 16GB
        
        assert view.test_data[1]['memory'] == 16384.0


class TestValidatorEdgeCases:
    """Validator-specific edge cases"""
    
    def test_all_validator_exit_codes(self, qtbot):
        """Test all possible validator exit codes"""
        view = ValidatorStatusView()
        qtbot.addWidget(view)
        
        view.on_tests_started(4)
        
        # Exit code 0 - Correct
        view.on_test_completed(1, True, "in", "out", "Correct", "", 0, 0.1, 10.0)
        
        # Exit code 1 - Wrong Answer
        view.on_test_completed(2, False, "in", "out", "Wrong", "", 1, 0.1, 10.0)
        
        # Exit code 2 - Presentation Error
        view.on_test_completed(3, False, "in", "out", "PE", "", 2, 0.1, 10.0)
        
        # Exit code -1 - Error
        view.on_test_completed(4, False, "in", "out", "Error", "crash", -1, 0.1, 10.0)
        
        # All should be tracked
        assert view.completed_tests == 4
        assert view.passed_tests == 1
        assert view.failed_tests == 3


class TestBenchmarkerEdgeCases:
    """Benchmarker-specific edge cases"""
    
    def test_time_limit_boundary(self, qtbot):
        """Test execution time exactly at limit"""
        view = BenchmarkerStatusView(time_limit_ms=1000, memory_limit_mb=256)
        qtbot.addWidget(view)
        
        view.on_tests_started(3)
        
        # Exactly at limit (1.0 seconds = 1000ms)
        view.on_test_completed("Test 1", 1, True, 1.0, 100.0, True)
        
        # Just under limit
        view.on_test_completed("Test 2", 2, True, 0.999, 100.0, True)
        
        # Over limit
        view.on_test_completed("Test 3", 3, False, 1.001, 100.0, True)
        
        assert view.completed_tests == 3
        assert view.passed_tests == 2
        assert view.failed_tests == 1
    
    def test_memory_limit_boundary(self, qtbot):
        """Test memory usage exactly at limit"""
        view = BenchmarkerStatusView(time_limit_ms=1000, memory_limit_mb=256)
        qtbot.addWidget(view)
        
        view.on_tests_started(3)
        
        # Exactly at limit
        view.on_test_completed("Test 1", 1, True, 0.5, 256.0, True)
        
        # Under limit
        view.on_test_completed("Test 2", 2, True, 0.5, 255.9, True)
        
        # Over limit (memory_passed=False)
        view.on_test_completed("Test 3", 3, False, 0.5, 300.0, False)
        
        assert view.completed_tests == 3
        assert view.passed_tests == 2
        assert view.failed_tests == 1
    
    def test_zero_limits(self, qtbot):
        """Test with zero time/memory limits"""
        view = BenchmarkerStatusView(time_limit_ms=0, memory_limit_mb=0)
        qtbot.addWidget(view)
        
        view.on_tests_started(1)
        view.on_test_completed("Test 1", 1, False, 0.1, 10.0, False)
        
        # Should handle gracefully
        assert view.time_limit_ms == 0
        assert view.memory_limit_mb == 0
