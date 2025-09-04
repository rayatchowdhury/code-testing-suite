#!/usr/bin/env python3
"""
Test script to verify DetailedResultsWidget creation without GUI
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database.database_manager import DatabaseManager
from views.results.detailed_results_widget import DetailedResultsWidget
from PySide6.QtWidgets import QApplication

def test_detailed_results():
    """Test creating DetailedResultsWidget with actual database data"""
    
    # Create minimal QApplication for testing
    if not QApplication.instance():
        app = QApplication(sys.argv)
    
    db = DatabaseManager()
    results = db.get_test_results(limit=5)
    
    print(f"Testing DetailedResultsWidget with {len(results)} results...")
    
    for i, result in enumerate(results):
        print(f"\nTesting result {i+1} (ID: {result.id}):")
        try:
            # Attempt to create the widget
            widget = DetailedResultsWidget(result)
            print(f"  ✅ Success: Widget created for {result.test_type} test")
            widget.deleteLater()  # Clean up
        except Exception as e:
            print(f"  ❌ Error: {str(e)}")
            print(f"     Test type: {result.test_type}")
            print(f"     Test details length: {len(result.test_details) if result.test_details else 0}")
            print(f"     Files snapshot length: {len(result.files_snapshot) if result.files_snapshot else 0}")
            print(f"     Mismatch analysis length: {len(result.mismatch_analysis) if result.mismatch_analysis else 0}")
    
    print("\nTest completed!")

if __name__ == "__main__":
    test_detailed_results()
