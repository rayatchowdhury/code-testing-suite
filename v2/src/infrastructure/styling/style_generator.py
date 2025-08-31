"""
Style Generator Service

Generates Qt stylesheets from theme models, providing a clean separation
between theme definitions and Qt-specific styling implementation.
"""

from typing import Dict, Optional, Any
from domain.models.theme import Theme, ColorPalette, EditorColorScheme, Typography, Spacing


class StyleGenerator:
    """Generates Qt stylesheets from theme models"""
    
    def __init__(self, theme: Theme):
        self.theme = theme
        self.colors = theme.colors
        self.editor_colors = theme.editor_colors
        self.typography = theme.typography
        self.spacing = theme.spacing
    
    def update_theme(self, theme: Theme) -> None:
        """Update the theme used for style generation"""
        self.theme = theme
        self.colors = theme.colors
        self.editor_colors = theme.editor_colors
        self.typography = theme.typography
        self.spacing = theme.spacing
    
    # Core Component Styles
    def generate_scrollbar_style(self) -> str:
        """Generate scrollbar stylesheet"""
        return f"""
        QScrollBar:vertical {{
            background: transparent;
            width: {self.spacing.unit}px;
            margin: 0;
        }}
        
        QScrollBar::handle:vertical {{
            background-color: {self._add_alpha(self.colors.text_secondary, 0.3)};
            min-height: {self.spacing.padding_lg}px;
            border-radius: {self.spacing.border_radius_sm}px;
        }}
        
        QScrollBar::handle:vertical:hover {{
            background-color: {self._add_alpha(self.colors.text_secondary, 0.4)};
        }}
        
        QScrollBar::handle:vertical:pressed {{
            background-color: {self._add_alpha(self.colors.text_secondary, 0.5)};
        }}
        
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
            height: 0px;
        }}
        
        QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
            background: none;
        }}
        
        QScrollBar:horizontal {{
            background: transparent;
            height: {self.spacing.unit}px;
            margin: 0;
        }}
        
        QScrollBar::handle:horizontal {{
            background-color: {self._add_alpha(self.colors.text_secondary, 0.3)};
            min-width: {self.spacing.padding_lg}px;
            border-radius: {self.spacing.border_radius_sm}px;
        }}
        
        QScrollBar::handle:horizontal:hover {{
            background-color: {self._add_alpha(self.colors.text_secondary, 0.4)};
        }}
        
        QScrollBar::handle:horizontal:pressed {{
            background-color: {self._add_alpha(self.colors.text_secondary, 0.5)};
        }}
        
        QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
            width: 0px;
        }}
        
        QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {{
            background: none;
        }}
        """
    
    def generate_button_style(self, variant: str = "primary") -> str:
        """Generate button stylesheet for different variants"""
        if variant == "primary":
            bg_color = self.colors.primary
            hover_color = self.colors.primary_dark
            pressed_color = self.colors.primary_darker
            text_color = self.colors.on_primary
        elif variant == "secondary":
            bg_color = self.colors.secondary
            hover_color = self._darken_color(self.colors.secondary, 0.1)
            pressed_color = self._darken_color(self.colors.secondary, 0.2)
            text_color = self.colors.text_primary
        elif variant == "surface":
            bg_color = self.colors.surface
            hover_color = self.colors.hover
            pressed_color = self.colors.pressed
            text_color = self.colors.text_primary
        else:
            bg_color = self.colors.surface
            hover_color = self.colors.hover
            pressed_color = self.colors.pressed
            text_color = self.colors.text_primary
        
        return f"""
        QPushButton {{
            background-color: {bg_color};
            color: {text_color};
            border: {self.spacing.border_width_normal}px solid {self.colors.outline};
            border-radius: {self.spacing.border_radius_md}px;
            padding: {self.spacing.padding_sm}px {self.spacing.padding_md}px;
            font-family: {self.typography.ui_font_family};
            font-size: {self.typography.font_size_base}px;
            font-weight: {self.typography.font_weight_medium};
        }}
        
        QPushButton:hover {{
            background-color: {hover_color};
            border-color: {self.colors.primary};
        }}
        
        QPushButton:pressed {{
            background-color: {pressed_color};
        }}
        
        QPushButton:disabled {{
            background-color: {self.colors.surface_dim};
            color: {self.colors.text_disabled};
            border-color: {self.colors.outline_variant};
        }}
        """
    
    def generate_sidebar_style(self) -> str:
        """Generate sidebar stylesheet"""
        return f"""
        QWidget#sidebar, QWidget#sidebar_scroll, QWidget#sidebar_content {{
            background: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1,
                stop:0 {self._add_alpha(self.colors.surface_dim, 0.98)},
                stop:0.3 {self._add_alpha(self.colors.surface, 0.95)},
                stop:0.7 {self._add_alpha(self.colors.surface_dim, 0.98)},
                stop:1 {self._add_alpha(self.colors.surface, 0.95)});
        }}
        
        QWidget#sidebar {{
            border-right: {self.spacing.border_width_normal}px solid {self._add_alpha(self.colors.outline, 0.3)};
        }}
        
        QLabel#section_title {{
            color: {self._add_alpha(self.colors.accent, 0.8)};
            background: transparent;
            padding: {self.spacing.padding_xs}px {self.spacing.padding_md}px;
            margin: {self.spacing.margin_xs}px 0;
            font-size: {self.typography.font_size_xs}px;
            font-weight: {self.typography.font_weight_bold};
            font-family: {self.typography.ui_font_family};
        }}
        
        QLabel#sidebar_title {{
            color: {self.colors.text_primary};
            background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                                     stop: 0 {self._add_alpha(self.colors.background, 0.98)},
                                     stop: 0.03 {self._add_alpha(self.colors.background, 0.98)},
                                     stop: 0.5 {self._add_alpha(self.colors.accent, 0.8)},
                                     stop: 0.6 {self._add_alpha(self.colors.background, 0.6)},
                                     stop: 1 {self._add_alpha(self.colors.background, 0.98)});
            border: {self.spacing.border_width_normal}px solid {self._add_alpha(self.colors.primary, 0.3)};
            border-radius: {self.spacing.border_radius_lg}px;
            margin: {self.spacing.margin_sm}px {self.spacing.margin_sm}px;
            padding: {self.spacing.padding_lg}px {self.spacing.padding_md}px;
            font-size: {self.typography.font_size_xl}px;
            font-weight: {self.typography.font_weight_bold};
            font-family: {self.typography.ui_font_family};
        }}
        """
    
    def generate_text_input_style(self) -> str:
        """Generate text input stylesheet"""
        return f"""
        QLineEdit, QTextEdit, QPlainTextEdit {{
            background-color: {self.colors.surface};
            color: {self.colors.text_primary};
            border: {self.spacing.border_width_normal}px solid {self.colors.outline};
            border-radius: {self.spacing.border_radius_sm}px;
            padding: {self.spacing.padding_sm}px;
            font-family: {self.typography.ui_font_family};
            font-size: {self.typography.font_size_base}px;
            selection-background-color: {self.colors.primary_container};
            selection-color: {self.colors.on_primary_container};
        }}
        
        QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {{
            border-color: {self.colors.primary};
            background-color: {self.colors.surface_bright};
        }}
        
        QLineEdit:disabled, QTextEdit:disabled, QPlainTextEdit:disabled {{
            background-color: {self.colors.surface_dim};
            color: {self.colors.text_disabled};
            border-color: {self.colors.outline_variant};
        }}
        """
    
    def generate_code_editor_style(self) -> str:
        """Generate code editor stylesheet"""
        return f"""
        QPlainTextEdit#code_editor {{
            background-color: {self.editor_colors.background};
            color: {self.editor_colors.text};
            border: {self.spacing.border_width_normal}px solid {self.colors.outline_variant};
            border-radius: {self.spacing.border_radius_sm}px;
            font-family: {self.typography.code_font_family};
            font-size: {self.typography.font_size_base}px;
            line-height: {int(self.typography.font_size_base * self.typography.line_height_normal)}px;
            selection-background-color: {self.editor_colors.selection};
            selection-color: {self.editor_colors.text};
        }}
        
        QPlainTextEdit#code_editor:focus {{
            border-color: {self.colors.primary};
            background-color: {self.editor_colors.background_darker};
        }}
        """
    
    def generate_splitter_style(self) -> str:
        """Generate splitter stylesheet"""
        return f"""
        QSplitter::handle {{
            background-color: {self.colors.outline_variant};
        }}
        
        QSplitter::handle:vertical {{
            height: {self.spacing.border_width_thick}px;
            margin: 0 {self.spacing.margin_xs}px;
        }}
        
        QSplitter::handle:horizontal {{
            width: {self.spacing.border_width_thick}px;
            margin: {self.spacing.margin_xs}px 0;
        }}
        
        QSplitter::handle:hover {{
            background-color: {self.colors.primary};
        }}
        
        QSplitter::handle:pressed {{
            background-color: {self.colors.primary_dark};
        }}
        """
    
    def generate_console_style(self) -> str:
        """Generate console/terminal stylesheet"""
        return f"""
        QTextEdit#console {{
            background-color: {self.colors.surface_dim};
            color: {self.colors.text_primary};
            border: {self.spacing.border_width_normal}px solid {self.colors.outline_variant};
            border-radius: {self.spacing.border_radius_sm}px;
            font-family: {self.typography.code_font_family};
            font-size: {self.typography.font_size_sm}px;
            padding: {self.spacing.padding_sm}px;
        }}
        
        QTextEdit#console::selection {{
            background-color: {self.colors.primary_container};
            color: {self.colors.on_primary_container};
        }}
        """
    
    def generate_menu_style(self) -> str:
        """Generate menu stylesheet"""
        return f"""
        QMenuBar {{
            background-color: {self.colors.surface};
            color: {self.colors.text_primary};
            border-bottom: {self.spacing.border_width_normal}px solid {self.colors.outline};
            font-family: {self.typography.ui_font_family};
            font-size: {self.typography.font_size_base}px;
        }}
        
        QMenuBar::item {{
            background: transparent;
            padding: {self.spacing.padding_sm}px {self.spacing.padding_md}px;
        }}
        
        QMenuBar::item:selected {{
            background-color: {self.colors.hover};
        }}
        
        QMenuBar::item:pressed {{
            background-color: {self.colors.pressed};
        }}
        
        QMenu {{
            background-color: {self.colors.surface};
            color: {self.colors.text_primary};
            border: {self.spacing.border_width_normal}px solid {self.colors.outline};
            border-radius: {self.spacing.border_radius_sm}px;
            padding: {self.spacing.padding_xs}px;
            font-family: {self.typography.ui_font_family};
            font-size: {self.typography.font_size_base}px;
        }}
        
        QMenu::item {{
            background: transparent;
            padding: {self.spacing.padding_sm}px {self.spacing.padding_md}px;
            border-radius: {self.spacing.border_radius_sm}px;
        }}
        
        QMenu::item:selected {{
            background-color: {self.colors.hover};
        }}
        
        QMenu::separator {{
            height: {self.spacing.border_width_normal}px;
            background-color: {self.colors.outline_variant};
            margin: {self.spacing.margin_xs}px;
        }}
        """
    
    # Utility Methods
    def _add_alpha(self, hex_color: str, alpha: float) -> str:
        """Add alpha transparency to a hex color"""
        if not hex_color.startswith('#') or len(hex_color) != 7:
            return hex_color
        
        # Convert alpha (0.0-1.0) to hex (00-FF)
        alpha_hex = format(int(alpha * 255), '02X')
        return f"{hex_color}{alpha_hex}"
    
    def _darken_color(self, hex_color: str, factor: float) -> str:
        """Darken a hex color by a factor (0.0-1.0)"""
        if not hex_color.startswith('#') or len(hex_color) != 7:
            return hex_color
        
        # Extract RGB components
        r = int(hex_color[1:3], 16)
        g = int(hex_color[3:5], 16)
        b = int(hex_color[5:7], 16)
        
        # Darken by reducing each component
        r = int(r * (1 - factor))
        g = int(g * (1 - factor))
        b = int(b * (1 - factor))
        
        # Convert back to hex
        return f"#{r:02X}{g:02X}{b:02X}"
    
    def _lighten_color(self, hex_color: str, factor: float) -> str:
        """Lighten a hex color by a factor (0.0-1.0)"""
        if not hex_color.startswith('#') or len(hex_color) != 7:
            return hex_color
        
        # Extract RGB components
        r = int(hex_color[1:3], 16)
        g = int(hex_color[3:5], 16)
        b = int(hex_color[5:7], 16)
        
        # Lighten by moving towards white
        r = int(r + (255 - r) * factor)
        g = int(g + (255 - g) * factor)
        b = int(b + (255 - b) * factor)
        
        # Convert back to hex
        return f"#{r:02X}{g:02X}{b:02X}"
    
    # Complete Style Generation
    def generate_application_style(self) -> str:
        """Generate complete application stylesheet"""
        return f"""
        /* Global Application Styles */
        QWidget {{
            background-color: {self.colors.background};
            color: {self.colors.text_primary};
            font-family: {self.typography.ui_font_family};
            font-size: {self.typography.font_size_base}px;
        }}
        
        /* Component Styles */
        {self.generate_scrollbar_style()}
        {self.generate_button_style("primary")}
        {self.generate_text_input_style()}
        {self.generate_splitter_style()}
        {self.generate_menu_style()}
        """
    
    def generate_component_style(self, component_type: str, **options) -> str:
        """Generate style for a specific component type"""
        generators = {
            'scrollbar': self.generate_scrollbar_style,
            'button': lambda: self.generate_button_style(options.get('variant', 'primary')),
            'sidebar': self.generate_sidebar_style,
            'text_input': self.generate_text_input_style,
            'code_editor': self.generate_code_editor_style,
            'splitter': self.generate_splitter_style,
            'console': self.generate_console_style,
            'menu': self.generate_menu_style,
            'application': self.generate_application_style,
        }
        
        generator = generators.get(component_type)
        if not generator:
            raise ValueError(f"Unknown component type: {component_type}")
        
        return generator()
