"""
Test suite for BaseCompiler multi-language compilation.

BaseCompiler handles compilation for C++, Python, and Java with smart caching,
parallel compilation, and optimization flags. Tests verify language detection,
compilation delegation, and caching behavior.
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock, call
import os
import time

from src.app.core.tools.base.base_compiler import BaseCompiler
from src.app.core.tools.base.language_detector import Language


class TestBaseCompilerInitialization:
    """Test BaseCompiler initialization with multi-language support."""
    
    def test_init_detects_cpp_files(self, temp_workspace):
        """Should detect C++ files and create appropriate executables."""
        cpp_file = temp_workspace / 'comparator' / 'test.cpp'
        cpp_file.parent.mkdir(parents=True, exist_ok=True)
        cpp_file.write_text('int main() { return 0; }')
        
        files = {'test': str(cpp_file)}
        compiler = BaseCompiler(str(temp_workspace), files, test_type='comparator')
        
        assert 'test' in compiler.file_languages
        assert compiler.file_languages['test'] == Language.CPP
    
    def test_init_detects_python_files(self, temp_workspace):
        """Should detect Python files (no compilation needed)."""
        py_file = temp_workspace / 'comparator' / 'test.py'
        py_file.parent.mkdir(parents=True, exist_ok=True)
        py_file.write_text('print("hello")')
        
        files = {'test': str(py_file)}
        compiler = BaseCompiler(str(temp_workspace), files, test_type='comparator')
        
        assert compiler.file_languages['test'] == Language.PYTHON
    
    def test_init_detects_java_files(self, temp_workspace):
        """Should detect Java files."""
        java_file = temp_workspace / 'comparator' / 'Main.java'
        java_file.parent.mkdir(parents=True, exist_ok=True)
        java_file.write_text('public class Main { }')
        
        files = {'test': str(java_file)}
        compiler = BaseCompiler(str(temp_workspace), files, test_type='comparator')
        
        assert compiler.file_languages['test'] == Language.JAVA
    
    def test_init_creates_executables_dict(self, temp_workspace):
        """Should create executables dict with language-aware paths."""
        cpp_file = temp_workspace / 'comparator' / 'test.cpp'
        cpp_file.parent.mkdir(parents=True, exist_ok=True)
        cpp_file.write_text('int main() { return 0; }')
        
        files = {'test': str(cpp_file)}
        compiler = BaseCompiler(str(temp_workspace), files, test_type='comparator')
        
        assert 'test' in compiler.executables
        # Should have .exe extension on Windows
        if os.name == 'nt':
            assert compiler.executables['test'].endswith('.exe')
    
    def test_init_accepts_optimization_level(self, temp_workspace):
        """Should accept custom optimization level."""
        cpp_file = temp_workspace / 'comparator' / 'test.cpp'
        cpp_file.parent.mkdir(parents=True, exist_ok=True)
        cpp_file.write_text('int main() { return 0; }')
        
        files = {'test': str(cpp_file)}
        compiler = BaseCompiler(
            str(temp_workspace), 
            files, 
            test_type='comparator',
            optimization_level='O3'
        )
        
        assert compiler.optimization_level == 'O3'
    
    def test_init_accepts_custom_config(self, temp_workspace):
        """Should accept custom configuration dictionary."""
        cpp_file = temp_workspace / 'comparator' / 'test.cpp'
        cpp_file.parent.mkdir(parents=True, exist_ok=True)
        cpp_file.write_text('int main() { return 0; }')
        
        custom_config = {'languages': {'cpp': {'compiler': 'clang++'}}}
        files = {'test': str(cpp_file)}
        compiler = BaseCompiler(
            str(temp_workspace),
            files,
            test_type='comparator',
            config=custom_config
        )
        
        assert compiler.config == custom_config
    
    def test_init_resolves_relative_paths(self, temp_workspace):
        """Should resolve relative paths within test type directory."""
        test_dir = temp_workspace / 'comparator'
        test_dir.mkdir(parents=True, exist_ok=True)
        cpp_file = test_dir / 'test.cpp'
        cpp_file.write_text('int main() { return 0; }')
        
        # Use relative path
        files = {'test': 'test.cpp'}
        compiler = BaseCompiler(str(temp_workspace), files, test_type='comparator')
        
        # Should resolve to absolute path
        assert os.path.isabs(compiler.files['test'])
        assert compiler.files['test'].endswith('test.cpp')
    
    def test_init_handles_absolute_paths(self, temp_workspace):
        """Should use absolute paths as-is."""
        cpp_file = temp_workspace / 'comparator' / 'test.cpp'
        cpp_file.parent.mkdir(parents=True, exist_ok=True)
        cpp_file.write_text('int main() { return 0; }')
        
        # Use absolute path
        files = {'test': str(cpp_file)}
        compiler = BaseCompiler(str(temp_workspace), files, test_type='comparator')
        
        assert compiler.files['test'] == str(cpp_file)


class TestBaseCompilerSmartCaching:
    """Test timestamp-based compilation caching."""
    
    def test_needs_recompilation_when_executable_missing(self, temp_workspace):
        """Should need recompilation if executable doesn't exist."""
        cpp_file = temp_workspace / 'comparator' / 'test.cpp'
        cpp_file.parent.mkdir(parents=True, exist_ok=True)
        cpp_file.write_text('int main() { return 0; }')
        
        files = {'test': str(cpp_file)}
        compiler = BaseCompiler(str(temp_workspace), files, test_type='comparator')
        
        assert compiler._needs_recompilation('test') is True
    
    def test_skips_recompilation_for_python(self, temp_workspace):
        """Should not need compilation for Python files."""
        py_file = temp_workspace / 'comparator' / 'test.py'
        py_file.parent.mkdir(parents=True, exist_ok=True)
        py_file.write_text('print("hello")')
        
        files = {'test': str(py_file)}
        compiler = BaseCompiler(str(temp_workspace), files, test_type='comparator')
        
        assert compiler._needs_recompilation('test') is False
    
    def test_skips_recompilation_when_up_to_date(self, temp_workspace):
        """Should skip compilation if executable is newer than source."""
        cpp_file = temp_workspace / 'comparator' / 'test.cpp'
        cpp_file.parent.mkdir(parents=True, exist_ok=True)
        cpp_file.write_text('int main() { return 0; }')
        
        # Create executable with newer timestamp
        exe_file = cpp_file.with_suffix('.exe' if os.name == 'nt' else '')
        exe_file.write_text('binary')
        
        # Make executable newer
        time.sleep(0.1)
        os.utime(exe_file, None)
        
        files = {'test': str(cpp_file)}
        compiler = BaseCompiler(str(temp_workspace), files, test_type='comparator')
        
        # Should not need recompilation
        assert compiler._needs_recompilation('test') is False
    
    def test_needs_recompilation_when_source_newer(self, temp_workspace):
        """Should need recompilation if source is newer than executable."""
        cpp_file = temp_workspace / 'comparator' / 'test.cpp'
        cpp_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Create old executable first
        exe_file = cpp_file.with_suffix('.exe' if os.name == 'nt' else '')
        exe_file.write_text('old binary')
        
        # Create newer source file
        time.sleep(0.1)
        cpp_file.write_text('int main() { return 0; }')
        
        files = {'test': str(cpp_file)}
        compiler = BaseCompiler(str(temp_workspace), files, test_type='comparator')
        
        # Should need recompilation
        assert compiler._needs_recompilation('test') is True


class TestBaseCompilerCompilationDelegation:
    """Test compilation is delegated to language-specific compilers."""
    
    def test_compile_all_returns_true(self, temp_workspace):
        """Should return True immediately (async compilation)."""
        cpp_file = temp_workspace / 'comparator' / 'test.cpp'
        cpp_file.parent.mkdir(parents=True, exist_ok=True)
        cpp_file.write_text('int main() { return 0; }')
        
        files = {'test': str(cpp_file)}
        compiler = BaseCompiler(str(temp_workspace), files, test_type='comparator')
        
        result = compiler.compile_all()
        
        assert result is True
    
    def test_compile_all_starts_thread(self, temp_workspace):
        """Should start compilation in separate thread."""
        cpp_file = temp_workspace / 'comparator' / 'test.cpp'
        cpp_file.parent.mkdir(parents=True, exist_ok=True)
        cpp_file.write_text('int main() { return 0; }')
        
        files = {'test': str(cpp_file)}
        compiler = BaseCompiler(str(temp_workspace), files, test_type='comparator')
        
        with patch('threading.Thread') as mock_thread:
            compiler.compile_all()
            
            # Should create and start thread
            mock_thread.assert_called_once()
            mock_thread.return_value.start.assert_called_once()
    
    @pytest.mark.slow
    @pytest.mark.skip(reason="Threading test requires complex executor mocking - tested via integration tests")
    def test_parallel_compile_uses_correct_worker_count(self, temp_workspace):
        """Should use optimal number of workers for parallel compilation."""
        # Create multiple files
        files = {}
        for i in range(3):
            cpp_file = temp_workspace / 'comparator' / f'test{i}.cpp'
            cpp_file.parent.mkdir(parents=True, exist_ok=True)
            cpp_file.write_text('int main() { return 0; }')
            files[f'test{i}'] = str(cpp_file)
        
        compiler = BaseCompiler(str(temp_workspace), files, test_type='comparator')
        
        # Mock the entire compilation to avoid threading issues
        with patch.object(compiler, '_compile_single_file', return_value=(True, "Success")):
            with patch('src.app.core.tools.base.base_compiler.ThreadPoolExecutor') as mock_executor:
                # Configure the mock to work as a context manager
                mock_executor_instance = MagicMock()
                mock_executor.return_value.__enter__.return_value = mock_executor_instance
                
                compiler._parallel_compile_all()
                
                # Should use ThreadPoolExecutor
                mock_executor.assert_called_once()


class TestBaseCompilerSignalEmission:
    """Test compilation progress signals."""
    
    def test_emits_compilation_output_signal(self, temp_workspace, qtbot):
        """Should emit compilationOutput signal with progress messages."""
        cpp_file = temp_workspace / 'comparator' / 'test.cpp'
        cpp_file.parent.mkdir(parents=True, exist_ok=True)
        cpp_file.write_text('int main() { return 0; }')
        
        files = {'test': str(cpp_file)}
        compiler = BaseCompiler(str(temp_workspace), files, test_type='comparator')
        
        signal_spy = []
        compiler.compilationOutput.connect(lambda msg, type: signal_spy.append((msg, type)))
        
        with patch.object(compiler, '_compile_single_file', return_value=(True, "Success")):
            compiler._parallel_compile_all()
        
        # Should have emitted some output
        assert len(signal_spy) > 0
    
    def test_emits_compilation_finished_signal(self, temp_workspace, qtbot):
        """Should emit compilationFinished signal with success status."""
        cpp_file = temp_workspace / 'comparator' / 'test.cpp'
        cpp_file.parent.mkdir(parents=True, exist_ok=True)
        cpp_file.write_text('int main() { return 0; }')
        
        files = {'test': str(cpp_file)}
        compiler = BaseCompiler(str(temp_workspace), files, test_type='comparator')
        
        with qtbot.waitSignal(compiler.compilationFinished, timeout=5000) as blocker:
            with patch.object(compiler, '_compile_single_file', return_value=(True, "OK")):
                compiler._parallel_compile_all()
        
        # Should emit True for successful compilation
        assert blocker.args[0] is True
    
    def test_emits_false_on_compilation_failure(self, temp_workspace, qtbot):
        """Should emit False when compilation fails."""
        cpp_file = temp_workspace / 'comparator' / 'test.cpp'
        cpp_file.parent.mkdir(parents=True, exist_ok=True)
        cpp_file.write_text('int main() { return 0; }')
        
        files = {'test': str(cpp_file)}
        compiler = BaseCompiler(str(temp_workspace), files, test_type='comparator')
        
        with qtbot.waitSignal(compiler.compilationFinished, timeout=5000) as blocker:
            with patch.object(compiler, '_compile_single_file', return_value=(False, "Error")):
                compiler._parallel_compile_all()
        
        # Should emit False for failed compilation
        assert blocker.args[0] is False


class TestBaseCompilerLanguageIntegration:
    """Test integration with language-specific compilers."""
    
    def test_creates_language_detector(self, temp_workspace):
        """Should initialize LanguageDetector with config."""
        cpp_file = temp_workspace / 'comparator' / 'test.cpp'
        cpp_file.parent.mkdir(parents=True, exist_ok=True)
        cpp_file.write_text('int main() { return 0; }')
        
        custom_config = {'languages': {'cpp': {'compiler': 'clang++'}}}
        files = {'test': str(cpp_file)}
        compiler = BaseCompiler(
            str(temp_workspace),
            files,
            test_type='comparator',
            config=custom_config
        )
        
        assert compiler.language_detector is not None
        assert compiler.language_detector.config == custom_config
    
    def test_detects_multiple_languages(self, temp_workspace):
        """Should correctly detect different languages in same project."""
        test_dir = temp_workspace / 'comparator'
        test_dir.mkdir(parents=True, exist_ok=True)
        
        cpp_file = test_dir / 'test.cpp'
        cpp_file.write_text('int main() { return 0; }')
        
        py_file = test_dir / 'generator.py'
        py_file.write_text('print("test")')
        
        java_file = test_dir / 'Main.java'
        java_file.write_text('public class Main { }')
        
        files = {
            'test': str(cpp_file),
            'generator': str(py_file),
            'validator': str(java_file)
        }
        compiler = BaseCompiler(str(temp_workspace), files, test_type='comparator')
        
        assert compiler.file_languages['test'] == Language.CPP
        assert compiler.file_languages['generator'] == Language.PYTHON
        assert compiler.file_languages['validator'] == Language.JAVA
    
    def test_creates_correct_executable_paths_per_language(self, temp_workspace):
        """Should create language-appropriate executable paths."""
        test_dir = temp_workspace / 'comparator'
        test_dir.mkdir(parents=True, exist_ok=True)
        
        cpp_file = test_dir / 'test.cpp'
        cpp_file.write_text('int main() { return 0; }')
        
        py_file = test_dir / 'gen.py'
        py_file.write_text('print("test")')
        
        files = {
            'test': str(cpp_file),
            'gen': str(py_file)
        }
        compiler = BaseCompiler(str(temp_workspace), files, test_type='comparator')
        
        # C++ should have executable extension
        if os.name == 'nt':
            assert compiler.executables['test'].endswith('.exe')
        
        # Python should point to the .py file itself
        assert compiler.executables['gen'].endswith('.py')


class TestBaseCompilerErrorHandling:
    """Test error handling and edge cases."""
    
    def test_handles_missing_source_file(self, temp_workspace):
        """Should handle initialization with non-existent files."""
        files = {'test': str(temp_workspace / 'comparator' / 'nonexistent.cpp')}
        
        # Should not raise exception during init
        compiler = BaseCompiler(str(temp_workspace), files, test_type='comparator')
        assert compiler is not None
    
    def test_handles_invalid_test_type(self, temp_workspace):
        """Should raise error for invalid test type."""
        cpp_file = temp_workspace / 'comparator' / 'test.cpp'
        cpp_file.parent.mkdir(parents=True, exist_ok=True)
        cpp_file.write_text('int main() { return 0; }')
        
        files = {'test': str(cpp_file)}
        
        with pytest.raises(ValueError, match="Unknown test type"):
            BaseCompiler(str(temp_workspace), files, test_type='invalid')
    
    def test_compilation_failed_flag(self, temp_workspace):
        """Should set compilation_failed flag on error."""
        cpp_file = temp_workspace / 'comparator' / 'test.cpp'
        cpp_file.parent.mkdir(parents=True, exist_ok=True)
        cpp_file.write_text('int main() { return 0; }')
        
        files = {'test': str(cpp_file)}
        compiler = BaseCompiler(str(temp_workspace), files, test_type='comparator')
        
        assert compiler.compilation_failed is False
        
        # Simulate compilation failure
        with patch.object(compiler, '_compile_single_file', return_value=(False, "Error")):
            compiler._parallel_compile_all()
        
        assert compiler.compilation_failed is True


class TestBaseCompilerMultiFileCompilation:
    """Test compilation of multiple files."""
    
    def test_compiles_multiple_files(self, temp_workspace):
        """Should compile all files in files dict."""
        test_dir = temp_workspace / 'comparator'
        test_dir.mkdir(parents=True, exist_ok=True)
        
        files = {}
        for name in ['generator', 'test', 'correct']:
            cpp_file = test_dir / f'{name}.cpp'
            cpp_file.write_text('int main() { return 0; }')
            files[name] = str(cpp_file)
        
        compiler = BaseCompiler(str(temp_workspace), files, test_type='comparator')
        
        assert len(compiler.files) == 3
        assert len(compiler.executables) == 3
    
    def test_skips_python_files_in_compilation(self, temp_workspace):
        """Should skip Python files but include them in executables."""
        test_dir = temp_workspace / 'comparator'
        test_dir.mkdir(parents=True, exist_ok=True)
        
        cpp_file = test_dir / 'test.cpp'
        cpp_file.write_text('int main() { return 0; }')
        
        py_file = test_dir / 'generator.py'
        py_file.write_text('print("test")')
        
        files = {
            'test': str(cpp_file),
            'generator': str(py_file)
        }
        compiler = BaseCompiler(str(temp_workspace), files, test_type='comparator')
        
        # Python file should be in executables
        assert 'generator' in compiler.executables
        # But should not need compilation
        assert compiler._needs_recompilation('generator') is False


class TestBaseCompilerWorkspaceIntegration:
    """Test integration with workspace directory structure."""
    
    def test_uses_correct_test_type_directory(self, temp_workspace):
        """Should resolve files within correct test type directory."""
        # Create nested structure
        for test_type in ['comparator', 'validator', 'benchmarker']:
            (temp_workspace / test_type).mkdir(parents=True, exist_ok=True)
        
        cpp_file = temp_workspace / 'comparator' / 'test.cpp'
        cpp_file.write_text('int main() { return 0; }')
        
        files = {'test': 'test.cpp'}  # Relative path
        compiler = BaseCompiler(str(temp_workspace), files, test_type='comparator')
        
        # Should resolve to comparator directory
        assert 'comparator' in compiler.files['test']
    
    def test_different_test_types_use_different_dirs(self, temp_workspace):
        """Should use different directories for different test types."""
        for test_type in ['comparator', 'validator']:
            test_dir = temp_workspace / test_type
            test_dir.mkdir(parents=True, exist_ok=True)
            (test_dir / 'test.cpp').write_text('int main() { return 0; }')
        
        files = {'test': 'test.cpp'}
        
        compiler1 = BaseCompiler(str(temp_workspace), files, test_type='comparator')
        compiler2 = BaseCompiler(str(temp_workspace), files, test_type='validator')
        
        # Should point to different directories
        assert 'comparator' in compiler1.files['test']
        assert 'validator' in compiler2.files['test']


# ============================================================================
# Additional Coverage Tests for Missing Lines
# ============================================================================

class TestBaseCompilerCachingStatusMessages:
    """Test status messages for up-to-date files of different languages."""
    
    def test_python_up_to_date_message(self, temp_workspace, qtbot):
        """Should emit Python-specific message when up-to-date."""
        py_file = temp_workspace / 'comparator' / 'test.py'
        py_file.parent.mkdir(parents=True, exist_ok=True)
        py_file.write_text('print("hello")')
        
        files = {'test': str(py_file)}
        compiler = BaseCompiler(str(temp_workspace), files, test_type='comparator')
        
        # Mock to make it appear up-to-date
        with patch.object(compiler, '_needs_recompilation', return_value=False):
            messages = []
            compiler.compilationOutput.connect(lambda msg, fmt: messages.append(msg))
            
            # Use waitSignal to ensure signal is emitted
            with qtbot.waitSignal(compiler.compilationFinished, timeout=2000):
                compiler.compile_all()
            
            # Should emit "no syntax errors" message
            full_msg = ''.join(messages)
            assert 'no syntax errors' in full_msg or 'up-to-date' in full_msg.lower()
    
    def test_java_up_to_date_message(self, temp_workspace, qtbot):
        """Should emit Java-specific message when up-to-date."""
        java_file = temp_workspace / 'comparator' / 'Test.java'
        java_file.parent.mkdir(parents=True, exist_ok=True)
        java_file.write_text('public class Test { }')
        
        files = {'test': str(java_file)}
        compiler = BaseCompiler(str(temp_workspace), files, test_type='comparator')
        
        # Mock to make it appear up-to-date
        with patch.object(compiler, '_needs_recompilation', return_value=False):
            messages = []
            compiler.compilationOutput.connect(lambda msg, fmt: messages.append(msg))
            
            with qtbot.waitSignal(compiler.compilationFinished, timeout=2000):
                compiler.compile_all()
            
            # Should emit ".class is up-to-date" message
            full_msg = ''.join(messages)
            assert '.class' in full_msg or 'up-to-date' in full_msg.lower()
    
    def test_cpp_up_to_date_message(self, temp_workspace, qtbot):
        """Should emit C++-specific message when up-to-date."""
        cpp_file = temp_workspace / 'comparator' / 'test.cpp'
        cpp_file.parent.mkdir(parents=True, exist_ok=True)
        cpp_file.write_text('int main() { return 0; }')
        
        # Create up-to-date executable
        exe_file = cpp_file.with_suffix('.exe' if os.name == 'nt' else '')
        exe_file.write_text('binary')
        time.sleep(0.1)
        exe_file.touch()  # Make newer than source
        
        files = {'test': str(cpp_file)}
        compiler = BaseCompiler(str(temp_workspace), files, test_type='comparator')
        
        messages = []
        compiler.compilationOutput.connect(lambda msg, fmt: messages.append(msg))
        
        with qtbot.waitSignal(compiler.compilationFinished, timeout=2000):
            compiler.compile_all()
        
        # Should emit executable name with "up-to-date"
        full_msg = ''.join(messages)
        assert 'up-to-date' in full_msg.lower()


class TestBaseCompilerTimestampEdgeCases:
    """Test timestamp checking edge cases."""
    
    def test_needs_recompilation_python_always_false(self, temp_workspace):
        """Python files never need recompilation."""
        py_file = temp_workspace / 'comparator' / 'test.py'
        py_file.parent.mkdir(parents=True, exist_ok=True)
        py_file.write_text('print("hello")')
        
        files = {'test': str(py_file)}
        compiler = BaseCompiler(str(temp_workspace), files, test_type='comparator')
        
        # Python never needs recompilation
        assert compiler._needs_recompilation('test') is False
    
    def test_needs_recompilation_source_missing_returns_true(self, temp_workspace):
        """Should return True if source file doesn't exist."""
        cpp_file = temp_workspace / 'comparator' / 'nonexistent.cpp'
        
        files = {'test': str(cpp_file)}
        compiler = BaseCompiler(str(temp_workspace), files, test_type='comparator')
        
        # Source doesn't exist, should return True
        assert compiler._needs_recompilation('test') is True
    
    def test_needs_recompilation_oserror_returns_true(self, temp_workspace):
        """Should return True on OSError during timestamp check."""
        cpp_file = temp_workspace / 'comparator' / 'test.cpp'
        cpp_file.parent.mkdir(parents=True, exist_ok=True)
        cpp_file.write_text('int main() { return 0; }')
        
        exe_file = cpp_file.with_suffix('.exe' if os.name == 'nt' else '')
        exe_file.write_text('binary')
        
        files = {'test': str(cpp_file)}
        compiler = BaseCompiler(str(temp_workspace), files, test_type='comparator')
        
        # Mock getmtime to raise OSError
        with patch('os.path.getmtime', side_effect=OSError("Permission denied")):
            assert compiler._needs_recompilation('test') is True


class TestBaseCompilerLanguageCompilerCreation:
    """Test language-specific compiler creation and caching."""
    
    def test_unknown_language_returns_error(self, temp_workspace):
        """Should return error for unknown language."""
        cpp_file = temp_workspace / 'comparator' / 'test.cpp'
        cpp_file.parent.mkdir(parents=True, exist_ok=True)
        cpp_file.write_text('int main() { return 0; }')
        
        files = {'test': str(cpp_file)}
        compiler = BaseCompiler(str(temp_workspace), files, test_type='comparator')
        
        # Manually set file_languages to UNKNOWN after init
        compiler.file_languages['test'] = Language.UNKNOWN
        
        # Should return error message (the _compile_single_file checks for UNKNOWN)
        success, message = compiler._compile_single_file('test')
        assert success is False
        assert 'Unknown language' in message or 'unknown' in message.lower()
    
    def test_language_compiler_caching(self, temp_workspace):
        """Should cache language-specific compilers."""
        cpp_file = temp_workspace / 'comparator' / 'test.cpp'
        cpp_file.parent.mkdir(parents=True, exist_ok=True)
        cpp_file.write_text('int main() { return 0; }')
        
        files = {'test': str(cpp_file)}
        compiler = BaseCompiler(str(temp_workspace), files, test_type='comparator')
        
        # Compile once (creates compiler)
        with patch('src.app.core.tools.base.language_compilers.LanguageCompilerFactory.create_compiler') as mock_create:
            mock_cpp_compiler = Mock()
            mock_cpp_compiler.compile.return_value = (True, "Success")
            mock_create.return_value = mock_cpp_compiler
            
            compiler._compile_single_file('test')
            
            # Should have created compiler
            assert Language.CPP in compiler.language_compilers
            assert mock_create.call_count == 1
            
            # Compile again - should use cached compiler
            compiler._compile_single_file('test')
            assert mock_create.call_count == 1  # Not called again


class TestBaseCompilerErrorHandling:
    """Test compilation error handling."""
    
    def test_compile_single_file_exception_returns_error(self, temp_workspace):
        """Should handle exceptions during compilation."""
        cpp_file = temp_workspace / 'comparator' / 'test.cpp'
        cpp_file.parent.mkdir(parents=True, exist_ok=True)
        cpp_file.write_text('int main() { return 0; }')
        
        files = {'test': str(cpp_file)}
        compiler = BaseCompiler(str(temp_workspace), files, test_type='comparator')
        
        # Mock compiler to raise exception
        with patch.object(compiler, 'language_compilers', {Language.CPP: Mock()}):
            compiler.language_compilers[Language.CPP].compile.side_effect = Exception("Compiler crashed")
            
            success, message = compiler._compile_single_file('test')
            assert success is False
            assert 'Compiler crashed' in message or 'Compilation' in message
    
    def test_parallel_compile_handles_future_exception(self, temp_workspace):
        """Should handle exceptions from parallel compilation futures."""
        cpp_file = temp_workspace / 'comparator' / 'test.cpp'
        cpp_file.parent.mkdir(parents=True, exist_ok=True)
        cpp_file.write_text('int main() { return 0; }')
        
        files = {'test': str(cpp_file)}
        compiler = BaseCompiler(str(temp_workspace), files, test_type='comparator')
        
        messages = []
        compiler.compilationOutput.connect(lambda msg, fmt: messages.append((msg, fmt)))
        
        # Mock _compile_single_file to raise exception
        with patch.object(compiler, '_compile_single_file', side_effect=RuntimeError("Thread error")):
            compiler._parallel_compile_all()
        
        # Should emit error message
        error_messages = [msg for msg, fmt in messages if fmt == 'error']
        assert any('Compilation error' in msg for msg in error_messages)
    
    def test_all_files_up_to_date_emits_success(self, temp_workspace, qtbot):
        """Should emit success message when all files up-to-date."""
        cpp_file = temp_workspace / 'comparator' / 'test.cpp'
        cpp_file.parent.mkdir(parents=True, exist_ok=True)
        cpp_file.write_text('int main() { return 0; }')
        
        # Create up-to-date executable
        exe_file = cpp_file.with_suffix('.exe' if os.name == 'nt' else '')
        exe_file.write_text('binary')
        time.sleep(0.1)
        exe_file.touch()
        
        files = {'test': str(cpp_file)}
        compiler = BaseCompiler(str(temp_workspace), files, test_type='comparator')
        
        messages = []
        compiler.compilationOutput.connect(lambda msg, fmt: messages.append(msg))
        
        with qtbot.waitSignal(compiler.compilationFinished, timeout=2000):
            compiler.compile_all()
        
        # Should emit "All files are up-to-date" message
        full_msg = ''.join(messages).lower()
        assert 'up-to-date' in full_msg or 'no compilation' in full_msg


class TestBaseCompilerLanguageConfigRetrieval:
    """Test language configuration retrieval."""
    
    def test_get_language_config_returns_defaults(self, temp_workspace):
        """Should return empty dict for languages without config."""
        cpp_file = temp_workspace / 'comparator' / 'test.cpp'
        cpp_file.parent.mkdir(parents=True, exist_ok=True)
        cpp_file.write_text('int main() { return 0; }')
        
        files = {'test': str(cpp_file)}
        compiler = BaseCompiler(str(temp_workspace), files, test_type='comparator')
        
        # Get config for a language
        config = compiler._get_language_config(Language.CPP)
        assert isinstance(config, dict)
    
    def test_get_language_config_uses_custom_config(self, temp_workspace):
        """Should use custom config when provided."""
        cpp_file = temp_workspace / 'comparator' / 'test.cpp'
        cpp_file.parent.mkdir(parents=True, exist_ok=True)
        cpp_file.write_text('int main() { return 0; }')
        
        custom_config = {
            'languages': {
                'cpp': {'compiler': 'clang++', 'flags': ['-std=c++20']}
            }
        }
        files = {'test': str(cpp_file)}
        compiler = BaseCompiler(
            str(temp_workspace), 
            files, 
            test_type='comparator',
            config=custom_config
        )
        
        config = compiler._get_language_config(Language.CPP)
        assert 'compiler' in config
        assert config['compiler'] == 'clang++'
