from PySide6.QtWidgets import (QWidget, QLabel, QComboBox, QLineEdit, 
                              QPushButton, QFrame, QVBoxLayout, QHBoxLayout,
                              QSpinBox, QCheckBox, QFileDialog)
import os
from PySide6.QtCore import Signal, QSize, Qt
from .config_exceptions import ConfigValidationError, ConfigMissingError, ConfigPermissionError

class ConfigError(Exception):
    pass

# Base section class
class BaseSection(QFrame):
    def __init__(self):
        super().__init__()
        self.setObjectName("section_frame")
        self.layout = QVBoxLayout(self)
        self.layout.setSpacing(2)  # More compact spacing
        self.layout.setContentsMargins(0, 0, 0, 3)  # Reduced bottom margin
        
        # Add hover effect
        self.setStyleSheet("""
            #section_frame:hover {
                background-color: #2a2a2a;
                border: 1px solid #0096C7;
            }
        """)

    def create_title(self, text):
        title = QLabel(text)
        title.setObjectName("section_title")
        return title

class TitleSection(QLabel):
    def __init__(self):
        super().__init__("Configurations")  # Simpler title
        self.setStyleSheet(
            "font-size: 18px; color: #58a6ff; font-weight: bold; margin: 3px 0;")
        self.setFixedHeight(25)  # Smaller height
        self.setAlignment(Qt.AlignCenter)

# Common measurements for all sections
COMMON_HEIGHT = 26  # Standard height for all controls
SECTION_PADDING = "8px 10px"  # Standard padding
BUTTON_WIDTH = 140  # Standard button width

class CppVersionSection(BaseSection):
    def __init__(self):
        super().__init__()
        title = self.create_title("🔧 C++ Version")
        self.layout.addWidget(title)

        content = QWidget()
        content.setObjectName("section_content")
        content_layout = QVBoxLayout(content)

        self.version_combo = QComboBox()
        self.version_combo.addItems(["c++11", "c++14", "c++17", "c++20", "c++23"])
        self.version_combo.setFixedSize(150, COMMON_HEIGHT)  # Smaller combo
        self.version_combo.setStyleSheet(self.version_combo.styleSheet() + """
            QComboBox { padding-left: 15px; font-size: 14px; }
        """)
        content_layout.addWidget(self.version_combo)
        content_layout.setContentsMargins(10, 5, 10, 10)  # Better padding

        self.layout.addWidget(content)

    def load_config(self, config):
        self.version_combo.setCurrentText(config.get('cpp_version', 'c++17'))

    def get_config(self):
        return self.version_combo.currentText()

class WorkspaceSection(BaseSection):
    def __init__(self):
        super().__init__()
        title = self.create_title("📁 Workspace Folder")
        self.layout.addWidget(title)

        content = QWidget()
        content.setObjectName("section_content")
        content_layout = QHBoxLayout(content)
        content_layout.setSpacing(8)  # Match spacing with other sections

        self.path_input = QLineEdit()
        self.path_input.setReadOnly(True)
        self.path_input.setPlaceholderText("Select workspace folder...")
        self.path_input.setFixedHeight(COMMON_HEIGHT)  # Use common height
        
        browse_btn = QPushButton("📁 Browse")
        browse_btn.setFixedSize(80, COMMON_HEIGHT)  # Match height with input
        browse_btn.setStyleSheet("""
            QPushButton {
                padding: 0px 8px;
                margin: 0px;
            }
        """)
        browse_btn.clicked.connect(self._browse_folder)

        content_layout.addWidget(self.path_input)
        content_layout.addWidget(browse_btn, 0, Qt.AlignVCenter)  # Align vertically
        content_layout.setContentsMargins(10, 5, 10, 10)
        self.layout.addWidget(content)

    def _browse_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Workspace Folder")
        if folder:
            self.path_input.setText(folder)

    def load_config(self, config):
        self.path_input.setText(config.get('workspace_folder', ''))

    def get_config(self):
        path = self.path_input.text()
        if not path:
            raise ConfigMissingError("workspace folder")
        if not os.path.exists(path):
            raise ConfigValidationError("workspace path",
                "Selected folder does not exist",
                f"Path: {path}")
        if not os.access(path, os.W_OK):
            raise ConfigPermissionError("accessing", path,
                "Please select a folder with write permissions")
        return path

class ApiKeySection(BaseSection):
    def __init__(self):
        super().__init__()
        title = self.create_title("🔑 Gemini API Key")
        self.layout.addWidget(title)

        content = QWidget()
        content.setObjectName("section_content")
        content_layout = QHBoxLayout(content)
        content_layout.setSpacing(8)  # Match spacing with other sections
        content_layout.setContentsMargins(10, 5, 10, 10)  # Match margins with other sections

        self.key_input = QLineEdit()
        self.key_input.setEchoMode(QLineEdit.Password)
        self.key_input.setPlaceholderText("Enter your API key...")
        self.key_input.setFixedHeight(COMMON_HEIGHT)
        
        toggle_btn = QPushButton("👁")
        toggle_btn.setFixedSize(COMMON_HEIGHT, COMMON_HEIGHT)
        toggle_btn.clicked.connect(self._toggle_visibility)  # This was already here

        self.toggle_btn = toggle_btn  # Save reference to the button
        self.toggle_btn.setStyleSheet("""
            QPushButton {
                padding: 0px;
                margin: 0px;
            }
        """)

        # Add widgets with alignment
        content_layout.addWidget(self.key_input)
        content_layout.addWidget(toggle_btn, 0, Qt.AlignVCenter)  # Align vertically
        
        # Add validation indicator
        self.status_label = QLabel()
        self.status_label.setFixedWidth(20)
        content_layout.addWidget(self.status_label)
        
        content_layout.setContentsMargins(10, 5, 10, 10)
        self.layout.addWidget(content)

    def _toggle_visibility(self):
        is_hidden = self.key_input.echoMode() == QLineEdit.Password
        self.key_input.setEchoMode(QLineEdit.Normal if is_hidden else QLineEdit.Password)
        self.toggle_btn.setText("👁" if is_hidden else "🔒")  # Change icon based on state
        
    def _validate_key(self, text):
        if len(text) >= 8:
            self.status_label.setText("✓")
            self.status_label.setStyleSheet("color: #40c057")
        else:
            self.status_label.setText("⚠")
            self.status_label.setStyleSheet("color: #ff6b6b")

    def load_config(self, config):
        self.key_input.setText(config.get('gemini_api_key', ''))

    def get_config(self):
        key = self.key_input.text()
        if not key:
            raise ConfigMissingError("API key")
        if len(key) < 8:
            raise ConfigValidationError("API key", 
                "Key must be at least 8 characters long",
                "Please enter a valid Gemini API key")
        return key

class EditorSettingsSection(BaseSection):
    def __init__(self):
        super().__init__()
        title = self.create_title("📝 Editor Settings")
        self.layout.addWidget(title)

        content = QWidget()
        content.setObjectName("section_content")
        content_layout = QVBoxLayout(content)
        content_layout.setSpacing(8)  # Reduced spacing

        # Autosave settings
        autosave_layout = QHBoxLayout()
        self.autosave_check = QCheckBox("Enable Auto-save in every")
        self.autosave_interval = QSpinBox()
        self.autosave_interval.setRange(1, 10)
        self.autosave_interval.setSuffix(" mins")
        self.autosave_interval.setFixedWidth(100)
        
        autosave_layout.addWidget(self.autosave_check)
        autosave_layout.addWidget(self.autosave_interval)
        autosave_layout.addStretch()
        content_layout.addLayout(autosave_layout)

        # Tab width settings
        tab_layout = QHBoxLayout()
        tab_label = QLabel("Tab Width:")
        self.tab_width = QSpinBox()
        self.tab_width.setRange(2, 8)
        self.tab_width.setFixedWidth(100)
        tab_layout.addWidget(tab_label)
        tab_layout.addWidget(self.tab_width)
        tab_layout.addStretch()
        content_layout.addLayout(tab_layout)

        # Font settings
        font_layout = QHBoxLayout()
        font_label = QLabel("Font Size:")
        self.font_size = QSpinBox()
        self.font_size.setRange(8, 24)
        self.font_size.setSuffix("px")
        self.font_size.setFixedWidth(100)
        font_layout.addWidget(font_label)
        font_layout.addWidget(self.font_size)
        font_layout.addStretch()
        content_layout.addLayout(font_layout)

        # Add bracket matching setting
        bracket_layout = QHBoxLayout()
        self.bracket_matching = QCheckBox("Enable Bracket Matching")
        bracket_layout.addWidget(self.bracket_matching)
        bracket_layout.addStretch()
        content_layout.addLayout(bracket_layout)

        self.layout.addWidget(content)
        
        # Add tooltips
        self.autosave_check.setToolTip("Automatically save your work periodically")
        self.bracket_matching.setToolTip("Highlight matching brackets and parentheses")
        self.tab_width.setToolTip("Number of spaces for each tab")
        
        # Add visual feedback
        for spinbox in (self.autosave_interval, self.tab_width, self.font_size):
            spinbox.setStyleSheet("""
                QSpinBox::up-button:hover, QSpinBox::down-button:hover {
                    background-color: #0096C7;
                }
            """)
        
        # Make spinboxes wider and taller
        for spinbox in (self.autosave_interval, self.tab_width, self.font_size):
            spinbox.setFixedSize(100, 28)
            spinbox.setStyleSheet(spinbox.styleSheet() + """
                QSpinBox { font-size: 14px; padding-left: 10px; }
            """)
            
        # Add some padding to checkboxes
        for checkbox in (self.autosave_check, self.bracket_matching):
            checkbox.setStyleSheet("""
                QCheckBox {
                    padding: 8px;
                    font-size: 14px;
                }
                QCheckBox::indicator {
                    width: 22px;
                    height: 22px;
                }
            """)

        content_layout.setContentsMargins(10, 5, 10, 10)

    def load_config(self, config):
        editor_settings = config.get('editor_settings', {})
        self.autosave_check.setChecked(editor_settings.get('autosave', True))
        self.autosave_interval.setValue(editor_settings.get('autosave_interval', 5))
        self.tab_width.setValue(editor_settings.get('tab_width', 4))
        self.font_size.setValue(editor_settings.get('font_size', 12))
        self.bracket_matching.setChecked(editor_settings.get('bracket_matching', True))

    def get_config(self):
        return {
            'autosave': self.autosave_check.isChecked(),
            'autosave_interval': self.autosave_interval.value(),
            'tab_width': self.tab_width.value(),
            'font_size': self.font_size.value(),
            'bracket_matching': self.bracket_matching.isChecked()
        }

class ButtonSection(QHBoxLayout):
    save_clicked = Signal()
    reset_clicked = Signal()
    cancel_clicked = Signal()
    
    def __init__(self):
        super().__init__()
        self.setSpacing(8)  # Reduced spacing

        # Create buttons
        cancel_btn = QPushButton("Cancel")
        reset_btn = QPushButton("Reset to Defaults")
        save_btn = QPushButton("Save Changes")
        save_btn.setObjectName("save_button")

        # Add icons to buttons
        # cancel_btn.setIcon(QIcon("resources/icons/cancel.png"))
        # reset_btn.setIcon(QIcon("resources/icons/reset.png"))
        # save_btn.setIcon(QIcon("resources/icons/save.png"))
        
        # Set fixed size for buttons
        for btn in (cancel_btn, reset_btn, save_btn):
            btn.setFixedSize(155, 30)  # Smaller buttons
            btn.setIconSize(QSize(16, 16))
            btn.setStyleSheet(btn.styleSheet() + """
                QPushButton {
                    font-size: 13px;
                    font-weight: normal;
                }
            """)

        # Connect signals
        cancel_btn.clicked.connect(self.cancel_clicked)
        reset_btn.clicked.connect(self.reset_clicked)
        save_btn.clicked.connect(self.save_clicked)

        # Add to layout
        self.addStretch()
        self.addWidget(cancel_btn)
        self.addWidget(reset_btn)
        self.addWidget(save_btn)