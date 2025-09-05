"""
AI Configuration Utility

Provides centralized access to AI settings and validation.
"""

import os
import json
from typing import Tuple, Optional
from constants import USER_DATA_DIR, CONFIG_FILE

class AIConfig:
    """Utility class for managing AI configuration across the application"""
    
    CONFIG_DIR = USER_DATA_DIR
    CONFIG_FILE = CONFIG_FILE
    
    @classmethod
    def is_ai_enabled(cls) -> bool:
        """Check if AI panel is enabled in configuration"""
        try:
            config = cls._load_config()
            ai_settings = config.get('ai_settings', {})
            return ai_settings.get('use_ai_panel', False)
        except (FileNotFoundError, json.JSONDecodeError, KeyError) as e:
            return False
    
    @classmethod
    def get_api_key(cls) -> Optional[str]:
        """Get the Gemini API key if available"""
        try:
            config = cls._load_config()
            ai_settings = config.get('ai_settings', {})
            key = ai_settings.get('gemini_api_key', '')
            return key if key else None
        except (FileNotFoundError, json.JSONDecodeError, KeyError) as e:
            return None
    
    @classmethod
    def is_ai_ready(cls) -> Tuple[bool, str]:
        """
        Check if AI is ready to use
        Returns: (is_ready, message)
        """
        if not cls.is_ai_enabled():
            return False, "AI Panel is disabled in settings"
        
        api_key = cls.get_api_key()
        if not api_key:
            return False, "No API key provided"
        
        if len(api_key) < 30:  # Basic validation
            return False, "API key appears to be invalid"
        
        return True, "AI is ready"
    
    @classmethod
    def should_show_ai_panel(cls) -> bool:
        """Check if AI panel should be shown in UI"""
        return cls.is_ai_enabled()
    
    @classmethod
    def _load_config(cls) -> dict:
        """Load configuration from file"""
        if not os.path.exists(cls.CONFIG_FILE):
            return {}
        
        with open(cls.CONFIG_FILE, 'r') as f:
            return json.load(f)
    
    @classmethod
    def get_ai_status_message(cls) -> str:
        """Get a user-friendly status message about AI configuration"""
        is_ready, message = cls.is_ai_ready()
        
        if is_ready:
            return "🤖 AI Assistant Ready"
        elif cls.is_ai_enabled():
            return f"⚠️ AI Panel Enabled - {message}"
        else:
            return "🔒 AI Panel Disabled"

    @classmethod
    def refresh_ai_model(cls) -> Tuple[bool, str]:
        """
        Refresh the AI model by recreating the EditorAI instance
        Returns: (success, message)
        """
        try:
            from ai.core.editor_ai import EditorAI
            # Force a new instance to be created with fresh model discovery
            ai = EditorAI()
            if ai.model:
                model_name = ai.get_current_model_name()
                return True, f"AI model refreshed successfully: {model_name}"
            else:
                return False, "Failed to initialize AI model after refresh"
        except Exception as e:
            return False, f"Error refreshing AI model: {str(e)}"
