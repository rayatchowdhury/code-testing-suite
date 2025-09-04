#!/usr/bin/env python3
"""
Test script to simulate clicking View Details button and catch crashes
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database.database_manager import DatabaseManager
from views.results.results_widget import TestResultsWidget
from views.results.detailed_results_widget import DetailedResultsWidget
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from PySide6.QtCore import QTimer

class TestWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Test View Details")
        self.setGeometry(100, 100, 800, 600)
        
        # Create main widget
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        
        layout = QVBoxLayout(main_widget)
        
        # Create results widget
        self.results_widget = TestResultsWidget()
        layout.addWidget(self.results_widget)
        
        # Test clicking after a delay
        QTimer.singleShot(1000, self.test_view_details)
    
    def test_view_details(self):
        """Test the View Details functionality"""
        print("Testing View Details functionality...")
        
        # Get test results
        db = DatabaseManager()
        results = db.get_test_results(limit=2)
        
        if not results:
            print("No test results found in database")
            QApplication.quit()
            return
        
        print(f"Found {len(results)} test results, testing each one...")
        
        # Test each result
        for i, result in enumerate(results):
            print(f"\nTesting result {i+1} (ID: {result.id}, type: {result.test_type}):")
            
            try:
                # Simulate clicking View Details
                self.results_widget._show_detailed_view(result)
                print(f"  ✅ Success: View Details worked for result {result.id}")
                
                # Close the detail tab after a moment
                if hasattr(self.results_widget, 'tab_widget'):
                    # Find and close detail tabs
                    tab_widget = self.results_widget.tab_widget
                    for tab_index in range(tab_widget.count()):
                        tab_text = tab_widget.tabText(tab_index)
                        if "Details" in tab_text:
                            print(f"  Closing detail tab: {tab_text}")
                            tab_widget.removeTab(tab_index)
                            break
                            
            except Exception as e:
                print(f"  ❌ Error: {str(e)}")
                import traceback
                traceback.print_exc()
        
        print("\nTest completed! Exiting in 2 seconds...")
        QTimer.singleShot(2000, QApplication.quit)

def main():
    app = QApplication(sys.argv)
    
    window = TestWindow()
    window.show()
    
    app.exec()

if __name__ == "__main__":
    main()
