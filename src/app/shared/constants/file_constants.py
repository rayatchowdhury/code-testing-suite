"""
File constants and naming conventions for the Code Testing Suite.

This module defines file naming patterns, extensions, and provides utilities
for generating correct file paths based on test type, role, and language.
"""

import os
from typing import Dict, List, Optional

from src.app.shared.constants.paths import get_test_type_dir, normalize_test_type

# File roles for each test type
TEST_TYPE_FILES: Dict[str, List[str]] = {
    "comparator": ["generator", "correct", "test"],
    "validator": ["generator", "test", "validator"],
    "benchmarker": ["generator", "test"],
}


# Language file extensions
LANGUAGE_EXTENSIONS: Dict[str, str] = {
    "cpp": ".cpp",
    "c++": ".cpp",
    "py": ".py",
    "python": ".py",
    "java": ".java",
}


# Executable/output extensions by platform and language
EXECUTABLE_EXTENSIONS: Dict[str, str] = {
    "cpp": (
        ".exe" if os.name == "nt" else ""
    ),  # Platform-specific: .exe on Windows, no extension on Unix
    "c++": ".exe" if os.name == "nt" else "",
    "py": ".py",  # Interpreted, no compilation
    "python": ".py",
    "java": ".class",  # Bytecode
}


# Java class naming (capitalize first letter)
JAVA_CLASS_NAMES: Dict[str, str] = {
    "generator": "Generator",
    "correct": "Correct",
    "test": "Test",
    "validator": "Validator",
}


def get_source_filename(role: str, language: str) -> str:
    """
    Get source filename for a specific role and language.

    Args:
        role: File role (generator/correct/test/validator)
        language: Programming language (cpp/py/java)

    Returns:
        Source filename with appropriate extension

    Examples:
        >>> get_source_filename('generator', 'cpp')
        'generator.cpp'
        >>> get_source_filename('test', 'java')
        'Test.java'
        >>> get_source_filename('correct', 'py')
        'correct.py'
    """
    language = language.lower()
    role = role.lower()

    # Get extension
    ext = LANGUAGE_EXTENSIONS.get(language)
    if not ext:
        raise ValueError(
            f"Unknown language: {language}. "
            f"Supported: {list(LANGUAGE_EXTENSIONS.keys())}"
        )

    # Java uses capitalized class names
    if language == "java":
        class_name = JAVA_CLASS_NAMES.get(role)
        if not class_name:
            # Fallback: capitalize first letter
            class_name = role.capitalize()
        return f"{class_name}{ext}"

    # C++ and Python use lowercase
    return f"{role}{ext}"


def get_executable_name(role: str, language: str) -> str:
    """
    Get executable/output filename for a specific role and language.

    Args:
        role: File role (generator/correct/test/validator)
        language: Programming language (cpp/py/java)

    Returns:
        Executable filename (or source filename for interpreted languages)

    Examples:
        >>> get_executable_name('generator', 'cpp')
        'generator.exe'  # On Windows
        >>> get_executable_name('test', 'py')
        'test.py'  # Interpreted
        >>> get_executable_name('correct', 'java')
        'Correct.class'
    """
    language = language.lower()
    role = role.lower()

    # For interpreted languages, return source filename
    if language in ["py", "python"]:
        return get_source_filename(role, language)

    # Get executable extension
    exec_ext = EXECUTABLE_EXTENSIONS.get(language, ".exe")

    # Java uses capitalized class names
    if language == "java":
        class_name = JAVA_CLASS_NAMES.get(role, role.capitalize())
        return f"{class_name}{exec_ext}"

    # C++ uses lowercase
    return f"{role}{exec_ext}"


def get_source_file_path(
    workspace_dir: str, test_type: str, role: str, language: str
) -> str:
    """
    Get full path for a source file in workspace.

    Args:
        workspace_dir: Root workspace directory path
        test_type: Test type (comparator/validator/benchmarker)
        role: File role (generator/correct/test/validator)
        language: Programming language (cpp/py/java)

    Returns:
        Full path to source file

    Examples:
        >>> get_source_file_path('/workspace', 'comparator', 'generator', 'cpp')
        '/workspace/comparator/generator.cpp'
        >>> get_source_file_path('/workspace', 'validator', 'test', 'java')
        '/workspace/validator/Test.java'
    """
    test_type = normalize_test_type(test_type)
    test_dir = get_test_type_dir(workspace_dir, test_type)
    filename = get_source_filename(role, language)
    return os.path.join(test_dir, filename)


def get_executable_path(
    workspace_dir: str, test_type: str, role: str, language: str
) -> str:
    """
    Get full path for an executable file in workspace.

    Args:
        workspace_dir: Root workspace directory path
        test_type: Test type (comparator/validator/benchmarker)
        role: File role (generator/correct/test/validator)
        language: Programming language (cpp/py/java)

    Returns:
        Full path to executable file

    Examples:
        >>> get_executable_path('/workspace', 'comparator', 'generator', 'cpp')
        '/workspace/comparator/generator.exe'
        >>> get_executable_path('/workspace', 'validator', 'test', 'py')
        '/workspace/validator/test.py'
    """
    test_type = normalize_test_type(test_type)
    test_dir = get_test_type_dir(workspace_dir, test_type)
    filename = get_executable_name(role, language)
    return os.path.join(test_dir, filename)


def get_language_from_filename(filename: str) -> Optional[str]:
    """
    Detect programming language from filename extension.

    Args:
        filename: Filename (with or without path)

    Returns:
        Language code ('cpp', 'py', 'java') or None if unknown

    Examples:
        >>> get_language_from_filename('generator.cpp')
        'cpp'
        >>> get_language_from_filename('/path/to/Test.java')
        'java'
        >>> get_language_from_filename('test.py')
        'py'
    """
    basename = os.path.basename(filename)
    ext = os.path.splitext(basename)[1].lower()

    # Map extensions to language codes
    ext_map = {
        ".cpp": "cpp",
        ".c++": "cpp",
        ".cc": "cpp",
        ".cxx": "cpp",
        ".py": "py",
        ".pyw": "py",
        ".java": "java",
    }

    return ext_map.get(ext)


def get_role_from_filename(filename: str) -> Optional[str]:
    """
    Detect file role from filename.

    Args:
        filename: Filename (with or without path)

    Returns:
        Role name ('generator', 'correct', 'test', 'validator') or None

    Examples:
        >>> get_role_from_filename('generator.cpp')
        'generator'
        >>> get_role_from_filename('Correct.java')
        'correct'
        >>> get_role_from_filename('test.py')
        'test'
    """
    basename = os.path.basename(filename)
    name = os.path.splitext(basename)[0].lower()

    # Direct matches
    if name in ["generator", "gen"]:
        return "generator"
    if name in ["correct", "solution", "sol"]:
        return "correct"
    if name in ["test", "brute"]:
        return "test"
    if name in ["validator", "checker"]:
        return "validator"

    return None


def validate_file_for_test_type(filename: str, test_type: str) -> bool:
    """
    Check if a file is valid for a specific test type.

    Args:
        filename: Name of the file
        test_type: Test type to check against

    Returns:
        True if file role is valid for test type, False otherwise

    Examples:
        >>> validate_file_for_test_type('generator.cpp', 'comparator')
        True
        >>> validate_file_for_test_type('correct.py', 'benchmarker')
        False  # benchmarker doesn't use correct solution
        >>> validate_file_for_test_type('validator.java', 'validator')
        True
    """
    role = get_role_from_filename(filename)
    if not role:
        return False

    test_type = normalize_test_type(test_type)
    valid_roles = TEST_TYPE_FILES.get(test_type, [])

    return role in valid_roles


def get_default_language() -> str:
    """Get default programming language."""
    return "cpp"


def get_supported_languages() -> List[str]:
    """Get list of supported programming languages."""
    return ["cpp", "py", "java"]


def get_file_display_name(role: str, language: str) -> str:
    """
    Get user-friendly display name for a file.

    Args:
        role: File role
        language: Programming language

    Returns:
        Display name

    Examples:
        >>> get_file_display_name('generator', 'cpp')
        'Generator (C++)'
        >>> get_file_display_name('test', 'java')
        'Test (Java)'
    """
    role_names = {
        "generator": "Generator",
        "correct": "Correct Solution",
        "test": "Test Solution",
        "validator": "Validator",
    }

    lang_names = {
        "cpp": "C++",
        "py": "Python",
        "java": "Java",
    }

    role_name = role_names.get(role, role.capitalize())
    lang_name = lang_names.get(language, language.upper())

    return f"{role_name} ({lang_name})"
