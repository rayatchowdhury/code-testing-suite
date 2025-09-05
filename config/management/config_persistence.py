"""Configuration persistence for the configuration dialog."""

from PySide6.QtWidgets import QMessageBox

from ..config_exceptions import ConfigError
from styles.constants.colors import MATERIAL_COLORS
from styles.components.config_ui import (
    SUCCESS_MESSAGE_STYLE, 
    INFO_MESSAGE_STYLE,
    get_success_status_style
)


class ConfigPersistence:
    """Handles configuration loading and saving for the configuration dialog."""
    
    def __init__(self, parent_dialog, config_manager):
        self.parent = parent_dialog
        self.config_manager = config_manager
        
    def load_config(self):
        """Load configuration from file and populate UI fields"""
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
        
        ai_settings = cfg.get("ai_settings", {}) if isinstance(cfg.get("ai_settings"), dict) else {}
        use_ai = ai_settings.get("use_ai_panel", False)
        api_key = ai_settings.get("gemini_api_key", "")
        preferred_model = ai_settings.get("preferred_model", "")
        
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
            use_ai = False
        
        self.parent.use_ai_checkbox.setChecked(use_ai)
        
        # Load preferred model
        self.parent.model_input.setText(preferred_model)
        
        editor_settings = cfg.get("editor_settings", {}) if isinstance(cfg.get("editor_settings"), dict) else {}
        self.parent.font_size_spin.setValue(int(editor_settings.get("font_size", 13)))
        self.parent.wrap_checkbox.setChecked(bool(editor_settings.get("wrap_lines", False)))

    def save_config(self):
        """Save configuration to file"""
        try:
            # Load current config to preserve settings not in the UI
            try:
                current_config = self.config_manager.load_config()
            except:
                current_config = self.config_manager.get_default_config()
            
            # Update with UI values while preserving other settings
            config = {
                "cpp_version": self.parent.cpp_version_combo.currentText(),
                "workspace_folder": self.parent.workspace_input.text().strip(),
                "ai_settings": {
                    "use_ai_panel": self.parent.use_ai_checkbox.isChecked(),
                    "gemini_api_key": self.parent.key_input.text().strip(),
                    "preferred_model": self.parent.model_input.text().strip()
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
            self.parent.configSaved.emit(config)

            # Show success message
            success_msg = QMessageBox(self.parent)
            success_msg.setIcon(QMessageBox.Information)
            success_msg.setWindowTitle("Success")
            success_msg.setText("Configuration saved successfully!")
            success_msg.setStyleSheet(SUCCESS_MESSAGE_STYLE)
            success_msg.exec()
            
            self.parent.accept()

        except ConfigError as e:
            self.parent.show_error("Configuration Error", str(e))
        except Exception as e:
            self.parent.show_error("Unexpected Error", "Failed to save configuration", str(e))

    def reset_to_defaults(self):
        """Reset configuration to defaults"""
        reply = QMessageBox.question(
            self.parent,
            "Confirm Reset",
            "Are you sure you want to reset all settings to defaults?\n\nThis action cannot be undone.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if reply == QMessageBox.Yes:
            try:
                default_cfg = self.config_manager.get_default_config()
                self.config_manager.save_config(default_cfg)
                self.load_config()
                
                # Show success message
                info_msg = QMessageBox(self.parent)
                info_msg.setIcon(QMessageBox.Information)
                info_msg.setWindowTitle("Reset Complete")
                info_msg.setText("All settings have been reset to defaults.")
                info_msg.setStyleSheet(INFO_MESSAGE_STYLE)
                info_msg.exec()
                
            except Exception as e:
                self.parent.show_error("Reset Error", "Failed to reset settings", str(e))
