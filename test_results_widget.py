#!/usr/bin/env python3
"""
Standalone test for Results widget
"""

import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PySide6.QtWidgets import QApplication, QMainWindow
from views.results.results_widget import TestResultsWidget

def test_results_widget():
    """Test the Results widget standalone"""
    print("🧪 Testing Results Widget Standalone")
    print("=" * 40)
    
    app = QApplication(sys.argv)
    
    # Create a simple window to hold the widget
    window = QMainWindow()
    window.setWindowTitle("Results Widget Test")
    window.setGeometry(100, 100, 1000, 600)
    
    # Create and add the results widget
    results_widget = TestResultsWidget()
    window.setCentralWidget(results_widget)
    
    # Show the window
    window.show()
    
    print("📊 Results widget window should now be visible")
    print("🔍 Check console for any debug messages")
    print("⏹️  Close the window to exit")
    
    # Run the application
    app.exec()

if __name__ == "__main__":
    test_results_widget()
