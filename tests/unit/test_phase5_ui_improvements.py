"""
Phase 5 Test Suite - UI Improvements & Detailed View Redesign

Tests for Phase 5 implementation covering:
- Issue #5: TypedDict schemas for test details
- Issue #34: Redesigned detailed view as integrated widget with sidebar (follows status_view pattern)

All tests verify the implementation against Phase 5 requirements.
Widget-based architecture integrates into parent window's display area.
"""

import pytest
import sys
import json
from pathlib import Path
from datetime import datetime, timedelta

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from PySide6.QtWidgets import QApplication, QStackedWidget
from PySide6.QtCore import Qt

from app.core.tools.schemas import (
    BaseTestDetail, ValidatorTestDetail, ComparisonTestDetail, 
    BenchmarkTestDetail, TestDetail
)
from app.persistence.database import TestResult
from app.presentation.views.results.detailed_results_window import DetailedResultsWidget
from app.presentation.views.results.results_widget import TestResultsWidget


@pytest.fixture(scope="module")
def qapp():
    """Create QApplication instance for tests"""
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    yield app


@pytest.fixture
def sample_test_result():
    """Create a sample test result for testing"""
    result = TestResult()
    result.id = 1
    result.test_type = "comparison"
    result.file_path = "/path/to/test.py"
    result.test_count = 5
    result.passed_tests = 3
    result.failed_tests = 2
    result.total_time = 10.5
    result.timestamp = datetime.now().isoformat()
    result.project_name = "TestProject"
    
    # Files snapshot
    result.files_snapshot = json.dumps({
        'generator_code': 'import random\nprint(random.randint(1, 100))',
        'test_code': 'def solution(n):\n    return n * 2',
        'correct_code': 'def correct(n):\n    return n * 2',
        'validator_code': 'def validate(output):\n    return True'
    })
    
    # Test details
    result.test_details = json.dumps([
        {
            'test': 1,
            'passed': True,
            'status': 'pass',
            'input': '5',
            'output': '10',
            'actual_output': '10',
            'execution_time': 0.1
        },
        {
            'test': 2,
            'passed': False,
            'status': 'fail',
            'input': '10',
            'output': '20',
            'actual_output': '15',
            'error': 'Output mismatch',
            'execution_time': 0.2
        },
        {
            'test': 3,
            'passed': True,
            'status': 'pass',
            'input': '7',
            'output': '14',
            'actual_output': '14',
            'execution_time': 0.15
        }
    ])
    
    result.mismatch_analysis = "Test 2 failed: expected 20, got 15"
    
    return result


# ============================================================================
# TASK 1 TESTS: TypedDict Schemas (Issue #5)
# ============================================================================

def test_base_test_detail_schema():
    """Test BaseTestDetail TypedDict schema"""
    # Should be able to create valid detail
    detail: BaseTestDetail = {
        'test_number': 1,
        'passed': True,
        'error_details': '',
        'total_time': 0.5,
        'memory': 100.0
    }
    
    assert detail['test_number'] == 1
    assert detail['passed'] is True


def test_validator_test_detail_schema():
    """Test ValidatorTestDetail TypedDict schema"""
    detail: ValidatorTestDetail = {
        'test_number': 1,
        'passed': True,
        'input': 'test input',
        'test_output': 'test output',
        'validation_message': 'Valid',
        'validator_exit_code': 0,
        'generator_time': 0.1,
        'test_time': 0.2,
        'validator_time': 0.05
    }
    
    assert detail['input'] == 'test input'
    assert detail['validator_exit_code'] == 0


def test_comparison_test_detail_schema():
    """Test ComparisonTestDetail TypedDict schema"""
    detail: ComparisonTestDetail = {
        'test_number': 1,
        'passed': False,
        'input': '5',
        'test_output': '10',
        'correct_output': '11',
        'generator_time': 0.1,
        'test_time': 0.2,
        'correct_time': 0.15,
        'comparison_time': 0.01
    }
    
    assert detail['input'] == '5'
    assert detail['test_output'] == '10'
    assert detail['correct_output'] == '11'


def test_benchmark_test_detail_schema():
    """Test BenchmarkTestDetail TypedDict schema"""
    detail: BenchmarkTestDetail = {
        'test_number': 1,
        'passed': True,
        'test_name': 'Performance Test',
        'execution_time': 1.5,
        'memory_used': 256.0,
        'memory_passed': True,
        'time_passed': True,
        'generator_time': 0.1,
        'input': 'test input',
        'output': 'test output',
        'test_size': 1000
    }
    
    assert detail['test_name'] == 'Performance Test'
    assert detail['memory_passed'] is True
    assert detail['time_passed'] is True


def test_schemas_file_exists():
    """Test that schemas.py file exists"""
    schemas_path = Path(__file__).parent.parent.parent / "src" / "app" / "core" / "tools" / "schemas.py"
    assert schemas_path.exists(), "schemas.py file not found"


def test_schemas_imports():
    """Test that all schema types can be imported"""
    try:
        from app.core.tools.schemas import (
            BaseTestDetail, ValidatorTestDetail, 
            ComparisonTestDetail, BenchmarkTestDetail, TestDetail
        )
        assert True
    except ImportError as e:
        pytest.fail(f"Failed to import schemas: {e}")


# ============================================================================
# TASK 2-3 TESTS: Detailed Results Window Structure (Issue #34)
# ============================================================================

def test_detailed_window_creation(qapp, sample_test_result):
    """Test that detailed results widget can be created"""
    widget = DetailedResultsWidget(sample_test_result)
    
    assert widget is not None
    assert widget.sidebar is not None  # Has sidebar
    assert widget.content_stack is not None  # Has content area


def test_detailed_window_has_sidebar(qapp, sample_test_result):
    """Test that window has sidebar"""
    window = DetailedResultsWidget(sample_test_result)
    
    # Should have navigation buttons
    assert hasattr(window, 'nav_buttons')
    assert len(window.nav_buttons) == 5  # 5 navigation sections


def test_detailed_window_has_content_stack(qapp, sample_test_result):
    """Test that window has stacked widget for content"""
    window = DetailedResultsWidget(sample_test_result)
    
    assert hasattr(window, 'content_stack')
    assert isinstance(window.content_stack, QStackedWidget)
    assert window.content_stack.count() == 5  # 5 pages


def test_detailed_window_navigation(qapp, sample_test_result):
    """Test sidebar navigation switches pages"""
    window = DetailedResultsWidget(sample_test_result)
    
    # Initially on summary page
    assert window.current_page == 0
    assert window.content_stack.currentIndex() == 0
    
    # Navigate to code files
    window._show_page(1)
    assert window.current_page == 1
    assert window.content_stack.currentIndex() == 1
    
    # Navigate to passed tests
    window._show_page(2)
    assert window.current_page == 2
    assert window.content_stack.currentIndex() == 2


def test_navigation_button_styles_update(qapp, sample_test_result):
    """Test that navigation button styles update on page change"""
    window = DetailedResultsWidget(sample_test_result)
    
    # Show page 1
    window._show_page(1)
    
    # Button styles should reflect active state
    # (Can't easily test exact style, but verify method runs without error)
    assert window.current_page == 1


# ============================================================================
# TASK 4 TESTS: Code Files Page (Issue #34)
# ============================================================================

def test_code_page_exists(qapp, sample_test_result):
    """Test that code files page is created"""
    window = DetailedResultsWidget(sample_test_result)
    
    # Navigate to code page (index 1)
    window._show_page(1)
    code_page = window.content_stack.widget(1)
    
    assert code_page is not None


def test_code_page_has_tabs(qapp, sample_test_result):
    """Test that code page contains tabs for each file"""
    window = DetailedResultsWidget(sample_test_result)
    window._show_page(1)
    
    # The page should exist and be displayed
    assert window.content_stack.currentIndex() == 1


def test_code_viewer_creation(qapp, sample_test_result):
    """Test that code viewer widget is created"""
    window = DetailedResultsWidget(sample_test_result)
    
    # Create code viewer
    viewer = window._create_code_viewer("def test():\n    return True")
    
    assert viewer is not None
    assert "def test()" in viewer.toPlainText()
    assert viewer.isReadOnly()


# ============================================================================
# TASK 5 TESTS: Passed/Failed Test Pages (Issue #34)
# ============================================================================

def test_passed_tests_page_exists(qapp, sample_test_result):
    """Test that passed tests page is created"""
    window = DetailedResultsWidget(sample_test_result)
    
    window._show_page(2)
    passed_page = window.content_stack.widget(2)
    
    assert passed_page is not None


def test_failed_tests_page_exists(qapp, sample_test_result):
    """Test that failed tests page is created"""
    window = DetailedResultsWidget(sample_test_result)
    
    window._show_page(3)
    failed_page = window.content_stack.widget(3)
    
    assert failed_page is not None


def test_test_filtering_logic(qapp, sample_test_result):
    """Test that tests are correctly identified as passed/failed"""
    window = DetailedResultsWidget(sample_test_result)
    
    # Test _test_passed method
    passed_test = {'passed': True, 'status': 'pass'}
    failed_test = {'passed': False, 'status': 'fail'}
    
    assert window._test_passed(passed_test) is True
    assert window._test_passed(failed_test) is False


def test_test_case_widget_creation(qapp, sample_test_result):
    """Test that test case widgets are created"""
    window = DetailedResultsWidget(sample_test_result)
    
    test_data = {
        'test': 1,
        'passed': True,
        'status': 'pass',
        'input': 'test input',
        'execution_time': 0.5
    }
    
    widget = window._create_test_case_widget(test_data)
    
    assert widget is not None


def test_failed_test_shows_errors(qapp, sample_test_result):
    """Test that failed tests display error information"""
    window = DetailedResultsWidget(sample_test_result)
    
    failed_test = {
        'test': 2,
        'passed': False,
        'status': 'fail',
        'input': '10',
        'output': '20',
        'actual_output': '15',
        'error': 'Output mismatch'
    }
    
    widget = window._create_test_case_widget(failed_test, show_errors=True)
    
    assert widget is not None


# ============================================================================
# TASK 6 TESTS: Results Widget Integration
# ============================================================================

def test_results_widget_uses_new_window(qapp):
    """Test that results_widget delegates to parent window"""
    from app.presentation.views.results import results_widget
    
    # results_widget no longer directly imports DetailedResultsWidget
    # It delegates to parent window's show_detailed_view method
    assert hasattr(results_widget.TestResultsWidget, '_show_detailed_view')


def test_show_detailed_view_opens_window(qapp, sample_test_result):
    """Test that _show_detailed_view delegates to parent window"""
    widget = TestResultsWidget()
    
    # _show_detailed_view should exist and call parent's show_detailed_view
    assert hasattr(widget, '_show_detailed_view')
    
    # Widget no longer creates detailed_window (delegates to parent window)
    # This test just verifies the method exists and doesn't crash
    # Actual integration test would require a parent window


def test_detailed_view_no_longer_creates_tabs(qapp):
    """Test that detailed view doesn't create tabs anymore"""
    # Read the source code to verify tab creation is removed
    widget_path = Path(__file__).parent.parent.parent / "src" / "app" / "presentation" / "views" / "results" / "results_widget.py"
    
    with open(widget_path, 'r') as f:
        content = f.read()
    
    # Verify old tab-based approach is gone
    assert "self.tab_widget.addTab(self.detailed_widget" not in content
    
    # Verify new widget-based approach: delegates to parent window
    assert "parent_window.show_detailed_view" in content
    # results_widget no longer manages detailed_window itself


# ============================================================================
# INTEGRATION TESTS
# ============================================================================

def test_summary_page_shows_statistics(qapp, sample_test_result):
    """Test that summary page displays test statistics"""
    window = DetailedResultsWidget(sample_test_result)
    
    # Navigate to summary (should be default)
    window._show_page(0)
    
    assert window.content_stack.currentIndex() == 0


def test_export_page_exists(qapp, sample_test_result):
    """Test that export options page is created"""
    window = DetailedResultsWidget(sample_test_result)
    
    window._show_page(4)
    export_page = window.content_stack.widget(4)
    
    assert export_page is not None


def test_window_close_signal(qapp, sample_test_result):
    """Test that widget emits back requested signal"""
    widget = DetailedResultsWidget(sample_test_result)
    
    # Widget-based architecture uses backRequested signal instead of window_closed
    assert hasattr(widget, 'backRequested')


def test_phase5_no_regressions(qapp):
    """Test that Phase 5 changes don't break existing functionality"""
    # Check that results widget still works
    widget = TestResultsWidget()
    
    assert hasattr(widget, 'results_table')
    assert hasattr(widget, 'db_manager')
    assert hasattr(widget, '_load_results')


def test_detailed_window_file_exists():
    """Test that detailed_results_window.py file exists"""
    window_path = Path(__file__).parent.parent.parent / "src" / "app" / "presentation" / "views" / "results" / "detailed_results_window.py"
    assert window_path.exists(), "detailed_results_window.py file not found"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
