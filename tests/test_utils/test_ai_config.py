"""
Tests for the AI configuration module.

This module tests AI configuration loading, validation,
and status checking functionality.
"""

import pytest
import json
import os
from unittest.mock import patch, mock_open, MagicMock

from utils.ai_config import AIConfig


class TestAIConfig:
    """Test AIConfig class functionality."""
    
    @pytest.mark.unit
    def test_is_ai_enabled_with_valid_config(self, mock_user_data_dir):
        """Test is_ai_enabled returns True when AI panel is enabled."""
        config_data = {
            "ai_settings": {
                "use_ai_panel": True
            }
        }
        config_content = json.dumps(config_data)
        
        with patch("builtins.open", mock_open(read_data=config_content)):
            with patch("os.path.exists", return_value=True):
                assert AIConfig.is_ai_enabled() == True
    
    @pytest.mark.unit
    def test_is_ai_enabled_with_disabled_config(self, mock_user_data_dir):
        """Test is_ai_enabled returns False when AI panel is disabled."""
        config_data = {
            "ai_settings": {
                "use_ai_panel": False
            }
        }
        config_content = json.dumps(config_data)
        
        with patch("builtins.open", mock_open(read_data=config_content)):
            with patch("os.path.exists", return_value=True):
                assert AIConfig.is_ai_enabled() == False
    
    @pytest.mark.unit
    def test_is_ai_enabled_with_missing_config(self):
        """Test is_ai_enabled returns False when config file doesn't exist."""
        with patch("os.path.exists", return_value=False):
            assert AIConfig.is_ai_enabled() == False
    
    @pytest.mark.unit
    def test_is_ai_enabled_with_invalid_json(self):
        """Test is_ai_enabled returns False when config has invalid JSON."""
        with patch("builtins.open", mock_open(read_data="invalid json")):
            with patch("os.path.exists", return_value=True):
                assert AIConfig.is_ai_enabled() == False
    
    @pytest.mark.unit
    def test_get_api_key_returns_key_when_present(self, mock_user_data_dir):
        """Test get_api_key returns API key when present in config."""
        config_data = {
            "ai_settings": {
                "gemini_api_key": "test_api_key_12345678901234567890"
            }
        }
        config_content = json.dumps(config_data)
        
        with patch("builtins.open", mock_open(read_data=config_content)):
            with patch("os.path.exists", return_value=True):
                result = AIConfig.get_api_key()
                assert result == "test_api_key_12345678901234567890"
    
    @pytest.mark.unit
    def test_get_api_key_returns_none_when_missing(self, mock_user_data_dir):
        """Test get_api_key returns None when API key is missing."""
        config_data = {
            "ai_settings": {}
        }
        config_content = json.dumps(config_data)
        
        with patch("builtins.open", mock_open(read_data=config_content)):
            with patch("os.path.exists", return_value=True):
                assert AIConfig.get_api_key() is None
    
    @pytest.mark.unit
    def test_get_api_key_returns_none_when_empty(self, mock_user_data_dir):
        """Test get_api_key returns None when API key is empty string."""
        config_data = {
            "ai_settings": {
                "gemini_api_key": ""
            }
        }
        config_content = json.dumps(config_data)
        
        with patch("builtins.open", mock_open(read_data=config_content)):
            with patch("os.path.exists", return_value=True):
                assert AIConfig.get_api_key() is None
    
    @pytest.mark.unit
    @pytest.mark.parametrize("key,expected_ready", [
        ("short", False),  # Too short
        ("a" * 35, True),  # Long enough
        ("", False),       # Empty
    ])
    def test_is_ai_ready_validates_key_length(self, key, expected_ready, mock_user_data_dir):
        """Test is_ai_ready validates API key length."""
        config_data = {
            "ai_settings": {
                "use_ai_panel": True,
                "gemini_api_key": key
            }
        }
        config_content = json.dumps(config_data)
        
        with patch("builtins.open", mock_open(read_data=config_content)):
            with patch("os.path.exists", return_value=True):
                is_ready, message = AIConfig.is_ai_ready()
                assert is_ready == expected_ready
                assert isinstance(message, str)
    
    @pytest.mark.unit
    def test_is_ai_ready_when_ai_disabled(self):
        """Test is_ai_ready returns False when AI is disabled."""
        with patch.object(AIConfig, 'is_ai_enabled', return_value=False):
            is_ready, message = AIConfig.is_ai_ready()
            assert is_ready == False
            assert "disabled" in message.lower()
    
    @pytest.mark.unit
    def test_should_show_ai_panel_delegates_to_is_ai_enabled(self):
        """Test should_show_ai_panel returns same as is_ai_enabled."""
        with patch.object(AIConfig, 'is_ai_enabled', return_value=True):
            assert AIConfig.should_show_ai_panel() == True
        
        with patch.object(AIConfig, 'is_ai_enabled', return_value=False):
            assert AIConfig.should_show_ai_panel() == False
    
    @pytest.mark.unit
    def test_get_ai_status_message_shows_ready_when_configured(self):
        """Test get_ai_status_message shows ready status when properly configured."""
        with patch.object(AIConfig, 'is_ai_ready', return_value=(True, "AI is ready")):
            message = AIConfig.get_ai_status_message()
            assert "Ready" in message
            assert "🤖" in message
    
    @pytest.mark.unit
    def test_get_ai_status_message_shows_warning_when_enabled_but_not_ready(self):
        """Test get_ai_status_message shows warning when enabled but not ready."""
        with patch.object(AIConfig, 'is_ai_ready', return_value=(False, "No API key")):
            with patch.object(AIConfig, 'is_ai_enabled', return_value=True):
                message = AIConfig.get_ai_status_message()
                assert "⚠️" in message
                assert "No API key" in message
    
    @pytest.mark.unit
    def test_get_ai_status_message_shows_disabled_when_off(self):
        """Test get_ai_status_message shows disabled status when AI is off."""
        with patch.object(AIConfig, 'is_ai_enabled', return_value=False):
            message = AIConfig.get_ai_status_message()
            assert "Disabled" in message
            assert "🔒" in message


class TestAIConfigIntegration:
    """Integration tests for AIConfig with real file operations."""
    
    @pytest.mark.integration
    def test_load_config_with_real_file(self, temp_dir, mock_config_file):
        """Test _load_config with actual file operations."""
        with patch.object(AIConfig, 'CONFIG_FILE', mock_config_file):
            config = AIConfig._load_config()
            assert isinstance(config, dict)
            assert 'ai_settings' in config
    
    @pytest.mark.integration
    def test_full_workflow_with_temp_config(self, temp_dir, mock_config_file):
        """Test complete AI config workflow with temporary config file."""
        with patch.object(AIConfig, 'CONFIG_FILE', mock_config_file):
            # Test that AI is enabled
            assert AIConfig.is_ai_enabled() == True
            
            # Test that API key is retrieved
            api_key = AIConfig.get_api_key()
            assert api_key is not None
            assert len(api_key) > 30
            
            # Test that AI is ready
            is_ready, message = AIConfig.is_ai_ready()
            assert is_ready == True
            assert "ready" in message.lower()
