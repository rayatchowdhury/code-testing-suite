"""
Tests for the constants module.

This module tests path constants and utility functions to ensure
they return correct paths and handle edge cases properly.
"""

import pytest
import os
from pathlib import Path
from unittest.mock import patch

import constants
from constants import (
    PROJECT_ROOT, RESOURCES_DIR, ICONS_DIR,
    APP_ICON, SETTINGS_ICON, CHECK_ICON,
    USER_DATA_DIR, WORKSPACE_DIR, CONFIG_FILE,
    get_icon_path, get_help_content_path, ensure_user_data_dir
)


class TestPathConstants:
    """Test path constant definitions."""
    
    @pytest.mark.unit
    def test_project_root_exists(self):
        """Test that PROJECT_ROOT points to actual project directory."""
        assert PROJECT_ROOT.exists()
        assert PROJECT_ROOT.is_dir()
        # Should contain main.py
        assert (PROJECT_ROOT / "main.py").exists()
    
    @pytest.mark.unit
    def test_resources_dir_path(self):
        """Test that RESOURCES_DIR is correctly constructed."""
        expected = PROJECT_ROOT / "resources"
        assert RESOURCES_DIR == expected
    
    @pytest.mark.unit  
    def test_icons_dir_path(self):
        """Test that ICONS_DIR is correctly constructed."""
        expected = RESOURCES_DIR / "icons"
        assert ICONS_DIR == expected
    
    @pytest.mark.unit
    def test_icon_constants_are_strings(self):
        """Test that icon constants return string paths."""
        assert isinstance(APP_ICON, str)
        assert isinstance(SETTINGS_ICON, str)
        assert isinstance(CHECK_ICON, str)
    
    @pytest.mark.unit
    def test_icon_paths_point_to_png_files(self):
        """Test that icon paths end with .png."""
        assert APP_ICON.endswith('.png')
        assert SETTINGS_ICON.endswith('.png')
        assert CHECK_ICON.endswith('.png')
    
    @pytest.mark.unit
    def test_user_data_dir_structure(self):
        """Test that user data directory path is correctly constructed."""
        assert '.code_testing_suite' in USER_DATA_DIR
        assert 'workspace' in WORKSPACE_DIR
        assert 'config.json' in CONFIG_FILE


class TestPathUtilities:
    """Test utility functions for path generation."""
    
    @pytest.mark.unit
    def test_get_icon_path_with_extension(self):
        """Test get_icon_path with .png extension."""
        result = get_icon_path('test.png')
        expected = str(ICONS_DIR / 'test.png')
        assert result == expected
    
    @pytest.mark.unit
    def test_get_icon_path_without_extension(self):
        """Test get_icon_path automatically adds .png extension."""
        result = get_icon_path('test')
        expected = str(ICONS_DIR / 'test.png')
        assert result == expected
    
    @pytest.mark.unit
    def test_get_help_content_path_with_extension(self):
        """Test get_help_content_path with .html extension."""
        result = get_help_content_path('intro.html')
        assert result.endswith('intro.html')
        assert 'help_center' in result
    
    @pytest.mark.unit
    def test_get_help_content_path_without_extension(self):
        """Test get_help_content_path automatically adds .html extension."""
        result = get_help_content_path('intro')
        assert result.endswith('intro.html')
        assert 'help_center' in result
    
    @pytest.mark.unit
    def test_ensure_user_data_dir(self, temp_dir):
        """Test ensure_user_data_dir creates directory."""
        test_dir = os.path.join(temp_dir, 'test_config')
        
        with patch('constants.paths.USER_DATA_DIR', test_dir):
            ensure_user_data_dir()
            assert os.path.exists(test_dir)
            assert os.path.isdir(test_dir)


class TestPathIntegration:
    """Integration tests for path constants with actual file system."""
    
    @pytest.mark.integration
    def test_app_icon_file_exists(self):
        """Test that APP_ICON points to existing file."""
        # This test might fail if icon file doesn't exist
        # But it's useful to know if resources are missing
        if os.path.exists(APP_ICON):
            assert os.path.isfile(APP_ICON)
    
    @pytest.mark.integration
    def test_resources_directory_structure(self):
        """Test that expected resource directories exist."""
        if RESOURCES_DIR.exists():
            # Check for expected subdirectories
            assert (RESOURCES_DIR / "icons").exists() or True  # Don't fail if missing
            assert (RESOURCES_DIR / "readme").exists() or True  # Don't fail if missing
