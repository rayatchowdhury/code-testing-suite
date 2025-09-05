"""Configuration dialog UI management."""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QScrollArea, QWidget,
    QLabel, QPushButton
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QIcon
import os

from styles.components.config_styles import CONFIG_DIALOG_STYLE
from styles.components.config_ui import CONFIG_DIALOG_TITLE_STYLE
from styles.constants.colors import MATERIAL_COLORS
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

        # Lazy imports to improve startup performance
        from ..management.config_manager import ConfigManager
        from database.database_manager import DatabaseManager
        from .section_builders import SectionBuilder
        from ..validation.api_validator_handler import APIValidatorHandler
        from ..management.database_operations import DatabaseOperations
        from ..management.config_persistence import ConfigPersistence

        # Initialize modules
        self.config_manager = ConfigManager()
        self.database_manager = DatabaseManager()
        self.section_builder = SectionBuilder(self)
        self.api_validator = APIValidatorHandler(self)
        self.db_operations = DatabaseOperations(self, self.database_manager)
        self.config_persistence = ConfigPersistence(self, self.config_manager)

        # Validation state
        self.validation_thread = None
        self.is_key_valid = False

        self.setup_ui()
        self.config_persistence.load_config()

    def setup_ui(self):
        """Setup UI using original app patterns"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(24, 24, 24, 24)
        main_layout.setSpacing(0)

        # Title section
        title_section = QLabel("⚙️ Configurations")
        title_section.setStyleSheet(CONFIG_DIALOG_TITLE_STYLE)
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

        # Create sections using section builder
        content_layout.addWidget(self.section_builder.create_cpp_section())
        content_layout.addWidget(self.section_builder.create_workspace_section())
        content_layout.addWidget(self.section_builder.create_ai_section())
        content_layout.addWidget(self.section_builder.create_editor_section())
        content_layout.addWidget(self.section_builder.create_database_section())
        
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
        self.save_btn.clicked.connect(self.config_persistence.save_config)
        self.reset_btn.clicked.connect(self.config_persistence.reset_to_defaults)
        self.cancel_btn.clicked.connect(self.reject)

    def show_error(self, title, message, details=None):
        """Show error dialog"""
        # Lazy import
        from .error_dialog import ErrorDialog
        dialog = ErrorDialog(title, message, details, self)
        dialog.exec()
