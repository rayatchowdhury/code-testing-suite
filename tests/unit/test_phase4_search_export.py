"""
Phase 4 Test Suite - Search, Export & Enhanced Features

Tests for Phase 4 implementation covering:
- Issue #10: SQL-based date filtering optimization
- Issue #12: Comprehensive search UI
- Issue #11, #33: ZIP export functionality  
- Issue #14: Delete functionality

All tests verify the implementation against Phase 4 requirements.
"""

import pytest
import sys
import os
import json
import zipfile
import tempfile
from datetime import datetime, timedelta
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from PySide6.QtWidgets import QApplication, QMessageBox
from PySide6.QtCore import Qt

from app.persistence.database import DatabaseManager, TestResult
from app.presentation.views.results.results_widget import TestResultsWidget
from app.presentation.views.results.results_window import ResultsWindow


@pytest.fixture(scope="module")
def qapp():
    """Create QApplication instance for tests"""
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    yield app


@pytest.fixture
def temp_db():
    """Create a temporary database for testing"""
    with tempfile.NamedTemporaryFile(delete=False, suffix='.db') as f:
        db_path = f.name
    
    db = DatabaseManager(db_path)
    yield db
    
    # Cleanup
    try:
        os.unlink(db_path)
    except:
        pass


@pytest.fixture
def sample_results(temp_db):
    """Create sample test results for testing"""
    results = []
    
    # Create results from different time periods
    now = datetime.now()
    
    # Recent result (2 days ago)
    result1 = TestResult()
    result1.test_type = "comparison"
    result1.file_path = "/path/to/test1.py"
    result1.test_count = 10
    result1.passed_tests = 10
    result1.failed_tests = 0
    result1.total_time = 5.5
    result1.timestamp = (now - timedelta(days=2)).isoformat()
    result1.project_name = "ProjectA"
    result1.test_details = json.dumps([
        {"test": 1, "status": "pass", "input": "1 2", "output": "3", "execution_time": 0.1},
        {"test": 2, "status": "pass", "input": "5 5", "output": "10", "execution_time": 0.2}
    ])
    result1.files_snapshot = json.dumps({
        "test1.py": "def add(a, b):\n    return a + b",
        "test2.cpp": "#include <iostream>\nint main() { return 0; }"
    })
    result1.mismatch_analysis = ""
    result1_id = temp_db.save_test_result(result1)
    result1.id = result1_id
    results.append(result1)
    
    # Old result (10 days ago)
    result2 = TestResult()
    result2.test_type = "benchmark"
    result2.file_path = "/path/to/test2.cpp"
    result2.test_count = 5
    result2.passed_tests = 3
    result2.failed_tests = 2
    result2.total_time = 10.0
    result2.timestamp = (now - timedelta(days=10)).isoformat()
    result2.project_name = "ProjectB"
    result2.test_details = json.dumps([
        {"test": 1, "status": "pass", "input": "100", "output": "OK", "execution_time": 0.5},
        {"test": 2, "status": "fail", "input": "200", "expected": "OK", "actual_output": "TLE", "execution_time": 2.1}
    ])
    result2.files_snapshot = json.dumps({
        "test2.cpp": "#include <vector>\nint main() { return 0; }"
    })
    result2.mismatch_analysis = "Test 2 exceeded time limit"
    result2_id = temp_db.save_test_result(result2)
    result2.id = result2_id
    results.append(result2)
    
    # Recent validator result (5 days ago)
    result3 = TestResult()
    result3.test_type = "validator"
    result3.file_path = "/path/to/validator.java"
    result3.test_count = 8
    result3.passed_tests = 7
    result3.failed_tests = 1
    result3.total_time = 3.2
    result3.timestamp = (now - timedelta(days=5)).isoformat()
    result3.project_name = "ProjectA"
    result3.test_details = json.dumps([
        {"test": 1, "status": "pass", "input": "valid", "output": "OK"},
        {"test": 2, "status": "fail", "input": "invalid", "expected": "FAIL", "actual_output": "OK"}
    ])
    result3.files_snapshot = json.dumps({
        "validator.java": "public class Validator { }"
    })
    result3.mismatch_analysis = ""
    result3_id = temp_db.save_test_result(result3)
    result3.id = result3_id
    results.append(result3)
    
    return results


# ============================================================================
# TASK 1 TESTS: SQL-Based Date Filtering (Issue #10)
# ============================================================================

def test_sql_date_filtering_7_days(temp_db, sample_results):
    """Test SQL-based filtering for last 7 days"""
    results = temp_db.get_test_results(days=7, limit=100)
    
    # Should only return result1 (2 days ago) and result3 (5 days ago)
    assert len(results) == 2
    assert all(r.id in [sample_results[0].id, sample_results[2].id] for r in results)


def test_sql_date_filtering_30_days(temp_db, sample_results):
    """Test SQL-based filtering for last 30 days"""
    results = temp_db.get_test_results(days=30, limit=100)
    
    # Should return all three results (2, 10, 5 days ago)
    assert len(results) == 3


def test_sql_date_filtering_none(temp_db, sample_results):
    """Test that days=None returns all results"""
    results = temp_db.get_test_results(days=None, limit=100)
    
    # Should return all results regardless of date
    assert len(results) == 3


def test_sql_project_name_filtering(temp_db, sample_results):
    """Test SQL-based project name filtering with LIKE operator"""
    results = temp_db.get_test_results(project_name="ProjectA", limit=100)
    
    # Should return result1 and result3 (both ProjectA)
    assert len(results) == 2
    assert all(r.project_name == "ProjectA" for r in results)


def test_sql_file_name_filtering(temp_db, sample_results):
    """Test SQL-based file name filtering with LIKE operator"""
    results = temp_db.get_test_results(file_name="test1.py", limit=100)
    
    # Should return result1 only
    assert len(results) == 1
    assert "test1.py" in results[0].file_path


def test_sql_status_filtering_passed(temp_db, sample_results):
    """Test SQL-based status filtering for passed tests"""
    results = temp_db.get_test_results(status="passed", limit=100)
    
    # Should return result1 (all tests passed)
    assert len(results) == 1
    assert results[0].passed_tests == results[0].test_count


def test_sql_status_filtering_failed(temp_db, sample_results):
    """Test SQL-based status filtering for failed tests"""
    results = temp_db.get_test_results(status="failed", limit=100)
    
    # Should return result2 and result3 (have failed tests)
    assert len(results) == 2
    assert all(r.failed_tests > 0 for r in results)


def test_sql_combined_filtering(temp_db, sample_results):
    """Test combining multiple SQL filters"""
    results = temp_db.get_test_results(
        test_type="comparison",
        project_name="ProjectA",
        days=7,
        status="passed",
        limit=100
    )
    
    # Should return only result1 (comparison, ProjectA, within 7 days, all passed)
    assert len(results) == 1
    assert results[0].test_type == "comparison"
    assert results[0].project_name == "ProjectA"


# ============================================================================
# TASK 2 TESTS: Comprehensive Search UI (Issue #12)
# ============================================================================

def test_search_ui_widgets_exist(qapp, temp_db):
    """Test that search UI widgets are created"""
    widget = TestResultsWidget()
    widget.db_manager = temp_db
    
    # Check that search widgets exist
    assert hasattr(widget, 'project_search'), "project_search widget missing"
    assert hasattr(widget, 'file_search'), "file_search widget missing"
    assert hasattr(widget, 'status_combo'), "status_combo widget missing"
    
    # Check initial values
    assert widget.project_search.placeholderText() != ""
    assert widget.file_search.placeholderText() != ""
    assert widget.status_combo.count() == 3  # All, Passed Only, Failed Only


def test_search_ui_status_filter_values(qapp, temp_db):
    """Test status filter dropdown values"""
    widget = TestResultsWidget()
    widget.db_manager = temp_db
    
    # Check status combo values
    assert widget.status_combo.itemText(0) == "All"
    assert widget.status_combo.itemText(1) == "Passed Only"
    assert widget.status_combo.itemText(2) == "Failed Only"


def test_search_method_exists(qapp, temp_db):
    """Test that _perform_search method exists"""
    widget = TestResultsWidget()
    widget.db_manager = temp_db
    
    assert hasattr(widget, '_perform_search'), "_perform_search method missing"
    assert callable(widget._perform_search), "_perform_search is not callable"


def test_clear_search_method_exists(qapp, temp_db):
    """Test that _clear_search method exists"""
    widget = TestResultsWidget()
    widget.db_manager = temp_db
    
    assert hasattr(widget, '_clear_search'), "_clear_search method missing"
    assert callable(widget._clear_search), "_clear_search is not callable"


def test_get_status_filter_method(qapp, temp_db):
    """Test _get_status_filter method returns correct values"""
    widget = TestResultsWidget()
    widget.db_manager = temp_db
    
    # Test "All" status
    widget.status_combo.setCurrentIndex(0)
    assert widget._get_status_filter() is None
    
    # Test "Passed Only"
    widget.status_combo.setCurrentIndex(1)
    assert widget._get_status_filter() == "passed"
    
    # Test "Failed Only"
    widget.status_combo.setCurrentIndex(2)
    assert widget._get_status_filter() == "failed"


def test_clear_search_functionality(qapp, temp_db):
    """Test that clear search resets all search fields"""
    widget = TestResultsWidget()
    widget.db_manager = temp_db
    
    # Set some search values
    widget.project_search.setText("ProjectA")
    widget.file_search.setText("test.py")
    widget.status_combo.setCurrentIndex(1)
    
    # Clear search
    widget._clear_search()
    
    # Verify all fields are cleared
    assert widget.project_search.text() == ""
    assert widget.file_search.text() == ""
    assert widget.status_combo.currentIndex() == 0


# ============================================================================
# TASK 3 TESTS: ZIP Export Functionality (Issues #11, #33)
# ============================================================================

def test_export_method_exists(qapp):
    """Test that export_results method exists in ResultsWindow"""
    window = ResultsWindow()
    
    assert hasattr(window, 'export_results'), "export_results method missing"
    assert callable(window.export_results), "export_results is not callable"


def test_export_method_not_placeholder(qapp):
    """Test that export_results is no longer a placeholder"""
    # Read the source code to verify implementation
    source_path = Path(__file__).parent.parent.parent / "src" / "app" / "presentation" / "views" / "results" / "results_window.py"
    
    with open(source_path, 'r') as f:
        content = f.read()
    
    # Verify old placeholder is gone
    assert "Export functionality coming soon!" not in content
    
    # Verify new implementation exists
    assert "zipfile.ZipFile" in content
    assert "code/" in content  # ZIP structure
    assert "passed/" in content
    assert "failed/" in content
    assert "summary.txt" in content


def test_result_id_stored_in_table(qapp, temp_db, sample_results):
    """Test that result ID is stored in table items for export"""
    widget = TestResultsWidget()
    widget.db_manager = temp_db
    
    # Populate table with sample results
    widget._populate_results_table(sample_results)
    
    # Check first row has result ID stored
    first_item = widget.results_table.item(0, 0)
    assert first_item is not None
    stored_id = first_item.data(1)
    assert stored_id is not None
    assert isinstance(stored_id, int)


def test_zip_export_imports(qapp):
    """Test that ZIP export imports are present"""
    source_path = Path(__file__).parent.parent.parent / "src" / "app" / "presentation" / "views" / "results" / "results_window.py"
    
    with open(source_path, 'r') as f:
        content = f.read()
    
    # Check for required imports
    assert "import zipfile" in content
    assert "import json" in content
    assert "QFileDialog" in content


# ============================================================================
# TASK 4 & 5 TESTS: Delete Functionality (Issue #14)
# ============================================================================

def test_delete_method_exists_in_database(temp_db):
    """Test that delete_test_result method exists in DatabaseManager"""
    assert hasattr(temp_db, 'delete_test_result'), "delete_test_result method missing"
    assert callable(temp_db.delete_test_result), "delete_test_result is not callable"


def test_delete_existing_result(temp_db, sample_results):
    """Test deleting an existing test result"""
    result_id = sample_results[0].id
    
    # Verify result exists
    results_before = temp_db.get_test_results(limit=100)
    assert len(results_before) == 3
    
    # Delete the result
    success = temp_db.delete_test_result(result_id)
    assert success is True
    
    # Verify result is deleted
    results_after = temp_db.get_test_results(limit=100)
    assert len(results_after) == 2
    assert all(r.id != result_id for r in results_after)


def test_delete_nonexistent_result(temp_db):
    """Test deleting a non-existent result returns False"""
    success = temp_db.delete_test_result(999999)
    assert success is False


def test_delete_ui_button_exists(qapp, temp_db):
    """Test that Delete button column exists in results table"""
    widget = TestResultsWidget()
    widget.db_manager = temp_db
    
    # Check column count (should be 10 now with Delete column)
    assert widget.results_table.columnCount() == 10
    
    # Check header label
    headers = [widget.results_table.horizontalHeaderItem(i).text() 
               for i in range(widget.results_table.columnCount())]
    assert "Delete" in headers


def test_delete_ui_method_exists(qapp, temp_db):
    """Test that _delete_selected_result method exists"""
    widget = TestResultsWidget()
    widget.db_manager = temp_db
    
    assert hasattr(widget, '_delete_selected_result'), "_delete_selected_result method missing"
    assert callable(widget._delete_selected_result), "_delete_selected_result is not callable"


def test_delete_button_created_for_each_result(qapp, temp_db, sample_results):
    """Test that Delete button is created for each result row"""
    widget = TestResultsWidget()
    widget.db_manager = temp_db
    
    # Populate table
    widget._populate_results_table(sample_results)
    
    # Check each row has a delete button in column 9
    for row in range(len(sample_results)):
        delete_btn = widget.results_table.cellWidget(row, 9)
        assert delete_btn is not None
        assert delete_btn.text() == "Delete"


# ============================================================================
# INTEGRATION TESTS
# ============================================================================

def test_results_widget_loads_with_filters(qapp, temp_db, sample_results):
    """Test that results widget loads with all new Phase 4 features"""
    widget = TestResultsWidget()
    widget.db_manager = temp_db
    
    # Load results
    widget._load_results()
    
    # Verify table is populated
    assert widget.results_table.rowCount() > 0


def test_results_window_initialization(qapp):
    """Test that results window initializes without errors"""
    window = ResultsWindow()
    
    # Check that display area is created
    assert hasattr(window, 'display_area')
    assert window.display_area.__class__.__name__ == "TestResultsWidget"


def test_phase4_no_regressions(qapp):
    """Test that Phase 4 changes don't break existing functionality"""
    # Read source files to check for Phase 1-3 features
    widget_path = Path(__file__).parent.parent.parent / "src" / "app" / "presentation" / "views" / "results" / "results_widget.py"
    
    with open(widget_path, 'r') as f:
        content = f.read()
    
    # Phase 1: Standardized naming
    assert '"comparison"' in content
    assert '"benchmark"' in content
    
    # Phase 3: Validator support
    assert '"validator"' in content
    assert '"Validator Tests"' in content


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
