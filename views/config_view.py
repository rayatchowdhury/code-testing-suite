from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                              QComboBox, QLineEdit, QCheckBox, QSpinBox,
                              QPushButton, QFileDialog, QFrame, QWidget, QSlider,
                              QMessageBox)  # Add QMessageBox
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QIcon, QFont
import json
import os


class ConfigError(Exception):
    """Base exception for configuration errors"""
    pass

class ConfigLoadError(ConfigError):
    """Error loading configuration"""
    pass

class ConfigSaveError(ConfigError):
    """Error saving configuration"""
    pass

class ConfigView(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Configurations")
        self.setWindowIcon(QIcon("resources/icons/settings.png"))
        self.setFixedSize(600, 700)  # Fixed size to prevent layout issues
        self.setWindowFlags(Qt.Dialog | Qt.WindowCloseButtonHint)
        self.setStyleSheet("""
            QDialog {
                background-color: #1e1e1e;
                color: #e0e0e0;
            }
            QLabel {
                color: #e0e0e0;
            }
            QComboBox, QLineEdit, QSpinBox {
                background-color: #2d2d2d;
                border: 1px solid #3d3d3d;
                border-radius: 4px;
                color: #e0e0e0;
                padding: 5px;
                min-height: 25px;
            }
            QComboBox:hover, QLineEdit:hover, QSpinBox:hover {
                border: 1px solid #0096C7;
            }
            QComboBox::drop-down {
                border: none;
                padding-right: 10px;
            }
            QPushButton {
                background-color: #2d2d2d;
                border: 1px solid #3d3d3d;
                border-radius: 4px;
                color: #e0e0e0;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background-color: #3d3d3d;
                border: 1px solid #0096C7;
            }
            QPushButton#save_button {
                background-color: #0096C7;
                border: none;
            }
            QPushButton#save_button:hover {
                background-color: #00b4d8;
            }
            QCheckBox {
                color: #e0e0e0;
                spacing: 8px;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border-radius: 3px;
                border: 1px solid #3d3d3d;
            }
            QCheckBox::indicator:unchecked {
                background-color: #2d2d2d;
            }
            QCheckBox::indicator:checked {
                background-color: #0096C7;
            }
            QFrame#section_frame {
                background-color: #2d2d2d;
                border-radius: 8px;
                padding: 0px;
                margin: 0px;
            }
            QLabel#section_title {
                color: #58a6ff;
                font-size: 14px;
                font-weight: bold;
                padding: 10px;
                background-color: #252525;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                border-bottom: 1px solid #333;
            }
            QWidget#section_content {
                padding: 15px;
            }
            /* Additional styles for editor settings */
            QGroupBox {
                border: 1px solid #3d3d3d;
                border-radius: 4px;
                margin-top: 12px;
                background-color: #252525;
            }
            QGroupBox::title {
                color: #58a6ff;
                padding: 0 8px;
                background-color: #252525;
            }
            .setting-label {
                color: #e0e0e0;
                font-size: 13px;
            }
            QSlider::groove:horizontal {
                border: 1px solid #3d3d3d;
                height: 8px;
                background: #2d2d2d;
                margin: 2px 0;
                border-radius: 4px;
            }
            QSlider::handle:horizontal {
                background: #0096C7;
                border: none;
                width: 18px;
                margin: -6px 0;
                border-radius: 9px;
            }
            QSlider::handle:horizontal:hover {
                background: #00b4d8;
            }
        """)
        self.config_file = 'config.json'
        self.setup_ui()
        self.load_config()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        # Title
        title = QLabel("⚙️ Configurations")
        title.setStyleSheet(
            "font-size: 24px; color: #58a6ff; font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(title)

        # CPP Version
        cpp_frame, cpp_layout = self.create_section("🔧 C++ Version")
        self.cpp_version = QComboBox()
        self.cpp_version.addItems(
            ["c++11", "c++14", "c++17", "c++20", "c++23"])
        cpp_layout.addWidget(self.cpp_version)
        layout.addWidget(cpp_frame)

        # Workspace
        workspace_frame, workspace_layout = self.create_section(
            "📁 Workspace Folder")
        path_layout = QHBoxLayout()
        self.workspace_path = QLineEdit()
        self.workspace_path.setReadOnly(True)
        self.workspace_path.setPlaceholderText("Select workspace folder...")
        browse_btn = QPushButton("Browse")
        browse_btn.setFixedWidth(80)
        browse_btn.clicked.connect(self.select_workspace)
        path_layout.addWidget(self.workspace_path)
        path_layout.addWidget(browse_btn)
        workspace_layout.addLayout(path_layout)
        layout.addWidget(workspace_frame)

        # API Key
        api_frame, api_layout = self.create_section("🔑 Gemini API Key")
        key_layout = QHBoxLayout()
        self.api_key = QLineEdit()
        self.api_key.setEchoMode(QLineEdit.Password)
        self.api_key.setPlaceholderText("Enter your API key...")
        toggle_btn = QPushButton("👁")
        toggle_btn.setFixedWidth(40)
        toggle_btn.clicked.connect(
            lambda: self.toggle_password_visibility(self.api_key))
        key_layout.addWidget(self.api_key)
        key_layout.addWidget(toggle_btn)
        api_layout.addLayout(key_layout)
        layout.addWidget(api_frame)

        # Editor Settings - Enhanced
        editor_frame, editor_layout = self.create_section("📝 Editor Settings")
        editor_layout.setSpacing(15)  # Increase spacing between settings

        # Auto-save settings
        autosave_group = QFrame()
        autosave_layout = QHBoxLayout(autosave_group)
        autosave_layout.setContentsMargins(0, 0, 0, 0)
        autosave_layout.setSpacing(8)

        self.autosave = QCheckBox("Enable Auto-save in every ")
        self.autosave.setStyleSheet("""
            QCheckBox {
                color: #e0e0e0;
                spacing: 8px;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border-radius: 3px;
                border: 1px solid #3d3d3d;
            }
            QCheckBox::indicator:unchecked {
                background-color: #2d2d2d;
            }
            QCheckBox::indicator:checked {
                background-color: #0096C7;
            }
        """)

        self.autosave_interval = QSpinBox()
        self.autosave_interval.setRange(1, 10)
        self.autosave_interval.setSuffix(" mins")
        self.autosave_interval.setFixedWidth(100)

        autosave_layout.addWidget(self.autosave)
        autosave_layout.addWidget(self.autosave_interval)

        # Enable/disable interval based on checkbox
        self.autosave.toggled.connect(self.autosave_interval.setEnabled)
        self.autosave.setChecked(True)

        editor_layout.addWidget(autosave_group)

        # Add separator
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        line.setStyleSheet("background-color: #3d3d3d;")
        editor_layout.addWidget(line)

        # Tab Width and Font Size in a grid
        settings_layout = QVBoxLayout()
        settings_layout.setSpacing(20)

        # Tab Width settings
        tab_layout = QHBoxLayout()
        tab_label = QLabel("Tab Width:")
        self.tab_width = QSpinBox()
        self.tab_width.setRange(2, 8)
        self.tab_width.setFixedWidth(100)
        tab_layout.addWidget(tab_label)
        tab_layout.addWidget(self.tab_width)

        # Font size settings
        font_layout = QHBoxLayout()
        font_label = QLabel("Font Size:")
        self.font_size = QSpinBox()
        self.font_size.setRange(8, 24)
        self.font_size.setSuffix("px")
        self.font_size.setFixedWidth(100)
        font_layout.addWidget(font_label)
        font_layout.addWidget(self.font_size)
        settings_layout.addStretch()
        self.font_family = QComboBox()
        self.font_family.addItems(
            ["Consolas", "Courier New", "Monospace", "Arial", "Verdana", "Tahoma", "Times New Roman", "Calibri", "Comic Sans MS"])
        self.font_family.setFixedWidth(200)
        font_family_label = QLabel("Font Family:")
        font_family_layout = QHBoxLayout()
        font_family_layout.addWidget(font_family_label)
        font_family_layout.addWidget(self.font_family)
        font_layout.addLayout(font_family_layout)
        settings_layout.addLayout(font_layout)
        settings_layout.addLayout(tab_layout)

        editor_layout.addLayout(settings_layout)
        editor_layout.addStretch()

        layout.addWidget(editor_frame)
        # Buttons
        layout.addStretch()
        btn_layout = QHBoxLayout()
        cancel_btn = QPushButton("Cancel")
        reset_btn = QPushButton("Reset to Defaults")
        save_btn = QPushButton("Save Changes")
        save_btn.setObjectName("save_button")
        cancel_btn.setFixedWidth(180)
        reset_btn.setFixedWidth(180)
        save_btn.setFixedWidth(180)
        btn_layout.addStretch()
        btn_layout.addWidget(cancel_btn)
        btn_layout.addWidget(reset_btn)
        btn_layout.addWidget(save_btn)

        save_btn.clicked.connect(self.save_config)
        reset_btn.clicked.connect(self.reset_to_defaults)
        cancel_btn.clicked.connect(self.reject)
        layout.addLayout(btn_layout)

    def toggle_password_visibility(self, line_edit):
        if line_edit.echoMode() == QLineEdit.Password:
            line_edit.setEchoMode(QLineEdit.Normal)
        else:
            line_edit.setEchoMode(QLineEdit.Password)

    def create_section(self, title):
        # Create main frame
        frame = QFrame()
        frame.setObjectName("section_frame")
        layout = QVBoxLayout(frame)
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)

        # Add title
        title_label = QLabel(title)
        title_label.setObjectName("section_title")
        layout.addWidget(title_label)

        # Create content widget
        content = QWidget()
        content.setObjectName("section_content")
        content_layout = QVBoxLayout(content)
        content_layout.setSpacing(10)
        layout.addWidget(content)

        return frame, content_layout

    def create_group(self, title):
        """Create a better organized group with proper spacing"""
        group = QFrame()
        group.setStyleSheet("""
            QFrame {
                background-color: #252525;
                border: 1px solid #333;
                border-radius: 6px;
            }
            QLabel {
                padding: 2px;
            }
        """)

        # Main layout for the group
        main_layout = QVBoxLayout(group)
        main_layout.setSpacing(8)
        main_layout.setContentsMargins(12, 8, 12, 12)

        # Add title
        title_label = QLabel(title)
        title_label.setStyleSheet("""
            color: #58a6ff;
            font-weight: bold;
            font-size: 13px;
            border-bottom: 1px solid #333;
            padding-bottom: 5px;
            margin-bottom: 5px;
        """)
        main_layout.addWidget(title_label)

        return group

    def select_workspace(self):
        """Select workspace with validation"""
        try:
            folder = QFileDialog.getExistingDirectory(
                self, "Select Workspace Folder")
            if folder:
                if not os.access(folder, os.W_OK):
                    raise ConfigError("Selected folder is not writable")
                self.workspace_path.setText(folder)
        except ConfigError as e:
            QMessageBox.critical(self, "Error", str(e))
        except Exception as e:
            QMessageBox.critical(self, "Error", 
                f"Error selecting workspace: {str(e)}")

    def validate_inputs(self):
        """Validate all input fields"""
        if not self.workspace_path.text().strip():
            raise ConfigError("Workspace path cannot be empty")
        
        if not os.path.exists(self.workspace_path.text()):
            raise ConfigError("Selected workspace path does not exist")
            
        if not self.api_key.text().strip():
            raise ConfigError("API key cannot be empty")
            
        # Validate API key format (basic check)
        if len(self.api_key.text()) < 8:
            raise ConfigError("API key seems invalid (too short)")

    def load_config(self):
        """Load configuration with error handling"""
        try:
            if not os.path.exists(self.config_file):
                # Create default config if doesn't exist
                self.save_default_config()
                return

            with open(self.config_file, 'r') as f:
                config = json.load(f)
                
            # Validate config structure
            required_keys = ['cpp_version', 'workspace_folder', 'gemini_api_key', 'editor_settings']
            if not all(key in config for key in required_keys):
                raise ConfigLoadError("Invalid config file structure")

            # Set values with validation
            self.cpp_version.setCurrentText(config.get('cpp_version', 'c++17'))
            
            workspace = config.get('workspace_folder', '')
            if workspace and not os.path.exists(workspace):
                QMessageBox.warning(self, "Warning", 
                    f"Configured workspace folder does not exist:\n{workspace}")
            self.workspace_path.setText(workspace)
            
            self.api_key.setText(config.get('gemini_api_key', ''))
            
            editor_settings = config.get('editor_settings', {})
            self.autosave.setChecked(editor_settings.get('autosave', True))
            self.autosave_interval.setValue(
                min(max(editor_settings.get('autosave_interval', 5), 1), 10))
            self.tab_width.setValue(
                min(max(editor_settings.get('tab_width', 4), 2), 8))
            self.font_size.setValue(
                min(max(editor_settings.get('font_size', 14), 8), 24))

        except json.JSONDecodeError as e:
            QMessageBox.critical(self, "Error", 
                f"Failed to parse config file: {str(e)}")
            self.save_default_config()
        except ConfigLoadError as e:
            QMessageBox.critical(self, "Error", str(e))
            self.save_default_config()
        except Exception as e:
            QMessageBox.critical(self, "Error", 
                f"Unexpected error loading config: {str(e)}")
            self.save_default_config()

    def save_default_config(self):
        """Save default configuration"""
        default_config = {
            'cpp_version': 'c++17',
            'workspace_folder': '',
            'gemini_api_key': '',
            'editor_settings': {
                'autosave': True,
                'autosave_interval': 5,
                'tab_width': 4,
                'font_size': 12,
                'font_family': 'Consolas'  # New default font family
            }
        }
        try:
            with open(self.config_file, 'w') as f:
                json.dump(default_config, f, indent=4)
            self.load_config()  # Reload with defaults
        except Exception as e:
            QMessageBox.critical(self, "Error", 
                f"Failed to save default config: {str(e)}")

    def save_config(self):
        """Save configuration with validation"""
        try:
            self.validate_inputs()
            
            config = {
                'cpp_version': self.cpp_version.currentText(),
                'workspace_folder': self.workspace_path.text(),
                'gemini_api_key': self.api_key.text(),
                'editor_settings': {
                    'autosave': self.autosave.isChecked(),
                    'autosave_interval': self.autosave_interval.value(),
                    'tab_width': self.tab_width.value(),
                    'font_size': self.font_size.value()
                }
            }

            # Create backup of existing config
            if os.path.exists(self.config_file):
                backup_file = f"{self.config_file}.bak"
                try:
                    os.replace(self.config_file, backup_file)
                except Exception as e:
                    QMessageBox.warning(self, "Warning", 
                        f"Failed to create backup: {str(e)}")

            # Save new config
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=4)

            self.accept()

        except ConfigError as e:
            QMessageBox.critical(self, "Validation Error", str(e))
        except Exception as e:
            QMessageBox.critical(self, "Error", 
                f"Failed to save configuration: {str(e)}")

    def reset_to_defaults(self):
        """Reset all settings to defaults with confirmation"""
        reply = QMessageBox.question(self, 'Confirm Reset',
                                   'Are you sure you want to reset all settings to defaults?',
                                   QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            self.cpp_version.setCurrentText('c++17')
            self.workspace_path.clear()
            self.api_key.clear()
            self.autosave.setChecked(True)
            self.autosave_interval.setValue(5)
            self.tab_width.setValue(4)
            self.font_size.setValue(12)
            self.font_family.setCurrentText('Consolas')
