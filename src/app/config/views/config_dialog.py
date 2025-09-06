"""Consolidated configuration dialog with all UI components."""

import os
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QScrollArea, QWidget,
    QLabel, QPushButton, QFrame, QComboBox, QLineEdit, QSpinBox, 
    QCheckBox, QFileDialog, QTextEdit, QMessageBox
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QIcon, QFont

from src.app.styles.components.config_styles import CONFIG_DIALOG_STYLE
from src.app.styles.components.config_ui import (
    CONFIG_DIALOG_TITLE_STYLE, SECTION_INFO_LABEL_STYLE
)
from src.app.styles.constants.colors import MATERIAL_COLORS
from src.app.constants import SETTINGS_ICON


class ErrorDialog(QDialog):
    """A styled error dialog for displaying error messages with optional details."""
    
    def __init__(self, title, message, details=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setMinimumSize(400, 200)
        self.setMaximumWidth(600)
        self.setWindowFlag(Qt.WindowContextHelpButtonHint, False)
        
        self.title_text = title
        self.message_text = message
        self.details_text = details
        
        self._setup_ui()
        self._setup_styles()

    def _setup_ui(self):
        """Set up the UI components."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)

        # Title label
        title_label = QLabel(self.title_text)
        title_label.setObjectName("error_title")
        title_font = QFont()
        title_font.setBold(True)
        title_font.setPointSize(14)
        title_label.setFont(title_font)
        layout.addWidget(title_label)

        # Message label
        message_label = QLabel(self.message_text)
        message_label.setObjectName("error_message")
        message_label.setWordWrap(True)
        layout.addWidget(message_label)

        # Details section (if provided)
        if self.details_text:
            # Separator
            separator = QFrame()
            separator.setFrameShape(QFrame.HLine)
            separator.setObjectName("error_separator")
            layout.addWidget(separator)

            # Details label
            details_label = QLabel("Details:")
            details_label.setObjectName("error_details_label")
            details_font = QFont()
            details_font.setBold(True)
            details_label.setFont(details_font)
            layout.addWidget(details_label)

            # Details text
            details_text = QTextEdit()
            details_text.setObjectName("error_details")
            details_text.setPlainText(self.details_text)
            details_text.setReadOnly(True)
            details_text.setMaximumHeight(150)
            layout.addWidget(details_text)

        # Button layout
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        # OK button
        ok_button = QPushButton("OK")
        ok_button.setObjectName("error_ok_button")
        ok_button.setDefault(True)
        ok_button.clicked.connect(self.accept)
        button_layout.addWidget(ok_button)

        layout.addLayout(button_layout)

    def _setup_styles(self):
        """Apply styling to the dialog."""
        from src.app.styles.components.config_ui import ERROR_DIALOG_STYLE
        self.setStyleSheet(ERROR_DIALOG_STYLE)

    @staticmethod
    def show_error(title, message, details=None, parent=None):
        """Convenience method to show an error dialog."""
        dialog = ErrorDialog(title, message, details, parent)
        return dialog.exec()


class ConfigView(QDialog):
    """Consolidated configuration dialog with all UI components."""

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

        # Initialize modules with updated imports (Phase 3)
        from src.app.config.core import ConfigManager, ConfigPersistence
        from src.app.database.database_manager import DatabaseManager
        from src.app.config.gemini import GeminiConfig
        from src.app.config.database import DatabaseOperations

        # Initialize components
        self.config_manager = ConfigManager()
        self.database_manager = DatabaseManager()
        self.gemini_config = GeminiConfig()
        self.db_operations = DatabaseOperations(self, self.database_manager)
        self.config_persistence = ConfigPersistence(self, self.config_manager)

        # Validation state
        self.validation_thread = None
        self.is_key_valid = False

        self.setup_ui()
        self.config_persistence.load_config()

    def setup_ui(self):
        """Setup UI using original app patterns with inline section builders."""
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

        # Create sections (inline section builders)
        content_layout.addWidget(self._create_cpp_section())
        content_layout.addWidget(self._create_workspace_section())
        content_layout.addWidget(self._create_ai_section())
        content_layout.addWidget(self._create_editor_section())
        content_layout.addWidget(self._create_database_section())
        
        # Add stretch to push content to top
        content_layout.addStretch(1)

        # Set content to scroll area
        scroll_area.setWidget(content_widget)
        main_layout.addWidget(scroll_area)

        # Button container
        button_container = QWidget()
        button_container.setObjectName("button_container")
        button_container.setFixedHeight(72)
        
        button_layout = QHBoxLayout(button_container)
        button_layout.setContentsMargins(0, 16, 0, 16)
        button_layout.setSpacing(12)
        
        # Reset button
        reset_btn = QPushButton("Reset to Defaults")
        reset_btn.setObjectName("secondary_button")
        reset_btn.clicked.connect(self.config_persistence.reset_to_defaults)
        button_layout.addWidget(reset_btn)
        
        button_layout.addStretch(1)
        
        # Cancel and Save buttons
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setObjectName("secondary_button")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        save_btn = QPushButton("Save")
        save_btn.setObjectName("primary_button")
        save_btn.setDefault(True)
        save_btn.clicked.connect(self._save_and_close)
        button_layout.addWidget(save_btn)
        
        main_layout.addWidget(button_container)

    def _create_section_frame(self, title_text):
        """Create section frame using original app patterns."""
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

    def _create_cpp_section(self):
        """Create C++ configuration section."""
        frame, layout = self._create_section_frame("🔧 C++ Version")

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

    def _create_workspace_section(self):
        """Create workspace configuration section."""
        frame, layout = self._create_section_frame("📁 Workspace")

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
        browse_btn.clicked.connect(self._browse_workspace)
        ws_layout.addWidget(browse_btn)
        
        layout.addWidget(ws_widget)
        return frame

    def _create_ai_section(self):
        """Create AI configuration section with proper controls."""
        frame, layout = self._create_section_frame("🤖 AI Assistant")

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

        # Model Selection section
        model_widget = QWidget()
        model_layout = QHBoxLayout(model_widget)
        model_layout.setContentsMargins(0, 0, 0, 0)
        model_layout.setSpacing(8)

        # Model label
        model_label = QLabel("Preferred Model:")
        model_label.setFixedWidth(120)
        model_layout.addWidget(model_label)

        # Model input (allows manual entry or selection)
        self.model_input = QLineEdit()
        self.model_input.setPlaceholderText("e.g., gemini-1.5-flash (leave empty for auto-selection)")
        self.model_input.setFixedHeight(28)
        self.model_input.setToolTip("Specify a Gemini model name, or leave empty to auto-select the best available model")
        model_layout.addWidget(self.model_input)
        
        # Discover models button
        self.discover_btn = QPushButton("🔍")
        self.discover_btn.setObjectName("small_button")
        self.discover_btn.setFixedSize(32, 32)
        self.discover_btn.clicked.connect(self.discover_models)
        self.discover_btn.setToolTip("Discover available models")
        model_layout.addWidget(self.discover_btn)

        layout.addWidget(model_widget)

        # Info label
        info_label = QLabel("💡 Enable AI Panel to access code assistance features. Valid API key required. Custom model names override auto-selection.")
        info_label.setStyleSheet(SECTION_INFO_LABEL_STYLE)
        info_label.setWordWrap(True)
        layout.addWidget(info_label)

        # Store widgets for enabling/disabling
        self.api_key_widget = api_key_widget
        self.model_widget = model_widget
        self.api_key_widget.setEnabled(True)
        self.model_widget.setEnabled(True)

        return frame

    def _create_editor_section(self):
        """Create editor configuration section."""
        frame, layout = self._create_section_frame("📝 Editor Settings")

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

    def _create_database_section(self):
        """Create database management section."""
        frame, layout = self._create_section_frame("🗄️ Database Management")

        # Database statistics display
        self.db_stats_label = QLabel("Click 'Refresh Stats' to view database information")
        self.db_stats_label.setObjectName("info_label")
        self.db_stats_label.setWordWrap(True)
        layout.addWidget(self.db_stats_label)

        # Buttons row 1: Stats and Cleanup
        buttons_row1 = QWidget()
        buttons_layout1 = QHBoxLayout(buttons_row1)
        buttons_layout1.setContentsMargins(0, 0, 0, 0)
        buttons_layout1.setSpacing(8)

        self.refresh_stats_btn = QPushButton("Refresh Stats")
        self.refresh_stats_btn.setObjectName("secondary_button")
        self.refresh_stats_btn.clicked.connect(self.db_operations.refresh_database_stats)
        buttons_layout1.addWidget(self.refresh_stats_btn)

        self.cleanup_btn = QPushButton("Cleanup Old Data (30 days)")
        self.cleanup_btn.setObjectName("secondary_button")
        self.cleanup_btn.clicked.connect(self.db_operations.cleanup_old_data)
        buttons_layout1.addWidget(self.cleanup_btn)

        buttons_layout1.addStretch(1)
        layout.addWidget(buttons_row1)

        # Buttons row 2: Delete All (with warning)
        buttons_row2 = QWidget()
        buttons_layout2 = QHBoxLayout(buttons_row2)
        buttons_layout2.setContentsMargins(0, 0, 0, 0)
        buttons_layout2.setSpacing(8)

        self.delete_all_btn = QPushButton("⚠️ Delete ALL Data")
        self.delete_all_btn.setObjectName("danger_button")
        self.delete_all_btn.clicked.connect(self.db_operations.delete_all_data)
        buttons_layout2.addWidget(self.delete_all_btn)

        buttons_layout2.addStretch(1)
        layout.addWidget(buttons_row2)

        # Warning text
        warning_label = QLabel("⚠️ Warning: 'Delete ALL Data' permanently removes all test results and sessions!")
        warning_label.setObjectName("warning_label")
        warning_label.setWordWrap(True)
        layout.addWidget(warning_label)

        return frame

    # Event handlers (previously in config_dialog.py)
    def show_error(self, title, message, details=None):
        """Show error dialog."""
        ErrorDialog.show_error(title, message, details, self)

    def show_success(self, title, message):
        """Show success message."""
        QMessageBox.information(self, title, message)

    # Compatibility methods for UI event handling (cleaned up from Phase 1)
    def on_ai_toggle(self, state):
        """Handle AI panel toggle."""
        # Enable/disable related controls based on checkbox state
        enabled = state == Qt.Checked
        # Implementation would go here
        pass
    
    def on_key_changed(self, text):
        """Handle API key text change."""
        # Reset validation state when key changes
        self.is_key_valid = False
        self.status_label.setText("")
        # Implementation would go here
        pass
    
    def toggle_visibility(self):
        """Toggle API key visibility."""
        if self.key_input.echoMode() == QLineEdit.Password:
            self.key_input.setEchoMode(QLineEdit.Normal)
            self.toggle_btn.setText("🙈")
        else:
            self.key_input.setEchoMode(QLineEdit.Password)
            self.toggle_btn.setText("👁")
    
    def force_validation(self):
        """Force API key validation."""
        api_key = self.key_input.text().strip()
        if api_key:
            # Use GeminiConfig for validation
            try:
                # Perform network validation in background
                valid, msg = self.gemini_config.validate_api_key_network(api_key)
                if valid:
                    self.is_key_valid = True
                    self.status_label.setText("✓")
                    print(f"Validation result: {valid} - {msg}")
                else:
                    self.is_key_valid = False
                    self.status_label.setText("✗")
                    print(f"Validation failed: {msg}")
            except Exception as e:
                self.status_label.setText("?")
                print(f"Validation error: {e}")
    
    def discover_models(self):
        """Discover available Gemini models."""
        api_key = self.key_input.text().strip()
        if not api_key:
            self.show_error("API Key Required", "Please enter a valid API key first.")
            return
            
        # Use GeminiConfig for model discovery
        thread = self.gemini_config.discover_models_async(api_key)
        thread.models_discovered.connect(self._on_models_discovered)
        thread.discovery_failed.connect(self._on_discovery_failed)
        thread.finished.connect(self._on_discovery_finished)
        thread.start()
        
        self.discover_btn.setText("⏳")
        self.discover_btn.setEnabled(False)
        self.validation_thread = thread
        
    def _on_models_discovered(self, models):
        """Handle successful model discovery."""
        if models:
            # Auto-select the best model
            preferred = self.gemini_config.get_preferred_model(models)
            if preferred:
                self.model_input.setText(preferred)
            self.show_success("Models Discovered", f"Found {len(models)} models. Selected: {preferred}")
        
    def _on_discovery_failed(self, error_msg):
        """Handle model discovery failure."""
        self.show_error("Model Discovery Failed", error_msg)
        
    def _on_discovery_finished(self):
        """Handle discovery completion."""
        self.discover_btn.setText("🔍")
        self.discover_btn.setEnabled(True)
        self.validation_thread = None

    def _browse_workspace(self):
        """Browse for workspace folder."""
        path = QFileDialog.getExistingDirectory(self, "Select workspace folder")
        if path:
            self.workspace_input.setText(path)

    def _save_and_close(self):
        """Save configuration and close dialog."""
        try:
            self.config_persistence.save_config()
            self.configSaved.emit(self.config_manager.load_config())
            self.accept()
        except Exception as e:
            self.show_error("Save Error", "Failed to save configuration", str(e))
