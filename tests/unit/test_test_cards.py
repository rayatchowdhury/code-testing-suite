"""
Unit tests for test card widgets.
"""

import pytest
from PySide6.QtCore import Qt
from src.app.presentation.widgets.test_cards import (
    BaseTestCard,
    ComparatorTestCard,
    ValidatorTestCard,
    BenchmarkerTestCard
)


class TestBaseTestCard:
    """Test suite for BaseTestCard"""
    
    def test_card_creation_passed(self, qtbot):
        """Test creating a passed test card"""
        card = BaseTestCard(1, True, 0.123, 45.6)
        qtbot.addWidget(card)
        
        assert card.test_number == 1
        assert card.passed == True
        assert card.time == 0.123
        assert card.memory == 45.6
        
    def test_card_creation_failed(self, qtbot):
        """Test creating a failed test card"""
        card = BaseTestCard(5, False, 1.5, 100.0)
        qtbot.addWidget(card)
        
        assert card.test_number == 5
        assert card.passed == False
        assert card.time == 1.5
        assert card.memory == 100.0
        
    def test_card_has_labels(self, qtbot):
        """Test card has all required labels"""
        card = BaseTestCard(3, True, 0.456, 78.9)
        qtbot.addWidget(card)
        
        assert card.test_label is not None
        assert card.status_label is not None
        assert card.time_label is not None
        assert card.memory_label is not None
        
    def test_card_label_text_passed(self, qtbot):
        """Test label text for passed card"""
        card = BaseTestCard(2, True, 0.234, 56.7)
        qtbot.addWidget(card)
        
        assert "Test #2" in card.test_label.text()
        assert "Passed" in card.status_label.text()
        assert "0.234" in card.time_label.text()
        assert "56.7" in card.memory_label.text()
        
    def test_card_label_text_failed(self, qtbot):
        """Test label text for failed card"""
        card = BaseTestCard(7, False, 2.1, 150.5)
        qtbot.addWidget(card)
        
        assert "Test #7" in card.test_label.text()
        assert "Failed" in card.status_label.text()
        assert "2.1" in card.time_label.text()
        assert "150.5" in card.memory_label.text()
        
    def test_card_click_signal(self, qtbot):
        """Test card emits clicked signal when clicked"""
        card = BaseTestCard(5, False, 1.5, 100.0)
        qtbot.addWidget(card)
        card.show()
        
        with qtbot.waitSignal(card.clicked, timeout=1000) as blocker:
            qtbot.mouseClick(card, Qt.LeftButton)
        
        assert blocker.args[0] == 5
        
    def test_card_cursor_is_pointer(self, qtbot):
        """Test card has pointing hand cursor"""
        card = BaseTestCard(1, True, 0.1, 10.0)
        qtbot.addWidget(card)
        
        assert card.cursor().shape() == Qt.PointingHandCursor
        
    def test_update_metrics(self, qtbot):
        """Test updating card metrics"""
        card = BaseTestCard(1, True, 0.1, 10.0)
        qtbot.addWidget(card)
        
        card.update_metrics(0.5, 50.0)
        
        assert card.time == 0.5
        assert card.memory == 50.0
        assert "0.500" in card.time_label.text()
        assert "50.0" in card.memory_label.text()
        
    def test_passed_card_styling(self, qtbot):
        """Test passed card has appropriate styling"""
        card = BaseTestCard(1, True, 0.1, 10.0)
        qtbot.addWidget(card)
        
        # Card should have stylesheet with green tint
        style = card.styleSheet()
        assert style  # Has styling
        assert "border" in style.lower()
        assert "radius" in style.lower()
        
    def test_failed_card_styling(self, qtbot):
        """Test failed card has appropriate styling"""
        card = BaseTestCard(1, False, 0.1, 10.0)
        qtbot.addWidget(card)
        
        # Card should have stylesheet with red tint
        style = card.styleSheet()
        assert style  # Has styling
        assert "border" in style.lower()
        assert "radius" in style.lower()


class TestComparatorTestCard:
    """Test suite for ComparatorTestCard"""
    
    def test_comparator_card_creation(self, qtbot):
        """Test creating comparator card with input/output"""
        card = ComparatorTestCard(
            1, True, 0.1, 10.0,
            "5 10", "15", "15"
        )
        qtbot.addWidget(card)
        
        assert card.test_number == 1
        assert card.input_text == "5 10"
        assert card.correct_output == "15"
        assert card.test_output == "15"
        
    def test_comparator_card_failed(self, qtbot):
        """Test comparator card with wrong output"""
        card = ComparatorTestCard(
            2, False, 0.2, 20.0,
            "3 7", "10", "9"
        )
        qtbot.addWidget(card)
        
        assert card.passed == False
        assert card.test_output != card.correct_output
        
    def test_comparator_card_inherits_base(self, qtbot):
        """Test comparator card inherits base functionality"""
        card = ComparatorTestCard(
            3, True, 0.3, 30.0,
            "input", "expected", "actual"
        )
        qtbot.addWidget(card)
        
        # Should have base card components
        assert card.test_label is not None
        assert card.status_label is not None
        assert card.time_label is not None
        assert card.memory_label is not None
        
    def test_comparator_card_click(self, qtbot):
        """Test comparator card emits click signal"""
        card = ComparatorTestCard(
            4, True, 0.4, 40.0,
            "in", "out", "out"
        )
        qtbot.addWidget(card)
        card.show()
        
        with qtbot.waitSignal(card.clicked, timeout=1000) as blocker:
            qtbot.mouseClick(card, Qt.LeftButton)
        
        assert blocker.args[0] == 4


class TestValidatorTestCard:
    """Test suite for ValidatorTestCard"""
    
    def test_validator_card_creation(self, qtbot):
        """Test creating validator card"""
        card = ValidatorTestCard(
            1, True, 0.15, 25.0,
            "Hello World", "Hello World"
        )
        qtbot.addWidget(card)
        
        assert card.test_number == 1
        assert card.expected_output == "Hello World"
        assert card.actual_output == "Hello World"
        
    def test_validator_card_failed(self, qtbot):
        """Test validator card with wrong output"""
        card = ValidatorTestCard(
            2, False, 0.25, 35.0,
            "Expected", "Actual"
        )
        qtbot.addWidget(card)
        
        assert card.passed == False
        assert card.actual_output != card.expected_output
        
    def test_validator_card_click(self, qtbot):
        """Test validator card emits click signal"""
        card = ValidatorTestCard(
            5, False, 0.5, 50.0,
            "exp", "act"
        )
        qtbot.addWidget(card)
        card.show()
        
        with qtbot.waitSignal(card.clicked, timeout=1000) as blocker:
            qtbot.mouseClick(card, Qt.LeftButton)
        
        assert blocker.args[0] == 5


class TestBenchmarkerTestCard:
    """Test suite for BenchmarkerTestCard"""
    
    def test_benchmarker_card_creation(self, qtbot):
        """Test creating benchmarker card"""
        card = BenchmarkerTestCard(
            1, True, 0.5, 100.0, 1000
        )
        qtbot.addWidget(card)
        
        assert card.test_number == 1
        assert card.test_size == 1000
        assert card.time == 0.5
        assert card.memory == 100.0
        
    def test_benchmarker_card_large_size(self, qtbot):
        """Test benchmarker card with large test size"""
        card = BenchmarkerTestCard(
            2, True, 2.5, 500.0, 1000000
        )
        qtbot.addWidget(card)
        
        assert card.test_size == 1000000
        
    def test_benchmarker_card_failed(self, qtbot):
        """Test benchmarker card that exceeded limits"""
        card = BenchmarkerTestCard(
            3, False, 5.0, 1000.0, 10000
        )
        qtbot.addWidget(card)
        
        assert card.passed == False
        
    def test_benchmarker_card_click(self, qtbot):
        """Test benchmarker card emits click signal"""
        card = BenchmarkerTestCard(
            6, True, 1.0, 200.0, 5000
        )
        qtbot.addWidget(card)
        card.show()
        
        with qtbot.waitSignal(card.clicked, timeout=1000) as blocker:
            qtbot.mouseClick(card, Qt.LeftButton)
        
        assert blocker.args[0] == 6


class TestCardIntegration:
    """Test suite for card integration with CardsSection"""
    
    def test_card_can_be_added_to_layout(self, qtbot):
        """Test card can be added to a layout"""
        from src.app.presentation.widgets.status_view_widgets import CardsSection
        
        section = CardsSection()
        qtbot.addWidget(section)
        
        card = BaseTestCard(1, True, 0.1, 10.0)
        section.add_card(card, passed=True)
        
        assert len(section.passed_cards) == 1
        assert card in section.passed_cards
        
    def test_failed_card_triggers_split_layout(self, qtbot):
        """Test adding failed card switches to split layout"""
        from src.app.presentation.widgets.status_view_widgets import CardsSection
        
        section = CardsSection()
        qtbot.addWidget(section)
        section.show()
        
        # Add passed card - should stay in single layout
        passed_card = BaseTestCard(1, True, 0.1, 10.0)
        section.add_card(passed_card, passed=True)
        assert section.layout_mode == 'single'
        
        # Add failed card - should switch to split layout
        failed_card = BaseTestCard(2, False, 0.2, 20.0)
        section.add_card(failed_card, passed=False)
        assert section.layout_mode == 'split'
        
    def test_multiple_cards_in_split_mode(self, qtbot):
        """Test multiple cards in split layout"""
        from src.app.presentation.widgets.status_view_widgets import CardsSection
        
        section = CardsSection()
        qtbot.addWidget(section)
        section.show()
        
        # Add multiple cards
        for i in range(3):
            passed_card = BaseTestCard(i+1, True, 0.1, 10.0)
            section.add_card(passed_card, passed=True)
            
        for i in range(2):
            failed_card = BaseTestCard(i+4, False, 0.2, 20.0)
            section.add_card(failed_card, passed=False)
            
        assert len(section.passed_cards) == 3
        assert len(section.failed_cards) == 2
        assert section.layout_mode == 'split'
