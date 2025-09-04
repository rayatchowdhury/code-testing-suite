# -*- coding: utf-8 -*-
"""
Legacy compatibility layer for EditorAI.

This file maintains backward compatibility while redirecting to the new modular structure.
The actual implementation is now in ai/core/editor_ai.py
"""

# Import from the new modular structure
from ai.core.editor_ai import EditorAI

# Re-export for backward compatibility
__all__ = ['EditorAI']
