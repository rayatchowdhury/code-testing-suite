# TODO: Extract theme system from v1 styles/ and create centralized theme service
"""
Theme Service - Centralized theme and styling management

Consolidates styling logic scattered across v1/styles/ into a single service.
Based on v1/styles/constants/colors.py and component-specific styles.
"""
from dataclasses import dataclass
from typing import Dict, Any, Optional
from enum import Enum

class ThemeMode(Enum):
    """Available theme modes"""
    DARK = "dark"
    LIGHT = "light"
    AUTO = "auto"

@dataclass
class ColorPalette:
    """Color palette for a theme"""
    # Background colors
    background: str
    surface: str
    surface_dim: str
    surface_variant: str
    surface_bright: str
    
    # Primary colors
    primary: str
    primary_dark: str
    primary_darker: str
    primary_container: str
    
    # Accent colors
    secondary: str
    accent: str
    error: str
    error_container: str
    on_error_container: str
    
    # Border and outline
    outline: str
    outline_variant: str
    border: str
    
    # Text colors
    text_primary: str
    text_secondary: str
    text_disabled: str
    
    # On-color variants
    on_primary: str
    on_primary_container: str
    on_surface: str
    on_surface_variant: str
    on_surface_dim: str
    on_surface_disabled: str
    
    # Interactive states
    button_hover: str
    
    # Component specific
    tab_height: str = "36px"

class ThemeService:
    """
    Centralized theme and styling service.
    
    ASSUMPTION: Migrates theme constants from v1/styles/constants/colors.py
    and provides a single point for all theming operations.
    """
    
    def __init__(self):
        self._current_mode = ThemeMode.DARK
        self._palettes = self._initialize_palettes()
    
    def _initialize_palettes(self) -> Dict[ThemeMode, ColorPalette]:
        """Initialize color palettes for different themes"""
        return {
            ThemeMode.DARK: ColorPalette(
                background='#1B1B1E',
                surface='#242426',
                surface_dim='#1F1F21',
                surface_variant='#2A2A2D',
                surface_bright='#2F2F33',
                
                primary='#0096C7',
                primary_dark='#023E8A',
                primary_darker='#012E52',
                primary_container='#004B63',
                
                secondary='#FFB703',
                accent='#F72585',
                error='#FF6B6B',
                error_container='#420101',
                on_error_container='#FFB6B6',
                
                outline='#3F3F3F',
                outline_variant='#2C2C2C',
                border='#333333',
                
                text_primary='#FFFFFF',
                text_secondary='#B3B3B3',
                text_disabled='#666666',
                
                on_primary='#FFFFFF',
                on_primary_container='#FFFFFF',
                on_surface='#FFFFFF',
                on_surface_variant='#B3B3B3',
                on_surface_dim='#999999',
                on_surface_disabled='#666666',
                
                button_hover='#2A2A2D'
            ),
            ThemeMode.LIGHT: ColorPalette(
                background='#FFFFFF',
                surface='#F8F9FA',
                surface_dim='#F0F1F3',
                surface_variant='#E8E9EB',
                surface_bright='#FFFFFF',
                
                primary='#0096C7',
                primary_dark='#023E8A',
                primary_darker='#012E52',
                primary_container='#B3E5FC',
                
                secondary='#FFB703',
                accent='#F72585',
                error='#D32F2F',
                error_container='#FFEBEE',
                on_error_container='#B71C1C',
                
                outline='#CCCCCC',
                outline_variant='#E0E0E0',
                border='#DDDDDD',
                
                text_primary='#000000',
                text_secondary='#666666',
                text_disabled='#AAAAAA',
                
                on_primary='#FFFFFF',
                on_primary_container='#000000',
                on_surface='#000000',
                on_surface_variant='#666666',
                on_surface_dim='#999999',
                on_surface_disabled='#CCCCCC',
                
                button_hover='#F0F0F0'
            )
        }
    
    def get_current_palette(self) -> ColorPalette:
        """Get the current color palette"""
        return self._palettes[self._current_mode]
    
    def set_theme_mode(self, mode: ThemeMode) -> None:
        """Set the current theme mode"""
        self._current_mode = mode
    
    def get_theme_mode(self) -> ThemeMode:
        """Get the current theme mode"""
        return self._current_mode
    
    def get_color(self, color_name: str) -> str:
        """Get a specific color from the current palette"""
        palette = self.get_current_palette()
        
        if hasattr(palette, color_name):
            return getattr(palette, color_name)
        
        raise ValueError(f"Color '{color_name}' not found in current palette")
    
    def get_button_style(self, button_type: str = "primary") -> str:
        """Get stylesheet for buttons"""
        palette = self.get_current_palette()
        
        if button_type == "primary":
            return f"""
                QPushButton {{
                    background-color: {palette.primary};
                    color: {palette.on_primary};
                    border: none;
                    border-radius: 4px;
                    padding: 8px 16px;
                    font-weight: 500;
                }}
                QPushButton:hover {{
                    background-color: {palette.primary_dark};
                }}
                QPushButton:pressed {{
                    background-color: {palette.primary_darker};
                }}
                QPushButton:disabled {{
                    background-color: {palette.surface_dim};
                    color: {palette.text_disabled};
                }}
            """
        elif button_type == "secondary":
            return f"""
                QPushButton {{
                    background-color: {palette.surface_variant};
                    color: {palette.on_surface_variant};
                    border: 1px solid {palette.outline};
                    border-radius: 4px;
                    padding: 8px 16px;
                    font-weight: 500;
                }}
                QPushButton:hover {{
                    background-color: {palette.button_hover};
                }}
                QPushButton:pressed {{
                    background-color: {palette.surface_dim};
                }}
            """
        
        return ""
    
    def get_dialog_style(self) -> str:
        """Get stylesheet for dialogs"""
        palette = self.get_current_palette()
        
        return f"""
            QDialog {{
                background-color: {palette.background};
                color: {palette.text_primary};
            }}
            QLabel {{
                color: {palette.text_primary};
            }}
            QLineEdit {{
                background-color: {palette.surface};
                border: 1px solid {palette.outline};
                border-radius: 4px;
                padding: 6px;
                color: {palette.text_primary};
            }}
            QLineEdit:focus {{
                border-color: {palette.primary};
            }}
            QComboBox {{
                background-color: {palette.surface};
                border: 1px solid {palette.outline};
                border-radius: 4px;
                padding: 6px;
                color: {palette.text_primary};
            }}
            QComboBox:focus {{
                border-color: {palette.primary};
            }}
            QCheckBox {{
                color: {palette.text_primary};
            }}
            QCheckBox::indicator:checked {{
                background-color: {palette.primary};
                border: 1px solid {palette.primary};
            }}
        """
    
    def get_section_style(self) -> str:
        """Get stylesheet for section frames"""
        palette = self.get_current_palette()
        
        return f"""
            QFrame#section_frame {{
                background-color: {palette.surface};
                border: 1px solid {palette.outline_variant};
                border-radius: 6px;
                margin: 4px 0;
            }}
            QLabel#section_title {{
                font-size: 14px;
                font-weight: 600;
                color: {palette.primary};
                margin: 8px 0;
            }}
            QWidget#section_content {{
                background-color: transparent;
            }}
        """
