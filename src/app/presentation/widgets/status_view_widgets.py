"""
Sub-widgets for unified status view.
"""

from PySide6.QtWidgets import (QWidget, QHBoxLayout, QVBoxLayout, QPushButton,
                              QLabel, QFrame, QScrollArea, QStackedWidget)
from PySide6.QtCore import Qt, Signal
from src.app.presentation.styles.style import MATERIAL_COLORS


class ControlsPanel(QWidget):
    """Control panel with file buttons and stop button"""
    
    stopClicked = Signal()
    
    def __init__(self, test_type: str, parent=None):
        super().__init__(parent)
        self.test_type = test_type
        self._setup_ui()
        
    def _setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # File buttons container (will be populated by parent)
        self.file_buttons_container = QWidget()
        self.file_buttons_layout = QHBoxLayout(self.file_buttons_container)
        self.file_buttons_layout.setContentsMargins(0, 0, 0, 0)
        
        # Note: Stop button removed - now in sidebar
        # The stopClicked signal is kept for backwards compatibility
        
        layout.addWidget(self.file_buttons_container, stretch=1)
        
        self._apply_styles()
        
    def _apply_styles(self):
        # Styles for file buttons container only now
        pass
        
    def update_stop_button_state(self, running: bool):
        """Kept for backwards compatibility - stop button now in sidebar"""
        pass
            

class ProgressSection(QWidget):
    """Progress bar with visual indicators and statistics"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
        
    def _setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Visual progress (80% width)
        self.visual_progress = VisualProgressBar()
        
        # Stats panel (20% width)
        self.stats_panel = StatsPanel()
        
        layout.addWidget(self.visual_progress, stretch=4)
        layout.addWidget(self.stats_panel, stretch=1)
        
    def reset(self, total_tests: int):
        """Reset for new test run"""
        self.visual_progress.reset(total_tests)
        self.stats_panel.reset()
        
    def add_test_result(self, passed: bool):
        """Add test result to visual progress"""
        self.visual_progress.add_result(passed)
        
    def update_stats(self, completed: int, total: int, passed: int, failed: int):
        """Update statistics display"""
        self.stats_panel.update(completed, total, passed, failed)
        
    def update_current_test(self, current: int, total: int):
        """Update current test indicator"""
        self.visual_progress.set_current(current, total)
        
    def mark_complete(self, all_passed: bool):
        """Mark tests as complete"""
        self.visual_progress.mark_complete(all_passed)


class VisualProgressBar(QWidget):
    """Visual progress bar with tick/cross emojis"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.results = []
        self.total = 0
        self.current = 0
        self._setup_ui()
        
    def _setup_ui(self):
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(8, 8, 8, 8)
        self.layout.setSpacing(4)
        
        self.setStyleSheet(f"""
            QWidget {{
                background: {MATERIAL_COLORS['surface_variant']};
                border: 1px solid {MATERIAL_COLORS['outline']};
                border-radius: 8px;
            }}
        """)
        
    def reset(self, total: int):
        """Reset progress bar"""
        self.results = []
        self.total = total
        self.current = 0
        self._clear_layout()
        
        # Add placeholders (limit to 50 for UI performance)
        display_count = min(total, 50)
        for i in range(display_count):
            label = QLabel("⏳")
            label.setAlignment(Qt.AlignCenter)
            label.setFixedSize(24, 24)
            self.layout.addWidget(label)
            
        # Add indicator if showing subset
        if total > 50:
            more_label = QLabel(f"+{total - 50}")
            more_label.setAlignment(Qt.AlignCenter)
            more_label.setStyleSheet("color: #666; font-size: 10px;")
            self.layout.addWidget(more_label)
            
    def add_result(self, passed: bool):
        """Add test result"""
        self.results.append(passed)
        index = len(self.results) - 1
        
        # Only update if within display limit
        if index < min(self.total, 50) and index < self.layout.count():
            label = self.layout.itemAt(index).widget()
            if isinstance(label, QLabel):
                label.setText("✓" if passed else "✗")
                label.setStyleSheet(f"""
                    color: {MATERIAL_COLORS['primary'] if passed else MATERIAL_COLORS['error']};
                    font-size: 16px;
                    font-weight: bold;
                """)
            
    def set_current(self, current: int, total: int):
        """Highlight current test"""
        self.current = current
        
    def mark_complete(self, all_passed: bool):
        """Mark as complete"""
        # Visual indication that all tests are done
        pass
        
    def _clear_layout(self):
        """Clear all widgets from layout"""
        while self.layout.count():
            item = self.layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()


class StatsPanel(QWidget):
    """Statistics display panel"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
        
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(4)
        
        self.percentage_label = QLabel("0%")
        self.passed_label = QLabel("Passed: 0")
        self.failed_label = QLabel("Failed: 0")
        
        for label in [self.percentage_label, self.passed_label, self.failed_label]:
            label.setAlignment(Qt.AlignCenter)
            layout.addWidget(label)
            
        self.setStyleSheet(f"""
            QWidget {{
                background: {MATERIAL_COLORS['surface_variant']};
                border: 1px solid {MATERIAL_COLORS['outline']};
                border-radius: 8px;
            }}
            QLabel {{
                color: {MATERIAL_COLORS['on_surface']};
                font-weight: bold;
                font-size: 13px;
            }}
        """)
        
    def reset(self):
        """Reset statistics"""
        self.percentage_label.setText("0%")
        self.passed_label.setText("Passed: 0")
        self.failed_label.setText("Failed: 0")
        
        # Reset styles
        self.passed_label.setStyleSheet("")
        self.failed_label.setStyleSheet("")
        
    def update(self, completed: int, total: int, passed: int, failed: int):
        """Update statistics"""
        percentage = (completed / total * 100) if total > 0 else 0
        self.percentage_label.setText(f"{percentage:.0f}%")
        self.passed_label.setText(f"Passed: {passed}")
        self.failed_label.setText(f"Failed: {failed}")
        
        # Color code labels
        if passed > 0:
            self.passed_label.setStyleSheet(f"color: {MATERIAL_COLORS['primary']}; font-weight: bold; font-size: 13px;")
        if failed > 0:
            self.failed_label.setStyleSheet(f"color: {MATERIAL_COLORS['error']}; font-weight: bold; font-size: 13px;")


class CardsSection(QWidget):
    """Container for test cards with dynamic layout"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout_mode = 'single'  # 'single' or 'split'
        self.passed_cards = []
        self.failed_cards = []
        self._setup_ui()
        
    def _setup_ui(self):
        self.main_layout = QHBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(16)
        
        # Single column initially
        self.single_scroll = self._create_scroll_area()
        self.single_container = QWidget()
        self.single_layout = QVBoxLayout(self.single_container)
        self.single_layout.setAlignment(Qt.AlignTop)
        self.single_layout.setSpacing(8)
        self.single_scroll.setWidget(self.single_container)
        
        self.main_layout.addWidget(self.single_scroll)
        
        # Split columns (will be created when needed)
        self.passed_scroll = None
        self.failed_scroll = None
        self.passed_container = None
        self.failed_container = None
        self.passed_layout = None
        self.failed_layout = None
        
    def _create_scroll_area(self) -> QScrollArea:
        """Create configured scroll area"""
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setStyleSheet(f"""
            QScrollArea {{
                border: 1px solid {MATERIAL_COLORS['outline']};
                border-radius: 8px;
                background: transparent;
            }}
        """)
        return scroll
        
    def clear(self):
        """Clear all cards"""
        self.passed_cards = []
        self.failed_cards = []
        self._clear_layout(self.single_layout)
        
        if self.layout_mode == 'split':
            self._switch_to_single_layout()
            
    def add_card(self, card: QWidget, passed: bool):
        """Add test card"""
        if passed:
            self.passed_cards.append(card)
            if self.layout_mode == 'single':
                self.single_layout.addWidget(card)
            else:
                self.passed_layout.addWidget(card)
        else:
            self.failed_cards.append(card)
            if self.layout_mode == 'single' and len(self.failed_cards) == 1:
                # First failure - switch to split layout
                self._switch_to_split_layout()
            if self.layout_mode == 'split':
                self.failed_layout.addWidget(card)
                
    def _switch_to_split_layout(self):
        """Switch from single to split column layout"""
        if self.layout_mode == 'split':
            return
            
        self.layout_mode = 'split'
        
        # Hide single column
        self.single_scroll.hide()
        
        # Create passed column
        passed_widget = QWidget()
        passed_main_layout = QVBoxLayout(passed_widget)
        passed_main_layout.setContentsMargins(0, 0, 0, 0)
        passed_main_layout.setSpacing(8)
        
        passed_title = QLabel("✓ Passed Tests")
        passed_title.setStyleSheet(f"""
            QLabel {{
                background: {MATERIAL_COLORS['primary_container']};
                color: {MATERIAL_COLORS['on_primary_container']};
                padding: 8px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 14px;
            }}
        """)
        passed_main_layout.addWidget(passed_title)
        
        self.passed_scroll = self._create_scroll_area()
        self.passed_container = QWidget()
        self.passed_layout = QVBoxLayout(self.passed_container)
        self.passed_layout.setAlignment(Qt.AlignTop)
        self.passed_layout.setSpacing(8)
        self.passed_scroll.setWidget(self.passed_container)
        passed_main_layout.addWidget(self.passed_scroll)
        
        # Create failed column
        failed_widget = QWidget()
        failed_main_layout = QVBoxLayout(failed_widget)
        failed_main_layout.setContentsMargins(0, 0, 0, 0)
        failed_main_layout.setSpacing(8)
        
        failed_title = QLabel("✗ Failed Tests")
        failed_title.setStyleSheet(f"""
            QLabel {{
                background: {MATERIAL_COLORS['error_container']};
                color: {MATERIAL_COLORS['on_error_container']};
                padding: 8px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 14px;
            }}
        """)
        failed_main_layout.addWidget(failed_title)
        
        self.failed_scroll = self._create_scroll_area()
        self.failed_container = QWidget()
        self.failed_layout = QVBoxLayout(self.failed_container)
        self.failed_layout.setAlignment(Qt.AlignTop)
        self.failed_layout.setSpacing(8)
        self.failed_scroll.setWidget(self.failed_container)
        failed_main_layout.addWidget(self.failed_scroll)
        
        # Add columns to main layout
        self.main_layout.addWidget(passed_widget)
        self.main_layout.addWidget(failed_widget)
        
        # Move existing passed cards
        for card in self.passed_cards:
            card.setParent(None)
            self.passed_layout.addWidget(card)
            
    def _switch_to_single_layout(self):
        """Switch back to single column (for reset)"""
        if self.layout_mode == 'single':
            return
            
        self.layout_mode = 'single'
        
        # Remove split columns
        if self.passed_scroll and self.passed_scroll.parent():
            self.passed_scroll.parent().deleteLater()
            self.passed_scroll = None
            self.passed_container = None
            self.passed_layout = None
            
        if self.failed_scroll and self.failed_scroll.parent():
            self.failed_scroll.parent().deleteLater()
            self.failed_scroll = None
            self.failed_container = None
            self.failed_layout = None
            
        # Show single column
        self.single_scroll.show()
        
    def _clear_layout(self, layout: QVBoxLayout):
        """Clear all widgets from layout"""
        if layout is None:
            return
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
