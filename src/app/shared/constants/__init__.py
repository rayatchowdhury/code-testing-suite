"""
Constants package for Code Testing Suite.

This package contains all application constants including paths,
configuration defaults, and other shared values.
"""

from .paths import (  # EDITOR_WELCOME_HTML removed - file doesn't exist; HTML_CSS removed - not used in codebase
    APP_ICON,
    CHECK_ICON,
    CONFIG_FILE,
    DOCS_DIR,
    EDITOR_STATE_FILE,
    HELP_CONTENT_DIR,
    ICONS_DIR,
    LOGO_ICON,
    MAIN_WINDOW_HTML,
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
    "MAIN_WINDOW_HTML",
    # 'EDITOR_WELCOME_HTML' removed - file doesn't exist
    # 'HTML_CSS' removed - not used in codebase
    "HELP_CONTENT_DIR",
    # Utility functions
    "ensure_user_data_dir",
    "get_icon_path",
    "get_help_content_path",
]
