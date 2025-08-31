# TODO: Create Qt adapter to break UI→service coupling from v1 config views
"""
Configuration View Adapter

Qt-based implementation of configuration UI that uses services through dependency injection.
Based on v1/views/config/config_view.py but with clean separation of concerns.
"""
from typing import Optional, Dict, Any
from pathlib import Path

try:
    from PySide6.QtWidgets import (
        QDialog, QVBoxLayout, QHBoxLayout, QScrollArea, QWidget,
        QLabel, QComboBox, QLineEdit, QCheckBox, QPushButton, QFileDialog,
        QFrame, QMessageBox
    )
    from PySide6.QtCore import Qt, Signal
    from PySide6.QtGui import QIcon
    HAS_QT = True
except ImportError:
    # Define mock classes for testing without Qt
    HAS_QT = False
    class QDialog: pass
    class Signal: pass
    class Qt: pass

from infrastructure.configuration.config_service import ConfigService, AISettings, CompilerSettings, AppSettings
from infrastructure.theming.theme_service import ThemeService

class ConfigurationViewAdapter:
    """
    Qt adapter for configuration view.
    
    ASSUMPTION: Provides Qt UI while delegating all business logic to ConfigService.
    This breaks the tight coupling between UI and configuration logic in v1.
    """
    
    def __init__(self, config_service: ConfigService, theme_service: ThemeService, parent=None):
        if not HAS_QT:
            raise RuntimeError("Qt is required for ConfigurationViewAdapter")
        
        self.config_service = config_service
        self.theme_service = theme_service
        self.parent = parent
        self._dialog: Optional[QDialog] = None
        
        # UI controls
        self._cpp_version_combo: Optional[QComboBox] = None
        self._workspace_edit: Optional[QLineEdit] = None
        self._ai_enabled_check: Optional[QCheckBox] = None
        self._api_key_edit: Optional[QLineEdit] = None
        self._auto_save_check: Optional[QCheckBox] = None
        
        # Signals
        self.configSaved = Signal(dict) if HAS_QT else None
    
    def create_dialog(self) -> QDialog:
        """Create and return the configuration dialog"""
        if self._dialog is not None:
            return self._dialog
        
        self._dialog = QDialog(self.parent)
        self._setup_dialog()
        self._setup_ui()
        self._load_current_config()
        return self._dialog
    
    def show_dialog(self) -> None:
        """Show the configuration dialog"""
        dialog = self.create_dialog()
        dialog.exec()
    
    def _setup_dialog(self) -> None:
        """Setup dialog properties"""
        dialog = self._dialog
        dialog.setWindowTitle("⚙️ Configuration")
        dialog.setFixedSize(700, 750)
        dialog.setWindowFlags(Qt.Dialog | Qt.WindowCloseButtonHint)
        
        # Apply theme
        dialog.setStyleSheet(self.theme_service.get_dialog_style())
    
    def _setup_ui(self) -> None:
        """Setup the user interface"""
        dialog = self._dialog
        main_layout = QVBoxLayout(dialog)
        main_layout.setContentsMargins(24, 24, 24, 24)
        main_layout.setSpacing(0)
        
        # Title
        title_label = QLabel("⚙️ Configuration")
        title_label.setStyleSheet(f"""
            font-size: 18px;
            color: {self.theme_service.get_color('primary')};
            font-weight: 600;
            margin: 8px 0;
        """)
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)
        
        # Scroll area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_area.setFrameShape(QScrollArea.NoFrame)
        
        # Content widget
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setSpacing(20)
        content_layout.setContentsMargins(0, 0, 20, 20)
        
        # Add sections
        content_layout.addWidget(self._create_cpp_section())
        content_layout.addWidget(self._create_workspace_section())
        content_layout.addWidget(self._create_ai_section())
        content_layout.addWidget(self._create_editor_section())
        content_layout.addStretch(1)
        
        scroll_area.setWidget(content_widget)
        main_layout.addWidget(scroll_area, 1)
        
        # Buttons
        button_container = self._create_button_container()
        main_layout.addWidget(button_container, 0)
    
    def _create_section_frame(self, title_text: str) -> tuple[QFrame, QVBoxLayout]:
        """Create a section frame with title"""
        frame = QFrame()
        frame.setObjectName("section_frame")
        frame.setStyleSheet(self.theme_service.get_section_style())
        
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
    
    def _create_cpp_section(self) -> QFrame:
        """Create C++ configuration section"""
        frame, layout = self._create_section_frame("🔧 C++ Version")
        
        # C++ version selection
        version_layout = QHBoxLayout()
        version_label = QLabel("C++ Standard:")
        version_label.setFixedWidth(120)
        
        self._cpp_version_combo = QComboBox()
        self._cpp_version_combo.addItems(["c++11", "c++14", "c++17", "c++20", "c++23"])
        
        version_layout.addWidget(version_label)
        version_layout.addWidget(self._cpp_version_combo)
        version_layout.addStretch()
        
        layout.addLayout(version_layout)
        return frame
    
    def _create_workspace_section(self) -> QFrame:
        """Create workspace configuration section"""
        frame, layout = self._create_section_frame("📁 Workspace")
        
        # Workspace folder selection
        workspace_layout = QHBoxLayout()
        workspace_label = QLabel("Workspace Folder:")
        workspace_label.setFixedWidth(120)
        
        self._workspace_edit = QLineEdit()
        browse_btn = QPushButton("Browse...")
        browse_btn.setStyleSheet(self.theme_service.get_button_style("secondary"))
        browse_btn.clicked.connect(self._browse_workspace)
        
        workspace_layout.addWidget(workspace_label)
        workspace_layout.addWidget(self._workspace_edit)
        workspace_layout.addWidget(browse_btn)
        
        layout.addLayout(workspace_layout)
        return frame
    
    def _create_ai_section(self) -> QFrame:
        """Create AI configuration section"""
        frame, layout = self._create_section_frame("🤖 AI Assistant")
        
        # AI enabled checkbox
        self._ai_enabled_check = QCheckBox("Enable AI Panel")
        layout.addWidget(self._ai_enabled_check)
        
        # API key input
        api_layout = QHBoxLayout()
        api_label = QLabel("Gemini API Key:")
        api_label.setFixedWidth(120)
        
        self._api_key_edit = QLineEdit()
        self._api_key_edit.setEchoMode(QLineEdit.Password)
        
        api_layout.addWidget(api_label)
        api_layout.addWidget(self._api_key_edit)
        
        layout.addLayout(api_layout)
        return frame
    
    def _create_editor_section(self) -> QFrame:
        """Create editor configuration section"""
        frame, layout = self._create_section_frame("✏️ Editor")
        
        # Auto-save checkbox
        self._auto_save_check = QCheckBox("Enable Auto-save")
        layout.addWidget(self._auto_save_check)
        
        return frame
    
    def _create_button_container(self) -> QWidget:
        """Create button container"""
        container = QWidget()
        container.setFixedHeight(72)
        
        layout = QHBoxLayout(container)
        layout.setContentsMargins(24, 18, 24, 18)
        layout.setSpacing(12)
        
        # Buttons
        reset_btn = QPushButton("Reset to Defaults")
        reset_btn.setStyleSheet(self.theme_service.get_button_style("secondary"))
        reset_btn.clicked.connect(self._reset_to_defaults)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setStyleSheet(self.theme_service.get_button_style("secondary"))
        cancel_btn.clicked.connect(self._dialog.reject)
        
        save_btn = QPushButton("Save Configuration")
        save_btn.setStyleSheet(self.theme_service.get_button_style("primary"))
        save_btn.clicked.connect(self._save_config)
        
        layout.addStretch(1)
        layout.addWidget(reset_btn)
        layout.addWidget(cancel_btn)
        layout.addWidget(save_btn)
        
        return container
    
    def _load_current_config(self) -> None:
        """Load current configuration into UI"""
        try:
            # Load configuration from service
            ai_settings = self.config_service.get_ai_settings()
            compiler_settings = self.config_service.get_compiler_settings()
            app_settings = self.config_service.get_app_settings()
            
            # Populate UI controls
            if self._cpp_version_combo:
                index = self._cpp_version_combo.findText(compiler_settings.cpp_version)
                if index >= 0:
                    self._cpp_version_combo.setCurrentIndex(index)
            
            if self._workspace_edit:
                self._workspace_edit.setText(app_settings.workspace_folder)
            
            if self._ai_enabled_check:
                self._ai_enabled_check.setChecked(ai_settings.enabled)
            
            if self._api_key_edit:
                self._api_key_edit.setText(ai_settings.api_key)
            
            if self._auto_save_check:
                self._auto_save_check.setChecked(app_settings.auto_save)
                
        except Exception as e:
            QMessageBox.warning(self._dialog, "Configuration Error", f"Failed to load configuration: {str(e)}")
    
    def _save_config(self) -> None:
        """Save configuration using service"""
        try:
            # Create settings objects from UI
            ai_settings = AISettings(
                enabled=self._ai_enabled_check.isChecked() if self._ai_enabled_check else False,
                api_key=self._api_key_edit.text() if self._api_key_edit else "",
                use_ai_panel=self._ai_enabled_check.isChecked() if self._ai_enabled_check else False
            )
            
            compiler_settings = CompilerSettings(
                cpp_version=self._cpp_version_combo.currentText() if self._cpp_version_combo else "c++17"
            )
            
            workspace_path = Path(self._workspace_edit.text()) if self._workspace_edit and self._workspace_edit.text() else Path.cwd()
            
            # Save using services
            results = [
                self.config_service.update_ai_settings(ai_settings),
                self.config_service.update_compiler_settings(compiler_settings),
                self.config_service.update_workspace_path(workspace_path)
            ]
            
            # Check for errors
            failed_results = [r for r in results if not r.success]
            if failed_results:
                error_messages = [r.error_message for r in failed_results]
                QMessageBox.critical(self._dialog, "Save Error", f"Failed to save configuration:\\n{'; '.join(error_messages)}")
                return
            
            # Success
            QMessageBox.information(self._dialog, "Configuration Saved", "Configuration saved successfully!")
            self._dialog.accept()
            
        except Exception as e:
            QMessageBox.critical(self._dialog, "Save Error", f"Unexpected error: {str(e)}")
    
    def _reset_to_defaults(self) -> None:
        """Reset configuration to defaults"""
        reply = QMessageBox.question(
            self._dialog,
            "Reset Configuration",
            "Are you sure you want to reset all settings to defaults?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # Reset UI to default values
            if self._cpp_version_combo:
                self._cpp_version_combo.setCurrentText("c++17")
            if self._workspace_edit:
                self._workspace_edit.setText("")
            if self._ai_enabled_check:
                self._ai_enabled_check.setChecked(False)
            if self._api_key_edit:
                self._api_key_edit.setText("")
            if self._auto_save_check:
                self._auto_save_check.setChecked(True)
    
    def _browse_workspace(self) -> None:
        """Browse for workspace folder"""
        folder = QFileDialog.getExistingDirectory(
            self._dialog,
            "Select Workspace Folder",
            self._workspace_edit.text() if self._workspace_edit else ""
        )
        
        if folder and self._workspace_edit:
            self._workspace_edit.setText(folder)
