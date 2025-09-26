# -*- coding: utf-8 -*-
"""
TestTabWidget - Reusable tab widget for test windows.

This widget provides a consistent tab interface for switching between different
code files in test windows (Comparator, Validator, Benchmarker).
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QMessageBox
from PySide6.QtCore import Qt, Signal
import os

from src.app.presentation.styles.components.test_view_styles import (
    TEST_VIEW_BUTTON_PANEL_STYLE,
    TEST_VIEW_FILE_BUTTON_STYLE,
    TEST_VIEW_CONTENT_PANEL_STYLE
)
from src.app.shared.constants import WORKSPACE_DIR


class TestTabWidget(QWidget):
    """
    Reusable tab widget for test windows.
    
    Provides file switching functionality with unsaved changes detection,
    visual tab states, and customizable tab configurations.
    """
    
    # Signals
    fileChanged = Signal(str)  # Emitted when switching to a different file
    tabClicked = Signal(str)   # Emitted when any tab is clicked
    
    def __init__(self, parent=None, tab_config=None, default_tab=None):
        """
        Initialize TestTabWidget.
        
        Args:
            parent: Parent widget
            tab_config: Dict mapping tab names to file names
            default_tab: Name of the tab to activate by default
        """
        super().__init__(parent)
        
        # Configuration
        self.tab_config = tab_config or {}
        self.default_tab = default_tab
        self.workspace_dir = WORKSPACE_DIR
        
        # State management
        self.file_buttons = {}
        self.current_button = None
        self._content_widget = None
        
        self._setup_ui()
        os.makedirs(self.workspace_dir, exist_ok=True)
        
    def _setup_ui(self):
        """Setup the tab widget UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Create button panel with background
        button_panel = QWidget()
        button_panel.setStyleSheet(TEST_VIEW_BUTTON_PANEL_STYLE)
        button_layout = QHBoxLayout(button_panel)
        button_layout.setContentsMargins(8, 8, 8, 8)
        button_layout.setSpacing(8)
        
        # Create tab buttons
        for tab_name in self.tab_config.keys():
            btn = QPushButton(tab_name)
            btn.setMinimumHeight(36)
            btn.setProperty("isActive", False)
            btn.setProperty("hasUnsavedChanges", False)
            btn.setStyleSheet(TEST_VIEW_FILE_BUTTON_STYLE)
            btn.clicked.connect(lambda checked, name=tab_name: self._handle_tab_click(name))
            
            self.file_buttons[tab_name] = btn
            button_layout.addWidget(btn)
        
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
        
    def _handle_tab_click(self, tab_name, skip_save_prompt=False):
        """Handle tab button clicks and switch between files."""
        # Check if current file has unsaved changes (unless skipping prompt)
        if not skip_save_prompt and self.current_button and self.current_button.property("hasUnsavedChanges"):
            reply = QMessageBox.question(
                self, 
                "Unsaved Changes",
                f"Do you want to save changes to {self.current_button.text()}?",
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
            self.current_button.setProperty("hasUnsavedChanges", False)
            self.current_button.style().polish(self.current_button)
        
        # Set new active button
        new_button = self.file_buttons[tab_name]
        new_button.setProperty("isActive", True)
        new_button.style().polish(new_button)
        self.current_button = new_button
        
        # Get file path
        file_name = self.tab_config[tab_name]
        file_path = os.path.join(self.workspace_dir, file_name)
        
        # Create file if it doesn't exist with appropriate content
        if not os.path.exists(file_path):
            default_content = self._get_default_content(tab_name)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(default_content)
        
        # Emit signals
        self.fileChanged.emit(file_path)
        self.tabClicked.emit(tab_name)
        
    def _get_default_content(self, tab_name):
        """Get default content for new files based on tab name."""
        if tab_name == 'Generator':
            return '''#include <iostream>
#include <random>
#include <chrono>
using namespace std;

int main() {
    // Seed random number generator
    mt19937 rng(chrono::steady_clock::now().time_since_epoch().count());
    
    // Generate random test case
    // Example: generate random array
    int n = uniform_int_distribution<int>(1, 10)(rng);
    
    cout << n << endl;
    for (int i = 0; i < n; i++) {
        cout << uniform_int_distribution<int>(1, 100)(rng);
        if (i < n - 1) cout << " ";
    }
    cout << endl;
    
    return 0;
}'''
        elif tab_name in ['Test Code', 'Correct Code']:
            return '''#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;

int main() {
    // Read input
    int n;
    cin >> n;
    
    vector<int> arr(n);
    for (int i = 0; i < n; i++) {
        cin >> arr[i];
    }
    
    // Your algorithm here
    
    // Output result
    for (int i = 0; i < n; i++) {
        cout << arr[i];
        if (i < n - 1) cout << " ";
    }
    cout << endl;
    
    return 0;
}'''
        elif tab_name == 'Validator Code':
            return '''#include <iostream>
#include <vector>
#include <cassert>
using namespace std;

int main() {
    // Read input
    int n;
    cin >> n;
    
    // Validate input constraints
    assert(n >= 1 && n <= 1000000);
    
    vector<int> arr(n);
    for (int i = 0; i < n; i++) {
        cin >> arr[i];
        assert(arr[i] >= 1 && arr[i] <= 1000000);
    }
    
    // Additional validation logic here
    
    cout << "Input is valid" << endl;
    
    return 0;
}'''
        else:
            return '''#include <iostream>
using namespace std;

int main() {
    // Your code here
    return 0;
}'''
    
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
            self.current_button.setProperty("hasUnsavedChanges", True)
            self.current_button.style().polish(self.current_button)
    
    def mark_current_tab_saved(self):
        """Mark the current tab as saved."""
        if self.current_button:
            self.current_button.setProperty("hasUnsavedChanges", False)
            self.current_button.style().polish(self.current_button)
    
    def get_current_tab_name(self):
        """Get the name of the currently active tab."""
        if self.current_button:
            return self.current_button.text()
        return None
    
    def get_current_file_path(self):
        """Get the file path of the currently active tab."""
        current_tab = self.get_current_tab_name()
        if current_tab and current_tab in self.tab_config:
            file_name = self.tab_config[current_tab]
            return os.path.join(self.workspace_dir, file_name)
        return None
    
    def has_unsaved_changes(self):
        """Check if the current tab has unsaved changes."""
        if self.current_button:
            return self.current_button.property("hasUnsavedChanges")
        return False

    def set_tab_config(self, tab_config, default_tab=None):
        """Update the tab configuration and rebuild the UI."""
        self.tab_config = tab_config
        self.default_tab = default_tab
        
        # Clear existing buttons
        for button in self.file_buttons.values():
            button.deleteLater()
        self.file_buttons.clear()
        self.current_button = None
        
        # Rebuild UI
        self._setup_ui()