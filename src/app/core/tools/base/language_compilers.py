"""
Language-Specific Compiler Implementations.

This module provides abstract base class and concrete implementations
for language-specific compilation and execution handling.
"""

import os
import subprocess
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
import logging

from src.app.core.tools.base.language_detector import Language

logger = logging.getLogger(__name__)


class BaseLanguageCompiler(ABC):
    """
    Abstract base class for language-specific compilers.

    Defines the interface that all language compilers must implement,
    ensuring consistent behavior across different languages.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the language compiler.

        Args:
            config: Optional configuration dictionary for compiler settings
        """
        self.config = config or {}
        self.language = self.get_language()

    @abstractmethod
    def get_language(self) -> Language:
        """Return the language this compiler handles."""
        pass

    @abstractmethod
    def needs_compilation(self) -> bool:
        """Return whether this language requires compilation."""
        pass

    @abstractmethod
    def compile(
        self,
        source_file: str,
        output_file: Optional[str] = None,
        custom_flags: Optional[List[str]] = None,
        timeout: int = 30,
    ) -> Tuple[bool, str]:
        """
        Compile source file.

        Args:
            source_file: Path to source file
            output_file: Optional output file path
            custom_flags: Optional custom compiler flags
            timeout: Compilation timeout in seconds

        Returns:
            Tuple[bool, str]: (success, output/error_message)
        """
        pass

    @abstractmethod
    def get_executable_command(self, executable_path: str, **kwargs) -> List[str]:
        """
        Get command to execute the compiled/interpreted code.

        Args:
            executable_path: Path to executable or source file
            **kwargs: Additional language-specific arguments

        Returns:
            List[str]: Command as list of arguments
        """
        pass

    def get_executable_path(self, source_file: str) -> str:
        """
        Get expected executable path for a source file.

        Args:
            source_file: Path to source file

        Returns:
            str: Path to executable
        """
        base_path = os.path.splitext(source_file)[0]
        extension = self.get_executable_extension()
        return base_path + extension

    @abstractmethod
    def get_executable_extension(self) -> str:
        """Return the executable file extension for this language."""
        pass

    def validate_environment(self) -> Tuple[bool, str]:
        """
        Validate that compiler/interpreter is available.

        Returns:
            Tuple[bool, str]: (is_valid, error_message)
        """
        try:
            compiler = self.get_compiler_executable()
            result = subprocess.run(
                [compiler, "--version"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=5,
                text=True,
            )
            if result.returncode == 0:
                return True, f"{compiler} is available"
            else:
                return False, f"{compiler} version check failed"
        except FileNotFoundError:
            compiler = self.get_compiler_executable()
            return False, f"{compiler} not found in PATH"
        except Exception as e:
            return False, f"Environment validation error: {str(e)}"

    @abstractmethod
    def get_compiler_executable(self) -> str:
        """Return the compiler/interpreter executable name."""
        pass


class CppCompiler(BaseLanguageCompiler):
    """C++ compiler implementation using g++."""

    def get_language(self) -> Language:
        return Language.CPP

    def needs_compilation(self) -> bool:
        return True

    def get_compiler_executable(self) -> str:
        return self.config.get("compiler", "g++")

    def get_executable_extension(self) -> str:
        return ".exe" if os.name == "nt" else ""

    def compile(
        self,
        source_file: str,
        output_file: Optional[str] = None,
        custom_flags: Optional[List[str]] = None,
        timeout: int = 30,
    ) -> Tuple[bool, str]:
        """
        Compile C++ source file using g++.

        Args:
            source_file: Path to .cpp file
            output_file: Optional output executable path
            custom_flags: Optional custom compiler flags
            timeout: Compilation timeout in seconds

        Returns:
            Tuple[bool, str]: (success, output/error_message)
        """
        if not output_file:
            output_file = self.get_executable_path(source_file)

        # Build compiler command
        compiler = self.get_compiler_executable()
        std_version = self.config.get("std_version", "c++17")
        optimization = self.config.get("optimization", "O2")

        cmd = [compiler]
        cmd.append(f"-{optimization}")
        cmd.append(f"-std={std_version}")

        # Add custom or default flags
        if custom_flags:
            cmd.extend(custom_flags)
        else:
            default_flags = self.config.get(
                "flags", ["-march=native", "-mtune=native", "-pipe", "-Wall"]
            )
            cmd.extend(default_flags)

        cmd.append(source_file)
        cmd.extend(["-o", output_file])

        logger.debug(f"C++ compile command: {' '.join(cmd)}")

        try:
            # Use numeric constant for CREATE_NO_WINDOW (0x08000000) to avoid
            # AttributeError on non-Windows platforms during testing
            result = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=timeout,
                creationflags=0x08000000 if os.name == "nt" else 0,
            )

            if result.returncode == 0:
                return True, f"Successfully compiled {os.path.basename(source_file)}"
            else:
                return False, result.stderr or result.stdout

        except subprocess.TimeoutExpired:
            return (
                False,
                f"Compilation timeout ({timeout}s) for {os.path.basename(source_file)}",
            )
        except FileNotFoundError:
            return (
                False,
                f"Compiler '{compiler}' not found. Please install g++ or update configuration.",
            )
        except Exception as e:
            return False, f"Compilation error: {str(e)}"

    def get_executable_command(self, executable_path: str, **kwargs) -> List[str]:
        """
        Get command to execute compiled C++ binary.

        Args:
            executable_path: Path to compiled executable

        Returns:
            List[str]: Command to run executable
        """
        return [executable_path]


class PythonCompiler(BaseLanguageCompiler):
    """Python interpreter handler (no compilation needed)."""

    def get_language(self) -> Language:
        return Language.PYTHON

    def needs_compilation(self) -> bool:
        return False

    def get_compiler_executable(self) -> str:
        return self.config.get("interpreter", "python")

    def get_executable_extension(self) -> str:
        return ".py"  # Python "executable" is the source file

    def compile(
        self,
        source_file: str,
        output_file: Optional[str] = None,
        custom_flags: Optional[List[str]] = None,
        timeout: int = 30,
    ) -> Tuple[bool, str]:
        """
        "Compile" Python file (actually just validation).

        Python doesn't require compilation, but we validate syntax here.

        Args:
            source_file: Path to .py file
            output_file: Ignored for Python
            custom_flags: Ignored for Python
            timeout: Validation timeout

        Returns:
            Tuple[bool, str]: (success, message)
        """
        # Validate Python syntax by trying to compile to bytecode
        try:
            with open(source_file, "r", encoding="utf-8") as f:
                code = f.read()

            compile(code, source_file, "exec")
            return True, f"Python syntax valid for {os.path.basename(source_file)}"

        except SyntaxError as e:
            return False, f"Syntax error in {os.path.basename(source_file)}: {e}"
        except Exception as e:
            return False, f"Validation error: {str(e)}"

    def get_executable_command(self, executable_path: str, **kwargs) -> List[str]:
        """
        Get command to execute Python script.

        Args:
            executable_path: Path to .py file

        Returns:
            List[str]: Command to run Python interpreter with script
        """
        interpreter = self.get_compiler_executable()
        flags = self.config.get("flags", ["-u"])  # Unbuffered by default
        return [interpreter] + flags + [executable_path]


class JavaCompiler(BaseLanguageCompiler):
    """Java compiler implementation using javac."""

    def get_language(self) -> Language:
        return Language.JAVA

    def needs_compilation(self) -> bool:
        return True

    def get_compiler_executable(self) -> str:
        return self.config.get("compiler", "javac")

    def get_executable_extension(self) -> str:
        return ".class"

    def compile(
        self,
        source_file: str,
        output_file: Optional[str] = None,
        custom_flags: Optional[List[str]] = None,
        timeout: int = 30,
    ) -> Tuple[bool, str]:
        """
        Compile Java source file using javac.

        Args:
            source_file: Path to .java file
            output_file: Optional output directory (Java compiles to .class)
            custom_flags: Optional custom compiler flags
            timeout: Compilation timeout in seconds

        Returns:
            Tuple[bool, str]: (success, output/error_message)
        """
        compiler = self.get_compiler_executable()

        cmd = [compiler]

        # Add custom or default flags
        if custom_flags:
            cmd.extend(custom_flags)
        else:
            default_flags = self.config.get("flags", [])
            cmd.extend(default_flags)

        # Set output directory if specified
        if output_file:
            output_dir = os.path.dirname(output_file)
            if output_dir:
                cmd.extend(["-d", output_dir])

        cmd.append(source_file)

        logger.debug(f"Java compile command: {' '.join(cmd)}")

        try:
            # Use numeric constant for CREATE_NO_WINDOW (0x08000000) to avoid
            # AttributeError on non-Windows platforms during testing
            result = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=timeout,
                creationflags=0x08000000 if os.name == "nt" else 0,
            )

            if result.returncode == 0:
                return True, f"Successfully compiled {os.path.basename(source_file)}"
            else:
                return False, result.stderr or result.stdout

        except subprocess.TimeoutExpired:
            return (
                False,
                f"Compilation timeout ({timeout}s) for {os.path.basename(source_file)}",
            )
        except FileNotFoundError:
            return (
                False,
                f"Compiler '{compiler}' not found. Please install Java JDK or update configuration.",
            )
        except Exception as e:
            return False, f"Compilation error: {str(e)}"

    def get_executable_command(self, executable_path: str, **kwargs) -> List[str]:
        """
        Get command to execute compiled Java class.

        Args:
            executable_path: Path to .class file or directory
            **kwargs: Must include 'class_name' - the main class name

        Returns:
            List[str]: Command to run Java runtime with class
        """
        runtime = self.config.get("runtime", "java")
        class_name = kwargs.get("class_name")

        if not class_name:
            # Extract class name from executable path
            class_name = os.path.splitext(os.path.basename(executable_path))[0]

        # Get class directory
        class_dir = os.path.dirname(executable_path) or "."

        return [runtime, "-cp", class_dir, class_name]


class LanguageCompilerFactory:
    """Factory for creating language-specific compilers."""

    _compilers = {
        Language.CPP: CppCompiler,
        Language.PYTHON: PythonCompiler,
        Language.JAVA: JavaCompiler,
    }

    @staticmethod
    def create_compiler(
        language: Language, config: Optional[Dict[str, Any]] = None
    ) -> BaseLanguageCompiler:
        """
        Create a compiler instance for the specified language.

        Args:
            language: Language enum
            config: Optional configuration dictionary

        Returns:
            BaseLanguageCompiler: Language-specific compiler instance

        Raises:
            ValueError: If language is not supported
        """
        if language == Language.UNKNOWN:
            raise ValueError("Cannot create compiler for UNKNOWN language")

        compiler_class = LanguageCompilerFactory._compilers.get(language)
        if not compiler_class:
            raise ValueError(f"No compiler implementation for language: {language}")

        return compiler_class(config)

    @staticmethod
    def get_supported_languages() -> List[Language]:
        """Get list of languages with compiler implementations."""
        return list(LanguageCompilerFactory._compilers.keys())
