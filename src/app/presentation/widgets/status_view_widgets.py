"""
Sub-widgets for unified status view.
"""

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from src.app.presentation.styles.constants.colors import MATERIAL_COLORS
from src.app.presentation.styles.constants.spacing import SPACING, FONTS, BORDER_RADIUS, BORDER_WIDTH, SIZES
from src.app.presentation.styles.components.status_view import (
    CARDS_SECTION_SCROLL_STYLE,
    CARDS_SECTION_TITLE_FAILED_STYLE,
    CARDS_SECTION_TITLE_PASSED_STYLE,
    PROGRESS_SECTION_CONTAINER_STYLE,
    SEGMENT_DEFAULT_STYLE,
    STATS_LABEL_FAILED_STYLE,
    STATS_LABEL_PASSED_STYLE,
    STATS_PANEL_STYLE,
    STATS_PERCENTAGE_STYLE,
    STATS_ROW_PERCENTAGE_STYLE,
    STATS_ROW_TIME_STYLE,
    STATS_ROW_PROGRESS_STYLE,
    STATS_ROW_PASSED_STYLE,
    STATS_ROW_FAILED_STYLE,
    STATS_ROW_WORKERS_ACTIVE_STYLE,
    WORKER_BADGE_IDLE_STYLE,
    WORKER_BADGE_ACTIVE_STYLE,
    STATS_INLINE_DIVIDER_STYLE,
    STATS_INLINE_PERCENTAGE_STYLE,
    STATS_INLINE_PROGRESS_STYLE,
    STATS_INLINE_COUNTS_STYLE,
    STATS_INLINE_WORKER_STYLE,
    EMPTY_STATE_LABEL_STYLE,
    VISUAL_PROGRESS_BAR_STYLE,
    get_segment_style,
)
from src.app.presentation.styles.helpers.common_styles import text_secondary


class ProgressSection(QWidget):
    """Progress bar with visual indicators and statistics - 3-row layout with detailed worker tracking"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.worker_labels = []  # Track individual worker status labels
        self.max_workers = 0
        self.start_time = None
        self._setup_ui()

    def _setup_ui(self):
        # Main vertical layout - 3 rows
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(SPACING['MD'])  # 12px between rows

        # ROW 1: Full-width progress bar
        self.visual_progress = VisualProgressBar()
        layout.addWidget(self.visual_progress)

        # ROW 2: Stats row - horizontal distribution
        stats_row = QWidget()
        stats_layout = QHBoxLayout(stats_row)
        stats_layout.setContentsMargins(SPACING['PADDING_MD'], SPACING['SM'], SPACING['PADDING_MD'], SPACING['SM'])
        stats_layout.setSpacing(SPACING['LG'])  # 16px between stats

        # Percentage
        self.percentage_label = QLabel("0%")
        self.percentage_label.setStyleSheet(STATS_ROW_PERCENTAGE_STYLE)
        
        # Time elapsed
        self.time_label = QLabel("0:00")
        self.time_label.setStyleSheet(STATS_ROW_TIME_STYLE)
        
        # X/Y tests completed
        self.progress_label = QLabel("0 / 0 tests")
        self.progress_label.setStyleSheet(STATS_ROW_PROGRESS_STYLE)
        
        # Passed count
        self.passed_label = QLabel("0 passed")
        self.passed_label.setStyleSheet(STATS_ROW_PASSED_STYLE)
        
        # Failed count
        self.failed_label = QLabel("0 failed")
        self.failed_label.setStyleSheet(STATS_ROW_FAILED_STYLE)
        
        # Workers active
        self.workers_active_label = QLabel("0 workers active")
        self.workers_active_label.setStyleSheet(STATS_ROW_WORKERS_ACTIVE_STYLE)
        
        stats_layout.addWidget(self.percentage_label)
        stats_layout.addWidget(self.time_label)
        stats_layout.addWidget(self.progress_label)
        stats_layout.addWidget(self.passed_label)
        stats_layout.addWidget(self.failed_label)
        stats_layout.addWidget(self.workers_active_label)
        stats_layout.addStretch()
        
        layout.addWidget(stats_row)

        # ROW 3: Individual worker status - horizontal distribution
        self.workers_row = QWidget()
        self.workers_layout = QHBoxLayout(self.workers_row)
        self.workers_layout.setContentsMargins(SPACING['PADDING_MD'], SPACING['SM'], SPACING['PADDING_MD'], SPACING['SM'])
        self.workers_layout.setSpacing(SPACING['SM'])  # 8px between workers
        
        # Initially hidden until tests start
        self.workers_row.setVisible(False)
        
        layout.addWidget(self.workers_row)

        # Apply container styling
        self.setStyleSheet(PROGRESS_SECTION_CONTAINER_STYLE)

    def reset(self, total_tests: int, max_workers: int = 0):
        """Reset for new test run"""
        import time
        self.start_time = time.time()
        self.max_workers = max_workers
        
        self.visual_progress.reset(total_tests)
        self.percentage_label.setText("0%")
        self.time_label.setText("0:00")
        self.progress_label.setText(f"0 / {total_tests} tests")
        self.passed_label.setText("0 passed")
        self.failed_label.setText("0 failed")
        self.workers_active_label.setText(f"{max_workers} workers active")
        
        # Create worker status labels
        self._setup_worker_labels(max_workers)

    def _setup_worker_labels(self, count: int):
        """Create individual worker status labels"""
        # Clear existing labels
        for label in self.worker_labels:
            label.deleteLater()
        self.worker_labels.clear()
        
        if count == 0:
            self.workers_row.setVisible(False)
            return
        
        # Create labels for each worker
        for i in range(count):
            worker_label = QLabel(f"Worker {i+1}: Idle")
            worker_label.setStyleSheet(WORKER_BADGE_IDLE_STYLE)
            self.workers_layout.addWidget(worker_label)
            self.worker_labels.append(worker_label)
        
        self.workers_layout.addStretch()
        self.workers_row.setVisible(True)

    def add_test_result(self, passed: bool):
        """Add test result to visual progress"""
        self.visual_progress.add_result(passed)

    def update_stats(self, completed: int, total: int, passed: int, failed: int):
        """Update statistics display"""
        import time
        
        # Calculate percentage
        percentage = (completed / total * 100) if total > 0 else 0
        self.percentage_label.setText(f"{percentage:.0f}%")
        
        # Calculate elapsed time
        if self.start_time:
            elapsed = time.time() - self.start_time
            minutes = int(elapsed // 60)
            seconds = int(elapsed % 60)
            self.time_label.setText(f"{minutes}:{seconds:02d}")
        
        # Update counts
        self.progress_label.setText(f"{completed} / {total} tests")
        self.passed_label.setText(f"{passed} passed")
        self.failed_label.setText(f"{failed} failed")

    def update_worker_status(self, worker_id: int, test_number: int = None, idle: bool = False):
        """
        Update individual worker status.
        
        Args:
            worker_id: Worker ID (0-indexed)
            test_number: Current test number being processed (None if idle)
            idle: Whether worker is idle
        """
        if worker_id < 0 or worker_id >= len(self.worker_labels):
            return
        
        label = self.worker_labels[worker_id]
        
        if idle or test_number is None:
            label.setText(f"Worker {worker_id + 1}: Idle")
            label.setStyleSheet(WORKER_BADGE_IDLE_STYLE)
        else:
            label.setText(f"Worker {worker_id + 1}: Test #{test_number}")
            label.setStyleSheet(WORKER_BADGE_ACTIVE_STYLE)

    def update_worker_info(self, workers_active: int, current_test: int = None):
        """Update worker information (legacy method for compatibility)"""
        self.workers_active_label.setText(f"{workers_active} workers active")

    def update_current_test(self, current: int, total: int):
        """Update current test indicator"""
        self.visual_progress.set_current(current, total)

    def mark_complete(self, all_passed: bool):
        """Mark tests as complete"""
        self.visual_progress.mark_complete(all_passed)
        self.workers_active_label.setText("0 workers active")
        
        # Mark all workers as idle
        for i in range(len(self.worker_labels)):
            self.update_worker_status(i, idle=True)


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
        self.layout.setContentsMargins(SPACING['MD'], SPACING['MD'], SPACING['MD'], SPACING['MD'])  # 12px padding
        self.layout.setSpacing(SPACING['NONE'])  # No spacing for connected segments

        self.setStyleSheet(VISUAL_PROGRESS_BAR_STYLE)

    def reset(self, total: int):
        """Reset progress bar with simplified segment calculation"""
        self.results = []
        self.total = total
        self.current = 0
        self._clear_layout()
        self.segments = []

        # Simplified segment calculation: max 50 segments
        if total <= 50:
            # Show individual segments for small test counts
            segment_count = total
            self.segment_size = 1
        else:
            # Cap at 50 segments, each representing multiple tests
            segment_count = 50
            self.segment_size = (total + 49) // 50  # Ceiling division

        # Create segments with consistent width
        segment_width = max(SPACING['MD'], 900 // segment_count)  # Minimum 12px per segment
        
        # Create segments
        for i in range(segment_count):
            segment = QFrame()
            segment.setFixedSize(segment_width, SIZES['PROGRESS_MD'])  # 32px progress bar height

            # Apply default style with no border radius on inner sides for connected look
            if i == 0:
                # First segment - round left side only
                segment.setStyleSheet(
                    SEGMENT_DEFAULT_STYLE.replace(
                        "border-radius: 4px;", "border-radius: 4px 0 0 4px;"
                    )
                )
            elif i == segment_count - 1:
                # Last segment - round right side only
                segment.setStyleSheet(
                    SEGMENT_DEFAULT_STYLE.replace(
                        "border-radius: 4px;", "border-radius: 0 4px 4px 0;"
                    )
                )
            else:
                # Middle segments - no rounding
                segment.setStyleSheet(
                    SEGMENT_DEFAULT_STYLE.replace(
                        "border-radius: 4px;", "border-radius: 0;"
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
            info_label.setStyleSheet(f"{text_secondary()} font-size: 9px;")
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
                "border-radius: 4px;", "border-radius: 4px 0 0 4px;"
            )
        elif position == "last":
            style = base_style.replace(
                "border-radius: 4px;", "border-radius: 0 4px 4px 0;"
            )
        else:
            style = base_style.replace("border-radius: 4px;", "border-radius: 0;")

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
        """Track current test (visual indicator disabled for now - causes stylesheet parsing issues)"""
        self.current = current

    def mark_complete(self, all_passed: bool):
        """Mark as complete"""
        # Visual indication that all tests are done

    def _clear_layout(self):
        """Clear all widgets from layout"""
        while self.layout.count():
            item = self.layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()


class StatsPanel(QWidget):
    """Statistics display panel with completion percentage and worker info (horizontal inline layout)"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()

    def _create_divider(self):
        """Create a vertical divider for inline layout"""
        divider = QLabel("│")  # Using box drawing character for better visibility
        divider.setStyleSheet(STATS_INLINE_DIVIDER_STYLE)
        return divider

    def _setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(SPACING['XL'], SPACING['MD'] + 2, SPACING['XL'], SPACING['MD'] + 2)  # 20px, 14px
        layout.setSpacing(SPACING['MD'])  # 12px between elements

        # Completion percentage (large and prominent)
        self.percentage_label = QLabel("0%")
        self.percentage_label.setAlignment(Qt.AlignCenter)
        self.percentage_label.setMinimumWidth(SIZES['MIN_WIDTH_MD'])  # 90px
        self.percentage_label.setStyleSheet(STATS_INLINE_PERCENTAGE_STYLE)

        # Progress text (e.g., "0 / 50 tests")
        self.progress_label = QLabel("0 / 0 tests")
        self.progress_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.progress_label.setStyleSheet(STATS_INLINE_PROGRESS_STYLE)

        # Pass/Fail counts (compact, single line)
        self.counts_label = QLabel("0 passed | 0 failed")
        self.counts_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.counts_label.setStyleSheet(STATS_INLINE_COUNTS_STYLE)

        # Worker info (will be updated during test execution)
        self.worker_label = QLabel("")
        self.worker_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.worker_label.setStyleSheet(STATS_INLINE_WORKER_STYLE)
        self.worker_label.setVisible(False)  # Hidden until tests start

        # Build horizontal layout: percentage | progress | counts | worker
        layout.addWidget(self.percentage_label)
        layout.addWidget(self._create_divider())
        layout.addWidget(self.progress_label)
        layout.addWidget(self._create_divider())
        layout.addWidget(self.counts_label)
        layout.addWidget(self.worker_label)
        layout.addStretch()

        self.setStyleSheet(STATS_PANEL_STYLE)

    def reset(self):
        """Reset statistics"""
        self.percentage_label.setText("0%")
        self.progress_label.setText("0 / 0 tests")
        self.counts_label.setText("0 passed | 0 failed")
        self.worker_label.setVisible(False)

    def update(self, completed: int, total: int, passed: int, failed: int):
        """Update statistics"""
        percentage = (completed / total * 100) if total > 0 else 0
        self.percentage_label.setText(f"{percentage:.0f}%")
        self.progress_label.setText(f"{completed} / {total} tests")
        
        # Compact single-line format with color coding
        counts_html = f'<span style="color: {MATERIAL_COLORS["primary"]};">{passed} passed</span> | <span style="color: {MATERIAL_COLORS["error"]};">{failed} failed</span>'
        self.counts_label.setText(counts_html)

    def update_worker_info(self, workers_active: int, current_test: int = None):
        """
        Update worker information display.
        
        Args:
            workers_active: Number of currently active workers
            current_test: Current test number being processed (optional)
        """
        if workers_active > 0:
            if current_test:
                self.worker_label.setText(f"⚡ {workers_active} workers | Test #{current_test}")
            else:
                self.worker_label.setText(f"⚡ {workers_active} workers active")
            self.worker_label.setVisible(True)
        else:
            self.worker_label.setVisible(False)


class CardsSection(QWidget):
    """Container for test cards - always shows both passed and failed columns"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.passed_cards = []
        self.failed_cards = []
        self._setup_ui()

    def _setup_ui(self):
        self.main_layout = QHBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(SPACING['LG'])  # 16px between columns

        # Passed column (always visible)
        passed_widget = QWidget()
        passed_main_layout = QVBoxLayout(passed_widget)
        passed_main_layout.setContentsMargins(0, 0, 0, 0)
        passed_main_layout.setSpacing(SPACING['SM'])  # 8px spacing

        # Passed title with counter
        self.passed_title = QLabel("✓ Passed Tests (0)")
        self.passed_title.setStyleSheet(CARDS_SECTION_TITLE_PASSED_STYLE)
        passed_main_layout.addWidget(self.passed_title)

        self.passed_scroll = self._create_scroll_area()
        self.passed_container = QWidget()
        self.passed_layout = QVBoxLayout(self.passed_container)
        self.passed_layout.setAlignment(Qt.AlignTop)
        self.passed_layout.setSpacing(SPACING['SM'])  # 8px between cards
        
        # Empty state label for passed tests
        self.passed_empty_label = QLabel("No passed tests yet")
        self.passed_empty_label.setAlignment(Qt.AlignCenter)
        self.passed_empty_label.setStyleSheet(EMPTY_STATE_LABEL_STYLE)
        self.passed_layout.addWidget(self.passed_empty_label)
        
        self.passed_scroll.setWidget(self.passed_container)
        passed_main_layout.addWidget(self.passed_scroll)
        self.main_layout.addWidget(passed_widget)

        # Failed column (always visible)
        failed_widget = QWidget()
        failed_main_layout = QVBoxLayout(failed_widget)
        failed_main_layout.setContentsMargins(0, 0, 0, 0)
        failed_main_layout.setSpacing(SPACING['SM'])  # 8px spacing

        # Failed title with counter
        self.failed_title = QLabel("✗ Failed Tests (0)")
        self.failed_title.setStyleSheet(CARDS_SECTION_TITLE_FAILED_STYLE)
        failed_main_layout.addWidget(self.failed_title)

        self.failed_scroll = self._create_scroll_area()
        self.failed_container = QWidget()
        self.failed_layout = QVBoxLayout(self.failed_container)
        self.failed_layout.setAlignment(Qt.AlignTop)
        self.failed_layout.setSpacing(SPACING['SM'])  # 8px between cards
        
        # Empty state label for failed tests
        self.failed_empty_label = QLabel("No failed tests yet! 🎉")
        self.failed_empty_label.setAlignment(Qt.AlignCenter)
        self.failed_empty_label.setStyleSheet(EMPTY_STATE_LABEL_STYLE)
        self.failed_layout.addWidget(self.failed_empty_label)
        
        self.failed_scroll.setWidget(self.failed_container)
        failed_main_layout.addWidget(self.failed_scroll)
        self.main_layout.addWidget(failed_widget)

    def _create_scroll_area(self) -> QScrollArea:
        """Create configured scroll area"""
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setStyleSheet(CARDS_SECTION_SCROLL_STYLE)
        return scroll

    def clear(self):
        """Clear all cards and show empty states"""
        self.passed_cards = []
        self.failed_cards = []
        self._clear_layout(self.passed_layout)
        self._clear_layout(self.failed_layout)
        
        # Show empty state labels
        self.passed_empty_label.setVisible(True)
        self.failed_empty_label.setVisible(True)
        
        # Reset counters
        self._update_title_counters()

    def add_card(self, card: QWidget, passed: bool):
        """Add test card to appropriate column"""
        if passed:
            # Hide empty state if this is first card
            if len(self.passed_cards) == 0:
                self.passed_empty_label.setVisible(False)
            
            self.passed_cards.append(card)
            self.passed_layout.addWidget(card)
        else:
            # Hide empty state if this is first card
            if len(self.failed_cards) == 0:
                self.failed_empty_label.setVisible(False)
            
            self.failed_cards.append(card)
            self.failed_layout.addWidget(card)
        
        # Update counters
        self._update_title_counters()

    def _update_title_counters(self):
        """Update the test counters in titles"""
        passed_count = len(self.passed_cards)
        failed_count = len(self.failed_cards)
        self.passed_title.setText(f"✓ Passed Tests ({passed_count})")
        self.failed_title.setText(f"✗ Failed Tests ({failed_count})")

    def _clear_layout(self, layout: QVBoxLayout):
        """Clear all widgets from layout except empty state labels"""
        if layout is None:
            return
        
        # Store empty labels before clearing
        empty_labels = []
        for i in range(layout.count()):
            item = layout.itemAt(i)
            if item and item.widget():
                widget = item.widget()
                # Check if it's an empty state label
                if isinstance(widget, QLabel) and ("No " in widget.text() or "🎉" in widget.text()):
                    empty_labels.append(widget)
        
        # Clear all widgets
        while layout.count():
            item = layout.takeAt(0)
            if item.widget() and item.widget() not in empty_labels:
                item.widget().deleteLater()
        
        # Re-add empty labels
        for label in empty_labels:
            layout.addWidget(label)
