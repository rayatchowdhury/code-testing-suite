"""
Integration tests for unified StatusView.

Phase 3: Status View Unification
Tests the preset-based StatusView that replaces per-tool status views.
"""

import pytest
from PySide6.QtCore import Qt
from src.app.presentation.widgets.status_view import (
    StatusView,
    StatusViewPreset,
    BENCHMARKER_PRESET,
    COMPARATOR_PRESET,
    VALIDATOR_PRESET,
    TestResult
)


class TestStatusViewBenchmarkerPreset:
    """Test StatusView with benchmarker preset."""
    
    def test_benchmarker_preset_creates_all_widgets(self, qtbot):
        """Verify benchmarker preset creates all expected widgets."""
        view = StatusView(BENCHMARKER_PRESET)
        qtbot.addWidget(view)
        
        # Check that required widgets exist
        assert view.header is not None
        assert view.performance is not None
        assert view.progress_bar is not None
        assert view.cards_section is not None
        assert view.viewmodel is not None
    
    def test_benchmarker_preset_shows_performance_panel(self, qtbot):
        """Verify benchmarker shows performance panel (preset.show_performance_panel=True)."""
        view = StatusView(BENCHMARKER_PRESET)
        qtbot.addWidget(view)
        
        # Performance panel should be created and have a parent (added to layout) for benchmarker
        assert view.performance is not None
        assert view.performance.parent() is not None
    
    def test_benchmarker_test_lifecycle(self, qtbot):
        """Test complete benchmarker test execution lifecycle."""
        view = StatusView(BENCHMARKER_PRESET)
        qtbot.addWidget(view)
        
        # Start tests
        view.on_tests_started(total=5)
        assert view.is_tests_running()  # Running after tests started
        
        # Complete a test
        view.on_benchmarker_test_completed(
            test_name="test_1",
            test_number=1,
            passed=True,
            execution_time=0.123,
            memory_used=12.5,
            memory_passed=True,
            input_data="input",
            output_data="output",
            test_size=100
        )
        
        # Verify result was stored
        assert 1 in view.test_results
        assert view.test_results[1].passed == True
        assert view.test_results[1].time == 0.123
        
        # Verify card was created
        assert view.cards_section.passed_count == 1
        assert view.cards_section.failed_count == 0
    
    def test_benchmarker_limits_can_be_set(self, qtbot):
        """Test that benchmarker-specific limits can be set."""
        view = StatusView(BENCHMARKER_PRESET)
        qtbot.addWidget(view)
        
        view.set_benchmarker_limits(time_limit_ms=1000.0, memory_limit_mb=256)
        
        assert view.time_limit_ms == 1000.0
        assert view.memory_limit_mb == 256


class TestStatusViewComparatorPreset:
    """Test StatusView with comparator preset."""
    
    def test_comparator_preset_creates_widgets(self, qtbot):
        """Verify comparator preset creates expected widgets."""
        view = StatusView(COMPARATOR_PRESET)
        qtbot.addWidget(view)
        
        assert view.header is not None
        assert view.progress_bar is not None
        assert view.cards_section is not None
    
    def test_comparator_preset_hides_performance_panel(self, qtbot):
        """Verify comparator hides performance panel (preset.show_performance_panel=False)."""
        view = StatusView(COMPARATOR_PRESET)
        qtbot.addWidget(view)
        
        # Performance panel should not be visible for comparator
        # (it's created but not added to layout based on preset)
        # Check parent to see if it's in layout
        assert view.performance.parent() is None
    
    def test_comparator_test_completion(self, qtbot):
        """Test comparator test completion."""
        view = StatusView(COMPARATOR_PRESET)
        qtbot.addWidget(view)
        
        view.on_tests_started(total=3)
        
        view.on_comparator_test_completed(
            test_number=1,
            passed=False,
            input_text="input",
            correct_output="expected",
            test_output="actual",
            time=0.05,
            memory=5.0
        )
        
        # Verify result stored
        assert 1 in view.test_results
        assert view.test_results[1].passed == False
        assert view.test_results[1].data['input_text'] == "input"
        assert view.test_results[1].data['correct_output'] == "expected"


class TestStatusViewValidatorPreset:
    """Test StatusView with validator preset."""
    
    def test_validator_preset_creates_widgets(self, qtbot):
        """Verify validator preset creates expected widgets."""
        view = StatusView(VALIDATOR_PRESET)
        qtbot.addWidget(view)
        
        assert view.header is not None
        assert view.progress_bar is not None
        assert view.cards_section is not None
    
    def test_validator_test_completion(self, qtbot):
        """Test validator test completion."""
        view = StatusView(VALIDATOR_PRESET)
        qtbot.addWidget(view)
        
        view.on_tests_started(total=2)
        
        view.on_validator_test_completed(
            test_number=1,
            passed=True,
            input_data="input",
            test_output="output",
            validation_message="Valid",
            error_details="",
            validator_exit_code=0,
            time=0.08,
            memory=8.0
        )
        
        # Verify result stored
        assert 1 in view.test_results
        assert view.test_results[1].passed == True
        assert view.test_results[1].data['validation_message'] == "Valid"


class TestStatusViewGenericCompletion:
    """Test generic on_test_completed dispatcher."""
    
    def test_benchmarker_dispatcher(self, qtbot):
        """Test that generic on_test_completed dispatches to benchmarker handler."""
        view = StatusView(BENCHMARKER_PRESET)
        qtbot.addWidget(view)
        
        view.on_tests_started(total=1)
        
        # Call generic method with benchmarker args
        view.on_test_completed(
            test_name="test_1",
            test_number=1,
            passed=True,
            execution_time=0.1,
            memory_used=10.0,
            memory_passed=True,
            input_data="in",
            output_data="out",
            test_size=50
        )
        
        # Verify it was handled
        assert 1 in view.test_results
    
    def test_comparator_dispatcher(self, qtbot):
        """Test that generic on_test_completed dispatches to comparator handler."""
        view = StatusView(COMPARATOR_PRESET)
        qtbot.addWidget(view)
        
        view.on_tests_started(total=1)
        
        # Call generic method with comparator args
        view.on_test_completed(
            test_number=1,
            passed=True,
            input_text="in",
            correct_output="expected",
            test_output="actual",
            time=0.05,
            memory=5.0
        )
        
        # Verify it was handled
        assert 1 in view.test_results
    
    def test_validator_dispatcher(self, qtbot):
        """Test that generic on_test_completed dispatches to validator handler."""
        view = StatusView(VALIDATOR_PRESET)
        qtbot.addWidget(view)
        
        view.on_tests_started(total=1)
        
        # Call generic method with validator args
        view.on_test_completed(
            test_number=1,
            passed=True,
            input_data="in",
            test_output="out",
            validation_message="OK",
            error_details="",
            validator_exit_code=0,
            time=0.06,
            memory=6.0
        )
        
        # Verify it was handled
        assert 1 in view.test_results


class TestStatusViewSignals:
    """Test StatusView signal emissions."""
    
    def test_signals_exist(self, qtbot):
        """Verify status view has required signals."""
        view = StatusView(BENCHMARKER_PRESET)
        qtbot.addWidget(view)
        
        assert hasattr(view, 'stopRequested')
        assert hasattr(view, 'backRequested')
        assert hasattr(view, 'runRequested')


class TestStatusViewPresetConfiguration:
    """Test preset configuration behavior."""
    
    def test_preset_determines_test_type(self, qtbot):
        """Verify preset correctly sets test type."""
        benchmarker_view = StatusView(BENCHMARKER_PRESET)
        comparator_view = StatusView(COMPARATOR_PRESET)
        validator_view = StatusView(VALIDATOR_PRESET)
        
        qtbot.addWidget(benchmarker_view)
        qtbot.addWidget(comparator_view)
        qtbot.addWidget(validator_view)
        
        assert benchmarker_view.test_type == "benchmarker"
        assert comparator_view.test_type == "comparator"
        assert validator_view.test_type == "validator"
    
    def test_preset_determines_runner_attribute(self, qtbot):
        """Verify preset correctly sets runner attribute name."""
        benchmarker_view = StatusView(BENCHMARKER_PRESET)
        comparator_view = StatusView(COMPARATOR_PRESET)
        validator_view = StatusView(VALIDATOR_PRESET)
        
        qtbot.addWidget(benchmarker_view)
        qtbot.addWidget(comparator_view)
        qtbot.addWidget(validator_view)
        
        assert benchmarker_view.preset.runner_attribute == "benchmarker"
        assert comparator_view.preset.runner_attribute == "comparator"
        assert validator_view.preset.runner_attribute == "validator_runner"


class TestStatusViewMultipleTests:
    """Test StatusView with multiple test completions."""
    
    def test_multiple_passed_tests(self, qtbot):
        """Test handling multiple passed tests."""
        view = StatusView(COMPARATOR_PRESET)
        qtbot.addWidget(view)
        
        view.on_tests_started(total=3)
        
        for i in range(1, 4):
            view.on_comparator_test_completed(
                test_number=i,
                passed=True,
                input_text=f"input_{i}",
                correct_output=f"output_{i}",
                test_output=f"output_{i}",
                time=0.05,
                memory=5.0
            )
        
        # Verify all results stored
        assert len(view.test_results) == 3
        assert view.cards_section.passed_count == 3
        assert view.cards_section.failed_count == 0
    
    def test_mixed_results(self, qtbot):
        """Test handling mixed passed/failed tests."""
        view = StatusView(BENCHMARKER_PRESET)
        qtbot.addWidget(view)
        
        view.on_tests_started(total=4)
        
        # 2 passed
        for i in [1, 2]:
            view.on_benchmarker_test_completed(
                test_name=f"test_{i}",
                test_number=i,
                passed=True,
                execution_time=0.1,
                memory_used=10.0,
                memory_passed=True,
                input_data="in",
                output_data="out",
                test_size=100
            )
        
        # 2 failed
        for i in [3, 4]:
            view.on_benchmarker_test_completed(
                test_name=f"test_{i}",
                test_number=i,
                passed=False,
                execution_time=0.1,
                memory_used=10.0,
                memory_passed=True,
                input_data="in",
                output_data="out",
                test_size=100
            )
        
        # Verify counts
        assert len(view.test_results) == 4
        assert view.cards_section.passed_count == 2
        assert view.cards_section.failed_count == 2
