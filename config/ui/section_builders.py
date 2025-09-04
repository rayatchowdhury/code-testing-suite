"""Section builders for configuration dialog UI components."""

from PySide6.QtWidgets import (
    QFrame, QVBoxLayout, QHBoxLayout, QWidget, QLabel, QComboBox, 
    QLineEdit, QSpinBox, QCheckBox, QPushButton, QFileDialog
)
from PySide6.QtCore import Qt

from styles.constants.colors import MATERIAL_COLORS


class SectionBuilder:
    """Builds configuration sections for the config dialog."""
    
    def __init__(self, parent_dialog):
        self.parent = parent_dialog
        
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

        self.parent.cpp_version_combo = QComboBox()
        self.parent.cpp_version_combo.addItems(["auto", "c++11", "c++14", "c++17", "c++20", "c++23"])
        self.parent.cpp_version_combo.setFixedHeight(28)
        cpp_layout.addWidget(self.parent.cpp_version_combo)
        
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
        
        self.parent.workspace_input = QLineEdit()
        self.parent.workspace_input.setPlaceholderText("Select workspace folder...")
        self.parent.workspace_input.setFixedHeight(28)
        ws_layout.addWidget(self.parent.workspace_input)
        
        browse_btn = QPushButton("Browse")
        browse_btn.setObjectName("small_button")
        browse_btn.setFixedSize(80, 28)
        browse_btn.clicked.connect(self._browse_workspace)
        ws_layout.addWidget(browse_btn)
        
        layout.addWidget(ws_widget)
        return frame

    def create_ai_section(self):
        """Create AI configuration section with proper controls"""
        frame, layout = self.create_section_frame("🤖 AI Assistant")

        # AI Panel checkbox
        self.parent.use_ai_checkbox = QCheckBox("Enable AI Panel")
        self.parent.use_ai_checkbox.setToolTip("Enable AI-powered code assistance features")
        self.parent.use_ai_checkbox.stateChanged.connect(self.parent.api_validator.on_ai_toggle)
        layout.addWidget(self.parent.use_ai_checkbox)

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
        self.parent.key_input = QLineEdit()
        self.parent.key_input.setEchoMode(QLineEdit.Password)
        self.parent.key_input.setPlaceholderText("Enter your Gemini API key...")
        self.parent.key_input.setFixedHeight(28)
        self.parent.key_input.textChanged.connect(self.parent.api_validator.on_key_changed)
        api_key_layout.addWidget(self.parent.key_input)
        
        # Toggle visibility button
        self.parent.toggle_btn = QPushButton("👁")
        self.parent.toggle_btn.setObjectName("small_button")
        self.parent.toggle_btn.setFixedSize(32, 32)
        self.parent.toggle_btn.clicked.connect(self.parent.api_validator.toggle_visibility)
        self.parent.toggle_btn.setToolTip("Show/Hide API key")
        api_key_layout.addWidget(self.parent.toggle_btn)
        
        # Validate button
        self.parent.validate_btn = QPushButton("🔄")
        self.parent.validate_btn.setObjectName("small_button")
        self.parent.validate_btn.setFixedSize(32, 32)
        self.parent.validate_btn.clicked.connect(self.parent.api_validator.force_validation)
        self.parent.validate_btn.setToolTip("Re-validate API key")
        api_key_layout.addWidget(self.parent.validate_btn)
        
        # Validation indicator
        self.parent.status_label = QLabel()
        self.parent.status_label.setFixedWidth(20)
        api_key_layout.addWidget(self.parent.status_label)

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
        self.parent.model_input = QLineEdit()
        self.parent.model_input.setPlaceholderText("e.g., gemini-1.5-flash (leave empty for auto-selection)")
        self.parent.model_input.setFixedHeight(28)
        self.parent.model_input.setToolTip("Specify a Gemini model name, or leave empty to auto-select the best available model")
        model_layout.addWidget(self.parent.model_input)
        
        # Discover models button
        self.parent.discover_btn = QPushButton("🔍")
        self.parent.discover_btn.setObjectName("small_button")
        self.parent.discover_btn.setFixedSize(32, 32)
        self.parent.discover_btn.clicked.connect(self.parent.api_validator.discover_models)
        self.parent.discover_btn.setToolTip("Discover available models")
        model_layout.addWidget(self.parent.discover_btn)

        layout.addWidget(model_widget)

        # Info label
        info_label = QLabel("💡 Enable AI Panel to access code assistance features. Valid API key required. Custom model names override auto-selection.")
        info_label.setStyleSheet(f"color: {MATERIAL_COLORS['on_surface_variant']}; font-size: 12px;")
        info_label.setWordWrap(True)
        layout.addWidget(info_label)

        # Store the API key widget for enabling/disabling
        self.parent.api_key_widget = api_key_widget
        self.parent.model_widget = model_widget
        self.parent.api_key_widget.setEnabled(True)
        self.parent.model_widget.setEnabled(True)

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
        
        self.parent.font_size_spin = QSpinBox()
        self.parent.font_size_spin.setRange(8, 28)
        self.parent.font_size_spin.setValue(13)
        self.parent.font_size_spin.setFixedHeight(28)
        font_layout.addWidget(self.parent.font_size_spin)
        font_layout.addStretch(1)
        
        layout.addWidget(font_widget)

        # Line wrap
        self.parent.wrap_checkbox = QCheckBox("Enable line wrap")
        layout.addWidget(self.parent.wrap_checkbox)
        
        return frame

    def create_database_section(self):
        """Create database management section"""
        frame, layout = self.create_section_frame("🗄️ Database Management")

        # Database statistics display
        self.parent.db_stats_label = QLabel("Click 'Refresh Stats' to view database information")
        self.parent.db_stats_label.setObjectName("info_label")
        self.parent.db_stats_label.setWordWrap(True)
        layout.addWidget(self.parent.db_stats_label)

        # Buttons row 1: Stats and Cleanup
        buttons_row1 = QWidget()
        buttons_layout1 = QHBoxLayout(buttons_row1)
        buttons_layout1.setContentsMargins(0, 0, 0, 0)
        buttons_layout1.setSpacing(8)

        self.parent.refresh_stats_btn = QPushButton("Refresh Stats")
        self.parent.refresh_stats_btn.setObjectName("secondary_button")
        self.parent.refresh_stats_btn.clicked.connect(self.parent.db_operations.refresh_database_stats)
        buttons_layout1.addWidget(self.parent.refresh_stats_btn)

        self.parent.cleanup_btn = QPushButton("Cleanup Old Data (30 days)")
        self.parent.cleanup_btn.setObjectName("secondary_button")
        self.parent.cleanup_btn.clicked.connect(self.parent.db_operations.cleanup_old_data)
        buttons_layout1.addWidget(self.parent.cleanup_btn)

        buttons_layout1.addStretch(1)
        layout.addWidget(buttons_row1)

        # Buttons row 2: Delete All (with warning)
        buttons_row2 = QWidget()
        buttons_layout2 = QHBoxLayout(buttons_row2)
        buttons_layout2.setContentsMargins(0, 0, 0, 0)
        buttons_layout2.setSpacing(8)

        self.parent.delete_all_btn = QPushButton("⚠️ Delete ALL Data")
        self.parent.delete_all_btn.setObjectName("danger_button")
        self.parent.delete_all_btn.clicked.connect(self.parent.db_operations.delete_all_data)
        buttons_layout2.addWidget(self.parent.delete_all_btn)

        buttons_layout2.addStretch(1)
        layout.addWidget(buttons_row2)

        # Warning text
        warning_label = QLabel("⚠️ Warning: 'Delete ALL Data' permanently removes all test results and sessions!")
        warning_label.setObjectName("warning_label")
        warning_label.setWordWrap(True)
        layout.addWidget(warning_label)

        return frame

    def _browse_workspace(self):
        """Browse for workspace folder"""
        path = QFileDialog.getExistingDirectory(self.parent, "Select workspace folder")
        if path:
            self.parent.workspace_input.setText(path)
