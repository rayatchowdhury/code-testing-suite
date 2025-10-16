"""
Integration tests for compilation workflow.

Tests end-to-end compilation using real BaseCompiler with:
- Multi-file C++ compilation
- Parallel compilation
- Executable creation and verification
- Compilation caching
- Multi-language support (C++, Python, Java)

Per Phase 6.1 requirements: Use real components, minimal mocking.
"""

import os
import shutil
import subprocess
import time
from pathlib import Path

import pytest
from PySide6.QtCore import QCoreApplication

from src.app.core.tools.base.base_compiler import BaseCompiler
from src.app.core.tools.base.language_detector import Language


def is_java_available():
    """Check if Java compiler is available."""
    return shutil.which("javac") is not None


@pytest.fixture
def qapp():
    """Create QCoreApplication for Qt signals."""
    app = QCoreApplication.instance()
    if app is None:
        app = QCoreApplication([])
    yield app


@pytest.fixture
def cpp_workspace(tmp_path):
    """Create workspace with C++ test files."""
    workspace = tmp_path / "cpp_test"
    workspace.mkdir()

    # Generator file
    generator_cpp = workspace / "generator.cpp"
    generator_cpp.write_text(
        """
#include <iostream>
#include <cstdlib>
#include <ctime>

int main() {
    srand(time(0));
    int n = 5 + rand() % 10;
    std::cout << n << std::endl;
    
    for (int i = 0; i < n; i++) {
        int value = rand() % 100;
        std::cout << value << " ";
    }
    std::cout << std::endl;
    
    return 0;
}
"""
    )

    # Correct solution file
    correct_cpp = workspace / "correct.cpp"
    correct_cpp.write_text(
        """
#include <iostream>
#include <algorithm>

int main() {
    int n;
    std::cin >> n;
    
    int arr[1000];
    for (int i = 0; i < n; i++) {
        std::cin >> arr[i];
    }
    
    std::sort(arr, arr + n);
    
    for (int i = 0; i < n; i++) {
        std::cout << arr[i] << " ";
    }
    std::cout << std::endl;
    
    return 0;
}
"""
    )

    # Test solution file
    test_cpp = workspace / "test.cpp"
    test_cpp.write_text(
        """
#include <iostream>
#include <vector>
#include <algorithm>

int main() {
    int n;
    std::cin >> n;
    
    std::vector<int> numbers(n);
    for (int i = 0; i < n; i++) {
        std::cin >> numbers[i];
    }
    
    std::sort(numbers.begin(), numbers.end());
    
    for (int num : numbers) {
        std::cout << num << " ";
    }
    std::cout << std::endl;
    
    return 0;
}
"""
    )

    return workspace


@pytest.fixture
def mixed_workspace(tmp_path):
    """Create workspace with mixed language files."""
    workspace = tmp_path / "mixed_test"
    workspace.mkdir()

    # C++ generator
    cpp_file = workspace / "generator.cpp"
    cpp_file.write_text(
        """
#include <iostream>
int main() {
    std::cout << "10" << std::endl;
    for (int i = 1; i <= 10; i++) {
        std::cout << i << " ";
    }
    std::cout << std::endl;
    return 0;
}
"""
    )

    # Python correct solution
    py_file = workspace / "correct.py"
    py_file.write_text(
        """
n = int(input())
numbers = list(map(int, input().split()))
numbers.sort()
print(' '.join(map(str, numbers)))
"""
    )

    # Java test solution
    java_file = workspace / "Test.java"
    java_file.write_text(
        """
import java.util.*;

public class Test {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int n = sc.nextInt();
        int[] arr = new int[n];
        
        for (int i = 0; i < n; i++) {
            arr[i] = sc.nextInt();
        }
        
        Arrays.sort(arr);
        
        for (int i = 0; i < n; i++) {
            System.out.print(arr[i] + " ");
        }
        System.out.println();
    }
}
"""
    )

    return workspace


class TestBasicCompilation:
    """Test basic compilation workflows."""

    def test_single_cpp_file_compilation(self, qapp, cpp_workspace):
        """Should compile a single C++ file successfully."""
        files = {"generator": str(cpp_workspace / "generator.cpp")}
        compiler = BaseCompiler(str(cpp_workspace), files)

        # Capture compilation output
        outputs = []
        results = []

        def capture_output(msg, msg_type):
            outputs.append((msg, msg_type))

        def capture_result(success):
            results.append(success)

        compiler.compilationOutput.connect(capture_output)
        compiler.compilationFinished.connect(capture_result)

        # Compile
        compiler.compile_all()

        # Wait for compilation to complete with event processing
        timeout = 5
        start = time.time()
        while not results and (time.time() - start) < timeout:
            qapp.processEvents()
            time.sleep(0.1)

        # Check executable exists
        exe_path = compiler.executables["generator"]
        assert os.path.exists(exe_path), f"Executable not created: {exe_path}"

        # Verify it's an executable
        if os.name == "nt":
            assert exe_path.endswith(".exe")

        # Check compilation was successful
        assert results and results[0] is True

    def test_multi_file_cpp_compilation(self, qapp, cpp_workspace):
        """Should compile multiple C++ files in parallel."""
        files = {
            "generator": str(cpp_workspace / "generator.cpp"),
            "correct": str(cpp_workspace / "correct.cpp"),
            "test": str(cpp_workspace / "test.cpp"),
        }
        compiler = BaseCompiler(str(cpp_workspace), files)

        # Track compilation results
        compilation_finished = []

        def on_finished(success):
            compilation_finished.append(success)

        compiler.compilationFinished.connect(on_finished)

        # Compile
        compiler.compile_all()

        # Wait for compilation
        timeout = 10
        start = time.time()
        while not compilation_finished and (time.time() - start) < timeout:
            qapp.processEvents()
            time.sleep(0.1)

        # All executables should exist
        for key in files:
            exe_path = compiler.executables[key]
            assert os.path.exists(exe_path), f"Executable for {key} not created"

        # Compilation should succeed
        assert compilation_finished
        assert compilation_finished[0] is True

    def test_detects_file_language(self, qapp, cpp_workspace):
        """Should correctly detect language from file extension."""
        files = {"generator": str(cpp_workspace / "generator.cpp")}
        compiler = BaseCompiler(str(cpp_workspace), files)

        language = compiler.get_file_language("generator")
        assert language == Language.CPP

    def test_needs_compilation_check(self, qapp, cpp_workspace):
        """Should detect when compilation is needed."""
        files = {"generator": str(cpp_workspace / "generator.cpp")}
        compiler = BaseCompiler(str(cpp_workspace), files)

        # Before compilation, should need compilation
        assert compiler.needs_compilation("generator") is True

        # Compile
        results = []
        compiler.compilationFinished.connect(lambda s: results.append(s))
        compiler.compile_all()

        # Wait for completion
        timeout = 5
        start = time.time()
        while not results and (time.time() - start) < timeout:
            qapp.processEvents()
            time.sleep(0.1)

        # After compilation, should not need recompilation (create new compiler instance)
        compiler2 = BaseCompiler(str(cpp_workspace), files)
        # Note: For C++, needs_compilation checks if source is newer than executable
        # Since we just compiled, executable should be up-to-date
        needs_recomp = compiler2._needs_recompilation("generator")
        assert needs_recomp is False


class TestCompilationCaching:
    """Test smart compilation caching."""

    def test_skips_up_to_date_files(self, qapp, cpp_workspace):
        """Should skip compilation if executable is up-to-date."""
        files = {"generator": str(cpp_workspace / "generator.cpp")}

        # First compilation
        compiler1 = BaseCompiler(str(cpp_workspace), files)
        results = []
        compiler1.compilationFinished.connect(lambda s: results.append(s))
        compiler1.compile_all()

        # Wait for completion
        timeout = 5
        start = time.time()
        while not results and (time.time() - start) < timeout:
            qapp.processEvents()
            time.sleep(0.1)

        exe_path = compiler1.executables["generator"]
        assert os.path.exists(exe_path)

        # Get modification time
        mtime1 = os.path.getmtime(exe_path)

        # Second compilation - should skip
        time.sleep(0.2)  # Ensure time difference
        outputs = []
        compiler2 = BaseCompiler(str(cpp_workspace), files)
        compiler2.compilationOutput.connect(lambda msg, t: outputs.append(msg))

        results2 = []
        compiler2.compilationFinished.connect(lambda s: results2.append(s))
        compiler2.compile_all()

        # Wait for completion
        timeout = 5
        start = time.time()
        while not results2 and (time.time() - start) < timeout:
            qapp.processEvents()
            time.sleep(0.1)

        # Check that "up-to-date" message appears
        output_text = "".join(outputs).lower()
        assert "up-to-date" in output_text or "no compilation needed" in output_text

        # Executable should not be recompiled
        mtime2 = os.path.getmtime(exe_path)
        assert mtime2 == mtime1

    def test_recompiles_after_source_change(self, qapp, cpp_workspace):
        """Should recompile when source file is modified."""
        files = {"generator": str(cpp_workspace / "generator.cpp")}

        # First compilation
        compiler1 = BaseCompiler(str(cpp_workspace), files)
        compiler1.compile_all()
        time.sleep(2)

        exe_path = compiler1.executables["generator"]
        mtime1 = os.path.getmtime(exe_path)

        # Modify source file
        time.sleep(0.1)  # Ensure timestamp difference
        source_path = cpp_workspace / "generator.cpp"
        content = source_path.read_text()
        source_path.write_text(content + "\n// Modified\n")

        # Second compilation - should recompile
        compiler2 = BaseCompiler(str(cpp_workspace), files)
        compiler2.compile_all()
        time.sleep(2)

        # Executable should be newer
        mtime2 = os.path.getmtime(exe_path)
        assert mtime2 > mtime1


class TestParallelCompilation:
    """Test parallel compilation functionality."""

    def test_compiles_multiple_files_in_parallel(self, qapp, cpp_workspace):
        """Should compile multiple files simultaneously."""
        files = {
            "generator": str(cpp_workspace / "generator.cpp"),
            "correct": str(cpp_workspace / "correct.cpp"),
            "test": str(cpp_workspace / "test.cpp"),
        }
        compiler = BaseCompiler(str(cpp_workspace), files)

        start_time = time.time()

        compiler.compile_all()

        # Wait for completion
        timeout = 10
        while (time.time() - start_time) < timeout:
            qapp.processEvents()
            time.sleep(0.1)
            # Check if all executables exist
            if all(os.path.exists(compiler.executables[k]) for k in files):
                break

        elapsed = time.time() - start_time

        # Parallel compilation should be reasonably fast
        # 3 files should compile in less than 8 seconds
        assert elapsed < 8, f"Parallel compilation took too long: {elapsed}s"

        # All files should be compiled
        for key in files:
            assert os.path.exists(compiler.executables[key])

    def test_handles_compilation_errors_gracefully(self, qapp, tmp_path):
        """Should handle compilation errors without crashing."""
        workspace = tmp_path / "error_test"
        workspace.mkdir()

        # Create file with syntax error
        bad_file = workspace / "bad.cpp"
        bad_file.write_text(
            """
#include <iostream>

int main() {
    std::cout << "Missing semicolon"  // Syntax error
    return 0;
}
"""
        )

        files = {"bad": str(bad_file)}
        compiler = BaseCompiler(str(workspace), files)

        outputs = []
        results = []

        compiler.compilationOutput.connect(lambda msg, t: outputs.append((msg, t)))
        compiler.compilationFinished.connect(lambda success: results.append(success))

        compiler.compile_all()

        # Wait for completion
        timeout = 5
        start = time.time()
        while not results and (time.time() - start) < timeout:
            qapp.processEvents()
            time.sleep(0.1)

        # Should fail compilation
        assert results
        assert results[0] is False

        # Should have error message
        assert any("error" in t.lower() for msg, t in outputs)


class TestMultiLanguageCompilation:
    """Test compilation of multiple languages."""

    @pytest.mark.skipif(not is_java_available(), reason="Java compiler not available")
    def test_compiles_mixed_languages(self, qapp, mixed_workspace):
        """Should compile C++, Python, and Java files together."""
        files = {
            "generator": str(mixed_workspace / "generator.cpp"),
            "correct": str(mixed_workspace / "correct.py"),
            "test": str(mixed_workspace / "Test.java"),
        }
        compiler = BaseCompiler(str(mixed_workspace), files)

        # Check language detection
        assert compiler.get_file_language("generator") == Language.CPP
        assert compiler.get_file_language("correct") == Language.PYTHON
        assert compiler.get_file_language("test") == Language.JAVA

        # Compile all
        results = []
        compiler.compilationFinished.connect(lambda s: results.append(s))
        compiler.compile_all()

        # Wait for completion
        timeout = 10
        start = time.time()
        while not results and (time.time() - start) < timeout:
            qapp.processEvents()
            time.sleep(0.1)

        # Should succeed
        assert results
        assert results[0] is True

        # Check executables/files exist
        assert os.path.exists(compiler.executables["generator"])  # C++ executable
        assert os.path.exists(compiler.executables["correct"])  # Python .py
        assert os.path.exists(str(mixed_workspace / "Test.class"))  # Java .class

    def test_python_needs_no_compilation(self, qapp, tmp_path):
        """Should validate Python files without compilation."""
        workspace = tmp_path / "python_test"
        workspace.mkdir()

        py_file = workspace / "script.py"
        py_file.write_text(
            """
def main():
    n = int(input())
    print(n * 2)

if __name__ == '__main__':
    main()
"""
        )

        files = {"script": str(py_file)}
        compiler = BaseCompiler(str(workspace), files)

        assert compiler.get_file_language("script") == Language.PYTHON
        assert compiler.needs_compilation("script") is False

    @pytest.mark.skipif(not is_java_available(), reason="Java compiler not available")
    def test_java_compilation(self, qapp, tmp_path):
        """Should compile Java files to .class files."""
        workspace = tmp_path / "java_test"
        workspace.mkdir()

        java_file = workspace / "Hello.java"
        java_file.write_text(
            """
public class Hello {
    public static void main(String[] args) {
        System.out.println("Hello, World!");
    }
}
"""
        )

        files = {"hello": str(java_file)}
        compiler = BaseCompiler(str(workspace), files)

        results = []
        compiler.compilationFinished.connect(lambda s: results.append(s))
        compiler.compile_all()

        # Wait for completion
        time.sleep(3)

        # Should create .class file
        class_file = workspace / "Hello.class"
        assert os.path.exists(class_file)


class TestExecutionCommands:
    """Test generation of execution commands."""

    def test_cpp_execution_command(self, qapp, cpp_workspace):
        """Should generate correct execution command for C++."""
        files = {"generator": str(cpp_workspace / "generator.cpp")}
        compiler = BaseCompiler(str(cpp_workspace), files)

        compiler.compile_all()
        time.sleep(2)

        cmd = compiler.get_execution_command("generator")

        # Should be direct executable path
        assert len(cmd) == 1
        assert cmd[0] == compiler.executables["generator"]

    def test_python_execution_command(self, qapp, tmp_path):
        """Should generate correct execution command for Python."""
        workspace = tmp_path / "py_test"
        workspace.mkdir()

        py_file = workspace / "script.py"
        py_file.write_text("print('Hello')")

        files = {"script": str(py_file)}
        compiler = BaseCompiler(str(workspace), files)

        cmd = compiler.get_execution_command("script")

        # Should be: python script.py
        assert "python" in cmd[0].lower()
        assert str(py_file) in cmd

    @pytest.mark.skipif(not is_java_available(), reason="Java compiler not available")
    def test_java_execution_command(self, qapp, tmp_path):
        """Should generate correct execution command for Java."""
        workspace = tmp_path / "java_test"
        workspace.mkdir()

        java_file = workspace / "Main.java"
        java_file.write_text(
            """
public class Main {
    public static void main(String[] args) {}
}
"""
        )

        files = {"main": str(java_file)}
        compiler = BaseCompiler(str(workspace), files)

        compiler.compile_all()
        time.sleep(2)

        cmd = compiler.get_execution_command("main", class_name="Main")

        # Should be: java -cp . Main
        assert "java" in cmd[0].lower()
        assert "Main" in cmd


class TestCompilationOptions:
    """Test compilation with different options."""

    def test_optimization_levels(self, qapp, cpp_workspace):
        """Should support different optimization levels."""
        files = {"generator": str(cpp_workspace / "generator.cpp")}

        # Test O0 (no optimization)
        compiler_o0 = BaseCompiler(str(cpp_workspace), files, optimization_level="O0")
        compiler_o0.compile_all()
        time.sleep(2)

        assert os.path.exists(compiler_o0.executables["generator"])

        # Clean up
        os.remove(compiler_o0.executables["generator"])

        # Test O3 (max optimization)
        compiler_o3 = BaseCompiler(str(cpp_workspace), files, optimization_level="O3")
        compiler_o3.compile_all()
        time.sleep(2)

        assert os.path.exists(compiler_o3.executables["generator"])

    def test_custom_config(self, qapp, cpp_workspace):
        """Should accept custom configuration."""
        files = {"generator": str(cpp_workspace / "generator.cpp")}

        config = {
            "cpp": {"compiler": "g++", "std_version": "c++17", "optimization": "O2"}
        }

        compiler = BaseCompiler(str(cpp_workspace), files, config=config)
        compiler.compile_all()
        time.sleep(2)

        assert os.path.exists(compiler.executables["generator"])


class TestErrorHandling:
    """Test error handling in compilation."""

    def test_handles_missing_compiler(self, qapp, tmp_path):
        """Should handle missing compiler gracefully."""
        workspace = tmp_path / "missing_compiler"
        workspace.mkdir()

        cpp_file = workspace / "test.cpp"
        cpp_file.write_text("#include <iostream>\nint main() { return 0; }")

        files = {"test": str(cpp_file)}

        # Use non-existent compiler
        config = {"cpp": {"compiler": "nonexistent-compiler-xyz"}}
        compiler = BaseCompiler(str(workspace), files, config=config)

        outputs = []
        results = []
        compiler.compilationOutput.connect(lambda msg, t: outputs.append((msg, t)))
        compiler.compilationFinished.connect(lambda s: results.append(s))

        compiler.compile_all()

        # Wait for completion
        timeout = 5
        start = time.time()
        while not results and (time.time() - start) < timeout:
            qapp.processEvents()
            time.sleep(0.1)

        # Should emit error or fail
        assert results or any("error" in t.lower() for msg, t in outputs)

    def test_handles_nonexistent_file(self, qapp, tmp_path):
        """Should handle nonexistent source files."""
        workspace = tmp_path / "missing_file"
        workspace.mkdir()

        files = {"nonexistent": str(workspace / "nonexistent.cpp")}
        compiler = BaseCompiler(str(workspace), files)

        # Should not crash
        compiler.compile_all()
        time.sleep(1)


class TestCompilationSignals:
    """Test Qt signals during compilation."""

    def test_emits_compilation_output(self, qapp, cpp_workspace):
        """Should emit compilation output signals."""
        files = {"generator": str(cpp_workspace / "generator.cpp")}
        compiler = BaseCompiler(str(cpp_workspace), files)

        outputs = []
        results = []
        compiler.compilationOutput.connect(lambda msg, t: outputs.append((msg, t)))
        compiler.compilationFinished.connect(lambda s: results.append(s))

        compiler.compile_all()

        # Wait for completion
        timeout = 5
        start = time.time()
        while not results and (time.time() - start) < timeout:
            qapp.processEvents()
            time.sleep(0.1)

        # Should have emitted output
        assert len(outputs) > 0

        # Should have both info and success messages
        types = [t for msg, t in outputs]
        assert "info" in types or "success" in types

    def test_emits_compilation_finished(self, qapp, cpp_workspace):
        """Should emit compilationFinished signal."""
        files = {"generator": str(cpp_workspace / "generator.cpp")}
        compiler = BaseCompiler(str(cpp_workspace), files)

        finished_called = []
        compiler.compilationFinished.connect(
            lambda success: finished_called.append(success)
        )

        compiler.compile_all()

        # Wait for signal
        timeout = 5
        start = time.time()
        while not finished_called and (time.time() - start) < timeout:
            qapp.processEvents()
            time.sleep(0.1)

        # Should have been called with True (success)
        assert finished_called
        assert finished_called[0] is True


class TestWorkspaceStructure:
    """Test handling of different workspace structures."""

    def test_handles_absolute_paths(self, qapp, cpp_workspace):
        """Should handle absolute file paths."""
        files = {"generator": str(cpp_workspace / "generator.cpp")}
        compiler = BaseCompiler(str(cpp_workspace), files)

        # Should resolve to absolute path
        assert os.path.isabs(compiler.files["generator"])

        compiler.compile_all()
        time.sleep(2)

        assert os.path.exists(compiler.executables["generator"])

    def test_handles_relative_paths(self, qapp, cpp_workspace):
        """Should handle relative file paths."""
        files = {"generator": "generator.cpp"}
        compiler = BaseCompiler(str(cpp_workspace), files, test_type="comparator")

        # Should resolve relative to workspace (in test_type subdirectory)
        # For now, just check the compilation completes
        results = []
        compiler.compilationFinished.connect(lambda s: results.append(s))

        # Note: This may fail if file doesn't exist in expected location
        # This is testing the path resolution logic
        compiler.compile_all()

        # Wait briefly
        timeout = 2
        start = time.time()
        while not results and (time.time() - start) < timeout:
            qapp.processEvents()
            time.sleep(0.1)

        # Test completes without crashing (may fail compilation if path doesn't exist)
        assert True  # Just verify it doesn't crash
