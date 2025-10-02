# Unified Status View - Migration Playbook

**Version:** 1.0  
**Date:** October 2, 2025  
**Scope:** Practical implementation guide with testing at each stage  
**Focus:** Stop functionality, no pause/resume

---

## 🎯 Executive Summary

**Goal:** Transform test execution from popup dialogs to embedded card-based views in display area.

**Key Changes:**
- ❌ Remove: Pause/Resume buttons (skipped)
- ✅ Keep: Stop button (with proper cleanup)
- ✅ Sidebar: Regular footer/header (header shows "Status")
- ✅ Content: All test window controls except Compile & Results buttons
- ✅ Stop button: Properly terminates execution and returns to test window

**Timeline:** 4-5 weeks  
**Risk Level:** Medium  
**Testing:** Comprehensive at each phase

---

## 📐 Architecture Overview

### Before (Current):
```
ComparatorWindow
├── Sidebar (with Compile/Run/Results buttons)
└── Display Area (ComparatorDisplay)
    ├── File buttons
    ├── Editor
    └── Console

[Run clicked] → Opens CompareStatusWindow (QDialog popup)
```

### After (Target):
```
ComparatorWindow
├── Sidebar
└── Display Area
    ├── [Normal Mode] ComparatorDisplay
    └── [Status Mode] UnifiedStatusView
        ├── Sidebar (header: "Status", footer: Back/Options)
        ├── Content Area
        │   ├── File buttons (from parent)
        │   ├── Stop button
        │   ├── Progress Section
        │   └── Test Cards Section

[Run clicked] → Switches display area to UnifiedStatusView
[Stop/Back clicked] → Switches back to ComparatorDisplay
```

---

## 🏗️ Phase 1: Foundation & Base Widgets (Week 1)

### 1.1 Create Base Status View Widget

**File:** `src/app/presentation/widgets/unified_status_view.py`

```python
"""
Unified Status View - Base widget for all test executions.
Embedded in display area, not a popup dialog.
"""

from PySide6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QSplitter
from PySide6.QtCore import Qt, Signal
from src.app.presentation.widgets.sidebar import Sidebar
from src.app.presentation.styles.style import SPLITTER_STYLE


class BaseStatusView(QWidget):
    """
    Base unified status view for test execution.
    
    Signals:
        stopRequested: User clicked stop button
        backRequested: User clicked back button
    """
    
    stopRequested = Signal()
    backRequested = Signal()
    
    def __init__(self, test_type: str, parent=None):
        """
        Args:
            test_type: 'comparator', 'validator', or 'benchmarker'
            parent: Parent widget
        """
        super().__init__(parent)
        self.test_type = test_type
        self.parent_window = parent
        
        # Store test state
        self.tests_running = False
        self.total_tests = 0
        self.completed_tests = 0
        self.passed_tests = 0
        self.failed_tests = 0
        
        self._setup_ui()
        self._setup_styles()
        
    def _setup_ui(self):
        """Setup the main UI structure"""
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Create splitter for sidebar + content
        self.splitter = QSplitter(Qt.Horizontal)
        self.splitter.setStyleSheet(SPLITTER_STYLE)
        
        # Create sidebar
        self.sidebar = self._create_sidebar()
        
        # Create content area
        self.content_area = self._create_content_area()
        
        # Add to splitter
        self.splitter.addWidget(self.sidebar)
        self.splitter.addWidget(self.content_area)
        
        # Set sizes
        self.sidebar.setMinimumWidth(250)
        self.content_area.setMinimumWidth(600)
        self.splitter.setSizes([250, 850])
        
        main_layout.addWidget(self.splitter)
        
    def _create_sidebar(self) -> Sidebar:
        """Create sidebar with Status header and Back/Options footer"""
        sidebar = Sidebar("Status")
        
        # Add Help button
        sidebar.add_help_button()
        sidebar.add_footer_divider()
        
        # Create footer buttons
        from PySide6.QtWidgets import QPushButton
        from PySide6.QtGui import QFont
        
        back_btn = QPushButton("Back")
        back_btn.setObjectName("back_button")
        back_btn.clicked.connect(self._handle_back)
        
        options_btn = QPushButton("⚙️")
        options_btn.setObjectName("back_button")
        options_btn.setFont(QFont('Segoe UI', 14))
        options_btn.clicked.connect(self._handle_options)
        
        sidebar.setup_horizontal_footer_buttons(back_btn, options_btn)
        
        return sidebar
        
    def _create_content_area(self) -> QWidget:
        """Create main content area with controls and test cards"""
        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)
        
        # Import here to avoid circular imports
        from src.app.presentation.widgets.status_view_widgets import (
            TestControlsPanel,
            ProgressSection,
            TestCardsSection
        )
        
        # Control panel (file buttons + stop button)
        self.controls_panel = TestControlsPanel(self.test_type)
        self.controls_panel.stopClicked.connect(self._handle_stop)
        
        # Progress section
        self.progress_section = ProgressSection()
        
        # Test cards section
        self.cards_section = TestCardsSection()
        
        # Add to layout
        layout.addWidget(self.controls_panel)
        layout.addWidget(self.progress_section)
        layout.addWidget(self.cards_section, stretch=1)
        
        return content
        
    def _setup_styles(self):
        """Apply styling"""
        from src.app.presentation.styles.style import MATERIAL_COLORS
        self.setStyleSheet(f"""
            QWidget {{
                background: {MATERIAL_COLORS['surface']};
            }}
        """)
        
    def _handle_back(self):
        """Handle back button click"""
        if self.tests_running:
            # Confirm before going back during test execution
            from PySide6.QtWidgets import QMessageBox
            reply = QMessageBox.question(
                self,
                "Tests Running",
                "Tests are still running. Stop and go back?",
                QMessageBox.Yes | QMessageBox.No
            )
            if reply == QMessageBox.Yes:
                self._handle_stop()
                self.backRequested.emit()
        else:
            self.backRequested.emit()
            
    def _handle_stop(self):
        """Handle stop button click"""
        if self.tests_running:
            self.tests_running = False
            self.stopRequested.emit()
            self.controls_panel.update_stop_button_state(False)
            
    def _handle_options(self):
        """Handle options button click"""
        from src.app.core.config import ConfigView
        config_dialog = ConfigView(self)
        config_dialog.exec()
        
    # Signal handlers for test execution
    
    def on_tests_started(self, total: int):
        """Called when tests start"""
        self.tests_running = True
        self.total_tests = total
        self.completed_tests = 0
        self.passed_tests = 0
        self.failed_tests = 0
        self.controls_panel.update_stop_button_state(True)
        self.progress_section.reset(total)
        self.cards_section.clear()
        
    def on_test_running(self, current: int, total: int):
        """Called when a test starts"""
        self.progress_section.update_current_test(current, total)
        
    def on_test_completed(self, test_number: int, passed: bool, **kwargs):
        """Called when a test completes - override in subclasses"""
        self.completed_tests += 1
        if passed:
            self.passed_tests += 1
        else:
            self.failed_tests += 1
            
        self.progress_section.add_test_result(passed)
        self.progress_section.update_stats(
            self.completed_tests,
            self.total_tests,
            self.passed_tests,
            self.failed_tests
        )
        
    def on_all_tests_completed(self, all_passed: bool):
        """Called when all tests complete"""
        self.tests_running = False
        self.controls_panel.update_stop_button_state(False)
        self.progress_section.mark_complete(all_passed)
```

**Testing 1.1:**
```python
# tests/unit/test_base_status_view.py

def test_base_status_view_creation(qtbot):
    """Test status view can be created"""
    view = BaseStatusView('comparator')
    qtbot.addWidget(view)
    
    assert view.test_type == 'comparator'
    assert view.sidebar is not None
    assert view.content_area is not None
    
def test_stop_signal_emitted(qtbot):
    """Test stop button emits signal"""
    view = BaseStatusView('comparator')
    qtbot.addWidget(view)
    
    view.tests_running = True
    
    with qtbot.waitSignal(view.stopRequested):
        view._handle_stop()
        
def test_back_signal_emitted(qtbot):
    """Test back button emits signal"""
    view = BaseStatusView('comparator')
    qtbot.addWidget(view)
    
    with qtbot.waitSignal(view.backRequested):
        view._handle_back()
```

---

### 1.2 Create Status View Sub-Widgets

**File:** `src/app/presentation/widgets/status_view_widgets.py`

```python
"""
Sub-widgets for unified status view.
"""

from PySide6.QtWidgets import (QWidget, QHBoxLayout, QVBoxLayout, QPushButton,
                              QLabel, QFrame, QScrollArea, QStackedWidget)
from PySide6.QtCore import Qt, Signal
from src.app.presentation.styles.style import MATERIAL_COLORS


class TestControlsPanel(QWidget):
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
        
        # Stop button
        self.stop_button = QPushButton("⬛ Stop")
        self.stop_button.setObjectName("stop_button")
        self.stop_button.setFixedWidth(120)
        self.stop_button.clicked.connect(self.stopClicked.emit)
        self.stop_button.setEnabled(False)
        
        layout.addWidget(self.file_buttons_container, stretch=1)
        layout.addWidget(self.stop_button)
        
        self._apply_styles()
        
    def _apply_styles(self):
        self.stop_button.setStyleSheet(f"""
            QPushButton {{
                background: {MATERIAL_COLORS['error']};
                color: {MATERIAL_COLORS['on_error']};
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
                font-weight: bold;
                font-size: 14px;
            }}
            QPushButton:hover {{
                background: #d32f2f;
            }}
            QPushButton:disabled {{
                background: {MATERIAL_COLORS['surface_variant']};
                color: {MATERIAL_COLORS['outline']};
            }}
        """)
        
    def update_stop_button_state(self, running: bool):
        """Enable/disable stop button based on test state"""
        self.stop_button.setEnabled(running)
        if running:
            self.stop_button.setText("⬛ Stop Tests")
        else:
            self.stop_button.setText("✓ Stopped")
            

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
        
        # Add placeholders
        for i in range(total):
            label = QLabel("⏳")
            label.setAlignment(Qt.AlignCenter)
            label.setFixedSize(24, 24)
            self.layout.addWidget(label)
            
    def add_result(self, passed: bool):
        """Add test result"""
        self.results.append(passed)
        index = len(self.results) - 1
        
        if index < self.layout.count():
            label = self.layout.itemAt(index).widget()
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
                background: {MATERIAL_COLORS['surface_container']};
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
        
    def update(self, completed: int, total: int, passed: int, failed: int):
        """Update statistics"""
        percentage = (completed / total * 100) if total > 0 else 0
        self.percentage_label.setText(f"{percentage:.0f}%")
        self.passed_label.setText(f"Passed: {passed}")
        self.failed_label.setText(f"Failed: {failed}")
        
        # Color code passed label
        if passed > 0:
            self.passed_label.setStyleSheet(f"color: {MATERIAL_COLORS['primary']};")
        if failed > 0:
            self.failed_label.setStyleSheet(f"color: {MATERIAL_COLORS['error']};")


class TestCardsSection(QWidget):
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
        self.single_scroll.setWidget(self.single_container)
        
        self.main_layout.addWidget(self.single_scroll)
        
        # Split columns (hidden initially)
        self.passed_scroll = None
        self.failed_scroll = None
        
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
        self.passed_scroll.setWidget(self.passed_container)
        passed_main_layout.addWidget(self.passed_scroll)
        
        # Create failed column
        failed_widget = QWidget()
        failed_main_layout = QVBoxLayout(failed_widget)
        failed_main_layout.setContentsMargins(0, 0, 0, 0)
        
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
        if self.passed_scroll:
            self.passed_scroll.parent().deleteLater()
            self.passed_scroll = None
        if self.failed_scroll:
            self.failed_scroll.parent().deleteLater()
            self.failed_scroll = None
            
        # Show single column
        self.single_scroll.show()
        
    def _clear_layout(self, layout: QVBoxLayout):
        """Clear all widgets from layout"""
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
```

**Testing 1.2:**
```python
# tests/unit/test_status_view_widgets.py

def test_progress_section_creation(qtbot):
    """Test progress section can be created"""
    section = ProgressSection()
    qtbot.addWidget(section)
    
    assert section.visual_progress is not None
    assert section.stats_panel is not None
    
def test_progress_updates(qtbot):
    """Test progress updates correctly"""
    section = ProgressSection()
    qtbot.addWidget(section)
    
    section.reset(5)
    section.add_test_result(True)
    section.update_stats(1, 5, 1, 0)
    
    assert section.stats_panel.passed_label.text() == "Passed: 1"
    
def test_cards_section_split_layout(qtbot):
    """Test cards section switches to split on first failure"""
    section = TestCardsSection()
    qtbot.addWidget(section)
    
    card1 = QLabel("Test 1")
    card2 = QLabel("Test 2 Failed")
    
    section.add_card(card1, passed=True)
    assert section.layout_mode == 'single'
    
    section.add_card(card2, passed=False)
    assert section.layout_mode == 'split'
```

---

## 🏗️ Phase 2: Test Cards & Detail Views (Week 2)

### 2.1 Create Base Test Card

**File:** `src/app/presentation/widgets/test_cards.py`

```python
"""
Test card widgets for unified status view.
"""

from PySide6.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
from PySide6.QtCore import Qt, Signal
from src.app.presentation.styles.style import MATERIAL_COLORS


class BaseTestCard(QFrame):
    """Base test card widget"""
    
    clicked = Signal(int)  # Emits test number
    
    def __init__(self, test_number: int, passed: bool, time: float, memory: float, parent=None):
        super().__init__(parent)
        self.test_number = test_number
        self.passed = passed
        self.time = time
        self.memory = memory
        
        self._setup_ui()
        self._apply_styling()
        
    def _setup_ui(self):
        """Setup card UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(6)
        
        # Header row
        header_layout = QHBoxLayout()
        
        self.test_label = QLabel(f"Test #{self.test_number}")
        self.test_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        
        self.status_label = QLabel("✓ Passed" if self.passed else "✗ Failed")
        self.status_label.setStyleSheet(f"""
            color: {MATERIAL_COLORS['primary'] if self.passed else MATERIAL_COLORS['error']};
            font-weight: bold;
        """)
        
        header_layout.addWidget(self.test_label)
        header_layout.addStretch()
        header_layout.addWidget(self.status_label)
        
        # Metrics row
        metrics_layout = QHBoxLayout()
        
        time_label = QLabel(f"⏱️ {self.time:.3f}s")
        memory_label = QLabel(f"💾 {self.memory:.1f} MB")
        
        for label in [time_label, memory_label]:
            label.setStyleSheet("color: #666; font-size: 12px;")
            
        metrics_layout.addWidget(time_label)
        metrics_layout.addWidget(memory_label)
        metrics_layout.addStretch()
        
        layout.addLayout(header_layout)
        layout.addLayout(metrics_layout)
        
        # Make clickable
        self.setMouseTracking(True)
        self.setCursor(Qt.PointingHandCursor)
        
    def _apply_styling(self):
        """Apply card styling with tint"""
        bg_color = MATERIAL_COLORS['primary_container'] if self.passed else MATERIAL_COLORS['error_container']
        border_color = MATERIAL_COLORS['primary'] if self.passed else MATERIAL_COLORS['error']
        
        self.setStyleSheet(f"""
            QFrame {{
                background: {bg_color};
                border: 2px solid {border_color};
                border-radius: 10px;
            }}
            QFrame:hover {{
                border-width: 3px;
                background: {MATERIAL_COLORS['surface_bright']};
            }}
        """)
        
    def mousePressEvent(self, event):
        """Handle mouse click"""
        if event.button() == Qt.LeftButton:
            self.clicked.emit(self.test_number)
        super().mousePressEvent(event)


class ComparatorTestCard(BaseTestCard):
    """Comparator-specific test card"""
    
    def __init__(self, test_number: int, passed: bool, time: float, memory: float,
                 input_text: str, correct_output: str, test_output: str, parent=None):
        self.input_text = input_text
        self.correct_output = correct_output
        self.test_output = test_output
        super().__init__(test_number, passed, time, memory, parent)
```

**Testing 2.1:**
```python
def test_test_card_creation(qtbot):
    """Test card can be created"""
    card = BaseTestCard(1, True, 0.123, 45.6)
    qtbot.addWidget(card)
    
    assert card.test_number == 1
    assert card.passed == True
    
def test_card_click_signal(qtbot):
    """Test card emits click signal"""
    card = BaseTestCard(5, False, 1.5, 100.0)
    qtbot.addWidget(card)
    
    with qtbot.waitSignal(card.clicked) as blocker:
        qtbot.mouseClick(card, Qt.LeftButton)
    
    assert blocker.args[0] == 5
```

---

## 🔧 Phase 3: Runner Integration (Week 3)

### 3.1 Modify BaseRunner

**File:** `src/app/core/tools/base/base_runner.py`

**Changes:**
```python
# Add new methods to BaseRunner class

def set_parent_window(self, window):
    """
    Set parent window for display area integration.
    
    Args:
        window: Parent window (ComparatorWindow, ValidatorWindow, etc.)
    """
    self.parent_window = window

def _create_test_status_window(self):
    """
    Create status view (not window) - TEMPLATE METHOD.
    
    Subclasses override to create their specific status view.
    Returns a QWidget (not QDialog).
    """
    return None

def run_tests(self, test_count: int, **kwargs):
    """Run tests with unified status view"""
    self.test_count = test_count
    self.test_start_time = datetime.now()
    
    # Create status view (embedded widget, not popup)
    self.status_view = self._create_test_status_window()
    
    if self.status_view:
        # Connect stop signal
        self.status_view.stopRequested.connect(self.stop)
        self.status_view.backRequested.connect(self._handle_back_request)
        
        # Integrate into display area
        if hasattr(self, 'parent_window'):
            self._integrate_status_view()
        
        # Notify view that tests are starting
        self.status_view.on_tests_started(test_count)
    
    # Create worker and thread (existing code)
    self.worker = self._create_test_worker(test_count, **kwargs)
    self.thread = QThread()
    
    # Move worker to thread
    self.worker.moveToThread(self.thread)
    
    # Connect worker signals to status view
    if self.status_view:
        self._connect_worker_to_status_view(self.worker, self.status_view)
    
    # Connect worker signals to external listeners
    self._connect_worker_signals(self.worker)
    
    # Connect database saving
    self.worker.allTestsCompleted.connect(self._save_test_results)
    
    # Set up thread lifecycle
    self.thread.started.connect(self.worker.run_tests)
    self.worker.allTestsCompleted.connect(self.thread.quit)
    self.worker.allTestsCompleted.connect(self.worker.deleteLater)
    self.thread.finished.connect(self.thread.deleteLater)
    
    # Start the thread
    self.thread.start()
    
    logger.debug(f"Started {test_count} {self.test_type} tests")

def _integrate_status_view(self):
    """Integrate status view into parent window's display area"""
    if not hasattr(self, 'parent_window'):
        return
        
    # Store original content for restoration
    self.original_display_content = self.parent_window.display_area.layout.itemAt(0)
    if self.original_display_content:
        self.original_display_content = self.original_display_content.widget()
    
    # Replace display area content with status view
    self.parent_window.display_area.set_content(self.status_view)

def _handle_back_request(self):
    """Handle back button from status view"""
    if hasattr(self, 'parent_window') and self.original_display_content:
        # Restore original display content
        self.parent_window.display_area.set_content(self.original_display_content)

def stop(self) -> None:
    """Stop execution and restore display"""
    # Stop compilation
    if hasattr(self, 'compiler') and self.compiler:
        self.compiler.stop()
    
    # Stop worker
    if self.worker and hasattr(self.worker, 'stop'):
        self.worker.stop()
    
    # Clean up thread
    try:
        if self.thread and hasattr(self.thread, 'isRunning') and self.thread.isRunning():
            self.thread.quit()
            if not self.thread.wait(3000):  # Wait up to 3 seconds
                self.thread.terminate()
                self.thread.wait(1000)
    except RuntimeError:
        pass
    
    # Restore display area
    self._handle_back_request()
    
    logger.debug(f"Stopped {self.test_type} runner")

def _connect_worker_to_status_view(self, worker, status_view):
    """Connect worker signals to status view"""
    if hasattr(worker, 'testStarted') and hasattr(status_view, 'on_test_running'):
        worker.testStarted.connect(status_view.on_test_running)
    
    if hasattr(worker, 'testCompleted') and hasattr(status_view, 'on_test_completed'):
        worker.testCompleted.connect(status_view.on_test_completed)
    
    if hasattr(worker, 'allTestsCompleted') and hasattr(status_view, 'on_all_tests_completed'):
        worker.allTestsCompleted.connect(status_view.on_all_tests_completed)
```

**Testing 3.1:**
```python
def test_runner_parent_window_integration(qtbot):
    """Test runner integrates with parent window"""
    # Create mock parent window
    from unittest.mock import Mock
    parent = Mock()
    parent.display_area = Mock()
    
    runner = Comparator(workspace_dir=tmp_path)
    runner.set_parent_window(parent)
    
    assert runner.parent_window == parent

def test_runner_stop_restores_display(qtbot):
    """Test stop restores original display content"""
    # Setup test environment
    ...
```

---

### 3.2 Update Comparator Implementation

**File:** `src/app/core/tools/comparator.py`

```python
def _create_test_status_window(self):
    """Create comparator-specific status view"""
    from src.app.presentation.views.comparator.comparator_status_view import ComparatorStatusView
    return ComparatorStatusView()
```

**New File:** `src/app/presentation/views/comparator/comparator_status_view.py`

```python
"""Comparator-specific status view"""

from src.app.presentation.widgets.unified_status_view import BaseStatusView
from src.app.presentation.widgets.test_cards import ComparatorTestCard


class ComparatorStatusView(BaseStatusView):
    """Status view for comparator tests"""
    
    def __init__(self, parent=None):
        super().__init__('comparator', parent)
        
    def on_test_completed(self, test_number: int, passed: bool, 
                         input_text: str, correct_output: str, test_output: str):
        """Handle comparator test completion"""
        # Call parent to update counters
        super().on_test_completed(test_number, passed)
        
        # Create comparator-specific card with mock time/memory for now
        # TODO: Add actual time/memory tracking in Phase 4
        card = ComparatorTestCard(
            test_number=test_number,
            passed=passed,
            time=0.0,  # Placeholder
            memory=0.0,  # Placeholder
            input_text=input_text,
            correct_output=correct_output,
            test_output=test_output
        )
        
        # Add card to section
        self.cards_section.add_card(card, passed)
```

---

### 3.3 Update ComparatorWindow

**File:** `src/app/presentation/views/comparator/comparator_window.py`

```python
def handle_action_button(self, button_text):
    if button_text == 'Compile':
        # ... existing compile code ...
        
    elif button_text == 'Run':
        # NEW: Set parent window reference
        self.comparator.set_parent_window(self)
        
        # Run tests (will now integrate with display area)
        test_count = self.test_count_slider.value()
        self.comparator.run_comparison_test(test_count)
        
    elif button_text == 'Results':
        # ... existing results code ...
```

**Testing 3.3:**
```python
def test_comparator_run_shows_status_view(qtbot):
    """Test running comparator shows status view in display area"""
    window = ComparatorWindow()
    qtbot.addWidget(window)
    
    # Compile first
    window.comparator.compile_all()
    qtbot.wait(2000)
    
    # Run tests
    window.handle_action_button('Run')
    qtbot.wait(500)
    
    # Check display area contains status view
    current_widget = window.display_area.layout.itemAt(0).widget()
    assert isinstance(current_widget, BaseStatusView)
```

---

## 🏗️ Phase 4: Time/Memory Tracking (Week 4)

### 4.1 Add Tracking to ComparisonTestWorker

**File:** `src/app/core/tools/specialized/comparison_test_worker.py`

```python
# Update signal signature
testCompleted = Signal(int, bool, str, str, str, float, float)
# Added: time (float), memory (float)

# Add tracking method
def _run_single_test_with_metrics(self, test_number: int) -> Optional[Dict[str, Any]]:
    """Run test with time and memory tracking"""
    import psutil
    
    total_time = 0.0
    peak_memory = 0.0
    
    # Generator stage
    gen_start = time.time()
    gen_process = subprocess.Popen(
        self.execution_commands['generator'],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
    )
    
    # Monitor generator memory
    try:
        proc = psutil.Process(gen_process.pid)
        while gen_process.poll() is None:
            mem = proc.memory_info().rss / (1024 * 1024)
            peak_memory = max(peak_memory, mem)
            time.sleep(0.01)
    except:
        pass
        
    gen_output, gen_error = gen_process.communicate(timeout=10)
    total_time += time.time() - gen_start
    
    # Test and correct stages (similar tracking)
    # ... existing code with added timing and memory tracking ...
    
    return {
        'test_number': test_number,
        'passed': passed,
        'input': input_data,
        'correct_output': correct_output,
        'test_output': test_output,
        'time': total_time,
        'memory': peak_memory
    }

# Update run_tests to use new tracking
def run_tests(self):
    """Run tests with metrics"""
    all_passed = True
    completed_tests = 0
    
    with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
        future_to_test = {
            executor.submit(self._run_single_test_with_metrics, i): i 
            for i in range(1, self.test_count + 1)
        }
        
        for future in as_completed(future_to_test):
            if not self.is_running:
                break
                
            test_number = future_to_test[future]
            completed_tests += 1
            
            try:
                result = future.result()
                if result:
                    with self._results_lock:
                        self.test_results.append(result)
                    
                    self.testStarted.emit(completed_tests, self.test_count)
                    self.testCompleted.emit(
                        result['test_number'],
                        result['passed'],
                        result['input'],
                        result['correct_output'],
                        result['test_output'],
                        result['time'],  # NEW
                        result['memory']  # NEW
                    )
                    
                    if not result['passed']:
                        all_passed = False
            except Exception as e:
                logger.error(f"Test {test_number} error: {e}")
                all_passed = False
    
    self.allTestsCompleted.emit(all_passed)
```

### 4.2 Update ComparatorStatusView

**File:** `src/app/presentation/views/comparator/comparator_status_view.py`

```python
def on_test_completed(self, test_number: int, passed: bool, 
                     input_text: str, correct_output: str, test_output: str,
                     time: float, memory: float):  # NEW PARAMETERS
    """Handle comparator test completion with metrics"""
    super().on_test_completed(test_number, passed)
    
    # Create card with actual time/memory
    card = ComparatorTestCard(
        test_number=test_number,
        passed=passed,
        time=time,
        memory=memory,
        input_text=input_text,
        correct_output=correct_output,
        test_output=test_output
    )
    
    self.cards_section.add_card(card, passed)
```

**Testing 4.1:**
```python
def test_comparison_worker_tracks_metrics(tmp_path, qtbot):
    """Test worker tracks time and memory"""
    # Create test files and executables
    setup_test_environment(tmp_path)
    
    worker = ComparisonTestWorker(...)
    
    results = []
    worker.testCompleted.connect(lambda *args: results.append(args))
    
    worker.run_tests()
    qtbot.wait(3000)
    
    assert len(results) > 0
    # Check result has time and memory
    test_num, passed, inp, correct, test_out, time, memory = results[0]
    assert isinstance(time, float)
    assert isinstance(memory, float)
    assert time > 0
```

---

## 🏗️ Phase 5: Extend to Other Test Types (Week 5)

### 5.1 Validator Status View

**File:** `src/app/presentation/views/validator/validator_status_view.py`

```python
from src.app.presentation.widgets.unified_status_view import BaseStatusView
from src.app.presentation.widgets.test_cards import ValidatorTestCard


class ValidatorStatusView(BaseStatusView):
    """Status view for validator tests"""
    
    def __init__(self, parent=None):
        super().__init__('validator', parent)
        
    def on_test_completed(self, test_number: int, passed: bool,
                         input_data: str, test_output: str,
                         validation_message: str, error_details: str,
                         validator_exit_code: int, time: float, memory: float):
        """Handle validator test completion"""
        super().on_test_completed(test_number, passed)
        
        card = ValidatorTestCard(
            test_number=test_number,
            passed=passed,
            time=time,
            memory=memory,
            input_data=input_data,
            test_output=test_output,
            validation_message=validation_message,
            error_details=error_details,
            validator_exit_code=validator_exit_code
        )
        
        self.cards_section.add_card(card, passed)
```

### 5.2 Benchmarker Status View

Already has time/memory tracking, just needs view adaptation.

**Testing 5.1:**
```python
def test_all_status_views_work(qtbot):
    """Integration test for all status views"""
    for test_type in ['comparator', 'validator', 'benchmarker']:
        view = create_status_view(test_type)
        qtbot.addWidget(view)
        
        # Simulate test execution
        view.on_tests_started(5)
        view.on_test_running(1, 5)
        view.on_test_completed(1, True, **test_data[test_type])
        
        assert view.completed_tests == 1
        assert view.passed_tests == 1
```

---

## 🧪 Phase 6: Comprehensive Testing

### Integration Tests

**File:** `tests/integration/test_unified_status_view.py`

```python
def test_full_comparator_workflow(qtbot, tmp_path):
    """End-to-end test of comparator with unified status view"""
    # Setup
    setup_workspace(tmp_path)
    window = ComparatorWindow()
    qtbot.addWidget(window)
    
    # Compile
    window.handle_action_button('Compile')
    qtbot.wait(2000)
    
    # Run tests
    window.handle_action_button('Run')
    qtbot.wait(500)
    
    # Verify status view is shown
    current = window.display_area.layout.itemAt(0).widget()
    assert isinstance(current, ComparatorStatusView)
    
    # Wait for tests to complete
    qtbot.wait(5000)
    
    # Verify cards were added
    assert len(current.cards_section.passed_cards) > 0
    
    # Click back
    current._handle_back()
    qtbot.wait(200)
    
    # Verify restored to original content
    current = window.display_area.layout.itemAt(0).widget()
    assert isinstance(current, ComparatorDisplay)

def test_stop_button_terminates_properly(qtbot, tmp_path):
    """Test stop button properly terminates execution"""
    setup_workspace(tmp_path)
    window = ComparatorWindow()
    qtbot.addWidget(window)
    
    window.handle_action_button('Compile')
    qtbot.wait(2000)
    
    # Start long-running tests
    window.test_count_slider.setValue(100)
    window.handle_action_button('Run')
    qtbot.wait(500)
    
    status_view = window.display_area.layout.itemAt(0).widget()
    
    # Click stop after 2 seconds
    qtbot.wait(2000)
    status_view._handle_stop()
    qtbot.wait(500)
    
    # Verify stopped
    assert not status_view.tests_running
    assert status_view.comparator.worker is None or not status_view.comparator.worker.is_running
```

---

## 📋 Migration Checklist

### Pre-Migration
- [ ] Review this playbook with team
- [ ] Set up test environment
- [ ] Create feature branch: `feature/unified-status-view`
- [ ] Backup current code

### Phase 1: Foundation
- [ ] Create `unified_status_view.py`
- [ ] Create `status_view_widgets.py`
- [ ] Write unit tests for base widgets
- [ ] Run tests: `pytest tests/unit/test_base_status_view.py -v`
- [ ] Code review

### Phase 2: Cards
- [ ] Create `test_cards.py`
- [ ] Implement BaseTestCard
- [ ] Write tests for cards
- [ ] Run tests: `pytest tests/unit/test_test_cards.py -v`
- [ ] Code review

### Phase 3: Integration
- [ ] Modify BaseRunner
- [ ] Create ComparatorStatusView
- [ ] Update ComparatorWindow
- [ ] Test with Comparator manually
- [ ] Write integration tests
- [ ] Run tests: `pytest tests/integration/test_comparator_status.py -v`
- [ ] Code review

### Phase 4: Metrics
- [ ] Update ComparisonTestWorker signals
- [ ] Add time/memory tracking
- [ ] Update ComparatorStatusView
- [ ] Test metric accuracy
- [ ] Run tests: `pytest tests/unit/test_comparison_worker_metrics.py -v`
- [ ] Code review

### Phase 5: Extend
- [ ] Create ValidatorStatusView
- [ ] Update ValidatorTestWorker
- [ ] Create BenchmarkerStatusView
- [ ] Test all three types
- [ ] Run tests: `pytest tests/integration/test_all_status_views.py -v`
- [ ] Code review

### Phase 6: Testing & Polish
- [ ] Comprehensive integration tests
- [ ] Manual testing all scenarios
- [ ] Performance testing (100+ tests)
- [ ] Stop button stress testing
- [ ] UI/UX review
- [ ] Documentation updates
- [ ] Final code review

### Deployment
- [ ] Merge to main branch
- [ ] Update changelog
- [ ] Deploy to production
- [ ] Monitor for issues

---

## 🎯 Success Criteria

**Must Have:**
- ✅ All three test types use unified status view
- ✅ Stop button properly terminates execution
- ✅ Display area switches correctly
- ✅ Time/memory tracked for all types
- ✅ Cards display with proper tinting
- ✅ Layout switches from 1 to 2 columns on first failure
- ✅ All existing tests still pass

**Nice to Have:**
- ✅ Card click shows detail view
- ✅ Smooth animations
- ✅ Progress bar with emojis
- ✅ Performance optimized for 100+ tests

---

## 🔧 Troubleshooting

### Issue: Display area doesn't switch
**Solution:** Check `parent_window` is set via `runner.set_parent_window(self)`

### Issue: Stop button doesn't work
**Solution:** Verify signal connection: `status_view.stopRequested.connect(self.stop)`

### Issue: Tests don't stop immediately
**Solution:** Workers check `self.is_running` flag, but current test completes first (expected)

### Issue: Time/memory metrics are 0
**Solution:** Check psutil is installed and process monitoring is working

### Issue: Cards don't appear
**Solution:** Verify signal connections between worker and status view

---

**End of Playbook**  
**Total Lines: 988**
