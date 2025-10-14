"""
Shared module for the Code Testing Suite.

This module contains shared utilities, constants, and common functionality.
"""

# Re-export everything for convenient access
# Import all constants
from .constants import *
from .constants import __all__ as constants_all

# Import all utils
from .utils import FileOperations

__all__ = constants_all + ["FileOperations"]
