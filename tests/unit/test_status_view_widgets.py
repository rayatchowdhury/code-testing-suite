"""
Unit tests for status view sub-widgets.
"""

import pytest
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel
from src.app.presentation.widgets.status_view_widgets import (
    ProgressSection,
    VisualProgressBar,
    StatsPanel,
    CardsSection
)

# Phase 6 (Issue #7): Removed TestControlsPanel class - ControlsPanel widget removed from codebase


class TestProgressSection:
    """Test suite for ProgressSection"""
    
    def test_progress_section_creation(self, qtbot):
        """Test progress section can be created"""
        section = ProgressSection()
        qtbot.addWidget(section)
        
        assert section.visual_progress is not None
        assert section.stats_panel is not None
        
    def test_progress_reset(self, qtbot):
        """Test progress section reset"""
        section = ProgressSection()
        qtbot.addWidget(section)
        
        section.reset(5)
        
        # Visual progress should be reset
        assert section.visual_progress.total == 5
        assert len(section.visual_progress.results) == 0
        
    def test_add_test_result(self, qtbot):
        """Test adding test results"""
        section = ProgressSection()
        qtbot.addWidget(section)
        
        section.reset(3)
        section.add_test_result(True)
        
        assert len(section.visual_progress.results) == 1
        assert section.visual_progress.results[0] == True
        
    def test_update_stats(self, qtbot):
        """Test stats update"""
        section = ProgressSection()
        qtbot.addWidget(section)
        
        section.reset(10)
        section.update_stats(5, 10, 4, 1)
        
        assert section.stats_panel.percentage_label.text() == "50%"
        assert section.stats_panel.passed_label.text() == "Passed: 4"
        assert section.stats_panel.failed_label.text() == "Failed: 1"


class TestVisualProgressBar:
    """Test suite for VisualProgressBar"""
    
    def test_visual_progress_creation(self, qtbot):
        """Test visual progress bar can be created"""
        bar = VisualProgressBar()
        qtbot.addWidget(bar)
        
        assert bar.results == []
        assert bar.total == 0
        
    def test_reset_creates_placeholders(self, qtbot):
        """Test reset creates placeholder labels"""
        bar = VisualProgressBar()
        qtbot.addWidget(bar)
        
        bar.reset(5)
        
        assert bar.total == 5
        # Should have 5 placeholder labels
        assert bar.layout.count() == 5
        
    def test_add_result_updates_label(self, qtbot):
        """Test adding result updates the correct label"""
        bar = VisualProgressBar()
        qtbot.addWidget(bar)
        
        bar.reset(3)
        bar.add_result(True)
        
        # First label should show checkmark
        first_label = bar.layout.itemAt(0).widget()
        assert isinstance(first_label, QLabel)
        assert "✓" in first_label.text()
        
    def test_large_test_count_limited(self, qtbot):
        """Test large test counts are limited to 50 display items"""
        bar = VisualProgressBar()
        qtbot.addWidget(bar)
        
        bar.reset(100)
        
        # Should have 50 items + 1 "more" indicator
        assert bar.layout.count() == 51


class TestStatsPanel:
    """Test suite for StatsPanel"""
    
    def test_stats_panel_creation(self, qtbot):
        """Test stats panel can be created"""
        panel = StatsPanel()
        qtbot.addWidget(panel)
        
        assert panel.percentage_label is not None
        assert panel.passed_label is not None
        assert panel.failed_label is not None
        
    def test_stats_panel_initial_values(self, qtbot):
        """Test stats panel has correct initial values"""
        panel = StatsPanel()
        qtbot.addWidget(panel)
        
        assert panel.percentage_label.text() == "0%"
        assert panel.passed_label.text() == "Passed: 0"
        assert panel.failed_label.text() == "Failed: 0"
        
    def test_stats_update(self, qtbot):
        """Test updating statistics"""
        panel = StatsPanel()
        qtbot.addWidget(panel)
        
        panel.update(7, 10, 5, 2)
        
        assert panel.percentage_label.text() == "70%"
        assert panel.passed_label.text() == "Passed: 5"
        assert panel.failed_label.text() == "Failed: 2"
        
    def test_stats_reset(self, qtbot):
        """Test resetting statistics"""
        panel = StatsPanel()
        qtbot.addWidget(panel)
        
        panel.update(5, 10, 3, 2)
        panel.reset()
        
        assert panel.percentage_label.text() == "0%"
        assert panel.passed_label.text() == "Passed: 0"
        assert panel.failed_label.text() == "Failed: 0"


class TestCardsSection:
    """Test suite for CardsSection"""
    
    def test_cards_section_creation(self, qtbot):
        """Test cards section can be created"""
        section = CardsSection()
        qtbot.addWidget(section)
        
        assert section.layout_mode == 'single'
        assert len(section.passed_cards) == 0
        assert len(section.failed_cards) == 0
        
    def test_single_layout_mode_initially(self, qtbot):
        """Test starts in single layout mode"""
        section = CardsSection()
        qtbot.addWidget(section)
        section.show()  # Widget must be shown for isVisible() to return True
        
        assert section.layout_mode == 'single'
        assert section.single_scroll.isVisible()
        
    def test_add_passed_card_in_single_mode(self, qtbot):
        """Test adding passed card in single mode"""
        section = CardsSection()
        qtbot.addWidget(section)
        
        card = QLabel("Test 1 Passed")
        section.add_card(card, passed=True)
        
        assert len(section.passed_cards) == 1
        assert section.layout_mode == 'single'
        
    def test_switch_to_split_on_first_failure(self, qtbot):
        """Test switches to split layout on first failure"""
        section = CardsSection()
        qtbot.addWidget(section)
        
        # Add some passed cards
        for i in range(3):
            card = QLabel(f"Test {i+1} Passed")
            section.add_card(card, passed=True)
            
        assert section.layout_mode == 'single'
        
        # Add first failed card
        failed_card = QLabel("Test 4 Failed")
        section.add_card(failed_card, passed=False)
        
        # Should switch to split layout
        assert section.layout_mode == 'split'
        assert section.passed_scroll is not None
        assert section.failed_scroll is not None
        
    def test_clear_resets_to_single_layout(self, qtbot):
        """Test clear resets to single layout"""
        section = CardsSection()
        qtbot.addWidget(section)
        
        # Add cards and switch to split
        section.add_card(QLabel("Passed"), passed=True)
        section.add_card(QLabel("Failed"), passed=False)
        
        assert section.layout_mode == 'split'
        
        # Clear
        section.clear()
        
        assert section.layout_mode == 'single'
        assert len(section.passed_cards) == 0
        assert len(section.failed_cards) == 0
        
    def test_cards_appear_in_correct_columns(self, qtbot):
        """Test cards appear in correct columns in split mode"""
        section = CardsSection()
        qtbot.addWidget(section)
        
        # Create split layout
        section.add_card(QLabel("Passed 1"), passed=True)
        section.add_card(QLabel("Failed 1"), passed=False)
        section.add_card(QLabel("Passed 2"), passed=True)
        section.add_card(QLabel("Failed 2"), passed=False)
        
        # Check counts
        assert len(section.passed_cards) == 2
        assert len(section.failed_cards) == 2
        
        # Check they're in the right layouts
        assert section.passed_layout.count() == 2
        assert section.failed_layout.count() == 2
