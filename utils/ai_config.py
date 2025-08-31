"""
AI Configuration Utility

Provides centralized access to AI settings and validation.
"""

import os
import json
from typing import Tuple, Optional

class AIConfig:
    """Utility class for managing AI configuration across the application"""
    
    CONFIG_DIR = os.path.join(os.path.expanduser('~'), '.code_testing_suite')
    CONFIG_FILE = os.path.join(CONFIG_DIR, 'config.json')
    
    @classmethod
    def is_ai_enabled(cls) -> bool:
        """Check if AI panel is enabled in configuration"""
        try:
            config = cls._load_config()
            ai_settings = config.get('ai_settings', {})
            return ai_settings.get('use_ai_panel', False)
        except:
            return False
    
    @classmethod
    def get_api_key(cls) -> Optional[str]:
        """Get the Gemini API key if available"""
        try:
            config = cls._load_config()
            ai_settings = config.get('ai_settings', {})
            key = ai_settings.get('gemini_api_key', '')
            return key if key else None
        except:
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
