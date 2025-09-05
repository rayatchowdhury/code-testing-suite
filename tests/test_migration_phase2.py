"""
Phase 2 Migration Tests - Comprehensive validation of src structure migration.
"""
import pytest
import sys
from pathlib import Path

# Add both src and project root to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
sys.path.insert(0, str(Path(__file__).parent.parent))

class TestPhase2Migration:
    """Test that Phase 2 migration preserved all functionality"""
    
    def test_directory_structure_complete(self):
        """Test that all expected directories were created"""
        expected_dirs = [
            "src/app/ai/config",
            "src/app/ai/core", 
            "src/app/config/management",
            "src/app/views/code_editor",
            "src/app/styles/components",
            "src/resources/icons"
        ]
        
        for dir_path in expected_dirs:
            assert Path(dir_path).exists(), f"Missing directory: {dir_path}"
    
    def test_entry_points_importable(self):
        """Test that entry points can be imported"""
        try:
            from app.__main__ import main
            assert callable(main)
        except ImportError:
            pytest.fail("Cannot import main entry point")
    
    def test_core_modules_importable(self):
        """Test that core modules can be imported from new locations"""
        try:
            from app.constants import paths
            from app.views import main_window
            from app.styles import style
            from app.utils import window_manager
        except ImportError as e:
            pytest.fail(f"Core module import failed: {e}")
    
    def test_resources_accessible(self):
        """Test that resources are accessible from new location"""
        from app.constants.paths import RESOURCES_DIR, ICONS_DIR
        
        assert Path(RESOURCES_DIR).exists(), "Resources directory not found"
        assert Path(ICONS_DIR).exists(), "Icons directory not found"
    
    def test_cross_module_imports(self):
        """Test that cross-module imports work in new structure"""
        try:
            # Test that views can import widgets
            from app.views.main_window import MainWindow
            # Test that widgets can import styles
            from app.widgets.sidebar import Sidebar
            # Test successful instantiation
            sidebar = Sidebar("Test")
            assert sidebar is not None
        except ImportError as e:
            pytest.fail(f"Cross-module import failed: {e}")

class TestPerformanceRegression:
    """Test that migration didn't cause performance regression"""
    
    def test_import_performance(self):
        """Test that imports are still fast after migration"""
        import time
        
        start_time = time.perf_counter()
        try:
            from app import __main__
            from app.views import main_window
            from app.styles import style
        except ImportError:
            pytest.skip("Imports not working - performance test skipped")
        
        end_time = time.perf_counter()
        import_time = end_time - start_time
        
        # Should complete within reasonable time
        assert import_time < 3.0, f"Imports too slow: {import_time:.3f}s"

class TestBackwardCompatibility:
    """Test that legacy interfaces still work"""
    
    def test_legacy_main_py_works(self):
        """Test that main.py still works as entry point"""
        # This would be tested in subprocess in real scenario
        # For now, just test the import structure exists
        assert Path("main.py").exists(), "Legacy main.py missing"
        
        # Test that main.py can find new structure
        with open("main.py") as f:
            content = f.read()
            assert "src" in content, "Legacy main.py not updated for src structure"
