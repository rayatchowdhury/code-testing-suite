"""
Predefined themes extracted and enhanced from v1 styling.

Contains built-in themes including the existing dark theme and
new light and high contrast variants.
"""

from typing import Dict
from domain.models.theme import (
    Theme, ThemeType, ColorPalette, EditorColorScheme, 
    Typography, Spacing
)


# Modern Dark Theme (based on v1 MATERIAL_COLORS)
DARK_COLOR_PALETTE = ColorPalette(
    # Primary colors
    primary='#0096C7',
    primary_dark='#023E8A', 
    primary_darker='#012E52',
    primary_container='#004B63',
    
    # Secondary colors
    secondary='#FFB703',
    accent='#F72585',
    error='#FF6B6B',
    success='#4ECDC4',
    warning='#FFE66D',
    
    # Surface colors
    background='#1B1B1E',
    surface='#242426',
    surface_dim='#1F1F21',
    surface_variant='#2A2A2D',
    surface_bright='#2F2F33',
    
    # Text colors
    text_primary='#FFFFFF',
    text_secondary='#B3B3B3',
    text_disabled='#666666',
    
    # Interactive colors
    border='#333333',
    outline='#3F3F3F',
    outline_variant='#2C2C2C',
    hover='#2A2A2D',
    pressed='#323235',
    selected='#004B63',
    
    # Container colors
    error_container='#420101',
    success_container='#1A4F4A',
    warning_container='#4A3F00',
    
    # Text on colors
    on_primary='#FFFFFF',
    on_primary_container='#FFFFFF',
    on_surface='#FFFFFF',
    on_surface_variant='#B3B3B3',
    on_error_container='#FFB6B6',
    on_success_container='#B8E6E4',
    on_warning_container='#FFEB9A'
)

DARK_EDITOR_COLORS = EditorColorScheme(
    background='#1C1C1E',
    background_darker='#18181A',
    text='#E8E8E8',
    line_number='#6C7A89',
    current_line='#252529',
    selection='#2D4F67',
    keyword='#569CD6',  # Blue keywords
    string='#CE9178',   # Orange strings
    comment='#6A9955',  # Green comments
    number='#B5CEA8',   # Light green numbers
    operator='#D4D4D4', # White operators
    bracket='#FFD700',  # Gold brackets
    error='#F44747',    # Red errors
    warning='#FF8C00'   # Orange warnings
)

# Light Theme
LIGHT_COLOR_PALETTE = ColorPalette(
    # Primary colors
    primary='#0077B6',
    primary_dark='#023047',
    primary_darker='#012028',
    primary_container='#B3E5FC',
    
    # Secondary colors
    secondary='#FF8500',
    accent='#D63384',
    error='#DC3545',
    success='#198754',
    warning='#FFC107',
    
    # Surface colors
    background='#FFFFFF',
    surface='#F8F9FA',
    surface_dim='#F1F3F4',
    surface_variant='#E9ECEF',
    surface_bright='#FFFFFF',
    
    # Text colors
    text_primary='#212529',
    text_secondary='#6C757D',
    text_disabled='#ADB5BD',
    
    # Interactive colors
    border='#DEE2E6',
    outline='#CED4DA',
    outline_variant='#E9ECEF',
    hover='#F8F9FA',
    pressed='#E9ECEF',
    selected='#B3E5FC',
    
    # Container colors
    error_container='#F8D7DA',
    success_container='#D1E7DD',
    warning_container='#FFF3CD',
    
    # Text on colors
    on_primary='#FFFFFF',
    on_primary_container='#212529',
    on_surface='#212529',
    on_surface_variant='#6C757D',
    on_error_container='#721C24',
    on_success_container='#0F5132',
    on_warning_container='#664D03'
)

LIGHT_EDITOR_COLORS = EditorColorScheme(
    background='#FFFFFF',
    background_darker='#F8F9FA',
    text='#212529',
    line_number='#6C757D',
    current_line='#F8F9FA',
    selection='#B3E5FC',
    keyword='#0000FF',   # Blue keywords
    string='#A31515',    # Red strings
    comment='#008000',   # Green comments
    number='#098658',    # Dark green numbers
    operator='#000000',  # Black operators
    bracket='#0431FA',   # Blue brackets
    error='#CD3131',     # Red errors
    warning='#FF8C00'    # Orange warnings
)

# High Contrast Theme
HIGH_CONTRAST_COLOR_PALETTE = ColorPalette(
    # Primary colors
    primary='#0000FF',
    primary_dark='#000080',
    primary_darker='#000040',
    primary_container='#8080FF',
    
    # Secondary colors
    secondary='#FF8000',
    accent='#FF00FF',
    error='#FF0000',
    success='#00FF00',
    warning='#FFFF00',
    
    # Surface colors
    background='#000000',
    surface='#1A1A1A',
    surface_dim='#0D0D0D',
    surface_variant='#333333',
    surface_bright='#404040',
    
    # Text colors
    text_primary='#FFFFFF',
    text_secondary='#CCCCCC',
    text_disabled='#808080',
    
    # Interactive colors
    border='#FFFFFF',
    outline='#FFFFFF',
    outline_variant='#CCCCCC',
    hover='#333333',
    pressed='#666666',
    selected='#0000FF',
    
    # Container colors
    error_container='#800000',
    success_container='#008000',
    warning_container='#808000',
    
    # Text on colors
    on_primary='#FFFFFF',
    on_primary_container='#FFFFFF',
    on_surface='#FFFFFF',
    on_surface_variant='#CCCCCC',
    on_error_container='#FFFFFF',
    on_success_container='#FFFFFF',
    on_warning_container='#FFFFFF'
)

HIGH_CONTRAST_EDITOR_COLORS = EditorColorScheme(
    background='#000000',
    background_darker='#000000',
    text='#FFFFFF',
    line_number='#CCCCCC',
    current_line='#333333',
    selection='#0000FF',
    keyword='#00FFFF',   # Cyan keywords
    string='#FFFF00',    # Yellow strings
    comment='#00FF00',   # Green comments
    number='#FF00FF',    # Magenta numbers
    operator='#FFFFFF',  # White operators
    bracket='#FF8000',   # Orange brackets
    error='#FF0000',     # Red errors
    warning='#FFFF00'    # Yellow warnings
)

# Common Typography
DEFAULT_TYPOGRAPHY = Typography(
    ui_font_family='Segoe UI, Tahoma, Geneva, Verdana, sans-serif',
    code_font_family='Consolas, Monaco, "Courier New", monospace',
    
    font_size_xs=10,
    font_size_sm=12,
    font_size_base=14,
    font_size_lg=16,
    font_size_xl=18,
    font_size_xxl=24,
    
    line_height_tight=1.2,
    line_height_normal=1.5,
    line_height_loose=1.8,
    
    font_weight_normal=400,
    font_weight_medium=500,
    font_weight_bold=700
)

# Common Spacing
DEFAULT_SPACING = Spacing(
    unit=8,
    
    padding_xs=4,
    padding_sm=8,
    padding_md=16,
    padding_lg=24,
    padding_xl=32,
    
    margin_xs=4,
    margin_sm=8,
    margin_md=16,
    margin_lg=24,
    margin_xl=32,
    
    border_radius_sm=4,
    border_radius_md=8,
    border_radius_lg=12,
    border_radius_full=9999,
    
    border_width_thin=1,
    border_width_normal=2,
    border_width_thick=3
)

# Predefined Themes
DARK_THEME = Theme(
    name='Modern Dark',
    type=ThemeType.DARK,
    description='Modern dark theme based on Material Design principles',
    version='2.0.0',
    colors=DARK_COLOR_PALETTE,
    editor_colors=DARK_EDITOR_COLORS,
    typography=DEFAULT_TYPOGRAPHY,
    spacing=DEFAULT_SPACING,
    author='v2 Migration Team',
    created_at='2025-08-31'
)

LIGHT_THEME = Theme(
    name='Clean Light',
    type=ThemeType.LIGHT,
    description='Clean light theme optimized for readability',
    version='2.0.0',
    colors=LIGHT_COLOR_PALETTE,
    editor_colors=LIGHT_EDITOR_COLORS,
    typography=DEFAULT_TYPOGRAPHY,
    spacing=DEFAULT_SPACING,
    author='v2 Migration Team',
    created_at='2025-08-31'
)

HIGH_CONTRAST_THEME = Theme(
    name='High Contrast',
    type=ThemeType.HIGH_CONTRAST,
    description='High contrast theme for accessibility',
    version='2.0.0',
    colors=HIGH_CONTRAST_COLOR_PALETTE,
    editor_colors=HIGH_CONTRAST_EDITOR_COLORS,
    typography=DEFAULT_TYPOGRAPHY,
    spacing=DEFAULT_SPACING,
    author='v2 Migration Team',
    created_at='2025-08-31'
)

# Theme registry
BUILT_IN_THEMES = {
    'dark': DARK_THEME,
    'light': LIGHT_THEME,
    'high_contrast': HIGH_CONTRAST_THEME
}

def get_default_theme() -> Theme:
    """Get the default theme (dark)"""
    return DARK_THEME

def get_theme_by_name(name: str) -> Theme:
    """Get a built-in theme by name"""
    theme = BUILT_IN_THEMES.get(name.lower())
    if not theme:
        raise ValueError(f"Unknown built-in theme: {name}")
    return theme

def get_available_themes() -> Dict[str, Theme]:
    """Get all available built-in themes"""
    return BUILT_IN_THEMES.copy()
