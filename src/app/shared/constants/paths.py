"""
Path constants for the Code Testing Suite application.

This module centralizes all file and directory paths to improve maintainability
and make the application more flexible for different deployment scenarios.
"""

import os
from pathlib import Path

# Project structure - updated for src layout  
# Navigate up from src/app/constants/paths.py to project root
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
SRC_ROOT = PROJECT_ROOT / "src"
RESOURCES_DIR = SRC_ROOT / "resources"
ICONS_DIR = RESOURCES_DIR / "icons"
README_DIR = RESOURCES_DIR / "readme"
TEMPLATES_DIR = RESOURCES_DIR / "templates"
DOCS_DIR = RESOURCES_DIR / "docs"

# Application icons
APP_ICON = str(ICONS_DIR / "app_icon.png")
SETTINGS_ICON = str(ICONS_DIR / "settings.png")
CHECK_ICON = str(ICONS_DIR / "check.png")
LOGO_ICON = str(ICONS_DIR / "logo.png")

# User data directories
USER_DATA_DIR = os.path.join(os.path.expanduser('~'), '.code_testing_suite')
WORKSPACE_DIR = os.path.join(USER_DATA_DIR, 'workspace')
CONFIG_FILE = os.path.join(USER_DATA_DIR, 'config.json')
EDITOR_STATE_FILE = os.path.join(USER_DATA_DIR, 'editor_state.json')

# HTML and CSS files
MAIN_WINDOW_HTML = PROJECT_ROOT / "views" / "main_window.html"
EDITOR_WELCOME_HTML = PROJECT_ROOT / "views" / "code_editor" / "editor_welcome.html"
HTML_CSS = PROJECT_ROOT / "styles" / "html.css"

# Help center content
HELP_CONTENT_DIR = PROJECT_ROOT / "views" / "help_center" / "content"

def ensure_user_data_dir():
    """Ensure user data directory exists."""
    os.makedirs(USER_DATA_DIR, exist_ok=True)

def get_icon_path(icon_name: str) -> str:
    """
    Get the full path to an icon file.
    
    Args:
        icon_name: Name of the icon file (with or without .png extension)
        
    Returns:
        Full path to the icon file
    """
    if not icon_name.endswith('.png'):
        icon_name += '.png'
    return str(ICONS_DIR / icon_name)

def get_help_content_path(content_name: str) -> str:
    """
    Get the full path to a help content file.
    
    Args:
        content_name: Name of the help content file
        
    Returns:
        Full path to the help content file
    """
    if not content_name.endswith('.html'):
        content_name += '.html'
    return str(HELP_CONTENT_DIR / content_name)
