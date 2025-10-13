"""
Phase 8 Task 4 - Phase 2: Tests for gemini_handler.py

Tests cover:
- GeminiConfig initialization
- API key format validation
- API key network validation (with timeout)
- Model management (default, available, validation)
- Configuration persistence (save/load)
- Migration from old format
- GeminiConfigUI helper methods
"""

import pytest
import json
import tempfile
import os
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock, mock_open
from PySide6.QtWidgets import QComboBox

from src.app.core.config.gemini.gemini_handler import GeminiConfig, GeminiConfigUI


# ============================================================================
# Test Fixtures
# ============================================================================

@pytest.fixture
def temp_config_file():
    """Create a temporary config file."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        config_path = f.name
    yield config_path
    # Cleanup
    if os.path.exists(config_path):
        os.unlink(config_path)


@pytest.fixture
def gemini_config(temp_config_file):
    """Create GeminiConfig instance with temp file."""
    return GeminiConfig(temp_config_file)


@pytest.fixture
def sample_config_data():
    """Sample configuration data."""
    return {
        "gemini": {
            "api_key": "AIzaSyTest1234567890abcdefghijk",
            "model": "gemini-2.5-flash",
            "enabled": True
        }
    }


# ============================================================================
# Initialization Tests
# ============================================================================

class TestGeminiConfigInitialization:
    """Test GeminiConfig initialization."""
    
    def test_init_with_custom_path(self):
        """Test initialization with custom config path."""
        config = GeminiConfig("/custom/path/config.json")
        assert config.config_file == "/custom/path/config.json"
    
    def test_init_with_default_path(self):
        """Test initialization uses CONFIG_FILE constant when no path provided."""
        with patch('src.app.core.config.gemini.gemini_handler.CONFIG_FILE', '/default/config.json'):
            config = GeminiConfig()
            assert config.config_file == '/default/config.json'
    
    def test_init_sets_internal_attributes(self):
        """Test initialization sets internal state attributes."""
        config = GeminiConfig()
        assert config._current_api_key is None
        assert config._available_models == []
        assert config._selected_model is None


# ============================================================================
# API Key Format Validation Tests
# ============================================================================

class TestAPIKeyFormatValidation:
    """Test validate_api_key_format method."""
    
    def test_valid_api_key_format(self, gemini_config):
        """Test valid API key passes format validation."""
        valid_key = "AIzaSyTest1234567890abcdefghijk"
        is_valid, message = gemini_config.validate_api_key_format(valid_key)
        
        assert is_valid is True
        assert "valid" in message.lower()
    
    def test_empty_api_key(self, gemini_config):
        """Test empty API key fails validation."""
        is_valid, message = gemini_config.validate_api_key_format("")
        
        assert is_valid is False
        assert "No API key" in message
    
    def test_api_key_too_short(self, gemini_config):
        """Test short API key fails validation."""
        short_key = "AIzaSy123"
        is_valid, message = gemini_config.validate_api_key_format(short_key)
        
        assert is_valid is False
        assert "too short" in message
    
    def test_api_key_too_long(self, gemini_config):
        """Test overly long API key fails validation."""
        long_key = "AIzaSy" + "x" * 100
        is_valid, message = gemini_config.validate_api_key_format(long_key)
        
        assert is_valid is False
        assert "too long" in message
    
    def test_api_key_wrong_prefix(self, gemini_config):
        """Test API key without correct prefix fails."""
        wrong_prefix = "XYZaSyTest1234567890abcdefghijk"
        is_valid, message = gemini_config.validate_api_key_format(wrong_prefix)
        
        assert is_valid is False
        assert "Invalid format" in message
        assert "AIzaSy" in message
    
    def test_api_key_invalid_characters(self, gemini_config):
        """Test API key with special characters fails."""
        # Use longer key with special chars to avoid "too short" error
        invalid_key = "AIzaSyTest@#$%^&*()Test@#$%^&*()"
        is_valid, message = gemini_config.validate_api_key_format(invalid_key)
        
        assert is_valid is False
        assert "invalid" in message.lower()
    
    def test_api_key_with_underscores_dashes(self, gemini_config):
        """Test API key with underscores and dashes is valid."""
        valid_key = "AIzaSyTest_1234-5678_90ab-cdefghijk"
        is_valid, message = gemini_config.validate_api_key_format(valid_key)
        
        assert is_valid is True


# ============================================================================
# API Key Network Validation Tests
# ============================================================================

class TestAPIKeyNetworkValidation:
    """Test validate_api_key_network method."""
    
    def test_network_validation_invalid_format(self, gemini_config):
        """Test network validation fails for invalid format."""
        is_valid, message = gemini_config.validate_api_key_network("short")
        
        assert is_valid is False
        assert "too short" in message
    
    @patch('urllib.request.urlopen')
    def test_network_validation_success(self, mock_urlopen, gemini_config):
        """Test successful network validation."""
        # Mock successful HTTP response
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.__enter__.return_value = mock_response
        mock_response.__exit__.return_value = False
        mock_urlopen.return_value = mock_response
        
        valid_key = "AIzaSyTest1234567890abcdefghijk"
        is_valid, message = gemini_config.validate_api_key_network(valid_key, timeout=5.0)
        
        # Should be valid (either success or timeout which defaults to valid)
        assert is_valid is True
    
    @patch('urllib.request.urlopen')
    def test_network_validation_invalid_key(self, mock_urlopen, gemini_config):
        """Test network validation with 403 error (invalid key)."""
        import urllib.error
        mock_urlopen.side_effect = urllib.error.HTTPError(
            url='test', code=403, msg='Forbidden', hdrs={}, fp=None
        )
        
        valid_format_key = "AIzaSyTest1234567890abcdefghijk"
        is_valid, message = gemini_config.validate_api_key_network(valid_format_key, timeout=5.0)
        
        assert is_valid is False
        assert "Invalid API key" in message
    
    @patch('urllib.request.urlopen')
    def test_network_validation_rate_limit(self, mock_urlopen, gemini_config):
        """Test network validation with 429 error (rate limit but valid key)."""
        import urllib.error
        mock_urlopen.side_effect = urllib.error.HTTPError(
            url='test', code=429, msg='Too Many Requests', hdrs={}, fp=None
        )
        
        valid_format_key = "AIzaSyTest1234567890abcdefghijk"
        is_valid, message = gemini_config.validate_api_key_network(valid_format_key, timeout=5.0)
        
        assert is_valid is True
        assert "Rate limit" in message
    
    @patch('urllib.request.urlopen')
    def test_network_validation_timeout(self, mock_urlopen, gemini_config):
        """Test network validation with timeout."""
        import time
        # Simulate slow response that exceeds timeout
        def slow_response(*args, **kwargs):
            time.sleep(10)  # Longer than timeout
            return MagicMock(status=200)
        
        mock_urlopen.side_effect = slow_response
        
        valid_key = "AIzaSyTest1234567890abcdefghijk"
        is_valid, message = gemini_config.validate_api_key_network(valid_key, timeout=0.5)
        
        # Timeout should result in valid with timeout message
        assert is_valid is True
        assert "timeout" in message.lower()
    
    @patch('urllib.request.urlopen')
    def test_network_validation_exception(self, mock_urlopen, gemini_config):
        """Test network validation with generic exception."""
        mock_urlopen.side_effect = Exception("Network error")
        
        valid_key = "AIzaSyTest1234567890abcdefghijk"
        is_valid, message = gemini_config.validate_api_key_network(valid_key, timeout=5.0)
        
        assert is_valid is False
        assert "error" in message.lower()


# ============================================================================
# Model Management Tests
# ============================================================================

class TestModelManagement:
    """Test model-related methods."""
    
    def test_get_default_model(self, gemini_config):
        """Test get_default_model returns expected model."""
        default_model = gemini_config.get_default_model()
        
        assert default_model == "gemini-2.5-flash"
    
    def test_get_available_models(self, gemini_config):
        """Test get_available_models returns list of Gemini 2.5 models."""
        models = gemini_config.get_available_models()
        
        assert isinstance(models, list)
        assert len(models) > 0
        assert "gemini-2.5-flash" in models
        assert "gemini-2.5-pro" in models
        assert "gemini-2.5-flash-lite" in models
    
    def test_validate_model_selection_valid(self, gemini_config):
        """Test validation of valid model selection."""
        api_key = "AIzaSyTest1234567890abcdefghijk"
        model = "gemini-2.5-flash"
        
        is_valid, message = gemini_config.validate_model_selection(api_key, model)
        
        assert is_valid is True
        assert "valid" in message.lower()
    
    def test_validate_model_selection_custom(self, gemini_config):
        """Test validation accepts custom model names."""
        api_key = "AIzaSyTest1234567890abcdefghijk"
        custom_model = "gemini-custom-model"
        
        is_valid, message = gemini_config.validate_model_selection(api_key, custom_model)
        
        assert is_valid is True
        assert "Custom model" in message
    
    def test_validate_model_selection_empty(self, gemini_config):
        """Test validation fails for empty model."""
        api_key = "AIzaSyTest1234567890abcdefghijk"
        
        is_valid, message = gemini_config.validate_model_selection(api_key, "")
        
        assert is_valid is False
        assert "No model" in message
    
    def test_get_fallback_models(self, gemini_config):
        """Test get_fallback_models returns same as available models."""
        fallback = gemini_config.get_fallback_models()
        available = gemini_config.get_available_models()
        
        assert fallback == available


# ============================================================================
# Save Configuration Tests
# ============================================================================

class TestSaveConfiguration:
    """Test save_config method."""
    
    def test_save_config_success(self, gemini_config, temp_config_file):
        """Test successful configuration save."""
        api_key = "AIzaSyTest1234567890abcdefghijk"
        model = "gemini-2.5-pro"
        
        result = gemini_config.save_config(api_key, model, enabled=True)
        
        assert result is True
        
        # Verify file was created and contains correct data
        with open(temp_config_file, 'r') as f:
            data = json.load(f)
        
        assert "gemini" in data
        assert data["gemini"]["api_key"] == api_key
        assert data["gemini"]["model"] == model
        assert data["gemini"]["enabled"] is True
    
    def test_save_config_uses_default_model(self, gemini_config, temp_config_file):
        """Test save uses default model when none provided."""
        api_key = "AIzaSyTest1234567890abcdefghijk"
        
        result = gemini_config.save_config(api_key, model_name=None)
        
        assert result is True
        
        with open(temp_config_file, 'r') as f:
            data = json.load(f)
        
        assert data["gemini"]["model"] == "gemini-2.5-flash"
    
    def test_save_config_updates_existing(self, gemini_config, temp_config_file):
        """Test save updates existing configuration."""
        # Write initial config
        initial_data = {
            "some_other_setting": "value",
            "gemini": {"api_key": "old_key", "model": "old_model", "enabled": False}
        }
        with open(temp_config_file, 'w') as f:
            json.dump(initial_data, f)
        
        # Update config
        new_key = "AIzaSyNewKey1234567890abcdefghijk"
        result = gemini_config.save_config(new_key, "gemini-2.5-pro", enabled=True)
        
        assert result is True
        
        # Verify update preserved other settings
        with open(temp_config_file, 'r') as f:
            data = json.load(f)
        
        assert data["some_other_setting"] == "value"
        assert data["gemini"]["api_key"] == new_key
    
    def test_save_config_no_config_file(self):
        """Test save works even when config initialized with None (uses CONFIG_FILE)."""
        # When None is passed, it uses CONFIG_FILE constant, so save should succeed
        # but we'll test with invalid path to actually test the error case
        config = GeminiConfig()
        config.config_file = None  # Force None after initialization
        
        result = config.save_config("AIzaSyTest1234567890abcdefghijk")
        
        # With None, open() will fail
        assert result is False
    
    def test_save_config_handles_exception(self, gemini_config):
        """Test save handles write exceptions."""
        # Set invalid path
        gemini_config.config_file = "/invalid/path/that/does/not/exist/config.json"
        
        result = gemini_config.save_config("AIzaSyTest1234567890abcdefghijk")
        
        assert result is False


# ============================================================================
# Load Configuration Tests
# ============================================================================

class TestLoadConfiguration:
    """Test load_config method."""
    
    def test_load_config_success(self, gemini_config, temp_config_file, sample_config_data):
        """Test successful configuration load."""
        # Write config file
        with open(temp_config_file, 'w') as f:
            json.dump(sample_config_data, f)
        
        api_key, model, enabled = gemini_config.load_config()
        
        assert api_key == "AIzaSyTest1234567890abcdefghijk"
        assert model == "gemini-2.5-flash"
        assert enabled is True
    
    def test_load_config_file_not_found(self, gemini_config):
        """Test load returns None values when file doesn't exist."""
        gemini_config.config_file = "/nonexistent/config.json"
        
        api_key, model, enabled = gemini_config.load_config()
        
        assert api_key is None
        assert model is None
        assert enabled is False
    
    def test_load_config_invalid_json(self, gemini_config, temp_config_file):
        """Test load handles invalid JSON gracefully."""
        # Write invalid JSON
        with open(temp_config_file, 'w') as f:
            f.write("{invalid json")
        
        api_key, model, enabled = gemini_config.load_config()
        
        assert api_key is None
        assert model is None
        assert enabled is False
    
    def test_load_config_missing_gemini_section(self, gemini_config, temp_config_file):
        """Test load handles missing gemini section."""
        # Write config without gemini section
        with open(temp_config_file, 'w') as f:
            json.dump({"other_setting": "value"}, f)
        
        api_key, model, enabled = gemini_config.load_config()
        
        assert api_key is None
        assert model is None
        assert enabled is False
    
    def test_load_config_no_config_file(self):
        """Test load returns None when no config file set."""
        config = GeminiConfig()
        config.config_file = None  # Force None after initialization
        
        api_key, model, enabled = config.load_config()
        
        assert api_key is None
        assert model is None
        assert enabled is False


# ============================================================================
# Migration Tests
# ============================================================================

class TestConfigMigration:
    """Test migrate_from_old_format method."""
    
    def test_migrate_success(self, gemini_config, temp_config_file):
        """Test successful migration from old format."""
        # Write old format config
        old_config = {
            "ai_settings": {
                "gemini_api_key": "AIzaSyOldKey1234567890abcdefghijk",
                "preferred_model": "old-model",
                "use_ai_panel": True
            }
        }
        with open(temp_config_file, 'w') as f:
            json.dump(old_config, f)
        
        result = gemini_config.migrate_from_old_format()
        
        assert result is True
        
        # Verify new format
        with open(temp_config_file, 'r') as f:
            data = json.load(f)
        
        assert "gemini" in data
        assert data["gemini"]["api_key"] == "AIzaSyOldKey1234567890abcdefghijk"
        assert data["gemini"]["model"] == "old-model"
        assert data["gemini"]["enabled"] is True
    
    def test_migrate_already_new_format(self, gemini_config, temp_config_file, sample_config_data):
        """Test migration skips if already in new format."""
        # Write new format config
        with open(temp_config_file, 'w') as f:
            json.dump(sample_config_data, f)
        
        result = gemini_config.migrate_from_old_format()
        
        assert result is True  # Already migrated
    
    def test_migrate_no_old_config(self, gemini_config, temp_config_file):
        """Test migration returns False when no old config exists."""
        # Write config without ai_settings
        with open(temp_config_file, 'w') as f:
            json.dump({"other": "data"}, f)
        
        result = gemini_config.migrate_from_old_format()
        
        assert result is False
    
    def test_migrate_missing_api_key(self, gemini_config, temp_config_file):
        """Test migration fails when old config has no API key."""
        old_config = {
            "ai_settings": {
                "preferred_model": "old-model",
                "use_ai_panel": True
            }
        }
        with open(temp_config_file, 'w') as f:
            json.dump(old_config, f)
        
        result = gemini_config.migrate_from_old_format()
        
        assert result is False
    
    def test_migrate_uses_default_model(self, gemini_config, temp_config_file):
        """Test migration uses default model when not specified."""
        old_config = {
            "ai_settings": {
                "gemini_api_key": "AIzaSyOldKey1234567890abcdefghijk",
                "use_ai_panel": True
            }
        }
        with open(temp_config_file, 'w') as f:
            json.dump(old_config, f)
        
        result = gemini_config.migrate_from_old_format()
        
        assert result is True
        
        with open(temp_config_file, 'r') as f:
            data = json.load(f)
        
        assert data["gemini"]["model"] == "gemini-2.5-flash"
    
    def test_migrate_file_not_found(self, gemini_config):
        """Test migration handles missing file."""
        gemini_config.config_file = "/nonexistent/config.json"
        
        result = gemini_config.migrate_from_old_format()
        
        assert result is False


# ============================================================================
# GeminiConfigUI Tests
# ============================================================================

class TestGeminiConfigUI:
    """Test GeminiConfigUI helper methods."""
    
    def test_setup_model_dropdown(self, qtbot):
        """Test setup_model_dropdown configures combo box."""
        combo = QComboBox()
        qtbot.addWidget(combo)
        
        models = ["model1", "model2", "model3"]
        GeminiConfigUI.setup_model_dropdown(combo, models, "model2")
        
        assert combo.count() == 3
        assert combo.currentText() == "model2"
    
    def test_setup_model_dropdown_default_selection(self, qtbot):
        """Test setup selects first item when no model specified."""
        combo = QComboBox()
        qtbot.addWidget(combo)
        
        models = ["default-model", "model2", "model3"]
        GeminiConfigUI.setup_model_dropdown(combo, models)
        
        assert combo.currentText() == "default-model"
    
    def test_setup_model_dropdown_invalid_selection(self, qtbot):
        """Test setup defaults to first when invalid model specified."""
        combo = QComboBox()
        qtbot.addWidget(combo)
        
        models = ["model1", "model2", "model3"]
        GeminiConfigUI.setup_model_dropdown(combo, models, "nonexistent")
        
        assert combo.currentText() == "model1"
    
    def test_get_status_styles(self):
        """Test get_status_styles returns CSS style dictionary."""
        styles = GeminiConfigUI.get_status_styles()
        
        assert isinstance(styles, dict)
        assert 'loading' in styles
        assert 'success' in styles
        assert 'error' in styles
        assert 'neutral' in styles
        
        # Verify they contain CSS
        assert 'color' in styles['success']
        assert 'font-weight' in styles['success']


# ============================================================================
# Integration Tests
# ============================================================================

class TestIntegration:
    """Integration tests for complete workflows."""
    
    def test_full_config_workflow(self, gemini_config, temp_config_file):
        """Test complete save and load workflow."""
        api_key = "AIzaSyTest1234567890abcdefghijk"
        model = "gemini-2.5-pro"
        
        # Validate format
        is_valid, _ = gemini_config.validate_api_key_format(api_key)
        assert is_valid
        
        # Save config
        save_result = gemini_config.save_config(api_key, model, enabled=True)
        assert save_result
        
        # Load config
        loaded_key, loaded_model, loaded_enabled = gemini_config.load_config()
        assert loaded_key == api_key
        assert loaded_model == model
        assert loaded_enabled is True
    
    def test_migration_then_load(self, gemini_config, temp_config_file):
        """Test migration followed by loading."""
        # Create old format
        old_config = {
            "ai_settings": {
                "gemini_api_key": "AIzaSyOldKey1234567890abcdefghijk",
                "preferred_model": "old-model",
                "use_ai_panel": True
            }
        }
        with open(temp_config_file, 'w') as f:
            json.dump(old_config, f)
        
        # Migrate
        migrate_result = gemini_config.migrate_from_old_format()
        assert migrate_result
        
        # Load
        api_key, model, enabled = gemini_config.load_config()
        assert api_key == "AIzaSyOldKey1234567890abcdefghijk"
        assert model == "old-model"
        assert enabled is True
