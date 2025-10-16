"""
Unit tests for shared/constants/file_constants.py module.

Tests file naming conventions, language detection, and file path generation.

Test Coverage:
- get_source_filename: Generates filenames for different languages
- get_executable_name: Generates executable names by language
- get_source_file_path: Constructs full source file paths
- get_executable_path: Constructs full executable paths
- get_language_from_filename: Detects language from extension
- get_role_from_filename: Detects role from filename
- validate_file_for_test_type: Validates file role for test type
- get_default_language: Returns default language
- get_supported_languages: Returns supported languages list
- get_file_display_name: Generates user-friendly display names
- Constants validation (TEST_TYPE_FILES, LANGUAGE_EXTENSIONS, etc.)
"""

import os

import pytest

from src.app.shared.constants.file_constants import (  # Constants; Functions
    EXECUTABLE_EXTENSIONS,
    JAVA_CLASS_NAMES,
    LANGUAGE_EXTENSIONS,
    TEST_TYPE_FILES,
    get_default_language,
    get_executable_name,
    get_executable_path,
    get_file_display_name,
    get_language_from_filename,
    get_role_from_filename,
    get_source_file_path,
    get_source_filename,
    get_supported_languages,
    validate_file_for_test_type,
)


class TestGetSourceFilename:
    """Tests for get_source_filename function."""

    @pytest.mark.parametrize(
        "role,language,expected",
        [
            ("generator", "cpp", "generator.cpp"),
            ("correct", "cpp", "correct.cpp"),
            ("test", "cpp", "test.cpp"),
            ("validator", "cpp", "validator.cpp"),
            ("generator", "py", "generator.py"),
            ("correct", "py", "correct.py"),
            ("test", "py", "test.py"),
            ("validator", "py", "validator.py"),
            ("generator", "java", "Generator.java"),
            ("correct", "java", "Correct.java"),
            ("test", "java", "Test.java"),
            ("validator", "java", "Validator.java"),
        ],
    )
    def test_generates_correct_filenames(self, role, language, expected):
        """Test filename generation for all role/language combinations."""
        result = get_source_filename(role, language)
        assert result == expected

    def test_handles_uppercase_language(self):
        """Test that uppercase language is normalized."""
        result = get_source_filename("generator", "CPP")
        assert result == "generator.cpp"

    def test_handles_uppercase_role(self):
        """Test that uppercase role is normalized."""
        result = get_source_filename("GENERATOR", "cpp")
        assert result == "generator.cpp"

    def test_java_capitalizes_class_names(self):
        """Test that Java uses capitalized class names."""
        result = get_source_filename("generator", "java")
        assert result.startswith("G")  # Generator
        assert result == "Generator.java"

    def test_cpp_uses_lowercase(self):
        """Test that C++ uses lowercase filenames."""
        result = get_source_filename("generator", "cpp")
        assert result == "generator.cpp"

    def test_python_uses_lowercase(self):
        """Test that Python uses lowercase filenames."""
        result = get_source_filename("generator", "py")
        assert result == "generator.py"

    def test_raises_error_for_unknown_language(self):
        """Test that unknown language raises ValueError."""
        with pytest.raises(ValueError, match="Unknown language"):
            get_source_filename("generator", "rust")

    def test_supports_python_alias(self):
        """Test that 'python' is aliased to 'py'."""
        result = get_source_filename("generator", "python")
        assert result == "generator.py"

    def test_supports_cpp_alias(self):
        """Test that 'c++' is aliased to 'cpp'."""
        result = get_source_filename("generator", "c++")
        assert result == "generator.cpp"


class TestGetExecutableName:
    """Tests for get_executable_name function."""

    @pytest.mark.parametrize(
        "role,language,expected",
        [
            ("generator", "cpp", "generator.exe" if os.name == "nt" else "generator"),
            ("correct", "cpp", "correct.exe" if os.name == "nt" else "correct"),
            ("test", "cpp", "test.exe" if os.name == "nt" else "test"),
            ("validator", "cpp", "validator.exe" if os.name == "nt" else "validator"),
            # Python interpreted - returns source filename
            ("generator", "py", "generator.py"),
            ("correct", "py", "correct.py"),
            ("test", "py", "test.py"),
            ("validator", "py", "validator.py"),
            # Java bytecode
            ("generator", "java", "Generator.class"),
            ("correct", "java", "Correct.class"),
            ("test", "java", "Test.class"),
            ("validator", "java", "Validator.class"),
        ],
    )
    def test_generates_correct_executables(self, role, language, expected):
        """Test executable name generation for all combinations."""
        result = get_executable_name(role, language)
        assert result == expected

    def test_python_returns_source_filename(self):
        """Test that Python returns source filename (interpreted)."""
        result = get_executable_name("generator", "py")
        assert result == "generator.py"

    def test_cpp_adds_exe_extension(self):
        """Test that C++ adds platform-appropriate extension."""
        result = get_executable_name("generator", "cpp")
        expected_ext = ".exe" if os.name == "nt" else ""
        assert result == f"generator{expected_ext}"

    def test_java_uses_class_extension(self):
        """Test that Java uses .class extension."""
        result = get_executable_name("generator", "java")
        assert result.endswith(".class")

    def test_handles_uppercase_language(self):
        """Test uppercase language normalization."""
        result = get_executable_name("generator", "CPP")
        expected_ext = ".exe" if os.name == "nt" else ""
        assert result == f"generator{expected_ext}"

    def test_handles_uppercase_role(self):
        """Test uppercase role normalization."""
        result = get_executable_name("GENERATOR", "cpp")
        expected_ext = ".exe" if os.name == "nt" else ""
        assert result == f"generator{expected_ext}"


class TestGetSourceFilePath:
    """Tests for get_source_file_path function."""

    def test_constructs_cpp_path(self, temp_dir):
        """Test path construction for C++ source file."""
        result = get_source_file_path(temp_dir, "comparator", "generator", "cpp")
        expected = os.path.join(temp_dir, "comparator", "generator.cpp")
        assert result == expected

    def test_constructs_python_path(self, temp_dir):
        """Test path construction for Python source file."""
        result = get_source_file_path(temp_dir, "validator", "test", "py")
        expected = os.path.join(temp_dir, "validator", "test.py")
        assert result == expected

    def test_constructs_java_path(self, temp_dir):
        """Test path construction for Java source file."""
        result = get_source_file_path(temp_dir, "benchmarker", "test", "java")
        expected = os.path.join(temp_dir, "benchmarker", "Test.java")
        assert result == expected

    @pytest.mark.parametrize(
        "alias,expected_subdir",
        [
            ("comparison", "comparator"),
            ("validation", "validator"),
            ("benchmark", "benchmarker"),
        ],
    )
    def test_normalizes_test_type_aliases(self, temp_dir, alias, expected_subdir):
        """Test that test type aliases are normalized."""
        result = get_source_file_path(temp_dir, alias, "generator", "cpp")
        assert expected_subdir in result

    def test_handles_all_roles(self, temp_dir):
        """Test path construction for all file roles."""
        roles = ["generator", "correct", "test", "validator"]
        for role in roles:
            result = get_source_file_path(temp_dir, "comparator", role, "cpp")
            assert f"{role}.cpp" in result


class TestGetExecutablePath:
    """Tests for get_executable_path function."""

    def test_constructs_cpp_executable_path(self, temp_dir):
        """Test path construction for C++ executable."""
        result = get_executable_path(temp_dir, "comparator", "generator", "cpp")
        expected_extension = ".exe" if os.name == "nt" else ""
        expected = os.path.join(
            temp_dir, "comparator", f"generator{expected_extension}"
        )
        assert result == expected

    def test_constructs_python_executable_path(self, temp_dir):
        """Test path construction for Python executable (source file)."""
        result = get_executable_path(temp_dir, "validator", "test", "py")
        expected = os.path.join(temp_dir, "validator", "test.py")
        assert result == expected

    def test_constructs_java_executable_path(self, temp_dir):
        """Test path construction for Java bytecode."""
        result = get_executable_path(temp_dir, "benchmarker", "test", "java")
        expected = os.path.join(temp_dir, "benchmarker", "Test.class")
        assert result == expected

    @pytest.mark.parametrize(
        "alias,expected_subdir",
        [
            ("comparison", "comparator"),
            ("validation", "validator"),
            ("benchmark", "benchmarker"),
        ],
    )
    def test_normalizes_test_type_aliases(self, temp_dir, alias, expected_subdir):
        """Test that test type aliases are normalized."""
        result = get_executable_path(temp_dir, alias, "generator", "cpp")
        assert expected_subdir in result


class TestGetLanguageFromFilename:
    """Tests for get_language_from_filename function."""

    @pytest.mark.parametrize(
        "filename,expected",
        [
            ("generator.cpp", "cpp"),
            ("correct.c++", "cpp"),
            ("test.cc", "cpp"),
            ("validator.cxx", "cpp"),
            ("generator.py", "py"),
            ("test.pyw", "py"),
            ("Generator.java", "java"),
            ("Test.java", "java"),
        ],
    )
    def test_detects_language_from_extension(self, filename, expected):
        """Test language detection from various extensions."""
        result = get_language_from_filename(filename)
        assert result == expected

    def test_handles_path_with_filename(self):
        """Test language detection from full path."""
        result = get_language_from_filename("/path/to/generator.cpp")
        assert result == "cpp"

    def test_handles_uppercase_extensions(self):
        """Test that uppercase extensions are normalized."""
        result = get_language_from_filename("test.CPP")
        assert result == "cpp"

    def test_returns_none_for_unknown_extension(self):
        """Test that unknown extensions return None."""
        result = get_language_from_filename("test.rs")
        assert result is None

    def test_returns_none_for_no_extension(self):
        """Test that files without extension return None."""
        result = get_language_from_filename("generator")
        assert result is None


class TestGetRoleFromFilename:
    """Tests for get_role_from_filename function."""

    @pytest.mark.parametrize(
        "filename,expected",
        [
            ("generator.cpp", "generator"),
            ("gen.py", "generator"),
            ("correct.cpp", "correct"),
            ("solution.py", "correct"),
            ("sol.java", "correct"),
            ("test.cpp", "test"),
            ("brute.py", "test"),
            ("validator.cpp", "validator"),
            ("checker.java", "validator"),
        ],
    )
    def test_detects_role_from_filename(self, filename, expected):
        """Test role detection from various filenames."""
        result = get_role_from_filename(filename)
        assert result == expected

    def test_handles_path_with_filename(self):
        """Test role detection from full path."""
        result = get_role_from_filename("/path/to/generator.cpp")
        assert result == "generator"

    def test_handles_uppercase_filenames(self):
        """Test that uppercase filenames are normalized."""
        result = get_role_from_filename("GENERATOR.cpp")
        assert result == "generator"

    def test_handles_capitalized_java_classes(self):
        """Test detection of capitalized Java class names."""
        result = get_role_from_filename("Generator.java")
        assert result == "generator"

    def test_returns_none_for_unknown_role(self):
        """Test that unknown roles return None."""
        result = get_role_from_filename("main.cpp")
        assert result is None


class TestValidateFileForTestType:
    """Tests for validate_file_for_test_type function."""

    def test_generator_valid_for_all_types(self):
        """Test that generator is valid for all test types."""
        assert validate_file_for_test_type("generator.cpp", "comparator") is True
        assert validate_file_for_test_type("generator.py", "validator") is True
        assert validate_file_for_test_type("generator.java", "benchmarker") is True

    def test_correct_valid_for_comparator_only(self):
        """Test that correct solution is only valid for comparator."""
        assert validate_file_for_test_type("correct.cpp", "comparator") is True
        assert validate_file_for_test_type("correct.py", "validator") is False
        assert validate_file_for_test_type("correct.java", "benchmarker") is False

    def test_test_valid_for_all_types(self):
        """Test that test solution is valid for all test types."""
        assert validate_file_for_test_type("test.cpp", "comparator") is True
        assert validate_file_for_test_type("test.py", "validator") is True
        assert validate_file_for_test_type("test.java", "benchmarker") is True

    def test_validator_valid_for_validator_only(self):
        """Test that validator is only valid for validator test type."""
        assert validate_file_for_test_type("validator.cpp", "validator") is True
        assert validate_file_for_test_type("validator.py", "comparator") is False
        assert validate_file_for_test_type("validator.java", "benchmarker") is False

    def test_normalizes_test_type_aliases(self):
        """Test that test type aliases are normalized."""
        assert validate_file_for_test_type("correct.cpp", "comparison") is True
        assert validate_file_for_test_type("validator.py", "validation") is True

    def test_returns_false_for_unknown_role(self):
        """Test that unknown roles return False."""
        assert validate_file_for_test_type("main.cpp", "comparator") is False

    def test_returns_false_for_invalid_filename(self):
        """Test that invalid filenames return False."""
        assert validate_file_for_test_type("unknown.cpp", "comparator") is False


class TestGetDefaultLanguage:
    """Tests for get_default_language function."""

    def test_returns_cpp(self):
        """Test that default language is C++."""
        result = get_default_language()
        assert result == "cpp"

    def test_returns_string(self):
        """Test that result is a string."""
        result = get_default_language()
        assert isinstance(result, str)


class TestGetSupportedLanguages:
    """Tests for get_supported_languages function."""

    def test_returns_list(self):
        """Test that result is a list."""
        result = get_supported_languages()
        assert isinstance(result, list)

    def test_contains_cpp(self):
        """Test that C++ is supported."""
        result = get_supported_languages()
        assert "cpp" in result

    def test_contains_python(self):
        """Test that Python is supported."""
        result = get_supported_languages()
        assert "py" in result

    def test_contains_java(self):
        """Test that Java is supported."""
        result = get_supported_languages()
        assert "java" in result

    def test_has_three_languages(self):
        """Test that exactly 3 languages are supported."""
        result = get_supported_languages()
        assert len(result) == 3


class TestGetFileDisplayName:
    """Tests for get_file_display_name function."""

    @pytest.mark.parametrize(
        "role,language,expected",
        [
            ("generator", "cpp", "Generator (C++)"),
            ("correct", "cpp", "Correct Solution (C++)"),
            ("test", "cpp", "Test Solution (C++)"),
            ("validator", "cpp", "Validator (C++)"),
            ("generator", "py", "Generator (Python)"),
            ("correct", "py", "Correct Solution (Python)"),
            ("test", "py", "Test Solution (Python)"),
            ("validator", "py", "Validator (Python)"),
            ("generator", "java", "Generator (Java)"),
            ("correct", "java", "Correct Solution (Java)"),
            ("test", "java", "Test Solution (Java)"),
            ("validator", "java", "Validator (Java)"),
        ],
    )
    def test_generates_display_names(self, role, language, expected):
        """Test display name generation for all combinations."""
        result = get_file_display_name(role, language)
        assert result == expected

    def test_capitalizes_role_name(self):
        """Test that role name is capitalized."""
        result = get_file_display_name("generator", "cpp")
        assert result.startswith("Generator")

    def test_formats_cpp_language(self):
        """Test that C++ is formatted correctly."""
        result = get_file_display_name("generator", "cpp")
        assert "C++" in result

    def test_formats_python_language(self):
        """Test that Python is formatted correctly."""
        result = get_file_display_name("generator", "py")
        assert "Python" in result

    def test_formats_java_language(self):
        """Test that Java is formatted correctly."""
        result = get_file_display_name("generator", "java")
        assert "Java" in result


class TestTestTypeFilesConstant:
    """Tests for TEST_TYPE_FILES constant."""

    def test_constant_exists(self):
        """Test that TEST_TYPE_FILES constant exists."""
        assert TEST_TYPE_FILES is not None
        assert isinstance(TEST_TYPE_FILES, dict)

    def test_has_comparator_entry(self):
        """Test that comparator is defined."""
        assert "comparator" in TEST_TYPE_FILES

    def test_has_validator_entry(self):
        """Test that validator is defined."""
        assert "validator" in TEST_TYPE_FILES

    def test_has_benchmarker_entry(self):
        """Test that benchmarker is defined."""
        assert "benchmarker" in TEST_TYPE_FILES

    def test_comparator_files(self):
        """Test comparator required files."""
        files = TEST_TYPE_FILES["comparator"]
        assert "generator" in files
        assert "correct" in files
        assert "test" in files

    def test_validator_files(self):
        """Test validator required files."""
        files = TEST_TYPE_FILES["validator"]
        assert "generator" in files
        assert "test" in files
        assert "validator" in files

    def test_benchmarker_files(self):
        """Test benchmarker required files."""
        files = TEST_TYPE_FILES["benchmarker"]
        assert "generator" in files
        assert "test" in files
        # Should not have correct or validator
        assert "correct" not in files
        assert "validator" not in files


class TestLanguageExtensionsConstant:
    """Tests for LANGUAGE_EXTENSIONS constant."""

    def test_constant_exists(self):
        """Test that LANGUAGE_EXTENSIONS exists."""
        assert LANGUAGE_EXTENSIONS is not None
        assert isinstance(LANGUAGE_EXTENSIONS, dict)

    def test_has_cpp_extension(self):
        """Test C++ extension mapping."""
        assert LANGUAGE_EXTENSIONS.get("cpp") == ".cpp"
        assert LANGUAGE_EXTENSIONS.get("c++") == ".cpp"

    def test_has_python_extension(self):
        """Test Python extension mapping."""
        assert LANGUAGE_EXTENSIONS.get("py") == ".py"
        assert LANGUAGE_EXTENSIONS.get("python") == ".py"

    def test_has_java_extension(self):
        """Test Java extension mapping."""
        assert LANGUAGE_EXTENSIONS.get("java") == ".java"


class TestExecutableExtensionsConstant:
    """Tests for EXECUTABLE_EXTENSIONS constant."""

    def test_constant_exists(self):
        """Test that EXECUTABLE_EXTENSIONS exists."""
        assert EXECUTABLE_EXTENSIONS is not None
        assert isinstance(EXECUTABLE_EXTENSIONS, dict)

    def test_cpp_has_exe_extension(self):
        """Test C++ executable extension."""
        expected_ext = ".exe" if os.name == "nt" else ""
        assert EXECUTABLE_EXTENSIONS.get("cpp") == expected_ext

    def test_python_has_py_extension(self):
        """Test Python executable is source file."""
        assert EXECUTABLE_EXTENSIONS.get("py") == ".py"

    def test_java_has_class_extension(self):
        """Test Java executable is .class file."""
        assert EXECUTABLE_EXTENSIONS.get("java") == ".class"


class TestJavaClassNamesConstant:
    """Tests for JAVA_CLASS_NAMES constant."""

    def test_constant_exists(self):
        """Test that JAVA_CLASS_NAMES exists."""
        assert JAVA_CLASS_NAMES is not None
        assert isinstance(JAVA_CLASS_NAMES, dict)

    def test_has_all_roles(self):
        """Test that all roles are defined."""
        assert "generator" in JAVA_CLASS_NAMES
        assert "correct" in JAVA_CLASS_NAMES
        assert "test" in JAVA_CLASS_NAMES
        assert "validator" in JAVA_CLASS_NAMES

    def test_class_names_are_capitalized(self):
        """Test that all class names are capitalized."""
        for class_name in JAVA_CLASS_NAMES.values():
            assert class_name[0].isupper()

    def test_specific_mappings(self):
        """Test specific class name mappings."""
        assert JAVA_CLASS_NAMES["generator"] == "Generator"
        assert JAVA_CLASS_NAMES["correct"] == "Correct"
        assert JAVA_CLASS_NAMES["test"] == "Test"
        assert JAVA_CLASS_NAMES["validator"] == "Validator"


class TestFileConstantsIntegration:
    """Integration tests for file constants module."""

    def test_source_and_executable_paths_consistent(self, temp_dir):
        """Test that source and executable paths are in same directory."""
        source = get_source_file_path(temp_dir, "comparator", "generator", "cpp")
        executable = get_executable_path(temp_dir, "comparator", "generator", "cpp")

        # Should be in same directory
        assert os.path.dirname(source) == os.path.dirname(executable)

    def test_filename_functions_roundtrip(self):
        """Test that filename functions work together."""
        # Generate filename
        filename = get_source_filename("generator", "cpp")

        # Detect language and role
        language = get_language_from_filename(filename)
        role = get_role_from_filename(filename)

        assert language == "cpp"
        assert role == "generator"

    def test_validation_uses_correct_constants(self):
        """Test that validation uses TEST_TYPE_FILES constant."""
        # Comparator has generator, correct, test
        assert validate_file_for_test_type("generator.cpp", "comparator") is True
        assert validate_file_for_test_type("correct.cpp", "comparator") is True
        assert validate_file_for_test_type("test.cpp", "comparator") is True

        # Benchmarker has generator, test (no correct)
        assert validate_file_for_test_type("generator.cpp", "benchmarker") is True
        assert validate_file_for_test_type("test.cpp", "benchmarker") is True
        assert validate_file_for_test_type("correct.cpp", "benchmarker") is False

    def test_all_languages_supported_consistently(self):
        """Test that all supported languages work across functions."""
        languages = get_supported_languages()

        for lang in languages:
            # Should generate valid filenames
            source = get_source_filename("generator", lang)
            assert source is not None

            # Should detect language
            detected = get_language_from_filename(source)
            assert detected == lang

            # Should generate display name
            display = get_file_display_name("generator", lang)
            assert display is not None
