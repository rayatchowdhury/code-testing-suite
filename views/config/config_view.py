from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QMessageBox, QScrollArea, QWidget,
    QLabel, QComboBox, QLineEdit, QSpinBox, QCheckBox, QPushButton, QFileDialog,
    QFrame
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QIcon
import os

from .config_manager import ConfigManager
from .config_exceptions import ConfigError
from .error_dialog import ErrorDialog
from .styles import CONFIG_DIALOG_STYLE
from styles.constants.colors import MATERIAL_COLORS
from utils.api_validator import APIValidator
from constants import SETTINGS_ICON


class ConfigView(QDialog):
    """Configuration dialog following original app design language."""

    configSaved = Signal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)

        # Window setup matching original app dialogs
        if os.path.exists(SETTINGS_ICON):
            self.setWindowIcon(QIcon(SETTINGS_ICON))

        self.setWindowTitle("⚙️ Configuration")
        self.setFixedSize(700, 750)  # Original app sizing
        self.setWindowFlags(Qt.Dialog | Qt.WindowCloseButtonHint)

        # Apply original styling
        self.setStyleSheet(CONFIG_DIALOG_STYLE)

        # Shared resources
        self.config_manager = ConfigManager()
        
        # Validation state
        self.validation_thread = None
        self.is_key_valid = False

        self.setup_ui()
        self.load_config()

    def setup_ui(self):
        """Setup UI using original app patterns"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(24, 24, 24, 24)
        main_layout.setSpacing(0)

        # Title section
        title_section = QLabel("⚙️ Configurations")
        title_section.setStyleSheet(f"""
            font-size: 18px; 
            color: {MATERIAL_COLORS['primary']}; 
            font-weight: 600;
            font-family: 'Segoe UI', system-ui;
            margin: 8px 0;
            text-align: center;
        """)
        title_section.setFixedHeight(35)
        title_section.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_section)

        # Create scroll area for content
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setFrameShape(QScrollArea.NoFrame)

        # Scrollable content widget
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setSpacing(20)
        content_layout.setContentsMargins(0, 0, 20, 20)

        # Create sections using original patterns
        content_layout.addWidget(self.create_cpp_section())
        content_layout.addWidget(self.create_workspace_section())
        content_layout.addWidget(self.create_ai_section())
        content_layout.addWidget(self.create_editor_section())
        
        # Add stretch to push content to top
        content_layout.addStretch(1)

        # Set content to scroll area
        scroll_area.setWidget(content_widget)

        # Button container
        button_container = QWidget()
        button_container.setObjectName("button_container")
        button_container.setFixedHeight(72)
        
        button_layout = QHBoxLayout(button_container)
        button_layout.setContentsMargins(24, 18, 24, 18)
        button_layout.setSpacing(12)

        # Buttons
        self.reset_btn = QPushButton("Reset to Defaults")
        self.reset_btn.setObjectName("reset_button")
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.setObjectName("cancel_button")
        self.save_btn = QPushButton("Save Configuration")
        self.save_btn.setObjectName("save_button")

        button_layout.addStretch(1)
        button_layout.addWidget(self.reset_btn)
        button_layout.addWidget(self.cancel_btn)
        button_layout.addWidget(self.save_btn)

        # Add to main layout
        main_layout.addWidget(scroll_area, 1)
        main_layout.addWidget(button_container, 0)

        # Connect signals
        self.save_btn.clicked.connect(self.save_config)
        self.reset_btn.clicked.connect(self.reset_to_defaults)
        self.cancel_btn.clicked.connect(self.reject)

    def create_section_frame(self, title_text):
        """Create section frame using original app patterns"""
        frame = QFrame()
        frame.setObjectName("section_frame")
        
        layout = QVBoxLayout(frame)
        layout.setSpacing(8)
        layout.setContentsMargins(0, 0, 0, 8)

        title = QLabel(title_text)
        title.setObjectName("section_title")
        layout.addWidget(title)

        content = QWidget()
        content.setObjectName("section_content")
        content_layout = QVBoxLayout(content)
        content_layout.setSpacing(12)
        content_layout.setContentsMargins(12, 8, 12, 12)
        layout.addWidget(content)

        return frame, content_layout

    def create_cpp_section(self):
        """Create C++ configuration section"""
        frame, layout = self.create_section_frame("🔧 C++ Version")

        # C++ Version selector row
        cpp_widget = QWidget()
        cpp_layout = QHBoxLayout(cpp_widget)
        cpp_layout.setContentsMargins(0, 0, 0, 0)
        cpp_layout.setSpacing(8)

        cpp_label = QLabel("Default C++ standard:")
        cpp_label.setFixedWidth(120)
        cpp_layout.addWidget(cpp_label)

        self.cpp_version_combo = QComboBox()
        self.cpp_version_combo.addItems(["auto", "c++11", "c++14", "c++17", "c++20", "c++23"])
        self.cpp_version_combo.setFixedHeight(28)
        cpp_layout.addWidget(self.cpp_version_combo)
        
        layout.addWidget(cpp_widget)
        return frame

    def create_workspace_section(self):
        """Create workspace configuration section"""
        frame, layout = self.create_section_frame("📁 Workspace")

        # Workspace folder row
        ws_widget = QWidget()
        ws_layout = QHBoxLayout(ws_widget)
        ws_layout.setContentsMargins(0, 0, 0, 0)
        ws_layout.setSpacing(8)

        ws_label = QLabel("Workspace folder:")
        ws_label.setFixedWidth(120)
        ws_layout.addWidget(ws_label)
        
        self.workspace_input = QLineEdit()
        self.workspace_input.setPlaceholderText("Select workspace folder...")
        self.workspace_input.setFixedHeight(28)
        ws_layout.addWidget(self.workspace_input)
        
        browse_btn = QPushButton("Browse")
        browse_btn.setObjectName("small_button")
        browse_btn.setFixedSize(80, 28)
        browse_btn.clicked.connect(self.browse_workspace)
        ws_layout.addWidget(browse_btn)
        
        layout.addWidget(ws_widget)
        return frame

    def create_ai_section(self):
        """Create AI configuration section with proper controls"""
        frame, layout = self.create_section_frame("🤖 AI Assistant")

        # AI Panel checkbox
        self.use_ai_checkbox = QCheckBox("Enable AI Panel")
        self.use_ai_checkbox.setToolTip("Enable AI-powered code assistance features")
        self.use_ai_checkbox.stateChanged.connect(self.on_ai_toggle)
        layout.addWidget(self.use_ai_checkbox)

        # API Key section
        api_key_widget = QWidget()
        api_key_layout = QHBoxLayout(api_key_widget)
        api_key_layout.setContentsMargins(0, 0, 0, 0)
        api_key_layout.setSpacing(8)

        # API Key label
        api_label = QLabel("Gemini API Key:")
        api_label.setFixedWidth(120)
        api_key_layout.addWidget(api_label)

        # API Key input
        self.key_input = QLineEdit()
        self.key_input.setEchoMode(QLineEdit.Password)
        self.key_input.setPlaceholderText("Enter your Gemini API key...")
        self.key_input.setFixedHeight(28)
        self.key_input.textChanged.connect(self.on_key_changed)
        api_key_layout.addWidget(self.key_input)
        
        # Toggle visibility button
        self.toggle_btn = QPushButton("👁")
        self.toggle_btn.setObjectName("small_button")
        self.toggle_btn.setFixedSize(32, 32)
        self.toggle_btn.clicked.connect(self.toggle_visibility)
        self.toggle_btn.setToolTip("Show/Hide API key")
        api_key_layout.addWidget(self.toggle_btn)
        
        # Validate button
        self.validate_btn = QPushButton("🔄")
        self.validate_btn.setObjectName("small_button")
        self.validate_btn.setFixedSize(32, 32)
        self.validate_btn.clicked.connect(self.force_validation)
        self.validate_btn.setToolTip("Re-validate API key")
        api_key_layout.addWidget(self.validate_btn)
        
        # Validation indicator
        self.status_label = QLabel()
        self.status_label.setFixedWidth(20)
        api_key_layout.addWidget(self.status_label)

        layout.addWidget(api_key_widget)

        # Info label
        info_label = QLabel("💡 Enable AI Panel to access code assistance features. Valid API key required.")
        info_label.setStyleSheet(f"color: {MATERIAL_COLORS['on_surface_variant']}; font-size: 12px;")
        info_label.setWordWrap(True)
        layout.addWidget(info_label)

        # Store the API key widget for enabling/disabling
        self.api_key_widget = api_key_widget
        self.api_key_widget.setEnabled(True)

        return frame

    def create_editor_section(self):
        """Create editor configuration section"""
        frame, layout = self.create_section_frame("📝 Editor Settings")

        # Font size
        font_widget = QWidget()
        font_layout = QHBoxLayout(font_widget)
        font_layout.setContentsMargins(0, 0, 0, 0)
        font_layout.setSpacing(8)

        font_label = QLabel("Editor font size:")
        font_label.setFixedWidth(120)
        font_layout.addWidget(font_label)
        
        self.font_size_spin = QSpinBox()
        self.font_size_spin.setRange(8, 28)
        self.font_size_spin.setValue(13)
        self.font_size_spin.setFixedHeight(28)
        font_layout.addWidget(self.font_size_spin)
        font_layout.addStretch(1)
        
        layout.addWidget(font_widget)

        # Line wrap
        self.wrap_checkbox = QCheckBox("Enable line wrap")
        layout.addWidget(self.wrap_checkbox)
        
        return frame

    # AI validation methods
    def on_ai_toggle(self, state):
        """Handle AI checkbox toggle with proper validation"""
        if state == 2:  # User wants to enable AI
            if not self.is_key_valid:
                dialog = ErrorDialog(
                    "Valid API Key Required",
                    "Please enter and validate a Gemini API key before enabling the AI Panel.",
                    "The API key will be tested against Google's servers to ensure it works properly.",
                    self
                )
                dialog.exec()
                
                self.use_ai_checkbox.blockSignals(True)
                self.use_ai_checkbox.setChecked(False)
                self.use_ai_checkbox.blockSignals(False)
                return
        
        if state != 2:
            self.status_label.clear()

    def on_key_changed(self, text):
        """Handle API key text changes"""
        if self.validation_thread and self.validation_thread.isRunning():
            self.validation_thread.terminate()
            self.validation_thread = None
        
        self.is_key_valid = False
        self.use_ai_checkbox.setEnabled(False)
        if self.use_ai_checkbox.isChecked():
            self.use_ai_checkbox.blockSignals(True)
            self.use_ai_checkbox.setChecked(False)
            self.use_ai_checkbox.blockSignals(False)
        
        if not text.strip():
            self.status_label.clear()
            return
        
        format_ok, format_msg = APIValidator.quick_format_check(text)
        if not format_ok:
            self.status_label.setText("⚠")
            self.status_label.setStyleSheet(f"color: {MATERIAL_COLORS['error']}")
            self.status_label.setToolTip(format_msg)
            return
        
        self.status_label.setText("⏳")
        self.status_label.setStyleSheet(f"color: {MATERIAL_COLORS['on_surface_variant']}")
        self.status_label.setToolTip("Validating...")
        
        # Start validation using APIValidator
        self.validation_thread = APIValidator.validate_key_async(text, self.on_validation_complete)

    def on_validation_complete(self, is_valid, message):
        """Handle API validation completion"""
        self.is_key_valid = is_valid
        
        if is_valid:
            self.status_label.setText("✓")
            self.status_label.setStyleSheet(f"color: {MATERIAL_COLORS['primary']}")
            self.status_label.setToolTip("API key validated successfully")
            self.use_ai_checkbox.setEnabled(True)
        else:
            self.status_label.setText("✗")
            self.status_label.setStyleSheet(f"color: {MATERIAL_COLORS['error']}")
            self.status_label.setToolTip(f"Validation failed: {message}")
            self.use_ai_checkbox.setEnabled(False)
            if self.use_ai_checkbox.isChecked():
                self.use_ai_checkbox.blockSignals(True)
                self.use_ai_checkbox.setChecked(False)
                self.use_ai_checkbox.blockSignals(False)

    def toggle_visibility(self):
        """Toggle API key visibility"""
        is_hidden = self.key_input.echoMode() == QLineEdit.Password
        self.key_input.setEchoMode(QLineEdit.Normal if is_hidden else QLineEdit.Password)
        self.toggle_btn.setText("🔒" if is_hidden else "👁")

    def force_validation(self):
        """Force re-validation of the current API key"""
        current_key = self.key_input.text().strip()
        if current_key:
            self.on_key_changed(current_key)

    def browse_workspace(self):
        """Browse for workspace folder"""
        path = QFileDialog.getExistingDirectory(self, "Select workspace folder")
        if path:
            self.workspace_input.setText(path)

    # Config persistence
    def load_config(self):
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
            self.show_error("Unexpected Error", "Failed to load configuration", str(e))
            cfg = {}

        # Populate fields with safe defaults
        self.cpp_version_combo.setCurrentText(cfg.get("cpp_version", "auto"))
        self.workspace_input.setText(cfg.get("workspace_folder", ""))
        
        ai_settings = cfg.get("ai_settings", {}) if isinstance(cfg.get("ai_settings"), dict) else {}
        use_ai = ai_settings.get("use_ai_panel", False)
        api_key = ai_settings.get("gemini_api_key", "")
        
        # Load API key first
        if api_key:
            self.key_input.setText(api_key)
            # Assume previously validated keys are still valid
            self.is_key_valid = True
            self.status_label.setText("✓")
            self.status_label.setStyleSheet(f"color: {MATERIAL_COLORS['primary']}")
            self.status_label.setToolTip("Previously validated API key")
            self.use_ai_checkbox.setEnabled(True)
        else:
            self.use_ai_checkbox.setEnabled(False)
            self.is_key_valid = False
            use_ai = False
        
        self.use_ai_checkbox.setChecked(use_ai)
        
        editor_settings = cfg.get("editor_settings", {}) if isinstance(cfg.get("editor_settings"), dict) else {}
        self.font_size_spin.setValue(int(editor_settings.get("font_size", 13)))
        self.wrap_checkbox.setChecked(bool(editor_settings.get("wrap_lines", False)))

    def save_config(self):
        try:
            # Load current config to preserve settings not in the UI
            try:
                current_config = self.config_manager.load_config()
            except:
                current_config = self.config_manager.get_default_config()
            
            # Update with UI values while preserving other settings
            config = {
                "cpp_version": self.cpp_version_combo.currentText(),
                "workspace_folder": self.workspace_input.text().strip(),
                "ai_settings": {
                    "use_ai_panel": self.use_ai_checkbox.isChecked(),
                    "gemini_api_key": self.key_input.text().strip()
                },
                "editor_settings": {
                    # Preserve existing settings not shown in UI
                    "autosave": current_config.get("editor_settings", {}).get("autosave", True),
                    "autosave_interval": current_config.get("editor_settings", {}).get("autosave_interval", 5),
                    "tab_width": current_config.get("editor_settings", {}).get("tab_width", 4),
                    "font_family": current_config.get("editor_settings", {}).get("font_family", "Consolas"),
                    "bracket_matching": current_config.get("editor_settings", {}).get("bracket_matching", True),
                    # Update with UI values
                    "font_size": int(self.font_size_spin.value()),
                    "wrap_lines": bool(self.wrap_checkbox.isChecked())
                }
            }
            self.config_manager.save_config(config)
            self.configSaved.emit(config)

            # Show success message
            success_msg = QMessageBox(self)
            success_msg.setIcon(QMessageBox.Information)
            success_msg.setWindowTitle("Success")
            success_msg.setText("Configuration saved successfully!")
            success_msg.setStyleSheet("""
                QMessageBox {
                    background: #1e1e1e;
                    color: white;
                }
                QMessageBox QPushButton {
                    background: #0096C7;
                    color: white;
                    border: none;
                    padding: 8px 16px;
                    border-radius: 6px;
                    font-weight: 600;
                }
                QMessageBox QPushButton:hover {
                    background: #023E8A;
                }
            """)
            success_msg.exec()
            
            self.accept()

        except ConfigError as e:
            self.show_error("Configuration Error", str(e))
        except Exception as e:
            self.show_error("Unexpected Error", "Failed to save configuration", str(e))

    def reset_to_defaults(self):
        reply = QMessageBox.question(
            self,
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
                info_msg = QMessageBox(self)
                info_msg.setIcon(QMessageBox.Information)
                info_msg.setWindowTitle("Reset Complete")
                info_msg.setText("All settings have been reset to defaults.")
                info_msg.setStyleSheet("""
                    QMessageBox {
                        background: #1e1e1e;
                        color: white;
                    }
                    QMessageBox QPushButton {
                        background: #0096C7;
                        color: white;
                        border: none;
                        padding: 8px 16px;
                        border-radius: 6px;
                        font-weight: 600;
                    }
                    QMessageBox QPushButton:hover {
                        background: #023E8A;
                    }
                """)
                info_msg.exec()
                
            except Exception as e:
                self.show_error("Reset Error", "Failed to reset settings", str(e))

    def show_error(self, title, message, details=None):
        dialog = ErrorDialog(title, message, details, self)
        dialog.exec()
