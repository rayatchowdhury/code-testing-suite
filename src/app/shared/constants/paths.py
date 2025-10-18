"""
Path constants for the Code Testing Suite application.

This module centralizes all file and directory paths to improve maintainability
and make the application more flexible for different deployment scenarios.
"""

import os
from pathlib import Path

# Project structure - updated for src layout
# Navigate up from src/app/shared/constants/paths.py to project root
# __file__ -> paths.py, .parent -> constants/, .parent -> shared/, .parent -> app/, .parent -> src/, .parent -> project root
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent.parent
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
USER_DATA_DIR = os.path.join(os.path.expanduser("~"), ".code_testing_suite")
WORKSPACE_DIR = os.path.join(USER_DATA_DIR, "workspace")
CONFIG_FILE = os.path.join(USER_DATA_DIR, "config.json")
EDITOR_STATE_FILE = os.path.join(USER_DATA_DIR, "editor_state.json")

# Workspace subdirectories by test type (nested structure)
WORKSPACE_COMPARATOR_SUBDIR = "comparator"
WORKSPACE_VALIDATOR_SUBDIR = "validator"
WORKSPACE_BENCHMARKER_SUBDIR = "benchmarker"

# I/O subdirectories within each test type
WORKSPACE_INPUTS_SUBDIR = "inputs"
WORKSPACE_OUTPUTS_SUBDIR = "outputs"

# Test type aliases (normalized names)
TEST_TYPE_ALIASES = {
    "comparison": "comparator",
    "comparator": "comparator",
    "validator": "validator",
    "validation": "validator",
    "benchmark": "benchmarker",
    "benchmarker": "benchmarker",
}

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
    if not icon_name.endswith(".png"):
        icon_name += ".png"
    return str(ICONS_DIR / icon_name)


def get_help_content_path(content_name: str) -> str:
    """
    Get the full path to a help content file.

    Args:
        content_name: Name of the help content file

    Returns:
        Full path to the help content file
    """
    if not content_name.endswith(".html"):
        content_name += ".html"
    return str(HELP_CONTENT_DIR / content_name)


# Workspace structure helper functions


def normalize_test_type(test_type: str) -> str:
    """
    Normalize test type name to canonical form.

    Args:
        test_type: Test type name (comparison/comparator/validator/benchmark/benchmarker)

    Returns:
        Normalized test type name (comparator/validator/benchmarker)

    Examples:
        >>> normalize_test_type('comparison')
        'comparator'
        >>> normalize_test_type('benchmark')
        'benchmarker'
    """
    normalized = TEST_TYPE_ALIASES.get(test_type.lower())
    if not normalized:
        raise ValueError(
            f"Unknown test type: {test_type}. "
            f"Valid types: {list(TEST_TYPE_ALIASES.keys())}"
        )
    return normalized


def get_test_type_dir(workspace_dir: str, test_type: str) -> str:
    """
    Get directory path for specific test type.

    Args:
        workspace_dir: Root workspace directory path
        test_type: Test type (comparison/comparator/validator/benchmark/benchmarker)

    Returns:
        Full path to test type directory (e.g., workspace/comparator/)

    Examples:
        >>> get_test_type_dir('/home/user/workspace', 'comparator')
        '/home/user/workspace/comparator'
    """
    test_type = normalize_test_type(test_type)
    return os.path.join(workspace_dir, test_type)


def get_inputs_dir(workspace_dir: str, test_type: str) -> str:
    """
    Get inputs directory path for specific test type.

    Args:
        workspace_dir: Root workspace directory path
        test_type: Test type (comparison/comparator/validator/benchmark/benchmarker)

    Returns:
        Full path to inputs directory (e.g., workspace/comparator/inputs/)

    Examples:
        >>> get_inputs_dir('/home/user/workspace', 'comparator')
        '/home/user/workspace/comparator/inputs'
    """
    test_dir = get_test_type_dir(workspace_dir, test_type)
    return os.path.join(test_dir, WORKSPACE_INPUTS_SUBDIR)


def get_outputs_dir(workspace_dir: str, test_type: str) -> str:
    """
    Get outputs directory path for specific test type.

    Args:
        workspace_dir: Root workspace directory path
        test_type: Test type (comparison/comparator/validator/benchmark/benchmarker)

    Returns:
        Full path to outputs directory (e.g., workspace/comparator/outputs/)

    Examples:
        >>> get_outputs_dir('/home/user/workspace', 'comparator')
        '/home/user/workspace/comparator/outputs'
    """
    test_dir = get_test_type_dir(workspace_dir, test_type)
    return os.path.join(test_dir, WORKSPACE_OUTPUTS_SUBDIR)


def get_workspace_file_path(workspace_dir: str, test_type: str, filename: str) -> str:
    """
    Get full path for a file within test type directory.

    Args:
        workspace_dir: Root workspace directory path
        test_type: Test type (comparison/comparator/validator/benchmark/benchmarker)
        filename: Name of the file (e.g., 'generator.cpp', 'test.py')

    Returns:
        Full path to file in test type directory

    Examples:
        >>> get_workspace_file_path('/home/user/workspace', 'comparator', 'generator.cpp')
        '/home/user/workspace/comparator/generator.cpp'
    """
    test_dir = get_test_type_dir(workspace_dir, test_type)
    return os.path.join(test_dir, filename)


def get_input_file_path(workspace_dir: str, test_type: str, filename: str) -> str:
    """
    Get full path for an input file.

    Args:
        workspace_dir: Root workspace directory path
        test_type: Test type (comparison/comparator/validator/benchmark/benchmarker)
        filename: Input filename (e.g., 'input_1.txt', 'input.txt')

    Returns:
        Full path to input file

    Examples:
        >>> get_input_file_path('/home/user/workspace', 'comparator', 'input_1.txt')
        '/home/user/workspace/comparator/inputs/input_1.txt'
    """
    inputs_dir = get_inputs_dir(workspace_dir, test_type)
    return os.path.join(inputs_dir, filename)


def get_output_file_path(workspace_dir: str, test_type: str, filename: str) -> str:
    """
    Get full path for an output file.

    Args:
        workspace_dir: Root workspace directory path
        test_type: Test type (comparison/comparator/validator/benchmark/benchmarker)
        filename: Output filename (e.g., 'output_1.txt', 'test_output.txt')

    Returns:
        Full path to output file

    Examples:
        >>> get_output_file_path('/home/user/workspace', 'comparator', 'output_1.txt')
        '/home/user/workspace/comparator/outputs/output_1.txt'
    """
    outputs_dir = get_outputs_dir(workspace_dir, test_type)
    return os.path.join(outputs_dir, filename)
