# -*- coding: utf-8 -*-
"""
EditorTabWidget - Reusable tab widget for code editor.

This widget provides a tab interface for managing multiple code files in the
code editor with dynamic tab creation, file opening/closing, and proper state management.
"""

import os

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QMessageBox, QPushButton, QTabWidget, QVBoxLayout, QWidget

from src.app.presentation.styles.components.editor import get_tab_style
from src.app.presentation.widgets.display_area_widgets.editor import EditorWidget


class EditorTab(QWidget):
    """Individual editor tab containing an EditorWidget."""

    def __init__(self):
        super().__init__()
        self.editor = EditorWidget()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.editor)


class EditorTabWidget(QWidget):
    """
    Reusable tab widget for code editor.

    Provides dynamic tab management with file opening/closing, unsaved changes detection,
    and proper integration with EditorWidget functionality.
    """

    # Signals
    filePathChanged = Signal()
    currentTabChanged = Signal(int)  # Emitted when active tab changes
    tabClosed = Signal(int)  # Emitted when a tab is closed

    def __init__(self, parent=None):
        """Initialize EditorTabWidget."""
        super().__init__(parent)

        self._setup_ui()
        self._connect_signals()

        # Start with one empty tab
        self.add_new_tab("Untitled")

    def _setup_ui(self):
        """Setup the tab widget UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Create main tab widget
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabsClosable(True)
        self.tab_widget.setMovable(True)  # Allow tab reordering

        # Add new tab button in corner
        self.new_tab_button = QPushButton("+")
        self.new_tab_button.setObjectName("new_tab_button")
        self.tab_widget.setCornerWidget(self.new_tab_button, Qt.TopLeftCorner)

        # Apply styling
        self.tab_widget.setStyleSheet(get_tab_style())

        layout.addWidget(self.tab_widget)

    def _connect_signals(self):
        """Connect internal signals."""
        self.new_tab_button.clicked.connect(lambda: self.add_new_tab())
        self.tab_widget.tabCloseRequested.connect(self.close_tab)
        self.tab_widget.currentChanged.connect(self._on_current_tab_changed)

    def _on_current_tab_changed(self, index):
        """Handle current tab change."""
        self.currentTabChanged.emit(index)
        self.filePathChanged.emit()

    def add_new_tab(self, title="Untitled", file_path=None):
        """
        Add a new editor tab.

        Args:
            title: Initial tab title
            file_path: Optional file path to open

        Returns:
            EditorTab: The newly created tab
        """
        new_tab = EditorTab()
        index = self.tab_widget.addTab(new_tab, title)
        self.tab_widget.setCurrentIndex(index)

        # Load file if provided
        if file_path and os.path.exists(file_path):
            new_tab.editor.openFile(file_path)

        # Connect editor signals
        editor = new_tab.editor
        doc = editor.codeEditor.document()

        def update_title():
            self._update_tab_title(index)
            self.filePathChanged.emit()

        # Connect modification and file change signals
        doc.modificationChanged.connect(lambda _: update_title())
        editor.filePathChanged.connect(update_title)
        editor.fileSaved.connect(update_title)

        # Initial title update
        self._update_tab_title(index)

        return new_tab

    def _update_tab_title(self, index):
        """Update tab title and tooltip based on file state."""
        tab = self.tab_widget.widget(index)
        if not tab:
            return

        editor = tab.editor
        if not editor:
            return

        # Set tooltip to show full path
        tooltip = editor.currentFilePath or "Untitled"
        self.tab_widget.setTabToolTip(index, tooltip)

        # Determine if file was deleted
        file_deleted = editor.currentFilePath and not os.path.exists(editor.currentFilePath)

        if file_deleted:
            title = f"[Deleted] {os.path.basename(editor.currentFilePath)}"
        else:
            # Get base title
            if editor.currentFilePath:
                title = os.path.basename(editor.currentFilePath)
            else:
                title = "Untitled"

            # Add modification indicator
            if editor.codeEditor.document().isModified():
                title += " *"

        self.tab_widget.setTabText(index, title)

    def close_tab(self, index):
        """
        Close tab with save check for modified files.

        Args:
            index: Index of tab to close
        """
        tab = self.tab_widget.widget(index)
        if not tab:
            return

        # Check if file is modified
        if tab.editor.codeEditor.document().isModified():
            reply = QMessageBox.question(
                self,
                "Save Changes?",
                f"Save changes to {self.tab_widget.tabText(index)}?",
                QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel,
            )

            if reply == QMessageBox.Save:
                if not tab.editor.saveFile():
                    return  # Save was cancelled or failed
            elif reply == QMessageBox.Cancel:
                return  # Don't close the tab

        # Remove the tab
        self._remove_tab(index)

    def _remove_tab(self, index):
        """Handle tab removal and ensure at least one tab remains."""
        self.tab_widget.removeTab(index)
        self.tabClosed.emit(index)

        # Ensure at least one tab is always open
        if self.tab_widget.count() == 0:
            self.add_new_tab("Untitled")

        self.filePathChanged.emit()

    def open_file_in_new_tab(self, file_path):
        """
        Open a file in a new tab.

        Args:
            file_path: Path to the file to open

        Returns:
            EditorTab: The tab containing the opened file
        """
        if not os.path.exists(file_path):
            return None

        # Check if file is already open
        for i in range(self.tab_widget.count()):
            tab = self.tab_widget.widget(i)
            if tab.editor.currentFilePath == file_path:
                # File already open, switch to that tab
                self.tab_widget.setCurrentIndex(i)
                return tab

        # Open in new tab
        filename = os.path.basename(file_path)
        return self.add_new_tab(filename, file_path)

    def close_current_tab(self):
        """Close the currently active tab."""
        current_index = self.tab_widget.currentIndex()
        if current_index >= 0:
            self.close_tab(current_index)

    def close_all_tabs(self):
        """Close all tabs with save checks."""
        while self.tab_widget.count() > 0:
            if not self.close_tab(0):
                break  # User cancelled, stop closing

    @property
    def current_editor(self):
        """Get the current editor widget."""
        current_tab = self.tab_widget.currentWidget()
        return current_tab.editor if current_tab else None

    @property
    def current_tab(self):
        """Get the current tab widget."""
        return self.tab_widget.currentWidget()

    @property
    def tab_count(self):
        """Get the number of open tabs."""
        return self.tab_widget.count()

    def get_tab_at_index(self, index):
        """Get tab at specified index."""
        return self.tab_widget.widget(index)

    def get_current_index(self):
        """Get index of current tab."""
        return self.tab_widget.currentIndex()

    def set_current_index(self, index):
        """Set the current tab by index."""
        if 0 <= index < self.tab_widget.count():
            self.tab_widget.setCurrentIndex(index)

    def get_all_file_paths(self):
        """Get list of all open file paths."""
        paths = []
        for i in range(self.tab_widget.count()):
            tab = self.tab_widget.widget(i)
            if tab.editor.currentFilePath:
                paths.append(tab.editor.currentFilePath)
        return paths

    def has_unsaved_changes(self):
        """Check if any tab has unsaved changes."""
        for i in range(self.tab_widget.count()):
            tab = self.tab_widget.widget(i)
            if tab.editor.codeEditor.document().isModified():
                return True
        return False

    def save_current_file(self):
        """Save the current file."""
        current_tab = self.tab_widget.currentWidget()
        if current_tab:
            return current_tab.editor.saveFile()
        return False

    def save_all_files(self):
        """Save all modified files."""
        success = True
        for i in range(self.tab_widget.count()):
            tab = self.tab_widget.widget(i)
            if tab.editor.codeEditor.document().isModified():
                if not tab.editor.saveFile():
                    success = False
        return success
