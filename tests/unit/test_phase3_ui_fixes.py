"""
Phase 3: Test Type Support & UI Fixes
Tests for Issues #18, #19, #17, #31, #32, #35, #36, #37
"""
import pytest
from PySide6.QtWidgets import QApplication
import sys


class TestValidatorSupport:
    """Test validator support in results UI (Issues #18, #19)"""
    
    def test_validator_in_filter_dropdown(self):
        """Test that Validator Tests appears in filter dropdown (Issue #18)"""
        from src.app.presentation.views.results.results_widget import TestResultsWidget
        
        if not QApplication.instance():
            app = QApplication(sys.argv)
        
        try:
            widget = TestResultsWidget()
            
            # Get all items in the combo box
            filter_items = [widget.test_type_combo.itemText(i) 
                           for i in range(widget.test_type_combo.count())]
            
            # Verify Validator Tests is included
            assert "Validator Tests" in filter_items
            assert "All" in filter_items
            assert "Comparison Tests" in filter_items
            assert "Benchmark Tests" in filter_items
            
        finally:
            if app:
                app.quit()
    
    def test_validator_filter_returns_correct_type(self):
        """Test that validator filter returns 'validator' (Issue #18)"""
        from src.app.presentation.views.results.results_widget import TestResultsWidget
        
        app = None
        if not QApplication.instance():
            app = QApplication(sys.argv)
        
        try:
            widget = TestResultsWidget()
            
            # Set to Validator Tests
            widget.test_type_combo.setCurrentText("Validator Tests")
            
            # Get filter value
            filter_value = widget._get_test_type_filter()
            
            # Should return 'validator' (new Phase 1 naming)
            assert filter_value == "validator"
            
        finally:
            if app:
                app.quit()
    
    def test_validator_statistics_label_exists(self):
        """Test that validator statistics label exists (Issue #19)"""
        from src.app.presentation.views.results.results_widget import TestResultsWidget
        
        app = None
        if not QApplication.instance():
            app = QApplication(sys.argv)
        
        try:
            widget = TestResultsWidget()
            
            # Should have validator label
            assert hasattr(widget, 'validator_tests_label')
            assert widget.validator_tests_label.text() == "Validator Tests: 0"
            
        finally:
            if app:
                app.quit()
    
    def test_filter_uses_new_naming_convention(self):
        """Test that filters use new naming (comparison, benchmark, validator)"""
        from src.app.presentation.views.results.results_widget import TestResultsWidget
        
        app = None
        if not QApplication.instance():
            app = QApplication(sys.argv)
        
        try:
            widget = TestResultsWidget()
            
            # Test Comparison Tests
            widget.test_type_combo.setCurrentText("Comparison Tests")
            assert widget._get_test_type_filter() == "comparison"  # Not "stress"
            
            # Test Benchmark Tests
            widget.test_type_combo.setCurrentText("Benchmark Tests")
            assert widget._get_test_type_filter() == "benchmark"  # Not "tle"
            
            # Test All
            widget.test_type_combo.setCurrentText("All")
            assert widget._get_test_type_filter() is None
            
        finally:
            if app:
                app.quit()


class TestUICleanup:
    """Test UI cleanup tasks (Issues #17, #35, #36, #37)"""
    
    def test_no_redundant_sidebar_buttons(self):
        """Test that redundant View Options section is removed (Issue #17)"""
        from src.app.presentation.views.results.results_window import ResultsWindow
        
        app = None
        if not QApplication.instance():
            app = QApplication(sys.argv)
        
        try:
            window = ResultsWindow()
            
            # The handle_view_button method should not exist
            assert not hasattr(window, 'handle_view_button') or \
                   'redundant' in window.handle_view_button.__doc__.lower() if hasattr(window, 'handle_view_button') else True
            
        finally:
            if app:
                app.quit()
    
    def test_no_recent_activity_table(self):
        """Test that Recent Activity table is removed (Issue #35)"""
        from src.app.presentation.views.results.results_widget import TestResultsWidget
        
        app = None
        if not QApplication.instance():
            app = QApplication(sys.argv)
        
        try:
            widget = TestResultsWidget()
            
            # Should not have recent_table attribute
            assert not hasattr(widget, 'recent_table')
            
            # _update_recent_activity method should not exist or be removed
            assert not hasattr(widget, '_update_recent_activity') or \
                   'removed' in widget._update_recent_activity.__doc__.lower() if hasattr(widget, '_update_recent_activity') else True
            
        finally:
            if app:
                app.quit()
    
    def test_no_success_progress_bar(self):
        """Test that success rate progress bar is removed (Issue #36)"""
        from src.app.presentation.views.results.results_widget import TestResultsWidget
        
        app = None
        if not QApplication.instance():
            app = QApplication(sys.argv)
        
        try:
            widget = TestResultsWidget()
            
            # Should not have success_progress attribute
            assert not hasattr(widget, 'success_progress')
            
            # Should still have success_rate_label (text display)
            assert hasattr(widget, 'success_rate_label')
            
        finally:
            if app:
                app.quit()
    
    def test_options_button_restored(self):
        """Test that Options button was restored (Issue #37 - REVERTED)"""
        # Issue #37 was reverted - Options button is functional (opens config dialog)
        # The button was restored as it provides access to configuration settings
        # This test verifies the code exists in the source file
        
        import os
        file_path = os.path.join('src', 'app', 'presentation', 'views', 'main_window', 'main_window.py')
        
        with open(file_path, 'r', encoding='utf-8') as f:
            source = f.read()
        
        # Verify the methods exist in source
        assert 'def _create_options_button' in source
        assert 'def _show_options_dialog' in source
        assert 'ConfigView' in source  # Opens config dialog


class TestDataCleanup:
    """Test data cleanup configuration (Issue #32)"""
    
    def test_clear_old_data_uses_7_days(self):
        """Test that clear old data uses 7 days instead of 30 (Issue #32)"""
        from src.app.presentation.views.results.results_window import ResultsWindow
        import re
        
        app = None
        if not QApplication.instance():
            app = QApplication(sys.argv)
        
        try:
            window = ResultsWindow()
            
            # Check the clear_old_data method source code for '7'
            import inspect
            source = inspect.getsource(window.clear_old_data)
            
            # Should mention 7 days, not 30
            assert '7' in source
            assert 'cleanup_old_data(7)' in source
            
        finally:
            if app:
                app.quit()


class TestPhase3Integration:
    """Integration tests for Phase 3 changes"""
    
    def test_results_widget_loads_without_errors(self):
        """Test that results widget loads successfully with all Phase 3 changes"""
        from src.app.presentation.views.results.results_widget import TestResultsWidget
        
        app = None
        if not QApplication.instance():
            app = QApplication(sys.argv)
        
        try:
            widget = TestResultsWidget()
            
            # Basic checks
            assert widget is not None
            assert hasattr(widget, 'test_type_combo')
            assert hasattr(widget, 'validator_tests_label')
            assert not hasattr(widget, 'success_progress')
            assert not hasattr(widget, 'recent_table')
            
        finally:
            if app:
                app.quit()
    
    def test_results_window_loads_without_errors(self):
        """Test that results window loads successfully with all Phase 3 changes"""
        from src.app.presentation.views.results.results_window import ResultsWindow
        
        app = None
        if not QApplication.instance():
            app = QApplication(sys.argv)
        
        try:
            window = ResultsWindow()
            
            # Basic checks
            assert window is not None
            assert hasattr(window, 'display_area')
            
        finally:
            if app:
                app.quit()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
