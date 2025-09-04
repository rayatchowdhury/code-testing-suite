"""
Compatibility layer for ConfigView.

This module provides backward compatibility for existing imports while 
redirecting to the new modular config structure.
"""

# Import from new modular location
from config import ConfigView

# Maintain backward compatibility
__all__ = ['ConfigView']
