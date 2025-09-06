"""
Enhanced Gemini AI Client with Configuration Management

Consolidated client that handles both configuration management and API interaction.
Single source of truth for all AI functionality.
"""

import json
import logging
import os
from typing import Optional, Dict, Any, Tuple
from pathlib import Path


class GeminiAI:
    """
    Unified Gemini AI client with configuration management.
    
    Handles both config reading and API interaction in one place.
    Single source of truth for AI availability and functionality.
    """
    
    def __init__(self, config_file_path: str = None):
        """Initialize with path to config JSON file."""
        # Import CONFIG_FILE from constants, fallback if not available
        try:
            from ...constants import CONFIG_FILE
            self.config_file = config_file_path or CONFIG_FILE
        except ImportError:
            self.config_file = config_file_path
        self.model = None
        self._is_configured = False
        self._api_key = None
        self._model_name = None
        self._enabled = False
        
    def load_from_config(self) -> bool:
        """Load and initialize from JSON config file."""
        if not self._load_config_data():
            return False
            
        if not self._enabled:
            logging.info("Gemini AI is disabled in config")
            return False
            
        if not self._api_key or not self._model_name:
            logging.error("Missing API key or model in config")
            return False
            
        return self._initialize_model()
    
    def _load_config_data(self) -> bool:
        """Load configuration data from JSON file."""
        if not self.config_file or not Path(self.config_file).exists():
            logging.warning("No config file found")
            return False
            
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
            
            # Try new format first (gemini section)
            gemini_config = config_data.get("gemini", {})
            if gemini_config:
                self._api_key = gemini_config.get("api_key")
                self._model_name = gemini_config.get("model")
                self._enabled = gemini_config.get("enabled", False)
                return True
            
            # Fallback to old format (ai_settings section)
            ai_settings = config_data.get('ai_settings', {})
            if ai_settings:
                self._api_key = ai_settings.get('gemini_api_key')
                self._model_name = ai_settings.get('preferred_model', 'gemini-1.5-flash-latest')
                self._enabled = ai_settings.get('use_ai_panel', False)
                return True
                
            return False
            
        except Exception as e:
            logging.error(f"Failed to load config: {e}")
            return False
    
    def _initialize_model(self) -> bool:
        """Initialize the Google Generative AI model."""
        try:
            import google.generativeai as genai
            genai.configure(api_key=self._api_key)
            self.model = genai.GenerativeModel(self._model_name)
            self._is_configured = True
            logging.info(f"Gemini AI initialized: {self._model_name}")
            return True
            
        except Exception as e:
            logging.error(f"Failed to initialize model: {e}")
            return False
    
    def is_available(self) -> bool:
        """Check if AI is available and configured."""
        return self._is_configured and self.model is not None
    
    def is_enabled(self) -> bool:
        """Check if AI is enabled in configuration."""
        if not self._load_config_data():
            return False
        return self._enabled
    
    def get_api_key(self) -> Optional[str]:
        """Get the configured API key."""
        if not self._load_config_data():
            return None
        return self._api_key
    
    def get_model_name(self) -> Optional[str]:
        """Get the configured model name."""
        if not self._load_config_data():
            return None
        return self._model_name
    
    def is_ready(self) -> Tuple[bool, str]:
        """
        Check if AI is ready to use.
        Returns: (is_ready, message)
        """
        if not self._load_config_data():
            return False, "No configuration found"
            
        if not self._enabled:
            return False, "AI Panel is disabled in settings"
        
        if not self._api_key:
            return False, "No API key provided"
        
        if len(self._api_key) < 30:  # Basic validation
            return False, "API key appears to be invalid"
        
        if not self._model_name:
            return False, "No AI model selected"
        
        # Try to initialize if not already done
        if not self.is_available():
            if not self._initialize_model():
                return False, "AI model initialization failed"
        
        return True, "AI is ready"
    
    def get_status_message(self) -> str:
        """Get a user-friendly status message."""
        is_ready, message = self.is_ready()
        
        if is_ready:
            return "🤖 AI Assistant Ready"
        elif self.is_enabled():
            return f"⚠️ AI Panel Enabled - {message}"
        else:
            return "🔒 AI Panel Disabled"
    
    def generate_response(self, prompt: str) -> Optional[str]:
        """Generate response using the configured model."""
        if not self.is_available():
            logging.warning("AI not available - check configuration")
            return None
            
        try:
            response = self.model.generate_content(prompt)
            return response.text
            
        except Exception as e:
            logging.error(f"Failed to generate response: {e}")
            return None
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the current model."""
        return {
            "model_name": self._model_name or 'Unknown',
            "is_configured": self._is_configured,
            "is_enabled": self._enabled,
            "has_api_key": bool(self._api_key),
            "config_file": self.config_file
        }
    
    def refresh_config(self) -> bool:
        """Refresh configuration from file."""
        self._is_configured = False
        self.model = None
        return self.load_from_config()


# Global instance for easy access
_gemini_client = None

def get_gemini_client(config_file: str = None) -> GeminiAI:
    """Get or create global Gemini client instance."""
    global _gemini_client
    
    if _gemini_client is None:
        _gemini_client = GeminiAI(config_file)
    
    return _gemini_client

def initialize_gemini(config_file: str) -> bool:
    """Initialize global Gemini client from config file."""
    client = get_gemini_client(config_file)
    return client.load_from_config()

def is_gemini_available() -> bool:
    """Check if global Gemini client is available."""
    return _gemini_client is not None and _gemini_client.is_available()

def is_gemini_ready() -> Tuple[bool, str]:
    """Check if global Gemini client is ready."""
    if _gemini_client is None:
        return False, "AI not initialized"
    return _gemini_client.is_ready()

# Backward compatibility aliases for AIConfig methods
def is_ai_enabled() -> bool:
    """Check if AI panel is enabled in configuration."""
    client = get_gemini_client()
    return client.is_enabled()

def get_api_key() -> Optional[str]:
    """Get the Gemini API key if available."""
    client = get_gemini_client()
    return client.get_api_key()

def get_selected_model() -> Optional[str]:
    """Get the selected Gemini model if available."""
    client = get_gemini_client()
    return client.get_model_name()

def is_ai_ready() -> Tuple[bool, str]:
    """Check if AI is ready to use."""
    client = get_gemini_client()
    return client.is_ready()

def should_show_ai_panel() -> bool:
    """Check if AI panel should be shown in UI."""
    return is_ai_enabled()

def get_ai_status_message() -> str:
    """Get a user-friendly status message about AI configuration."""
    client = get_gemini_client()
    return client.get_status_message()
