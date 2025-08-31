"""
Unit tests for ConfigService

Tests the configuration management logic extracted from v1
"""
import pytest
import json
from pathlib import Path
from unittest.mock import patch, mock_open
from infrastructure.configuration.config_service import (
    ConfigService, 
    AISettings, 
    CompilerSettings, 
    AppSettings,
    ConfigResult
)

class TestConfigService:
    """Test configuration service operations"""
    
    def test_get_ai_settings_with_default_config(self, tmp_path):
        """Test AI settings with default configuration"""
        with patch.object(ConfigService, 'CONFIG_DIR', tmp_path):
            service = ConfigService()
            settings = service.get_ai_settings()
            
            assert not settings.enabled
            assert settings.api_key == ""
            assert not settings.use_ai_panel
    
    def test_get_ai_settings_with_custom_config(self, tmp_path):
        """Test AI settings with custom configuration"""
        config_file = tmp_path / 'config.json'
        config_data = {
            'ai_settings': {
                'use_ai_panel': True,
                'gemini_api_key': 'test_api_key_12345678901234567890'
            }
        }
        config_file.write_text(json.dumps(config_data))
        
        with patch.object(ConfigService, 'CONFIG_DIR', tmp_path):
            service = ConfigService()
            settings = service.get_ai_settings()
            
            assert settings.enabled
            assert settings.api_key == 'test_api_key_12345678901234567890'
            assert settings.use_ai_panel
    
    def test_get_compiler_settings_default(self, tmp_path):
        """Test compiler settings with defaults"""
        with patch.object(ConfigService, 'CONFIG_DIR', tmp_path):
            service = ConfigService()
            settings = service.get_compiler_settings()
            
            assert settings.cpp_version == 'c++17'
            assert settings.optimization_level == '-O2'
            assert settings.warnings_enabled is True
    
    def test_get_compiler_settings_custom(self, tmp_path):
        """Test compiler settings with custom values"""
        config_file = tmp_path / 'config.json'
        config_data = {
            'cpp_version': 'c++20',
            'optimization_level': '-O3',
            'warnings_enabled': False
        }
        config_file.write_text(json.dumps(config_data))
        
        with patch.object(ConfigService, 'CONFIG_DIR', tmp_path):
            service = ConfigService()
            settings = service.get_compiler_settings()
            
            assert settings.cpp_version == 'c++20'
            assert settings.optimization_level == '-O3'
            assert settings.warnings_enabled is False
    
    def test_is_ai_ready_disabled(self, tmp_path):
        """Test AI readiness check when disabled"""
        with patch.object(ConfigService, 'CONFIG_DIR', tmp_path):
            service = ConfigService()
            is_ready, message = service.is_ai_ready()
            
            assert not is_ready
            assert "disabled" in message.lower()
    
    def test_is_ai_ready_no_api_key(self, tmp_path):
        """Test AI readiness check with no API key"""
        config_file = tmp_path / 'config.json'
        config_data = {
            'ai_settings': {
                'use_ai_panel': True,
                'gemini_api_key': ''
            }
        }
        config_file.write_text(json.dumps(config_data))
        
        with patch.object(ConfigService, 'CONFIG_DIR', tmp_path):
            service = ConfigService()
            is_ready, message = service.is_ai_ready()
            
            assert not is_ready
            assert "api key" in message.lower()
    
    def test_is_ai_ready_short_api_key(self, tmp_path):
        """Test AI readiness check with invalid API key"""
        config_file = tmp_path / 'config.json'
        config_data = {
            'ai_settings': {
                'use_ai_panel': True,
                'gemini_api_key': 'short'
            }
        }
        config_file.write_text(json.dumps(config_data))
        
        with patch.object(ConfigService, 'CONFIG_DIR', tmp_path):
            service = ConfigService()
            is_ready, message = service.is_ai_ready()
            
            assert not is_ready
            assert "invalid" in message.lower()
    
    def test_is_ai_ready_valid(self, tmp_path):
        """Test AI readiness check with valid configuration"""
        config_file = tmp_path / 'config.json'
        config_data = {
            'ai_settings': {
                'use_ai_panel': True,
                'gemini_api_key': 'valid_api_key_12345678901234567890_long_enough'
            }
        }
        config_file.write_text(json.dumps(config_data))
        
        with patch.object(ConfigService, 'CONFIG_DIR', tmp_path):
            service = ConfigService()
            is_ready, message = service.is_ai_ready()
            
            assert is_ready
            assert "ready" in message.lower()
    
    def test_update_ai_settings(self, tmp_path):
        """Test updating AI settings"""
        with patch.object(ConfigService, 'CONFIG_DIR', tmp_path):
            service = ConfigService()
            
            new_settings = AISettings(
                enabled=True,
                api_key='new_api_key_12345678901234567890',
                use_ai_panel=True
            )
            
            result = service.update_ai_settings(new_settings)
            
            assert result.success
            assert result.error_message is None
            
            # Verify settings were saved
            service.invalidate_cache()
            saved_settings = service.get_ai_settings()
            assert saved_settings.enabled
            assert saved_settings.api_key == 'new_api_key_12345678901234567890'
    
    def test_get_workspace_path_default(self, tmp_path):
        """Test workspace path with default setting"""
        with patch.object(ConfigService, 'CONFIG_DIR', tmp_path):
            service = ConfigService()
            workspace_path = service.get_workspace_path()
            
            assert workspace_path == Path.cwd()
    
    def test_get_workspace_path_custom(self, tmp_path):
        """Test workspace path with custom setting"""
        config_file = tmp_path / 'config.json'
        custom_workspace = str(tmp_path / 'custom_workspace')
        config_data = {
            'workspace_folder': custom_workspace
        }
        config_file.write_text(json.dumps(config_data))
        
        with patch.object(ConfigService, 'CONFIG_DIR', tmp_path):
            service = ConfigService()
            workspace_path = service.get_workspace_path()
            
            assert workspace_path == Path(custom_workspace)
    
    def test_config_caching(self, tmp_path):
        """Test that configuration is cached properly"""
        config_file = tmp_path / 'config.json'
        config_data = {'test_value': 'cached'}
        config_file.write_text(json.dumps(config_data))
        
        with patch.object(ConfigService, 'CONFIG_DIR', tmp_path):
            service = ConfigService()
            
            # Load config twice
            config1 = service._load_config()
            config2 = service._load_config()
            
            # Should return same cached instance
            assert config1 is config2
            assert config1['test_value'] == 'cached'
    
    def test_cache_invalidation(self, tmp_path):
        """Test cache invalidation"""
        config_file = tmp_path / 'config.json'
        config_data = {'test_value': 'original'}
        config_file.write_text(json.dumps(config_data))
        
        with patch.object(ConfigService, 'CONFIG_DIR', tmp_path):
            service = ConfigService()
            
            # Load config
            config1 = service._load_config()
            assert config1['test_value'] == 'original'
            
            # Invalidate cache
            service.invalidate_cache()
            
            # Update file
            config_data['test_value'] = 'updated'
            config_file.write_text(json.dumps(config_data))
            
            # Load again should read from file
            config2 = service._load_config()
            assert config2['test_value'] == 'updated'
