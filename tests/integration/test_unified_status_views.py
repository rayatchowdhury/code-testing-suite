"""
Cross-type integration tests for unified status views.

Tests consistent behavior across Comparator, Validator, and Benchmarker
status views, ensuring architectural uniformity.
"""

import pytest
from unittest.mock import Mock
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget

from src.app.core.tools.comparator import Comparator
from src.app.core.tools.validator import ValidatorRunner
from src.app.core.tools.benchmarker import Benchmarker
from src.app.presentation.views.comparator.comparator_status_view import ComparatorStatusView
from src.app.presentation.views.validator.validator_status_view import ValidatorStatusView
from src.app.presentation.views.benchmarker.benchmarker_status_view import BenchmarkerStatusView
from src.app.presentation.widgets.unified_status_view import BaseStatusView


class MockWindow(QWidget):
    """Generic mock window for testing all test types"""
    def __init__(self):
        super().__init__()
        self.display_area = Mock()
        self.display_area.layout = Mock()
        self.display_area.layout.count = Mock(return_value=1)
        self.display_area.layout.itemAt = Mock()
        self.display_area.set_content = Mock()


class TestUnifiedArchitecture:
    """Test that all status views follow the same architectural pattern"""
    
    def test_all_views_inherit_from_base(self, qtbot):
        """Test all status views inherit from BaseStatusView"""
        comparator_view = ComparatorStatusView()
        validator_view = ValidatorStatusView()
        benchmarker_view = BenchmarkerStatusView(time_limit_ms=1000, memory_limit_mb=256)
        
        qtbot.addWidget(comparator_view)
        qtbot.addWidget(validator_view)
        qtbot.addWidget(benchmarker_view)
        
        assert isinstance(comparator_view, BaseStatusView)
        assert isinstance(validator_view, BaseStatusView)
        assert isinstance(benchmarker_view, BaseStatusView)
    
    def test_all_views_have_required_attributes(self, qtbot):
        """Test all status views have required attributes"""
        views = [
            ComparatorStatusView(),
            ValidatorStatusView(),
            BenchmarkerStatusView(time_limit_ms=1000, memory_limit_mb=256)
        ]
        
        for view in views:
            qtbot.addWidget(view)
            
            # Common attributes from BaseStatusView
            assert hasattr(view, 'test_type')
            assert hasattr(view, 'total_tests')
            assert hasattr(view, 'completed_tests')
            assert hasattr(view, 'passed_tests')
            assert hasattr(view, 'failed_tests')
            assert hasattr(view, 'test_data')
            
            # Signal attributes
            assert hasattr(view, 'stopRequested')
            assert hasattr(view, 'backRequested')
            
            # Method attributes
            assert hasattr(view, 'on_tests_started')
            assert hasattr(view, 'on_test_completed')
            # Note: on_tests_finished is not a required method
    
    def test_all_views_have_stop_back_buttons(self, qtbot):
        """Test all status views have stop and back button support"""
        views = [
            ComparatorStatusView(),
            ValidatorStatusView(),
            BenchmarkerStatusView(time_limit_ms=1000, memory_limit_mb=256)
        ]
        
        for view in views:
            qtbot.addWidget(view)
            
            # Check for controls panel with stop button support
            assert hasattr(view, 'controls_panel')
            assert hasattr(view.controls_panel, 'stopClicked')
            
            # Check for back button handler
            assert hasattr(view, '_handle_back')
            assert hasattr(view, '_handle_stop')
    
    def test_all_views_emit_stop_signal(self, qtbot):
        """Test all status views can emit stop signal"""
        views = [
            ComparatorStatusView(),
            ValidatorStatusView(),
            BenchmarkerStatusView(time_limit_ms=1000, memory_limit_mb=256)
        ]
        
        for view in views:
            qtbot.addWidget(view)
            
            # Connect signal and verify it can be emitted
            signal_received = []
            view.stopRequested.connect(lambda: signal_received.append(True))
            
            # Simulate stop via _handle_stop method (stop button now in sidebar)
            view.on_tests_started(5)  # Start tests first
            with qtbot.waitSignal(view.stopRequested, timeout=1000):
                view._handle_stop()  # Call method directly
            
            assert len(signal_received) == 1
    
    def test_all_views_emit_back_signal(self, qtbot):
        """Test all status views can emit back signal"""
        views = [
            ComparatorStatusView(),
            ValidatorStatusView(),
            BenchmarkerStatusView(time_limit_ms=1000, memory_limit_mb=256)
        ]
        
        for view in views:
            qtbot.addWidget(view)
            
            # Connect signal and verify it can be emitted
            signal_received = []
            view.backRequested.connect(lambda: signal_received.append(True))
            
            # Directly call the back handler (simulating button click)
            view._handle_back()
            
            assert len(signal_received) == 1


class TestConsistentBehavior:
    """Test consistent behavior across all status views"""
    
    def test_test_started_initializes_counters(self, qtbot):
        """Test on_tests_started initializes counters consistently"""
        views = [
            ComparatorStatusView(),
            ValidatorStatusView(),
            BenchmarkerStatusView(time_limit_ms=1000, memory_limit_mb=256)
        ]
        
        for view in views:
            qtbot.addWidget(view)
            
            view.on_tests_started(10)
            
            assert view.total_tests == 10
            assert view.completed_tests == 0
            assert view.passed_tests == 0
            assert view.failed_tests == 0
    
    def test_progress_tracking_consistent(self, qtbot):
        """Test progress tracking works consistently"""
        comparator_view = ComparatorStatusView()
        validator_view = ValidatorStatusView()
        benchmarker_view = BenchmarkerStatusView(time_limit_ms=1000, memory_limit_mb=256)
        
        qtbot.addWidget(comparator_view)
        qtbot.addWidget(validator_view)
        qtbot.addWidget(benchmarker_view)
        
        # Start tests
        comparator_view.on_tests_started(3)
        validator_view.on_tests_started(3)
        benchmarker_view.on_tests_started(3)
        
        # Complete one passing test
        comparator_view.on_test_completed(1, True, "1", "1", "1", 0.1, 10.0)
        validator_view.on_test_completed(1, True, "input", "output", "Correct", "", 0, 0.1, 10.0)
        benchmarker_view.on_test_completed("Test 1", 1, True, 0.5, 100.0, True)
        
        # Verify consistent state
        for view in [comparator_view, validator_view, benchmarker_view]:
            assert view.completed_tests == 1
            assert view.passed_tests == 1
            assert view.failed_tests == 0
        
        # Complete one failing test
        comparator_view.on_test_completed(2, False, "2", "2", "3", 0.1, 10.0)
        validator_view.on_test_completed(2, False, "input", "output", "Wrong", "error", 1, 0.1, 10.0)
        benchmarker_view.on_test_completed("Test 2", 2, False, 1.5, 100.0, True)
        
        # Verify consistent state
        for view in [comparator_view, validator_view, benchmarker_view]:
            assert view.completed_tests == 2
            assert view.passed_tests == 1
            assert view.failed_tests == 1
    
    def test_completion_state_consistent(self, qtbot):
        """Test completion state is consistent"""
        views = [
            ComparatorStatusView(),
            ValidatorStatusView(),
            BenchmarkerStatusView(time_limit_ms=1000, memory_limit_mb=256)
        ]
        
        for view in views:
            qtbot.addWidget(view)
            
            view.on_tests_started(2)
            
            # Complete both tests
            if isinstance(view, ComparatorStatusView):
                view.on_test_completed(1, True, "1", "1", "1", 0.1, 10.0)
                view.on_test_completed(2, True, "2", "2", "2", 0.1, 10.0)
            elif isinstance(view, ValidatorStatusView):
                view.on_test_completed(1, True, "in", "out", "OK", "", 0, 0.1, 10.0)
                view.on_test_completed(2, True, "in", "out", "OK", "", 0, 0.1, 10.0)
            else:  # BenchmarkerStatusView
                view.on_test_completed("Test 1", 1, True, 0.5, 100.0, True)
                view.on_test_completed("Test 2", 2, True, 0.5, 100.0, True)
            
            # All should be complete
            assert view.completed_tests == 2
            assert view.total_tests == 2
            assert view.passed_tests == 2


class TestRunnerIntegration:
    """Test runner integration is consistent across all types"""
    
    def test_all_runners_create_views_with_parent(self, qtbot, tmp_path):
        """Test all runners create status views when parent is set"""
        # Create test files
        test_file = tmp_path / "test.py"
        test_file.write_text("print(input())")
        
        gen_file = tmp_path / "gen.py"
        gen_file.write_text("print('5')")
        
        correct_file = tmp_path / "correct.py"
        correct_file.write_text("print(input())")
        
        validator_file = tmp_path / "validator.py"
        validator_file.write_text("import sys; sys.exit(0)")
        
        # Create runners
        comparator = Comparator(
            workspace_dir=str(tmp_path),
            files={
                'test': str(test_file),
                'generator': str(gen_file),
                'correct': str(correct_file)
            }
        )
        
        validator = ValidatorRunner(
            workspace_dir=str(tmp_path),
            files={
                'test': str(test_file),
                'generator': str(gen_file),
                'validator': str(validator_file)
            }
        )
        
        benchmarker = Benchmarker(
            workspace_dir=str(tmp_path),
            files={
                'test': str(test_file),
                'generator': str(gen_file)
            }
        )
        
        # Set parent windows
        mock_window = MockWindow()
        comparator.set_parent_window(mock_window)
        validator.set_parent_window(mock_window)
        benchmarker.set_parent_window(mock_window)
        
        # All should have parent_window attribute
        assert hasattr(comparator, 'parent_window')
        assert hasattr(validator, 'parent_window')
        assert hasattr(benchmarker, 'parent_window')
        
        assert comparator.parent_window == mock_window
        assert validator.parent_window == mock_window
        assert benchmarker.parent_window == mock_window
    
    def test_all_runners_create_correct_view_type(self, qtbot, tmp_path):
        """Test all runners create the correct status view type"""
        # Create test files
        test_file = tmp_path / "test.py"
        test_file.write_text("print(input())")
        
        gen_file = tmp_path / "gen.py"
        gen_file.write_text("print('5')")
        
        correct_file = tmp_path / "correct.py"
        correct_file.write_text("print(input())")
        
        validator_file = tmp_path / "validator.py"
        validator_file.write_text("import sys; sys.exit(0)")
        
        # Create runners with parent
        mock_window = MockWindow()
        
        comparator = Comparator(
            workspace_dir=str(tmp_path),
            files={
                'test': str(test_file),
                'generator': str(gen_file),
                'correct': str(correct_file)
            }
        )
        comparator.set_parent_window(mock_window)
        
        validator = ValidatorRunner(
            workspace_dir=str(tmp_path),
            files={
                'test': str(test_file),
                'generator': str(gen_file),
                'validator': str(validator_file)
            }
        )
        validator.set_parent_window(mock_window)
        
        benchmarker = Benchmarker(
            workspace_dir=str(tmp_path),
            files={
                'test': str(test_file),
                'generator': str(gen_file)
            }
        )
        benchmarker.set_parent_window(mock_window)
        
        # Create status views
        comp_view = comparator._create_test_status_window()
        val_view = validator._create_test_status_window()
        bench_view = benchmarker._create_test_status_window()
        
        qtbot.addWidget(comp_view)
        qtbot.addWidget(val_view)
        qtbot.addWidget(bench_view)
        
        # Verify types
        assert isinstance(comp_view, ComparatorStatusView)
        assert isinstance(val_view, ValidatorStatusView)
        assert isinstance(bench_view, BenchmarkerStatusView)
        
        # All should inherit from BaseStatusView
        assert isinstance(comp_view, BaseStatusView)
        assert isinstance(val_view, BaseStatusView)
        assert isinstance(bench_view, BaseStatusView)
    
    def test_all_runners_fallback_to_dialog(self, qtbot, tmp_path):
        """Test all runners create dialog when no parent is set"""
        # Create test files
        test_file = tmp_path / "test.py"
        test_file.write_text("print(input())")
        
        gen_file = tmp_path / "gen.py"
        gen_file.write_text("print('5')")
        
        correct_file = tmp_path / "correct.py"
        correct_file.write_text("print(input())")
        
        validator_file = tmp_path / "validator.py"
        validator_file.write_text("import sys; sys.exit(0)")
        
        # Create runners WITHOUT parent
        comparator = Comparator(
            workspace_dir=str(tmp_path),
            files={
                'test': str(test_file),
                'generator': str(gen_file),
                'correct': str(correct_file)
            }
        )
        
        validator = ValidatorRunner(
            workspace_dir=str(tmp_path),
            files={
                'test': str(test_file),
                'generator': str(gen_file),
                'validator': str(validator_file)
            }
        )
        
        benchmarker = Benchmarker(
            workspace_dir=str(tmp_path),
            files={
                'test': str(test_file),
                'generator': str(gen_file)
            }
        )
        
        # Create status windows (should be dialogs, not views)
        comp_window = comparator._create_test_status_window()
        val_window = validator._create_test_status_window()
        bench_window = benchmarker._create_test_status_window()
        
        # These should NOT be BaseStatusView instances (they're dialogs)
        assert not isinstance(comp_window, BaseStatusView)
        assert not isinstance(val_window, BaseStatusView)
        assert not isinstance(bench_window, BaseStatusView)
