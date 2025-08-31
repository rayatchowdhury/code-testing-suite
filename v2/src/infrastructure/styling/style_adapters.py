"""
Component Style Adapters

Adapters that apply theme-aware styling to Qt widgets using the clean
architecture pattern, separating styling logic from component logic.
"""

from typing import Any, Optional, Dict
from abc import ABC, abstractmethod

from domain.models.theme import Theme
from infrastructure.styling.style_generator import StyleGenerator


class StyleAdapter(ABC):
    """Base adapter for applying styles to Qt components"""
    
    def __init__(self, theme: Theme):
        self.theme = theme
        self.style_generator = StyleGenerator(theme)
    
    def update_theme(self, new_theme: Theme) -> None:
        """Update the theme and regenerate styles"""
        self.theme = new_theme
        self.style_generator.update_theme(new_theme)
        self.refresh_styles()
    
    @abstractmethod
    def refresh_styles(self) -> None:
        """Refresh the styles after theme change"""
        pass


class ButtonStyleAdapter(StyleAdapter):
    """Style adapter for buttons"""
    
    def __init__(self, theme: Theme, button_variant: str = "primary"):
        super().__init__(theme)
        self.variant = button_variant
        self._styled_buttons = []
    
    def style_button(self, button: Any, variant: Optional[str] = None) -> None:
        """Apply styling to a QPushButton"""
        variant = variant or self.variant
        style = self.style_generator.generate_button_style(variant)
        
        # Apply the style (Qt-specific implementation would go here)
        if hasattr(button, 'setStyleSheet'):
            button.setStyleSheet(style)
        
        # Track styled buttons for theme updates
        if button not in self._styled_buttons:
            self._styled_buttons.append(button)
    
    def refresh_styles(self) -> None:
        """Refresh all styled buttons"""
        for button in self._styled_buttons:
            if hasattr(button, 'setStyleSheet'):
                style = self.style_generator.generate_button_style(self.variant)
                button.setStyleSheet(style)


class SidebarStyleAdapter(StyleAdapter):
    """Style adapter for sidebar components"""
    
    def __init__(self, theme: Theme):
        super().__init__(theme)
        self._styled_sidebars = []
    
    def style_sidebar(self, sidebar_widget: Any) -> None:
        """Apply styling to a sidebar widget"""
        style = self.style_generator.generate_sidebar_style()
        
        if hasattr(sidebar_widget, 'setStyleSheet'):
            sidebar_widget.setStyleSheet(style)
        
        if sidebar_widget not in self._styled_sidebars:
            self._styled_sidebars.append(sidebar_widget)
    
    def refresh_styles(self) -> None:
        """Refresh all styled sidebars"""
        for sidebar in self._styled_sidebars:
            if hasattr(sidebar, 'setStyleSheet'):
                style = self.style_generator.generate_sidebar_style()
                sidebar.setStyleSheet(style)


class CodeEditorStyleAdapter(StyleAdapter):
    """Style adapter for code editor components"""
    
    def __init__(self, theme: Theme):
        super().__init__(theme)
        self._styled_editors = []
    
    def style_code_editor(self, editor_widget: Any) -> None:
        """Apply styling to a code editor widget"""
        style = self.style_generator.generate_code_editor_style()
        
        if hasattr(editor_widget, 'setStyleSheet'):
            editor_widget.setStyleSheet(style)
        
        if editor_widget not in self._styled_editors:
            self._styled_editors.append(editor_widget)
    
    def refresh_styles(self) -> None:
        """Refresh all styled code editors"""
        for editor in self._styled_editors:
            if hasattr(editor, 'setStyleSheet'):
                style = self.style_generator.generate_code_editor_style()
                editor.setStyleSheet(style)


class TextInputStyleAdapter(StyleAdapter):
    """Style adapter for text input components"""
    
    def __init__(self, theme: Theme):
        super().__init__(theme)
        self._styled_inputs = []
    
    def style_text_input(self, input_widget: Any) -> None:
        """Apply styling to text input widgets"""
        style = self.style_generator.generate_text_input_style()
        
        if hasattr(input_widget, 'setStyleSheet'):
            input_widget.setStyleSheet(style)
        
        if input_widget not in self._styled_inputs:
            self._styled_inputs.append(input_widget)
    
    def refresh_styles(self) -> None:
        """Refresh all styled text inputs"""
        for input_widget in self._styled_inputs:
            if hasattr(input_widget, 'setStyleSheet'):
                style = self.style_generator.generate_text_input_style()
                input_widget.setStyleSheet(style)


class ApplicationStyleAdapter(StyleAdapter):
    """Style adapter for application-wide styling"""
    
    def __init__(self, theme: Theme):
        super().__init__(theme)
        self._application = None
    
    def style_application(self, app: Any) -> None:
        """Apply global application styling"""
        self._application = app
        style = self.style_generator.generate_application_style()
        
        if hasattr(app, 'setStyleSheet'):
            app.setStyleSheet(style)
    
    def refresh_styles(self) -> None:
        """Refresh application-wide styles"""
        if self._application and hasattr(self._application, 'setStyleSheet'):
            style = self.style_generator.generate_application_style()
            self._application.setStyleSheet(style)


class ComponentStyleManager:
    """Manages all style adapters for a theme"""
    
    def __init__(self, theme: Theme):
        self.theme = theme
        self.adapters: Dict[str, StyleAdapter] = {
            'button': ButtonStyleAdapter(theme),
            'sidebar': SidebarStyleAdapter(theme),
            'code_editor': CodeEditorStyleAdapter(theme),
            'text_input': TextInputStyleAdapter(theme),
            'application': ApplicationStyleAdapter(theme),
        }
    
    def get_adapter(self, adapter_type: str) -> Optional[StyleAdapter]:
        """Get a specific style adapter"""
        return self.adapters.get(adapter_type)
    
    def update_theme(self, new_theme: Theme) -> None:
        """Update theme for all adapters"""
        self.theme = new_theme
        for adapter in self.adapters.values():
            adapter.update_theme(new_theme)
    
    def style_component(self, component_type: str, widget: Any, **options) -> bool:
        """Style a component using the appropriate adapter"""
        adapter = self.get_adapter(component_type)
        if not adapter:
            return False
        
        try:
            if component_type == 'button':
                variant = options.get('variant', 'primary')
                adapter.style_button(widget, variant)
            elif component_type == 'sidebar':
                adapter.style_sidebar(widget)
            elif component_type == 'code_editor':
                adapter.style_code_editor(widget)
            elif component_type == 'text_input':
                adapter.style_text_input(widget)
            elif component_type == 'application':
                adapter.style_application(widget)
            else:
                return False
            
            return True
            
        except Exception as e:
            print(f"⚠️ Failed to style {component_type}: {e}")
            return False
    
    def refresh_all_styles(self) -> None:
        """Refresh styles for all managed components"""
        for adapter in self.adapters.values():
            try:
                adapter.refresh_styles()
            except Exception as e:
                print(f"⚠️ Failed to refresh styles: {e}")


# Mock widgets for testing (when Qt is not available)
class MockWidget:
    """Mock widget for testing without Qt"""
    
    def __init__(self, name: str = "MockWidget"):
        self.name = name
        self.stylesheet = ""
        self.properties = {}
    
    def setStyleSheet(self, style: str) -> None:
        """Mock setStyleSheet method"""
        self.stylesheet = style
        print(f"📝 Applied style to {self.name} ({len(style)} chars)")
    
    def setProperty(self, name: str, value: Any) -> None:
        """Mock setProperty method"""
        self.properties[name] = value


class MockApplication:
    """Mock application for testing without Qt"""
    
    def __init__(self):
        self.stylesheet = ""
    
    def setStyleSheet(self, style: str) -> None:
        """Mock setStyleSheet method"""
        self.stylesheet = style
        print(f"🎨 Applied global application style ({len(style)} chars)")


# Factory functions for creating styled components
def create_styled_button(theme: Theme, text: str = "Button", variant: str = "primary") -> Any:
    """Factory function to create a styled button"""
    # In a real implementation, this would create a QPushButton
    button = MockWidget(f"Button({text})")
    
    adapter = ButtonStyleAdapter(theme, variant)
    adapter.style_button(button, variant)
    
    return button


def create_styled_sidebar(theme: Theme) -> Any:
    """Factory function to create a styled sidebar"""
    sidebar = MockWidget("Sidebar")
    
    adapter = SidebarStyleAdapter(theme)
    adapter.style_sidebar(sidebar)
    
    return sidebar


def create_styled_code_editor(theme: Theme) -> Any:
    """Factory function to create a styled code editor"""
    editor = MockWidget("CodeEditor")
    
    adapter = CodeEditorStyleAdapter(theme)
    adapter.style_code_editor(editor)
    
    return editor
