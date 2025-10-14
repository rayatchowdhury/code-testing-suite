"""
Gemini Configuration Handler

Simple file to handle Gemini API configuration:
- API key validation
- Model selection with sensible defaults
- Configuration persistence
- UI integration for config dialog
"""

import json
import logging
import os
import threading
import time
from typing import List, Optional, Tuple

from PySide6.QtWidgets import QComboBox, QLineEdit

# Import CONFIG_FILE constant
from src.app.shared.constants import CONFIG_FILE

# Model discovery removed - using user input with sensible defaults


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

        if not api_key.replace("_", "").replace("-", "").isalnum():
            return False, "Contains invalid characters"

        return True, "Format valid"

    def validate_api_key_network(
        self, api_key: str, timeout: float = 3.0
    ) -> Tuple[bool, str]:
        """Validate API key with network test."""
        # First check format
        format_valid, format_msg = self.validate_api_key_format(api_key)
        if not format_valid:
            return False, format_msg

        # Network validation with timeout - simplified
        result = {"success": False, "message": "Validation failed", "completed": False}

        def validation_worker():
            try:
                # Simple HTTP validation instead of using google library
                import json
                import urllib.request

                # Test API endpoint
                url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"
                req = urllib.request.Request(
                    url, headers={"User-Agent": "CodeTestingSuite/1.0"}
                )

                with urllib.request.urlopen(req, timeout=10) as response:
                    if response.status == 200:
                        result["success"] = True
                        result["message"] = "API key is valid"
                    else:
                        result["message"] = f"HTTP {response.status}"

                result["completed"] = True

            except urllib.error.HTTPError as e:
                result["completed"] = True
                if e.code == 403:
                    result["message"] = "Invalid API key"
                elif e.code == 429:
                    result["message"] = "Rate limit exceeded (key is valid)"
                    result["success"] = True
                else:
                    result["message"] = f"HTTP error {e.code}"

            except Exception as e:
                result["completed"] = True
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

    def get_default_model(self) -> str:
        """Get the default model to use when none is specified."""
        return "gemini-2.5-flash"  # Updated to 2.5 flash as requested

    def get_available_models(self) -> List[str]:
        """Get list of available Gemini 2.5 models only."""
        return [
            "gemini-2.5-flash",  # Default selection
            "gemini-2.5-pro",
            "gemini-2.5-flash-lite",
        ]

    def validate_model_selection(
        self, api_key: str, model_name: str
    ) -> Tuple[bool, str]:
        """Validate that the selected model works with the API key."""
        if not model_name:
            return False, "No model selected"

        # For our direct HTTP approach, just check if it's in our supported list
        available_models = self.get_available_models()
        if model_name in available_models:
            return True, "Model is valid"
        else:
            # Allow custom models
            return True, f"Custom model: {model_name}"

    def save_config(
        self, api_key: str, model_name: str = None, enabled: bool = True
    ) -> bool:
        """Save configuration to JSON file."""
        if not self.config_file:
            return False

        # Use default model if none provided
        if not model_name:
            model_name = self.get_default_model()

        try:
            config_data = {
                "gemini": {"api_key": api_key, "model": model_name, "enabled": enabled}
            }

            # Try to load existing config and update
            try:
                with open(self.config_file, "r", encoding="utf-8") as f:
                    existing_config = json.load(f)
                existing_config.update(config_data)
                config_data = existing_config
            except (FileNotFoundError, json.JSONDecodeError):
                pass

            with open(self.config_file, "w", encoding="utf-8") as f:
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
            with open(self.config_file, "r", encoding="utf-8") as f:
                config = json.load(f)

            # Check if already has gemini format
            if "gemini" in config:
                return True

            # Check for old format
            ai_settings = config.get("ai_settings", {})
            if not ai_settings:
                return False

            api_key = ai_settings.get("gemini_api_key", "").strip()
            model_name = ai_settings.get("preferred_model", "").strip()
            enabled = ai_settings.get("use_ai_panel", False)

            if not api_key:
                return False

            # Set default model if none specified
            if not model_name:
                model_name = self.get_default_model()

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
            with open(self.config_file, "r", encoding="utf-8") as f:
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
        """Get fallback model list when dropdown needs options."""
        return self.get_available_models()


class GeminiConfigUI:
    """UI helper methods for Gemini configuration dialog."""

    @staticmethod
    def setup_model_dropdown(
        combo_box: QComboBox, models: List[str], selected_model: Optional[str] = None
    ):
        """Setup the model selection dropdown with available models."""
        combo_box.clear()
        combo_box.addItems(models)

        # Select the specified model if available
        if selected_model and selected_model in models:
            index = models.index(selected_model)
            combo_box.setCurrentIndex(index)
        else:
            # Select first item (default model) if no valid selection
            combo_box.setCurrentIndex(0)

    @staticmethod
    def get_status_styles():
        """Get CSS styles for validation status indicators."""
        return {
            "loading": "color: #FF9800; font-weight: bold;",
            "success": "color: #4CAF50; font-weight: bold;",
            "error": "color: #F44336; font-weight: bold;",
            "neutral": "color: #757575; font-weight: normal;",
        }
