"""
Unit tests for core/config/core/config_handler.py module.

Tests the ConfigManager class for configuration management.

Test Coverage:
- ConfigManager initialization
- load_config: Loading from file with validation
- save_config: Saving with backup creation
- _validate_config_structure: Structure validation
- get_default_config: Default configuration generation
- Error handling for all exception types
- Multi-language configuration support
- Backup file creation
"""

import json
import os
from unittest.mock import MagicMock, mock_open, patch

import pytest

from src.app.core.config.core.config_handler import ConfigManager
from src.app.core.config.core.exceptions import (
    ConfigError,
    ConfigFormatError,
    ConfigLoadError,
    ConfigMissingError,
    ConfigPermissionError,
    ConfigSaveError,
    ConfigValidationError,
)


@pytest.fixture
def config_manager(temp_dir):
    """Create ConfigManager with temporary config file."""
    config_file = os.path.join(temp_dir, "config.json")
    return ConfigManager(config_file)


@pytest.fixture
def valid_config():
    """Return a valid configuration dictionary."""
    return {
        "cpp_version": "c++17",
        "languages": {
            "cpp": {
                "compiler": "g++",
                "std_version": "c++17",
                "optimization": "O2",
                "flags": ["-Wall", "-O2"],
            },
            "py": {"interpreter": "python", "version": "3", "flags": ["-u"]},
            "java": {
                "compiler": "javac",
                "version": "11",
                "flags": [],
                "runtime": "java",
            },
        },
        "gemini": {"enabled": False, "api_key": "", "model": "gemini-2.5-flash"},
        "editor_settings": {
            "autosave": True,
            "autosave_interval": 5,
            "tab_width": 4,
            "font_size": 12,
            "bracket_matching": True,
        },
    }


class TestConfigManagerInitialization:
    """Tests for ConfigManager initialization."""

    def test_creates_with_absolute_path(self, temp_dir):
        """Test ConfigManager with absolute config file path."""
        config_file = os.path.join(temp_dir, "config.json")
        manager = ConfigManager(config_file)
        assert manager.config_file == config_file

    def test_creates_with_relative_filename(self, temp_dir):
        """Test ConfigManager with relative filename (uses CONFIG_DIR)."""
        # Temporarily override CONFIG_DIR
        original_dir = ConfigManager.CONFIG_DIR
        try:
            ConfigManager.CONFIG_DIR = temp_dir
            manager = ConfigManager("config.json")
            expected_path = os.path.join(temp_dir, "config.json")
            assert manager.config_file == expected_path
        finally:
            ConfigManager.CONFIG_DIR = original_dir

    def test_has_config_dir_attribute(self):
        """Test that ConfigManager has CONFIG_DIR class attribute."""
        assert hasattr(ConfigManager, "CONFIG_DIR")
        assert isinstance(ConfigManager.CONFIG_DIR, str)


class TestLoadConfig:
    """Tests for load_config method."""

    def test_loads_valid_config(self, config_manager, valid_config):
        """Test loading valid configuration from file."""
        # Write valid config to file
        with open(config_manager.config_file, "w") as f:
            json.dump(valid_config, f)

        # Load and verify
        loaded = config_manager.load_config()
        assert loaded == valid_config

    def test_returns_default_config_when_file_missing(self, config_manager):
        """Test that default config is returned when file doesn't exist."""
        # Ensure file doesn't exist
        if os.path.exists(config_manager.config_file):
            os.remove(config_manager.config_file)

        loaded = config_manager.load_config()
        default = config_manager.get_default_config()
        assert loaded == default

    def test_raises_permission_error_for_unreadable_file(self, config_manager, valid_config):
        """Test ConfigPermissionError for unreadable file."""
        # Write config file
        with open(config_manager.config_file, "w") as f:
            json.dump(valid_config, f)

        # Mock os.access to simulate permission denied
        with patch("os.access", return_value=False):
            with pytest.raises(ConfigPermissionError) as exc_info:
                config_manager.load_config()

            assert exc_info.value.operation == "reading"
            assert config_manager.config_file in exc_info.value.file_path

    def test_raises_format_error_for_invalid_json(self, config_manager):
        """Test ConfigFormatError for invalid JSON."""
        # Write invalid JSON
        with open(config_manager.config_file, "w") as f:
            f.write("{invalid json content")

        with pytest.raises(ConfigFormatError) as exc_info:
            config_manager.load_config()

        assert exc_info.value.line_number is not None

    def test_raises_validation_error_for_invalid_structure(self, config_manager):
        """Test ConfigMissingError for missing required keys."""
        # Write config missing required keys
        invalid_config = {"cpp_version": "c++17"}  # Missing gemini, editor_settings
        with open(config_manager.config_file, "w") as f:
            json.dump(invalid_config, f)

        # Should raise ConfigMissingError (not ConfigValidationError)
        with pytest.raises(ConfigMissingError):
            config_manager.load_config()

    def test_handles_missing_languages_key(self, config_manager):
        """Test that missing 'languages' key doesn't cause error."""
        # Config without languages key (should be auto-populated)
        config_without_languages = {
            "cpp_version": "c++17",
            "gemini": {"enabled": False, "api_key": "", "model": "gemini-2.5-flash"},
            "editor_settings": {
                "autosave": True,
                "autosave_interval": 5,
                "tab_width": 4,
                "font_size": 12,
                "bracket_matching": True,
            },
        }
        with open(config_manager.config_file, "w") as f:
            json.dump(config_without_languages, f)

        # Should load successfully (languages is optional)
        loaded = config_manager.load_config()
        assert loaded is not None


class TestSaveConfig:
    """Tests for save_config method."""

    def test_saves_config_to_file(self, config_manager, valid_config):
        """Test saving configuration to file."""
        config_manager.save_config(valid_config)

        # Verify file exists and contains correct data
        assert os.path.exists(config_manager.config_file)
        with open(config_manager.config_file, "r") as f:
            saved = json.load(f)
        assert saved == valid_config

    def test_creates_directory_if_missing(self, temp_dir):
        """Test that save_config creates directory structure."""
        nested_dir = os.path.join(temp_dir, "nested", "path")
        config_file = os.path.join(nested_dir, "config.json")
        manager = ConfigManager(config_file)

        config = {"test": "data"}
        manager.save_config(config)

        # Verify directory and file exist
        assert os.path.exists(nested_dir)
        assert os.path.exists(config_file)

    def test_creates_backup_of_existing_config(self, config_manager, valid_config):
        """Test that existing config is backed up before saving."""
        # Save initial config
        initial_config = {"version": 1}
        with open(config_manager.config_file, "w") as f:
            json.dump(initial_config, f)

        # Save new config (should create backup)
        config_manager.save_config(valid_config)

        # Verify backup exists
        backup_file = f"{config_manager.config_file}.bak"
        assert os.path.exists(backup_file)

        # Verify backup contains initial config
        with open(backup_file, "r") as f:
            backup = json.load(f)
        assert backup == initial_config

    def test_ignores_backup_failure(self, config_manager, valid_config):
        """Test that save succeeds even if backup fails."""
        # Create initial config
        with open(config_manager.config_file, "w") as f:
            json.dump({"old": "config"}, f)

        # Mock shutil.copy2 to raise exception
        with patch("shutil.copy2", side_effect=Exception("Backup failed")):
            # Should not raise exception
            config_manager.save_config(valid_config)

        # Verify new config was saved
        with open(config_manager.config_file, "r") as f:
            saved = json.load(f)
        assert saved == valid_config

    def test_raises_save_error_on_failure(self, config_manager, valid_config):
        """Test ConfigSaveError when save fails."""
        # Mock open to raise exception
        with patch("builtins.open", side_effect=PermissionError("Cannot write")):
            with pytest.raises(ConfigSaveError):
                config_manager.save_config(valid_config)

    def test_saves_with_proper_formatting(self, config_manager, valid_config):
        """Test that JSON is saved with indentation."""
        config_manager.save_config(valid_config)

        # Read file and verify it's formatted
        with open(config_manager.config_file, "r") as f:
            content = f.read()

        # Should have indentation (newlines indicate formatting)
        assert "\n" in content
        assert "    " in content  # 4-space indent


class TestValidateConfigStructure:
    """Tests for _validate_config_structure method."""

    def test_validates_complete_config(self, config_manager, valid_config):
        """Test validation of complete valid configuration."""
        errors = config_manager._validate_config_structure(valid_config)
        assert errors == []

    def test_detects_missing_required_keys(self, config_manager):
        """Test detection of missing required keys."""
        incomplete_config = {"cpp_version": "c++17"}

        with pytest.raises(ConfigMissingError) as exc_info:
            config_manager._validate_config_structure(incomplete_config)

        assert "gemini" in str(exc_info.value) or "editor_settings" in str(exc_info.value)

    def test_detects_invalid_type_for_cpp_version(self, config_manager, valid_config):
        """Test detection of invalid type for cpp_version."""
        valid_config["cpp_version"] = 17  # Should be string
        errors = config_manager._validate_config_structure(valid_config)
        assert any("cpp_version" in error for error in errors)

    def test_detects_invalid_type_for_gemini(self, config_manager, valid_config):
        """Test detection of invalid type for gemini settings."""
        valid_config["gemini"] = "not a dict"
        errors = config_manager._validate_config_structure(valid_config)
        assert any("gemini" in error for error in errors)

    def test_detects_missing_gemini_enabled(self, config_manager, valid_config):
        """Test detection of missing gemini.enabled."""
        del valid_config["gemini"]["enabled"]
        errors = config_manager._validate_config_structure(valid_config)
        assert any("enabled" in error for error in errors)

    def test_detects_missing_gemini_api_key(self, config_manager, valid_config):
        """Test detection of missing gemini.api_key."""
        del valid_config["gemini"]["api_key"]
        errors = config_manager._validate_config_structure(valid_config)
        assert any("api_key" in error for error in errors)

    def test_detects_missing_gemini_model(self, config_manager, valid_config):
        """Test detection of missing gemini.model."""
        del valid_config["gemini"]["model"]
        errors = config_manager._validate_config_structure(valid_config)
        assert any("model" in error for error in errors)

    def test_detects_invalid_gemini_enabled_type(self, config_manager, valid_config):
        """Test detection of invalid type for gemini.enabled."""
        valid_config["gemini"]["enabled"] = "true"  # Should be bool
        errors = config_manager._validate_config_structure(valid_config)
        assert any("enabled" in error for error in errors)

    def test_detects_missing_editor_settings(self, config_manager, valid_config):
        """Test detection of missing editor settings."""
        del valid_config["editor_settings"]["autosave"]
        errors = config_manager._validate_config_structure(valid_config)
        assert any("autosave" in error for error in errors)

    def test_detects_invalid_editor_setting_type(self, config_manager, valid_config):
        """Test detection of invalid type for editor settings."""
        valid_config["editor_settings"]["font_size"] = "12"  # Should be int
        errors = config_manager._validate_config_structure(valid_config)
        assert any("font_size" in error for error in errors)

    def test_validates_cpp_language_config(self, config_manager, valid_config):
        """Test validation of C++ language configuration."""
        # Valid cpp config should pass
        errors = config_manager._validate_config_structure(valid_config)
        assert errors == []

        # Invalid compiler type
        valid_config["languages"]["cpp"]["compiler"] = 123
        errors = config_manager._validate_config_structure(valid_config)
        assert any("cpp.compiler" in error for error in errors)

    def test_validates_python_language_config(self, config_manager, valid_config):
        """Test validation of Python language configuration."""
        # Invalid interpreter type
        valid_config["languages"]["py"]["interpreter"] = []
        errors = config_manager._validate_config_structure(valid_config)
        assert any("py.interpreter" in error for error in errors)

    def test_validates_java_language_config(self, config_manager, valid_config):
        """Test validation of Java language configuration."""
        # Invalid compiler type
        valid_config["languages"]["java"]["compiler"] = 123
        errors = config_manager._validate_config_structure(valid_config)
        assert any("java.compiler" in error for error in errors)

        # Invalid runtime type
        valid_config["languages"]["java"]["runtime"] = []
        errors = config_manager._validate_config_structure(valid_config)
        assert any("java.runtime" in error for error in errors)

    def test_handles_missing_optional_language_configs(self, config_manager, valid_config):
        """Test that missing language configs are handled gracefully."""
        # Remove one language
        del valid_config["languages"]["java"]
        errors = config_manager._validate_config_structure(valid_config)
        # Should not error - languages are optional
        assert errors == []

    def test_handles_invalid_language_config_type(self, config_manager, valid_config):
        """Test detection of invalid language config type."""
        valid_config["languages"]["cpp"] = "not a dict"
        errors = config_manager._validate_config_structure(valid_config)
        assert any("cpp" in error for error in errors)


class TestGetDefaultConfig:
    """Tests for get_default_config method."""

    def test_returns_dict(self, config_manager):
        """Test that default config is a dictionary."""
        default = config_manager.get_default_config()
        assert isinstance(default, dict)

    def test_has_required_keys(self, config_manager):
        """Test that default config has all required keys."""
        default = config_manager.get_default_config()
        assert "cpp_version" in default
        assert "gemini" in default
        assert "editor_settings" in default
        assert "languages" in default

    def test_has_all_languages(self, config_manager):
        """Test that default config includes all supported languages."""
        default = config_manager.get_default_config()
        assert "cpp" in default["languages"]
        assert "py" in default["languages"]
        assert "java" in default["languages"]

    def test_cpp_language_has_required_fields(self, config_manager):
        """Test that default C++ config has required fields."""
        default = config_manager.get_default_config()
        cpp = default["languages"]["cpp"]
        assert "compiler" in cpp
        assert "std_version" in cpp
        assert "optimization" in cpp
        assert "flags" in cpp

    def test_python_language_has_required_fields(self, config_manager):
        """Test that default Python config has required fields."""
        default = config_manager.get_default_config()
        py = default["languages"]["py"]
        assert "interpreter" in py
        assert "version" in py
        assert "flags" in py

    def test_java_language_has_required_fields(self, config_manager):
        """Test that default Java config has required fields."""
        default = config_manager.get_default_config()
        java = default["languages"]["java"]
        assert "compiler" in java
        assert "version" in java
        assert "flags" in java
        assert "runtime" in java

    def test_gemini_settings_complete(self, config_manager):
        """Test that default gemini settings are complete."""
        default = config_manager.get_default_config()
        gemini = default["gemini"]
        assert "enabled" in gemini
        assert "api_key" in gemini
        assert "model" in gemini
        assert isinstance(gemini["enabled"], bool)
        assert isinstance(gemini["api_key"], str)
        assert isinstance(gemini["model"], str)

    def test_editor_settings_complete(self, config_manager):
        """Test that default editor settings are complete."""
        default = config_manager.get_default_config()
        editor = default["editor_settings"]
        required_settings = [
            "autosave",
            "autosave_interval",
            "tab_width",
            "font_size",
            "font_family",
            "bracket_matching",
        ]
        for setting in required_settings:
            assert setting in editor

    def test_default_config_is_valid(self, config_manager):
        """Test that default config passes validation."""
        default = config_manager.get_default_config()
        errors = config_manager._validate_config_structure(default)
        assert errors == []

    def test_gemini_disabled_by_default(self, config_manager):
        """Test that Gemini is disabled by default."""
        default = config_manager.get_default_config()
        assert default["gemini"]["enabled"] is False

    def test_default_model_is_gemini_2_5_flash(self, config_manager):
        """Test that default model is gemini-2.5-flash."""
        default = config_manager.get_default_config()
        assert default["gemini"]["model"] == "gemini-2.5-flash"


class TestConfigManagerIntegration:
    """Integration tests for ConfigManager."""

    def test_save_and_load_roundtrip(self, config_manager, valid_config):
        """Test that save and load preserve configuration."""
        # Save config
        config_manager.save_config(valid_config)

        # Load config
        loaded = config_manager.load_config()

        # Should match
        assert loaded == valid_config

    def test_default_config_can_be_saved_and_loaded(self, config_manager):
        """Test that default config can be saved and reloaded."""
        # Get default config
        default = config_manager.get_default_config()

        # Save it
        config_manager.save_config(default)

        # Load it back
        loaded = config_manager.load_config()

        # Should match
        assert loaded == default

    def test_multiple_save_operations(self, config_manager):
        """Test multiple consecutive save operations with valid configs."""
        for i in range(3):
            config = config_manager.get_default_config()
            config["cpp_version"] = f"c++{17 + i}"
            config_manager.save_config(config)
            loaded = config_manager.load_config()
            assert loaded["cpp_version"] == f"c++{17 + i}"

    def test_backup_chain(self, config_manager):
        """Test that multiple saves create backup correctly."""
        # First save with valid config
        config1 = config_manager.get_default_config()
        config1["cpp_version"] = "c++17"
        config_manager.save_config(config1)

        # Second save (should backup config1)
        config2 = config_manager.get_default_config()
        config2["cpp_version"] = "c++20"
        config_manager.save_config(config2)

        # Verify current config
        loaded = config_manager.load_config()
        assert loaded["cpp_version"] == "c++20"

        # Verify backup exists with config1
        backup_file = f"{config_manager.config_file}.bak"
        with open(backup_file, "r") as f:
            backup = json.load(f)
        assert backup["cpp_version"] == "c++17"

    def test_handles_corrupted_backup(self, config_manager, valid_config):
        """Test that corrupted backup doesn't prevent saving."""
        # Create corrupted backup file
        backup_file = f"{config_manager.config_file}.bak"
        with open(backup_file, "w") as f:
            f.write("corrupted backup")

        # Should still be able to save
        config_manager.save_config(valid_config)

        # Verify new config saved
        loaded = config_manager.load_config()
        assert loaded == valid_config

    def test_multilanguage_workflow(self, config_manager):
        """Test complete workflow with multi-language configuration."""
        # Create config with all languages
        config = config_manager.get_default_config()

        # Modify each language config
        config["languages"]["cpp"]["std_version"] = "c++20"
        config["languages"]["py"]["interpreter"] = "python3"
        config["languages"]["java"]["version"] = "17"

        # Save
        config_manager.save_config(config)

        # Load and verify
        loaded = config_manager.load_config()
        assert loaded["languages"]["cpp"]["std_version"] == "c++20"
        assert loaded["languages"]["py"]["interpreter"] == "python3"
        assert loaded["languages"]["java"]["version"] == "17"
