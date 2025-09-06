"""Consolidated configuration handler combining management and persistence."""

import json
import os
import os.path
from typing import Dict, Any, Optional

from PySide6.QtWidgets import QMessageBox

from src.app.core.config.core.exceptions import (
    ConfigError,
    ConfigPermissionError,
    ConfigFormatError,
    ConfigValidationError,
    ConfigLoadError,
    ConfigSaveError,
    ConfigMissingError
)
from src.app.constants import USER_DATA_DIR, CONFIG_FILE
from src.app.styles.constants.colors import MATERIAL_COLORS
from src.app.styles.components.config_ui import (
    SUCCESS_MESSAGE_STYLE, 
    INFO_MESSAGE_STYLE,
    get_success_status_style
)


class ConfigManager:
    """Core configuration management - loading, saving, validation."""
    
    CONFIG_DIR = USER_DATA_DIR
    
    def __init__(self, config_file='config.json'):
        self.config_file = os.path.join(self.CONFIG_DIR, config_file)

    def load_config(self):
        """Load configuration from JSON file with validation."""
        try:
            if not os.path.exists(self.config_file):
                return self.get_default_config()

            if not os.access(self.config_file, os.R_OK):
                raise ConfigPermissionError("reading", self.config_file)

            try:
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
            except json.JSONDecodeError as e:
                raise ConfigFormatError(e.msg, e.lineno)
            
            validation_errors = self._validate_config_structure(config)
            if validation_errors:
                raise ConfigValidationError("configuration structure",
                    "Invalid configuration format",
                    "\n".join(validation_errors))
            
            return config

        except ConfigError:
            raise
        except Exception as e:
            raise ConfigLoadError(str(e))

    def save_config(self, config):
        """Save configuration to JSON file with backup."""
        try:
            # Ensure config directory exists
            os.makedirs(self.CONFIG_DIR, exist_ok=True)

            # Backup existing config
            if os.path.exists(self.config_file):
                backup_file = f"{self.config_file}.bak"
                try:
                    import shutil
                    shutil.copy2(self.config_file, backup_file)
                except Exception:
                    pass  # Ignore backup failures

            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=4)

        except Exception as e:
            raise ConfigSaveError(f"Failed to save config: {str(e)}")

    def _validate_config_structure(self, config):
        """Validate configuration structure and return list of errors."""
        errors = []
        required_keys = {
            'cpp_version': str,
            'workspace_folder': str,
            'gemini': dict,  # Standardized format (Phase 1)
            'editor_settings': dict
        }
        
        for key, expected_type in required_keys.items():
            if key not in config:
                errors.append(f"Missing required key: {key}")
            elif not isinstance(config[key], expected_type):
                errors.append(f"Invalid type for {key}: expected {expected_type.__name__}")
        
        if 'gemini' in config:
            gemini_settings = config['gemini']
            required_gemini_settings = {
                'enabled': bool,
                'api_key': str,
                'model': str
            }
            
            for key, expected_type in required_gemini_settings.items():
                if key not in gemini_settings:
                    errors.append(f"Missing Gemini setting: {key}")
                elif not isinstance(gemini_settings[key], expected_type):
                    errors.append(f"Invalid type for Gemini setting {key}")
            
            # Note: We don't require a valid API key, just the correct structure
        
        if 'editor_settings' in config:
            editor_settings = config['editor_settings']
            required_settings = {
                'autosave': bool,
                'autosave_interval': int,
                'tab_width': int,
                'font_size': int,
                'bracket_matching': bool
            }
            
            for key, expected_type in required_settings.items():
                if key not in editor_settings:
                    errors.append(f"Missing editor setting: {key}")
                elif not isinstance(editor_settings[key], expected_type):
                    errors.append(f"Invalid type for editor setting {key}")
        
        if missing_keys := [k for k in required_keys if k not in config]:
            raise ConfigMissingError(f"Required keys: {', '.join(missing_keys)}")
        
        return errors

    def get_default_config(self):
        """Get default configuration structure."""
        return {
            'cpp_version': 'c++17',
            'workspace_folder': '',
            'gemini': {  # Standardized format (Phase 1)
                'enabled': False,
                'api_key': '',
                'model': ''
            },
            'editor_settings': {
                'autosave': True,
                'autosave_interval': 5,
                'tab_width': 4,
                'font_size': 12,
                'font_family': 'Consolas',
                'bracket_matching': True
            }
        }


class ConfigPersistence:
    """UI-specific configuration persistence - loading/saving from dialog."""
    
    def __init__(self, parent_dialog, config_manager):
        self.parent = parent_dialog
        self.config_manager = config_manager
        
    def load_config(self):
        """Load configuration from file and populate UI fields."""
        try:
            cfg = self.config_manager.load_config()
        except ConfigError as e:
            # If config is invalid, try to reset to defaults
            try:
                default_cfg = self.config_manager.get_default_config()
                self.config_manager.save_config(default_cfg)
                cfg = default_cfg
            except:
                cfg = {}
        except Exception as e:
            self.parent.show_error("Unexpected Error", "Failed to load configuration", str(e))
            cfg = {}

        # Populate fields with safe defaults
        self.parent.cpp_version_combo.setCurrentText(cfg.get("cpp_version", "auto"))
        self.parent.workspace_input.setText(cfg.get("workspace_folder", ""))
        
        # Updated for new gemini format (Phase 1)
        gemini_settings = cfg.get("gemini", {}) if isinstance(cfg.get("gemini"), dict) else {}
        enabled = gemini_settings.get("enabled", False)
        api_key = gemini_settings.get("api_key", "")
        model = gemini_settings.get("model", "")
        
        # Load API key first
        if api_key:
            self.parent.key_input.setText(api_key)
            # Assume previously validated keys are still valid
            self.parent.is_key_valid = True
            self.parent.status_label.setText("✓")
            self.parent.status_label.setStyleSheet(get_success_status_style())
            self.parent.status_label.setToolTip("Previously validated API key")
            self.parent.use_ai_checkbox.setEnabled(True)
        else:
            self.parent.use_ai_checkbox.setEnabled(False)
            self.parent.is_key_valid = False
            enabled = False
        
        self.parent.use_ai_checkbox.setChecked(enabled)
        
        # Load preferred model
        self.parent.model_input.setText(model)
        
        editor_settings = cfg.get("editor_settings", {}) if isinstance(cfg.get("editor_settings"), dict) else {}
        self.parent.font_size_spin.setValue(int(editor_settings.get("font_size", 13)))
        self.parent.wrap_checkbox.setChecked(bool(editor_settings.get("wrap_lines", False)))

    def save_config(self):
        """Save configuration to file from UI values."""
        try:
            # Load current config to preserve settings not in the UI
            try:
                current_config = self.config_manager.load_config()
            except:
                current_config = self.config_manager.get_default_config()
            
            # Update with UI values using new gemini format (Phase 1)
            config = {
                "cpp_version": self.parent.cpp_version_combo.currentText(),
                "workspace_folder": self.parent.workspace_input.text().strip(),
                "gemini": {  # New standardized format
                    "enabled": self.parent.use_ai_checkbox.isChecked(),
                    "api_key": self.parent.key_input.text().strip(),
                    "model": self.parent.model_input.text().strip()
                },
                "editor_settings": {
                    # Preserve existing settings not shown in UI
                    "autosave": current_config.get("editor_settings", {}).get("autosave", True),
                    "autosave_interval": current_config.get("editor_settings", {}).get("autosave_interval", 5),
                    "tab_width": current_config.get("editor_settings", {}).get("tab_width", 4),
                    "font_family": current_config.get("editor_settings", {}).get("font_family", "Consolas"),
                    "bracket_matching": current_config.get("editor_settings", {}).get("bracket_matching", True),
                    # Update with UI values
                    "font_size": int(self.parent.font_size_spin.value()),
                    "wrap_lines": bool(self.parent.wrap_checkbox.isChecked())
                }
            }
            self.config_manager.save_config(config)
            
            # Success message
            self.parent.show_success("Configuration Saved", "Settings saved successfully!")
            
        except ConfigError as e:
            self.parent.show_error("Configuration Error", str(e))
        except Exception as e:
            self.parent.show_error("Save Error", "Failed to save configuration", str(e))

    def reset_to_defaults(self):
        """Reset configuration to defaults."""
        reply = QMessageBox.question(
            self.parent,
            "Confirm Reset",
            "Are you sure you want to reset all settings to defaults?\n\nThis action cannot be undone.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if reply == QMessageBox.Yes:
            try:
                default_config = self.config_manager.get_default_config()
                self.config_manager.save_config(default_config)
                
                # Reload UI with defaults
                self.load_config()
                
                # Show success
                self.parent.show_success("Reset Complete", "Configuration reset to defaults.")
                
            except Exception as e:
                self.parent.show_error("Reset Error", "Failed to reset configuration", str(e))

    def show_success(self, title, message):
        """Show success message to user."""
        QMessageBox.information(self.parent, title, message)
