# -*- coding: utf-8 -*-
"""
Quick test to verify multi-language TestTabWidget integration
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_multi_language_config():
    """Test multi-language configuration parsing."""
    from src.app.presentation.widgets.display_area_widgets.test_tab_widget import TestTabWidget
    
    print("🧪 Testing Multi-Language TestTabWidget...")
    
    # Test 1: Multi-language config
    tab_config = {
        'Generator': {
            'cpp': 'generator.cpp',
            'py': 'generator.py',
            'java': 'Generator.java'
        },
        'Test Code': {
            'cpp': 'test.cpp',
            'py': 'test.py',
            'java': 'TestCode.java'
        }
    }
    
    try:
        widget = TestTabWidget(
            tab_config=tab_config,
            multi_language=True,
            default_language='cpp'
        )
        
        print("✅ Multi-language widget created successfully!")
        
        # Test language state
        print(f"   Available languages: {widget.available_languages}")
        print(f"   Default language: {widget.default_language}")
        print(f"   Current languages per tab: {widget.current_language_per_tab}")
        
        # Test file path generation
        file_path = widget._get_current_file_path('Generator', 'py')
        print(f"   Python Generator file path: {file_path}")
        
        # Test template generation
        cpp_template = widget._get_cpp_template('Generator')
        py_template = widget._get_python_template('Generator') 
        java_template = widget._get_java_template('Generator')
        
        print(f"   C++ template length: {len(cpp_template)} chars")
        print(f"   Python template length: {len(py_template)} chars")
        print(f"   Java template length: {len(java_template)} chars")
        
    except Exception as e:
        print(f"❌ Error creating multi-language widget: {e}")
        return False
    
    # Test 2: Legacy compatibility
    try:
        legacy_config = {
            'Generator': 'generator.cpp',
            'Test Code': 'test.cpp'
        }
        
        legacy_widget = TestTabWidget(
            tab_config=legacy_config,
            multi_language=False
        )
        
        print("✅ Legacy single-language widget created successfully!")
        
    except Exception as e:
        print(f"❌ Error creating legacy widget: {e}")
        return False
    
    print("🎉 All tests passed!")
    return True

if __name__ == "__main__":
    success = test_multi_language_config()
    
    if success:
        print("\n🚀 Multi-language TestTabWidget is ready!")
        print("   - Open Comparator, Validator, or Benchmarker")
        print("   - Look for dropdown arrows on tab buttons")
        print("   - Click dropdown to switch between CPP, PY, JAVA")
        print("   - Each language gets appropriate templates!")
    else:
        print("\n❌ Tests failed - check implementation")
        sys.exit(1)