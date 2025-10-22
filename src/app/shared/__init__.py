"""
Shared module for the Code Testing Suite.

This module contains shared utilities, constants, and common functionality.
"""

# Re-export specific items for convenient access
# Import path constants and utilities
from .constants import (
    APP_ICON,
    CHECK_ICON,
    CONFIG_FILE,
    DOCS_DIR,
    EDITOR_STATE_FILE,
    HELP_CONTENT_DIR,
    ICONS_DIR,
    LOGO_ICON,
    PROJECT_ROOT,
    README_DIR,
    RESOURCES_DIR,
    SETTINGS_ICON,
    SRC_ROOT,
    TEMPLATES_DIR,
    USER_DATA_DIR,
    WORKSPACE_DIR,
    ensure_user_data_dir,
    get_help_content_path,
    get_icon_path,
)
from .utils import FileOperations

__all__ = [
    # Path constants
    "PROJECT_ROOT",
    "SRC_ROOT",
    "RESOURCES_DIR",
    "ICONS_DIR",
    "README_DIR",
    "TEMPLATES_DIR",
    "DOCS_DIR",
    "APP_ICON",
    "SETTINGS_ICON",
    "CHECK_ICON",
    "LOGO_ICON",
    "USER_DATA_DIR",
    "WORKSPACE_DIR",
    "CONFIG_FILE",
    "EDITOR_STATE_FILE",
    "HELP_CONTENT_DIR",
    # Utility functions
    "ensure_user_data_dir",
    "get_icon_path",
    "get_help_content_path",
    # Utils
    "FileOperations",
]
