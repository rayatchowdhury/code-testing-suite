"""
Unit tests for ConfigurationViewAdapter

Tests the Qt adapter for configuration view (mock-based without actual Qt)
"""
import pytest
from unittest.mock import Mock, patch
from infrastructure.configuration.config_service import ConfigService, AISettings
from infrastructure.theming.theme_service import ThemeService

# Mock Qt classes for testing
class MockQDialog:
    def __init__(self, parent=None):
        self.parent = parent
        self.accepted = False
    
    def setWindowTitle(self, title): pass
    def setFixedSize(self, w, h): pass
    def setWindowFlags(self, flags): pass
    def setStyleSheet(self, style): pass
    def exec(self): return 1
    def accept(self): self.accepted = True
    def reject(self): pass

class TestConfigurationViewAdapter:
    """Test configuration view adapter without Qt dependencies"""
    
    def test_adapter_initialization(self):
        """Test adapter initialization with services"""
        config_service = Mock(spec=ConfigService)
        theme_service = Mock(spec=ThemeService)
        
        # Import with mocked Qt
        with patch('presentation.adapters.config_view_adapter.HAS_QT', True):
            with patch('presentation.adapters.config_view_adapter.QDialog', MockQDialog):
                from presentation.adapters.config_view_adapter import ConfigurationViewAdapter
                
                adapter = ConfigurationViewAdapter(config_service, theme_service)
                
                assert adapter.config_service is config_service
                assert adapter.theme_service is theme_service
                assert adapter._dialog is None
    
    def test_adapter_without_qt_raises_error(self):
        """Test adapter raises error when Qt is not available"""
        config_service = Mock(spec=ConfigService)
        theme_service = Mock(spec=ThemeService)
        
        with patch('presentation.adapters.config_view_adapter.HAS_QT', False):
            from presentation.adapters.config_view_adapter import ConfigurationViewAdapter
            
            with pytest.raises(RuntimeError, match="Qt is required"):
                ConfigurationViewAdapter(config_service, theme_service)
    
    def test_dialog_creation(self):
        """Test dialog creation and setup"""
        config_service = Mock(spec=ConfigService)
        config_service.get_ai_settings.return_value = AISettings()
        config_service.get_compiler_settings.return_value = Mock(cpp_version="c++17")
        config_service.get_app_settings.return_value = Mock(workspace_folder="", auto_save=True)
        
        theme_service = Mock(spec=ThemeService)
        theme_service.get_dialog_style.return_value = "test-style"
        theme_service.get_color.return_value = "#0096C7"
        
        with patch('presentation.adapters.config_view_adapter.HAS_QT', True):
            with patch('presentation.adapters.config_view_adapter.QDialog', MockQDialog):
                with patch('presentation.adapters.config_view_adapter.QVBoxLayout'):
                    with patch('presentation.adapters.config_view_adapter.QLabel'):
                        from presentation.adapters.config_view_adapter import ConfigurationViewAdapter
                        
                        adapter = ConfigurationViewAdapter(config_service, theme_service)
                        dialog = adapter.create_dialog()
                        
                        assert isinstance(dialog, MockQDialog)
                        assert adapter._dialog is dialog
                        
                        # Should load config on creation
                        config_service.get_ai_settings.assert_called_once()
                        config_service.get_compiler_settings.assert_called_once()
                        config_service.get_app_settings.assert_called_once()
    
    @patch('presentation.adapters.config_view_adapter.HAS_QT', True)
    def test_service_delegation(self):
        """Test that business logic is delegated to services"""
        config_service = Mock(spec=ConfigService)
        theme_service = Mock(spec=ThemeService)
        
        # Mock theme service responses
        theme_service.get_dialog_style.return_value = "dialog-style"
        theme_service.get_button_style.return_value = "button-style"
        theme_service.get_section_style.return_value = "section-style"
        theme_service.get_color.return_value = "#0096C7"
        
        # Mock config service responses
        config_service.get_ai_settings.return_value = AISettings(enabled=True, api_key="test")
        config_service.get_compiler_settings.return_value = Mock(cpp_version="c++20")
        config_service.get_app_settings.return_value = Mock(workspace_folder="/test", auto_save=False)
        
        with patch('presentation.adapters.config_view_adapter.QDialog', MockQDialog):
            with patch('presentation.adapters.config_view_adapter.QVBoxLayout'):
                with patch('presentation.adapters.config_view_adapter.QLabel'):
                    from presentation.adapters.config_view_adapter import ConfigurationViewAdapter
                    
                    adapter = ConfigurationViewAdapter(config_service, theme_service)
                    dialog = adapter.create_dialog()
                    
                    # Verify theme service was used for styling
                    theme_service.get_dialog_style.assert_called()
                    theme_service.get_button_style.assert_called()
                    theme_service.get_section_style.assert_called()
                    
                    # Verify config service was used for data
                    config_service.get_ai_settings.assert_called()
                    config_service.get_compiler_settings.assert_called()
                    config_service.get_app_settings.assert_called()
    
    def test_import_without_qt_defines_mocks(self):
        """Test that module can be imported without Qt"""
        with patch('presentation.adapters.config_view_adapter.HAS_QT', False):
            # Should not raise ImportError
            from presentation.adapters.config_view_adapter import ConfigurationViewAdapter
            
            # Class should exist but not be functional
            assert ConfigurationViewAdapter is not None
