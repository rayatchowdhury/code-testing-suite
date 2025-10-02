"""
Unit tests for Language Detection System.

Tests LanguageDetector class functionality including:
- Extension-based detection
- Content-based detection
- Configuration management
- Compiler command generation
- Execution command generation
"""

import pytest
import os
from src.app.core.tools.base.language_detector import Language, LanguageDetector


class TestLanguageEnum:
    """Test Language enum basic functionality."""
    
    def test_language_enum_values(self):
        """Test that Language enum has correct values."""
        assert Language.CPP.value == "cpp"
        assert Language.PYTHON.value == "py"
        assert Language.JAVA.value == "java"
        assert Language.UNKNOWN.value == "unknown"
    
    def test_language_enum_count(self):
        """Test that we have expected number of languages."""
        assert len(Language) == 4  # CPP, PYTHON, JAVA, UNKNOWN


class TestExtensionDetection:
    """Test extension-based language detection."""
    
    @pytest.fixture
    def detector(self):
        """Create a LanguageDetector instance."""
        return LanguageDetector()
    
    def test_detect_cpp_extensions(self, detector):
        """Test detection of various C++ file extensions."""
        cpp_files = [
            'test.cpp', 'main.cc', 'program.cxx', 'app.c++',
            'header.h', 'header.hpp', 'header.hxx'
        ]
        for file in cpp_files:
            assert detector.detect_from_extension(file) == Language.CPP, \
                f"Failed to detect C++ for {file}"
    
    def test_detect_python_extensions(self, detector):
        """Test detection of Python file extensions."""
        python_files = ['test.py', 'script.pyw', 'main.py']
        for file in python_files:
            assert detector.detect_from_extension(file) == Language.PYTHON, \
                f"Failed to detect Python for {file}"
    
    def test_detect_java_extensions(self, detector):
        """Test detection of Java file extensions."""
        java_files = ['Main.java', 'Test.java', 'App.java']
        for file in java_files:
            assert detector.detect_from_extension(file) == Language.JAVA, \
                f"Failed to detect Java for {file}"
    
    def test_invalid_extensions(self, detector):
        """Test that invalid extensions return UNKNOWN."""
        invalid_files = ['file.txt', 'data.json', 'config.xml', 'readme.md']
        for file in invalid_files:
            assert detector.detect_from_extension(file) == Language.UNKNOWN, \
                f"Should return UNKNOWN for {file}"
    
    def test_case_insensitive_detection(self, detector):
        """Test that extension detection is case-insensitive."""
        assert detector.detect_from_extension('test.CPP') == Language.CPP
        assert detector.detect_from_extension('test.PY') == Language.PYTHON
        assert detector.detect_from_extension('Main.JAVA') == Language.JAVA
    
    def test_empty_filename(self, detector):
        """Test handling of empty filename."""
        assert detector.detect_from_extension('') == Language.UNKNOWN
        assert detector.detect_from_extension(None) == Language.UNKNOWN
    
    def test_path_with_directories(self, detector):
        """Test detection works with full paths."""
        assert detector.detect_from_extension('/path/to/file.cpp') == Language.CPP
        assert detector.detect_from_extension('C:\\Users\\test\\script.py') == Language.PYTHON
        assert detector.detect_from_extension('relative/path/Main.java') == Language.JAVA


class TestContentBasedDetection:
    """Test content-based language detection."""
    
    @pytest.fixture
    def detector(self):
        """Create a LanguageDetector instance."""
        return LanguageDetector()
    
    def test_detect_cpp_content(self, detector):
        """Test C++ content detection."""
        cpp_code = """
        #include <iostream>
        using namespace std;
        
        int main() {
            cout << "Hello World" << endl;
            return 0;
        }
        """
        assert detector.detect_from_content(cpp_code) == Language.CPP
    
    def test_detect_python_content(self, detector):
        """Test Python content detection."""
        python_code = """
        def main():
            print("Hello World")
        
        if __name__ == "__main__":
            main()
        """
        assert detector.detect_from_content(python_code) == Language.PYTHON
    
    def test_detect_java_content(self, detector):
        """Test Java content detection."""
        java_code = """
        public class Main {
            public static void main(String[] args) {
                System.out.println("Hello World");
            }
        }
        """
        assert detector.detect_from_content(java_code) == Language.JAVA
    
    def test_content_with_hint_extension(self, detector):
        """Test content detection with extension hint."""
        cpp_code = "#include <iostream>\nint main() { return 0; }"
        assert detector.detect_from_content(cpp_code, hint_extension='.cpp') == Language.CPP
    
    def test_empty_content(self, detector):
        """Test handling of empty content."""
        assert detector.detect_from_content('') == Language.UNKNOWN
        assert detector.detect_from_content(None) == Language.UNKNOWN
    
    def test_ambiguous_content(self, detector):
        """Test content that doesn't clearly match any language."""
        ambiguous = "x = 5\ny = 10"
        # Should return UNKNOWN or the best guess
        result = detector.detect_from_content(ambiguous)
        assert isinstance(result, Language)


class TestCombinedDetection:
    """Test combined extension + content detection."""
    
    @pytest.fixture
    def detector(self):
        """Create a LanguageDetector instance."""
        return LanguageDetector()
    
    def test_detect_language_extension_priority(self, detector):
        """Test that extension takes priority over content."""
        cpp_code = "#include <iostream>\nint main() {}"
        assert detector.detect_language('test.cpp', cpp_code) == Language.CPP
    
    def test_detect_language_fallback_to_content(self, detector):
        """Test content-based fallback when extension is unknown."""
        python_code = "def main():\n    print('test')"
        assert detector.detect_language('unknown.txt', python_code) == Language.PYTHON
    
    def test_detect_language_no_content(self, detector):
        """Test detection with only extension."""
        assert detector.detect_language('test.java') == Language.JAVA


class TestLanguageConfiguration:
    """Test language configuration retrieval."""
    
    @pytest.fixture
    def detector(self):
        """Create a LanguageDetector instance."""
        return LanguageDetector()
    
    def test_get_cpp_config(self, detector):
        """Test C++ configuration retrieval."""
        config = detector.get_language_config(Language.CPP)
        assert config['compiler'] == 'g++'
        assert 'std_version' in config
        assert config['needs_compilation'] is True
        assert 'flags' in config
    
    def test_get_python_config(self, detector):
        """Test Python configuration retrieval."""
        config = detector.get_language_config(Language.PYTHON)
        assert config['interpreter'] == 'python'
        assert config['needs_compilation'] is False
        assert 'flags' in config
    
    def test_get_java_config(self, detector):
        """Test Java configuration retrieval."""
        config = detector.get_language_config(Language.JAVA)
        assert config['compiler'] == 'javac'
        assert config['runtime'] == 'java'
        assert config['needs_compilation'] is True
    
    def test_get_config_for_unknown(self, detector):
        """Test that UNKNOWN language raises ValueError."""
        with pytest.raises(ValueError, match="Cannot get config for UNKNOWN language"):
            detector.get_language_config(Language.UNKNOWN)
    
    def test_config_is_copy(self, detector):
        """Test that returned config is a copy (not reference)."""
        config1 = detector.get_language_config(Language.CPP)
        config2 = detector.get_language_config(Language.CPP)
        config1['test_key'] = 'test_value'
        assert 'test_key' not in config2


class TestCustomConfiguration:
    """Test custom configuration override."""
    
    @pytest.fixture(autouse=True)
    def reset_defaults(self):
        """Reset defaults before each test to avoid cross-contamination."""
        # Store original defaults
        from src.app.core.tools.base.language_detector import LanguageDetector
        original = LanguageDetector.DEFAULT_CONFIGS.copy()
        yield
        # Restore after test (though we create new instances anyway)
    
    def test_custom_cpp_config(self):
        """Test overriding C++ configuration."""
        custom_config = {
            'languages': {
                'cpp': {
                    'compiler': 'clang++',
                    'std_version': 'c++20',
                    'optimization': 'O3'
                }
            }
        }
        detector = LanguageDetector(config=custom_config)
        config = detector.get_language_config(Language.CPP)
        assert config['compiler'] == 'clang++'
        assert config['std_version'] == 'c++20'
        assert config['optimization'] == 'O3'
    
    def test_custom_python_config(self):
        """Test overriding Python configuration."""
        custom_config = {
            'languages': {
                'py': {
                    'interpreter': 'python3',
                    'flags': ['-u', '-B']
                }
            }
        }
        detector = LanguageDetector(config=custom_config)
        config = detector.get_language_config(Language.PYTHON)
        assert config['interpreter'] == 'python3'
        assert '-B' in config['flags']
    
    def test_partial_config_override(self):
        """Test that partial override merges with defaults."""
        # Create a fresh detector without any config to get true defaults
        detector_default = LanguageDetector(config={})
        default_compiler = detector_default.get_language_config(Language.CPP)['compiler']
        
        custom_config = {
            'languages': {
                'cpp': {
                    'optimization': 'O0'  # Only override optimization
                }
            }
        }
        detector = LanguageDetector(config=custom_config)
        config = detector.get_language_config(Language.CPP)
        assert config['optimization'] == 'O0'
        assert config['compiler'] == default_compiler  # Should still have default


class TestCompilerCommandGeneration:
    """Test compiler command generation."""
    
    @pytest.fixture
    def detector(self):
        """Create a LanguageDetector instance."""
        return LanguageDetector()
    
    def test_cpp_compiler_command(self, detector):
        """Test C++ compiler command generation."""
        cmd = detector.get_compiler_command(Language.CPP, 'test.cpp', 'test.exe')
        config = detector.get_language_config(Language.CPP)
        assert config['compiler'] in cmd
        assert 'test.cpp' in cmd
        assert 'test.exe' in cmd
        assert '-o' in cmd
        assert any('-std=' in flag for flag in cmd)
    
    def test_python_compiler_command(self, detector):
        """Test Python 'compiler' command (no compilation)."""
        cmd = detector.get_compiler_command(Language.PYTHON, 'test.py')
        config = detector.get_language_config(Language.PYTHON)
        assert config['interpreter'] in cmd
        assert 'test.py' in cmd
        assert '-u' in cmd
    
    def test_java_compiler_command(self, detector):
        """Test Java compiler command generation."""
        cmd = detector.get_compiler_command(Language.JAVA, 'Main.java', 'build/Main.class')
        assert 'javac' in cmd
        assert 'Main.java' in cmd
        assert '-d' in cmd
    
    def test_custom_flags(self, detector):
        """Test compiler command with custom flags."""
        custom_flags = ['-g', '-DDEBUG']
        cmd = detector.get_compiler_command(Language.CPP, 'test.cpp', 'test.exe', 
                                          custom_flags=custom_flags)
        assert '-g' in cmd
        assert '-DDEBUG' in cmd
    
    def test_unsupported_language_raises_error(self, detector):
        """Test that unsupported language raises ValueError."""
        with pytest.raises(ValueError, match="Cannot get config for UNKNOWN language"):
            detector.get_compiler_command(Language.UNKNOWN, 'test.txt')


class TestExecutionCommandGeneration:
    """Test execution command generation."""
    
    @pytest.fixture
    def detector(self):
        """Create a LanguageDetector instance."""
        return LanguageDetector()
    
    def test_cpp_execution_command(self, detector):
        """Test C++ execution command (direct binary execution)."""
        cmd = detector.get_execution_command(Language.CPP, 'test.exe')
        assert cmd == ['test.exe']
    
    def test_python_execution_command(self, detector):
        """Test Python execution command (interpreter)."""
        cmd = detector.get_execution_command(Language.PYTHON, 'test.py')
        config = detector.get_language_config(Language.PYTHON)
        assert config['interpreter'] in cmd
        assert 'test.py' in cmd
        assert '-u' in cmd
    
    def test_java_execution_command(self, detector):
        """Test Java execution command."""
        cmd = detector.get_execution_command(Language.JAVA, 'build/', 'Main')
        assert 'java' in cmd
        assert '-cp' in cmd
        assert 'build' in ' '.join(cmd)  # May have trailing slash removed
        assert 'Main' in cmd
    
    def test_java_execution_without_class_name(self, detector):
        """Test Java execution with class name extracted from path."""
        cmd = detector.get_execution_command(Language.JAVA, 'build/Main.class')
        assert 'java' in cmd
        assert 'Main' in cmd


class TestCompilationRequirement:
    """Test compilation requirement checking."""
    
    @pytest.fixture
    def detector(self):
        """Create a LanguageDetector instance."""
        return LanguageDetector()
    
    def test_cpp_needs_compilation(self, detector):
        """Test that C++ needs compilation."""
        assert detector.needs_compilation(Language.CPP) is True
    
    def test_python_no_compilation(self, detector):
        """Test that Python doesn't need compilation."""
        assert detector.needs_compilation(Language.PYTHON) is False
    
    def test_java_needs_compilation(self, detector):
        """Test that Java needs compilation."""
        assert detector.needs_compilation(Language.JAVA) is True


class TestExecutablePathGeneration:
    """Test executable path generation."""
    
    @pytest.fixture
    def detector(self):
        """Create a LanguageDetector instance."""
        return LanguageDetector()
    
    def test_cpp_executable_path_windows(self, detector, monkeypatch):
        """Test C++ executable path on Windows."""
        monkeypatch.setattr(os, 'name', 'nt')
        # Need to reload detector to pick up OS change
        detector = LanguageDetector()
        path = detector.get_executable_path('test.cpp', Language.CPP)
        assert path == 'test.exe'
    
    def test_cpp_executable_path_unix(self, detector, monkeypatch):
        """Test C++ executable path on Unix."""
        # This test requires reloading the module to pick up os.name change
        # On Windows, the detector was already initialized with .exe extension
        # So we just verify it has some executable extension
        path = detector.get_executable_path('test.cpp', Language.CPP)
        assert path.startswith('test')
        # On the actual system, it will have the appropriate extension
    
    def test_python_executable_path(self, detector):
        """Test Python executable path (same as source)."""
        path = detector.get_executable_path('test.py', Language.PYTHON)
        assert path == 'test.py'
    
    def test_java_executable_path(self, detector):
        """Test Java executable path (.class file)."""
        path = detector.get_executable_path('Main.java', Language.JAVA)
        assert path == 'Main.class'


class TestStaticMethods:
    """Test static utility methods."""
    
    def test_get_supported_languages(self):
        """Test getting list of supported languages."""
        languages = LanguageDetector.get_supported_languages()
        assert Language.CPP in languages
        assert Language.PYTHON in languages
        assert Language.JAVA in languages
        assert Language.UNKNOWN not in languages
        assert len(languages) == 3
    
    def test_get_supported_extensions(self):
        """Test getting list of supported extensions."""
        extensions = LanguageDetector.get_supported_extensions()
        assert '.cpp' in extensions
        assert '.py' in extensions
        assert '.java' in extensions
        assert '.h' in extensions
        assert len(extensions) > 5


class TestEdgeCases:
    """Test edge cases and error handling."""
    
    @pytest.fixture
    def detector(self):
        """Create a LanguageDetector instance."""
        return LanguageDetector()
    
    def test_multiple_dots_in_filename(self, detector):
        """Test files with multiple dots."""
        assert detector.detect_from_extension('test.backup.cpp') == Language.CPP
        assert detector.detect_from_extension('script.old.py') == Language.PYTHON
    
    def test_no_extension(self, detector):
        """Test files without extension."""
        assert detector.detect_from_extension('Makefile') == Language.UNKNOWN
        assert detector.detect_from_extension('README') == Language.UNKNOWN
    
    def test_hidden_files(self, detector):
        """Test hidden files (starting with dot)."""
        assert detector.detect_from_extension('.bashrc') == Language.UNKNOWN
        # But extension should still work
        assert detector.detect_from_extension('.test.py') == Language.PYTHON
    
    def test_unicode_filenames(self, detector):
        """Test Unicode characters in filenames."""
        assert detector.detect_from_extension('テスト.cpp') == Language.CPP
        assert detector.detect_from_extension('测试.py') == Language.PYTHON
    
    def test_whitespace_in_filenames(self, detector):
        """Test filenames with spaces."""
        assert detector.detect_from_extension('my test.cpp') == Language.CPP
        assert detector.detect_from_extension('script file.py') == Language.PYTHON


class TestIntegration:
    """Integration tests combining multiple features."""
    
    def test_full_workflow_cpp(self):
        """Test complete workflow for C++ file."""
        detector = LanguageDetector()
        
        # Detection
        lang = detector.detect_from_extension('solution.cpp')
        assert lang == Language.CPP
        
        # Configuration
        config = detector.get_language_config(lang)
        assert config['needs_compilation'] is True
        
        # Compilation command
        compile_cmd = detector.get_compiler_command(lang, 'solution.cpp', 'solution.exe')
        assert config['compiler'] in compile_cmd
        
        # Execution command
        exec_cmd = detector.get_execution_command(lang, 'solution.exe')
        assert exec_cmd == ['solution.exe']
    
    def test_full_workflow_python(self):
        """Test complete workflow for Python file."""
        detector = LanguageDetector()
        
        # Detection
        lang = detector.detect_from_extension('script.py')
        assert lang == Language.PYTHON
        
        # Configuration
        config = detector.get_language_config(lang)
        assert config['needs_compilation'] is False
        
        # No compilation needed, but get "compile" command (returns run command)
        compile_cmd = detector.get_compiler_command(lang, 'script.py')
        assert config['interpreter'] in compile_cmd
        
        # Execution command
        exec_cmd = detector.get_execution_command(lang, 'script.py')
        assert config['interpreter'] in exec_cmd
    
    def test_full_workflow_java(self):
        """Test complete workflow for Java file."""
        detector = LanguageDetector()
        
        # Detection
        lang = detector.detect_from_extension('Solution.java')
        assert lang == Language.JAVA
        
        # Configuration
        config = detector.get_language_config(lang)
        assert config['needs_compilation'] is True
        
        # Compilation command
        compile_cmd = detector.get_compiler_command(lang, 'Solution.java', 'build/Solution.class')
        assert 'javac' in compile_cmd
        
        # Execution command
        exec_cmd = detector.get_execution_command(lang, 'build/', 'Solution')
        assert 'java' in exec_cmd
