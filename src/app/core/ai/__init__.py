# -*- coding: utf-8 -*-
"""
AI Module for Code Testing Suite.

Comprehensive AI integration with Gemini client, EditorAI processing,
and template-based prompt generation.

Public API:
- AI Client: get_ai_client(), initialize_ai(), is_ai_available(), is_ai_ready()
- AI Processing: get_editor_ai(), process_code()
- Status Checks: should_show_ai_panel(), get_ai_status(), check_ai_status()
- Templates: get_prompt_templates()
"""

# Core AI Client
from src.app.core.ai.gemini_client import (
    GeminiAI,
    get_gemini_client,
    initialize_gemini,
    is_gemini_available,
    is_gemini_ready,
    is_ai_enabled,
    get_api_key,
    get_selected_model,
    is_ai_ready,
    should_show_ai_panel,
    get_ai_status_message
)

# EditorAI Processing
from src.app.core.ai.core.editor_ai import EditorAI

# Template System
from src.app.core.ai.templates.prompt_templates import PromptTemplates


# Public API Functions
def get_ai_client(config_file: str = None) -> GeminiAI:
    """Get the main AI client instance."""
    return get_gemini_client(config_file)


def initialize_ai(config_file: str = None) -> bool:
    """Initialize the AI system from configuration."""
    if config_file:
        return initialize_gemini(config_file)
    
    # Try to initialize with default config
    try:
        from src.app.constants import CONFIG_FILE
        return initialize_gemini(CONFIG_FILE)
    except Exception:
        return False


def is_ai_available() -> bool:
    """Check if AI is available and configured."""
    return is_gemini_available()


def get_editor_ai(config_file: str = None) -> EditorAI:
    """Get an EditorAI instance for code processing."""
    return EditorAI(config_file)


def process_code(action: str, code: str, config_file: str = None) -> str:
    """Process code using EditorAI with the specified action."""
    editor_ai = get_editor_ai(config_file)
    return editor_ai.process_code(action, code)


def check_ai_status() -> dict:
    """Get comprehensive AI status information."""
    is_ready, message = is_ai_ready()
    
    return {
        "ready": is_ready,
        "message": message,
        "enabled": is_ai_enabled(),
        "available": is_ai_available(),
        "show_panel": should_show_ai_panel(),
        "status_text": get_ai_status_message(),
        "has_api_key": bool(get_api_key()),
        "selected_model": get_selected_model()
    }


def get_ai_status() -> str:
    """Get user-friendly AI status message."""
    return get_ai_status_message()


def get_prompt_templates() -> PromptTemplates:
    """Get the prompt templates system."""
    return PromptTemplates


# Backward compatibility aliases
def get_gemini_ai(config_file: str = None) -> GeminiAI:
    """Alias for get_ai_client() for backward compatibility."""
    return get_ai_client(config_file)


# Hide internal modules from public API
import sys
_current_module = sys.modules[__name__]

# Remove internal modules from public interface
for _internal in ['core', 'gemini_client', 'templates']:
    if hasattr(_current_module, _internal):
        delattr(_current_module, _internal)

del sys, _current_module, _internal

# Export all public functions
__all__ = [
    # Core Classes
    'GeminiAI',
    'EditorAI', 
    'PromptTemplates',
    
    # Main API Functions
    'get_ai_client',
    'initialize_ai',
    'is_ai_available',
    'get_editor_ai',
    'process_code',
    'check_ai_status',
    'get_ai_status',
    'get_prompt_templates',
    
    # Status Functions
    'is_ai_ready',
    'should_show_ai_panel',
    'is_ai_enabled',
    'get_api_key',
    'get_selected_model',
    'get_ai_status_message',
    
    # Low-level Functions
    'get_gemini_client',
    'initialize_gemini',
    'is_gemini_available',
    'is_gemini_ready',
    
    # Backward Compatibility
    'get_gemini_ai'
]
