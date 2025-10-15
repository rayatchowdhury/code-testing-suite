"""Consolidated configuration handler combining management and persistence."""

import json
import os
from typing import Dict

from PySide6.QtWidgets import QMessageBox

from src.app.core.config.core.exceptions import (
    ConfigError,
    ConfigFormatError,
    ConfigLoadError,
    ConfigMissingError,
    ConfigPermissionError,
    ConfigSaveError,
    ConfigValidationError,
)
from src.app.presentation.styles.components.config_ui import get_success_status_style
from src.app.shared.constants import USER_DATA_DIR


class ConfigManager:
    """Core configuration management - loading, saving, validation."""

    CONFIG_DIR = USER_DATA_DIR

    def __init__(self, config_file="config.json"):
        # If config_file is an absolute path, use it directly
        # Otherwise, treat it as a filename under CONFIG_DIR
        if os.path.isabs(config_file):
            self.config_file = config_file
        else:
            self.config_file = os.path.join(self.CONFIG_DIR, config_file)

    def load_config(self):
        """Load configuration from JSON file with validation."""
        try:
            if not os.path.exists(self.config_file):
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
                raise ConfigValidationError(
                    "configuration structure",
                    "Invalid configuration format",
                    "\n".join(validation_errors),
                )

            return config

        except ConfigError:
            raise
        except Exception as e:
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
                except Exception:
                    pass  # Ignore backup failures

            with open(self.config_file, "w") as f:
                json.dump(config, f, indent=4)

        except Exception as e:
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
                errors.append(f"Invalid type for {key}: expected {expected_type.__name__}")

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
                    if field in lang_config and not isinstance(lang_config[field], field_type):
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
        missing_keys = [k for k in required_keys if k not in config and k != "languages"]
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
            except Exception:
                cfg = {}
        except Exception as e:
            self.parent.show_error("Unexpected Error", "Failed to load configuration", str(e))
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
        if hasattr(self.parent, "cpp_compiler_combo"):
            self.parent.cpp_compiler_combo.setCurrentText(cpp_config.get("compiler", "g++"))
        if hasattr(self.parent, "cpp_std_combo"):
            # Use languages.cpp.std_version as primary, cpp_version as fallback for backward compat
            std_version = cpp_config.get("std_version", cfg.get("cpp_version", "c++17"))
            self.parent.cpp_std_combo.setCurrentText(std_version)
        if hasattr(self.parent, "cpp_opt_combo"):
            self.parent.cpp_opt_combo.setCurrentText(cpp_config.get("optimization", "O2"))
        cpp_flags = cpp_config.get("flags", [])
        if hasattr(self.parent, "cpp_flags_input"):
            self.parent.cpp_flags_input.setText(
                ", ".join(cpp_flags) if isinstance(cpp_flags, list) else str(cpp_flags)
            )

        # Python configuration
        py_config = languages.get("py", {})
        if hasattr(self.parent, "py_interpreter_combo"):
            self.parent.py_interpreter_combo.setCurrentText(py_config.get("interpreter", "python"))
        py_flags = py_config.get("flags", [])
        if hasattr(self.parent, "py_flags_input"):
            self.parent.py_flags_input.setText(
                ", ".join(py_flags) if isinstance(py_flags, list) else str(py_flags)
            )

        # Java configuration
        java_config = languages.get("java", {})
        if hasattr(self.parent, "java_compiler_combo"):
            self.parent.java_compiler_combo.setCurrentText(java_config.get("compiler", "javac"))
        if hasattr(self.parent, "java_runtime_combo"):
            self.parent.java_runtime_combo.setCurrentText(java_config.get("runtime", "java"))
        java_flags = java_config.get("flags", [])
        if hasattr(self.parent, "java_flags_input"):
            self.parent.java_flags_input.setText(
                ", ".join(java_flags) if isinstance(java_flags, list) else str(java_flags)
            )

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

        # Load preferred model to combo box
        if model and hasattr(self.parent, "model_combo"):
            self.parent.model_combo.setCurrentText(model)
        elif hasattr(self.parent, "model_combo"):
            # Set default model if none configured
            default_model = "gemini-2.5-flash"
            self.parent.model_combo.setCurrentText(default_model)

        # Backward compatibility for code that expects model_input
        if hasattr(self.parent, "model_input"):
            self.parent.model_input.setText(model)

        editor_settings = (
            cfg.get("editor_settings", {}) if isinstance(cfg.get("editor_settings"), dict) else {}
        )
        self.parent.font_size_spin.setValue(int(editor_settings.get("font_size", 13)))
        self.parent.wrap_checkbox.setChecked(bool(editor_settings.get("wrap_lines", False)))

    def save_config(self):
        """Save configuration to file from UI values."""
        try:
            # Load current config to preserve settings not in the UI
            try:
                current_config = self.config_manager.load_config()
            except Exception:
                current_config = self.config_manager.get_default_config()

            # Update with UI values using new gemini format (Phase 1)
            # Keep cpp_version for backward compatibility but use languages.cpp.std_version as primary
            cpp_std_version = (
                self.parent.cpp_std_combo.currentText()
                if hasattr(self.parent, "cpp_std_combo")
                else current_config.get("languages", {}).get("cpp", {}).get("std_version", "c++17")
            )

            config = {
                "cpp_version": cpp_std_version,  # Legacy field for backward compatibility
                "languages": {
                    "cpp": {
                        "compiler": (
                            self.parent.cpp_compiler_combo.currentText()
                            if hasattr(self.parent, "cpp_compiler_combo")
                            else current_config.get("languages", {})
                            .get("cpp", {})
                            .get("compiler", "g++")
                        ),
                        "std_version": cpp_std_version,
                        "optimization": (
                            self.parent.cpp_opt_combo.currentText()
                            if hasattr(self.parent, "cpp_opt_combo")
                            else current_config.get("languages", {})
                            .get("cpp", {})
                            .get("optimization", "O2")
                        ),
                        "flags": (
                            [
                                f.strip()
                                for f in self.parent.cpp_flags_input.text().split(",")
                                if f.strip()
                            ]
                            if hasattr(self.parent, "cpp_flags_input")
                            else current_config.get("languages", {}).get("cpp", {}).get("flags", [])
                        ),
                    },
                    "py": {
                        "interpreter": (
                            self.parent.py_interpreter_combo.currentText()
                            if hasattr(self.parent, "py_interpreter_combo")
                            else current_config.get("languages", {})
                            .get("py", {})
                            .get("interpreter", "python")
                        ),
                        "version": current_config.get("languages", {})
                        .get("py", {})
                        .get("version", "3"),
                        "flags": (
                            [
                                f.strip()
                                for f in self.parent.py_flags_input.text().split(",")
                                if f.strip()
                            ]
                            if hasattr(self.parent, "py_flags_input")
                            else current_config.get("languages", {}).get("py", {}).get("flags", [])
                        ),
                    },
                    "java": {
                        "compiler": (
                            self.parent.java_compiler_combo.currentText()
                            if hasattr(self.parent, "java_compiler_combo")
                            else current_config.get("languages", {})
                            .get("java", {})
                            .get("compiler", "javac")
                        ),
                        "version": current_config.get("languages", {})
                        .get("java", {})
                        .get("version", "11"),
                        "flags": (
                            [
                                f.strip()
                                for f in self.parent.java_flags_input.text().split(",")
                                if f.strip()
                            ]
                            if hasattr(self.parent, "java_flags_input")
                            else current_config.get("languages", {})
                            .get("java", {})
                            .get("flags", [])
                        ),
                        "runtime": (
                            self.parent.java_runtime_combo.currentText()
                            if hasattr(self.parent, "java_runtime_combo")
                            else current_config.get("languages", {})
                            .get("java", {})
                            .get("runtime", "java")
                        ),
                    },
                },
                "gemini": {  # New standardized format
                    "enabled": self.parent.use_ai_checkbox.isChecked(),
                    "api_key": self.parent.key_input.text().strip(),
                    "model": (
                        self.parent.model_combo.currentText().strip()
                        if hasattr(self.parent, "model_combo")
                        else self.parent.model_input.text().strip()
                    ),
                },
                "editor_settings": {
                    # Preserve existing settings not shown in UI
                    "autosave": current_config.get("editor_settings", {}).get("autosave", True),
                    "autosave_interval": current_config.get("editor_settings", {}).get(
                        "autosave_interval", 5
                    ),
                    "tab_width": current_config.get("editor_settings", {}).get("tab_width", 4),
                    "font_family": current_config.get("editor_settings", {}).get(
                        "font_family", "Consolas"
                    ),
                    "bracket_matching": current_config.get("editor_settings", {}).get(
                        "bracket_matching", True
                    ),
                    # Update with UI values
                    "font_size": int(self.parent.font_size_spin.value()),
                    "wrap_lines": bool(self.parent.wrap_checkbox.isChecked()),
                },
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
