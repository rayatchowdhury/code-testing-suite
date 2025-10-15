"""
BaseCompiler - Consolidated compilation logic for all tools.

This class consolidates the 450+ lines of duplicated compilation logic
from validator.py, benchmarker.py, and comparator.py into a single
reusable base class with consistent optimizations and caching.

Now supports multi-language compilation (C++, Python, Java) with automatic
language detection and routing to appropriate compilers.
"""

import logging
import multiprocessing
import os
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any, Dict, List, Optional, Tuple

from PySide6.QtCore import QObject, Signal

from src.app.core.tools.base.language_compilers import LanguageCompilerFactory
from src.app.core.tools.base.language_detector import Language, LanguageDetector

logger = logging.getLogger(__name__)


class BaseCompiler(QObject):
    """
    Base compiler with parallel compilation, smart caching, and optimizations.

    This class consolidates compilation logic that was duplicated across multiple
    tool implementations, providing:
    - Parallel compilation with optimal worker count
    - Smart timestamp-based caching to avoid unnecessary recompilation
    - Consistent optimization flags across all tools
    - Unified error handling and status reporting
    - Template method pattern for customization
    """

    # Signals for compilation progress and results
    compilationFinished = Signal(bool)  # True if successful, False if failed
    compilationOutput = Signal(str, str)  # (message, type)

    def __init__(
        self,
        workspace_dir: str,
        files_dict: Dict[str, str],
        optimization_level: str = "O2",
        config: Optional[Dict[str, Any]] = None,
        test_type: str = "comparator",
    ):
        """
        Initialize the base compiler with multi-language support and nested workspace structure.

        Args:
            workspace_dir: Root workspace directory
            files_dict: Dictionary mapping file keys to source file paths (can be relative or absolute)
            optimization_level: Compiler optimization level ('O0', 'O1', 'O2', 'O3')
            config: Optional configuration dictionary with language settings
            test_type: Type of test (comparator/validator/benchmarker) for nested structure
        """
        super().__init__()
        self.workspace_dir = workspace_dir
        self.test_type = test_type
        self.optimization_level = optimization_level
        self.compilation_failed = False
        self.config = config or {}

        # Resolve file paths to nested structure if needed
        self.files = self._resolve_file_paths(files_dict)

        # Initialize language detection and compilation
        self.language_detector = LanguageDetector(self.config)
        self.language_compilers = {}  # Cache for language-specific compilers

        # Detect languages for each file
        self.file_languages = {}
        for key, file_path in self.files.items():
            language = self.language_detector.detect_from_extension(file_path)
            self.file_languages[key] = language
            logger.debug(f"Detected {language.value} for {key}: {file_path}")

        # Create executables dict with language-aware paths
        self.executables = {}
        for key, file_path in self.files.items():
            language = self.file_languages[key]
            executable_path = self.language_detector.get_executable_path(file_path, language)
            self.executables[key] = executable_path

    def _resolve_file_paths(self, files_dict: Dict[str, str]) -> Dict[str, str]:
        """
        Resolve relative paths within test type directory structure.

        Args:
            files_dict: Map of role -> file path (can be relative or absolute)

        Returns:
            Dictionary with resolved absolute paths
        """
        from src.app.shared.constants.paths import get_test_type_dir

        resolved = {}
        test_dir = get_test_type_dir(self.workspace_dir, self.test_type)

        for role, path in files_dict.items():
            if os.path.isabs(path):
                # Already absolute, use as-is
                resolved[role] = path
            else:
                # Relative path - resolve within test type directory
                resolved[role] = os.path.join(test_dir, path)

        return resolved

    def compile_all(self) -> bool:
        """
        Compile all files in parallel with optimizations and caching.

        Returns:
            bool: True if all files compiled successfully, False otherwise
        """
        self.compilation_failed = False

        # Start parallel compilation in a separate thread to avoid blocking UI
        compile_thread = threading.Thread(target=self._parallel_compile_all)
        compile_thread.daemon = True
        compile_thread.start()

        return True  # Return immediately, actual result comes via signal

    def _parallel_compile_all(self) -> None:
        """
        Compile all files in parallel with smart caching and optimization.

        This method consolidates the identical logic from validator_runner.py,
        benchmarker.py, and comparator.py.
        """
        files_to_compile = list(self.files.keys())
        max_workers = min(len(files_to_compile), multiprocessing.cpu_count())

        self.compilationOutput.emit("🚀 Starting optimized parallel compilation...\n", "info")

        # Check which files need recompilation
        files_needing_compilation = []
        for file_key in files_to_compile:
            if self._needs_recompilation(file_key):
                files_needing_compilation.append(file_key)
            else:
                # Get language-specific status message
                language = self.file_languages.get(file_key, Language.UNKNOWN)
                if language == Language.PYTHON:
                    source_file = self.files[file_key]
                    self.compilationOutput.emit(
                        f"✅ {os.path.basename(source_file)} has no syntax errors\n",
                        "success",
                    )
                elif language == Language.JAVA:
                    source_file = self.files[file_key]
                    class_file = os.path.basename(source_file).replace(".java", ".class")
                    self.compilationOutput.emit(
                        f"✅ {class_file} is up-to-date, skipping compilation\n",
                        "success",
                    )
                else:  # C++ and others
                    executable_file = self.executables[file_key]
                    self.compilationOutput.emit(
                        f"✅ {os.path.basename(executable_file)} is up-to-date, skipping compilation\n",
                        "success",
                    )

        if not files_needing_compilation:
            self.compilationOutput.emit(
                "\n🎉 All files are up-to-date! No compilation needed.\n", "success"
            )
            self.compilationFinished.emit(True)
            return

        compilation_results = {}
        all_success = True

        # Compile files in parallel
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit compilation jobs
            future_to_file = {
                executor.submit(self._compile_single_file, file_key): file_key
                for file_key in files_needing_compilation
            }

            # Process results as they complete
            for future in as_completed(future_to_file):
                file_key = future_to_file[future]
                try:
                    success, output = future.result()
                    compilation_results[file_key] = (success, output)

                    # Get language for better messaging
                    language = self.file_languages.get(file_key, Language.UNKNOWN)
                    lang_display = language.value.upper() if language != Language.UNKNOWN else ""
                    file_name = os.path.basename(self.files[file_key])

                    if success:
                        self.compilationOutput.emit(f"✅ {output}\n", "success")
                    else:
                        all_success = False
                        self.compilationOutput.emit(
                            f"❌ Failed ({lang_display}): {file_name}\n{output}\n",
                            "error",
                        )

                except Exception as e:
                    all_success = False
                    error_msg = f"Compilation error for {file_key}: {str(e)}"
                    self.compilationOutput.emit(f"❌ {error_msg}\n", "error")

        # Final result
        if all_success:
            self.compilationOutput.emit(
                "\n🎉 All files compiled successfully with optimizations!\n", "success"
            )
            self.compilationFinished.emit(True)
        else:
            self.compilation_failed = True
            self.compilationOutput.emit("\n❌ Some files failed to compile.\n", "error")
            self.compilationFinished.emit(False)

    def _needs_recompilation(self, file_key: str) -> bool:
        """
        Check if file needs recompilation based on timestamps and language.

        For interpreted languages (Python), always returns False since no compilation needed.
        For compiled languages (C++, Java), checks timestamps.

        Args:
            file_key: Key identifying the file to check

        Returns:
            bool: True if recompilation is needed, False if executable is up-to-date
        """
        language = self.file_languages.get(file_key, Language.UNKNOWN)

        # Check if language needs compilation
        if language in self.language_compilers:
            compiler = self.language_compilers[language]
        else:
            # Create temporary compiler to check
            lang_config = self._get_language_config(language)
            compiler = LanguageCompilerFactory.create_compiler(language, lang_config)

        # Interpreted languages don't need compilation
        if not compiler.needs_compilation():
            return False

        source_file = self.files[file_key]
        executable_file = self.executables[file_key]

        # For Python, executable is the source file itself
        if language == Language.PYTHON:
            return False

        # If executable doesn't exist, need to compile
        if not os.path.exists(executable_file):
            return True

        # If source doesn't exist, can't compile
        if not os.path.exists(source_file):
            return True

        # Compare timestamps
        try:
            source_mtime = os.path.getmtime(source_file)
            exe_mtime = os.path.getmtime(executable_file)
            return source_mtime > exe_mtime  # Source is newer than executable
        except OSError:
            return True  # If we can't check timestamps, be safe and recompile

    def _compile_single_file(self, file_key: str) -> Tuple[bool, str]:
        """
        Compile a single file using language-specific compiler.

        Now supports multi-language compilation with automatic language detection.
        Routes to appropriate compiler (g++, python validation, javac) based on file type.

        Args:
            file_key: Key identifying the file to compile

        Returns:
            Tuple[bool, str]: (success, output/error_message)
        """
        source_file = self.files[file_key]
        executable_file = self.executables[file_key]
        language = self.file_languages.get(file_key, Language.UNKNOWN)

        if language == Language.UNKNOWN:
            return False, f"Unknown language for {file_key}: {source_file}"

        try:
            # Get or create language-specific compiler
            if language not in self.language_compilers:
                lang_config = self._get_language_config(language)
                self.language_compilers[language] = LanguageCompilerFactory.create_compiler(
                    language, lang_config
                )

            compiler = self.language_compilers[language]

            # Compile using language-specific compiler
            success, message = compiler.compile(
                source_file=source_file, output_file=executable_file, timeout=30
            )

            return success, message

        except Exception as e:
            logger.error(f"Compilation error for {file_key}: {e}")
            return False, f"Compilation error: {str(e)}"

    def _get_language_config(self, language: Language) -> Dict[str, Any]:
        """
        Get language-specific configuration from config.

        Args:
            language: Language enum

        Returns:
            Dict: Language configuration with compiler settings
        """
        # Get language config from main config
        languages_config = self.config.get("languages", {})
        lang_key = language.value
        lang_config = languages_config.get(lang_key, {})

        # Add optimization level for C++
        if language == Language.CPP and "optimization" not in lang_config:
            lang_config["optimization"] = self.optimization_level

        return lang_config

    def get_compiler_flags(self) -> List[str]:
        """
        Get compiler flags for compilation.

        This method can be overridden by subclasses to customize compilation flags
        for specific use cases while maintaining consistent base optimizations.

        Returns:
            List[str]: List of compiler flags
        """
        # Standard optimization flags used across all tools
        return [
            f"-{self.optimization_level}",  # Optimization level (O2 by default)
            "-march=native",  # Optimize for current CPU architecture
            "-mtune=native",  # Tune for current CPU
            "-pipe",  # Use pipes instead of temporary files
            "-std=c++17",  # Use modern C++ standard
            "-Wall",  # Enable common warnings
        ]

    def get_debug_flags(self) -> List[str]:
        """
        Get debug-specific compiler flags.

        Returns:
            List[str]: List of debug compiler flags
        """
        return [
            "-g",  # Include debug information
            "-DDEBUG",  # Define DEBUG macro
            "-fsanitize=address",  # Enable address sanitizer
            "-fsanitize=undefined",  # Enable undefined behavior sanitizer
        ]

    def get_release_flags(self) -> List[str]:
        """
        Get release-specific compiler flags.

        Returns:
            List[str]: List of release compiler flags
        """
        return [
            "-DNDEBUG",  # Disable debug assertions
            "-flto",  # Link-time optimization
            "-fomit-frame-pointer",  # Omit frame pointer for better performance
        ]

    def get_execution_command(self, file_key: str, **kwargs) -> List[str]:
        """
        Get execution command for a compiled/interpreted file.

        This is crucial for multi-language support as different languages
        require different execution methods:
        - C++: Direct execution of .exe
        - Python: python script.py
        - Java: java -cp . ClassName

        Args:
            file_key: Key identifying the file
            **kwargs: Additional arguments (e.g., class_name for Java)

        Returns:
            List[str]: Command to execute the file
        """
        language = self.file_languages.get(file_key, Language.UNKNOWN)
        executable_path = self.executables[file_key]

        if language not in self.language_compilers:
            lang_config = self._get_language_config(language)
            self.language_compilers[language] = LanguageCompilerFactory.create_compiler(
                language, lang_config
            )

        compiler = self.language_compilers[language]
        return compiler.get_executable_command(executable_path, **kwargs)

    def get_file_language(self, file_key: str) -> Language:
        """
        Get the detected language for a file.

        Args:
            file_key: Key identifying the file

        Returns:
            Language: Detected language enum
        """
        return self.file_languages.get(file_key, Language.UNKNOWN)

    def needs_compilation(self, file_key: str) -> bool:
        """
        Check if a file needs compilation (vs interpreted execution).

        Args:
            file_key: Key identifying the file

        Returns:
            bool: True if compilation required, False for interpreted languages
        """
        language = self.file_languages.get(file_key, Language.UNKNOWN)

        if language not in self.language_compilers:
            lang_config = self._get_language_config(language)
            self.language_compilers[language] = LanguageCompilerFactory.create_compiler(
                language, lang_config
            )

        compiler = self.language_compilers[language]
        return compiler.needs_compilation()

    def stop(self) -> None:
        """Stop any running compilation process."""
        # This method can be extended by subclasses if they need
        # to stop specific compilation processes

    def __del__(self):
        """Destructor to ensure proper cleanup."""
        self.stop()
