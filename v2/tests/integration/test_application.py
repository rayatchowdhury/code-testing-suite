"""
Integration tests for Application class

Tests the full application initialization and service wiring
"""
import pytest
from unittest.mock import patch, Mock
from app.application import Application, create_application
from app.dependency_injection import get_container

@pytest.mark.integration
class TestApplication:
    """Test application initialization and integration"""
    
    def setup_method(self):
        """Setup for each test"""
        # Clear container before each test
        get_container().clear()
    
    def test_application_initialization(self):
        """Test basic application initialization"""
        app = Application()
        
        # Should not be initialized yet
        assert app._config_service is None
        assert app._file_service is None
        
        # Initialize
        app.initialize()
        
        # Should have services now
        assert app._config_service is not None
        assert app._file_service is not None
    
    def test_create_application_factory(self):
        """Test application factory method"""
        app = create_application()
        
        assert isinstance(app, Application)
        assert app._config_service is not None
        assert app._file_service is not None
    
    def test_console_mode_success(self):
        """Test console mode execution"""
        app = create_application()
        
        # Should run successfully
        result = app.run_console_mode()
        assert result is True
    
    def test_application_shutdown(self):
        """Test application shutdown"""
        app = create_application()
        container = get_container()
        
        # Container should have services
        assert len(container._singletons) > 0
        
        # Shutdown should clear container
        app.shutdown()
        assert len(container._singletons) == 0
    
    @pytest.mark.asyncio
    async def test_gui_mode_placeholder(self):
        """Test GUI mode placeholder"""
        app = create_application()
        
        # Should not crash (just a placeholder for now)
        await app.run_gui_mode()
    
    def test_error_handling_in_console_mode(self):
        """Test error handling in console mode"""
        app = Application()
        app.initialize()
        
        # Mock config service to raise error
        app._config_service = Mock()
        app._config_service.get_ai_settings.side_effect = Exception("Test error")
        
        result = app.run_console_mode()
        assert result is False
