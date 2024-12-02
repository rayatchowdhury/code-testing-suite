from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                               QComboBox, QLineEdit, QCheckBox, QSpinBox,
                               QPushButton, QFileDialog, QFrame, QWidget, QSlider)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QIcon, QFont
import json
import os


class ConfigView(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
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
        self.setup_ui()
        self.load_config()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        # Title
        title = QLabel("⚙️ Application Settings")
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
        settings_layout = QHBoxLayout()
        settings_layout.setSpacing(20)
        
        # Tab Width settings
        tab_layout = QVBoxLayout()
        tab_label = QLabel("Tab Width:")
        self.tab_width = QSpinBox()
        self.tab_width.setRange(2, 8)
        self.tab_width.setFixedWidth(60)
        tab_layout.addWidget(tab_label)
        tab_layout.addWidget(self.tab_width)
        settings_layout.addLayout(tab_layout)
        
        # Font size settings
        font_layout = QVBoxLayout()
        font_label = QLabel("Font Size:")
        self.font_size = QSpinBox()
        self.font_size.setRange(8, 24)
        self.font_size.setSuffix("px")
        self.font_size.setFixedWidth(70)
        font_layout.addWidget(font_label)
        font_layout.addWidget(self.font_size)
        settings_layout.addLayout(font_layout)
        settings_layout.addStretch()
        
        editor_layout.addLayout(settings_layout)
        editor_layout.addStretch()

        layout.addWidget(editor_frame)
        # Buttons
        layout.addStretch()
        btn_layout = QHBoxLayout()
        cancel_btn = QPushButton("Cancel")
        save_btn = QPushButton("Save Changes")
        save_btn.setObjectName("save_button")
        cancel_btn.setFixedWidth(100)
        save_btn.setFixedWidth(120)
        btn_layout.addStretch()
        btn_layout.addWidget(cancel_btn)
        btn_layout.addWidget(save_btn)

        save_btn.clicked.connect(self.save_config)
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
        folder = QFileDialog.getExistingDirectory(
            self, "Select Workspace Folder")
        if folder:
            self.workspace_path.setText(folder)

    def load_config(self):
        try:
            with open('config.json', 'r') as f:
                config = json.load(f)
                self.cpp_version.setCurrentText(config.get('cpp_version', 'c++17'))
                self.workspace_path.setText(config.get('workspace_folder', ''))
                self.api_key.setText(config.get('gemini_api_key', ''))
                editor_settings = config.get('editor_settings', {})
                self.autosave.setChecked(editor_settings.get('autosave', True))
                self.autosave_interval.setValue(editor_settings.get('autosave_interval', 5))
                self.tab_width.setValue(editor_settings.get('tab_width', 4))
                self.font_size.setValue(editor_settings.get('font_size', 14))
        except FileNotFoundError:
            pass

    def save_config(self):
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

        with open('config.json', 'w') as f:
            json.dump(config, f, indent=4)

        self.accept()
