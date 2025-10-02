"""
Unit tests for Language Compiler Implementations.

Tests BaseLanguageCompiler, CppCompiler, PythonCompiler, JavaCompiler,
and LanguageCompilerFactory with mocked subprocess calls.
"""

import pytest
import os
from unittest.mock import Mock, patch, mock_open, MagicMock
from subprocess import CompletedProcess, TimeoutExpired
from src.app.core.tools.base.language_compilers import (
    BaseLanguageCompiler,
    CppCompiler,
    PythonCompiler,
    JavaCompiler,
    LanguageCompilerFactory
)
from src.app.core.tools.base.language_detector import Language


class TestCppCompiler:
    """Test C++ compiler functionality."""
    
    @pytest.fixture
    def compiler(self):
        """Create a CppCompiler instance with default config."""
        return CppCompiler()
    
    @pytest.fixture
    def custom_compiler(self):
        """Create a CppCompiler with custom config."""
        config = {
            'compiler': 'clang++',
            'std_version': 'c++20',
            'optimization': 'O3',
            'flags': ['-Wall', '-Wextra']
        }
        return CppCompiler(config)
    
    def test_get_language(self, compiler):
        """Test that CppCompiler returns CPP language."""
        assert compiler.get_language() == Language.CPP
    
    def test_needs_compilation(self, compiler):
        """Test that C++ requires compilation."""
        assert compiler.needs_compilation() is True
    
    def test_get_compiler_executable_default(self, compiler):
        """Test default compiler is g++."""
        assert compiler.get_compiler_executable() == 'g++'
    
    def test_get_compiler_executable_custom(self, custom_compiler):
        """Test custom compiler configuration."""
        assert custom_compiler.get_compiler_executable() == 'clang++'
    
    def test_get_executable_extension_windows(self, compiler, monkeypatch):
        """Test executable extension on Windows."""
        monkeypatch.setattr(os, 'name', 'nt')
        assert compiler.get_executable_extension() == '.exe'
    
    def test_get_executable_extension_unix(self, compiler, monkeypatch):
        """Test executable extension on Unix."""
        monkeypatch.setattr(os, 'name', 'posix')
        compiler_unix = CppCompiler()
        assert compiler_unix.get_executable_extension() == ''
    
    def test_get_executable_path(self, compiler):
        """Test executable path generation."""
        path = compiler.get_executable_path('test.cpp')
        assert path.startswith('test')
        assert path.endswith('.exe') or not path.endswith('.cpp')
    
    @patch('subprocess.run')
    def test_compile_success(self, mock_run, compiler):
        """Test successful C++ compilation."""
        mock_run.return_value = CompletedProcess(
            args=['g++'],
            returncode=0,
            stdout='',
            stderr=''
        )
        
        success, message = compiler.compile('test.cpp', 'test.exe')
        assert success is True
        assert 'Successfully compiled' in message
        mock_run.assert_called_once()
    
    @patch('subprocess.run')
    def test_compile_with_custom_flags(self, mock_run, compiler):
        """Test compilation with custom flags."""
        mock_run.return_value = CompletedProcess(
            args=['g++'],
            returncode=0,
            stdout='',
            stderr=''
        )
        
        custom_flags = ['-g', '-DDEBUG']
        success, message = compiler.compile('test.cpp', 'test.exe', custom_flags=custom_flags)
        assert success is True
        
        # Check that custom flags were used
        call_args = mock_run.call_args[0][0]
        assert '-g' in call_args
        assert '-DDEBUG' in call_args
    
    @patch('subprocess.run')
    def test_compile_failure(self, mock_run, compiler):
        """Test compilation failure."""
        mock_run.return_value = CompletedProcess(
            args=['g++'],
            returncode=1,
            stdout='',
            stderr='error: expected semicolon'
        )
        
        success, message = compiler.compile('test.cpp', 'test.exe')
        assert success is False
        assert 'expected semicolon' in message
    
    @patch('subprocess.run')
    def test_compile_timeout(self, mock_run, compiler):
        """Test compilation timeout handling."""
        mock_run.side_effect = TimeoutExpired(cmd=['g++'], timeout=30)
        
        success, message = compiler.compile('test.cpp', 'test.exe', timeout=30)
        assert success is False
        assert 'timeout' in message.lower()
    
    @patch('subprocess.run')
    def test_compile_compiler_not_found(self, mock_run, compiler):
        """Test handling when compiler is not found."""
        mock_run.side_effect = FileNotFoundError()
        
        success, message = compiler.compile('test.cpp', 'test.exe')
        assert success is False
        assert 'not found' in message.lower()
    
    @patch('subprocess.run')
    def test_compile_uses_config(self, mock_run, custom_compiler):
        """Test that compile uses custom configuration."""
        mock_run.return_value = CompletedProcess(
            args=['clang++'],
            returncode=0,
            stdout='',
            stderr=''
        )
        
        custom_compiler.compile('test.cpp', 'test.exe')
        
        call_args = mock_run.call_args[0][0]
        assert 'clang++' in call_args
        assert '-O3' in call_args
        assert '-std=c++20' in call_args
    
    def test_get_executable_command(self, compiler):
        """Test C++ executable command generation."""
        cmd = compiler.get_executable_command('test.exe')
        assert cmd == ['test.exe']
    
    @patch('subprocess.run')
    def test_validate_environment_success(self, mock_run, compiler):
        """Test environment validation success."""
        mock_run.return_value = CompletedProcess(
            args=['g++', '--version'],
            returncode=0,
            stdout='g++ version 11.0',
            stderr=''
        )
        
        is_valid, message = compiler.validate_environment()
        assert is_valid is True
        assert 'available' in message.lower()
    
    @patch('subprocess.run')
    def test_validate_environment_not_found(self, mock_run, compiler):
        """Test environment validation when compiler not found."""
        mock_run.side_effect = FileNotFoundError()
        
        is_valid, message = compiler.validate_environment()
        assert is_valid is False
        assert 'not found' in message.lower()


class TestPythonCompiler:
    """Test Python compiler (interpreter) functionality."""
    
    @pytest.fixture
    def compiler(self):
        """Create a PythonCompiler instance."""
        return PythonCompiler()
    
    @pytest.fixture
    def custom_compiler(self):
        """Create a PythonCompiler with custom config."""
        config = {
            'interpreter': 'python3',
            'flags': ['-u', '-B']
        }
        return PythonCompiler(config)
    
    def test_get_language(self, compiler):
        """Test that PythonCompiler returns PYTHON language."""
        assert compiler.get_language() == Language.PYTHON
    
    def test_needs_compilation(self, compiler):
        """Test that Python doesn't require compilation."""
        assert compiler.needs_compilation() is False
    
    def test_get_compiler_executable_default(self, compiler):
        """Test default interpreter is python."""
        assert compiler.get_compiler_executable() == 'python'
    
    def test_get_compiler_executable_custom(self, custom_compiler):
        """Test custom interpreter configuration."""
        assert custom_compiler.get_compiler_executable() == 'python3'
    
    def test_get_executable_extension(self, compiler):
        """Test Python executable extension is .py."""
        assert compiler.get_executable_extension() == '.py'
    
    def test_get_executable_path(self, compiler):
        """Test Python executable path (same as source)."""
        path = compiler.get_executable_path('script.py')
        assert path == 'script.py'
    
    def test_compile_valid_syntax(self, compiler, tmp_path):
        """Test Python syntax validation with valid code."""
        test_file = tmp_path / "test.py"
        test_file.write_text("def main():\n    print('Hello')\n")
        
        success, message = compiler.compile(str(test_file))
        assert success is True
        assert 'syntax valid' in message.lower()
    
    def test_compile_invalid_syntax(self, compiler, tmp_path):
        """Test Python syntax validation with invalid code."""
        test_file = tmp_path / "test.py"
        test_file.write_text("def main(\n    print('Hello')\n")  # Missing closing paren
        
        success, message = compiler.compile(str(test_file))
        assert success is False
        assert 'syntax error' in message.lower()
    
    def test_compile_file_not_found(self, compiler):
        """Test compilation with non-existent file."""
        success, message = compiler.compile('nonexistent.py')
        assert success is False
        assert 'error' in message.lower()
    
    def test_get_executable_command_default(self, compiler):
        """Test Python execution command with default config."""
        cmd = compiler.get_executable_command('script.py')
        assert 'python' in cmd
        assert '-u' in cmd
        assert 'script.py' in cmd
    
    def test_get_executable_command_custom(self, custom_compiler):
        """Test Python execution command with custom config."""
        cmd = custom_compiler.get_executable_command('script.py')
        assert 'python3' in cmd
        assert '-u' in cmd
        assert '-B' in cmd
        assert 'script.py' in cmd
    
    @patch('subprocess.run')
    def test_validate_environment_success(self, mock_run, compiler):
        """Test Python environment validation."""
        mock_run.return_value = CompletedProcess(
            args=['python', '--version'],
            returncode=0,
            stdout='Python 3.9.0',
            stderr=''
        )
        
        is_valid, message = compiler.validate_environment()
        assert is_valid is True


class TestJavaCompiler:
    """Test Java compiler functionality."""
    
    @pytest.fixture
    def compiler(self):
        """Create a JavaCompiler instance."""
        return JavaCompiler()
    
    @pytest.fixture
    def custom_compiler(self):
        """Create a JavaCompiler with custom config."""
        config = {
            'compiler': 'javac',
            'runtime': 'java',
            'flags': ['-Xlint:all']
        }
        return JavaCompiler(config)
    
    def test_get_language(self, compiler):
        """Test that JavaCompiler returns JAVA language."""
        assert compiler.get_language() == Language.JAVA
    
    def test_needs_compilation(self, compiler):
        """Test that Java requires compilation."""
        assert compiler.needs_compilation() is True
    
    def test_get_compiler_executable(self, compiler):
        """Test default compiler is javac."""
        assert compiler.get_compiler_executable() == 'javac'
    
    def test_get_executable_extension(self, compiler):
        """Test Java executable extension is .class."""
        assert compiler.get_executable_extension() == '.class'
    
    def test_get_executable_path(self, compiler):
        """Test Java class file path generation."""
        path = compiler.get_executable_path('Main.java')
        assert path == 'Main.class'
    
    @patch('subprocess.run')
    def test_compile_success(self, mock_run, compiler):
        """Test successful Java compilation."""
        mock_run.return_value = CompletedProcess(
            args=['javac'],
            returncode=0,
            stdout='',
            stderr=''
        )
        
        success, message = compiler.compile('Main.java', 'build/Main.class')
        assert success is True
        assert 'Successfully compiled' in message
    
    @patch('subprocess.run')
    def test_compile_with_output_directory(self, mock_run, compiler):
        """Test Java compilation with output directory."""
        mock_run.return_value = CompletedProcess(
            args=['javac'],
            returncode=0,
            stdout='',
            stderr=''
        )
        
        compiler.compile('Main.java', 'build/Main.class')
        
        call_args = mock_run.call_args[0][0]
        assert '-d' in call_args
        assert 'build' in call_args
    
    @patch('subprocess.run')
    def test_compile_with_custom_flags(self, mock_run, custom_compiler):
        """Test Java compilation with custom flags."""
        mock_run.return_value = CompletedProcess(
            args=['javac'],
            returncode=0,
            stdout='',
            stderr=''
        )
        
        custom_compiler.compile('Main.java')
        
        call_args = mock_run.call_args[0][0]
        assert '-Xlint:all' in call_args
    
    @patch('subprocess.run')
    def test_compile_failure(self, mock_run, compiler):
        """Test Java compilation failure."""
        mock_run.return_value = CompletedProcess(
            args=['javac'],
            returncode=1,
            stdout='',
            stderr="Main.java:5: error: ';' expected"
        )
        
        success, message = compiler.compile('Main.java')
        assert success is False
        assert 'expected' in message
    
    @patch('subprocess.run')
    def test_compile_timeout(self, mock_run, compiler):
        """Test Java compilation timeout."""
        mock_run.side_effect = TimeoutExpired(cmd=['javac'], timeout=30)
        
        success, message = compiler.compile('Main.java', timeout=30)
        assert success is False
        assert 'timeout' in message.lower()
    
    @patch('subprocess.run')
    def test_compile_compiler_not_found(self, mock_run, compiler):
        """Test handling when javac is not found."""
        mock_run.side_effect = FileNotFoundError()
        
        success, message = compiler.compile('Main.java')
        assert success is False
        assert 'not found' in message.lower()
    
    def test_get_executable_command_with_class_name(self, compiler):
        """Test Java execution command with explicit class name."""
        cmd = compiler.get_executable_command('build/', class_name='Main')
        assert 'java' in cmd
        assert '-cp' in cmd
        assert 'build' in ' '.join(cmd)
        assert 'Main' in cmd
    
    def test_get_executable_command_extract_class_name(self, compiler):
        """Test Java execution command with class name extraction."""
        cmd = compiler.get_executable_command('build/Main.class')
        assert 'java' in cmd
        assert 'Main' in cmd
    
    def test_get_executable_command_current_directory(self, compiler):
        """Test Java execution command with current directory."""
        cmd = compiler.get_executable_command('Main.class')
        assert '-cp' in cmd
        assert '.' in cmd


class TestLanguageCompilerFactory:
    """Test LanguageCompilerFactory functionality."""
    
    def test_create_cpp_compiler(self):
        """Test creating C++ compiler."""
        compiler = LanguageCompilerFactory.create_compiler(Language.CPP)
        assert isinstance(compiler, CppCompiler)
        assert compiler.get_language() == Language.CPP
    
    def test_create_python_compiler(self):
        """Test creating Python compiler."""
        compiler = LanguageCompilerFactory.create_compiler(Language.PYTHON)
        assert isinstance(compiler, PythonCompiler)
        assert compiler.get_language() == Language.PYTHON
    
    def test_create_java_compiler(self):
        """Test creating Java compiler."""
        compiler = LanguageCompilerFactory.create_compiler(Language.JAVA)
        assert isinstance(compiler, JavaCompiler)
        assert compiler.get_language() == Language.JAVA
    
    def test_create_compiler_with_config(self):
        """Test creating compiler with custom config."""
        config = {'compiler': 'clang++'}
        compiler = LanguageCompilerFactory.create_compiler(Language.CPP, config)
        assert compiler.get_compiler_executable() == 'clang++'
    
    def test_create_compiler_unknown_language(self):
        """Test that UNKNOWN language raises ValueError."""
        with pytest.raises(ValueError, match="Cannot create compiler for UNKNOWN language"):
            LanguageCompilerFactory.create_compiler(Language.UNKNOWN)
    
    def test_get_supported_languages(self):
        """Test getting list of supported languages."""
        languages = LanguageCompilerFactory.get_supported_languages()
        assert Language.CPP in languages
        assert Language.PYTHON in languages
        assert Language.JAVA in languages
        assert len(languages) == 3


class TestBaseLanguageCompiler:
    """Test BaseLanguageCompiler abstract functionality."""
    
    def test_cannot_instantiate_abstract_class(self):
        """Test that BaseLanguageCompiler cannot be instantiated directly."""
        with pytest.raises(TypeError):
            BaseLanguageCompiler()


class TestConfigIntegration:
    """Test configuration integration across compilers."""
    
    def test_cpp_config_precedence(self):
        """Test that custom config overrides defaults for C++."""
        config = {
            'compiler': 'clang++',
            'std_version': 'c++20',
            'optimization': 'O0',
            'flags': ['-g']
        }
        compiler = CppCompiler(config)
        
        assert compiler.config['compiler'] == 'clang++'
        assert compiler.config['std_version'] == 'c++20'
        assert compiler.config['optimization'] == 'O0'
        assert compiler.config['flags'] == ['-g']
    
    def test_python_config_precedence(self):
        """Test that custom config overrides defaults for Python."""
        config = {
            'interpreter': 'python3.11',
            'flags': ['-u', '-B', '-O']
        }
        compiler = PythonCompiler(config)
        
        assert compiler.config['interpreter'] == 'python3.11'
        assert '-O' in compiler.config['flags']
    
    def test_java_config_precedence(self):
        """Test that custom config overrides defaults for Java."""
        config = {
            'compiler': 'javac',
            'runtime': 'java',
            'flags': ['-encoding', 'UTF-8']
        }
        compiler = JavaCompiler(config)
        
        assert compiler.config['compiler'] == 'javac'
        assert '-encoding' in compiler.config['flags']
    
    def test_empty_config(self):
        """Test compilers work with empty config."""
        for language in [Language.CPP, Language.PYTHON, Language.JAVA]:
            compiler = LanguageCompilerFactory.create_compiler(language, {})
            assert compiler is not None
            assert compiler.get_language() == language


class TestErrorHandling:
    """Test error handling across all compilers."""
    
    @patch('subprocess.run')
    def test_cpp_unexpected_error(self, mock_run):
        """Test C++ compiler handles unexpected errors."""
        mock_run.side_effect = RuntimeError("Unexpected error")
        
        compiler = CppCompiler()
        success, message = compiler.compile('test.cpp')
        assert success is False
        assert 'error' in message.lower()
    
    def test_python_encoding_error(self, tmp_path):
        """Test Python compiler handles encoding errors."""
        test_file = tmp_path / "test.py"
        # Write invalid UTF-8
        test_file.write_bytes(b'\xff\xfe')
        
        compiler = PythonCompiler()
        success, message = compiler.compile(str(test_file))
        assert success is False
        assert 'error' in message.lower()
    
    @patch('subprocess.run')
    def test_java_unexpected_error(self, mock_run):
        """Test Java compiler handles unexpected errors."""
        mock_run.side_effect = RuntimeError("Unexpected error")
        
        compiler = JavaCompiler()
        success, message = compiler.compile('Main.java')
        assert success is False
        assert 'error' in message.lower()


class TestCompilerIntegration:
    """Integration tests for compiler workflows."""
    
    @patch('subprocess.run')
    def test_cpp_full_workflow(self, mock_run):
        """Test complete C++ workflow: validate -> compile -> execute."""
        # Mock validation
        mock_run.return_value = CompletedProcess(
            args=['g++', '--version'],
            returncode=0,
            stdout='g++ version 11.0',
            stderr=''
        )
        
        compiler = CppCompiler()
        is_valid, _ = compiler.validate_environment()
        assert is_valid is True
        
        # Mock compilation
        mock_run.return_value = CompletedProcess(
            args=['g++'],
            returncode=0,
            stdout='',
            stderr=''
        )
        
        success, _ = compiler.compile('test.cpp', 'test.exe')
        assert success is True
        
        # Get execution command
        cmd = compiler.get_executable_command('test.exe')
        assert cmd == ['test.exe']
    
    def test_python_full_workflow(self, tmp_path):
        """Test complete Python workflow: validate -> compile -> execute."""
        test_file = tmp_path / "test.py"
        test_file.write_text("print('Hello')")
        
        compiler = PythonCompiler()
        
        # Validate syntax
        success, _ = compiler.compile(str(test_file))
        assert success is True
        
        # Get execution command
        cmd = compiler.get_executable_command(str(test_file))
        assert 'python' in cmd
        assert str(test_file) in cmd
    
    @patch('subprocess.run')
    def test_java_full_workflow(self, mock_run):
        """Test complete Java workflow: validate -> compile -> execute."""
        # Mock compilation
        mock_run.return_value = CompletedProcess(
            args=['javac'],
            returncode=0,
            stdout='',
            stderr=''
        )
        
        compiler = JavaCompiler()
        success, _ = compiler.compile('Main.java', 'build/Main.class')
        assert success is True
        
        # Get execution command
        cmd = compiler.get_executable_command('build/', class_name='Main')
        assert 'java' in cmd
        assert 'Main' in cmd
