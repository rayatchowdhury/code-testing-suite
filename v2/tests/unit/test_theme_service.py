"""
Unit tests for ThemeService

Tests the centralized theme management functionality
"""
import pytest
from infrastructure.theming.theme_service import ThemeService, ThemeMode, ColorPalette

class TestThemeService:
    """Test theme service functionality"""
    
    def test_theme_service_initialization(self):
        """Test theme service initializes with default dark theme"""
        service = ThemeService()
        
        assert service.get_theme_mode() == ThemeMode.DARK
        palette = service.get_current_palette()
        assert isinstance(palette, ColorPalette)
        assert palette.background == '#1B1B1E'
    
    def test_theme_mode_switching(self):
        """Test switching between theme modes"""
        service = ThemeService()
        
        # Switch to light theme
        service.set_theme_mode(ThemeMode.LIGHT)
        assert service.get_theme_mode() == ThemeMode.LIGHT
        
        palette = service.get_current_palette()
        assert palette.background == '#FFFFFF'
        assert palette.text_primary == '#000000'
    
    def test_get_color_by_name(self):
        """Test getting colors by name"""
        service = ThemeService()
        
        primary_color = service.get_color('primary')
        assert primary_color == '#0096C7'
        
        background_color = service.get_color('background')
        assert background_color == '#1B1B1E'
    
    def test_get_invalid_color_raises_error(self):
        """Test error when requesting invalid color"""
        service = ThemeService()
        
        with pytest.raises(ValueError, match="Color 'invalid_color' not found"):
            service.get_color('invalid_color')
    
    def test_primary_button_style(self):
        """Test primary button stylesheet generation"""
        service = ThemeService()
        
        style = service.get_button_style("primary")
        
        assert "QPushButton" in style
        assert "#0096C7" in style  # primary color
        assert "background-color" in style
        assert "border-radius" in style
    
    def test_secondary_button_style(self):
        """Test secondary button stylesheet generation"""
        service = ThemeService()
        
        style = service.get_button_style("secondary")
        
        assert "QPushButton" in style
        assert "border:" in style
        assert "background-color" in style
    
    def test_dialog_style(self):
        """Test dialog stylesheet generation"""
        service = ThemeService()
        
        style = service.get_dialog_style()
        
        assert "QDialog" in style
        assert "QLabel" in style
        assert "QLineEdit" in style
        assert service.get_color('background') in style
    
    def test_section_style(self):
        """Test section frame stylesheet generation"""
        service = ThemeService()
        
        style = service.get_section_style()
        
        assert "QFrame#section_frame" in style
        assert "QLabel#section_title" in style
        assert "border-radius" in style
    
    def test_light_theme_colors(self):
        """Test light theme color palette"""
        service = ThemeService()
        service.set_theme_mode(ThemeMode.LIGHT)
        
        palette = service.get_current_palette()
        
        assert palette.background == '#FFFFFF'
        assert palette.text_primary == '#000000'
        assert palette.on_primary == '#FFFFFF'
        assert palette.button_hover == '#F0F0F0'
    
    def test_dark_theme_colors(self):
        """Test dark theme color palette"""
        service = ThemeService()
        service.set_theme_mode(ThemeMode.DARK)
        
        palette = service.get_current_palette()
        
        assert palette.background == '#1B1B1E'
        assert palette.text_primary == '#FFFFFF'
        assert palette.on_primary == '#FFFFFF'
        assert palette.button_hover == '#2A2A2D'
