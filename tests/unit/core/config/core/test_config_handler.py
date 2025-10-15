"""
Phase 8 Task 4 - Phase 2: Tests for config_handler.py

Tests cover:
- ConfigManager: load_config, save_config, validation, defaults
- ConfigPersistence: UI loading/saving, error handling
- Exception handling for all config operations
"""

import json
import os
import tempfile
from unittest.mock import MagicMock, Mock, mock_open, patch

import pytest
from PySide6.QtWidgets import QMessageBox

from src.app.core.config.core.config_handler import ConfigManager, ConfigPersistence
from src.app.core.config.core.exceptions import (
    ConfigError,
    ConfigFormatError,
    ConfigLoadError,
    ConfigMissingError,
    ConfigPermissionError,
    ConfigSaveError,
    ConfigValidationError,
)

# ============================================================================
# Test Fixtures
# ============================================================================


@pytest.fixture
def temp_config_file():
    """Create a temporary config file."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        config_path = f.name
    yield config_path
    # Cleanup
    if os.path.exists(config_path):
        os.unlink(config_path)


@pytest.fixture
def config_manager(temp_config_file):
    """Create ConfigManager instance with temp file."""
    return ConfigManager(temp_config_file)


@pytest.fixture
def valid_config():
    """Valid configuration data."""
    return {
        "cpp_version": "c++17",
        "gemini": {"enabled": False, "api_key": "", "model": "gemini-2.5-flash"},
        "editor_settings": {
            "autosave": True,
            "autosave_interval": 5,
            "tab_width": 4,
            "font_size": 12,
            "bracket_matching": True,
        },
        "languages": {"cpp": {"compiler": "g++", "std_version": "c++17"}},
    }


@pytest.fixture
def mock_parent_dialog():
    """Mock parent dialog with UI elements."""
    parent = Mock()
    parent.key_input = Mock()
    parent.use_ai_checkbox = Mock()
    parent.status_label = Mock()
    parent.is_key_valid = False
    parent.cpp_compiler_combo = Mock()
    parent.cpp_std_combo = Mock()
    parent.cpp_opt_combo = Mock()
    parent.cpp_flags_input = Mock()
    parent.py_interpreter_combo = Mock()
    parent.py_flags_input = Mock()
    parent.java_compiler_combo = Mock()
    parent.java_runtime_combo = Mock()
    parent.java_flags_input = Mock()
    parent.show_error = Mock()
    return parent


# ============================================================================
# ConfigManager Initialization Tests
# ============================================================================


class TestConfigManagerInitialization:
    """Test ConfigManager initialization."""

    def test_init_with_absolute_path(self):
        """Test initialization with absolute path."""
        manager = ConfigManager("/absolute/path/config.json")
        # On Windows, path gets normalized
        assert "config.json" in manager.config_file

    def test_init_with_relative_path(self, temp_config_file):
        """Test initialization with relative path uses CONFIG_DIR."""
        manager = ConfigManager("config.json")
        # Should join with CONFIG_DIR
        assert "config.json" in manager.config_file
        assert os.path.isabs(manager.config_file)


# ============================================================================
# ConfigManager Load Tests
# ============================================================================


class TestConfigManagerLoad:
    """Test load_config method."""

    def test_load_existing_valid_config(self, config_manager, temp_config_file, valid_config):
        """Test loading existing valid configuration."""
        # Write valid config
        with open(temp_config_file, "w") as f:
            json.dump(valid_config, f)

        loaded = config_manager.load_config()

        assert loaded["cpp_version"] == "c++17"
        assert loaded["gemini"]["enabled"] is False
        assert loaded["editor_settings"]["autosave"] is True

    def test_load_nonexistent_returns_default(self, config_manager):
        """Test loading nonexistent file returns defaults."""
        config_manager.config_file = "/nonexistent/path/config.json"

        config = config_manager.load_config()

        assert "cpp_version" in config
        assert "gemini" in config
        assert "editor_settings" in config

    def test_load_invalid_json_raises_format_error(self, config_manager, temp_config_file):
        """Test loading invalid JSON raises ConfigFormatError."""
        # Write invalid JSON
        with open(temp_config_file, "w") as f:
            f.write("{invalid json")

        with pytest.raises(ConfigFormatError):
            config_manager.load_config()

    def test_load_missing_required_keys_raises_validation_error(
        self, config_manager, temp_config_file
    ):
        """Test loading config with missing keys raises ConfigMissingError."""
        # Write config missing required keys
        with open(temp_config_file, "w") as f:
            json.dump({"cpp_version": "c++17"}, f)  # Missing gemini, editor_settings

        # Raises ConfigMissingError (subclass of ConfigError)
        with pytest.raises(ConfigMissingError):
            config_manager.load_config()

    @patch("os.access")
    def test_load_no_read_permission_raises_permission_error(
        self, mock_access, config_manager, temp_config_file
    ):
        """Test loading file without read permission raises ConfigPermissionError."""
        # Write valid config
        with open(temp_config_file, "w") as f:
            json.dump({"test": "data"}, f)

        # Mock no read permission
        mock_access.return_value = False

        with pytest.raises(ConfigPermissionError) as exc_info:
            config_manager.load_config()

        assert "reading" in str(exc_info.value)


# ============================================================================
# ConfigManager Save Tests
# ============================================================================


class TestConfigManagerSave:
    """Test save_config method."""

    def test_save_config_success(self, config_manager, temp_config_file, valid_config):
        """Test successful configuration save."""
        config_manager.save_config(valid_config)

        # Verify file was written
        with open(temp_config_file, "r") as f:
            saved = json.load(f)

        assert saved == valid_config

    def test_save_creates_directory(self, temp_config_file):
        """Test save creates directory if it doesn't exist."""
        # Create path with non-existent directory
        new_dir = os.path.join(os.path.dirname(temp_config_file), "new_subdir")
        new_path = os.path.join(new_dir, "config.json")

        manager = ConfigManager(new_path)
        manager.save_config({"test": "data"})

        assert os.path.exists(new_path)

        # Cleanup
        os.unlink(new_path)
        os.rmdir(new_dir)

    def test_save_creates_backup(self, config_manager, temp_config_file, valid_config):
        """Test save creates backup of existing config."""
        # Create initial config
        with open(temp_config_file, "w") as f:
            json.dump({"old": "data"}, f)

        # Save new config
        config_manager.save_config(valid_config)

        # Check backup was created
        backup_file = f"{temp_config_file}.bak"
        if os.path.exists(backup_file):
            with open(backup_file, "r") as f:
                backup = json.load(f)
            assert backup == {"old": "data"}
            os.unlink(backup_file)

    @patch("os.makedirs")
    def test_save_invalid_path_raises_error(self, mock_makedirs):
        """Test save with invalid path raises ConfigSaveError."""
        # Mock makedirs to fail
        mock_makedirs.side_effect = PermissionError("Access denied")

        manager = ConfigManager("/invalid/readonly/path/config.json")

        with pytest.raises(ConfigSaveError):
            manager.save_config({"test": "data"})


# ============================================================================
# ConfigManager Validation Tests
# ============================================================================


class TestConfigManagerValidation:
    """Test _validate_config_structure method."""

    def test_validate_valid_config(self, config_manager, valid_config):
        """Test validation of valid configuration."""
        errors = config_manager._validate_config_structure(valid_config)

        assert errors == []

    def test_validate_missing_cpp_version(self, config_manager):
        """Test validation catches missing cpp_version."""
        config = {
            "gemini": {"enabled": False, "api_key": "", "model": "test"},
            "editor_settings": {
                "autosave": True,
                "autosave_interval": 5,
                "tab_width": 4,
                "font_size": 12,
                "bracket_matching": True,
            },
        }

        with pytest.raises(ConfigMissingError):
            config_manager._validate_config_structure(config)

    def test_validate_wrong_type_cpp_version(self, config_manager, valid_config):
        """Test validation catches wrong type for cpp_version."""
        valid_config["cpp_version"] = 123  # Should be string

        errors = config_manager._validate_config_structure(valid_config)

        assert any("cpp_version" in error for error in errors)

    def test_validate_invalid_gemini_structure(self, config_manager, valid_config):
        """Test validation catches invalid gemini structure."""
        valid_config["gemini"] = {"enabled": "not a bool"}  # Missing required keys

        errors = config_manager._validate_config_structure(valid_config)

        assert len(errors) > 0
        assert any("Gemini" in error for error in errors)

    def test_validate_invalid_editor_settings(self, config_manager, valid_config):
        """Test validation catches invalid editor settings."""
        valid_config["editor_settings"] = {"autosave": "not a bool"}  # Missing required keys

        errors = config_manager._validate_config_structure(valid_config)

        assert len(errors) > 0
        assert any("editor setting" in error for error in errors)

    def test_validate_languages_optional(self, config_manager):
        """Test languages section is optional."""
        config = {
            "cpp_version": "c++17",
            "gemini": {"enabled": False, "api_key": "", "model": "test"},
            "editor_settings": {
                "autosave": True,
                "autosave_interval": 5,
                "tab_width": 4,
                "font_size": 12,
                "bracket_matching": True,
            },
        }

        errors = config_manager._validate_config_structure(config)

        assert errors == []

    def test_validate_cpp_language_config(self, config_manager, valid_config):
        """Test validation of C++ language config."""
        valid_config["languages"]["cpp"]["compiler"] = 123  # Should be string

        errors = config_manager._validate_config_structure(valid_config)

        assert any("cpp.compiler" in error for error in errors)


# ============================================================================
# ConfigManager Default Config Tests
# ============================================================================


class TestConfigManagerDefaults:
    """Test get_default_config method."""

    def test_get_default_config_structure(self, config_manager):
        """Test default config has all required keys."""
        config = config_manager.get_default_config()

        assert "cpp_version" in config
        assert "gemini" in config
        assert "editor_settings" in config
        assert "languages" in config

    def test_get_default_config_gemini_disabled(self, config_manager):
        """Test default config has Gemini disabled."""
        config = config_manager.get_default_config()

        assert config["gemini"]["enabled"] is False
        assert config["gemini"]["api_key"] == ""

    def test_get_default_config_languages(self, config_manager):
        """Test default config includes all language configurations."""
        config = config_manager.get_default_config()

        assert "cpp" in config["languages"]
        assert "py" in config["languages"]
        assert "java" in config["languages"]

    def test_get_default_config_editor_settings(self, config_manager):
        """Test default config has complete editor settings."""
        config = config_manager.get_default_config()
        settings = config["editor_settings"]

        assert "autosave" in settings
        assert "autosave_interval" in settings
        assert "tab_width" in settings
        assert "font_size" in settings
        assert "bracket_matching" in settings


# ============================================================================
# ConfigPersistence Tests
# ============================================================================


class TestConfigPersistence:
    """Test ConfigPersistence class."""

    def test_init(self, mock_parent_dialog, config_manager):
        """Test ConfigPersistence initialization."""
        persistence = ConfigPersistence(mock_parent_dialog, config_manager)

        assert persistence.parent == mock_parent_dialog
        assert persistence.config_manager == config_manager

    def test_load_config_populates_ui(
        self, mock_parent_dialog, config_manager, temp_config_file, valid_config
    ):
        """Test load_config populates UI fields."""
        # Write config with API key to trigger all code paths
        valid_config["gemini"]["api_key"] = "AIzaSyTest1234567890abcdefghijk"
        with open(temp_config_file, "w") as f:
            json.dump(valid_config, f)

        persistence = ConfigPersistence(mock_parent_dialog, config_manager)
        persistence.load_config()

        # Verify UI was populated
        mock_parent_dialog.cpp_std_combo.setCurrentText.assert_called()
        mock_parent_dialog.key_input.setText.assert_called()

    def test_load_config_invalid_uses_default(
        self, mock_parent_dialog, config_manager, temp_config_file
    ):
        """Test load_config falls back to defaults on error."""
        # Write invalid config
        with open(temp_config_file, "w") as f:
            f.write("{invalid json")

        persistence = ConfigPersistence(mock_parent_dialog, config_manager)
        persistence.load_config()

        # Should not crash, uses defaults
        mock_parent_dialog.show_error.assert_not_called()

    def test_load_config_with_api_key_enables_checkbox(
        self, mock_parent_dialog, config_manager, temp_config_file, valid_config
    ):
        """Test load_config with API key enables AI checkbox."""
        valid_config["gemini"]["api_key"] = "AIzaSyTest1234567890abcdefghijk"
        valid_config["gemini"]["enabled"] = True

        with open(temp_config_file, "w") as f:
            json.dump(valid_config, f)

        persistence = ConfigPersistence(mock_parent_dialog, config_manager)
        persistence.load_config()

        mock_parent_dialog.use_ai_checkbox.setEnabled.assert_called_with(True)
        mock_parent_dialog.use_ai_checkbox.setChecked.assert_called_with(True)

    def test_load_config_without_api_key_disables_checkbox(
        self, mock_parent_dialog, config_manager, temp_config_file, valid_config
    ):
        """Test load_config without API key disables AI checkbox."""
        with open(temp_config_file, "w") as f:
            json.dump(valid_config, f)

        persistence = ConfigPersistence(mock_parent_dialog, config_manager)
        persistence.load_config()

        mock_parent_dialog.use_ai_checkbox.setEnabled.assert_called_with(False)

    def test_load_config_populates_language_flags(
        self, mock_parent_dialog, config_manager, temp_config_file, valid_config
    ):
        """Test load_config populates language compiler flags."""
        # Ensure all language configs exist
        valid_config["languages"]["cpp"]["flags"] = ["-Wall", "-Wextra"]
        valid_config["languages"]["py"] = {
            "interpreter": "python",
            "flags": ["-u", "-B"],
        }

        with open(temp_config_file, "w") as f:
            json.dump(valid_config, f)

        persistence = ConfigPersistence(mock_parent_dialog, config_manager)
        persistence.load_config()

        mock_parent_dialog.cpp_flags_input.setText.assert_called_with("-Wall, -Wextra")
        mock_parent_dialog.py_flags_input.setText.assert_called_with("-u, -B")


# ============================================================================
# Integration Tests
# ============================================================================


class TestIntegration:
    """Integration tests for complete workflows."""

    def test_save_and_load_roundtrip(self, config_manager, temp_config_file, valid_config):
        """Test save and load roundtrip preserves data."""
        # Save
        config_manager.save_config(valid_config)

        # Load
        loaded = config_manager.load_config()

        assert loaded == valid_config

    def test_config_persistence_workflow(
        self, mock_parent_dialog, config_manager, temp_config_file, valid_config
    ):
        """Test complete config persistence workflow."""
        # Write config with API key to trigger setText
        valid_config["gemini"]["api_key"] = "AIzaSyTest1234567890abcdefghijk"
        with open(temp_config_file, "w") as f:
            json.dump(valid_config, f)

        # Load via persistence
        persistence = ConfigPersistence(mock_parent_dialog, config_manager)
        persistence.load_config()

        # Verify UI populated
        assert mock_parent_dialog.cpp_std_combo.setCurrentText.called
        assert mock_parent_dialog.key_input.setText.called

    def test_default_config_is_valid(self, config_manager):
        """Test default config passes validation."""
        default = config_manager.get_default_config()

        errors = config_manager._validate_config_structure(default)

        assert errors == []
