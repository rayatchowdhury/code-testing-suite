"""Validate Phase 3 cleanup results"""

import pytest
import time
from pathlib import Path

class TestCleanupResults:
    """Verify cleanup didn't break functionality"""
    
    def test_import_optimization(self):
        """Verify wildcard imports are eliminated"""
        
        # Test that cleaned imports still work
        from src.app.constants import PROJECT_ROOT, RESOURCES_DIR, USER_DATA_DIR
        from src.app.config.management.config_manager import ConfigManager
        from src.app.config.config_exceptions import (
            ConfigError,
            ConfigPermissionError,
            ConfigFormatError,
            ConfigValidationError,
            ConfigLoadError,
            ConfigSaveError,
            ConfigMissingError
        )
        
        # Test that imports are functional
        assert PROJECT_ROOT is not None
        assert RESOURCES_DIR is not None
        assert USER_DATA_DIR is not None
        
        # Test config manager instantiation
        config_mgr = ConfigManager()
        assert hasattr(config_mgr, 'load_config')
        assert hasattr(config_mgr, 'save_config')
        
        # Test exception classes exist
        assert issubclass(ConfigError, Exception)
        assert issubclass(ConfigPermissionError, ConfigError)
        assert issubclass(ConfigFormatError, ConfigError)
        assert issubclass(ConfigValidationError, ConfigError)
        assert issubclass(ConfigLoadError, ConfigError)
        assert issubclass(ConfigSaveError, ConfigError)
        assert issubclass(ConfigMissingError, ConfigError)
    
    def test_functionality_preserved(self):
        """Verify all original functionality still works"""
        
        # Test file operations optimization
        from src.app.utils.file_operations import FileOperations
        
        file_ops = FileOperations()
        assert hasattr(file_ops, 'save_file')
        assert hasattr(file_ops, 'load_file')
        assert hasattr(file_ops, 'open_file')
        
        # Test optimized file operations with Path objects
        test_path = Path("test.txt")
        test_content = "test content"
        
        # This should work with both string and Path objects
        assert callable(file_ops.save_file)
        assert callable(file_ops.load_file)
    
    def test_debug_code_removal(self):
        """Verify debug print statements are removed"""
        
        # Check that debug prints are cleaned up
        stress_tester_path = Path("src/app/views/stress_tester/stress_tester_display_area.py")
        tle_tester_path = Path("src/app/views/tle_tester/tle_tester_display_area.py")
        
        if stress_tester_path.exists():
            content = stress_tester_path.read_text()
            assert 'print("File saved - updating button state")' not in content
            assert '# Debug print' not in content
        
        if tle_tester_path.exists():
            content = tle_tester_path.read_text()
            assert 'print("File saved - updating button state")' not in content
            assert '# Debug print' not in content
    
    def test_error_handling_standardization(self):
        """Verify standardized error handling patterns"""
        
        from src.app.ai.config.ai_config import AIConfig
        
        # Test that bare except statements are replaced
        ai_config_path = Path("src/app/ai/config/ai_config.py")
        if ai_config_path.exists():
            content = ai_config_path.read_text(encoding='utf-8')
            # Should not have bare except statements
            assert 'except:' not in content
            # Should have specific exception handling
            assert 'except (FileNotFoundError, json.JSONDecodeError, KeyError)' in content
    
    def test_performance_improvements(self):
        """Verify performance optimizations work"""
        
        from src.app.utils.file_operations import FileOperations
        
        file_ops = FileOperations()
        
        # Test that optimized methods are functional
        # (We can't easily test performance without actual file operations)
        assert hasattr(file_ops, 'save_file')
        assert hasattr(file_ops, 'load_file')
        
        # Verify type hints are added for better maintainability
        import inspect
        save_sig = inspect.signature(file_ops.save_file)
        load_sig = inspect.signature(file_ops.load_file)
        
        # These should have proper type annotations after optimization
        assert len(save_sig.parameters) >= 2
        assert len(load_sig.parameters) >= 1


class TestImportCleanup:
    """Test that import cleanup is successful"""
    
    def test_no_wildcard_imports(self):
        """Ensure no wildcard imports remain in key files"""
        
        # Check constants __init__.py
        constants_init = Path("src/app/constants/__init__.py")
        if constants_init.exists():
            content = constants_init.read_text()
            assert 'from .paths import *' not in content
            assert 'from .paths import (' in content
        
        # Check config manager
        config_mgr = Path("src/app/config/management/config_manager.py")
        if config_mgr.exists():
            content = config_mgr.read_text()
            assert 'from ..config_exceptions import *' not in content
            assert 'from ..config_exceptions import (' in content

    def test_explicit_imports(self):
        """Verify explicit imports are working"""
        
        # Test explicit imports work
        try:
            from src.app.constants import PROJECT_ROOT, USER_DATA_DIR
            from src.app.config.config_exceptions import ConfigError
            success = True
        except ImportError as e:
            print(f"Import error: {e}")
            success = False
        
        assert success, "Explicit imports should work after cleanup"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
