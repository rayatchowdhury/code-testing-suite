"""
Functional baseline tests to ensure migration preserves all functionality.
These tests establish the baseline that must be maintained throughout migration.
"""
import pytest
from PySide6.QtWidgets import QApplication
from unittest.mock import patch
import sys
import time
from pathlib import Path

# Add src to Python path for testing
src_path = Path(__file__).parent.parent / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

class TestApplicationBaseline:
    """Test core application functionality"""
    
    def test_main_module_import(self):
        """Test that main module imports without error"""
        try:
            import main
            assert hasattr(main, 'main')
            assert callable(main.main)
        except ImportError as e:
            pytest.fail(f"Cannot import main module: {e}")
    
    def test_window_manager_creation(self):
        """Test that window manager can be instantiated"""
        from src.app.utils.window_manager import WindowManager
        wm = WindowManager()
        assert wm is not None
    
    def test_main_window_creation(self, qapp):
        """Test that main window can be created"""
        from src.app.views.main_window import MainWindow
        window = MainWindow()
        assert window is not None
        window.close()

class TestUIComponentBaseline:
    """Test UI component functionality"""
    
    def test_sidebar_creation(self, qapp):
        """Test sidebar widget creation"""
        from src.app.widgets.sidebar import Sidebar
        sidebar = Sidebar("Test")
        assert sidebar is not None
        assert sidebar.objectName() == "sidebar"
    
    def test_display_area_creation(self, qapp):
        """Test display area widget creation"""
        from src.app.widgets.display_area import DisplayArea
        display = DisplayArea()
        assert display is not None
        assert display.objectName() == "display_area"

class TestStyleSystemBaseline:
    """Test styling system functionality"""
    
    def test_styles_import(self):
        """Test that style modules can be imported"""
        try:
            from src.app.styles.style import SIDEBAR_STYLE, WEBVIEW_STYLE, DISPLAY_AREA_STYLE
            assert isinstance(SIDEBAR_STYLE, str)
            assert isinstance(WEBVIEW_STYLE, str) 
            assert isinstance(DISPLAY_AREA_STYLE, str)
        except ImportError as e:
            pytest.fail(f"Cannot import styles: {e}")

class TestCoreServicesBaseline:
    """Test core service functionality"""
    
    def test_config_manager(self):
        """Test configuration manager"""
        from src.app.config.management.config_manager import ConfigManager
        config = ConfigManager()
        assert config is not None
    
    def test_database_manager(self):
        """Test database manager"""
        from src.app.database.database_manager import DatabaseManager
        db = DatabaseManager()
        assert db is not None

class TestPerformanceBaseline:
    """Performance baseline measurements"""
    
    def test_import_performance(self):
        """Test that imports complete within reasonable time"""
        start_time = time.time()
        
        # Import core modules
        import main
        from src.app.views import main_window
        from src.app.widgets import sidebar
        from src.app.utils import window_manager
        
        end_time = time.time()
        import_time = end_time - start_time
        
        # Should complete within 2 seconds
        assert import_time < 2.0, f"Imports took {import_time:.3f}s (too slow)"
    
    def test_main_window_creation_performance(self, qapp):
        """Test main window creation performance"""
        start_time = time.time()
        
        try:
            from src.app.views.main_window import MainWindow
            window = MainWindow()
            window.close()
        except Exception as e:
            pytest.fail(f"Main window creation failed: {e}")
        
        end_time = time.time()
        creation_time = end_time - start_time
        
        # Should complete within 3 seconds  
        assert creation_time < 3.0, f"Window creation took {creation_time:.3f}s (too slow)"
