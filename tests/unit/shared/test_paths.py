"""
Unit tests for shared/constants/paths.py module.

Tests path constants, test type normalization, and path helper functions.

Test Coverage:
- normalize_test_type: Validates test type aliases and canonical names
- get_test_type_dir: Constructs test type directory paths
- get_inputs_dir: Constructs inputs subdirectory paths
- get_outputs_dir: Constructs outputs subdirectory paths
- get_workspace_file_path: Constructs workspace file paths
- get_input_file_path: Constructs input file paths
- get_output_file_path: Constructs output file paths
- TEST_TYPE_ALIASES: Validates constant dictionary
- Path constants validation
"""

import os
import pytest
from pathlib import Path

from src.app.shared.constants.paths import (
    # Constants
    PROJECT_ROOT,
    SRC_ROOT,
    RESOURCES_DIR,
    ICONS_DIR,
    USER_DATA_DIR,
    WORKSPACE_DIR,
    CONFIG_FILE,
    EDITOR_STATE_FILE,
    WORKSPACE_COMPARATOR_SUBDIR,
    WORKSPACE_VALIDATOR_SUBDIR,
    WORKSPACE_BENCHMARKER_SUBDIR,
    WORKSPACE_INPUTS_SUBDIR,
    WORKSPACE_OUTPUTS_SUBDIR,
    TEST_TYPE_ALIASES,
    # Functions
    normalize_test_type,
    get_test_type_dir,
    get_inputs_dir,
    get_outputs_dir,
    get_workspace_file_path,
    get_input_file_path,
    get_output_file_path,
)


class TestNormalizeTestType:
    """Tests for normalize_test_type function."""

    @pytest.mark.parametrize(
        "alias,expected",
        [
            ("comparison", "comparator"),
            ("validation", "validator"),
            ("benchmark", "benchmarker"),
        ],
    )
    def test_normalizes_aliases(self, alias, expected):
        """Test that aliases are normalized to canonical names."""
        result = normalize_test_type(alias)
        assert result == expected

    @pytest.mark.parametrize(
        "canonical_name",
        [
            "comparator",
            "validator",
            "benchmarker",
        ],
    )
    def test_handles_canonical_names(self, canonical_name):
        """Test that canonical names pass through unchanged."""
        result = normalize_test_type(canonical_name)
        assert result == canonical_name

    @pytest.mark.parametrize(
        "test_type",
        [
            "Comparator",
            "VALIDATOR",
            "BenchMarker",
            "CoMpArIsOn",
        ],
    )
    def test_case_insensitive(self, test_type):
        """Test that normalization is case-insensitive."""
        result = normalize_test_type(test_type)
        assert result in ["comparator", "validator", "benchmarker"]

    def test_raises_value_error_for_invalid_type(self):
        """Test that invalid test types raise ValueError."""
        with pytest.raises(ValueError, match="Unknown test type"):
            normalize_test_type("invalid_type")

    def test_raises_value_error_for_empty_string(self):
        """Test that empty string raises ValueError."""
        with pytest.raises(ValueError, match="Unknown test type"):
            normalize_test_type("")

    def test_raises_value_error_for_none(self):
        """Test that None raises TypeError or ValueError."""
        with pytest.raises((ValueError, AttributeError)):
            normalize_test_type(None)


class TestGetTestTypeDir:
    """Tests for get_test_type_dir function."""

    def test_returns_correct_path_for_comparator(self, temp_dir):
        """Test path construction for comparator."""
        result = get_test_type_dir(temp_dir, "comparator")
        expected = os.path.join(temp_dir, "comparator")
        assert result == expected

    def test_returns_correct_path_for_validator(self, temp_dir):
        """Test path construction for validator."""
        result = get_test_type_dir(temp_dir, "validator")
        expected = os.path.join(temp_dir, "validator")
        assert result == expected

    def test_returns_correct_path_for_benchmarker(self, temp_dir):
        """Test path construction for benchmarker."""
        result = get_test_type_dir(temp_dir, "benchmarker")
        expected = os.path.join(temp_dir, "benchmarker")
        assert result == expected

    @pytest.mark.parametrize(
        "alias,expected_subdir",
        [
            ("comparison", "comparator"),
            ("validation", "validator"),
            ("benchmark", "benchmarker"),
        ],
    )
    def test_normalizes_aliases(self, temp_dir, alias, expected_subdir):
        """Test that aliases are normalized before path construction."""
        result = get_test_type_dir(temp_dir, alias)
        expected = os.path.join(temp_dir, expected_subdir)
        assert result == expected

    def test_handles_absolute_workspace_path(self):
        """Test with absolute workspace path."""
        workspace = r"C:\Users\Test\workspace"
        result = get_test_type_dir(workspace, "comparator")
        expected = os.path.join(workspace, "comparator")
        assert result == expected

    def test_handles_relative_workspace_path(self):
        """Test with relative workspace path."""
        workspace = "workspace"
        result = get_test_type_dir(workspace, "validator")
        expected = os.path.join("workspace", "validator")
        assert result == expected


class TestGetInputsDir:
    """Tests for get_inputs_dir function."""

    def test_returns_inputs_subdirectory(self, temp_dir):
        """Test that inputs subdirectory is appended."""
        result = get_inputs_dir(temp_dir, "comparator")
        expected = os.path.join(temp_dir, "comparator", "inputs")
        assert result == expected

    @pytest.mark.parametrize(
        "test_type",
        [
            "comparator",
            "validator",
            "benchmarker",
        ],
    )
    def test_handles_all_test_types(self, temp_dir, test_type):
        """Test inputs directory for all test types."""
        result = get_inputs_dir(temp_dir, test_type)
        expected = os.path.join(temp_dir, test_type, "inputs")
        assert result == expected

    @pytest.mark.parametrize(
        "alias,expected_subdir",
        [
            ("comparison", "comparator"),
            ("validation", "validator"),
            ("benchmark", "benchmarker"),
        ],
    )
    def test_normalizes_test_type(self, temp_dir, alias, expected_subdir):
        """Test that test type is normalized before path construction."""
        result = get_inputs_dir(temp_dir, alias)
        expected = os.path.join(temp_dir, expected_subdir, "inputs")
        assert result == expected

    def test_inputs_subdir_constant_matches(self):
        """Test that function uses WORKSPACE_INPUTS_SUBDIR constant."""
        # Validate the constant
        assert WORKSPACE_INPUTS_SUBDIR == "inputs"


class TestGetOutputsDir:
    """Tests for get_outputs_dir function."""

    def test_returns_outputs_subdirectory(self, temp_dir):
        """Test that outputs subdirectory is appended."""
        result = get_outputs_dir(temp_dir, "comparator")
        expected = os.path.join(temp_dir, "comparator", "outputs")
        assert result == expected

    @pytest.mark.parametrize(
        "test_type",
        [
            "comparator",
            "validator",
            "benchmarker",
        ],
    )
    def test_handles_all_test_types(self, temp_dir, test_type):
        """Test outputs directory for all test types."""
        result = get_outputs_dir(temp_dir, test_type)
        expected = os.path.join(temp_dir, test_type, "outputs")
        assert result == expected

    @pytest.mark.parametrize(
        "alias,expected_subdir",
        [
            ("comparison", "comparator"),
            ("validation", "validator"),
            ("benchmark", "benchmarker"),
        ],
    )
    def test_normalizes_test_type(self, temp_dir, alias, expected_subdir):
        """Test that test type is normalized before path construction."""
        result = get_outputs_dir(temp_dir, alias)
        expected = os.path.join(temp_dir, expected_subdir, "outputs")
        assert result == expected

    def test_outputs_subdir_constant_matches(self):
        """Test that function uses WORKSPACE_OUTPUTS_SUBDIR constant."""
        # Validate the constant
        assert WORKSPACE_OUTPUTS_SUBDIR == "outputs"


class TestGetWorkspaceFilePath:
    """Tests for get_workspace_file_path function."""

    @pytest.mark.parametrize(
        "filename",
        [
            "generator.cpp",
            "correct.py",
            "test.java",
            "validator.cpp",
        ],
    )
    def test_constructs_file_path(self, temp_dir, filename):
        """Test file path construction with different filenames."""
        result = get_workspace_file_path(temp_dir, "comparator", filename)
        expected = os.path.join(temp_dir, "comparator", filename)
        assert result == expected

    def test_handles_all_test_types(self, temp_dir):
        """Test file path construction for all test types."""
        filename = "generator.cpp"
        
        result = get_workspace_file_path(temp_dir, "comparator", filename)
        assert result == os.path.join(temp_dir, "comparator", filename)
        
        result = get_workspace_file_path(temp_dir, "validator", filename)
        assert result == os.path.join(temp_dir, "validator", filename)
        
        result = get_workspace_file_path(temp_dir, "benchmarker", filename)
        assert result == os.path.join(temp_dir, "benchmarker", filename)

    @pytest.mark.parametrize(
        "alias,expected_subdir",
        [
            ("comparison", "comparator"),
            ("validation", "validator"),
            ("benchmark", "benchmarker"),
        ],
    )
    def test_normalizes_test_type(self, temp_dir, alias, expected_subdir):
        """Test that test type is normalized."""
        filename = "test.cpp"
        result = get_workspace_file_path(temp_dir, alias, filename)
        expected = os.path.join(temp_dir, expected_subdir, filename)
        assert result == expected

    def test_handles_filenames_with_special_characters(self, temp_dir):
        """Test filenames with spaces and special characters."""
        filename = "test file (1).cpp"
        result = get_workspace_file_path(temp_dir, "comparator", filename)
        expected = os.path.join(temp_dir, "comparator", filename)
        assert result == expected


class TestGetInputFilePath:
    """Tests for get_input_file_path function."""

    @pytest.mark.parametrize(
        "filename",
        [
            "input_1.txt",
            "test_input.txt",
            "data.txt",
        ],
    )
    def test_constructs_input_file_path(self, temp_dir, filename):
        """Test input file path construction."""
        result = get_input_file_path(temp_dir, "comparator", filename)
        expected = os.path.join(temp_dir, "comparator", "inputs", filename)
        assert result == expected

    def test_handles_all_test_types(self, temp_dir):
        """Test input file path for all test types."""
        filename = "input.txt"
        
        result = get_input_file_path(temp_dir, "comparator", filename)
        assert result == os.path.join(temp_dir, "comparator", "inputs", filename)
        
        result = get_input_file_path(temp_dir, "validator", filename)
        assert result == os.path.join(temp_dir, "validator", "inputs", filename)
        
        result = get_input_file_path(temp_dir, "benchmarker", filename)
        assert result == os.path.join(temp_dir, "benchmarker", "inputs", filename)

    @pytest.mark.parametrize(
        "alias,expected_subdir",
        [
            ("comparison", "comparator"),
            ("validation", "validator"),
            ("benchmark", "benchmarker"),
        ],
    )
    def test_normalizes_test_type(self, temp_dir, alias, expected_subdir):
        """Test that test type is normalized."""
        filename = "input.txt"
        result = get_input_file_path(temp_dir, alias, filename)
        expected = os.path.join(temp_dir, expected_subdir, "inputs", filename)
        assert result == expected

    def test_handles_numeric_filenames(self, temp_dir):
        """Test input files with numeric names."""
        filename = "1.txt"
        result = get_input_file_path(temp_dir, "comparator", filename)
        expected = os.path.join(temp_dir, "comparator", "inputs", filename)
        assert result == expected


class TestGetOutputFilePath:
    """Tests for get_output_file_path function."""

    @pytest.mark.parametrize(
        "filename",
        [
            "output_1.txt",
            "expected_output.txt",
            "result.txt",
        ],
    )
    def test_constructs_output_file_path(self, temp_dir, filename):
        """Test output file path construction."""
        result = get_output_file_path(temp_dir, "comparator", filename)
        expected = os.path.join(temp_dir, "comparator", "outputs", filename)
        assert result == expected

    def test_handles_all_test_types(self, temp_dir):
        """Test output file path for all test types."""
        filename = "output.txt"
        
        result = get_output_file_path(temp_dir, "comparator", filename)
        assert result == os.path.join(temp_dir, "comparator", "outputs", filename)
        
        result = get_output_file_path(temp_dir, "validator", filename)
        assert result == os.path.join(temp_dir, "validator", "outputs", filename)
        
        result = get_output_file_path(temp_dir, "benchmarker", filename)
        assert result == os.path.join(temp_dir, "benchmarker", "outputs", filename)

    @pytest.mark.parametrize(
        "alias,expected_subdir",
        [
            ("comparison", "comparator"),
            ("validation", "validator"),
            ("benchmark", "benchmarker"),
        ],
    )
    def test_normalizes_test_type(self, temp_dir, alias, expected_subdir):
        """Test that test type is normalized."""
        filename = "output.txt"
        result = get_output_file_path(temp_dir, alias, filename)
        expected = os.path.join(temp_dir, expected_subdir, "outputs", filename)
        assert result == expected

    def test_handles_numeric_filenames(self, temp_dir):
        """Test output files with numeric names."""
        filename = "1.txt"
        result = get_output_file_path(temp_dir, "comparator", filename)
        expected = os.path.join(temp_dir, "comparator", "outputs", filename)
        assert result == expected


class TestTestTypeAliases:
    """Tests for TEST_TYPE_ALIASES constant."""

    def test_aliases_dict_exists(self):
        """Test that TEST_TYPE_ALIASES exists and is a dict."""
        assert isinstance(TEST_TYPE_ALIASES, dict)

    def test_has_comparison_alias(self):
        """Test that 'comparison' alias maps to 'comparator'."""
        assert TEST_TYPE_ALIASES.get("comparison") == "comparator"

    def test_has_validation_alias(self):
        """Test that 'validation' alias maps to 'validator'."""
        assert TEST_TYPE_ALIASES.get("validation") == "validator"

    def test_has_benchmark_alias(self):
        """Test that 'benchmark' alias maps to 'benchmarker'."""
        assert TEST_TYPE_ALIASES.get("benchmark") == "benchmarker"

    def test_canonical_names_map_to_themselves(self):
        """Test that canonical names map to themselves."""
        assert TEST_TYPE_ALIASES.get("comparator") == "comparator"
        assert TEST_TYPE_ALIASES.get("validator") == "validator"
        assert TEST_TYPE_ALIASES.get("benchmarker") == "benchmarker"

    def test_all_values_are_canonical(self):
        """Test that all alias values are canonical test types."""
        canonical_types = {"comparator", "validator", "benchmarker"}
        for value in TEST_TYPE_ALIASES.values():
            assert value in canonical_types

    def test_aliases_are_lowercase(self):
        """Test that all alias keys are lowercase."""
        for key in TEST_TYPE_ALIASES.keys():
            assert key == key.lower()


class TestPathConstants:
    """Tests for path constants."""

    def test_project_root_exists(self):
        """Test that PROJECT_ROOT is defined."""
        assert PROJECT_ROOT is not None
        assert isinstance(PROJECT_ROOT, (str, Path))

    def test_src_root_exists(self):
        """Test that SRC_ROOT is defined."""
        assert SRC_ROOT is not None
        assert isinstance(SRC_ROOT, (str, Path))

    def test_resources_dir_exists(self):
        """Test that RESOURCES_DIR is defined."""
        assert RESOURCES_DIR is not None
        assert isinstance(RESOURCES_DIR, (str, Path))

    def test_icons_dir_exists(self):
        """Test that ICONS_DIR is defined."""
        assert ICONS_DIR is not None
        assert isinstance(ICONS_DIR, (str, Path))

    def test_user_data_dir_exists(self):
        """Test that USER_DATA_DIR is defined."""
        assert USER_DATA_DIR is not None
        assert isinstance(USER_DATA_DIR, (str, Path))

    def test_workspace_dir_exists(self):
        """Test that WORKSPACE_DIR is defined."""
        assert WORKSPACE_DIR is not None
        assert isinstance(WORKSPACE_DIR, (str, Path))

    def test_config_file_exists(self):
        """Test that CONFIG_FILE is defined."""
        assert CONFIG_FILE is not None
        assert isinstance(CONFIG_FILE, (str, Path))

    def test_editor_state_file_exists(self):
        """Test that EDITOR_STATE_FILE is defined."""
        assert EDITOR_STATE_FILE is not None
        assert isinstance(EDITOR_STATE_FILE, (str, Path))

    def test_workspace_subdirs_are_strings(self):
        """Test that workspace subdirectory constants are strings."""
        assert isinstance(WORKSPACE_COMPARATOR_SUBDIR, str)
        assert isinstance(WORKSPACE_VALIDATOR_SUBDIR, str)
        assert isinstance(WORKSPACE_BENCHMARKER_SUBDIR, str)
        assert isinstance(WORKSPACE_INPUTS_SUBDIR, str)
        assert isinstance(WORKSPACE_OUTPUTS_SUBDIR, str)

    def test_workspace_subdirs_match_expected(self):
        """Test that workspace subdirectory constants have expected values."""
        assert WORKSPACE_COMPARATOR_SUBDIR == "comparator"
        assert WORKSPACE_VALIDATOR_SUBDIR == "validator"
        assert WORKSPACE_BENCHMARKER_SUBDIR == "benchmarker"
        assert WORKSPACE_INPUTS_SUBDIR == "inputs"
        assert WORKSPACE_OUTPUTS_SUBDIR == "outputs"


class TestPathsIntegration:
    """Integration tests for path functions working together."""

    def test_complete_path_hierarchy(self, temp_dir):
        """Test complete path hierarchy from workspace to input file."""
        test_type = "comparator"
        filename = "input_1.txt"
        
        # Build path step by step
        test_type_dir = get_test_type_dir(temp_dir, test_type)
        inputs_dir = get_inputs_dir(temp_dir, test_type)
        input_file = get_input_file_path(temp_dir, test_type, filename)
        
        # Verify hierarchy
        assert test_type_dir in input_file
        assert inputs_dir in input_file
        assert filename in input_file

    def test_input_and_output_paths_parallel(self, temp_dir):
        """Test that input and output paths are parallel."""
        test_type = "validator"
        
        input_file = get_input_file_path(temp_dir, test_type, "1.txt")
        output_file = get_output_file_path(temp_dir, test_type, "1.txt")
        
        # Both should be under test_type directory
        test_type_dir = get_test_type_dir(temp_dir, test_type)
        assert test_type_dir in input_file
        assert test_type_dir in output_file
        
        # Should be in different subdirectories
        assert "inputs" in input_file
        assert "outputs" in output_file

    def test_alias_normalization_across_functions(self, temp_dir):
        """Test that all functions normalize aliases consistently."""
        alias = "comparison"
        canonical = "comparator"
        filename = "test.cpp"
        
        test_type_dir = get_test_type_dir(temp_dir, alias)
        workspace_file = get_workspace_file_path(temp_dir, alias, filename)
        inputs_dir = get_inputs_dir(temp_dir, alias)
        outputs_dir = get_outputs_dir(temp_dir, alias)
        
        # All should contain canonical name
        assert canonical in test_type_dir
        assert canonical in workspace_file
        assert canonical in inputs_dir
        assert canonical in outputs_dir

    def test_paths_are_os_independent(self, temp_dir):
        """Test that paths use os.path.join for OS independence."""
        result = get_input_file_path(temp_dir, "comparator", "test.txt")
        
        # Should use proper path separator for OS
        assert os.path.sep in result or len(result.split(os.path.sep)) > 1
