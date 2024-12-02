from PySide6.QtWidgets import QDialog, QVBoxLayout, QMessageBox
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
import os

from .config_manager import ConfigManager
from .config_exceptions import ConfigError
from .ui_components import (
    TitleSection,
    CppVersionSection,
    WorkspaceSection,
    ApiKeySection,
    EditorSettingsSection,
    ButtonSection
)
from .styles import CONFIG_DIALOG_STYLE
from .error_dialog import ErrorDialog

class ConfigView(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        base_path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        icon_path = os.path.join(base_path, "resources", "icons", "settings.png")
        self.setWindowIcon(QIcon(icon_path))
        self.setWindowTitle("Configurations")
        self.setFixedSize(500, 570)  # More compact size
        self.setWindowFlags(Qt.Dialog | Qt.WindowCloseButtonHint)
        self.setStyleSheet(CONFIG_DIALOG_STYLE)
        
        self.config_manager = ConfigManager()
        self.setup_ui()
        self.load_config()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(6)  # Tighter spacing
        layout.setContentsMargins(12, 12, 12, 12)  # Smaller margins

        # Add sections
        self.title_section = TitleSection()
        self.cpp_section = CppVersionSection()
        self.workspace_section = WorkspaceSection()
        self.api_section = ApiKeySection()
        self.editor_section = EditorSettingsSection()
        self.button_section = ButtonSection()

        # Add to layout
        layout.addWidget(self.title_section)
        layout.addWidget(self.cpp_section)
        layout.addWidget(self.workspace_section)
        layout.addWidget(self.api_section)
        layout.addWidget(self.editor_section)
        layout.addStretch()
        layout.addLayout(self.button_section)

        # Connect signals
        self.button_section.save_clicked.connect(self.save_config)
        self.button_section.reset_clicked.connect(self.reset_to_defaults)
        self.button_section.cancel_clicked.connect(self.reject)

    def load_config(self):
        try:
            config = self.config_manager.load_config()
            self.cpp_section.load_config(config)
            self.workspace_section.load_config(config)
            self.api_section.load_config(config)
            self.editor_section.load_config(config)
        except ConfigError as e:
            self.show_error("Configuration Error", str(e))
        except Exception as e:
            self.show_error("Unexpected Error",
                          "Failed to load configuration",
                          str(e))

    def save_config(self):
        try:
            config = {
                'cpp_version': self.cpp_section.get_config(),
                'workspace_folder': self.workspace_section.get_config(),
                'gemini_api_key': self.api_section.get_config(),
                'editor_settings': self.editor_section.get_config()
            }
            
            self.config_manager.save_config(config)
            self.accept()
            
        except ConfigError as e:
            self.show_error("Configuration Error", str(e))
        except Exception as e:
            self.show_error("Unexpected Error", 
                          "Failed to save configuration",
                          str(e))

    def reset_to_defaults(self):
        reply = QMessageBox.question(self, 'Confirm Reset',
                                   'Are you sure you want to reset all settings to defaults?',
                                   QMessageBox.Yes | QMessageBox.No, 
                                   QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            default_config = self.config_manager.get_default_config()
            self.cpp_section.load_config(default_config)
            self.workspace_section.load_config(default_config)
            self.api_section.load_config(default_config)
            self.editor_section.load_config(default_config)

    def show_error(self, title, message, details=None):
        dialog = ErrorDialog(title, message, details, self)
        dialog.exec()
