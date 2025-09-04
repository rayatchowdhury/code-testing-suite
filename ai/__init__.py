# -*- coding: utf-8 -*-
"""
AI Module for Code Testing Suite.

This module provides AI-powered code assistance using Google's Gemini API.
It includes model management, prompt templates, and response processing.
"""

from .core.editor_ai import EditorAI
from .models.model_manager import ModelManager
from .templates.prompt_templates import PromptTemplates

__all__ = ['EditorAI', 'ModelManager', 'PromptTemplates']
