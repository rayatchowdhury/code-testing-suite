"""
Integration tests for configuration persistence

Tests the full configuration roundtrip functionality
"""
import pytest
from pathlib import Path
from infrastructure.configuration.config_service import ConfigService, AISettings

@pytest.mark.integration
class TestConfigPersistence:
    """Test configuration persistence integration"""
    
    def test_config_roundtrip(self, tmp_path):
        """Test configuration save and load roundtrip"""
        # Override config directory for test
        with pytest.MonkeyPatch().context() as m:
            m.setattr(ConfigService, 'CONFIG_DIR', tmp_path)
            
            service = ConfigService()
            
            # Update AI settings
            ai_settings = AISettings(
                enabled=True,
                api_key='test_key_12345678901234567890',
                use_ai_panel=True
            )
            
            result = service.update_ai_settings(ai_settings)
            assert result.success
            
            # Create new service instance (simulating app restart)
            service2 = ConfigService()
            
            # Verify settings persisted
            loaded_settings = service2.get_ai_settings()
            assert loaded_settings.enabled
            assert loaded_settings.api_key == 'test_key_12345678901234567890'
            assert loaded_settings.use_ai_panel
    
    def test_workspace_path_persistence(self, tmp_path):
        """Test workspace path persistence"""
        with pytest.MonkeyPatch().context() as m:
            m.setattr(ConfigService, 'CONFIG_DIR', tmp_path)
            
            service = ConfigService()
            test_workspace = tmp_path / 'test_workspace'
            
            # Update workspace path
            result = service.update_workspace_path(test_workspace)
            assert result.success
            
            # Verify persistence
            service2 = ConfigService()
            loaded_path = service2.get_workspace_path()
            assert loaded_path == test_workspace
