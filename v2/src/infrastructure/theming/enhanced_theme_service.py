"""
Enhanced Theme Service v2 - Advanced theme management

Provides comprehensive theme management including validation, 
custom themes, and dynamic switching capabilities.
"""

import json
from pathlib import Path
from typing import Dict, List, Optional, Callable, Any
from dataclasses import asdict

from domain.models.theme import Theme, ThemeType, ThemeValidationResult
from domain.models.theme.predefined_themes import (
    get_default_theme, get_theme_by_name, get_available_themes
)


class ThemeChangeEvent:
    """Event fired when theme changes"""
    
    def __init__(self, old_theme: Optional[Theme], new_theme: Theme):
        self.old_theme = old_theme
        self.new_theme = new_theme
        self.theme_name = new_theme.name
        self.theme_type = new_theme.type


class EnhancedThemeService:
    """Enhanced theme service with advanced capabilities"""
    
    def __init__(self, config_dir: Optional[Path] = None):
        self._current_theme: Theme = get_default_theme()
        self._custom_themes: Dict[str, Theme] = {}
        self._theme_change_listeners: List[Callable[[ThemeChangeEvent], None]] = []
        
        # Configuration
        self._config_dir = config_dir or Path.home() / '.code_editor' / 'themes'
        self._ensure_config_dir()
        
        # Load custom themes
        self._load_custom_themes()
    
    def _ensure_config_dir(self) -> None:
        """Ensure theme configuration directory exists"""
        self._config_dir.mkdir(parents=True, exist_ok=True)
    
    def _load_custom_themes(self) -> None:
        """Load custom themes from configuration directory"""
        theme_files = self._config_dir.glob('*.json')
        
        for theme_file in theme_files:
            try:
                theme = self._load_theme_from_file(theme_file)
                self._custom_themes[theme.name.lower()] = theme
            except Exception as e:
                print(f"⚠️ Failed to load theme from {theme_file}: {e}")
    
    def _load_theme_from_file(self, file_path: Path) -> Theme:
        """Load a theme from a JSON file"""
        with open(file_path, 'r', encoding='utf-8') as f:
            theme_data = json.load(f)
        
        # TODO: Implement proper theme deserialization
        # For now, this is a placeholder
        raise NotImplementedError("Custom theme loading will be implemented in next iteration")
    
    # Theme Management
    def get_current_theme(self) -> Theme:
        """Get the currently active theme"""
        return self._current_theme
    
    def set_theme(self, theme_name: str) -> bool:
        """Set the active theme by name"""
        try:
            # Try built-in themes first
            if theme_name.lower() in get_available_themes():
                new_theme = get_theme_by_name(theme_name)
            # Then try custom themes
            elif theme_name.lower() in self._custom_themes:
                new_theme = self._custom_themes[theme_name.lower()]
            else:
                raise ValueError(f"Theme not found: {theme_name}")
            
            return self._apply_theme(new_theme)
            
        except Exception as e:
            print(f"❌ Failed to set theme '{theme_name}': {e}")
            return False
    
    def set_theme_by_type(self, theme_type: ThemeType) -> bool:
        """Set theme by type (finds first matching built-in theme)"""
        for theme in get_available_themes().values():
            if theme.type == theme_type:
                return self._apply_theme(theme)
        
        print(f"❌ No built-in theme found for type: {theme_type}")
        return False
    
    def _apply_theme(self, new_theme: Theme) -> bool:
        """Apply a new theme and notify listeners"""
        old_theme = self._current_theme
        self._current_theme = new_theme
        
        # Notify listeners
        event = ThemeChangeEvent(old_theme, new_theme)
        for listener in self._theme_change_listeners:
            try:
                listener(event)
            except Exception as e:
                print(f"⚠️ Theme change listener error: {e}")
        
        print(f"✅ Applied theme: {new_theme.name}")
        return True
    
    # Theme Discovery
    def get_available_theme_names(self) -> List[str]:
        """Get names of all available themes (built-in + custom)"""
        built_in = list(get_available_themes().keys())
        custom = list(self._custom_themes.keys())
        return built_in + custom
    
    def get_themes_by_type(self, theme_type: ThemeType) -> List[Theme]:
        """Get all themes of a specific type"""
        themes = []
        
        # Built-in themes
        for theme in get_available_themes().values():
            if theme.type == theme_type:
                themes.append(theme)
        
        # Custom themes
        for theme in self._custom_themes.values():
            if theme.type == theme_type:
                themes.append(theme)
        
        return themes
    
    def get_theme_info(self, theme_name: str) -> Optional[Theme]:
        """Get detailed information about a theme"""
        theme_name_lower = theme_name.lower()
        
        # Check built-in themes
        if theme_name_lower in get_available_themes():
            return get_theme_by_name(theme_name)
        
        # Check custom themes
        if theme_name_lower in self._custom_themes:
            return self._custom_themes[theme_name_lower]
        
        return None
    
    # Custom Theme Management
    def create_custom_theme(self, theme: Theme) -> bool:
        """Create and save a custom theme"""
        try:
            validation = self.validate_theme(theme)
            if not validation.is_valid:
                print(f"❌ Theme validation failed: {validation.errors}")
                return False
            
            # Save to custom themes
            self._custom_themes[theme.name.lower()] = theme
            
            # Persist to file
            theme_file = self._config_dir / f"{theme.name.lower().replace(' ', '_')}.json"
            self._save_theme_to_file(theme, theme_file)
            
            print(f"✅ Created custom theme: {theme.name}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to create custom theme: {e}")
            return False
    
    def _save_theme_to_file(self, theme: Theme, file_path: Path) -> None:
        """Save a theme to a JSON file"""
        theme_data = asdict(theme)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(theme_data, f, indent=2, ensure_ascii=False)
    
    def delete_custom_theme(self, theme_name: str) -> bool:
        """Delete a custom theme"""
        theme_name_lower = theme_name.lower()
        
        if theme_name_lower not in self._custom_themes:
            print(f"❌ Custom theme not found: {theme_name}")
            return False
        
        try:
            # Remove from memory
            del self._custom_themes[theme_name_lower]
            
            # Remove file
            theme_file = self._config_dir / f"{theme_name_lower.replace(' ', '_')}.json"
            if theme_file.exists():
                theme_file.unlink()
            
            print(f"✅ Deleted custom theme: {theme_name}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to delete custom theme: {e}")
            return False
    
    # Theme Validation
    def validate_theme(self, theme: Theme) -> ThemeValidationResult:
        """Validate a theme for completeness and correctness"""
        errors = []
        warnings = []
        
        # Basic validation
        if not theme.name:
            errors.append("Theme name is required")
        
        if not theme.version:
            errors.append("Theme version is required")
        
        # Color validation (basic hex color check)
        color_fields = [
            'primary', 'secondary', 'background', 'surface', 'text_primary'
        ]
        
        for field in color_fields:
            color = getattr(theme.colors, field, None)
            if color and not self._is_valid_hex_color(color):
                errors.append(f"Invalid hex color for {field}: {color}")
        
        # Typography validation
        if theme.typography.font_size_base <= 0:
            errors.append("Base font size must be positive")
        
        if theme.typography.line_height_normal <= 0:
            errors.append("Line height must be positive")
        
        # Spacing validation
        if theme.spacing.unit <= 0:
            errors.append("Spacing unit must be positive")
        
        # Warnings for best practices
        if len(theme.name) > 50:
            warnings.append("Theme name is quite long")
        
        if not theme.description:
            warnings.append("Theme description is recommended")
        
        return ThemeValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings
        )
    
    def _is_valid_hex_color(self, color: str) -> bool:
        """Check if a string is a valid hex color"""
        if not color.startswith('#'):
            return False
        
        hex_part = color[1:]
        if len(hex_part) not in [3, 6]:
            return False
        
        try:
            int(hex_part, 16)
            return True
        except ValueError:
            return False
    
    # Event System
    def add_theme_change_listener(self, listener: Callable[[ThemeChangeEvent], None]) -> None:
        """Add a listener for theme change events"""
        self._theme_change_listeners.append(listener)
    
    def remove_theme_change_listener(self, listener: Callable[[ThemeChangeEvent], None]) -> None:
        """Remove a theme change listener"""
        if listener in self._theme_change_listeners:
            self._theme_change_listeners.remove(listener)
    
    # Utility Methods
    def get_color(self, color_name: str) -> Optional[str]:
        """Get a color value from the current theme"""
        colors = self._current_theme.colors
        return getattr(colors, color_name, None)
    
    def get_editor_color(self, color_name: str) -> Optional[str]:
        """Get an editor color value from the current theme"""
        editor_colors = self._current_theme.editor_colors
        return getattr(editor_colors, color_name, None)
    
    def get_font_family(self, font_type: str = 'ui') -> str:
        """Get font family (ui or code)"""
        typography = self._current_theme.typography
        if font_type == 'code':
            return typography.code_font_family
        return typography.ui_font_family
    
    def get_font_size(self, size_name: str) -> int:
        """Get font size by name (xs, sm, base, lg, xl, xxl)"""
        typography = self._current_theme.typography
        return getattr(typography, f'font_size_{size_name}', typography.font_size_base)
    
    def get_spacing(self, spacing_name: str) -> int:
        """Get spacing value by name"""
        spacing = self._current_theme.spacing
        return getattr(spacing, spacing_name, spacing.unit)
    
    # Configuration
    def export_current_theme(self, file_path: Path) -> bool:
        """Export the current theme to a file"""
        try:
            self._save_theme_to_file(self._current_theme, file_path)
            print(f"✅ Exported theme to: {file_path}")
            return True
        except Exception as e:
            print(f"❌ Failed to export theme: {e}")
            return False
    
    def get_theme_stats(self) -> Dict[str, Any]:
        """Get statistics about available themes"""
        built_in_themes = get_available_themes()
        custom_themes = self._custom_themes
        
        type_counts = {}
        for theme in {**built_in_themes, **custom_themes}.values():
            type_name = theme.type.value
            type_counts[type_name] = type_counts.get(type_name, 0) + 1
        
        return {
            'total_themes': len(built_in_themes) + len(custom_themes),
            'built_in_themes': len(built_in_themes),
            'custom_themes': len(custom_themes),
            'current_theme': self._current_theme.name,
            'themes_by_type': type_counts,
            'config_directory': str(self._config_dir)
        }
