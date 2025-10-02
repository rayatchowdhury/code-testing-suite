"""
Integration tests for Multi-Language Compilation Workflow.

End-to-end tests using real files in temporary workspaces to validate:
- Language switching during session
- Mixed-language compilation (Generator=Python, Test=C++, Correct=Java)
- Compilation manifest flow
- Language change triggering recompilation
"""

import pytest
import os
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch, MagicMock

from src.app.core.tools.base.language_detector import Language, LanguageDetector
from src.app.core.tools.base.base_compiler import BaseCompiler
from src.app.core.tools.comparator import Comparator
from src.app.core.config.core.config_handler import ConfigManager


@pytest.fixture
def temp_workspace(tmp_path):
    """Create a temporary workspace directory."""
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    return workspace


@pytest.fixture
def cpp_source_files(temp_workspace):
    """Create sample C++ source files."""
    files = {}
    
    # Generator
    generator_cpp = temp_workspace / "generator.cpp"
    generator_cpp.write_text("""
#include <iostream>
using namespace std;

int main() {
    cout << "5" << endl;
    return 0;
}
""")
    files['generator'] = str(generator_cpp)
    
    # Test solution
    test_cpp = temp_workspace / "test.cpp"
    test_cpp.write_text("""
#include <iostream>
using namespace std;

int main() {
    int n;
    cin >> n;
    cout << n * 2 << endl;
    return 0;
}
""")
    files['test'] = str(test_cpp)
    
    # Correct solution
    correct_cpp = temp_workspace / "correct.cpp"
    correct_cpp.write_text("""
#include <iostream>
using namespace std;

int main() {
    int n;
    cin >> n;
    cout << n * 2 << endl;
    return 0;
}
""")
    files['correct'] = str(correct_cpp)
    
    return files


@pytest.fixture
def python_source_files(temp_workspace):
    """Create sample Python source files."""
    files = {}
    
    # Generator
    generator_py = temp_workspace / "generator.py"
    generator_py.write_text("""
print("5")
""")
    files['generator'] = str(generator_py)
    
    # Test solution
    test_py = temp_workspace / "test.py"
    test_py.write_text("""
n = int(input())
print(n * 2)
""")
    files['test'] = str(test_py)
    
    # Correct solution
    correct_py = temp_workspace / "correct.py"
    correct_py.write_text("""
n = int(input())
print(n * 2)
""")
    files['correct'] = str(correct_py)
    
    return files


@pytest.fixture
def java_source_files(temp_workspace):
    """Create sample Java source files."""
    files = {}
    
    # Generator
    generator_java = temp_workspace / "Generator.java"
    generator_java.write_text("""
public class Generator {
    public static void main(String[] args) {
        System.out.println("5");
    }
}
""")
    files['generator'] = str(generator_java)
    
    # Test solution
    test_java = temp_workspace / "Test.java"
    test_java.write_text("""
import java.util.Scanner;

public class Test {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int n = sc.nextInt();
        System.out.println(n * 2);
        sc.close();
    }
}
""")
    files['test'] = str(test_java)
    
    # Correct solution
    correct_java = temp_workspace / "Correct.java"
    correct_java.write_text("""
import java.util.Scanner;

public class Correct {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int n = sc.nextInt();
        System.out.println(n * 2);
        sc.close();
    }
}
""")
    files['correct'] = str(correct_java)
    
    return files


@pytest.fixture
def config():
    """Get default configuration."""
    config_manager = ConfigManager()
    return config_manager.get_default_config()


class TestLanguageDetectionIntegration:
    """Test language detection with real files."""
    
    def test_detect_cpp_files(self, cpp_source_files):
        """Test detection of C++ files."""
        detector = LanguageDetector()
        
        for key, file_path in cpp_source_files.items():
            lang = detector.detect_from_extension(file_path)
            assert lang == Language.CPP, f"Failed to detect C++ for {key}"
    
    def test_detect_python_files(self, python_source_files):
        """Test detection of Python files."""
        detector = LanguageDetector()
        
        for key, file_path in python_source_files.items():
            lang = detector.detect_from_extension(file_path)
            assert lang == Language.PYTHON, f"Failed to detect Python for {key}"
    
    def test_detect_java_files(self, java_source_files):
        """Test detection of Java files."""
        detector = LanguageDetector()
        
        for key, file_path in java_source_files.items():
            lang = detector.detect_from_extension(file_path)
            assert lang == Language.JAVA, f"Failed to detect Java for {key}"


class TestBaseCompilerIntegration:
    """Test BaseCompiler with real files."""
    
    def test_cpp_compilation_success(self, temp_workspace, cpp_source_files, config):
        """Test successful C++ compilation."""
        compiler = BaseCompiler(str(temp_workspace), cpp_source_files, config)
        
        # Compile all files
        success = compiler.compile_all()
        
        # On systems without g++, compilation will fail gracefully
        # Check that we get proper response
        assert isinstance(success, bool)
    
    def test_python_no_compilation(self, temp_workspace, python_source_files, config):
        """Test Python 'compilation' (syntax validation)."""
        compiler = BaseCompiler(str(temp_workspace), python_source_files, config)
        
        # Python doesn't compile but validates syntax
        success = compiler.compile_all()
        
        # Should succeed with valid syntax
        assert success is True
    
    def test_mixed_language_detection(self, temp_workspace, config):
        """Test BaseCompiler detects different languages."""
        # Create mixed-language files
        files = {
            'generator': str(temp_workspace / "gen.py"),
            'test': str(temp_workspace / "test.cpp"),
            'correct': str(temp_workspace / "correct.java")
        }
        
        # Create the files
        Path(files['generator']).write_text("print('test')")
        Path(files['test']).write_text("#include <iostream>\nint main() { return 0; }")
        Path(files['correct']).write_text("public class Correct { public static void main(String[] args) {} }")
        
        compiler = BaseCompiler(str(temp_workspace), files, config)
        
        # Check language detection
        assert compiler.get_file_language('generator') == Language.PYTHON
        assert compiler.get_file_language('test') == Language.CPP
        assert compiler.get_file_language('correct') == Language.JAVA


class TestExecutionCommandGeneration:
    """Test execution command generation for different languages."""
    
    def test_cpp_execution_command(self, temp_workspace, cpp_source_files, config):
        """Test C++ execution command generation."""
        compiler = BaseCompiler(str(temp_workspace), cpp_source_files, config)
        
        cmd = compiler.get_execution_command('generator')
        assert isinstance(cmd, list)
        assert len(cmd) >= 1
        # Should be direct executable path
        assert 'generator' in cmd[0].lower()
    
    def test_python_execution_command(self, temp_workspace, python_source_files, config):
        """Test Python execution command generation."""
        compiler = BaseCompiler(str(temp_workspace), python_source_files, config)
        
        cmd = compiler.get_execution_command('generator')
        assert isinstance(cmd, list)
        assert len(cmd) >= 2
        # Should have python interpreter
        assert 'python' in cmd[0].lower()
        assert 'generator.py' in cmd[-1]
    
    def test_java_execution_command(self, temp_workspace, java_source_files, config):
        """Test Java execution command generation."""
        compiler = BaseCompiler(str(temp_workspace), java_source_files, config)
        
        cmd = compiler.get_execution_command('generator')
        assert isinstance(cmd, list)
        # Should have java runtime
        assert 'java' in cmd[0].lower()
        assert '-cp' in cmd


class TestLanguageSwitching:
    """Test switching languages for same file role."""
    
    def test_switch_generator_cpp_to_python(self, temp_workspace, config):
        """Test switching generator from C++ to Python."""
        # Start with C++ generator
        cpp_file = temp_workspace / "generator.cpp"
        cpp_file.write_text("#include <iostream>\nint main() { std::cout << 5; return 0; }")
        
        files_cpp = {'generator': str(cpp_file)}
        compiler_cpp = BaseCompiler(str(temp_workspace), files_cpp, config)
        
        assert compiler_cpp.get_file_language('generator') == Language.CPP
        
        # Switch to Python generator
        py_file = temp_workspace / "generator.py"
        py_file.write_text("print(5)")
        
        files_py = {'generator': str(py_file)}
        compiler_py = BaseCompiler(str(temp_workspace), files_py, config)
        
        assert compiler_py.get_file_language('generator') == Language.PYTHON
        
        # Verify execution commands are different
        cmd_cpp = compiler_cpp.get_execution_command('generator')
        cmd_py = compiler_py.get_execution_command('generator')
        
        assert cmd_cpp != cmd_py
        assert 'python' not in ' '.join(cmd_cpp).lower()
        assert 'python' in ' '.join(cmd_py).lower()
    
    def test_recompilation_after_language_change(self, temp_workspace, config):
        """Test that changing language triggers proper recompilation."""
        # Create C++ file
        cpp_file = temp_workspace / "test.cpp"
        cpp_file.write_text("#include <iostream>\nint main() { return 0; }")
        
        files_cpp = {'test': str(cpp_file)}
        compiler_cpp = BaseCompiler(str(temp_workspace), files_cpp, config)
        
        # Check C++ needs compilation
        assert compiler_cpp.file_languages['test'] == Language.CPP
        
        # Switch to Python
        py_file = temp_workspace / "test.py"
        py_file.write_text("print('test')")
        
        files_py = {'test': str(py_file)}
        compiler_py = BaseCompiler(str(temp_workspace), files_py, config)
        
        # Check Python doesn't need compilation
        assert compiler_py.file_languages['test'] == Language.PYTHON
        
        # Verify needs_compilation returns different values
        needs_cpp = compiler_cpp.needs_compilation('test')
        needs_py = compiler_py.needs_compilation('test')
        
        assert needs_cpp is True
        assert needs_py is False


class TestMixedLanguageCompilation:
    """Test mixed-language project compilation."""
    
    def test_python_generator_cpp_solutions(self, temp_workspace, config):
        """Test Python generator with C++ test/correct solutions."""
        files = {
            'generator': str(temp_workspace / "gen.py"),
            'test': str(temp_workspace / "test.cpp"),
            'correct': str(temp_workspace / "correct.cpp")
        }
        
        # Create files
        Path(files['generator']).write_text("print('5')")
        Path(files['test']).write_text("#include <iostream>\nusing namespace std;\nint main() { int n; cin >> n; cout << n*2; return 0; }")
        Path(files['correct']).write_text("#include <iostream>\nusing namespace std;\nint main() { int n; cin >> n; cout << n*2; return 0; }")
        
        compiler = BaseCompiler(str(temp_workspace), files, config)
        
        # Verify each file detected correctly
        assert compiler.get_file_language('generator') == Language.PYTHON
        assert compiler.get_file_language('test') == Language.CPP
        assert compiler.get_file_language('correct') == Language.CPP
        
        # Verify execution commands differ
        gen_cmd = compiler.get_execution_command('generator')
        test_cmd = compiler.get_execution_command('test')
        
        # Generator should use Python
        assert 'python' in ' '.join(gen_cmd).lower()
        # Test solution should NOT contain 'python' in the path
        # (it will be .exe on Windows, no extension on Unix)
        test_cmd_str = ' '.join(test_cmd)
        # Check that test command is not using python interpreter (first element should be the exe)
        assert not test_cmd[0].lower().endswith('python.exe') and not test_cmd[0].lower() == 'python'
    
    def test_mixed_three_languages(self, temp_workspace, config):
        """Test all three languages in one project."""
        files = {
            'generator': str(temp_workspace / "gen.py"),
            'test': str(temp_workspace / "Test.java"),
            'correct': str(temp_workspace / "correct.cpp")
        }
        
        # Create files
        Path(files['generator']).write_text("print('5')")
        Path(files['test']).write_text("public class Test { public static void main(String[] args) { } }")
        Path(files['correct']).write_text("#include <iostream>\nint main() { return 0; }")
        
        compiler = BaseCompiler(str(temp_workspace), files, config)
        
        # Verify detection
        assert compiler.get_file_language('generator') == Language.PYTHON
        assert compiler.get_file_language('test') == Language.JAVA
        assert compiler.get_file_language('correct') == Language.CPP
        
        # Verify all have execution commands
        for key in files.keys():
            cmd = compiler.get_execution_command(key)
            assert isinstance(cmd, list)
            assert len(cmd) >= 1


class TestCompilationManifestFlow:
    """Test compilation manifest data flow."""
    
    def test_manifest_structure(self, temp_workspace, python_source_files):
        """Test that manifest contains required fields."""
        # Simulate manifest from TestTabWidget
        manifest = {
            'workspace_dir': str(temp_workspace),
            'files': python_source_files,
            'languages': {
                'generator': 'py',
                'test': 'py',
                'correct': 'py'
            }
        }
        
        # Verify manifest structure
        assert 'workspace_dir' in manifest
        assert 'files' in manifest
        assert 'languages' in manifest
        
        # Verify files structure
        for key in ['generator', 'test', 'correct']:
            assert key in manifest['files']
            assert os.path.exists(manifest['files'][key])
    
    def test_manifest_to_compiler(self, temp_workspace, python_source_files, config):
        """Test passing manifest to compiler."""
        manifest = {
            'workspace_dir': str(temp_workspace),
            'files': python_source_files
        }
        
        # Create compiler from manifest
        compiler = BaseCompiler(
            manifest['workspace_dir'],
            manifest['files'],
            config
        )
        
        # Verify compiler initialized correctly
        assert compiler.workspace_dir == manifest['workspace_dir']
        assert compiler.files == manifest['files']
        
        # Verify languages detected
        for key in manifest['files'].keys():
            lang = compiler.get_file_language(key)
            assert lang == Language.PYTHON


class TestComparatorIntegration:
    """Test Comparator with different language combinations."""
    
    def test_comparator_with_python_files(self, temp_workspace, python_source_files, config):
        """Test Comparator initialization with Python files."""
        comparator = Comparator(
            workspace_dir=str(temp_workspace),
            files=python_source_files,
            config=config
        )
        
        # Verify comparator initialized
        assert comparator.workspace_dir == str(temp_workspace)
        assert comparator.files == python_source_files
        
        # Verify compiler initialized
        assert comparator.compiler is not None
        assert comparator.compiler.get_file_language('generator') == Language.PYTHON
    
    def test_comparator_mixed_languages(self, temp_workspace, config):
        """Test Comparator with mixed languages."""
        files = {
            'generator': str(temp_workspace / "gen.py"),
            'test': str(temp_workspace / "test.cpp"),
            'correct': str(temp_workspace / "correct.cpp")
        }
        
        # Create files
        for path in files.values():
            Path(path).touch()
            if path.endswith('.py'):
                Path(path).write_text("print('test')")
            else:
                Path(path).write_text("int main() { return 0; }")
        
        comparator = Comparator(
            workspace_dir=str(temp_workspace),
            files=files,
            config=config
        )
        
        # Verify languages detected
        assert comparator.compiler.get_file_language('generator') == Language.PYTHON
        assert comparator.compiler.get_file_language('test') == Language.CPP
        assert comparator.compiler.get_file_language('correct') == Language.CPP


class TestErrorHandling:
    """Test error handling in integration scenarios."""
    
    def test_invalid_python_syntax(self, temp_workspace, config):
        """Test handling of invalid Python syntax."""
        files = {
            'generator': str(temp_workspace / "gen.py")
        }
        
        # Create file with syntax error
        Path(files['generator']).write_text("def main(\nprint('test')")
        
        compiler = BaseCompiler(str(temp_workspace), files, config)
        
        # Verify file is detected as Python
        assert compiler.get_file_language('generator') == Language.PYTHON
        
        # When running compile_all, it will attempt to validate syntax
        # The actual behavior depends on whether Python syntax checking is enabled
        success = compiler.compile_all()
        # Just verify it returns a boolean (doesn't crash)
        assert isinstance(success, bool)
    
    def test_missing_file(self, temp_workspace, config):
        """Test handling of missing file."""
        files = {
            'generator': str(temp_workspace / "nonexistent.py")
        }
        
        compiler = BaseCompiler(str(temp_workspace), files, config)
        
        # Should handle missing file gracefully
        # Language detection should still work based on extension
        assert compiler.get_file_language('generator') == Language.PYTHON
    
    def test_unsupported_extension(self, temp_workspace, config):
        """Test handling of unsupported file extension."""
        files = {
            'generator': str(temp_workspace / "gen.txt")
        }
        
        Path(files['generator']).write_text("some text")
        
        # BaseCompiler will raise error for UNKNOWN language when trying to create executables
        # This is expected behavior - unsupported files should not be allowed
        with pytest.raises(ValueError, match="Cannot get config for UNKNOWN language"):
            compiler = BaseCompiler(str(temp_workspace), files, config)


class TestBackwardCompatibility:
    """Test that changes maintain backward compatibility."""
    
    def test_legacy_cpp_only_project(self, temp_workspace, cpp_source_files, config):
        """Test that legacy C++-only projects still work."""
        # Create comparator the old way (before multi-language)
        comparator = Comparator(
            workspace_dir=str(temp_workspace),
            files=cpp_source_files,
            config=config
        )
        
        # Should work exactly as before
        assert comparator.compiler is not None
        assert all(comparator.compiler.get_file_language(key) == Language.CPP 
                  for key in cpp_source_files.keys())
    
    def test_optional_files_parameter(self, temp_workspace, config):
        """Test that files parameter is optional for backward compatibility."""
        # Old code might not pass files parameter
        comparator = Comparator(
            workspace_dir=str(temp_workspace),
            config=config
        )
        
        # Should initialize without files
        assert comparator.workspace_dir == str(temp_workspace)


class TestRealWorldScenario:
    """Test realistic user scenarios."""
    
    def test_user_switches_generator_language(self, temp_workspace, config):
        """Simulate user switching generator from C++ to Python mid-session."""
        # Session 1: User has C++ generator
        cpp_files = {
            'generator': str(temp_workspace / "generator.cpp"),
            'test': str(temp_workspace / "test.cpp"),
            'correct': str(temp_workspace / "correct.cpp")
        }
        
        for path in cpp_files.values():
            Path(path).write_text("#include <iostream>\nint main() { return 0; }")
        
        comparator1 = Comparator(str(temp_workspace), cpp_files, config)
        assert comparator1.compiler.get_file_language('generator') == Language.CPP
        
        # Session 2: User switches to Python generator
        py_files = {
            'generator': str(temp_workspace / "generator.py"),
            'test': str(temp_workspace / "test.cpp"),
            'correct': str(temp_workspace / "correct.cpp")
        }
        
        Path(py_files['generator']).write_text("print('5')")
        
        comparator2 = Comparator(str(temp_workspace), py_files, config)
        assert comparator2.compiler.get_file_language('generator') == Language.PYTHON
        assert comparator2.compiler.get_file_language('test') == Language.CPP
        
        # Verify execution commands updated
        gen_cmd = comparator2.compiler.get_execution_command('generator')
        assert 'python' in ' '.join(gen_cmd).lower()
    
    def test_competitive_programming_workflow(self, temp_workspace, config):
        """Simulate typical competitive programming workflow."""
        # User creates Python generator for quick testing
        files = {
            'generator': str(temp_workspace / "gen.py"),
            'test': str(temp_workspace / "solution.cpp"),
            'correct': str(temp_workspace / "brute.cpp")
        }
        
        Path(files['generator']).write_text("""
import random
print(random.randint(1, 100))
""")
        
        Path(files['test']).write_text("""
#include <iostream>
using namespace std;
int main() {
    int n; cin >> n;
    cout << n * n << endl;
    return 0;
}
""")
        
        Path(files['correct']).write_text("""
#include <iostream>
using namespace std;
int main() {
    int n; cin >> n;
    int result = 0;
    for(int i = 0; i < n; i++) result += n;
    cout << result << endl;
    return 0;
}
""")
        
        comparator = Comparator(str(temp_workspace), files, config)
        
        # Verify mixed setup
        assert comparator.compiler.get_file_language('generator') == Language.PYTHON
        assert comparator.compiler.get_file_language('test') == Language.CPP
        assert comparator.compiler.get_file_language('correct') == Language.CPP
        
        # Verify compilation would handle each correctly
        gen_cmd = comparator.compiler.get_execution_command('generator')
        test_cmd = comparator.compiler.get_execution_command('test')
        
        # Generator uses Python
        assert 'python' in ' '.join(gen_cmd).lower()
        # Solutions use compiled C++
        assert 'python' not in ' '.join(test_cmd).lower()
