#!/usr/bin/env python3

"""
Debug script to test AI panel functionality
"""

import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from widgets.display_area_widgets.ai_panel import AIPanel
from ai.config.ai_config import AIConfig

def main():
    app = QApplication(sys.argv)
    
    # Test AI configuration
    print(f"AI Enabled: {AIConfig.is_ai_enabled()}")
    print(f"Should Show Panel: {AIConfig.should_show_ai_panel()}")
    print(f"AI Ready: {AIConfig.is_ai_ready()}")
    
    # Create main window
    window = QMainWindow()
    window.setWindowTitle("AI Panel Debug")
    window.resize(800, 200)
    
    central_widget = QWidget()
    layout = QVBoxLayout(central_widget)
    
    # Create AI panel
    print("Creating AI panel...")
    ai_panel = AIPanel(parent=central_widget)
    print(f"AI panel created. Visible: {ai_panel.isVisible()}")
    print(f"AI panel size: {ai_panel.size()}")
    
    layout.addWidget(ai_panel)
    window.setCentralWidget(central_widget)
    
    print(f"After adding to layout. Visible: {ai_panel.isVisible()}")
    print(f"AI panel size: {ai_panel.size()}")
    
    # Show window
    window.show()
    
    print(f"After showing window. AI panel visible: {ai_panel.isVisible()}")
    print(f"AI panel size: {ai_panel.size()}")
    
    app.exec()

if __name__ == '__main__':
    main()
