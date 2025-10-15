"""
Workspace utility functions for directory structure management.

This module provides utilities for creating and managing the workspace directory
structure, including nested test type directories and migration from flat structure.
"""

import os
from pathlib import Path
from typing import Dict, List, Optional

from src.app.shared.constants.paths import (
    WORKSPACE_BENCHMARKER_SUBDIR,
    WORKSPACE_COMPARATOR_SUBDIR,
    WORKSPACE_VALIDATOR_SUBDIR,
    get_inputs_dir,
    get_outputs_dir,
    get_test_type_dir,
)


def ensure_workspace_structure(workspace_dir: str) -> None:
    """
    Create complete workspace directory structure with nested test type directories.

    Creates the following structure:
        workspace/
        ├── comparator/
        │   ├── inputs/
        │   └── outputs/
        ├── validator/
        │   ├── inputs/
        │   └── outputs/
        └── benchmarker/
            ├── inputs/
            └── outputs/

    Args:
        workspace_dir: Root workspace directory path

    Examples:
        >>> ensure_workspace_structure('/home/user/workspace')
        # Creates all subdirectories if they don't exist
    """
    if not workspace_dir:
        return

    # Create root workspace directory
    os.makedirs(workspace_dir, exist_ok=True)

    # Create test type directories with their subdirectories
    test_types = ["comparator", "validator", "benchmarker"]

    for test_type in test_types:
        # Create test type directory (e.g., workspace/comparator/)
        test_dir = get_test_type_dir(workspace_dir, test_type)
        os.makedirs(test_dir, exist_ok=True)

        # Create inputs subdirectory
        inputs_dir = get_inputs_dir(workspace_dir, test_type)
        os.makedirs(inputs_dir, exist_ok=True)

        # Create outputs subdirectory
        outputs_dir = get_outputs_dir(workspace_dir, test_type)
        os.makedirs(outputs_dir, exist_ok=True)


def get_test_type_from_path(file_path: str) -> Optional[str]:
    """
    Extract test type from file path.

    Args:
        file_path: Full file path or relative path

    Returns:
        Test type name (comparator/validator/benchmarker) or None if not found

    Examples:
        >>> get_test_type_from_path('/workspace/comparator/generator.cpp')
        'comparator'
        >>> get_test_type_from_path('validator/inputs/input_1.txt')
        'validator'
        >>> get_test_type_from_path('/workspace/generator.cpp')
        None
    """
    # Normalize path separators for cross-platform compatibility
    normalized_path = file_path.replace("\\", "/")
    path_parts = Path(normalized_path).parts

    # Look for test type directory in path (case-insensitive for cross-platform)
    test_types = [
        WORKSPACE_COMPARATOR_SUBDIR,
        WORKSPACE_VALIDATOR_SUBDIR,
        WORKSPACE_BENCHMARKER_SUBDIR,
    ]

    for part in path_parts:
        part_lower = part.lower()
        for test_type in test_types:
            if part_lower == test_type.lower():
                return test_type

    return None


def is_flat_workspace_structure(workspace_dir: str) -> bool:
    """
    Check if workspace has old flat structure (files in root).

    Args:
        workspace_dir: Root workspace directory path

    Returns:
        True if flat structure detected, False if nested or empty

    Examples:
        >>> is_flat_workspace_structure('/workspace')  # Has generator.cpp in root
        True
        >>> is_flat_workspace_structure('/workspace')  # Has comparator/ subdir
        False
    """
    if not os.path.exists(workspace_dir):
        return False

    # Source file indicators (any language)
    source_indicators = [
        "generator.cpp",
        "generator.py",
        "Generator.java",
        "correct.cpp",
        "correct.py",
        "Correct.java",
        "test.cpp",
        "test.py",
        "Test.java",
        "validator.cpp",
        "validator.py",
        "Validator.java",
    ]

    # Check if any source files exist in root
    for indicator in source_indicators:
        if os.path.exists(os.path.join(workspace_dir, indicator)):
            return True

    # Check for I/O files in root
    io_indicators = ["input.txt", "output.txt"]
    for indicator in io_indicators:
        if os.path.exists(os.path.join(workspace_dir, indicator)):
            return True

    # Check for numbered I/O files
    for filename in os.listdir(workspace_dir):
        if filename.startswith("input_") and filename.endswith(".txt"):
            return True
        if filename.startswith("output_") and filename.endswith(".txt"):
            return True

    return False


def get_file_language_extension(filename: str) -> Optional[str]:
    """
    Get language extension from filename.

    Args:
        filename: Name of the file

    Returns:
        Language code ('cpp', 'py', 'java') or None
    """
    ext = os.path.splitext(filename)[1].lower()

    if ext == ".cpp":
        return "cpp"
    if ext == ".py":
        return "py"
    if ext == ".java":
        return "java"
    if ext == ".exe":
        return "cpp"  # Assume C++ executable
    if ext == ".class":
        return "java"  # Java bytecode

    return None


def get_file_role(filename: str) -> Optional[str]:
    """
    Determine file role from filename.

    Args:
        filename: Name of the file (without path)

    Returns:
        Role name ('generator', 'correct', 'test', 'validator') or None

    Examples:
        >>> get_file_role('generator.cpp')
        'generator'
        >>> get_file_role('Generator.java')
        'generator'
        >>> get_file_role('correct.py')
        'correct'
    """
    basename = os.path.splitext(filename)[0].lower()

    if basename in ["generator", "gen"]:
        return "generator"
    if basename in ["correct", "solution", "sol"]:
        return "correct"
    if basename in ["test", "brute"]:
        return "test"
    if basename in ["validator", "checker"]:
        return "validator"

    return None


def list_workspace_files(
    workspace_dir: str, test_type: Optional[str] = None
) -> Dict[str, List[str]]:
    """
    List all files in workspace, optionally filtered by test type.

    Args:
        workspace_dir: Root workspace directory path
        test_type: Optional test type to filter by

    Returns:
        Dictionary mapping test types to lists of file paths (relative to workspace)

    Examples:
        >>> list_workspace_files('/workspace')
        {'comparator': ['generator.cpp', 'test.cpp'], 'validator': ['validator.py']}
        >>> list_workspace_files('/workspace', 'comparator')
        {'comparator': ['generator.cpp', 'test.cpp']}
    """
    if not os.path.exists(workspace_dir):
        return {}

    result = {}
    test_types = [test_type] if test_type else ["comparator", "validator", "benchmarker"]

    for ttype in test_types:
        test_dir = get_test_type_dir(workspace_dir, ttype)
        if not os.path.exists(test_dir):
            continue

        files = []

        # List source files in test type directory
        for filename in os.listdir(test_dir):
            filepath = os.path.join(test_dir, filename)
            if os.path.isfile(filepath):
                # Store relative path
                rel_path = os.path.join(ttype, filename)
                files.append(rel_path)

        if files:
            result[ttype] = files

    return result


def clean_workspace_io_files(workspace_dir: str, test_type: str) -> int:
    """
    Clean input/output files for a specific test type.

    Args:
        workspace_dir: Root workspace directory path
        test_type: Test type to clean

    Returns:
        Number of files deleted
    """
    count = 0

    # Clean inputs
    inputs_dir = get_inputs_dir(workspace_dir, test_type)
    if os.path.exists(inputs_dir):
        for filename in os.listdir(inputs_dir):
            filepath = os.path.join(inputs_dir, filename)
            if os.path.isfile(filepath) and filename.endswith(".txt"):
                os.remove(filepath)
                count += 1

    # Clean outputs
    outputs_dir = get_outputs_dir(workspace_dir, test_type)
    if os.path.exists(outputs_dir):
        for filename in os.listdir(outputs_dir):
            filepath = os.path.join(outputs_dir, filename)
            if os.path.isfile(filepath) and filename.endswith(".txt"):
                os.remove(filepath)
                count += 1

    return count


def ensure_test_type_directory(workspace_dir: str, test_type: str) -> str:
    """
    Ensure test type directory and subdirectories exist.

    Args:
        workspace_dir: Root workspace directory path
        test_type: Test type to create

    Returns:
        Path to test type directory
    """
    test_dir = get_test_type_dir(workspace_dir, test_type)
    os.makedirs(test_dir, exist_ok=True)

    inputs_dir = get_inputs_dir(workspace_dir, test_type)
    os.makedirs(inputs_dir, exist_ok=True)

    outputs_dir = get_outputs_dir(workspace_dir, test_type)
    os.makedirs(outputs_dir, exist_ok=True)

    return test_dir
