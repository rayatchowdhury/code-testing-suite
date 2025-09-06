# -*- coding: utf-8 -*-
"""
AI Module for Code Testing Suite.

Simple Gemini AI integration that reads from JSON config.
"""

from .gemini_client import (
    GeminiAI, get_gemini_client, initialize_gemini, is_gemini_available,
    is_gemini_ready, is_ai_enabled, get_api_key, get_selected_model,
    is_ai_ready, should_show_ai_panel, get_ai_status_message
)

__all__ = [
    'GeminiAI', 'get_gemini_client', 'initialize_gemini', 'is_gemini_available',
    'is_gemini_ready', 'is_ai_enabled', 'get_api_key', 'get_selected_model',
    'is_ai_ready', 'should_show_ai_panel', 'get_ai_status_message'
]
