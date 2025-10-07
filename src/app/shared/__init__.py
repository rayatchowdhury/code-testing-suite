"""
Shared module for the Code Testing Suite.

This module contains shared utilities, constants, and common functionality.
"""

# Import all constants
from .constants import *

# Import all utils  
from .utils import FileOperations

# Re-export everything for convenient access
from .constants import __all__ as constants_all

__all__ = constants_all + [
    'FileOperations'
]
