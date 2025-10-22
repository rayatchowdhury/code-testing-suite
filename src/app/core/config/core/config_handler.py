"""Consolidated configuration handler combining management and persistence."""

import json
import logging
import os
from typing import Dict, Optional, Protocol

from PySide6.QtWidgets import QCheckBox, QComboBox, QLabel, QLineEdit, QMessageBox, QSpinBox

from src.app.core.config.core.exceptions import (
    ConfigError,
    ConfigFormatError,
    ConfigLoadError,
    ConfigMissingError,
    ConfigPermissionError,
    ConfigSaveError,
    ConfigValidationError,
)
from src.app.presentation.shared.design_system.styles.components.config_ui import get_success_status_style
from src.app.shared.constants import USER_DATA_DIR
from src.app.presentation.services import ErrorHandlerService

# Setup logger
logger = logging.getLogger(__name__)


class ConfigDialogProtocol(Protocol):
    """Protocol defining the expected interface for config dialog widgets."""
    
    # Required attributes (always present)
    key_input: QLineEdit
    is_key_valid: bool
    status_label: QLabel
    use_ai_checkbox: QCheckBox
    font_size_spin: QSpinBox
    wrap_checkbox: QCheckBox
    
    # Optional language compiler attributes
    cpp_compiler_combo: Optional[QComboBox]
    cpp_std_combo: Optional[QComboBox]
    cpp_opt_combo: Optional[QComboBox]
    cpp_flags_input: Optional[QLineEdit]
    py_interpreter_combo: Optional[QComboBox]
    py_flags_input: Optional[QLineEdit]
    java_compiler_combo: Optional[QComboBox]
    java_runtime_combo: Optional[QComboBox]
    java_flags_input: Optional[QLineEdit]
    
    # Optional editor settings attributes
    font_family_combo: Optional[QComboBox]
    tab_width_spin: Optional[QSpinBox]
    bracket_match_checkbox: Optional[QCheckBox]
    autosave_checkbox: Optional[QCheckBox]
    autosave_interval_spin: Optional[QSpinBox]
    
    # Optional model selection (backward compatibility)
    model_combo: Optional[QComboBox]
    model_input: Optional[QLineEdit]
    
    # Required methods
    def show_error(self, title: str, message: str, details: str = "") -> None: ...
    def show_success(self, title: str, message: str) -> None: ...


class ConfigManager:
    """Core configuration management - loading, saving, validation."""

    CONFIG_DIR = USER_DATA_DIR
    _instance = None

    def __init__(self, config_file="config.json"):
        # If config_file is an absolute path, use it directly
        # Otherwise, treat it as a filename under CONFIG_DIR
        if os.path.isabs(config_file):
            self.config_file = config_file
        else:
            self.config_file = os.path.join(self.CONFIG_DIR, config_file)
    
    @classmethod
    def instance(cls, config_file="config.json"):
        """
        Get or create singleton instance of ConfigManager.
        
        This is the recommended way to access configuration throughout the application.
        Uses a singleton pattern to ensure consistent config access across all modules.
        
        Args:
            config_file: Optional config file path (only used on first call)
        
        Returns:
            ConfigManager: Singleton instance
        
        Example:
            config_manager = ConfigManager.instance()
            config = config_manager.load_config()
        """
        if cls._instance is None:
            cls._instance = cls(config_file)
            logger.info(f"ConfigManager singleton created with config file: {cls._instance.config_file}")
        return cls._instance
    
    @classmethod
    def reset_instance(cls):
        """
        Reset singleton instance (primarily for testing).
        
        Allows tests to create fresh ConfigManager instances with different
        config files without affecting other tests.
        """
        cls._instance = None
        logger.debug("ConfigManager singleton reset")

    def load_config(self):
        """Load configuration from JSON file with validation."""
        try:
            if not os.path.exists(self.config_file):
                logger.info(f"Config file not found, using defaults: {self.config_file}")
                return self.get_default_config()

            if not os.access(self.config_file, os.R_OK):
                raise ConfigPermissionError("reading", self.config_file)

            try:
                with open(self.config_file, "r") as f:
                    config = json.load(f)
            except json.JSONDecodeError as e:
                raise ConfigFormatError(e.msg, e.lineno)

            validation_errors = self._validate_config_structure(config)
            if validation_errors:
                logger.error(f"Config validation failed: {validation_errors}")
                raise ConfigValidationError(
                    "configuration structure",
                    "Invalid configuration format",
                    "\n".join(validation_errors),
                )

            logger.info(f"Config loaded successfully from {self.config_file}")
            return config

        except ConfigError:
            raise
        except Exception as e:
            logger.exception(f"Unexpected error loading config: {e}")
            raise ConfigLoadError(str(e))

    def save_config(self, config):
        """Save configuration to JSON file with backup."""
        try:
            # Ensure the directory for the config file exists
            config_dir = os.path.dirname(self.config_file)
            os.makedirs(config_dir, exist_ok=True)

            # Backup existing config
            if os.path.exists(self.config_file):
                backup_file = f"{self.config_file}.bak"
                try:
                    import shutil
                    shutil.copy2(self.config_file, backup_file)
                    logger.debug(f"Config backed up to {backup_file}")
                except (IOError, OSError) as e:
                    logger.warning(f"Failed to create config backup: {e}")

            with open(self.config_file, "w") as f:
                json.dump(config, f, indent=4)
            
            logger.info(f"Config saved successfully to {self.config_file}")

        except (IOError, OSError, PermissionError) as e:
            logger.error(f"Failed to save config: {e}")
            raise ConfigSaveError(f"Failed to save config: {str(e)}")
        except Exception as e:
            logger.exception(f"Unexpected error saving config: {e}")
            raise ConfigSaveError(f"Failed to save config: {str(e)}")

    def _validate_config_structure(self, config):
        """Validate configuration structure and return list of errors."""
        errors = []
        required_keys = {
            "cpp_version": str,
            "gemini": dict,  # Standardized format (Phase 1)
            "editor_settings": dict,
            "languages": dict,  # Multi-language support
        }

        for key, expected_type in required_keys.items():
            if key not in config:
                # Languages is optional - auto-populate with defaults if missing
                if key == "languages":
                    continue
                errors.append(f"Missing required key: {key}")
            elif not isinstance(config[key], expected_type):
                errors.append(
                    f"Invalid type for {key}: expected {expected_type.__name__}"
                )

        # Validate multi-language configurations
        if "languages" in config:
            languages = config["languages"]
            supported_langs = ["cpp", "py", "java"]

            for lang in supported_langs:
                if lang not in languages:
                    continue  # Optional - will use defaults

                lang_config = languages[lang]
                if not isinstance(lang_config, dict):
                    errors.append(f"Invalid language config for {lang}: expected dict")
                    continue

                # Validate language-specific fields
                if lang == "cpp":
                    required_fields = {"compiler": str, "std_version": str}
                elif lang == "py":
                    required_fields = {"interpreter": str}
                elif lang == "java":
                    required_fields = {"compiler": str, "runtime": str}

                for field, field_type in required_fields.items():
                    if field in lang_config and not isinstance(
                        lang_config[field], field_type
                    ):
                        errors.append(
                            f"Invalid type for {lang}.{field}: expected {field_type.__name__}"
                        )

        if "gemini" in config:
            gemini_settings = config["gemini"]
            required_gemini_settings = {"enabled": bool, "api_key": str, "model": str}

            for key, expected_type in required_gemini_settings.items():
                if key not in gemini_settings:
                    errors.append(f"Missing Gemini setting: {key}")
                elif not isinstance(gemini_settings[key], expected_type):
                    errors.append(f"Invalid type for Gemini setting {key}")

            # Note: We don't require a valid API key, just the correct structure

        if "editor_settings" in config:
            editor_settings = config["editor_settings"]
            required_settings = {
                "autosave": bool,
                "autosave_interval": int,
                "tab_width": int,
                "font_size": int,
                "bracket_matching": bool,
            }

            for key, expected_type in required_settings.items():
                if key not in editor_settings:
                    errors.append(f"Missing editor setting: {key}")
                elif not isinstance(editor_settings[key], expected_type):
                    errors.append(f"Invalid type for editor setting {key}")

        # Check for truly missing keys (excluding optional 'languages')
        missing_keys = [
            k for k in required_keys if k not in config and k != "languages"
        ]
        if missing_keys:
            raise ConfigMissingError(f"Required keys: {', '.join(missing_keys)}")

        return errors

    def get_default_config(self):
        """Get default configuration structure."""
        return {
            "cpp_version": "c++17",  # Legacy field - kept for backward compatibility
            "languages": {  # Multi-language compiler configurations
                "cpp": {
                    "compiler": "g++",
                    "std_version": "c++17",
                    "optimization": "O2",
                    "flags": ["-march=native", "-mtune=native", "-pipe", "-Wall"],
                },
                "py": {
                    "interpreter": "python",
                    "version": "3",
                    "flags": ["-u"],  # Unbuffered output
                },
                "java": {
                    "compiler": "javac",
                    "version": "11",
                    "flags": [],
                    "runtime": "java",
                },
            },
            "gemini": {  # Standardized format (Phase 1)
                "enabled": False,
                "api_key": "",
                "model": "gemini-2.5-flash",  # Updated to 2.5 flash default
            },
            "editor_settings": {
                "autosave": True,
                "autosave_interval": 5,
                "tab_width": 4,
                "font_size": 12,
                "font_family": "Consolas",
                "bracket_matching": True,
            },
        }


class ConfigPersistence:
    """UI-specific configuration persistence - loading/saving from dialog."""

    def __init__(self, parent_dialog: ConfigDialogProtocol, config_manager: ConfigManager):
        self.parent = parent_dialog
        self.config_manager = config_manager
    
    def _get_combo_text(self, attr_name: str, default: str = "") -> str:
        """Safely get text from combo box attribute."""
        combo = getattr(self.parent, attr_name, None)
        return combo.currentText() if combo is not None else default
    
    def _set_combo_text(self, attr_name: str, value: str) -> None:
        """Safely set text in combo box attribute."""
        combo = getattr(self.parent, attr_name, None)
        if combo is not None:
            combo.setCurrentText(value)
    
    def _get_line_edit_text(self, attr_name: str, default: str = "") -> str:
        """Safely get text from line edit attribute."""
        edit = getattr(self.parent, attr_name, None)
        return edit.text() if edit is not None else default
    
    def _set_line_edit_text(self, attr_name: str, value: str) -> None:
        """Safely set text in line edit attribute."""
        edit = getattr(self.parent, attr_name, None)
        if edit is not None:
            edit.setText(value)
    
    def _get_spin_value(self, attr_name: str, default: int = 0) -> int:
        """Safely get value from spin box attribute."""
        spin = getattr(self.parent, attr_name, None)
        return spin.value() if spin is not None else default
    
    def _set_spin_value(self, attr_name: str, value: int) -> None:
        """Safely set value in spin box attribute."""
        spin = getattr(self.parent, attr_name, None)
        if spin is not None:
            spin.setValue(value)
    
    def _get_checkbox_checked(self, attr_name: str, default: bool = False) -> bool:
        """Safely get checked state from checkbox attribute."""
        checkbox = getattr(self.parent, attr_name, None)
        return checkbox.isChecked() if checkbox is not None else default
    
    def _set_checkbox_checked(self, attr_name: str, value: bool) -> None:
        """Safely set checked state in checkbox attribute."""
        checkbox = getattr(self.parent, attr_name, None)
        if checkbox is not None:
            checkbox.setChecked(value)

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
            except Exception:
                cfg = {}
        except Exception as e:
            self.parent.show_error(
                "Unexpected Error", "Failed to load configuration", str(e)
            )
            cfg = {}

        # Populate fields with safe defaults (use actual defaults from get_default_config)
        try:
            default_config = self.config_manager.get_default_config()
        except Exception:
            default_config = {}

        # Note: cpp_version_combo removed - C++ version now in Language Compilers section
        # Note: workspace_input removed - workspace is always ~/.code_testing_suite/workspace/

        # Load language-specific compiler flags
        languages = cfg.get("languages", default_config.get("languages", {}))

        # C++ configuration
        cpp_config = languages.get("cpp", {})
        self._set_combo_text("cpp_compiler_combo", cpp_config.get("compiler", "g++"))
        
        # Use languages.cpp.std_version as primary, cpp_version as fallback for backward compat
        std_version = cpp_config.get("std_version", cfg.get("cpp_version", "c++17"))
        self._set_combo_text("cpp_std_combo", std_version)
        
        self._set_combo_text("cpp_opt_combo", cpp_config.get("optimization", "O2"))
        
        cpp_flags = cpp_config.get("flags", [])
        cpp_flags_str = ", ".join(cpp_flags) if isinstance(cpp_flags, list) else str(cpp_flags)
        self._set_line_edit_text("cpp_flags_input", cpp_flags_str)

        # Python configuration
        py_config = languages.get("py", {})
        self._set_combo_text("py_interpreter_combo", py_config.get("interpreter", "python"))
        
        py_flags = py_config.get("flags", [])
        py_flags_str = ", ".join(py_flags) if isinstance(py_flags, list) else str(py_flags)
        self._set_line_edit_text("py_flags_input", py_flags_str)

        # Java configuration
        java_config = languages.get("java", {})
        self._set_combo_text("java_compiler_combo", java_config.get("compiler", "javac"))
        self._set_combo_text("java_runtime_combo", java_config.get("runtime", "java"))
        
        java_flags = java_config.get("flags", [])
        java_flags_str = ", ".join(java_flags) if isinstance(java_flags, list) else str(java_flags)
        self._set_line_edit_text("java_flags_input", java_flags_str)

        # Updated for new gemini format (Phase 1)
        gemini_settings = (
            cfg.get("gemini", {}) if isinstance(cfg.get("gemini"), dict) else {}
        )
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

        # Load preferred model to combo box
        if model:
            self._set_combo_text("model_combo", model)
        else:
            # Set default model if none configured
            default_model = "gemini-2.5-flash"
            self._set_combo_text("model_combo", default_model)

        # Backward compatibility for code that expects model_input
        self._set_line_edit_text("model_input", model)

        editor_settings = (
            cfg.get("editor_settings", {})
            if isinstance(cfg.get("editor_settings"), dict)
            else {}
        )
        
        # Load font family
        self._set_combo_text("font_family_combo", editor_settings.get("font_family", "Consolas"))
        
        # Load font size (required attribute)
        self.parent.font_size_spin.setValue(int(editor_settings.get("font_size", 12)))
        
        # Load tab width
        self._set_spin_value("tab_width_spin", int(editor_settings.get("tab_width", 4)))
        
        # Load line wrap (required attribute)
        self.parent.wrap_checkbox.setChecked(bool(editor_settings.get("wrap_lines", False)))
        
        # Load bracket matching
        self._set_checkbox_checked("bracket_match_checkbox", bool(editor_settings.get("bracket_matching", True)))
        
        # Load autosave settings
        autosave_enabled = bool(editor_settings.get("autosave", True))
        self._set_checkbox_checked("autosave_checkbox", autosave_enabled)
        
        autosave_interval = int(editor_settings.get("autosave_interval", 5))
        self._set_spin_value("autosave_interval_spin", autosave_interval)
        
        # Enable/disable autosave interval based on checkbox
        autosave_spin = getattr(self.parent, "autosave_interval_spin", None)
        if autosave_spin is not None:
            autosave_spin.setEnabled(self._get_checkbox_checked("autosave_checkbox", True))

    def save_config(self):
        """Save configuration to file from UI values."""
        try:
            # Load current config to preserve settings not in the UI
            try:
                current_config = self.config_manager.load_config()
            except (ConfigError, Exception) as e:
                logger.warning(f"Could not load current config, using defaults: {e}")
                current_config = self.config_manager.get_default_config()

            # Update with UI values using new gemini format (Phase 1)
            # Keep cpp_version for backward compatibility but use languages.cpp.std_version as primary
            cpp_std_version = self._get_combo_text(
                "cpp_std_combo",
                current_config.get("languages", {}).get("cpp", {}).get("std_version", "c++17")
            )

            # Helper to parse comma-separated flags
            def parse_flags(text: str) -> list:
                return [f.strip() for f in text.split(",") if f.strip()]
            
            config = {
                "cpp_version": cpp_std_version,  # Legacy field for backward compatibility
                "languages": {
                    "cpp": {
                        "compiler": self._get_combo_text(
                            "cpp_compiler_combo",
                            current_config.get("languages", {}).get("cpp", {}).get("compiler", "g++")
                        ),
                        "std_version": cpp_std_version,
                        "optimization": self._get_combo_text(
                            "cpp_opt_combo",
                            current_config.get("languages", {}).get("cpp", {}).get("optimization", "O2")
                        ),
                        "flags": parse_flags(
                            self._get_line_edit_text(
                                "cpp_flags_input",
                                ",".join(current_config.get("languages", {}).get("cpp", {}).get("flags", []))
                            )
                        ),
                    },
                    "py": {
                        "interpreter": self._get_combo_text(
                            "py_interpreter_combo",
                            current_config.get("languages", {}).get("py", {}).get("interpreter", "python")
                        ),
                        "version": current_config.get("languages", {}).get("py", {}).get("version", "3"),
                        "flags": parse_flags(
                            self._get_line_edit_text(
                                "py_flags_input",
                                ",".join(current_config.get("languages", {}).get("py", {}).get("flags", []))
                            )
                        ),
                    },
                    "java": {
                        "compiler": self._get_combo_text(
                            "java_compiler_combo",
                            current_config.get("languages", {}).get("java", {}).get("compiler", "javac")
                        ),
                        "version": current_config.get("languages", {}).get("java", {}).get("version", "11"),
                        "flags": parse_flags(
                            self._get_line_edit_text(
                                "java_flags_input",
                                ",".join(current_config.get("languages", {}).get("java", {}).get("flags", []))
                            )
                        ),
                        "runtime": self._get_combo_text(
                            "java_runtime_combo",
                            current_config.get("languages", {}).get("java", {}).get("runtime", "java")
                        ),
                    },
                },
                "gemini": {  # New standardized format
                    "enabled": self.parent.use_ai_checkbox.isChecked(),
                    "api_key": self.parent.key_input.text().strip(),
                    "model": self._get_combo_text(
                        "model_combo",
                        self._get_line_edit_text("model_input", "gemini-2.5-flash")
                    ).strip(),
                },
                "editor_settings": {
                    # Update with UI values
                    "autosave": self._get_checkbox_checked(
                        "autosave_checkbox",
                        current_config.get("editor_settings", {}).get("autosave", True)
                    ),
                    "autosave_interval": self._get_spin_value(
                        "autosave_interval_spin",
                        current_config.get("editor_settings", {}).get("autosave_interval", 5)
                    ),
                    "tab_width": self._get_spin_value(
                        "tab_width_spin",
                        current_config.get("editor_settings", {}).get("tab_width", 4)
                    ),
                    "font_family": self._get_combo_text(
                        "font_family_combo",
                        current_config.get("editor_settings", {}).get("font_family", "Consolas")
                    ),
                    "font_size": int(self.parent.font_size_spin.value()),
                    "bracket_matching": self._get_checkbox_checked(
                        "bracket_match_checkbox",
                        current_config.get("editor_settings", {}).get("bracket_matching", True)
                    ),
                    "wrap_lines": bool(self.parent.wrap_checkbox.isChecked()),
                },
            }
            self.config_manager.save_config(config)
            logger.info("Configuration saved successfully via UI")

            # Success message
            self.parent.show_success(
                "Configuration Saved", "Settings saved successfully!"
            )

        except ConfigError as e:
            logger.error(f"Configuration error while saving: {e}")
            self.parent.show_error("Configuration Error", str(e))
        except (IOError, OSError, PermissionError) as e:
            logger.error(f"File error while saving config: {e}")
            self.parent.show_error("Save Error", "Failed to save configuration", str(e))
        except Exception as e:
            logger.exception(f"Unexpected error while saving config: {e}")
            self.parent.show_error("Save Error", "Failed to save configuration", str(e))

    def reset_to_defaults(self):
        """Reset configuration to defaults."""
        error_service = ErrorHandlerService.instance()
        reply = error_service.ask_question(
            "Confirm Reset",
            "Are you sure you want to reset all settings to defaults?\n\nThis action cannot be undone.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
            self.parent
        )
        if reply == QMessageBox.Yes:
            try:
                logger.info("Resetting configuration to defaults")
                default_config = self.config_manager.get_default_config()
                self.config_manager.save_config(default_config)

                # Reload UI with defaults
                self.load_config()
                
                logger.info("Configuration reset completed successfully")
                # Show success
                self.parent.show_success(
                    "Reset Complete", "Configuration reset to defaults."
                )

            except ConfigError as e:
                logger.error(f"Configuration error during reset: {e}")
                self.parent.show_error("Reset Error", "Failed to reset configuration", str(e))
            except (IOError, OSError, PermissionError) as e:
                logger.error(f"File error during reset: {e}")
                self.parent.show_error("Reset Error", "Failed to reset configuration", str(e))
            except Exception as e:
                logger.exception(f"Unexpected error during reset: {e}")
                self.parent.show_error("Reset Error", "Failed to reset configuration", str(e))

    def show_success(self, title, message):
        """Show success message to user."""
        error_service = ErrorHandlerService.instance()
        error_service.show_success(title, message, self.parent)
