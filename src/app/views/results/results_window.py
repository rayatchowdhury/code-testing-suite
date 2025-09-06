from ...views.base_window import SidebarWindowBase
from ...widgets.sidebar import Sidebar
from PySide6.QtWidgets import QPushButton, QVBoxLayout, QWidget
from ...views.results.results_widget import TestResultsWidget

class ResultsWindow(SidebarWindowBase):
    """Window to display test results and analytics"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.sidebar = Sidebar("Results & Analytics")
        
        # Actions section
        action_section = self.sidebar.add_section("Actions")
        
        # Add action buttons
        for button_text in ['Refresh Data', 'Export Results', 'Clear Old Data']:
            btn = self.sidebar.add_button(button_text, action_section)
            btn.clicked.connect(lambda checked, text=button_text: self.handle_action_button(text))
        
        # View options section
        view_section = self.sidebar.add_section("View Options")
        
        for button_text in ['Show All', 'Show Stress Tests', 'Show TLE Tests']:
            btn = self.sidebar.add_button(button_text, view_section)
            btn.clicked.connect(lambda checked, text=button_text: self.handle_view_button(text))
        
        self.sidebar.add_help_button()
        self.sidebar.add_footer_divider()
        
        # Footer buttons
        back_btn, options_btn = self.create_footer_buttons()
        self.sidebar.setup_horizontal_footer_buttons(back_btn, options_btn)
        
        # Create display area with results widget
        self.display_area = TestResultsWidget()
        
        # Setup splitter
        self.setup_splitter(self.sidebar, self.display_area)
        
        # Connect signals
        self.sidebar.button_clicked.connect(self.handle_button_click)
    
    def handle_action_button(self, button_text):
        """Handle action button clicks"""
        if button_text == 'Refresh Data':
            self.display_area._load_results()
        elif button_text == 'Export Results':
            self.export_results()
        elif button_text == 'Clear Old Data':
            self.clear_old_data()
    
    def handle_view_button(self, button_text):
        """Handle view option button clicks"""
        if button_text == 'Show All':
            self.display_area.test_type_combo.setCurrentText("All")
        elif button_text == 'Show Stress Tests':
            self.display_area.test_type_combo.setCurrentText("Stress Tests")
        elif button_text == 'Show TLE Tests':
            self.display_area.test_type_combo.setCurrentText("TLE Tests")
    
    def export_results(self):
        """Export results to CSV or JSON"""
        # NOTE: Export functionality planned for future release
        from PySide6.QtWidgets import QMessageBox
        QMessageBox.information(self, "Export", "Export functionality coming soon!")
    
    def clear_old_data(self):
        """Clear old data from database"""
        reply = QMessageBox.question(
            self, 
            "Clear Old Data", 
            "This will delete test results older than 30 days. Continue?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.display_area.db_manager.cleanup_old_data(30)
            self.display_area._load_results()
            QMessageBox.information(self, "Success", "Old data cleared successfully!")
    
    def handle_button_click(self, button_text):
        """Handle sidebar button clicks"""
        if button_text == 'Help Center':
            if self.can_close():
                self.parent.window_manager.show_window('help_center')
        else:
            super().handle_button_click(button_text)
    
    def refresh_ai_panels(self):
        """Refresh AI panel visibility (not applicable for results window)"""
        pass
