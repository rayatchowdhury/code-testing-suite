# -*- coding: utf-8 -*-
"""
Example usage of the enhanced TestTabWidget with multi-language support.

This example shows how to use both legacy (single-language) and new 
(multi-language) modes of TestTabWidget.
"""

from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QTextEdit
from PySide6.QtCore import QObject
import sys
import os

# Add the src directory to the Python path so we can import the widget
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from src.app.presentation.widgets.display_area_widgets.test_tab_widget import TestTabWidget

class TestWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("TestTabWidget Multi-Language Demo")
        self.setGeometry(100, 100, 800, 600)
        
        layout = QVBoxLayout(self)
        
        # Example 1: Legacy single-language mode
        legacy_config = {
            'Generator': 'generator.cpp',
            'Test Code': 'test.cpp'
        }
        
        self.legacy_widget = TestTabWidget(
            parent=self,
            tab_config=legacy_config,
            default_tab='Generator',
            multi_language=False
        )
        
        # Example 2: New multi-language mode
        multi_lang_config = {
            'Generator': {
                'cpp': 'generator.cpp',
                'py': 'generator.py',
                'java': 'Generator.java'
            },
            'Test Code': {
                'cpp': 'test.cpp', 
                'py': 'test.py',
                'java': 'TestCode.java'
            },
            'Validator Code': {
                'cpp': 'validator.cpp',
                'py': 'validator.py',
                'java': 'ValidatorCode.java'
            }
        }
        
        self.multi_lang_widget = TestTabWidget(
            parent=self,
            tab_config=multi_lang_config,
            default_tab='Generator',
            multi_language=True,
            default_language='cpp'
        )
        
        # Mock editor for demonstration
        self.text_edit = QTextEdit()
        self.text_edit.setPlainText("Select a tab above to see language-specific templates!")
        
        # Set the text editor as content widget
        self.multi_lang_widget.set_content_widget(self.text_edit)
        
        # Connect signals
        self.multi_lang_widget.fileChanged.connect(self.load_file)
        self.multi_lang_widget.languageChanged.connect(self.on_language_changed)
        
        layout.addWidget(self.legacy_widget)
        layout.addWidget(self.multi_lang_widget)
        
        # Activate default tab to show initial content
        self.multi_lang_widget.activate_default_tab()
    
    def load_file(self, file_path):
        """Load file content into text editor."""
        try:
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                self.text_edit.setPlainText(content)
                print(f"Loaded: {file_path}")
            else:
                print(f"File not found: {file_path}")
        except Exception as e:
            print(f"Error loading file {file_path}: {e}")
    
    def on_language_changed(self, tab_name, language):
        """Handle language change events."""
        print(f"Language changed: {tab_name} -> {language.upper()}")

def main():
    app = QApplication(sys.argv)
    window = TestWindow()
    window.show()
    
    print("Multi-Language TestTabWidget Demo")
    print("- Top widget: Legacy single-language mode")  
    print("- Bottom widget: New multi-language mode with dropdowns")
    print("- Try clicking the dropdown arrows on the bottom widget!")
    
    return app.exec()

if __name__ == "__main__":
    sys.exit(main())