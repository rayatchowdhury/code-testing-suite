"""
Language Detection System for Multi-Language Compilation Support.

This module provides language detection from file extensions and content analysis,
mapping to appropriate compiler configurations for C++, Python, and Java.
"""

import logging
import os
import re
from enum import Enum
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class Language(Enum):
    """Supported programming languages."""

    CPP = "cpp"
    PYTHON = "py"
    JAVA = "java"
    UNKNOWN = "unknown"


class LanguageDetector:
    """
    Detects programming language from file extensions and content.

    Provides language-specific compiler configurations and validation.
    Supports C++, Python, and Java with extensible architecture.
    """

    # File extension mappings
    EXTENSION_MAP = {
        ".cpp": Language.CPP,
        ".cc": Language.CPP,
        ".cxx": Language.CPP,
        ".c++": Language.CPP,
        ".h": Language.CPP,
        ".hpp": Language.CPP,
        ".hxx": Language.CPP,
        ".py": Language.PYTHON,
        ".pyw": Language.PYTHON,
        ".java": Language.JAVA,
    }

    # Content-based detection patterns
    CONTENT_PATTERNS = {
        Language.CPP: [
            r'#include\s*[<"]',
            r"using\s+namespace\s+std",
            r"std::\w+",
            r"int\s+main\s*\(",
            r"class\s+\w+\s*{",
        ],
        Language.PYTHON: [
            r"def\s+\w+\s*\(",
            r"import\s+\w+",
            r"from\s+\w+\s+import",
            r'if\s+__name__\s*==\s*["\']__main__["\']',
            r"print\s*\(",
        ],
        Language.JAVA: [
            r"public\s+class\s+\w+",
            r"public\s+static\s+void\s+main",
            r"import\s+java\.",
            r"package\s+\w+",
            r"System\.out\.print",
        ],
    }

    # Default compiler configurations per language
    DEFAULT_CONFIGS = {
        Language.CPP: {
            "compiler": "g++",
            "std_version": "c++17",
            "optimization": "O2",
            "flags": ["-march=native", "-mtune=native", "-pipe", "-Wall"],
            "needs_compilation": True,
            "executable_extension": ".exe" if os.name == "nt" else "",
            "output_flag": "-o",
        },
        Language.PYTHON: {
            "interpreter": "python",
            "version": "3",
            "flags": ["-u"],  # Unbuffered output
            "needs_compilation": False,
            "executable_extension": ".py",
            "output_flag": None,
        },
        Language.JAVA: {
            "compiler": "javac",
            "version": "11",
            "flags": [],
            "needs_compilation": True,
            "executable_extension": ".class",
            "output_flag": "-d",
            "runtime": "java",
        },
    }

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the language detector.

        Args:
            config: Optional configuration dictionary to override defaults
        """
        self.config = config or {}
        # Create instance-level copy of DEFAULT_CONFIGS to avoid modifying class attribute
        self.language_configs = {}
        self._load_custom_configs()

    def _load_custom_configs(self):
        """Load custom language configurations from config."""
        # Merge custom configurations with defaults
        languages_config = self.config.get("languages", {})

        for lang in Language:
            if lang == Language.UNKNOWN:
                continue

            lang_key = lang.value
            default_config = self.DEFAULT_CONFIGS.get(lang, {}).copy()

            if lang_key in languages_config:
                custom_config = languages_config[lang_key]
                # Merge custom config with defaults
                merged_config = {**default_config, **custom_config}
                self.language_configs[lang] = merged_config
            else:
                self.language_configs[lang] = default_config

    def detect_from_extension(self, file_path: str) -> Language:
        """
        Detect language from file extension.

        Args:
            file_path: Path to the file

        Returns:
            Language: Detected language enum

        Examples:
            >>> detector.detect_from_extension('test.cpp')
            Language.CPP
            >>> detector.detect_from_extension('test.py')
            Language.PYTHON
            >>> detector.detect_from_extension('Main.java')
            Language.JAVA
        """
        if not file_path:
            return Language.UNKNOWN

        # Extract extension
        _, ext = os.path.splitext(file_path.lower())

        # Look up in extension map
        language = self.EXTENSION_MAP.get(ext, Language.UNKNOWN)

        if language == Language.UNKNOWN:
            logger.warning(f"Unknown file extension: {ext} for file: {file_path}")

        return language

    def detect_from_content(self, content: str, hint_extension: Optional[str] = None) -> Language:
        """
        Detect language from file content using pattern matching.

        Useful as a fallback when extension is ambiguous or missing.

        Args:
            content: File content as string
            hint_extension: Optional file extension to narrow search

        Returns:
            Language: Detected language enum
        """
        if not content:
            return Language.UNKNOWN

        # If hint provided, try that first
        if hint_extension:
            hint_lang = self.detect_from_extension(f"file{hint_extension}")
            if hint_lang != Language.UNKNOWN:
                # Verify with content patterns
                if self._matches_language_patterns(content, hint_lang):
                    return hint_lang

        # Try all language patterns
        scores = {}
        for language, patterns in self.CONTENT_PATTERNS.items():
            score = sum(1 for pattern in patterns if re.search(pattern, content, re.MULTILINE))
            scores[language] = score

        # Return language with highest score
        if scores:
            best_match = max(scores.items(), key=lambda x: x[1])
            if best_match[1] > 0:  # At least one pattern matched
                return best_match[0]

        return Language.UNKNOWN

    def _matches_language_patterns(self, content: str, language: Language) -> bool:
        """Check if content matches patterns for given language."""
        patterns = self.CONTENT_PATTERNS.get(language, [])
        return any(re.search(pattern, content, re.MULTILINE) for pattern in patterns)

    def detect_language(self, file_path: str, content: Optional[str] = None) -> Language:
        """
        Detect language using extension first, then content as fallback.

        Args:
            file_path: Path to the file
            content: Optional file content for content-based detection

        Returns:
            Language: Detected language enum
        """
        # Try extension first
        language = self.detect_from_extension(file_path)

        # If unknown and content provided, try content-based detection
        if language == Language.UNKNOWN and content:
            _, ext = os.path.splitext(file_path)
            language = self.detect_from_content(content, hint_extension=ext)

        return language

    def get_language_config(self, language: Language) -> Dict[str, Any]:
        """
        Get compiler/interpreter configuration for a language.

        Args:
            language: Language enum

        Returns:
            Dict: Configuration dictionary with compiler settings

        Raises:
            ValueError: If language is UNKNOWN or not supported
        """
        if language == Language.UNKNOWN:
            raise ValueError("Cannot get config for UNKNOWN language")

        config = self.language_configs.get(language)
        if not config:
            raise ValueError(f"No configuration found for language: {language}")

        return config.copy()

    def get_compiler_command(
        self,
        language: Language,
        source_file: str,
        output_file: Optional[str] = None,
        custom_flags: Optional[List[str]] = None,
    ) -> List[str]:
        """
        Build compiler/interpreter command for a language.

        Args:
            language: Language enum
            source_file: Path to source file
            output_file: Optional output file path
            custom_flags: Optional custom flags to override defaults

        Returns:
            List[str]: Command as list of arguments

        Examples:
            >>> detector.get_compiler_command(Language.CPP, 'test.cpp', 'test.exe')
            ['g++', '-O2', '-std=c++17', '-march=native', 'test.cpp', '-o', 'test.exe']

            >>> detector.get_compiler_command(Language.PYTHON, 'test.py')
            ['python', '-u', 'test.py']
        """
        config = self.get_language_config(language)

        if language == Language.CPP:
            cmd = [config["compiler"]]
            cmd.append(f"-{config['optimization']}")
            cmd.append(f"-std={config['std_version']}")
            cmd.extend(custom_flags or config["flags"])
            cmd.append(source_file)
            if output_file:
                cmd.extend([config["output_flag"], output_file])
            return cmd

        if language == Language.PYTHON:
            cmd = [config["interpreter"]]
            cmd.extend(custom_flags or config["flags"])
            cmd.append(source_file)
            return cmd

        if language == Language.JAVA:
            cmd = [config["compiler"]]
            cmd.extend(custom_flags or config["flags"])
            if output_file:
                # Java output directory
                output_dir = os.path.dirname(output_file)
                cmd.extend([config["output_flag"], output_dir])
            cmd.append(source_file)
            return cmd

        raise ValueError(f"Unsupported language: {language}")

    def get_execution_command(
        self, language: Language, executable_path: str, class_name: Optional[str] = None
    ) -> List[str]:
        """
        Build execution command for compiled/interpreted code.

        Args:
            language: Language enum
            executable_path: Path to executable/script
            class_name: Optional class name (required for Java)

        Returns:
            List[str]: Execution command as list

        Examples:
            >>> detector.get_execution_command(Language.CPP, 'test.exe')
            ['test.exe']

            >>> detector.get_execution_command(Language.PYTHON, 'test.py')
            ['python', '-u', 'test.py']

            >>> detector.get_execution_command(Language.JAVA, 'build/', 'Main')
            ['java', '-cp', 'build/', 'Main']
        """
        config = self.get_language_config(language)

        if language == Language.CPP:
            # Direct execution of compiled binary
            return [executable_path]

        if language == Language.PYTHON:
            # Run through Python interpreter
            return [config["interpreter"]] + config["flags"] + [executable_path]

        if language == Language.JAVA:
            # Run through Java runtime
            if not class_name:
                # Extract class name from path
                class_name = os.path.splitext(os.path.basename(executable_path))[0]

            class_dir = os.path.dirname(executable_path)
            return [config["runtime"], "-cp", class_dir, class_name]

        raise ValueError(f"Unsupported language: {language}")

    def needs_compilation(self, language: Language) -> bool:
        """
        Check if language requires compilation step.

        Args:
            language: Language enum

        Returns:
            bool: True if compilation needed, False for interpreted languages
        """
        config = self.get_language_config(language)
        return config.get("needs_compilation", True)

    def get_executable_path(self, source_path: str, language: Language) -> str:
        """
        Get expected executable path for a source file.

        Args:
            source_path: Path to source file
            language: Language enum

        Returns:
            str: Path to executable/compiled output
        """
        config = self.get_language_config(language)

        base_path = os.path.splitext(source_path)[0]
        extension = config["executable_extension"]

        if language == Language.PYTHON:
            # Python "executable" is the source file itself
            return source_path

        return base_path + extension

    @staticmethod
    def get_supported_languages() -> List[Language]:
        """Get list of supported languages (excluding UNKNOWN)."""
        return [lang for lang in Language if lang != Language.UNKNOWN]

    @staticmethod
    def get_supported_extensions() -> List[str]:
        """Get list of all supported file extensions."""
        return list(LanguageDetector.EXTENSION_MAP.keys())
