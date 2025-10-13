"""
Sub-widgets for unified status view.
"""

from PySide6.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QPushButton,
    QLabel,
    QFrame,
    QScrollArea,
    QStackedWidget,
)
from PySide6.QtCore import Qt, Signal
from src.app.presentation.styles.style import MATERIAL_COLORS
from src.app.presentation.styles.components.status_view_styles import (
    PROGRESS_SECTION_CONTAINER_STYLE,
    VISUAL_PROGRESS_BAR_STYLE,
    SEGMENT_DEFAULT_STYLE,
    get_segment_style,
    STATS_PANEL_STYLE,
    STATS_LABEL_PASSED_STYLE,
    STATS_LABEL_FAILED_STYLE,
    STATS_PERCENTAGE_STYLE,
    CARDS_SECTION_SCROLL_STYLE,
    CARDS_SECTION_TITLE_PASSED_STYLE,
    CARDS_SECTION_TITLE_FAILED_STYLE,
)


class ProgressSection(QWidget):
    """Progress bar with visual indicators and statistics"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

        # Visual progress (75% width)
        self.visual_progress = VisualProgressBar()

        # Stats panel (25% width)
        self.stats_panel = StatsPanel()

        layout.addWidget(self.visual_progress, stretch=3)
        layout.addWidget(self.stats_panel, stretch=1)

        # Apply container styling
        self.setStyleSheet(PROGRESS_SECTION_CONTAINER_STYLE)

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
    """Segmented progress bar with color-coded blocks"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.results = []
        self.total = 0
        self.current = 0
        self.segments = []
        self.segment_size = 1  # How many tests per segment
        self._setup_ui()

    def _setup_ui(self):
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(12, 12, 12, 12)
        self.layout.setSpacing(0)  # No spacing for connected segments

        self.setStyleSheet(VISUAL_PROGRESS_BAR_STYLE)

    def reset(self, total: int):
        """Reset progress bar"""
        self.results = []
        self.total = total
        self.current = 0
        self._clear_layout()
        self.segments = []

        # Calculate optimal segment count and size
        if total <= 100:
            # Show individual segments for small test counts
            segment_count = total
            self.segment_size = 1
        elif total <= 200:
            # 1 segment = 2 tests
            segment_count = 100
            self.segment_size = 2
        elif total <= 500:
            # 1 segment = ~5 tests
            segment_count = 100
            self.segment_size = total // 100
        else:
            # 1 segment = ~10+ tests
            segment_count = 100
            self.segment_size = total // 100

        # Create segments
        for i in range(segment_count):
            segment = QFrame()
            segment.setFixedSize(max(5, 800 // segment_count), 28)

            # Apply default style with no border radius on inner sides for connected look
            if i == 0:
                # First segment - round left side only
                segment.setStyleSheet(
                    SEGMENT_DEFAULT_STYLE.replace(
                        "border-radius: 3px;", "border-radius: 3px 0 0 3px;"
                    )
                )
            elif i == segment_count - 1:
                # Last segment - round right side only
                segment.setStyleSheet(
                    SEGMENT_DEFAULT_STYLE.replace(
                        "border-radius: 3px;", "border-radius: 0 3px 3px 0;"
                    )
                )
            else:
                # Middle segments - no rounding
                segment.setStyleSheet(
                    SEGMENT_DEFAULT_STYLE.replace(
                        "border-radius: 3px;", "border-radius: 0;"
                    )
                )

            # Add tooltip
            start_test = i * self.segment_size + 1
            end_test = min((i + 1) * self.segment_size, total)
            if self.segment_size == 1:
                segment.setToolTip(f"Test {start_test}")
            else:
                segment.setToolTip(f"Tests {start_test}-{end_test}")

            self.layout.addWidget(segment)
            self.segments.append(
                {
                    "widget": segment,
                    "passed": 0,
                    "failed": 0,
                    "total": 0,
                    "position": (
                        "first"
                        if i == 0
                        else "last" if i == segment_count - 1 else "middle"
                    ),
                }
            )

        # Add indicator if using aggregated segments
        if self.segment_size > 1:
            info_label = QLabel(f"({self.segment_size} tests/segment)")
            info_label.setAlignment(Qt.AlignCenter)
            info_label.setStyleSheet("color: #666; font-size: 9px;")
            self.layout.addWidget(info_label)

    def add_result(self, passed: bool):
        """Add test result"""
        self.results.append(passed)
        test_index = len(self.results) - 1

        # Calculate which segment this test belongs to
        segment_index = test_index // self.segment_size

        if segment_index < len(self.segments):
            segment = self.segments[segment_index]
            segment["total"] += 1
            if passed:
                segment["passed"] += 1
            else:
                segment["failed"] += 1

            # Update segment color based on results
            self._update_segment_color(segment_index)

    def _update_segment_color(self, segment_index: int):
        """Update segment color based on its test results"""
        segment = self.segments[segment_index]
        widget = segment["widget"]
        passed = segment["passed"]
        failed = segment["failed"]
        total = segment["total"]
        position = segment["position"]

        # Determine state and apply appropriate gradient style
        if total == 0:
            state = "default"
        elif failed == 0:
            state = "passed"
        elif passed == 0:
            state = "failed"
        else:
            # Mixed results - determine by majority
            if passed > failed:
                state = "mixed_pass"
            else:
                state = "mixed_fail"

        # Get base style and adjust border radius based on position
        base_style = get_segment_style(state)
        if position == "first":
            style = base_style.replace(
                "border-radius: 3px;", "border-radius: 3px 0 0 3px;"
            )
        elif position == "last":
            style = base_style.replace(
                "border-radius: 3px;", "border-radius: 0 3px 3px 0;"
            )
        else:
            style = base_style.replace("border-radius: 3px;", "border-radius: 0;")

        widget.setStyleSheet(style)

        # Update tooltip with current stats
        start_test = segment_index * self.segment_size + 1
        end_test = min((segment_index + 1) * self.segment_size, self.total)
        if self.segment_size == 1:
            tooltip = f"Test {start_test}: {'Passed' if passed > 0 else 'Failed'}"
        else:
            tooltip = (
                f"Tests {start_test}-{end_test}\nPassed: {passed}, Failed: {failed}"
            )
        widget.setToolTip(tooltip)

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
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(8)

        self.percentage_label = QLabel("0%")
        self.percentage_label.setAlignment(Qt.AlignCenter)
        self.percentage_label.setStyleSheet(STATS_PERCENTAGE_STYLE)

        self.passed_label = QLabel("Passed: 0")
        self.passed_label.setAlignment(Qt.AlignCenter)

        self.failed_label = QLabel("Failed: 0")
        self.failed_label.setAlignment(Qt.AlignCenter)

        layout.addWidget(self.percentage_label)
        layout.addSpacing(4)
        layout.addWidget(self.passed_label)
        layout.addWidget(self.failed_label)
        layout.addStretch()

        self.setStyleSheet(STATS_PANEL_STYLE)

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

        # Color code labels with new gradient-aware styles
        if passed > 0:
            self.passed_label.setStyleSheet(STATS_LABEL_PASSED_STYLE)
        if failed > 0:
            self.failed_label.setStyleSheet(STATS_LABEL_FAILED_STYLE)


class CardsSection(QWidget):
    """Container for test cards with dynamic layout"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout_mode = "single"  # 'single' or 'split'
        self.passed_cards = []
        self.failed_cards = []
        self._setup_ui()

    def _setup_ui(self):
        self.main_layout = QHBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(16)

        # Always start with passed column (single mode will show passed tests)
        passed_widget = QWidget()
        passed_main_layout = QVBoxLayout(passed_widget)
        passed_main_layout.setContentsMargins(0, 0, 0, 0)
        passed_main_layout.setSpacing(8)

        # Passed title with counter
        self.passed_title = QLabel("✓ Passed Tests (0)")
        self.passed_title.setStyleSheet(CARDS_SECTION_TITLE_PASSED_STYLE)
        passed_main_layout.addWidget(self.passed_title)

        self.passed_scroll = self._create_scroll_area()
        self.passed_container = QWidget()
        self.passed_layout = QVBoxLayout(self.passed_container)
        self.passed_layout.setAlignment(Qt.AlignTop)
        self.passed_layout.setSpacing(8)
        self.passed_scroll.setWidget(self.passed_container)
        passed_main_layout.addWidget(self.passed_scroll)

        self.main_layout.addWidget(passed_widget)

        # Failed column (will be created when needed)
        self.failed_scroll = None
        self.failed_container = None
        self.failed_layout = None
        self.failed_title = None
        self.failed_widget = None

    def _create_scroll_area(self) -> QScrollArea:
        """Create configured scroll area"""
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setStyleSheet(CARDS_SECTION_SCROLL_STYLE)
        return scroll

    def clear(self):
        """Clear all cards"""
        self.passed_cards = []
        self.failed_cards = []
        self._clear_layout(self.passed_layout)

        # Remove failed column if it exists
        if self.layout_mode == "split":
            self._remove_failed_column()

        # Reset counter
        self._update_title_counters()

    def add_card(self, card: QWidget, passed: bool):
        """Add test card"""
        if passed:
            self.passed_cards.append(card)
            self.passed_layout.addWidget(card)
            # Update passed counter
            self._update_title_counters()
        else:
            self.failed_cards.append(card)
            if self.layout_mode == "single" and len(self.failed_cards) == 1:
                # First failure - add failed column
                self._add_failed_column()
            if self.layout_mode == "split":
                self.failed_layout.addWidget(card)
                # Update failed counter
                self._update_title_counters()

    def _update_title_counters(self):
        """Update the test counters in titles"""
        passed_count = len(self.passed_cards)
        self.passed_title.setText(f"✓ Passed Tests ({passed_count})")

        if self.layout_mode == "split" and self.failed_title:
            failed_count = len(self.failed_cards)
            self.failed_title.setText(f"✗ Failed Tests ({failed_count})")

    def _add_failed_column(self):
        """Add failed column when first test fails"""
        if self.layout_mode == "split":
            return

        self.layout_mode = "split"

        # Create failed column
        self.failed_widget = QWidget()
        failed_main_layout = QVBoxLayout(self.failed_widget)
        failed_main_layout.setContentsMargins(0, 0, 0, 0)
        failed_main_layout.setSpacing(8)

        # Failed title with counter
        failed_count = len(self.failed_cards)
        self.failed_title = QLabel(f"✗ Failed Tests ({failed_count})")
        self.failed_title.setStyleSheet(CARDS_SECTION_TITLE_FAILED_STYLE)
        failed_main_layout.addWidget(self.failed_title)

        self.failed_scroll = self._create_scroll_area()
        self.failed_container = QWidget()
        self.failed_layout = QVBoxLayout(self.failed_container)
        self.failed_layout.setAlignment(Qt.AlignTop)
        self.failed_layout.setSpacing(8)
        self.failed_scroll.setWidget(self.failed_container)
        failed_main_layout.addWidget(self.failed_scroll)

        # Add failed column to main layout
        self.main_layout.addWidget(self.failed_widget)

    def _remove_failed_column(self):
        """Remove failed column when clearing tests"""
        if self.layout_mode == "single":
            return

        self.layout_mode = "single"

        # Remove failed column
        if self.failed_widget:
            self.failed_widget.deleteLater()
            self.failed_widget = None
            self.failed_scroll = None
            self.failed_container = None
            self.failed_layout = None
            self.failed_title = None

    def _clear_layout(self, layout: QVBoxLayout):
        """Clear all widgets from layout"""
        if layout is None:
            return
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
