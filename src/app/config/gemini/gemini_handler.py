"""
Gemini Configuration Handler

Single file to handle all Gemini API configuration:
- API key validation
- Model discovery and selection  
- Configuration persistence
- UI integration for config dialog
"""

import json
import os
import threading
import time
import logging
from typing import Tuple, List, Optional
from PySide6.QtCore import QThread, Signal
from PySide6.QtWidgets import QComboBox, QLineEdit

# Import CONFIG_FILE constant
from src.app.constants import CONFIG_FILE


class GeminiModelDiscoveryThread(QThread):
    """Thread for discovering available Gemini models."""
    
    models_discovered = Signal(list)  # List of model names
    discovery_failed = Signal(str)    # Error message
    
    def __init__(self, api_key: str):
        super().__init__()
        self.api_key = api_key
    
    def run(self):
        """Discover available models in background thread."""
        try:
            import google.generativeai as genai
            genai.configure(api_key=self.api_key)
            
            models = []
            for model in genai.list_models():
                if ('generateContent' in model.supported_generation_methods and 
                    model.name.startswith('models/gemini')):
                    model_name = model.name.replace('models/', '')
                    models.append(model_name)
            
            # Sort by preference: 1.5-flash (latest) -> 1.0-pro -> others
            def model_priority(name):
                priority = 0
                if '1.5' in name:
                    priority += 100
                elif '1.0' in name:
                    priority += 50
                    
                if 'flash' in name:
                    priority += 20
                elif 'pro' in name:
                    priority += 10
                    
                if 'latest' in name:
                    priority += 5
                    
                return priority
            
            models.sort(key=model_priority, reverse=True)
            self.models_discovered.emit(models)
            
        except Exception as e:
            self.discovery_failed.emit(f"Model discovery failed: {str(e)}")


class GeminiConfig:
    """Complete Gemini configuration handler."""
    
    def __init__(self, config_file_path: str = None):
        """Initialize with optional config file path."""
        self.config_file = config_file_path or CONFIG_FILE
        self._current_api_key = None
        self._available_models = []
        self._selected_model = None
        
    def validate_api_key_format(self, api_key: str) -> Tuple[bool, str]:
        """Quick format validation without network calls."""
        if not api_key:
            return False, "No API key provided"
            
        if len(api_key) < 20:
            return False, "API key too short"
            
        if len(api_key) > 100:
            return False, "API key too long"
            
        if not api_key.startswith("AIzaSy"):
            return False, "Invalid format (should start with 'AIzaSy')"
            
        if not api_key.replace('_', '').replace('-', '').isalnum():
            return False, "Contains invalid characters"
            
        return True, "Format valid"
    
    def validate_api_key_network(self, api_key: str, timeout: float = 3.0) -> Tuple[bool, str]:
        """Validate API key with network test."""
        # First check format
        format_valid, format_msg = self.validate_api_key_format(api_key)
        if not format_valid:
            return False, format_msg
            
        # Network validation with timeout
        result = {"success": False, "message": "Validation failed", "completed": False}
        
        def validation_worker():
            try:
                import google.generativeai as genai
                genai.configure(api_key=api_key)
                
                # Try to list models - will fail if key is invalid
                list(genai.list_models())
                
                result["success"] = True
                result["message"] = "API key is valid"
                result["completed"] = True
                
            except Exception as e:
                result["completed"] = True
                error_msg = str(e).lower()
                
                if "invalid api key" in error_msg or "invalid argument" in error_msg:
                    result["message"] = "Invalid API key"
                elif "permission denied" in error_msg or "forbidden" in error_msg:
                    result["message"] = "Permission denied"
                elif "quota" in error_msg or "rate limit" in error_msg:
                    result["message"] = "Quota exceeded (key is valid)"
                    result["success"] = True
                else:
                    result["message"] = f"Validation error: {str(e)}"
        
        # Run in thread with timeout
        worker_thread = threading.Thread(target=validation_worker, daemon=True)
        worker_thread.start()
        
        start_time = time.time()
        while not result["completed"] and (time.time() - start_time) < timeout:
            time.sleep(0.1)
            
        if not result["completed"]:
            return True, "Format valid (network timeout)"
            
        return result["success"], result["message"]
    
    def discover_models_async(self, api_key: str) -> GeminiModelDiscoveryThread:
        """Start async model discovery and return thread."""
        thread = GeminiModelDiscoveryThread(api_key)
        return thread
    
    def get_preferred_model(self, available_models: List[str]) -> Optional[str]:
        """Get the preferred model from available models using priority logic."""
        if not available_models:
            return None
            
        # Priority order: gemini-1.5-flash-latest -> gemini-1.5-pro -> gemini-1.0-pro-latest
        priority_models = [
            'gemini-1.5-flash-latest',
            'gemini-1.5-flash', 
            'gemini-1.5-pro-latest',
            'gemini-1.5-pro',
            'gemini-1.0-pro-latest',
            'gemini-1.0-pro',
            'gemini-pro'
        ]
        
        # Find first available model from priority list
        for preferred in priority_models:
            if preferred in available_models:
                return preferred
                
        # If none found, return first available
        return available_models[0] if available_models else None
    
    def validate_model_selection(self, api_key: str, model_name: str) -> Tuple[bool, str]:
        """Validate that the selected model works with the API key."""
        if not model_name:
            return False, "No model selected"
            
        try:
            import google.generativeai as genai
            genai.configure(api_key=api_key)
            
            # Try to create the model
            model = genai.GenerativeModel(model_name)
            
            return True, "Model is valid"
            
        except Exception as e:
            return False, f"Model validation failed: {str(e)}"
    
    def save_config(self, api_key: str, model_name: str, enabled: bool = True) -> bool:
        """Save configuration to JSON file."""
        if not self.config_file:
            return False
            
        try:
            config_data = {
                "gemini": {
                    "api_key": api_key,
                    "model": model_name,
                    "enabled": enabled
                }
            }
            
            # Try to load existing config and update
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    existing_config = json.load(f)
                existing_config.update(config_data)
                config_data = existing_config
            except (FileNotFoundError, json.JSONDecodeError):
                pass
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=2, ensure_ascii=False)
                
            logging.info(f"Gemini config saved: model={model_name}, enabled={enabled}")
            return True
            
        except Exception as e:
            logging.error(f"Failed to save config: {e}")
            return False
    
    def migrate_from_old_format(self) -> bool:
        """Migrate configuration from old ai_settings format to new gemini format."""
        if not self.config_file or not os.path.exists(self.config_file):
            return False
            
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
                
            # Check if already has gemini format
            if 'gemini' in config:
                return True
                
            # Check for old format
            ai_settings = config.get('ai_settings', {})
            if not ai_settings:
                return False
                
            api_key = ai_settings.get('gemini_api_key', '').strip()
            model_name = ai_settings.get('preferred_model', '').strip()
            enabled = ai_settings.get('use_ai_panel', False)
            
            if not api_key:
                return False
                
            # Set default model if none specified
            if not model_name:
                model_name = 'gemini-1.5-flash-latest'
            
            # Save in new format
            return self.save_config(api_key, model_name, enabled)
            
        except Exception as e:
            logging.error(f"Failed to migrate config: {e}")
            return False
    
    def load_config(self) -> Tuple[Optional[str], Optional[str], bool]:
        """Load configuration from JSON file."""
        if not self.config_file:
            return None, None, False
            
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
                
            gemini_config = config_data.get("gemini", {})
            api_key = gemini_config.get("api_key")
            model_name = gemini_config.get("model") 
            enabled = gemini_config.get("enabled", False)
            
            return api_key, model_name, enabled
            
        except (FileNotFoundError, json.JSONDecodeError, KeyError) as e:
            logging.info(f"No valid config found: {e}")
            return None, None, False
    
    def get_fallback_models(self) -> List[str]:
        """Get fallback model list when discovery fails."""
        return [
            'gemini-1.5-flash-latest',
            'gemini-1.5-flash',
            'gemini-1.5-pro-latest', 
            'gemini-1.5-pro',
            'gemini-1.0-pro-latest',
            'gemini-1.0-pro',
            'gemini-pro'
        ]


class GeminiConfigUI:
    """UI helper methods for Gemini configuration dialog."""
    
    @staticmethod
    def setup_model_dropdown(combo_box: QComboBox, models: List[str], 
                           preferred_model: Optional[str] = None):
        """Setup the model selection dropdown."""
        combo_box.clear()
        combo_box.addItems(models)
        
        # Select preferred model if available
        if preferred_model and preferred_model in models:
            index = models.index(preferred_model)
            combo_box.setCurrentIndex(index)
    
    @staticmethod
    def get_status_styles():
        """Get CSS styles for validation status indicators."""
        return {
            'loading': "color: #FF9800; font-weight: bold;",
            'success': "color: #4CAF50; font-weight: bold;", 
            'error': "color: #F44336; font-weight: bold;",
            'neutral': "color: #757575; font-weight: normal;"
        }
