# -*- coding: utf-8 -*-
"""
AI Module for Code Testing Suite.

Simple Gemini AI integration that reads from JSON config.
"""

from src.app.core.ai.gemini_client.gemini_client import (
    GeminiAI,
    get_gemini_client,
    initialize_gemini,
    is_gemini_available,
    is_gemini_ready,
    get_ai_key,
    get_ai_model,
    is_ai_ready,
    should_show_ai_panel,
    generate_ai_response,
    reload_ai_config,
)

__all__ = [
    "GeminiAI",
    "get_gemini_client",
    "initialize_gemini",
    "is_gemini_available",
    "is_gemini_ready",
    "get_ai_key",
    "get_ai_model",
    "is_ai_ready",
    "should_show_ai_panel",
    "generate_ai_response",
    "reload_ai_config",
]
