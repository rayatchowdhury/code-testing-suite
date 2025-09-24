"""Unit tests for ConfigManager and related configuration components."""

import json
import os
import tempfile
import pytest
from pathlib import Path
from unittest.mock import patch, mock_open, MagicMock

from src.app.core.config.core.config_handler import ConfigManager, ConfigPersistence
from src.app.core.config.core.exceptions import (
    ConfigError, ConfigPermissionError, ConfigFormatError, 
    ConfigValidationError, ConfigLoadError, ConfigSaveError, ConfigMissingError
)


class TestConfigManager:
    """Test cases for ConfigManager class."""

    @pytest.fixture
    def config_manager(self, temp_config_dir):
        """Create ConfigManager with temporary directory."""
        config_file = os.path.join(temp_config_dir, 'test_config.json')
        return ConfigManager(config_file)

    def test_init_with_custom_config_file(self, temp_config_dir):
        """Test ConfigManager initialization with custom config file."""
        custom_config = os.path.join(temp_config_dir, 'custom.json')
        manager = ConfigManager(custom_config)
        assert manager.config_file == custom_config

    def test_get_default_config(self, config_manager):
        """Test default configuration structure."""
        config = config_manager.get_default_config()
        
        # Verify required keys exist
        assert 'cpp_version' in config
        assert 'workspace_folder' in config
        assert 'gemini' in config
        assert 'editor_settings' in config
        
        # Verify data types
        assert isinstance(config['cpp_version'], str)
        assert isinstance(config['workspace_folder'], str)
        assert isinstance(config['gemini'], dict)
        assert isinstance(config['editor_settings'], dict)
        
        # Verify Gemini settings
        gemini = config['gemini']
        assert 'enabled' in gemini
        assert 'api_key' in gemini
        assert 'model' in gemini
        assert isinstance(gemini['enabled'], bool)
        
        # Verify editor settings
        editor = config['editor_settings']
        assert 'autosave' in editor
        assert 'tab_width' in editor
        assert 'font_size' in editor
        assert isinstance(editor['autosave'], bool)
        assert isinstance(editor['tab_width'], int)

    def test_load_config_file_not_exists(self, config_manager):
        """Test loading config when file doesn't exist returns default."""
        config = config_manager.load_config()
        expected = config_manager.get_default_config()
        assert config == expected

    def test_load_config_valid_file(self, config_manager, sample_config):
        """Test loading valid configuration file."""
        # Write test config to file
        with open(config_manager.config_file, 'w') as f:
            json.dump(sample_config, f)
        
        config = config_manager.load_config()
        assert config == sample_config

    def test_load_config_invalid_json(self, config_manager):
        """Test loading configuration with invalid JSON format."""
        # Write invalid JSON
        with open(config_manager.config_file, 'w') as f:
            f.write('{ invalid json }')
        
        with pytest.raises(ConfigFormatError) as exc_info:
            config_manager.load_config()
        
        assert "Config format error" in str(exc_info.value)

    def test_load_config_permission_error(self, config_manager):
        """Test loading config with permission denied."""
        # Create file and remove read permission
        Path(config_manager.config_file).touch()
        
        with patch('os.access', return_value=False):
            with pytest.raises(ConfigPermissionError) as exc_info:
                config_manager.load_config()
            
            assert "Permission denied reading" in str(exc_info.value)

    def test_validate_config_structure_valid(self, config_manager, sample_config):
        """Test configuration structure validation with valid config."""
        errors = config_manager._validate_config_structure(sample_config)
        assert errors == []

    def test_validate_config_structure_missing_keys(self, config_manager):
        """Test validation with missing required keys."""
        incomplete_config = {'cpp_version': 'c++17'}
        
        with pytest.raises(ConfigMissingError) as exc_info:
            config_manager._validate_config_structure(incomplete_config)
        
        assert "Required keys" in str(exc_info.value)

    def test_validate_config_structure_invalid_types(self, config_manager, invalid_config):
        """Test validation with invalid data types."""
        errors = config_manager._validate_config_structure(invalid_config)
        
        # Should have multiple validation errors
        assert len(errors) > 0
        assert any("Invalid type for" in error for error in errors)

    def test_save_config_success(self, config_manager, sample_config):
        """Test successful configuration saving."""
        config_manager.save_config(sample_config)
        
        # Verify file was created and contains correct data
        assert os.path.exists(config_manager.config_file)
        
        with open(config_manager.config_file, 'r') as f:
            saved_config = json.load(f)
        
        assert saved_config == sample_config

    def test_save_config_creates_directory(self, temp_config_dir, sample_config):
        """Test that save_config creates directory if it doesn't exist."""
        nested_config_file = os.path.join(temp_config_dir, 'nested', 'config.json')
        manager = ConfigManager(nested_config_file)
        
        manager.save_config(sample_config)
        
        # The config file should exist
        assert os.path.exists(nested_config_file)
        # The parent directory should have been created
        assert os.path.exists(os.path.dirname(nested_config_file))

    def test_save_config_creates_backup(self, config_manager, sample_config):
        """Test that save_config creates backup of existing file."""
        # Create initial config
        config_manager.save_config(sample_config)
        
        # Modify and save again
        modified_config = sample_config.copy()
        modified_config['cpp_version'] = 'c++20'
        config_manager.save_config(modified_config)
        
        # Check backup exists
        backup_file = f"{config_manager.config_file}.bak"
        assert os.path.exists(backup_file)
        
        # Verify backup contains original config
        with open(backup_file, 'r') as f:
            backup_config = json.load(f)
        
        assert backup_config == sample_config

    @patch('builtins.open', side_effect=PermissionError("Access denied"))
    def test_save_config_permission_error(self, mock_open_func, config_manager, sample_config):
        """Test save_config with permission error."""
        with pytest.raises(ConfigSaveError) as exc_info:
            config_manager.save_config(sample_config)
        
        assert "Failed to save config" in str(exc_info.value)


class TestConfigPersistence:
    """Test cases for ConfigPersistence class."""

    @pytest.fixture
    def mock_dialog(self):
        """Create mock dialog with required UI components."""
        dialog = MagicMock()
        dialog.cpp_version_combo = MagicMock()
        dialog.workspace_input = MagicMock()
        dialog.key_input = MagicMock()
        dialog.status_label = MagicMock()
        dialog.use_ai_checkbox = MagicMock()
        dialog.is_key_valid = False
        dialog.show_error = MagicMock()
        return dialog

    @pytest.fixture
    def config_persistence(self, mock_dialog, temp_config_dir):
        """Create ConfigPersistence with mock dialog and temporary config."""
        config_file = os.path.join(temp_config_dir, 'test_config.json')
        config_manager = ConfigManager(config_file)
        return ConfigPersistence(mock_dialog, config_manager)

    def test_load_config_success(self, config_persistence, sample_config):
        """Test successful configuration loading into UI."""
        # Save sample config first
        config_persistence.config_manager.save_config(sample_config)
        
        # Load config into UI
        config_persistence.load_config()
        
        # Verify UI components were populated
        config_persistence.parent.cpp_version_combo.setCurrentText.assert_called_with(sample_config['cpp_version'])
        config_persistence.parent.workspace_input.setText.assert_called_with(sample_config['workspace_folder'])
        config_persistence.parent.key_input.setText.assert_called_with(sample_config['gemini']['api_key'])

    def test_load_config_missing_file(self, config_persistence):
        """Test loading config when file doesn't exist."""
        # Load config (should use defaults)
        config_persistence.load_config()
        
        # Verify default values were set (actual default is 'c++17', not 'auto')
        config_persistence.parent.cpp_version_combo.setCurrentText.assert_called_with("c++17")
        config_persistence.parent.workspace_input.setText.assert_called_with("")

    def test_load_config_with_corrupted_file(self, config_persistence):
        """Test loading config with corrupted file."""
        # Create corrupted config file
        with open(config_persistence.config_manager.config_file, 'w') as f:
            f.write('{ invalid json }')
        
        # Load config should handle error gracefully
        config_persistence.load_config()
        
        # Should fall back to defaults (actual default is 'c++17', not 'auto')
        config_persistence.parent.cpp_version_combo.setCurrentText.assert_called_with("c++17")

    def test_load_config_handles_config_errors(self, config_persistence):
        """Test that load_config handles ConfigError exceptions."""
        # Mock config_manager to raise ConfigError
        config_persistence.config_manager.load_config = MagicMock(
            side_effect=ConfigValidationError("test", "test error")
        )
        config_persistence.config_manager.get_default_config = MagicMock(return_value={})
        config_persistence.config_manager.save_config = MagicMock()
        
        # Should not raise exception
        config_persistence.load_config()
        
        # Should attempt to reset to defaults
        config_persistence.config_manager.save_config.assert_called_once()


class TestConfigExceptions:
    """Test cases for configuration exception classes."""

    def test_config_permission_error(self):
        """Test ConfigPermissionError creation and attributes."""
        error = ConfigPermissionError("reading", "/path/to/config.json")
        
        assert error.operation == "reading"
        assert error.file_path == "/path/to/config.json"
        assert "Permission denied reading" in str(error)

    def test_config_format_error_with_line_number(self):
        """Test ConfigFormatError with line number."""
        error = ConfigFormatError("Invalid syntax", 42)
        
        assert error.line_number == 42
        assert "line 42" in str(error)
        assert "Invalid syntax" in str(error)

    def test_config_format_error_without_line_number(self):
        """Test ConfigFormatError without line number."""
        error = ConfigFormatError("Invalid syntax")
        
        assert error.line_number is None
        assert "Config format error: Invalid syntax" in str(error)

    def test_config_validation_error(self):
        """Test ConfigValidationError creation."""
        error = ConfigValidationError("gemini.api_key", "Missing API key", "Details here")
        
        assert error.field == "gemini.api_key"
        assert error.details == "Details here"
        assert "gemini.api_key" in str(error)
        assert "Missing API key" in str(error)

    def test_config_load_error(self):
        """Test ConfigLoadError creation."""
        error = ConfigLoadError("File not found")
        
        assert "Failed to load config: File not found" in str(error)

    def test_config_save_error(self):
        """Test ConfigSaveError creation."""
        error = ConfigSaveError("Permission denied")
        
        assert "Failed to save config: Permission denied" in str(error)

    def test_config_missing_error(self):
        """Test ConfigMissingError creation."""
        error = ConfigMissingError("Required keys: api_key, model")
        
        assert "Required keys: api_key, model" in str(error)