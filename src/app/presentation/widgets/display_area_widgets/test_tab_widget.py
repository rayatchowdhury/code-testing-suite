# -*- coding: utf-8 -*-
"""
TestTabWidget - Reusable tab widget for test windows.

This widget provides a consistent tab interface for switching between different
code files in test windows (Comparator, Validator, Benchmarker).
"""

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                              QMessageBox, QLabel, QMenu, QSpacerItem, QSizePolicy)
from PySide6.QtCore import Qt, Signal, QPoint
from PySide6.QtGui import QCursor
import os

from src.app.presentation.styles.components.test_view_styles import (
    TEST_VIEW_BUTTON_PANEL_STYLE,
    TEST_VIEW_FILE_BUTTON_STYLE,
    TEST_VIEW_CONTENT_PANEL_STYLE
)
from src.app.shared.constants import WORKSPACE_DIR
from src.app.shared.constants.paths import get_workspace_file_path
from src.app.shared.utils.workspace_utils import ensure_test_type_directory
from src.app.shared.utils.tab_code_templates import TabCodeTemplates
from src.app.presentation.styles.constants import MATERIAL_COLORS


class TestTabWidget(QWidget):
    """
    Reusable tab widget for test windows.
    
    Provides file switching functionality with unsaved changes detection,
    visual tab states, and customizable tab configurations.
    """
    
    # Signals
    fileChanged = Signal(str)  # Emitted when switching to a different file
    tabClicked = Signal(str)   # Emitted when any tab is clicked
    languageChanged = Signal(str, str)  # Emitted when language changes (tab_name, language)
    filesManifestChanged = Signal()  # Emitted when file manifest changes (for compilation)
    
    def __init__(self, parent=None, tab_config=None, default_tab=None, multi_language=False, default_language='cpp', test_type='comparator'):
        """
        Initialize TestTabWidget.
        
        Args:
            parent: Parent widget
            tab_config: Dict mapping tab names to file names (legacy) or language configs
            default_tab: Name of the tab to activate by default
            multi_language: Enable multi-language support
            default_language: Default language for new tabs ('cpp', 'py', 'java')
            test_type: Type of test (comparator/validator/benchmarker) for nested file paths
        """
        super().__init__(parent)
        
        # Configuration
        self.tab_config = tab_config or {}
        self.default_tab = default_tab
        self.workspace_dir = WORKSPACE_DIR
        self.multi_language = multi_language
        self.available_languages = ['cpp', 'py', 'java']
        self.default_language = default_language
        self.test_type = test_type  # Store test type for nested file paths
        
        # Multi-language state management
        if multi_language:
            self.current_language_per_tab = {}  # tab_name -> current_language
            self.unsaved_changes_per_tab = {}   # tab_name -> {language: bool}
            # Convert legacy config to multi-language format if needed
            self._ensure_multi_language_config()
        
        # State management
        self.file_buttons = {}
        self.current_button = None
        self._content_widget = None
        
        self._setup_ui()
        # Ensure nested workspace structure exists for this test type
        if self.workspace_dir:
            ensure_test_type_directory(self.workspace_dir, self.test_type)
        
    def _ensure_multi_language_config(self):
        """Convert legacy config to multi-language format if needed."""
        for tab_name, config in self.tab_config.items():
            if isinstance(config, str):
                # Legacy format: convert single file to language dict
                extension = config.split('.')[-1]
                base_name = config.rsplit('.', 1)[0]
                
                # Create consistent naming for all languages
                if tab_name == 'Generator':
                    self.tab_config[tab_name] = {
                        'cpp': 'generator.cpp',
                        'py': 'generator.py', 
                        'java': 'Generator.java'  # Capital for Java class
                    }
                elif tab_name == 'Test Code':
                    self.tab_config[tab_name] = {
                        'cpp': 'test.cpp',
                        'py': 'test.py',
                        'java': 'Test.java'  # Consistent naming
                    }
                elif tab_name == 'Correct Code':
                    self.tab_config[tab_name] = {
                        'cpp': 'correct.cpp',
                        'py': 'correct.py',
                        'java': 'Correct.java'  # Consistent naming
                    }
                elif tab_name == 'Validator Code':
                    self.tab_config[tab_name] = {
                        'cpp': 'validator.cpp',
                        'py': 'validator.py',
                        'java': 'Validator.java'  # Consistent naming
                    }
                else:
                    # Generic fallback
                    clean_name = base_name.replace(' ', '').lower()
                    self.tab_config[tab_name] = {
                        'cpp': f"{clean_name}.cpp",
                        'py': f"{clean_name}.py",
                        'java': f"{clean_name.title()}.java"
                    }
            
            # Initialize current language and unsaved state
            self.current_language_per_tab[tab_name] = self.default_language
            self.unsaved_changes_per_tab[tab_name] = {lang: False for lang in self.available_languages}
        
    def _setup_ui(self):
        """Setup the tab widget UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Create button panel with background
        button_panel = QWidget()
        # button_panel.setMinimumHeight(40)  # Set minimum height for button panel
        button_panel.setStyleSheet(TEST_VIEW_BUTTON_PANEL_STYLE)
        button_layout = QHBoxLayout(button_panel)
        button_layout.setContentsMargins(8, 8, 8, 8)  # Reduced padding for edge-to-edge
        button_layout.setSpacing(7)  # Reduced spacing for better space utilization
        
        # Create tab buttons
        for tab_name in self.tab_config.keys():
            if self.multi_language:
                # Create custom tab widget with responsive design
                tab_widget = QWidget()
                # tab_widget.setMinimumWidth(140)  # Reduced minimum width for better fitting
                # tab_widget.setMaximumHeight(48)  # Control height
                tab_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)  # Allow horizontal expansion
                tab_widget.setStyleSheet(f"""
                    QWidget {{
                        border: 1px solid {MATERIAL_COLORS['outline_variant']};
                        border-radius: 8px;
                        background: {MATERIAL_COLORS['surface_variant']};
                        margin: 1px 0 1px 1px;
                    }}
                    QWidget:hover {{
                        border-color: {MATERIAL_COLORS['outline']};
                        background: {MATERIAL_COLORS['surface_bright']};
                    }}
                    QWidget[hasUnsavedChanges="true"] {{
                        border: 2px solid {MATERIAL_COLORS['error']} !important;
                        margin: 1px 0 1px 1px;
                    }}
                """)
                
                tab_layout = QHBoxLayout(tab_widget)
                tab_layout.setContentsMargins(2, 2, 2, 2)
                tab_layout.setSpacing(0)
                
                # Main button (flexible width with minimum)
                btn = QPushButton(tab_name)
                btn.setMinimumHeight(35)
                # btn.setMinimumWidth(90)  # Reduced minimum for narrower windows
                btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)  # Allow expansion
                btn.clicked.connect(lambda checked, name=tab_name: self._handle_tab_click(name))
                
                # Modern button styling with connected design (no right border-radius for seamless connection)
                btn.setStyleSheet(f"""
                    QPushButton {{
                        border: none;
                        border-radius: 6px;
                        border-top-right-radius: 0;
                        border-bottom-right-radius: 0;
                        background: transparent;
                        color: {MATERIAL_COLORS['on_surface']};
                        font-size: 13px;
                        font-weight: 500;
                        text-align: center;
                    }}
                    QPushButton:hover {{
                        background: rgba(255, 255, 255, 0.08);
                    }}
                    QPushButton:pressed {{
                        background: rgba(255, 255, 255, 0.12);
                    }}
                    QPushButton[isActive="true"] {{
                        background: {MATERIAL_COLORS['primary_container']};
                        color: {MATERIAL_COLORS['on_primary_container']};
                        font-weight: 600;
                    }}
                    QPushButton[isActive="true"]:hover {{
                        background: {MATERIAL_COLORS['primary']};
                        color: {MATERIAL_COLORS['on_primary']};
                    }}
                    QPushButton[hasUnsavedChanges="true"] {{
                        border: 2px solid {MATERIAL_COLORS['error']} !important;
                        border-radius: 6px;
                        border-top-right-radius: 0;
                        border-bottom-right-radius: 0;
                        padding: 6px 6px;
                        padding-right: 0px;
                    }}
                """)
                
                # Language selector container with fixed width to prevent collision
                lang_container = QWidget()
                lang_container.setFixedWidth(45)  # Slightly smaller fixed width
                lang_container.setStyleSheet(f"""
                    QWidget {{
                        border: none;
                        border-left: 1px solid {MATERIAL_COLORS['outline_variant']};
                        border-radius: 0;
                        border-top-right-radius: 6px;
                        border-bottom-right-radius: 6px;
                        background: {MATERIAL_COLORS['surface_dim']};
                        min-width: 45px;
                        max-width: 45px;
                    }}
                    QWidget:hover {{
                        background: {MATERIAL_COLORS['surface_bright']};
                        border-left-color: {MATERIAL_COLORS['outline']};
                    }}
                """)
                
                lang_layout = QVBoxLayout(lang_container)
                lang_layout.setContentsMargins(2, 4, 2, 4)
                lang_layout.setAlignment(Qt.AlignCenter)
                
                current_lang = self.current_language_per_tab[tab_name]
                lang_label = QLabel(current_lang.upper())
                lang_label.setAlignment(Qt.AlignCenter)
                lang_label.setStyleSheet(f"""
                    QLabel {{
                        color: {MATERIAL_COLORS['text_secondary']};
                        font-size: 9px;
                        font-weight: 600;
                        padding: 4px 1px;
                        background: transparent;
                        border: none;
                        border-radius: 3px;
                    }}
                    QLabel:hover {{
                        color: {MATERIAL_COLORS['primary']};
                        background: rgba(0, 150, 199, 0.1);
                    }}
                """)
                lang_label.mousePressEvent = lambda event, tab=tab_name: self._show_language_menu(event, tab)
                lang_label.setCursor(QCursor(Qt.PointingHandCursor))
                lang_label.setToolTip(f"Click to change language for {tab_name}")
                
                lang_layout.addWidget(lang_label)
                
                # Add widgets to tab layout - button expands, language selector fixed
                tab_layout.addWidget(btn, 1)  # Button gets all available space
                tab_layout.addWidget(lang_container, 0)  # Language selector fixed width
                
                # Store references
                self.file_buttons[tab_name] = btn
                setattr(btn, 'language_label', lang_label)
                setattr(btn, 'tab_container', tab_widget)
                tab_widget.setProperty("hasUnsavedChanges", False)
                
                # Add tab widget to layout with equal stretch
                button_layout.addWidget(tab_widget, 1)  # Each tab gets equal space
            else:
                # Legacy single-language button with stretching support
                btn = QPushButton(tab_name)
                # btn.setMinimumHeight(40)
                # btn.setMinimumWidth(100)  # Reduced minimum width
                btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)  # Allow expansion
                btn.clicked.connect(lambda checked, name=tab_name: self._handle_tab_click(name))
                
                # Apply consistent Material Design styling for single-language buttons
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background-color: {MATERIAL_COLORS['surface_variant']};
                        border: 1px solid {MATERIAL_COLORS['outline_variant']};
                        border-radius: 8px;
                        color: {MATERIAL_COLORS['on_surface']};
                        padding: 8px 12px;
                        font-weight: 500;
                        font-size: 13px;
                    }}
                    QPushButton:hover {{
                        background-color: {MATERIAL_COLORS['surface_bright']};
                        border-color: {MATERIAL_COLORS['outline']};
                    }}
                    QPushButton[isActive="true"] {{
                        background-color: {MATERIAL_COLORS['primary_container']};
                        border: 2px solid {MATERIAL_COLORS['primary']};
                        color: {MATERIAL_COLORS['on_primary_container']};
                        font-weight: 600;
                        padding: 7px 11px;
                    }}
                    QPushButton[isActive="true"]:hover {{
                        background-color: {MATERIAL_COLORS['primary']};
                        color: {MATERIAL_COLORS['on_primary']};
                    }}
                    QPushButton[hasUnsavedChanges="true"] {{
                        border: 2px solid {MATERIAL_COLORS['error']} !important;
                        padding: 7px 11px;
                    }}
                """)
                
                self.file_buttons[tab_name] = btn
                # Add with equal stretch for edge-to-edge layout
                button_layout.addWidget(btn, 1)  # Each button gets equal space
            
            # Set properties for state management
            btn.setProperty("isActive", False)
            btn.setProperty("hasUnsavedChanges", False)
        
        # Create content panel
        self.content_panel = QWidget()
        self.content_panel.setStyleSheet(TEST_VIEW_CONTENT_PANEL_STYLE)
        self.content_layout = QVBoxLayout(self.content_panel)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setSpacing(0)
        
        # Add panels to main layout
        layout.addWidget(button_panel)
        layout.addWidget(self.content_panel)
        
    def set_content_widget(self, widget):
        """Set the content widget that will be displayed below the tabs."""
        # Clear existing content
        if self._content_widget:
            self.content_layout.removeWidget(self._content_widget)
            
        self._content_widget = widget
        if widget:
            self.content_layout.addWidget(widget)
    
    def get_content_widget(self):
        """Get the current content widget."""
        return self._content_widget
    
    def _show_language_menu(self, event, tab_name):
        """Show language selection menu when language indicator is clicked."""
        if not self.multi_language:
            return
            
        menu = QMenu()
        menu.setStyleSheet(f"""
            QMenu {{
                background-color: {MATERIAL_COLORS['surface']};
                border: 1px solid {MATERIAL_COLORS['outline']};
                border-radius: 8px;
                padding: 8px 0px;
                min-width: 100px;
            }}
            QMenu::item {{
                background-color: transparent;
                padding: 10px 16px;
                margin: 2px 6px;
                border-radius: 6px;
                color: {MATERIAL_COLORS['on_surface']};
                font-size: 12px;
                font-weight: 500;
                min-height: 20px;
            }}
            QMenu::item:selected {{
                background-color: {MATERIAL_COLORS['primary_container']};
                color: {MATERIAL_COLORS['on_primary_container']};
            }}
            QMenu::item:checked {{
                background-color: {MATERIAL_COLORS['primary']};
                color: {MATERIAL_COLORS['on_primary']};
                font-weight: 600;
            }}
            QMenu::separator {{
                height: 1px;
                background-color: {MATERIAL_COLORS['outline_variant']};
                margin: 6px 12px;
            }}
        """)
        
        current_lang = self.current_language_per_tab.get(tab_name)
        
        for lang in self.available_languages:
            action = menu.addAction(f"{lang.upper()}")
            action.setCheckable(True)
            action.setChecked(lang == current_lang)
            action.triggered.connect(
                lambda checked, language=lang: self._handle_language_change(tab_name, language)
            )
        
        # Show menu at cursor position
        menu.exec(QCursor.pos())
    
    def _handle_language_change(self, tab_name, new_language):
        """Handle language dropdown selection change."""
        if not self.multi_language:
            return
            
        old_language = self.current_language_per_tab.get(tab_name)
        
        # Check for unsaved changes in current language
        if (old_language and 
            old_language != new_language and 
            self.unsaved_changes_per_tab[tab_name].get(old_language, False)):
            
            reply = QMessageBox.question(
                self, "Unsaved Changes",
                f"Save changes to {tab_name} ({old_language.upper()}) before switching to {new_language.upper()}?",
                QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel
            )
            
            if reply == QMessageBox.Save:
                self.tabClicked.emit("save_current")
                # Note: Parent should handle saving and call this method again
                return
            elif reply == QMessageBox.Cancel:
                return
        
        # Update current language
        self.current_language_per_tab[tab_name] = new_language
        
        # Update language indicator
        self._update_tab_language_indicator(tab_name, new_language)
        
        # If this tab is currently active, switch to new language file
        button = self.file_buttons[tab_name]
        if button == self.current_button:
            file_path = self._get_current_file_path(tab_name, new_language)
            
            # Create file if it doesn't exist
            if not os.path.exists(file_path):
                default_content = self._get_default_content(tab_name, new_language)
                os.makedirs(os.path.dirname(file_path), exist_ok=True)
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(default_content)
                print(f"  → Created new {new_language.upper()} file: {os.path.basename(file_path)}")
            
            # Emit signals to reload file content
            self.fileChanged.emit(file_path)
            self.languageChanged.emit(tab_name, new_language)
        
        # Notify that file manifest has changed (for recompilation)
        self.filesManifestChanged.emit()
    
    def _update_tab_language_indicator(self, tab_name, language):
        """Update the language indicator label for a tab."""
        button = self.file_buttons[tab_name]
        if hasattr(button, 'language_label'):
            button.language_label.setText(language.upper())
        
    def _get_current_file_path(self, tab_name, language=None):
        """Get file path for specific tab and language using nested structure."""
        if self.multi_language:
            if language is None:
                language = self.current_language_per_tab.get(tab_name, self.default_language)
            file_name = self.tab_config[tab_name][language]
        else:
            file_name = self.tab_config[tab_name]
        
        # Use nested workspace structure (e.g., workspace/comparator/generator.cpp)
        return get_workspace_file_path(self.workspace_dir, self.test_type, file_name)
        
    def _handle_tab_click(self, tab_name, skip_save_prompt=False):
        """Handle tab button clicks and switch between files."""
        # Check if current file has unsaved changes (unless skipping prompt)
        if not skip_save_prompt and self.current_button:
            if self.multi_language:
                # Check unsaved changes for current language
                current_tab_name = self._get_original_tab_name()
                current_lang = self.current_language_per_tab.get(current_tab_name, self.default_language)
                has_changes = self.unsaved_changes_per_tab.get(current_tab_name, {}).get(current_lang, False)
            else:
                has_changes = self.current_button.property("hasUnsavedChanges")
                
            if has_changes:
                reply = QMessageBox.question(
                    self, 
                    "Unsaved Changes",
                    f"Do you want to save changes to {current_tab_name if self.multi_language else self.current_button.text()}?",
                    QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel
                )
                
                if reply == QMessageBox.Save:
                    # Emit signal for parent to handle saving
                    self.tabClicked.emit("save_current")
                    # Note: Parent should call this method again with skip_save_prompt=True after saving
                    return
                elif reply == QMessageBox.Cancel:
                    return
        
        # Update button states
        if self.current_button:
            self.current_button.setProperty("isActive", False)
            if not self.multi_language:
                self.current_button.setProperty("hasUnsavedChanges", False)
            self.current_button.style().polish(self.current_button)
            
            # Update container styling if multi-language
            if self.multi_language and hasattr(self.current_button, 'tab_container'):
                old_tab_name = self._get_original_tab_name()
                container = self.current_button.tab_container
                current_style = container.styleSheet()
                
                # Check if old tab has unsaved changes
                has_unsaved = self.unsaved_changes_per_tab.get(old_tab_name, {}).get(
                    self.current_language_per_tab.get(old_tab_name, self.default_language), False
                )
                
                if has_unsaved:
                    # Inactive tab with unsaved changes - keep error border but thinner
                    new_style = current_style.replace(
                        f"border: 2px solid {MATERIAL_COLORS['primary']};",
                        f"border: 2px solid {MATERIAL_COLORS['error']};"
                    )
                    new_style = new_style.replace(
                        f"border: 2px solid {MATERIAL_COLORS['error']};",
                        f"border: 2px solid {MATERIAL_COLORS['error']};"
                    )  # Keep error color
                else:
                    # Inactive tab without unsaved changes - normal border
                    new_style = current_style.replace(
                        f"border: 2px solid {MATERIAL_COLORS['primary']};",
                        f"border: 1px solid {MATERIAL_COLORS['outline_variant']};"
                    )
                    new_style = new_style.replace(
                        f"border: 2px solid {MATERIAL_COLORS['error']};",
                        f"border: 1px solid {MATERIAL_COLORS['outline_variant']};"
                    )
                
                container.setStyleSheet(new_style)
        
        # Set new active button
        new_button = self.file_buttons[tab_name]
        new_button.setProperty("isActive", True)
        new_button.style().polish(new_button)
        self.current_button = new_button
        
        # Update container styling for active state
        if self.multi_language and hasattr(new_button, 'tab_container'):
            container = new_button.tab_container
            current_style = container.styleSheet()
            
            # Check if this tab has unsaved changes
            has_unsaved = self.unsaved_changes_per_tab.get(tab_name, {}).get(
                self.current_language_per_tab.get(tab_name, self.default_language), False
            )
            
            if has_unsaved:
                # Active tab with unsaved changes - error border
                new_style = current_style.replace(
                    f"border: 1px solid {MATERIAL_COLORS['outline_variant']};",
                    f"border: 2px solid {MATERIAL_COLORS['error']};"
                )
            else:
                # Active tab without unsaved changes - primary border
                new_style = current_style.replace(
                    f"border: 1px solid {MATERIAL_COLORS['outline_variant']};",
                    f"border: 2px solid {MATERIAL_COLORS['primary']};"
                )
            
            container.setStyleSheet(new_style)
        
        # Get file path
        if self.multi_language:
            current_lang = self.current_language_per_tab.get(tab_name, self.default_language)
            file_path = self._get_current_file_path(tab_name, current_lang)
        else:
            file_name = self.tab_config[tab_name]
            file_path = os.path.join(self.workspace_dir, file_name)
        
        # Create file if it doesn't exist with appropriate content
        if not os.path.exists(file_path):
            if self.multi_language:
                default_content = self._get_default_content(tab_name, current_lang)
            else:
                default_content = self._get_default_content(tab_name)
            
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(default_content)
        
        # Emit signals
        self.fileChanged.emit(file_path)
        self.tabClicked.emit(tab_name)
        
    def _get_default_content(self, tab_name, language='cpp'):
        """
        Get default template content for a tab in specified language.
        Uses centralized TabCodeTemplates for consistency.
        """
        try:
            return TabCodeTemplates.get_template(tab_name, language)
        except Exception as e:
            print(f"Error getting template for {tab_name} ({language}): {e}")
            # Fallback to basic template
            if language == 'cpp':
                return '#include <iostream>\nusing namespace std;\n\nint main() {\n    // Your code here\n    return 0;\n}'
            elif language == 'py':
                return 'def main():\n    # Your code here\n    pass\n\nif __name__ == "__main__":\n    main()\n'
            elif language == 'java':
                class_name = tab_name.replace(' ', '') if tab_name else 'Main'
                return f'public class {class_name} {{\n    public static void main(String[] args) {{\n        // Your code here\n    }}\n}}'
            else:
                return '// Your code here\n'
    
    def activate_tab(self, tab_name, skip_save_prompt=False):
        """Programmatically activate a tab."""
        if tab_name in self.file_buttons:
            self._handle_tab_click(tab_name, skip_save_prompt)
    
    def activate_default_tab(self):
        """Activate the default tab if specified."""
        if self.default_tab and self.default_tab in self.file_buttons:
            self.activate_tab(self.default_tab, skip_save_prompt=True)
        elif self.file_buttons:
            # Activate first tab if no default specified
            first_tab = list(self.file_buttons.keys())[0]
            self.activate_tab(first_tab, skip_save_prompt=True)
    
    def mark_current_tab_unsaved(self):
        """Mark the current tab as having unsaved changes."""
        if self.current_button:
            if self.multi_language:
                current_tab_name = self._get_original_tab_name()
                current_lang = self.current_language_per_tab.get(current_tab_name, self.default_language)
                self.unsaved_changes_per_tab[current_tab_name][current_lang] = True
                # Update visual indicator with border color
                self._update_tab_unsaved_indicator(current_tab_name, True)
            else:
                self.current_button.setProperty("hasUnsavedChanges", True)
            self.current_button.style().polish(self.current_button)
    
    def mark_current_tab_saved(self):
        """Mark the current tab as saved."""
        if self.current_button:
            if self.multi_language:
                current_tab_name = self._get_original_tab_name()
                current_lang = self.current_language_per_tab.get(current_tab_name, self.default_language)
                self.unsaved_changes_per_tab[current_tab_name][current_lang] = False
                # Update visual indicator with border color
                self._update_tab_unsaved_indicator(current_tab_name, False)
            else:
                self.current_button.setProperty("hasUnsavedChanges", False)
            self.current_button.style().polish(self.current_button)
    
    def _get_original_tab_name(self):
        """Get the original tab name without any asterisk indicators."""
        if self.current_button:
            # Remove asterisk if present
            return self.current_button.text().rstrip('*')
        return None
    
    def _update_tab_unsaved_indicator(self, tab_name, has_unsaved):
        """Update visual indicator for unsaved changes using properties."""
        if tab_name in self.file_buttons:
            button = self.file_buttons[tab_name]
            
            if self.multi_language and hasattr(button, 'tab_container'):
                container = button.tab_container
                container.setProperty("hasUnsavedChanges", has_unsaved)
                container.style().polish(container)
            else:
                # Single language mode - use the button directly
                button.setProperty("hasUnsavedChanges", has_unsaved)
                button.style().polish(button)
    
    def get_current_tab_name(self):
        """Get the name of the currently active tab."""
        if self.current_button:
            # Always return the original button text without any indicators
            return self.current_button.text().rstrip('*')
        return None
    
    def get_current_file_path(self):
        """Get the file path of the currently active tab."""
        current_tab = self.get_current_tab_name()
        if current_tab:
            if self.multi_language:
                current_lang = self.current_language_per_tab.get(current_tab, self.default_language)
                return self._get_current_file_path(current_tab, current_lang)
            else:
                file_name = self.tab_config[current_tab]
                return os.path.join(self.workspace_dir, file_name)
        return None
    
    def has_unsaved_changes(self):
        """Check if the current tab has unsaved changes."""
        if self.current_button:
            if self.multi_language:
                current_tab_name = self._get_original_tab_name()
                current_lang = self.current_language_per_tab.get(current_tab_name, self.default_language)
                return self.unsaved_changes_per_tab.get(current_tab_name, {}).get(current_lang, False)
            else:
                return self.current_button.property("hasUnsavedChanges")
        return False
    
    def get_current_language(self):
        """Get the current language of the active tab."""
        if self.multi_language:
            current_tab = self.get_current_tab_name()
            return self.current_language_per_tab.get(current_tab, self.default_language)
        return 'cpp'  # Default for non-multi-language mode

    def set_tab_config(self, tab_config, default_tab=None):
        """Update the tab configuration and rebuild the UI."""
        self.tab_config = tab_config
        self.default_tab = default_tab
        
        # Clear existing buttons
        for button in self.file_buttons.values():
            button.deleteLater()
        self.file_buttons.clear()
        self.current_button = None
        
        # Re-initialize multi-language state if needed
        if self.multi_language:
            self._ensure_multi_language_config()
        
        # Rebuild UI
        self._setup_ui()
    
    def switch_language(self, tab_name, language):
        """Programmatically switch language for a specific tab."""
        if self.multi_language and tab_name in self.file_buttons:
            self._handle_language_change(tab_name, language)
    
    def get_all_file_paths_with_languages(self):
        """
        Get all file paths with their current languages.
        
        Returns:
            Dict[str, Dict[str, str]]: Dictionary mapping tab names to file info
                {
                    'Generator': {'language': 'py', 'file_path': '/path/to/generator.py'},
                    'Test Code': {'language': 'cpp', 'file_path': '/path/to/test.cpp'},
                    ...
                }
        """
        result = {}
        
        for tab_name in self.tab_config.keys():
            if self.multi_language:
                current_lang = self.current_language_per_tab.get(tab_name, self.default_language)
                file_path = self._get_current_file_path(tab_name, current_lang)
            else:
                current_lang = 'cpp'
                file_name = self.tab_config[tab_name]
                file_path = os.path.join(self.workspace_dir, file_name)
            
            result[tab_name] = {
                'language': current_lang,
                'file_path': file_path
            }
        
        return result
    
    def get_compilation_manifest(self):
        """
        Get complete compilation manifest for all tabs.
        
        This provides all information needed by core tools for multi-language compilation.
        
        Returns:
            Dict[str, Any]: Comprehensive manifest with file info
                {
                    'files': {
                        'generator': '/path/to/generator.py',
                        'test': '/path/to/test.cpp',
                        ...
                    },
                    'languages': {
                        'generator': 'py',
                        'test': 'cpp',
                        ...
                    },
                    'tab_info': {
                        'Generator': {'language': 'py', 'file_path': '...'},
                        ...
                    },
                    'workspace_dir': '/path/to/workspace',
                    'multi_language': True
                }
        """
        files_dict = {}
        languages_dict = {}
        tab_info = self.get_all_file_paths_with_languages()
        
        # Map tab names to standardized keys (lowercase, remove spaces)
        key_mapping = {
            'Generator': 'generator',
            'Test Code': 'test',
            'Correct Code': 'correct',
            'Validator Code': 'validator'
        }
        
        for tab_name, info in tab_info.items():
            # Get standardized key
            key = key_mapping.get(tab_name, tab_name.lower().replace(' ', '_'))
            
            files_dict[key] = info['file_path']
            languages_dict[key] = info['language']
        
        manifest = {
            'files': files_dict,
            'languages': languages_dict,
            'tab_info': tab_info,
            'workspace_dir': self.workspace_dir,
            'multi_language': self.multi_language
        }
        
        return manifest
    
    def get_files_for_tool(self, tool_type='comparator'):
        """
        Get file dictionary formatted for specific tool type.
        
        Args:
            tool_type: Type of tool ('comparator', 'benchmarker', 'validator')
            
        Returns:
            Dict[str, str]: File key to path mapping for the tool
        """
        manifest = self.get_compilation_manifest()
        files = manifest['files']
        
        # Filter files based on tool type
        if tool_type == 'comparator':
            # Needs: generator, correct, test
            return {k: files[k] for k in ['generator', 'correct', 'test'] if k in files}
        elif tool_type == 'benchmarker':
            # Needs: generator, test
            return {k: files[k] for k in ['generator', 'test'] if k in files}
        elif tool_type == 'validator':
            # Needs: generator, test, validator
            return {k: files[k] for k in ['generator', 'test', 'validator'] if k in files}
        else:
            return files