"""
Constants package for Code Testing Suite.

This package contains all application constants including paths, 
configuration defaults, and other shared values.
"""

from .paths import (
    PROJECT_ROOT,
    SRC_ROOT,
    RESOURCES_DIR,
    ICONS_DIR,
    README_DIR,
    TEMPLATES_DIR,
    DOCS_DIR,
    APP_ICON,
    SETTINGS_ICON,
    CHECK_ICON,
    LOGO_ICON,
    USER_DATA_DIR,
    WORKSPACE_DIR,
    CONFIG_FILE,
    EDITOR_STATE_FILE,
    MAIN_WINDOW_HTML,
    EDITOR_WELCOME_HTML,
    HTML_CSS,
    HELP_CONTENT_DIR,
    ensure_user_data_dir,
    get_icon_path,
    get_help_content_path
)

__all__ = [
    # Path constants
    'PROJECT_ROOT',
    'SRC_ROOT',
    'RESOURCES_DIR', 
    'ICONS_DIR',
    'README_DIR',
    'TEMPLATES_DIR',
    'DOCS_DIR',
    'APP_ICON',
    'SETTINGS_ICON',
    'CHECK_ICON',
    'LOGO_ICON',
    'USER_DATA_DIR',
    'WORKSPACE_DIR',
    'CONFIG_FILE',
    'EDITOR_STATE_FILE',
    'MAIN_WINDOW_HTML',
    'EDITOR_WELCOME_HTML',
    'HTML_CSS',
    'HELP_CONTENT_DIR',
    
    # Utility functions
    'ensure_user_data_dir',
    'get_icon_path',
    'get_help_content_path'
]
