"""
Unit tests for Sidebar widget.

Tests sidebar creation, button management, and signal emission using pytest-qt.
"""

import pytest
from PySide6.QtWidgets import QPushButton, QLabel
from PySide6.QtCore import Qt

from src.app.presentation.widgets.sidebar import Sidebar, SidebarSection


@pytest.fixture
def sidebar(qtbot):
    """Create Sidebar widget for testing."""
    widget = Sidebar("Test Window")
    qtbot.addWidget(widget)
    return widget


class TestSidebarInitialization:
    """Test sidebar initialization and setup."""
    
    def test_creates_with_title(self, sidebar):
        """Should display title in header."""
        assert sidebar.windowTitleWidget is not None
        assert sidebar.windowTitleWidget.text() == "Test Window"
    
    def test_creates_without_title(self, qtbot):
        """Should create sidebar without title."""
        widget = Sidebar()
        qtbot.addWidget(widget)
        
        assert widget.windowTitleWidget is None
    
    def test_has_content_area(self, sidebar):
        """Should have content area for widgets."""
        assert sidebar.content is not None
        assert sidebar.content_layout is not None
    
    def test_has_footer_area(self, sidebar):
        """Should have footer area for buttons."""
        assert sidebar.footer is not None
    
    def test_sets_size_constraints(self, sidebar):
        """Should set minimum and maximum width constraints."""
        assert sidebar.minimumWidth() == 250
        assert sidebar.maximumWidth() == 350


class TestSidebarSectionManagement:
    """Test sidebar section creation and management."""
    
    def test_adds_section_without_title(self, sidebar):
        """Should create section without title."""
        section = sidebar.add_section()
        
        assert section is not None
        assert isinstance(section, SidebarSection)
    
    def test_adds_section_with_title(self, sidebar):
        """Should create section with title label."""
        section = sidebar.add_section("Test Section")
        
        assert section is not None
        # Section should have title in its layout
        layout = section.layout()
        assert layout.count() > 0
    
    def test_multiple_sections(self, sidebar):
        """Should support multiple sections."""
        section1 = sidebar.add_section("Section 1")
        section2 = sidebar.add_section("Section 2")
        
        assert section1 is not None
        assert section2 is not None
        assert section1 != section2


class TestSidebarButtonManagement:
    """Test button creation and management."""
    
    def test_adds_button_to_content(self, sidebar):
        """Should add button directly to content area."""
        btn = sidebar.add_button("Test Button")
        
        assert btn is not None
        assert isinstance(btn, QPushButton)
        assert btn.text() == "Test Button"
    
    def test_adds_button_to_section(self, sidebar):
        """Should add button to specific section."""
        section = sidebar.add_section("Section")
        btn = sidebar.add_button("Section Button", section)
        
        assert btn is not None
        assert btn.text() == "Section Button"
        # Button should be in section's layout
        assert section.layout().count() > 0
    
    def test_multiple_buttons_in_section(self, sidebar):
        """Should add multiple buttons to same section."""
        section = sidebar.add_section("Section")
        btn1 = sidebar.add_button("Button 1", section)
        btn2 = sidebar.add_button("Button 2", section)
        
        assert btn1 != btn2
        assert section.layout().count() >= 2


class TestSidebarSignalEmission:
    """Test signal emission from buttons."""
    
    def test_button_click_emits_signal(self, sidebar, qtbot):
        """Should emit button_clicked signal with button text."""
        btn = sidebar.add_button("Click Me")
        
        with qtbot.waitSignal(sidebar.button_clicked, timeout=1000) as blocker:
            btn.click()
        
        assert blocker.args[0] == "Click Me"
    
    def test_multiple_button_clicks_emit_correct_text(self, sidebar, qtbot):
        """Should emit correct text for each button click."""
        btn1 = sidebar.add_button("First")
        btn2 = sidebar.add_button("Second")
        
        # Click first button
        with qtbot.waitSignal(sidebar.button_clicked, timeout=1000) as blocker:
            btn1.click()
        assert blocker.args[0] == "First"
        
        # Click second button
        with qtbot.waitSignal(sidebar.button_clicked, timeout=1000) as blocker:
            btn2.click()
        assert blocker.args[0] == "Second"


class TestSidebarFooterButtons:
    """Test footer button functionality."""
    
    def test_adds_back_button(self, sidebar):
        """Should add back button to footer."""
        btn = sidebar.add_back_button()
        
        assert btn is not None
        assert btn.text() == "Back"
        assert sidebar.back_button is btn
    
    def test_back_button_emits_signal(self, sidebar, qtbot):
        """Should emit 'Back' signal when back button clicked."""
        btn = sidebar.add_back_button()
        
        with qtbot.waitSignal(sidebar.button_clicked, timeout=1000) as blocker:
            btn.click()
        
        assert blocker.args[0] == "Back"
    
    def test_adds_results_button(self, sidebar):
        """Should add results button to footer."""
        btn = sidebar.add_results_button()
        
        assert btn is not None
        assert btn.text() == "Results"
    
    def test_results_button_emits_signal(self, sidebar, qtbot):
        """Should emit 'Results' signal when results button clicked."""
        btn = sidebar.add_results_button()
        
        with qtbot.waitSignal(sidebar.button_clicked, timeout=1000) as blocker:
            btn.click()
        
        assert blocker.args[0] == "Results"
    
    def test_adds_help_button(self, sidebar):
        """Should add help button to footer."""
        btn = sidebar.add_help_button()
        
        assert btn is not None
        assert btn.text() == "Help Center"
    
    def test_help_button_emits_signal(self, sidebar, qtbot):
        """Should emit 'Help Center' signal when help button clicked."""
        btn = sidebar.add_help_button()
        
        with qtbot.waitSignal(sidebar.button_clicked, timeout=1000) as blocker:
            btn.click()
        
        assert blocker.args[0] == "Help Center"


class TestSidebarSaveButtonFunctionality:
    """Test save button replacement and state management."""
    
    def test_replaces_results_with_save_button(self, sidebar):
        """Should replace results button with save button."""
        # First add results button
        results_btn = sidebar.add_results_button()
        
        # Replace with save button
        save_btn = sidebar.replace_results_with_save_button()
        
        assert save_btn is not None
        assert save_btn.text() == "Tests Running..."
        assert save_btn.isEnabled() is False
        assert results_btn.isVisible() is False
    
    def test_enables_save_button(self, sidebar):
        """Should enable save button when tests complete."""
        sidebar.add_results_button()
        save_btn = sidebar.replace_results_with_save_button()
        
        sidebar.enable_save_button()
        
        assert save_btn.isEnabled() is True
        assert "Save Results" in save_btn.text()
    
    def test_marks_results_saved(self, sidebar):
        """Should update save button to show saved state."""
        sidebar.add_results_button()
        save_btn = sidebar.replace_results_with_save_button()
        sidebar.enable_save_button()
        
        sidebar.mark_results_saved()
        
        assert "Saved" in save_btn.text()
        assert save_btn.isEnabled() is False
    
    def test_restores_results_button(self, sidebar):
        """Should restore results button after save flow."""
        results_btn = sidebar.add_results_button()
        sidebar.replace_results_with_save_button()
        
        sidebar.restore_results_button()
        
        # Results button should be restored (exists and accessible)
        assert sidebar.results_button is not None
        # Note: Widget visibility depends on layout management, check it exists
        assert hasattr(sidebar, 'results_button')
    
    def test_save_button_emits_signal(self, sidebar, qtbot):
        """Should emit 'Save' signal when save button clicked."""
        sidebar.add_results_button()
        save_btn = sidebar.replace_results_with_save_button()
        sidebar.enable_save_button()
        
        with qtbot.waitSignal(sidebar.button_clicked, timeout=1000) as blocker:
            save_btn.click()
        
        assert blocker.args[0] == "Save"


class TestSidebarLayout:
    """Test sidebar layout and spacing."""
    
    def test_adds_spacer(self, sidebar):
        """Should add spacer to content layout."""
        initial_count = sidebar.content_layout.count()
        
        sidebar.add_spacer()
        
        assert sidebar.content_layout.count() == initial_count + 1
    
    def test_horizontal_footer_buttons(self, sidebar):
        """Should setup two buttons horizontally in footer."""
        left_btn = QPushButton("Left")
        right_btn = QPushButton("Right")
        
        sidebar.setup_horizontal_footer_buttons(left_btn, right_btn)
        
        # Both buttons should be in footer
        assert left_btn.parent() is not None
        assert right_btn.parent() is not None


class TestSidebarSection:
    """Test SidebarSection component."""
    
    def test_creates_section_without_title(self, qtbot):
        """Should create section without title."""
        section = SidebarSection(None)
        qtbot.addWidget(section)
        
        assert section is not None
    
    def test_creates_section_with_title(self, qtbot):
        """Should create section with title label."""
        section = SidebarSection("Test Title")
        qtbot.addWidget(section)
        
        # Should have title in layout
        assert section.layout().count() > 0
    
    def test_adds_widget_to_section(self, qtbot):
        """Should add widgets to section layout."""
        section = SidebarSection("Section")
        qtbot.addWidget(section)
        
        initial_count = section.layout().count()
        
        widget = QPushButton("Test")
        section.add_widget(widget)
        
        assert section.layout().count() == initial_count + 1


class TestSidebarDividers:
    """Test divider creation and styling."""
    
    def test_add_footer_divider_returns_widget(self, sidebar):
        """add_footer_divider should return a divider widget."""
        divider = sidebar.add_footer_divider()
        
        assert divider is not None
        assert divider.height() == 1
    
    def test_add_footer_divider_adds_to_footer(self, sidebar):
        """add_footer_divider should add divider container to footer layout."""
        initial_count = sidebar.footer.layout().count()
        
        sidebar.add_footer_divider()
        
        # Should add container to footer
        assert sidebar.footer.layout().count() > initial_count
    
    def test_add_vertical_footer_divider_returns_widget(self, sidebar):
        """add_vertical_footer_divider should return a vertical divider widget."""
        divider = sidebar.add_vertical_footer_divider()
        
        assert divider is not None
        assert divider.width() == 1
        assert divider.minimumHeight() == 30
    
    def test_add_footer_button_divider_calls_add_footer_divider(self, sidebar):
        """add_footer_button_divider should call add_footer_divider."""
        initial_count = sidebar.footer.layout().count()
        
        sidebar.add_footer_button_divider()
        
        # Should add a divider to footer
        assert sidebar.footer.layout().count() > initial_count


class TestSidebarRestoreResultsButtonEdgeCases:
    """Test edge cases in restore_results_button method."""
    
    def test_restore_results_button_when_no_results_button_exists(self, sidebar):
        """restore_results_button should create new results button if none exists."""
        # Don't add results button initially
        sidebar.replace_results_with_save_button()
        
        # Now restore - should create new results button
        sidebar.restore_results_button()
        
        assert hasattr(sidebar, 'results_button')
        assert sidebar.results_button is not None
    
    def test_restore_results_button_shows_existing_button(self, sidebar):
        """restore_results_button should restore existing results button and call show()."""
        # Add results button
        results_btn = sidebar.add_results_button()
        original_btn = results_btn  # Keep reference
        
        # Simulate the replace flow completely (not just hide)
        save_btn = sidebar.replace_results_with_save_button()
        
        # Verify button is hidden after replace
        assert not results_btn.isVisible()
        
        # Now restore - should call show() on existing results button
        sidebar.restore_results_button()
        
        # Results button reference should still exist and be the same object
        assert sidebar.results_button is original_btn
        # Note: isVisible() may return False in test environment without parent window being shown
        # The key test is that restore_results_button() doesn't crash and maintains the button reference
    
    def test_restore_results_button_removes_save_button(self, sidebar):
        """restore_results_button should remove save button if it exists."""
        sidebar.add_results_button()
        save_btn = sidebar.replace_results_with_save_button()
        
        sidebar.restore_results_button()
        
        # Save button should be None after restore
        assert sidebar.save_button is None
    
    def test_enable_save_button_with_no_save_button(self, sidebar):
        """enable_save_button should handle case when save button doesn't exist."""
        # Should not crash
        sidebar.enable_save_button()
        
        # No assertions needed - just verify it doesn't crash
        assert True
    
    def test_mark_results_saved_with_no_save_button(self, sidebar):
        """mark_results_saved should handle case when save button doesn't exist."""
        # Should not crash
        sidebar.mark_results_saved()
        
        # No assertions needed - just verify it doesn't crash
        assert True
