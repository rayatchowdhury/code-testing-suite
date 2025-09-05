"""
Test GUI application startup without actually showing windows.
This validates that the application can be instantiated.
"""
import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_gui_startup():
    """Test that GUI application can start up"""
    # Set environment to avoid GUI display
    os.environ['QT_QPA_PLATFORM'] = 'offscreen'
    
    try:
        from PySide6.QtWidgets import QApplication
        from app.__main__ import create_main_window
        
        # Create application
        app = QApplication(sys.argv)
        
        # Test window creation
        window = create_main_window()
        assert window is not None
        
        print("✅ GUI startup test passed")
        
        # Clean shutdown
        window.close()
        app.quit()
        return True
        
    except Exception as e:
        print(f"❌ GUI startup test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_gui_startup()
    sys.exit(0 if success else 1)
