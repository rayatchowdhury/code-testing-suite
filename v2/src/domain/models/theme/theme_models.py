"""
Theme domain models for the v2 architecture.

Defines the core data structures for theme management without
coupling to any specific UI framework or implementation.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Dict, Optional, Any, List
from pathlib import Path


class ThemeType(Enum):
    """Available theme types"""
    LIGHT = "light"
    DARK = "dark"
    HIGH_CONTRAST = "high_contrast"
    CUSTOM = "custom"


@dataclass(frozen=True)
class ColorPalette:
    """Core color palette for a theme"""
    
    # Primary colors
    primary: str
    primary_dark: str
    primary_darker: str
    primary_container: str
    
    # Secondary colors  
    secondary: str
    accent: str
    error: str
    success: str
    warning: str
    
    # Surface colors
    background: str
    surface: str
    surface_dim: str
    surface_variant: str
    surface_bright: str
    
    # Text colors
    text_primary: str
    text_secondary: str
    text_disabled: str
    
    # Interactive colors
    border: str
    outline: str
    outline_variant: str
    hover: str
    pressed: str
    selected: str
    
    # Container colors
    error_container: str
    success_container: str
    warning_container: str
    
    # Text on colors (for accessibility)
    on_primary: str
    on_primary_container: str
    on_surface: str
    on_surface_variant: str
    on_error_container: str
    on_success_container: str
    on_warning_container: str


@dataclass(frozen=True)
class EditorColorScheme:
    """Color scheme specifically for code editor"""
    
    background: str
    background_darker: str
    text: str
    line_number: str
    current_line: str
    selection: str
    keyword: str
    string: str
    comment: str
    number: str
    operator: str
    bracket: str
    error: str
    warning: str


@dataclass(frozen=True)
class Typography:
    """Typography settings for the theme"""
    
    # Font families
    ui_font_family: str
    code_font_family: str
    
    # Font sizes (in points)
    font_size_xs: int
    font_size_sm: int
    font_size_base: int
    font_size_lg: int
    font_size_xl: int
    font_size_xxl: int
    
    # Line heights (as multipliers)
    line_height_tight: float
    line_height_normal: float
    line_height_loose: float
    
    # Font weights
    font_weight_normal: int
    font_weight_medium: int
    font_weight_bold: int


@dataclass(frozen=True)
class Spacing:
    """Spacing and sizing constants"""
    
    # Base spacing unit (in pixels)
    unit: int
    
    # Padding values
    padding_xs: int
    padding_sm: int
    padding_md: int
    padding_lg: int
    padding_xl: int
    
    # Margin values
    margin_xs: int
    margin_sm: int
    margin_md: int
    margin_lg: int
    margin_xl: int
    
    # Border radii
    border_radius_sm: int
    border_radius_md: int
    border_radius_lg: int
    border_radius_full: int
    
    # Border widths
    border_width_thin: int
    border_width_normal: int
    border_width_thick: int


@dataclass(frozen=True)
class Theme:
    """Complete theme definition"""
    
    name: str
    type: ThemeType
    description: str
    version: str
    
    # Core theme components
    colors: ColorPalette
    editor_colors: EditorColorScheme
    typography: Typography
    spacing: Spacing
    
    # Metadata
    author: Optional[str] = None
    created_at: Optional[str] = None
    custom_properties: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        """Validate theme after creation"""
        if not self.name:
            raise ValueError("Theme name cannot be empty")
        if not self.version:
            raise ValueError("Theme version cannot be empty")


@dataclass
class ThemeValidationResult:
    """Result of theme validation"""
    
    is_valid: bool
    errors: List[str]
    warnings: List[str]
    
    def __post_init__(self):
        if self.errors is None:
            self.errors = []
        if self.warnings is None:
            self.warnings = []
