"""
Unit tests for BaseStatusView widget.
"""

import pytest
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QMessageBox
from unittest.mock import Mock, patch
from src.app.presentation.widgets.unified_status_view import BaseStatusView


class TestBaseStatusView:
    """Test suite for BaseStatusView"""
    
    def test_base_status_view_creation(self, qtbot):
        """Test status view can be created"""
        view = BaseStatusView('comparator')
        qtbot.addWidget(view)
        
        assert view.test_type == 'comparator'
        assert hasattr(view, 'controls_panel')
        assert hasattr(view, 'progress_section')
        assert hasattr(view, 'cards_section')
        assert view.tests_running == False
        assert view.total_tests == 0
        
    def test_status_view_has_required_components(self, qtbot):
        """Test status view has all required UI components"""
        view = BaseStatusView('validator')
        qtbot.addWidget(view)
        
        # Check components exist - no sidebar or splitter anymore
        assert hasattr(view, 'controls_panel')
        assert hasattr(view, 'progress_section')
        assert hasattr(view, 'cards_section')
        assert not hasattr(view, 'sidebar')  # Should not have sidebar
        assert not hasattr(view, 'splitter')  # Should not have splitter
        
    def test_stop_signal_emitted_when_running(self, qtbot):
        """Test stop button emits signal when tests are running"""
        view = BaseStatusView('comparator')
        qtbot.addWidget(view)
        
        view.tests_running = True
        
        with qtbot.waitSignal(view.stopRequested):
            view._handle_stop()
            
        assert view.tests_running == False
        
    def test_stop_does_nothing_when_not_running(self, qtbot):
        """Test stop does nothing when tests aren't running"""
        view = BaseStatusView('comparator')
        qtbot.addWidget(view)
        
        view.tests_running = False
        
        # Should not emit signal
        with qtbot.assertNotEmitted(view.stopRequested):
            view._handle_stop()
            
    def test_back_signal_emitted_when_not_running(self, qtbot):
        """Test back button emits signal when tests aren't running"""
        view = BaseStatusView('comparator')
        qtbot.addWidget(view)
        
        view.tests_running = False
        
        with qtbot.waitSignal(view.backRequested):
            view._handle_back()
            
    @patch('src.app.presentation.widgets.unified_status_view.QMessageBox.question')
    def test_back_shows_confirmation_when_running(self, mock_question, qtbot):
        """Test back button shows confirmation when tests are running"""
        view = BaseStatusView('comparator')
        qtbot.addWidget(view)
        
        view.tests_running = True
        
        # User clicks "No"
        mock_question.return_value = QMessageBox.No
        
        with qtbot.assertNotEmitted(view.backRequested):
            view._handle_back()
            
        mock_question.assert_called_once()
        
    @patch('src.app.presentation.widgets.unified_status_view.QMessageBox.question')
    def test_back_stops_and_emits_on_yes(self, mock_question, qtbot):
        """Test back button stops tests and emits signal when user confirms"""
        view = BaseStatusView('comparator')
        qtbot.addWidget(view)
        
        view.tests_running = True
        
        # User clicks "Yes"
        mock_question.return_value = QMessageBox.Yes
        
        with qtbot.waitSignal(view.backRequested):
            view._handle_back()
            
        assert view.tests_running == False
        
    def test_on_tests_started_initializes_state(self, qtbot):
        """Test on_tests_started initializes test state"""
        view = BaseStatusView('benchmarker')
        qtbot.addWidget(view)
        
        view.on_tests_started(10)
        
        assert view.tests_running == True
        assert view.total_tests == 10
        assert view.completed_tests == 0
        assert view.passed_tests == 0
        assert view.failed_tests == 0
        
    def test_on_test_completed_updates_counters(self, qtbot):
        """Test on_test_completed updates test counters"""
        view = BaseStatusView('comparator')
        qtbot.addWidget(view)
        
        view.on_tests_started(5)
        
        # Complete a passing test
        view.on_test_completed(1, True)
        assert view.completed_tests == 1
        assert view.passed_tests == 1
        assert view.failed_tests == 0
        
        # Complete a failing test
        view.on_test_completed(2, False)
        assert view.completed_tests == 2
        assert view.passed_tests == 1
        assert view.failed_tests == 1
        
    def test_on_all_tests_completed_marks_done(self, qtbot):
        """Test on_all_tests_completed marks tests as done"""
        view = BaseStatusView('validator')
        qtbot.addWidget(view)
        
        view.tests_running = True
        view.on_all_tests_completed(True)
        
        assert view.tests_running == False
        
    def test_test_type_stored_correctly(self, qtbot):
        """Test test_type is stored for all types"""
        for test_type in ['comparator', 'validator', 'benchmarker']:
            view = BaseStatusView(test_type)
            qtbot.addWidget(view)
            assert view.test_type == test_type
            
    def test_content_only_no_sidebar_or_splitter(self, qtbot):
        """Test status view is content-only (no sidebar or splitter)"""
        view = BaseStatusView('comparator')
        qtbot.addWidget(view)
        
        # Should not have sidebar or splitter - embedded in display area
        assert not hasattr(view, 'sidebar')
        assert not hasattr(view, 'splitter')
        # Should have content components
        assert hasattr(view, 'controls_panel')
        assert hasattr(view, 'progress_section')
        assert hasattr(view, 'cards_section')
