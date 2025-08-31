"""
Comprehensive Styling Service

Integrates theme management with component styling, providing a unified
interface for applying themes to the entire application.
"""

from typing import Any, Dict, List, Optional, Callable
from domain.models.theme import Theme
from infrastructure.theming.enhanced_theme_service import EnhancedThemeService, ThemeChangeEvent
from infrastructure.styling.style_adapters import ComponentStyleManager


class StylingService:
    """Unified service for theme-aware application styling"""
    
    def __init__(self, theme_service: EnhancedThemeService):
        self.theme_service = theme_service
        self.style_manager = ComponentStyleManager(theme_service.get_current_theme())
        
        # Track styled applications for global updates
        self._styled_applications: List[Any] = []
        
        # Listen for theme changes
        self.theme_service.add_theme_change_listener(self._on_theme_changed)
    
    def _on_theme_changed(self, event: ThemeChangeEvent) -> None:
        """Handle theme change events"""
        print(f"🎨 Theme changed from '{event.old_theme.name if event.old_theme else 'None'}' to '{event.new_theme.name}'")
        
        # Update style manager with new theme
        self.style_manager.update_theme(event.new_theme)
        
        # Refresh all application styles
        self._refresh_application_styles()
    
    def _refresh_application_styles(self) -> None:
        """Refresh styles for all styled applications"""
        for app in self._styled_applications:
            try:
                self.style_manager.style_component('application', app)
            except Exception as e:
                print(f"⚠️ Failed to refresh application styles: {e}")
    
    # Application-level styling
    def style_application(self, app: Any) -> bool:
        """Apply theme to entire application"""
        success = self.style_manager.style_component('application', app)
        
        if success and app not in self._styled_applications:
            self._styled_applications.append(app)
        
        return success
    
    # Component styling methods
    def style_button(self, button: Any, variant: str = "primary") -> bool:
        """Style a button with current theme"""
        return self.style_manager.style_component('button', button, variant=variant)
    
    def style_sidebar(self, sidebar: Any) -> bool:
        """Style a sidebar with current theme"""
        return self.style_manager.style_component('sidebar', sidebar)
    
    def style_code_editor(self, editor: Any) -> bool:
        """Style a code editor with current theme"""
        return self.style_manager.style_component('code_editor', editor)
    
    def style_text_input(self, input_widget: Any) -> bool:
        """Style a text input with current theme"""
        return self.style_manager.style_component('text_input', input_widget)
    
    # Batch styling
    def style_multiple_components(self, components: List[Dict[str, Any]]) -> Dict[str, bool]:
        """Style multiple components at once
        
        Args:
            components: List of dicts with 'type', 'widget', and optional 'options' keys
            
        Returns:
            Dict mapping component types to success status
        """
        results = {}
        
        for component in components:
            component_type = component.get('type')
            widget = component.get('widget')
            options = component.get('options', {})
            
            if not component_type or not widget:
                results[f"invalid_{len(results)}"] = False
                continue
            
            success = self.style_manager.style_component(component_type, widget, **options)
            results[component_type] = success
        
        return results
    
    # Theme management integration
    def set_theme(self, theme_name: str) -> bool:
        """Set application theme by name"""
        return self.theme_service.set_theme(theme_name)
    
    def get_current_theme(self) -> Theme:
        """Get current theme"""
        return self.theme_service.get_current_theme()
    
    def get_available_themes(self) -> List[str]:
        """Get available theme names"""
        return self.theme_service.get_available_theme_names()
    
    # Style generation utilities
    def get_style_for_component(self, component_type: str, **options) -> Optional[str]:
        """Get stylesheet string for a component type"""
        try:
            generator = self.style_manager.get_adapter(component_type)
            if not generator:
                return None
            
            return generator.style_generator.generate_component_style(component_type, **options)
            
        except Exception as e:
            print(f"⚠️ Failed to generate style for {component_type}: {e}")
            return None
    
    def get_color_from_theme(self, color_name: str) -> Optional[str]:
        """Get a color value from current theme"""
        return self.theme_service.get_color(color_name)
    
    def get_font_from_theme(self, font_type: str = 'ui') -> str:
        """Get font family from current theme"""
        return self.theme_service.get_font_family(font_type)
    
    # Debugging and introspection
    def get_styling_stats(self) -> Dict[str, Any]:
        """Get statistics about styled components"""
        theme_stats = self.theme_service.get_theme_stats()
        
        adapter_counts = {}
        for adapter_type, adapter in self.style_manager.adapters.items():
            if hasattr(adapter, '_styled_buttons'):
                adapter_counts[f"{adapter_type}_count"] = len(adapter._styled_buttons)
            elif hasattr(adapter, '_styled_sidebars'):
                adapter_counts[f"{adapter_type}_count"] = len(adapter._styled_sidebars)
            elif hasattr(adapter, '_styled_editors'):
                adapter_counts[f"{adapter_type}_count"] = len(adapter._styled_editors)
            elif hasattr(adapter, '_styled_inputs'):
                adapter_counts[f"{adapter_type}_count"] = len(adapter._styled_inputs)
        
        return {
            'current_theme': theme_stats['current_theme'],
            'total_themes': theme_stats['total_themes'],
            'styled_applications': len(self._styled_applications),
            'adapters': list(self.style_manager.adapters.keys()),
            'component_counts': adapter_counts
        }
    
    def export_current_theme_styles(self) -> Dict[str, str]:
        """Export all component styles for current theme"""
        styles = {}
        
        for component_type in self.style_manager.adapters.keys():
            try:
                style = self.get_style_for_component(component_type)
                if style:
                    styles[component_type] = style
            except Exception as e:
                print(f"⚠️ Failed to export style for {component_type}: {e}")
        
        return styles
    
    # Cleanup
    def cleanup(self) -> None:
        """Clean up resources and listeners"""
        try:
            self.theme_service.remove_theme_change_listener(self._on_theme_changed)
        except:
            pass  # Listener might not be registered
        
        self._styled_applications.clear()


# Convenience factory for creating a complete styling system
def create_styling_system(config_dir: Optional[str] = None) -> StylingService:
    """Create a complete styling system with theme and style services"""
    from pathlib import Path
    
    config_path = Path(config_dir) if config_dir else None
    theme_service = EnhancedThemeService(config_path)
    styling_service = StylingService(theme_service)
    
    return styling_service
