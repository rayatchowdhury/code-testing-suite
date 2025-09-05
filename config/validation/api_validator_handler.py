"""API validation handling for configuration dialog."""

from PySide6.QtWidgets import QLineEdit, QMessageBox, QInputDialog
from PySide6.QtCore import QThread, Signal

from styles.constants.colors import MATERIAL_COLORS
from styles.components.config_ui import (
    get_error_status_style, 
    get_neutral_status_style,
    get_success_status_style
)
from utils.api_validator import APIValidator
from ..ui.error_dialog import ErrorDialog
import re


class ModelDiscoveryThread(QThread):
    """Thread for discovering available Gemini models."""
    
    discovered = Signal(list)
    error = Signal(str)
    
    def __init__(self, api_key):
        super().__init__()
        self.api_key = api_key
    
    def run(self):
        try:
            # Lazy import to avoid slow startup
            import google.generativeai as genai
            
            genai.configure(api_key=self.api_key)
            models = []
            for model in genai.list_models():
                if ('generateContent' in model.supported_generation_methods and 
                    model.name.startswith('models/gemini')):
                    model_name = model.name.replace('models/', '')
                    models.append(model_name)
            
            # Sort models by preference
            def model_priority(model_name):
                priority = 0
                version_match = re.search(r'(\d+)\.(\d+)', model_name)
                if version_match:
                    major, minor = map(int, version_match.groups())
                    priority += major * 100 + minor * 10
                if 'flash' in model_name:
                    priority += 20
                elif 'pro' in model_name:
                    priority += 15
                return priority
            
            models.sort(key=model_priority, reverse=True)
            self.discovered.emit(models)
        except Exception as e:
            self.error.emit(str(e))


class APIValidatorHandler:
    """Handles API validation for the configuration dialog."""
    
    def __init__(self, parent_dialog):
        self.parent = parent_dialog
        self.discovery_thread = None
        
    def on_ai_toggle(self, state):
        """Handle AI checkbox toggle with proper validation"""
        if state == 2:  # User wants to enable AI
            if not self.parent.is_key_valid:
                dialog = ErrorDialog(
                    "Valid API Key Required",
                    "Please enter and validate a Gemini API key before enabling the AI Panel.",
                    "The API key will be tested against Google's servers to ensure it works properly.",
                    self.parent
                )
                dialog.exec()
                
                self.parent.use_ai_checkbox.blockSignals(True)
                self.parent.use_ai_checkbox.setChecked(False)
                self.parent.use_ai_checkbox.blockSignals(False)
                return
        
        if state != 2:
            self.parent.status_label.clear()

    def on_key_changed(self, text):
        """Handle API key text changes"""
        if self.parent.validation_thread and self.parent.validation_thread.isRunning():
            self.parent.validation_thread.terminate()
            self.parent.validation_thread = None
        
        self.parent.is_key_valid = False
        self.parent.use_ai_checkbox.setEnabled(False)
        if self.parent.use_ai_checkbox.isChecked():
            self.parent.use_ai_checkbox.blockSignals(True)
            self.parent.use_ai_checkbox.setChecked(False)
            self.parent.use_ai_checkbox.blockSignals(False)
        
        if not text.strip():
            self.parent.status_label.clear()
            return
        
        format_ok, format_msg = APIValidator.quick_format_check(text)
        if not format_ok:
            self.parent.status_label.setText("⚠")
            self.parent.status_label.setStyleSheet(get_error_status_style())
            self.parent.status_label.setToolTip(format_msg)
            return
        
        self.parent.status_label.setText("⏳")
        self.parent.status_label.setStyleSheet(get_neutral_status_style())
        self.parent.status_label.setToolTip("Validating...")
        
        # Start validation using APIValidator
        self.parent.validation_thread = APIValidator.validate_key_async(text, self.on_validation_complete)

    def on_validation_complete(self, is_valid, message):
        """Handle API validation completion"""
        self.parent.is_key_valid = is_valid
        
        if is_valid:
            self.parent.status_label.setText("✓")
            self.parent.status_label.setStyleSheet(get_success_status_style())
            self.parent.status_label.setToolTip("API key validated successfully")
            self.parent.use_ai_checkbox.setEnabled(True)
        else:
            self.parent.status_label.setText("✗")
            self.parent.status_label.setStyleSheet(get_error_status_style())
            self.parent.status_label.setToolTip(f"Validation failed: {message}")
            self.parent.use_ai_checkbox.setEnabled(False)
            if self.parent.use_ai_checkbox.isChecked():
                self.parent.use_ai_checkbox.blockSignals(True)
                self.parent.use_ai_checkbox.setChecked(False)
                self.parent.use_ai_checkbox.blockSignals(False)

    def toggle_visibility(self):
        """Toggle API key visibility"""
        is_hidden = self.parent.key_input.echoMode() == QLineEdit.Password
        self.parent.key_input.setEchoMode(QLineEdit.Normal if is_hidden else QLineEdit.Password)
        self.parent.toggle_btn.setText("🔒" if is_hidden else "👁")

    def force_validation(self):
        """Force re-validation of the current API key"""
        current_key = self.parent.key_input.text().strip()
        if current_key:
            self.on_key_changed(current_key)

    def discover_models(self):
        """Discover available Gemini models"""
        api_key = self.parent.key_input.text().strip()
        if not api_key:
            QMessageBox.warning(self.parent, "API Key Required", "Please enter a valid API key first.")
            return
        
        self.discovery_thread = ModelDiscoveryThread(api_key)
        self.discovery_thread.discovered.connect(self.on_models_discovered)
        self.discovery_thread.error.connect(self.on_discovery_error)
        self.discovery_thread.start()
        
        # Update button to show loading
        self.parent.discover_btn.setText("⏳")
        self.parent.discover_btn.setEnabled(False)
    
    def on_models_discovered(self, models):
        """Handle successful model discovery"""        
        self.parent.discover_btn.setText("🔍")
        self.parent.discover_btn.setEnabled(True)
        
        if models:
            selected_model, ok = QInputDialog.getItem(
                self.parent, "Available Models", 
                "Select a model or click Cancel to keep current setting:",
                models, 0, False
            )
            if ok and selected_model:
                self.parent.model_input.setText(selected_model)
        else:
            QMessageBox.information(self.parent, "No Models", "No compatible models found.")
    
    def on_discovery_error(self, error):
        """Handle model discovery error"""
        self.parent.discover_btn.setText("🔍")
        self.parent.discover_btn.setEnabled(True)
        
        QMessageBox.warning(self.parent, "Discovery Failed", f"Failed to discover models:\n{error}")
