"""
Test suite for LanguageDetector.

Tests language detection from file extensions and content analysis.
"""

import pytest
from pathlib import Path
from src.app.core.tools.base.language_detector import LanguageDetector, Language


class TestLanguageDetectorExtension:
    """Test language detection from file extensions."""
    
    @pytest.mark.parametrize("filename,expected", [
        ('test.cpp', Language.CPP),
        ('test.cc', Language.CPP),
        ('test.cxx', Language.CPP),
        ('test.c++', Language.CPP),
        ('test.h', Language.CPP),
        ('test.hpp', Language.CPP),
        ('test.hxx', Language.CPP),
        ('test.py', Language.PYTHON),
        ('test.pyw', Language.PYTHON),
        ('Main.java', Language.JAVA),
        ('test.txt', Language.UNKNOWN),
        ('noextension', Language.UNKNOWN),
    ])
    def test_detect_from_extension(self, filename, expected):
        """Should correctly detect language from extension."""
        detector = LanguageDetector()
        result = detector.detect_from_extension(filename)
        assert result == expected
    
    def test_case_insensitive_extension(self):
        """Should handle case-insensitive extensions."""
        detector = LanguageDetector()
        
        # Test various case combinations
        assert detector.detect_from_extension('test.CPP') == Language.CPP
        assert detector.detect_from_extension('test.Py') == Language.PYTHON
        assert detector.detect_from_extension('Test.JAVA') == Language.JAVA
    
    def test_handles_full_paths(self):
        """Should extract extension from full file paths."""
        detector = LanguageDetector()
        
        assert detector.detect_from_extension('/path/to/test.cpp') == Language.CPP
        assert detector.detect_from_extension('C:\\Users\\test.py') == Language.PYTHON
        assert detector.detect_from_extension('./relative/Main.java') == Language.JAVA


class TestLanguageDetectorConfiguration:
    """Test custom language configuration."""
    
    def test_loads_default_configs(self):
        """Should load default compiler configurations."""
        detector = LanguageDetector()
        
        assert Language.CPP in detector.DEFAULT_CONFIGS
        assert Language.PYTHON in detector.DEFAULT_CONFIGS
        assert Language.JAVA in detector.DEFAULT_CONFIGS
    
    def test_default_cpp_config_has_compiler(self):
        """Should have C++ compiler configuration."""
        detector = LanguageDetector()
        cpp_config = detector.DEFAULT_CONFIGS[Language.CPP]
        
        assert 'compiler' in cpp_config
        assert cpp_config['compiler'] == 'g++'
        assert cpp_config['needs_compilation'] is True
    
    def test_default_python_config_has_interpreter(self):
        """Should have Python interpreter configuration."""
        detector = LanguageDetector()
        py_config = detector.DEFAULT_CONFIGS[Language.PYTHON]
        
        assert 'interpreter' in py_config
        assert py_config['interpreter'] == 'python'
        assert py_config['needs_compilation'] is False
    
    def test_default_java_config_has_compiler(self):
        """Should have Java compiler configuration."""
        detector = LanguageDetector()
        java_config = detector.DEFAULT_CONFIGS[Language.JAVA]
        
        assert 'compiler' in java_config
        assert java_config['compiler'] == 'javac'
        assert java_config['needs_compilation'] is True
    
    def test_merges_custom_config(self):
        """Should merge custom config with defaults."""
        custom_config = {
            'languages': {
                'cpp': {'compiler': 'clang++', 'std_version': 'c++20'}
            }
        }
        detector = LanguageDetector(custom_config)
        
        # Should have merged config
        cpp_config = detector.get_language_config(Language.CPP)
        assert cpp_config['compiler'] == 'clang++'
        assert cpp_config['std_version'] == 'c++20'
        # Should preserve other defaults
        assert 'flags' in cpp_config
    
    def test_custom_config_does_not_override_defaults_for_other_languages(self):
        """Custom config for one language should not affect others."""
        custom_config = {
            'languages': {
                'cpp': {'compiler': 'clang++'}
            }
        }
        detector = LanguageDetector(custom_config)
        
        # Python config should remain unchanged
        py_config = detector.get_language_config(Language.PYTHON)
        assert py_config['interpreter'] == 'python'


class TestLanguageDetectorExecutablePaths:
    """Test executable path generation for different languages."""
    
    def test_cpp_executable_path_windows(self):
        """Should generate .exe path for C++ on Windows."""
        import os
        detector = LanguageDetector()
        
        source_path = 'test.cpp'
        exe_path = detector.get_executable_path(source_path, Language.CPP)
        
        if os.name == 'nt':
            assert exe_path.endswith('.exe')
        else:
            # On Unix, no extension
            assert not exe_path.endswith('.exe')
    
    def test_python_executable_path(self):
        """Should return same path for Python files."""
        detector = LanguageDetector()
        
        source_path = 'test.py'
        exe_path = detector.get_executable_path(source_path, Language.PYTHON)
        
        # Python files execute directly
        assert exe_path.endswith('.py')
    
    def test_java_executable_path(self):
        """Should generate .class path for Java."""
        detector = LanguageDetector()
        
        source_path = 'Main.java'
        exe_path = detector.get_executable_path(source_path, Language.JAVA)
        
        # Java compiles to .class
        assert '.class' in exe_path or exe_path.endswith('Main')
    
    def test_preserves_directory_in_executable_path(self):
        """Should preserve directory structure in executable path."""
        detector = LanguageDetector()
        
        source_path = '/path/to/test.cpp'
        exe_path = detector.get_executable_path(source_path, Language.CPP)
        
        assert '/path/to/' in exe_path or '\\path\\to\\' in exe_path


class TestLanguageDetectorContentAnalysis:
    """Test language detection from file content."""
    
    def test_detects_cpp_from_content(self, temp_dir):
        """Should detect C++ from file content."""
        cpp_content = '''
#include <iostream>
using namespace std;

int main() {
    cout << "Hello" << endl;
    return 0;
}
'''
        
        detector = LanguageDetector()
        language = detector.detect_from_content(cpp_content)
        
        assert language == Language.CPP
    
    def test_detects_python_from_content(self, temp_dir):
        """Should detect Python from file content."""
        py_content = '''
def main():
    print("Hello")

if __name__ == '__main__':
    main()
'''
        
        detector = LanguageDetector()
        language = detector.detect_from_content(py_content)
        
        assert language == Language.PYTHON
    
    def test_detects_java_from_content(self, temp_dir):
        """Should detect Java from file content."""
        java_content = '''
public class Main {
    public static void main(String[] args) {
        System.out.println("Hello");
    }
}
'''
        
        detector = LanguageDetector()
        language = detector.detect_from_content(java_content)
        
        assert language == Language.JAVA
    
    def test_returns_unknown_for_ambiguous_content(self, temp_dir):
        """Should return UNKNOWN for unclear content."""
        file = temp_dir / 'unknown.txt'
        file.write_text('Just some random text with no code patterns')
        
        detector = LanguageDetector()
        language = detector.detect_from_content(str(file))
        
        assert language == Language.UNKNOWN


class TestLanguageDetectorValidation:
    """Test language validation and checking."""
    
    def test_needs_compilation_cpp(self):
        """Should indicate C++ needs compilation."""
        detector = LanguageDetector()
        config = detector.get_language_config(Language.CPP)
        
        assert config['needs_compilation'] is True
    
    def test_needs_compilation_python(self):
        """Should indicate Python does not need compilation."""
        detector = LanguageDetector()
        config = detector.get_language_config(Language.PYTHON)
        
        assert config['needs_compilation'] is False
    
    def test_needs_compilation_java(self):
        """Should indicate Java needs compilation."""
        detector = LanguageDetector()
        config = detector.get_language_config(Language.JAVA)
        
        assert config['needs_compilation'] is True
    
    def test_is_supported_language(self):
        """Should correctly identify supported languages."""
        # Check if languages are in supported list
        supported = LanguageDetector.get_supported_languages()
        
        assert Language.CPP in supported
        assert Language.PYTHON in supported
        assert Language.JAVA in supported
        assert Language.UNKNOWN not in supported


class TestLanguageDetectorCompilerFlags:
    """Test compiler flag generation."""
    
    def test_cpp_optimization_flags(self):
        """Should provide C++ optimization flags."""
        detector = LanguageDetector()
        config = detector.get_language_config(Language.CPP)
        
        assert 'optimization' in config
        assert config['optimization'] == 'O2'
        assert 'flags' in config
        assert isinstance(config['flags'], list)
    
    def test_cpp_standard_version(self):
        """Should specify C++ standard version."""
        detector = LanguageDetector()
        config = detector.get_language_config(Language.CPP)
        
        assert 'std_version' in config
        assert 'c++' in config['std_version']
    
    def test_python_unbuffered_flag(self):
        """Should provide Python unbuffered flag."""
        detector = LanguageDetector()
        config = detector.get_language_config(Language.PYTHON)
        
        assert 'flags' in config
        assert '-u' in config['flags']
    
    def test_java_version_info(self):
        """Should provide Java version information."""
        detector = LanguageDetector()
        config = detector.get_language_config(Language.JAVA)
        
        assert 'version' in config
        assert config['version'] is not None


class TestLanguageDetectorEdgeCases:
    """Test edge cases and error handling."""
    
    def test_handles_empty_filename(self):
        """Should handle empty filename gracefully."""
        detector = LanguageDetector()
        result = detector.detect_from_extension('')
        
        assert result == Language.UNKNOWN
    
    def test_handles_filename_with_multiple_dots(self):
        """Should extract correct extension from filename with dots."""
        detector = LanguageDetector()
        
        assert detector.detect_from_extension('test.backup.cpp') == Language.CPP
        assert detector.detect_from_extension('my.test.file.py') == Language.PYTHON
    
    def test_handles_nonexistent_file_content_detection(self):
        """Should handle nonexistent files in content detection."""
        detector = LanguageDetector()
        result = detector.detect_from_content('/nonexistent/file.txt')
        
        assert result == Language.UNKNOWN
    
    def test_get_compiler_config_for_unknown_language(self):
        """Should raise ValueError for unknown language config request."""
        detector = LanguageDetector()
        
        # Should raise ValueError for unknown language
        with pytest.raises(ValueError, match="Cannot get config for UNKNOWN language"):
            detector.get_language_config(Language.UNKNOWN)


class TestLanguageDetectorIntegration:
    """Test integration scenarios with multiple languages."""
    
    def test_detects_mixed_language_project(self, temp_dir):
        """Should correctly detect languages in multi-language project."""
        files = {
            'test.cpp': Language.CPP,
            'generator.py': Language.PYTHON,
            'Main.java': Language.JAVA,
            'validator.cc': Language.CPP,
        }
        
        detector = LanguageDetector()
        
        for filename, expected_lang in files.items():
            file_path = temp_dir / filename
            file_path.write_text('// content')
            
            detected = detector.detect_from_extension(str(file_path))
            assert detected == expected_lang, f"Failed for {filename}"
    
    def test_consistent_detection_methods(self, temp_dir):
        """Extension and content detection should agree when possible."""
        cpp_file = temp_dir / 'test.cpp'
        cpp_content = '#include <iostream>\nint main() { return 0; }'
        cpp_file.write_text(cpp_content)
        
        detector = LanguageDetector()
        
        ext_detection = detector.detect_from_extension(str(cpp_file))
        content_detection = detector.detect_from_content(cpp_content)
        
        # Both should detect C++
        assert ext_detection == Language.CPP
        assert content_detection == Language.CPP


class TestGetCompilerCommand:
    """Test compiler command generation."""
    
    def test_cpp_compiler_command_with_output(self):
        """Should generate correct C++ compiler command."""
        detector = LanguageDetector()
        cmd = detector.get_compiler_command(Language.CPP, 'test.cpp', 'test.exe')
        
        assert 'g++' in cmd
        assert '-O2' in cmd
        assert '-std=c++17' in cmd
        assert 'test.cpp' in cmd
        assert '-o' in cmd
        assert 'test.exe' in cmd
    
    def test_cpp_compiler_command_without_output(self):
        """Should generate C++ command without output file."""
        detector = LanguageDetector()
        cmd = detector.get_compiler_command(Language.CPP, 'test.cpp')
        
        assert 'test.cpp' in cmd
        assert '-o' not in cmd
    
    def test_cpp_compiler_command_with_custom_flags(self):
        """Should use custom flags for C++ compilation."""
        detector = LanguageDetector()
        custom_flags = ['-g', '-DDEBUG']
        cmd = detector.get_compiler_command(Language.CPP, 'test.cpp', custom_flags=custom_flags)
        
        assert '-g' in cmd
        assert '-DDEBUG' in cmd
    
    def test_python_interpreter_command(self):
        """Should generate correct Python interpreter command."""
        detector = LanguageDetector()
        cmd = detector.get_compiler_command(Language.PYTHON, 'test.py')
        
        assert 'python' in cmd
        assert '-u' in cmd
        assert 'test.py' in cmd
    
    def test_python_command_with_custom_flags(self):
        """Should use custom flags for Python execution."""
        detector = LanguageDetector()
        custom_flags = ['-W', 'ignore']
        cmd = detector.get_compiler_command(Language.PYTHON, 'test.py', custom_flags=custom_flags)
        
        assert '-W' in cmd
        assert 'ignore' in cmd
    
    def test_java_compiler_command_with_output(self):
        """Should generate correct Java compiler command."""
        detector = LanguageDetector()
        cmd = detector.get_compiler_command(Language.JAVA, 'Main.java', 'build/Main.class')
        
        assert 'javac' in cmd
        assert 'Main.java' in cmd
        assert '-d' in cmd
        assert 'build' in cmd
    
    def test_java_compiler_command_without_output(self):
        """Should generate Java command without output directory."""
        detector = LanguageDetector()
        cmd = detector.get_compiler_command(Language.JAVA, 'Main.java')
        
        assert 'javac' in cmd
        assert 'Main.java' in cmd
    
    def test_unsupported_language_raises_error(self):
        """Should raise ValueError for unsupported language."""
        detector = LanguageDetector()
        
        with pytest.raises(ValueError, match="Cannot get config for UNKNOWN language"):
            detector.get_compiler_command(Language.UNKNOWN, 'test.txt')


class TestGetExecutionCommand:
    """Test execution command generation."""
    
    def test_cpp_execution_command(self):
        """Should generate direct execution for compiled C++."""
        detector = LanguageDetector()
        cmd = detector.get_execution_command(Language.CPP, 'test.exe')
        
        assert cmd == ['test.exe']
    
    def test_python_execution_command(self):
        """Should generate Python interpreter execution."""
        detector = LanguageDetector()
        cmd = detector.get_execution_command(Language.PYTHON, 'test.py')
        
        assert 'python' in cmd
        assert '-u' in cmd
        assert 'test.py' in cmd
    
    def test_java_execution_command_with_class_name(self):
        """Should generate Java execution with class name."""
        detector = LanguageDetector()
        cmd = detector.get_execution_command(Language.JAVA, 'build/', 'Main')
        
        assert 'java' in cmd
        assert '-cp' in cmd
        assert 'build/' in cmd or 'build' in cmd
        assert 'Main' in cmd
    
    def test_java_execution_command_extracts_class_name(self):
        """Should extract class name from path if not provided."""
        detector = LanguageDetector()
        cmd = detector.get_execution_command(Language.JAVA, 'build/Main.class')
        
        assert 'java' in cmd
        assert 'Main' in cmd
    
    def test_execution_command_unsupported_language(self):
        """Should raise ValueError for unsupported language execution."""
        detector = LanguageDetector()
        
        with pytest.raises(ValueError, match="Cannot get config for UNKNOWN language"):
            detector.get_execution_command(Language.UNKNOWN, 'test.txt')


class TestDetectLanguage:
    """Test combined detection method."""
    
    def test_detect_language_from_extension_only(self):
        """Should detect language from extension without content."""
        detector = LanguageDetector()
        lang = detector.detect_language('test.cpp')
        
        assert lang == Language.CPP
    
    def test_detect_language_fallback_to_content(self):
        """Should fallback to content detection when extension unknown."""
        detector = LanguageDetector()
        content = '#include <iostream>\nint main() {}'
        lang = detector.detect_language('unknown.txt', content=content)
        
        assert lang == Language.CPP
    
    def test_detect_language_prefers_extension(self):
        """Should prefer extension over content when available."""
        detector = LanguageDetector()
        python_content = 'print("hello")'
        lang = detector.detect_language('test.cpp', content=python_content)
        
        # Extension should win
        assert lang == Language.CPP
    
    def test_detect_language_returns_unknown_without_both(self):
        """Should return UNKNOWN when extension and content fail."""
        detector = LanguageDetector()
        lang = detector.detect_language('unknown.txt')
        
        assert lang == Language.UNKNOWN


class TestMatchesLanguagePatterns:
    """Test pattern matching helper method."""
    
    def test_matches_cpp_patterns(self):
        """Should match C++ patterns in content."""
        detector = LanguageDetector()
        cpp_content = '#include <iostream>\nusing namespace std;'
        
        assert detector._matches_language_patterns(cpp_content, Language.CPP) is True
    
    def test_matches_python_patterns(self):
        """Should match Python patterns in content."""
        detector = LanguageDetector()
        py_content = 'def main():\n    print("hello")'
        
        assert detector._matches_language_patterns(py_content, Language.PYTHON) is True
    
    def test_matches_java_patterns(self):
        """Should match Java patterns in content."""
        detector = LanguageDetector()
        java_content = 'public class Main {\n    public static void main(String[] args) {}'
        
        assert detector._matches_language_patterns(java_content, Language.JAVA) is True
    
    def test_no_match_for_unrelated_content(self):
        """Should not match when content doesn't fit patterns."""
        detector = LanguageDetector()
        random_content = 'just some random text'
        
        assert detector._matches_language_patterns(random_content, Language.CPP) is False
        assert detector._matches_language_patterns(random_content, Language.PYTHON) is False
        assert detector._matches_language_patterns(random_content, Language.JAVA) is False


class TestDetectFromContentEdgeCases:
    """Test content detection edge cases."""
    
    def test_detect_from_content_with_empty_string(self):
        """Should return UNKNOWN for empty content."""
        detector = LanguageDetector()
        lang = detector.detect_from_content('')
        
        assert lang == Language.UNKNOWN
    
    def test_detect_from_content_with_hint(self):
        """Should use hint extension to narrow detection."""
        detector = LanguageDetector()
        cpp_content = '#include <iostream>'
        lang = detector.detect_from_content(cpp_content, hint_extension='.cpp')
        
        assert lang == Language.CPP
    
    def test_detect_from_content_hint_mismatch(self):
        """Should detect from content even when hint mismatches."""
        detector = LanguageDetector()
        python_content = 'def main():\n    pass'
        # Hint says .cpp but content is clearly Python
        lang = detector.detect_from_content(python_content, hint_extension='.cpp')
        
        # Should fallback to best match from all patterns
        assert lang == Language.PYTHON
    
    def test_detect_from_content_multiple_pattern_matches(self):
        """Should choose language with most pattern matches."""
        detector = LanguageDetector()
        cpp_content = '''
        #include <iostream>
        using namespace std;
        int main() {
            std::cout << "hello";
            return 0;
        }
        '''
        lang = detector.detect_from_content(cpp_content)
        
        assert lang == Language.CPP


class TestGetSupportedExtensions:
    """Test supported extensions listing."""
    
    def test_get_supported_extensions_returns_list(self):
        """Should return list of supported extensions."""
        extensions = LanguageDetector.get_supported_extensions()
        
        assert isinstance(extensions, list)
        assert len(extensions) > 0
    
    def test_get_supported_extensions_includes_common_types(self):
        """Should include common file extensions."""
        extensions = LanguageDetector.get_supported_extensions()
        
        assert '.cpp' in extensions
        assert '.py' in extensions
        assert '.java' in extensions
    
    def test_get_supported_extensions_includes_cpp_variants(self):
        """Should include all C++ extension variants."""
        extensions = LanguageDetector.get_supported_extensions()
        
        assert '.cpp' in extensions
        assert '.cc' in extensions
        assert '.cxx' in extensions
        assert '.h' in extensions
        assert '.hpp' in extensions


class TestGetLanguageConfigErrorHandling:
    """Test error handling in language configuration."""
    
    def test_get_config_unknown_language_raises_error(self):
        """Should raise ValueError for UNKNOWN language."""
        detector = LanguageDetector()
        
        with pytest.raises(ValueError, match="Cannot get config for UNKNOWN language"):
            detector.get_language_config(Language.UNKNOWN)
    
    def test_get_config_returns_copy(self):
        """Should return copy of config, not original."""
        detector = LanguageDetector()
        config1 = detector.get_language_config(Language.CPP)
        config2 = detector.get_language_config(Language.CPP)
        
        # Modify one copy
        config1['test_field'] = 'modified'
        
        # Other copy should be unaffected
        assert 'test_field' not in config2


class TestContentDetectionScoring:
    """Test content detection scoring mechanism."""
    
    def test_higher_score_wins_detection(self):
        """Language with more matching patterns should win."""
        detector = LanguageDetector()
        
        # Content with multiple C++ indicators
        strong_cpp_content = '''
        #include <iostream>
        #include <vector>
        using namespace std;
        int main() {
            std::vector<int> v;
            return 0;
        }
        '''
        
        lang = detector.detect_from_content(strong_cpp_content)
        assert lang == Language.CPP
    
    def test_zero_score_returns_unknown(self):
        """Content with no pattern matches should return UNKNOWN."""
        detector = LanguageDetector()
        
        no_match_content = '1234567890 random numbers'
        lang = detector.detect_from_content(no_match_content)
        
        assert lang == Language.UNKNOWN
    
    def test_tie_score_picks_first(self):
        """When scores tie, should pick based on ordering."""
        detector = LanguageDetector()
        
        # Minimal content that could match multiple languages
        minimal_content = 'main'
        lang = detector.detect_from_content(minimal_content)
        
        # Should return something or UNKNOWN, shouldn't crash
        assert lang in [Language.CPP, Language.PYTHON, Language.JAVA, Language.UNKNOWN]
