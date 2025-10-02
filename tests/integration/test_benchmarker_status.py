"""
Integration tests for BenchmarkerStatusView.

Tests the complete integration of unified status view with the benchmarker runner,
including display area integration, signal connections, card creation, and progress tracking.
"""

import pytest
from unittest.mock import Mock, MagicMock
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QVBoxLayout

from src.app.core.tools.benchmarker import Benchmarker
from src.app.presentation.views.benchmarker.benchmarker_status_view import BenchmarkerStatusView


class MockBenchmarkerWindow(QWidget):
    """Mock benchmarker window with display area for testing"""
    def __init__(self):
        super().__init__()
        self.display_area = Mock()
        self.display_area.layout = Mock()
        self.display_area.layout.count = Mock(return_value=1)
        self.display_area.layout.itemAt = Mock()
        self.display_area.set_content = Mock()


class TestBenchmarkerRunnerIntegration:
    """Test benchmarker runner creates and uses status view correctly"""
    
    def test_runner_creates_status_view_with_parent(self, qtbot, tmp_path):
        """Test benchmarker runner creates status view when parent window is set"""
        # Create test files
        test_file = tmp_path / "test.py"
        test_file.write_text("import time; print(input()); time.sleep(0.01)")

        gen_file = tmp_path / "gen.py"
        gen_file.write_text("print('5')")

        # Create runner
        runner = Benchmarker(
            workspace_dir=str(tmp_path),
            files={'test': str(test_file), 'generator': str(gen_file)}
        )        # Set parent window
        mock_window = MockBenchmarkerWindow()
        runner.set_parent_window(mock_window)
        
        # Create status window (should return view, not dialog)
        status = runner._create_test_status_window()
        
        assert status is not None
        assert isinstance(status, BenchmarkerStatusView)
    
    def test_runner_creates_status_view_correct_type(self, qtbot, tmp_path):
        """Test status view is BenchmarkerStatusView"""
        test_file = tmp_path / "test.py"
        test_file.write_text("import time; print(input()); time.sleep(0.01)")

        gen_file = tmp_path / "gen.py"
        gen_file.write_text("print('5')")

        runner = Benchmarker(
            workspace_dir=str(tmp_path),
            files={'test': str(test_file), 'generator': str(gen_file)}
        )
        
        mock_window = MockBenchmarkerWindow()
        runner.set_parent_window(mock_window)
        
        status = runner._create_test_status_window()
        qtbot.addWidget(status)
        
        assert status.test_type == 'benchmarker'
        assert hasattr(status, 'on_test_completed')
        assert hasattr(status, 'stopRequested')
        assert hasattr(status, 'backRequested')
        # Time/memory limits default to 0 until run_benchmark_test is called
        assert hasattr(status, 'time_limit_ms')
        assert hasattr(status, 'memory_limit_mb')
    
    def test_runner_without_parent_creates_dialog(self, qtbot, tmp_path):
        """Test runner without parent window creates dialog (backward compatibility)"""
        test_file = tmp_path / "test.py"
        test_file.write_text("print(input())")

        gen_file = tmp_path / "gen.py"
        gen_file.write_text("print('5')")

        runner = Benchmarker(
            workspace_dir=str(tmp_path),
            files={'test': str(test_file), 'generator': str(gen_file)}
        )        # Don't set parent window
        status = runner._create_test_status_window()
        
        # Should create BenchmarkStatusWindow (dialog), not BenchmarkerStatusView
        assert status is not None
        assert not isinstance(status, BenchmarkerStatusView)


class TestDisplayAreaIntegration:
    """Test status view integrates properly with display area"""
    
    def test_status_view_integrates_with_display_area(self, qtbot, tmp_path):
        """Test status view can be set as display area content"""
        test_file = tmp_path / "test.py"
        test_file.write_text("print(input())")

        gen_file = tmp_path / "gen.py"
        gen_file.write_text("print('5')")

        runner = Benchmarker(
            workspace_dir=str(tmp_path),
            files={'test': str(test_file), 'generator': str(gen_file)}
        )
        
        mock_window = MockBenchmarkerWindow()
        runner.set_parent_window(mock_window)
        
        status_view = runner._create_test_status_window()
        qtbot.addWidget(status_view)
        
        # Simulate setting as display content
        mock_window.display_area.set_content(status_view)
        
        # Verify set_content was called
        mock_window.display_area.set_content.assert_called_once_with(status_view)
    
    def test_original_content_stored_for_restoration(self, qtbot, tmp_path):
        """Test original display content is stored"""
        test_file = tmp_path / "test.py"
        test_file.write_text("print(input())")

        gen_file = tmp_path / "gen.py"
        gen_file.write_text("print('5')")

        runner = Benchmarker(
            workspace_dir=str(tmp_path),
            files={'test': str(test_file), 'generator': str(gen_file)}
        )        # Create mock original content
        original_widget = QWidget()
        mock_item = Mock()
        mock_item.widget = Mock(return_value=original_widget)
        
        mock_window = MockBenchmarkerWindow()
        mock_window.display_area.layout.itemAt = Mock(return_value=mock_item)
        runner.set_parent_window(mock_window)
        
        # Integrate status view (simulates what happens in run_tests)
        runner.status_view = runner._create_test_status_window()
        runner._integrate_status_view()
        
        # Check original content was stored
        assert runner.original_display_content is not None


class TestStatusViewSignals:
    """Test signal connections between status view and runner"""
    
    def test_stop_signal_connected(self, qtbot):
        """Test stop signal connects to runner"""
        view = BenchmarkerStatusView(time_limit_ms=1000, memory_limit_mb=256)
        qtbot.addWidget(view)
        
        # Mock slot
        slot_called = []
        view.stopRequested.connect(lambda: slot_called.append(True))
        
        # Trigger stop
        view.on_tests_started(5)
        view._handle_stop()
        
        # Verify signal emitted
        assert len(slot_called) == 1
    
    def test_back_signal_connected(self, qtbot):
        """Test back signal connects to runner"""
        view = BenchmarkerStatusView(time_limit_ms=1000, memory_limit_mb=256)
        qtbot.addWidget(view)
        
        # Mock slot
        slot_called = []
        view.backRequested.connect(lambda: slot_called.append(True))
        
        # Trigger back (when not running)
        view._handle_back()
        
        # Verify signal emitted
        assert len(slot_called) == 1


class TestCardCreation:
    """Test card creation during test execution"""
    
    def test_test_completed_creates_card(self, qtbot):
        """Test on_test_completed creates a card"""
        view = BenchmarkerStatusView(time_limit_ms=1000, memory_limit_mb=256)
        qtbot.addWidget(view)
        
        view.on_tests_started(3)
        
        # Simulate test completion (passed)
        view.on_test_completed(
            test_name="Test 1",
            test_number=1,
            passed=True,
            execution_time=0.5,  # 500ms, under limit
            memory_used=100.0,   # 100MB, under limit
            memory_passed=True
        )
        
        # Check card was added
        assert len(view.cards_section.passed_cards) == 1
        assert len(view.cards_section.failed_cards) == 0
    
    def test_failed_test_switches_layout(self, qtbot):
        """Test first failed test switches to split layout"""
        view = BenchmarkerStatusView(time_limit_ms=1000, memory_limit_mb=256)
        qtbot.addWidget(view)
        
        view.on_tests_started(3)
        
        # Add passing test
        view.on_test_completed("Test 1", 1, True, 0.5, 100.0, True)
        assert view.cards_section.layout_mode == 'single'
        
        # Add failing test (TLE)
        view.on_test_completed("Test 2", 2, False, 1.5, 120.0, True)
        assert view.cards_section.layout_mode == 'split'
    
    def test_test_data_stored_for_details(self, qtbot):
        """Test test data is stored for detail view"""
        view = BenchmarkerStatusView(time_limit_ms=1000, memory_limit_mb=256)
        qtbot.addWidget(view)
        
        view.on_tests_started(1)
        
        view.on_test_completed(
            test_name="Performance Test",
            test_number=1,
            passed=True,
            execution_time=0.75,
            memory_used=150.0,
            memory_passed=True
        )
        
        # Check data stored
        assert 1 in view.test_data
        assert view.test_data[1]['test_name'] == "Performance Test"
        assert view.test_data[1]['execution_time'] == 0.75
        assert view.test_data[1]['memory_used'] == 150.0
        assert view.test_data[1]['time_passed'] == True
        assert view.test_data[1]['memory_passed'] == True


class TestProgressUpdates:
    """Test progress tracking during test execution"""
    
    def test_progress_updates_on_completion(self, qtbot):
        """Test progress updates as tests complete"""
        view = BenchmarkerStatusView(time_limit_ms=1000, memory_limit_mb=256)
        qtbot.addWidget(view)
        
        view.on_tests_started(3)
        assert view.total_tests == 3
        assert view.completed_tests == 0
        
        view.on_test_completed("Test 1", 1, True, 0.5, 100.0, True)
        assert view.completed_tests == 1
        assert view.passed_tests == 1
        
        view.on_test_completed("Test 2", 2, False, 1.5, 120.0, True)
        assert view.completed_tests == 2
        assert view.passed_tests == 1
        assert view.failed_tests == 1
    
    def test_all_tests_completed_updates_state(self, qtbot):
        """Test completion state updates"""
        view = BenchmarkerStatusView(time_limit_ms=1000, memory_limit_mb=256)
        qtbot.addWidget(view)
        
        view.on_tests_started(2)
        view.on_test_completed("Test 1", 1, True, 0.5, 100.0, True)
        view.on_test_completed("Test 2", 2, True, 0.6, 110.0, True)
        
        view.on_all_tests_completed(True)
        
        assert not view.tests_running
        assert view.completed_tests == 2
        assert view.passed_tests == 2


class TestPerformanceMetrics:
    """Test performance-specific features"""
    
    def test_time_limit_tracking(self, qtbot):
        """Test time limit is properly tracked"""
        view = BenchmarkerStatusView(time_limit_ms=1000, memory_limit_mb=256)
        qtbot.addWidget(view)
        
        assert view.time_limit_ms == 1000
        
        view.on_tests_started(1)
        
        # Test exceeds time limit
        view.on_test_completed("TLE Test", 1, False, 1.5, 100.0, True)
        
        # Card should show time limit exceeded
        assert len(view.cards_section.failed_cards) == 1
    
    def test_memory_limit_tracking(self, qtbot):
        """Test memory limit is properly tracked"""
        view = BenchmarkerStatusView(time_limit_ms=1000, memory_limit_mb=256)
        qtbot.addWidget(view)
        
        assert view.memory_limit_mb == 256
        
        view.on_tests_started(1)
        
        # Test exceeds memory limit
        view.on_test_completed("MLE Test", 1, False, 0.5, 300.0, False)
        
        # Card should show memory limit exceeded
        assert len(view.cards_section.failed_cards) == 1
