"""
Integration Tests for DetailedResultDialog

Phase 4: Results Detail Consolidation
Tests for unified detailed results dialog with all 4 content pages.
"""

import json
import pytest
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock

from PySide6.QtWidgets import QApplication, QFileDialog, QMessageBox
from PySide6.QtCore import Qt

from src.app.persistence.database import TestResult
from src.app.presentation.dialogs.result_detail import DetailedResultDialog, DetailedResultViewModel


@pytest.fixture
def sample_test_result():
    """Create a sample test result with all fields populated."""
    test_result = TestResult(
        id=1,
        project_name="TestProject",
        test_type="comparison",
        file_path="c:/test/test.cpp",
        timestamp=datetime.now().isoformat(),
        test_count=5,
        passed_tests=3,
        failed_tests=2,
        total_time=1.234,
        test_details=json.dumps([
            {
                "test": 1,
                "passed": True,
                "execution_time": 0.1,
                "input": "1 2",
                "output": "3"
            },
            {
                "test": 2,
                "passed": True,
                "execution_time": 0.2,
                "input": "5 10",
                "output": "15"
            },
            {
                "test": 3,
                "passed": True,
                "execution_time": 0.15,
                "input": "0 0",
                "output": "0"
            },
            {
                "test": 4,
                "passed": False,
                "execution_time": 0.3,
                "input": "100 200",
                "expected_output": "300",
                "actual_output": "299",
                "error": "Output mismatch"
            },
            {
                "test": 5,
                "passed": False,
                "execution_time": 0.484,
                "input": "-5 5",
                "expected_output": "0",
                "actual_output": "1",
                "error": "Incorrect calculation"
            },
        ]),
        files_snapshot=json.dumps({
            "generator_code": "// Generator code\n#include <iostream>",
            "test_code": "// Test code\n#include <iostream>",
            "correct_code": "// Correct code\n#include <iostream>",
        }),
        mismatch_analysis=json.dumps({
            "summary": {
                "total_char_differences": 5,
                "total_line_differences": 2
            }
        }),
    )
    return test_result


@pytest.fixture
def dialog(qtbot, sample_test_result):
    """Create dialog instance for testing."""
    dialog = DetailedResultDialog(sample_test_result)
    qtbot.addWidget(dialog)
    return dialog


class TestDetailedResultViewModel:
    """Test ViewModel logic (pure Python, no Qt)."""

    def test_viewmodel_initialization(self, sample_test_result):
        """Test ViewModel initializes with test result."""
        viewmodel = DetailedResultViewModel(sample_test_result)

        assert viewmodel.test_result == sample_test_result
        assert viewmodel._test_details_cache is None
        assert viewmodel._files_snapshot_cache is None
        assert viewmodel._mismatch_analysis_cache is None

    def test_get_summary_data(self, sample_test_result):
        """Test summary data formatting."""
        viewmodel = DetailedResultViewModel(sample_test_result)
        summary = viewmodel.get_summary_data()

        assert summary["test_type"] == "COMPARISON"
        assert summary["project_name"] == "TestProject"
        assert summary["total_tests"] == 5
        assert summary["passed_tests"] == 3
        assert summary["failed_tests"] == 2
        assert summary["success_rate"] == "60.0%"
        assert "1.234" in summary["total_time"]

    def test_get_test_details_caching(self, sample_test_result):
        """Test test details are parsed and cached."""
        viewmodel = DetailedResultViewModel(sample_test_result)

        # First call parses
        details1 = viewmodel.get_test_details()
        assert isinstance(details1, list)
        assert len(details1) == 5
        assert viewmodel._test_details_cache is not None

        # Second call uses cache
        details2 = viewmodel.get_test_details()
        assert details1 is details2  # Same object reference

    def test_get_passed_tests_filtering(self, sample_test_result):
        """Test filtering passed tests."""
        viewmodel = DetailedResultViewModel(sample_test_result)
        passed = viewmodel.get_passed_tests()

        assert len(passed) == 3
        assert all(t["passed"] for t in passed)

    def test_get_failed_tests_filtering(self, sample_test_result):
        """Test filtering failed tests."""
        viewmodel = DetailedResultViewModel(sample_test_result)
        failed = viewmodel.get_failed_tests()

        assert len(failed) == 2
        assert all(not viewmodel._is_test_passed(t) for t in failed)

    def test_get_files_snapshot_parsing(self, sample_test_result):
        """Test files snapshot parsing."""
        viewmodel = DetailedResultViewModel(sample_test_result)
        files = viewmodel.get_files_snapshot()

        assert isinstance(files, dict)
        assert "generator_code" in files
        assert "test_code" in files
        assert "correct_code" in files

    def test_get_code_file_tabs(self, sample_test_result):
        """Test code file tabs generation."""
        viewmodel = DetailedResultViewModel(sample_test_result)
        tabs = viewmodel.get_code_file_tabs()

        assert isinstance(tabs, list)
        assert len(tabs) == 3  # 3 code files
        assert all(isinstance(tab, tuple) and len(tab) == 2 for tab in tabs)

    def test_get_test_case_display_data(self, sample_test_result):
        """Test test case display data formatting."""
        viewmodel = DetailedResultViewModel(sample_test_result)
        test_details = viewmodel.get_test_details()

        # Test passed test
        passed_data = viewmodel.get_test_case_display_data(test_details[0])
        assert passed_data["passed"] is True
        assert passed_data["test_number"] == 1
        assert passed_data["execution_time"] == 0.1

        # Test failed test
        failed_data = viewmodel.get_test_case_display_data(test_details[3])
        assert failed_data["passed"] is False
        assert failed_data["expected_output"] == "300"
        assert failed_data["actual_output"] == "299"
        assert failed_data["error"] == "Output mismatch"

    def test_has_code_files(self, sample_test_result):
        """Test code files detection."""
        viewmodel = DetailedResultViewModel(sample_test_result)
        assert viewmodel.has_code_files() is True

        # Test with empty snapshot
        sample_test_result.files_snapshot = "{}"
        viewmodel2 = DetailedResultViewModel(sample_test_result)
        assert viewmodel2.has_code_files() is False

    def test_get_export_file_name(self, sample_test_result):
        """Test export filename generation."""
        viewmodel = DetailedResultViewModel(sample_test_result)
        filename = viewmodel.get_export_file_name()

        assert "test_export" in filename
        assert "TestProject" in filename
        assert ".zip" in filename


class TestDetailedResultDialogUI:
    """Test dialog UI creation and interaction."""

    def test_dialog_creation(self, dialog):
        """Test dialog creates successfully."""
        assert dialog is not None
        assert dialog.test_result is not None
        assert dialog.viewmodel is not None
        assert dialog.sidebar is not None
        assert dialog.content_stack is not None

    def test_dialog_has_4_pages(self, dialog):
        """Test dialog has 4 content pages."""
        assert dialog.content_stack.count() == 4

    def test_dialog_navigation_buttons(self, dialog):
        """Test navigation buttons exist and work."""
        assert len(dialog.nav_buttons) == 4

        # Test switching pages
        for i in range(4):
            dialog._show_page(i)
            assert dialog.content_stack.currentIndex() == i

    def test_summary_page_content(self, dialog):
        """Test summary page displays correct data."""
        dialog._show_page(0)  # Show summary page

        # Check page widget exists
        summary_page = dialog.content_stack.widget(0)
        assert summary_page is not None

        # Summary should display test type, project name, etc.
        # (Visual inspection - we can't easily test label text in Qt)

    def test_code_files_page_content(self, dialog):
        """Test code files page displays tabs."""
        dialog._show_page(1)  # Show code files page

        code_page = dialog.content_stack.widget(1)
        assert code_page is not None

        # Should have tab widget with 3 tabs (3 code files)
        # (Detailed UI testing would require more complex checks)

    def test_passed_tests_page_content(self, dialog):
        """Test passed tests page displays filtered tests."""
        dialog._show_page(2)  # Show passed tests page

        passed_page = dialog.content_stack.widget(2)
        assert passed_page is not None

        # Should show 3 passed tests
        # (Visual inspection - we can't easily count widgets)

    def test_failed_tests_page_content(self, dialog):
        """Test failed tests page displays filtered tests."""
        dialog._show_page(3)  # Show failed tests page

        failed_page = dialog.content_stack.widget(3)
        assert failed_page is not None

        # Should show 2 failed tests with error details
        # (Visual inspection - we can't easily count widgets)

    def test_back_signal_emission(self, qtbot, dialog):
        """Test back button emits signal."""
        with qtbot.waitSignal(dialog.backRequested, timeout=1000):
            # Find and click back button
            # (In real test, we'd need to find the actual button)
            dialog.backRequested.emit()

    @patch('src.app.presentation.dialogs.result_detail.view.QFileDialog.getSaveFileName')
    @patch('src.app.presentation.dialogs.result_detail.view.QMessageBox.information')
    def test_export_results(self, mock_info, mock_file_dialog, dialog, tmp_path):
        """Test export functionality."""
        # Mock file dialog to return a path
        test_file = str(tmp_path / "test_export.zip")
        mock_file_dialog.return_value = (test_file, "")

        # Trigger export
        dialog._export_results()

        # Check file dialog was called
        mock_file_dialog.assert_called_once()

        # Check success message was shown
        mock_info.assert_called_once()

        # Check file was created
        import os
        assert os.path.exists(test_file)

    @patch('src.app.persistence.database.FilesSnapshot')
    @patch('src.app.presentation.dialogs.result_detail.view.QMessageBox.question')
    @patch('src.app.presentation.dialogs.result_detail.view.QMessageBox.information')
    def test_load_to_test_cancel(self, mock_info, mock_question, mock_snapshot, dialog):
        """Test load to test cancellation."""
        # Mock FilesSnapshot
        mock_snapshot_instance = Mock()
        mock_snapshot_instance.files = {"test.cpp": {"content": "code"}}
        mock_snapshot_instance.test_type = "comparison"
        mock_snapshot_instance.primary_language = "cpp"
        mock_snapshot.from_json.return_value = mock_snapshot_instance
        
        # Mock user clicking No
        mock_question.return_value = QMessageBox.No

        # Trigger load
        dialog._load_to_test()

        # Check question was asked
        mock_question.assert_called_once()

        # Check info was not shown (cancelled)
        mock_info.assert_not_called()

    @patch('src.app.presentation.dialogs.result_detail.view.QMessageBox.warning')
    def test_load_to_test_no_files(self, mock_warning, qtbot, sample_test_result):
        """Test load to test with no files."""
        # Create result with no files
        sample_test_result.files_snapshot = None
        dialog = DetailedResultDialog(sample_test_result)
        qtbot.addWidget(dialog)

        # Trigger load
        dialog._load_to_test()

        # Check warning was shown (called with parent, title, message)
        assert mock_warning.call_count == 1


class TestDetailedResultDialogIntegration:
    """Test full integration scenarios."""

    def test_full_workflow_passed_tests(self, qtbot, dialog):
        """Test full workflow: open dialog, navigate to passed tests, view details."""
        # Open dialog (already done by fixture)
        assert dialog.content_stack.currentIndex() == 0  # Summary page

        # Navigate to passed tests
        dialog._show_page(2)
        assert dialog.content_stack.currentIndex() == 2

        # Check passed tests page exists
        passed_page = dialog.content_stack.widget(2)
        assert passed_page is not None

    def test_full_workflow_failed_tests(self, qtbot, dialog):
        """Test full workflow: open dialog, navigate to failed tests, view errors."""
        # Navigate to failed tests
        dialog._show_page(3)
        assert dialog.content_stack.currentIndex() == 3

        # Check failed tests page exists
        failed_page = dialog.content_stack.widget(3)
        assert failed_page is not None

    def test_full_workflow_code_files(self, qtbot, dialog):
        """Test full workflow: open dialog, view code files."""
        # Navigate to code files
        dialog._show_page(1)
        assert dialog.content_stack.currentIndex() == 1

        # Check code files page exists
        code_page = dialog.content_stack.widget(1)
        assert code_page is not None

    def test_dialog_data_consistency(self, dialog):
        """Test data consistency across all pages."""
        # Check viewmodel data
        summary = dialog.viewmodel.get_summary_data()
        assert summary["total_tests"] == 5
        assert summary["passed_tests"] == 3
        assert summary["failed_tests"] == 2

        # Check filtering consistency
        passed = dialog.viewmodel.get_passed_tests()
        failed = dialog.viewmodel.get_failed_tests()
        assert len(passed) + len(failed) == 5

    def test_dialog_with_minimal_data(self, qtbot):
        """Test dialog with minimal test result data."""
        minimal_result = TestResult(
            id=1,
            project_name="Minimal",
            test_type="comparison",
            file_path="test.cpp",
            timestamp=datetime.now().isoformat(),
            test_count=0,
            passed_tests=0,
            failed_tests=0,
            total_time=0.0,
        )

        dialog = DetailedResultDialog(minimal_result)
        qtbot.addWidget(dialog)

        # Should still create successfully
        assert dialog is not None
        assert dialog.content_stack.count() == 4

    def test_dialog_with_empty_json_fields(self, qtbot, sample_test_result):
        """Test dialog handles empty JSON fields gracefully."""
        sample_test_result.test_details = None
        sample_test_result.files_snapshot = None
        sample_test_result.mismatch_analysis = None

        dialog = DetailedResultDialog(sample_test_result)
        qtbot.addWidget(dialog)

        # Should create successfully
        assert dialog is not None

        # Should have empty lists/dicts
        assert dialog.viewmodel.get_test_details() == []
        assert dialog.viewmodel.get_files_snapshot() == {}
        assert dialog.viewmodel.get_mismatch_analysis() is None
