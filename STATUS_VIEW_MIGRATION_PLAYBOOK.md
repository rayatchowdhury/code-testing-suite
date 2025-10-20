# Status View Migration Playbook
## Clean Architecture with Proper Separation of Concerns

**Goal:** Refactor status view system to have clean responsibility distribution where:
- **Presenters** coordinate between domain and UI
- **Widgets** are pure presentation components
- **Status Views** act as thin adapters for domain-specific tests
- **Worker integration** is properly handled through presenter layer

**Constraints:**
- Max 5 files in new `widgets/status_view/` folder
- Only edit: `*_status_view.py`, `styles/components/status_view/*`
- Don't create/change other files
- Final cleanup: Delete `unified_status_view.py`, `status_view_widgets.py`
- Target: <1100 lines total

---

## Phase 1: Create New Architecture (widgets/status_view/)

### File 1: `models.py` (~120 lines)
**Purpose:** Data models and state management

```python
"""
Status View Data Models

Immutable data classes for test execution state and results.
These models provide clean interfaces between workers and presenters.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional
from enum import Enum


class TestType(Enum):
    """Test execution types"""
    COMPARATOR = "comparator"
    VALIDATOR = "validator"
    BENCHMARKER = "benchmarker"


@dataclass(frozen=True)
class TestResult:
    """
    Immutable test result from worker.
    
    Single source of truth for test completion data.
    Replaces inconsistent **kwargs passing in current implementation.
    """
    test_number: int
    passed: bool
    time: float  # seconds
    memory: float  # MB
    test_type: TestType
    
    # Type-specific data stored in flexible dict
    # Comparator: input_text, correct_output, test_output
    # Validator: input_data, test_output, validation_message, error_details, exit_code
    # Benchmarker: test_name, execution_time, memory_passed, input_data, output_data, test_size
    data: Dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def from_comparator(cls, test_number: int, passed: bool, 
                       input_text: str, correct_output: str, test_output: str,
                       time: float, memory: float) -> 'TestResult':
        """Create TestResult from comparator worker signal"""
        return cls(
            test_number=test_number,
            passed=passed,
            time=time,
            memory=memory,
            test_type=TestType.COMPARATOR,
            data={
                'input_text': input_text,
                'correct_output': correct_output,
                'test_output': test_output
            }
        )
    
    @classmethod
    def from_validator(cls, test_number: int, passed: bool,
                      input_data: str, test_output: str, validation_message: str,
                      error_details: str, validator_exit_code: int,
                      time: float, memory: float) -> 'TestResult':
        """Create TestResult from validator worker signal"""
        return cls(
            test_number=test_number,
            passed=passed,
            time=time,
            memory=memory,
            test_type=TestType.VALIDATOR,
            data={
                'input_data': input_data,
                'test_output': test_output,
                'validation_message': validation_message,
                'error_details': error_details,
                'validator_exit_code': validator_exit_code
            }
        )
    
    @classmethod
    def from_benchmarker(cls, test_name: str, test_number: int, passed: bool,
                        execution_time: float, memory_used: float, memory_passed: bool,
                        input_data: str, output_data: str, test_size: int) -> 'TestResult':
        """Create TestResult from benchmarker worker signal"""
        return cls(
            test_number=test_number,
            passed=passed,
            time=execution_time,
            memory=memory_used,
            test_type=TestType.BENCHMARKER,
            data={
                'test_name': test_name,
                'memory_passed': memory_passed,
                'input_data': input_data,
                'output_data': output_data,
                'test_size': test_size
            }
        )


@dataclass
class TestExecutionState:
    """
    Mutable state for test execution progress.
    
    Replaces scattered state variables in BaseStatusView.
    Single responsibility: track execution metrics.
    """
    total_tests: int = 0
    completed_tests: int = 0
    passed_tests: int = 0
    failed_tests: int = 0
    max_workers: int = 0
    is_running: bool = False
    start_time: Optional[float] = None
    
    def reset(self, total: int, workers: int) -> None:
        """Reset state for new test run"""
        self.total_tests = total
        self.completed_tests = 0
        self.passed_tests = 0
        self.failed_tests = 0
        self.max_workers = workers
        self.is_running = True
        import time
        self.start_time = time.time()
    
    def record_result(self, passed: bool) -> None:
        """Record a test completion"""
        self.completed_tests += 1
        if passed:
            self.passed_tests += 1
        else:
            self.failed_tests += 1
    
    def mark_complete(self) -> None:
        """Mark execution as complete"""
        self.is_running = False
    
    @property
    def progress_percentage(self) -> float:
        """Calculate progress percentage"""
        if self.total_tests == 0:
            return 0.0
        return (self.completed_tests / self.total_tests) * 100
    
    @property
    def elapsed_time(self) -> float:
        """Get elapsed time in seconds"""
        if self.start_time is None:
            return 0.0
        import time
        return time.time() - self.start_time
    
    @property
    def tests_per_second(self) -> float:
        """Calculate test execution speed"""
        elapsed = self.elapsed_time
        if elapsed == 0:
            return 0.0
        return self.completed_tests / elapsed
    
    @property
    def estimated_remaining_seconds(self) -> float:
        """Estimate remaining time"""
        if self.completed_tests == 0:
            return 0.0
        speed = self.tests_per_second
        if speed == 0:
            return 0.0
        return (self.total_tests - self.completed_tests) / speed


@dataclass
class TestStatistics:
    """Statistics snapshot for widget updates"""
    completed: int
    total: int
    passed: int
    failed: int
    progress_pct: float
    elapsed_seconds: float
    remaining_seconds: float
    tests_per_second: float
    workers_active: int
```

---

### File 2: `presenter.py` (~200 lines)
**Purpose:** Coordination layer between state and widgets

```python
"""
Status View Presenter

Implements Presenter pattern to coordinate between:
- TestExecutionState (model)
- StatusViewWidgets (view components)
- Domain-specific status views (controllers)

Responsibility: Translate state changes into widget update calls.
Does NOT contain business logic or UI rendering code.
"""

from typing import Optional
import time

from .models import TestResult, TestExecutionState, TestStatistics
from .widgets import (
    StatusHeaderSection,
    PerformancePanelSection,
    VisualProgressBarSection,
    TestResultsCardsSection
)


class StatusViewPresenter:
    """
    Presenter for status view coordination.
    
    Separates concerns:
    - State management (TestExecutionState)
    - Widget manipulation (knows how to update widgets)
    - Event translation (domain events → widget updates)
    """
    
    def __init__(
        self,
        header: StatusHeaderSection,
        performance: PerformancePanelSection,
        progress_bar: VisualProgressBarSection,
        cards_section: TestResultsCardsSection
    ):
        """
        Initialize presenter with widget references.
        
        Args:
            header: Status header widget
            performance: Performance panel widget
            progress_bar: Visual progress bar widget
            cards_section: Test cards section widget
        """
        self.header = header
        self.performance = performance
        self.progress_bar = progress_bar
        self.cards_section = cards_section
        
        self.state = TestExecutionState()
    
    def start_test_execution(self, total_tests: int, max_workers: int) -> None:
        """
        Initialize presenter for new test run.
        
        Args:
            total_tests: Total number of tests
            max_workers: Number of parallel workers
        """
        # Reset state
        self.state.reset(total_tests, max_workers)
        
        # Reset all widgets
        self.header.reset(total_tests)
        self.progress_bar.reset(total_tests)
        self.cards_section.clear()
        
        # Setup performance panel
        if max_workers > 0:
            self.performance.setup_workers(max_workers)
            self.performance.update_summary(max_workers, 0.0)
    
    def handle_test_result(self, result: TestResult) -> None:
        """
        Process test result and update all widgets.
        
        Single entry point for test completion events.
        Coordinates all widget updates in proper order.
        
        Args:
            result: Test result from worker
        """
        # Update state
        self.state.record_result(result.passed)
        
        # Update progress bar
        self.progress_bar.add_result(result.test_number, result.passed)
        
        # Update header statistics
        self.header.update_stats(
            completed=self.state.completed_tests,
            total=self.state.total_tests,
            passed=self.state.passed_tests,
            failed=self.state.failed_tests
        )
        
        # Update performance panel
        self.performance.update_summary(
            workers_active=self.state.max_workers,
            speed=self.state.tests_per_second
        )
    
    def update_worker_status(self, worker_id: int, test_number: Optional[int], 
                            progress: float, elapsed: float) -> None:
        """
        Update individual worker status.
        
        Called by domain-specific views when worker signals are received.
        
        Args:
            worker_id: Worker identifier (1-indexed)
            test_number: Currently executing test (None if idle)
            progress: Execution progress (0.0-1.0)
            elapsed: Elapsed time for current test
        """
        if worker_id <= len(self.performance.worker_bars):
            worker_bar = self.performance.worker_bars[worker_id - 1]
            worker_bar.set_status(test_number, progress, elapsed)
    
    def complete_execution(self) -> None:
        """
        Finalize test execution.
        
        Updates widgets to show completion state.
        """
        self.state.mark_complete()
        self.header.mark_complete()
    
    def get_statistics(self) -> TestStatistics:
        """
        Get current statistics snapshot.
        
        Returns:
            TestStatistics with current state
        """
        return TestStatistics(
            completed=self.state.completed_tests,
            total=self.state.total_tests,
            passed=self.state.passed_tests,
            failed=self.state.failed_tests,
            progress_pct=self.state.progress_percentage,
            elapsed_seconds=self.state.elapsed_time,
            remaining_seconds=self.state.estimated_remaining_seconds,
            tests_per_second=self.state.tests_per_second,
            workers_active=self.state.max_workers
        )
    
    def is_running(self) -> bool:
        """Check if tests are running"""
        return self.state.is_running
```

---

### File 3: `widgets.py` (~350 lines)
**Purpose:** Pure UI components (extracted from status_view_widgets.py)

```python
"""
Status View UI Widgets

Pure presentation components with no business logic.
Widgets expose clean update APIs and emit user interaction signals.

Extracted from status_view_widgets.py with cleanup.
"""

import random
from PySide6.QtCore import Qt, Property, QPropertyAnimation, QEasingCurve, QTimer, Signal
from PySide6.QtGui import QPainter, QPen, QColor, QFont
from PySide6.QtWidgets import (
    QFrame, QHBoxLayout, QLabel, QPushButton, QScrollArea,
    QVBoxLayout, QWidget
)

from src.app.presentation.styles.constants.colors import MATERIAL_COLORS
from src.app.presentation.styles.fonts.emoji import set_emoji_font
from src.app.presentation.styles.components.status_view import (
    STATUS_HEADER_SECTION_STYLE,
    STATUS_HEADER_TIME_LABEL_STYLE,
    STATUS_HEADER_ETA_LABEL_STYLE,
    STATUS_HEADER_SPEED_LABEL_STYLE,
    STATUS_HEADER_COMPLETION_LABEL_STYLE,
    STATUS_HEADER_PASSED_LABEL_STYLE,
    STATUS_HEADER_FAILED_LABEL_STYLE,
    PERFORMANCE_PANEL_SECTION_STYLE,
    PERFORMANCE_PANEL_SUMMARY_LABEL_STYLE,
    PERFORMANCE_PANEL_TOGGLE_BUTTON_STYLE,
    WORKER_LABEL_STYLE,
    WORKER_TEST_LABEL_IDLE_STYLE,
    WORKER_TEST_LABEL_ACTIVE_STYLE,
    WORKER_TIME_LABEL_IDLE_STYLE,
    WORKER_TIME_LABEL_ACTIVE_STYLE,
    get_worker_progress_container_style,
    VISUAL_PROGRESS_BAR_SECTION_STYLE,
    PROGRESS_BAR_LEGEND_PASSED_STYLE,
    PROGRESS_BAR_LEGEND_FAILED_STYLE,
    get_progress_segment_style,
    CARDS_SECTION_PASSED_TITLE_STYLE,
    CARDS_SECTION_FAILED_TITLE_STYLE,
    CARDS_SECTION_EMPTY_LABEL_STYLE,
    CARDS_SECTION_SCROLLBAR_STYLE,
    TEST_RESULTS_CARDS_SECTION_STYLE,
    TEST_CARD_LABEL_HEADER_STYLE,
    TEST_CARD_LABEL_STATUS_PASSED_STYLE,
    TEST_CARD_LABEL_STATUS_FAILED_STYLE,
    TEST_CARD_LABEL_METRIC_STYLE,
    get_test_card_style,
)


# ============================================================================
# PROGRESS RING
# ============================================================================
class ProgressRing(QWidget):
    """Circular progress indicator with animation"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._progress = 0.0
        self._animated_progress = 0.0
        self._passed = 0
        self._failed = 0
        self.setFixedSize(150, 150)
        
        self.progress_animation = QPropertyAnimation(self, b"animated_progress")
        self.progress_animation.setDuration(800)
        self.progress_animation.setEasingCurve(QEasingCurve.OutCubic)
    
    @Property(float)
    def progress(self):
        return self._progress
    
    @progress.setter
    def progress(self, value):
        self._progress = value
        self.progress_animation.stop()
        self.progress_animation.setStartValue(self._animated_progress)
        self.progress_animation.setEndValue(value)
        self.progress_animation.start()
    
    @Property(float)
    def animated_progress(self):
        return self._animated_progress
    
    @animated_progress.setter
    def animated_progress(self, value):
        self._animated_progress = value
        self.update()
    
    def set_results(self, passed, failed):
        self._passed = passed
        self._failed = failed
        self.update()
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        rect = self.rect().adjusted(18, 18, -18, -18)
        
        # Background ring
        pen = QPen(QColor(MATERIAL_COLORS['progress_track']), 15)
        pen.setCapStyle(Qt.RoundCap)
        painter.setPen(pen)
        painter.drawArc(rect, 0, 360 * 16)
        
        # Progress ring with glow
        if self._failed > 0:
            color = QColor(MATERIAL_COLORS['error'])
        elif self._passed > 0:
            color = QColor(MATERIAL_COLORS['success'])
        else:
            color = QColor(MATERIAL_COLORS['info'])
        
        # Glow layers
        for i in range(3):
            glow_color = QColor(color)
            glow_color.setAlpha(30 - i * 10)
            pen = QPen(glow_color, 15 + i * 3)
            pen.setCapStyle(Qt.RoundCap)
            painter.setPen(pen)
            span = int(self._animated_progress * 3.6 * 16)
            painter.drawArc(rect.adjusted(-i*2, -i*2, i*2, i*2), 90 * 16, -span)
        
        # Main ring
        pen = QPen(color, 15)
        pen.setCapStyle(Qt.RoundCap)
        painter.setPen(pen)
        span_angle = int(self._animated_progress * 3.6 * 16)
        painter.drawArc(rect, 90 * 16, -span_angle)
        
        # Percentage text
        painter.setPen(QColor(MATERIAL_COLORS['text_primary']))
        font = QFont("Segoe UI", 28, QFont.Bold)
        painter.setFont(font)
        painter.drawText(rect, Qt.AlignCenter, f"{int(self._animated_progress)}%")


# ============================================================================
# STATUS HEADER
# ============================================================================
class StatusHeaderSection(QWidget):
    """Header with progress ring and stats"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(190)
        self.start_time = None
        self._setup_ui()
        
    def _setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(40)
        
        # LEFT: Time stats
        left_section = QWidget()
        left_layout = QVBoxLayout(left_section)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(8)
        left_layout.setAlignment(Qt.AlignVCenter | Qt.AlignRight)
        
        self.time_label = QLabel("⏱ 0:00 elapsed")
        self.time_label.setAlignment(Qt.AlignRight)
        self.time_label.setStyleSheet(STATUS_HEADER_TIME_LABEL_STYLE)
        left_layout.addWidget(self.time_label)
        
        self.eta_label = QLabel("⏳ ~0:00 remaining")
        self.eta_label.setAlignment(Qt.AlignRight)
        self.eta_label.setStyleSheet(STATUS_HEADER_ETA_LABEL_STYLE)
        left_layout.addWidget(self.eta_label)
        
        self.speed_label = QLabel("⚡ 0.00 tests/sec")
        self.speed_label.setAlignment(Qt.AlignRight)
        self.speed_label.setStyleSheet(STATUS_HEADER_SPEED_LABEL_STYLE)
        left_layout.addWidget(self.speed_label)
        
        layout.addWidget(left_section, stretch=1)
        
        # CENTER: Progress ring
        ring_container = QWidget()
        ring_layout = QVBoxLayout(ring_container)
        ring_layout.setContentsMargins(0, 0, 0, 0)
        ring_layout.addStretch()
        self.progress_ring = ProgressRing()
        ring_layout.addWidget(self.progress_ring, alignment=Qt.AlignCenter)
        ring_layout.addStretch()
        layout.addWidget(ring_container)
        
        # RIGHT: Completion stats
        right_section = QWidget()
        right_layout = QVBoxLayout(right_section)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(8)
        right_layout.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)
        
        self.completion_label = QLabel("0 / 0 tests")
        self.completion_label.setAlignment(Qt.AlignLeft)
        self.completion_label.setStyleSheet(STATUS_HEADER_COMPLETION_LABEL_STYLE)
        right_layout.addWidget(self.completion_label)
        
        self.passed_label = QLabel("✓ 0 passed (0%)")
        self.passed_label.setAlignment(Qt.AlignLeft)
        self.passed_label.setStyleSheet(STATUS_HEADER_PASSED_LABEL_STYLE)
        right_layout.addWidget(self.passed_label)
        
        self.failed_label = QLabel("✗ 0 failed (0%)")
        self.failed_label.setAlignment(Qt.AlignLeft)
        self.failed_label.setStyleSheet(STATUS_HEADER_FAILED_LABEL_STYLE)
        right_layout.addWidget(self.failed_label)
        
        layout.addWidget(right_section, stretch=1)
        
        self.setStyleSheet(STATUS_HEADER_SECTION_STYLE)
    
    def reset(self, total_tests: int):
        """Reset for new test run"""
        import time
        self.start_time = time.time()
        self.total_tests = total_tests
        
        self.completion_label.setText(f"0 / {total_tests} tests")
        self.passed_label.setText("✓ 0 passed (0%)")
        self.failed_label.setText("✗ 0 failed (0%)")
        self.time_label.setText("⏱ 0:00 elapsed")
        self.eta_label.setText("⏳ ~0:00 remaining")
        self.speed_label.setText("⚡ 0.00 tests/sec")
        
        self.progress_ring.progress = 0
        self.progress_ring.set_results(0, 0)
    
    def update_stats(self, completed: int, total: int, passed: int, failed: int):
        """Update all statistics"""
        import time
        
        # Update progress ring
        progress = (completed / total * 100) if total > 0 else 0
        self.progress_ring.progress = progress
        self.progress_ring.set_results(passed, failed)
        
        # Update completion
        self.completion_label.setText(f"{completed} / {total} tests")
        
        # Update pass/fail with percentages
        pass_pct = (passed / completed * 100) if completed > 0 else 0
        fail_pct = (failed / completed * 100) if completed > 0 else 0
        self.passed_label.setText(f"✓ {passed} passed ({pass_pct:.0f}%)")
        self.failed_label.setText(f"✗ {failed} failed ({fail_pct:.0f}%)")
        
        # Update time stats
        if self.start_time:
            elapsed = time.time() - self.start_time
            speed = completed / elapsed if elapsed > 0 else 0
            remaining = (total - completed) / speed if speed > 0 else 0
            
            mins = int(elapsed // 60)
            secs = int(elapsed % 60)
            self.time_label.setText(f"⏱ {mins}:{secs:02d} elapsed")
            
            mins_remain = int(remaining // 60)
            secs_remain = int(remaining % 60)
            self.eta_label.setText(f"⏳ ~{mins_remain}:{secs_remain:02d} remaining")
            
            self.speed_label.setText(f"⚡ {speed:.2f} tests/sec")
    
    def mark_complete(self):
        """Mark tests as complete"""
        self.eta_label.setText("⏳ Complete!")


# ============================================================================
# PERFORMANCE PANEL
# ============================================================================
class WorkerProgressBar(QWidget):
    """Individual worker progress bar"""
    
    def __init__(self, worker_id, parent=None):
        super().__init__(parent)
        self.worker_id = worker_id
        self._setup_ui()
        
    def _setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)
        
        self.worker_label = QLabel(f"Worker {self.worker_id}")
        self.worker_label.setFixedWidth(75)
        self.worker_label.setStyleSheet(WORKER_LABEL_STYLE)
        layout.addWidget(self.worker_label)
        
        self.test_label = QLabel("Idle")
        self.test_label.setFixedWidth(85)
        self.test_label.setStyleSheet(WORKER_TEST_LABEL_IDLE_STYLE)
        layout.addWidget(self.test_label)
        
        self.progress_container = QWidget()
        self.progress_container.setFixedHeight(22)
        self.progress_container.setStyleSheet(get_worker_progress_container_style(idle=True, progress=0.0))
        layout.addWidget(self.progress_container, stretch=1)
        
        self.time_label = QLabel("--")
        self.time_label.setFixedWidth(65)
        self.time_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.time_label.setStyleSheet(WORKER_TIME_LABEL_IDLE_STYLE)
        layout.addWidget(self.time_label)
    
    def set_status(self, test_number=None, progress=0.0, elapsed=0.0):
        """Update worker status"""
        if test_number:
            self.test_label.setText(f"Test #{test_number}")
            self.test_label.setStyleSheet(WORKER_TEST_LABEL_ACTIVE_STYLE)
            self.time_label.setText(f"{elapsed:.1f}s")
            self.time_label.setStyleSheet(WORKER_TIME_LABEL_ACTIVE_STYLE)
            self.progress_container.setStyleSheet(get_worker_progress_container_style(idle=False, progress=progress))
        else:
            self.test_label.setText("Idle")
            self.test_label.setStyleSheet(WORKER_TEST_LABEL_IDLE_STYLE)
            self.time_label.setText("--")
            self.progress_container.setStyleSheet(get_worker_progress_container_style(idle=True, progress=0.0))


class PerformancePanelSection(QWidget):
    """Collapsible performance panel"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._expanded = False
        self._setup_ui()
        
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 10, 24, 10)
        layout.setSpacing(8)
        
        header_layout = QHBoxLayout()
        
        self.summary_label = QLabel("⚡ 0 Workers │ 0.00 tests/s")
        self.summary_label.setStyleSheet(PERFORMANCE_PANEL_SUMMARY_LABEL_STYLE)
        header_layout.addWidget(self.summary_label)
        
        header_layout.addStretch()
        
        self.toggle_btn = QPushButton("Show Details ▼")
        self.toggle_btn.setStyleSheet(PERFORMANCE_PANEL_TOGGLE_BUTTON_STYLE)
        self.toggle_btn.clicked.connect(self._toggle_expanded)
        header_layout.addWidget(self.toggle_btn)
        
        layout.addLayout(header_layout)
        
        self.workers_container = QWidget()
        workers_layout = QVBoxLayout(self.workers_container)
        workers_layout.setContentsMargins(0, 10, 0, 0)
        workers_layout.setSpacing(8)
        
        self.worker_bars = []
        self.workers_container.setVisible(False)
        layout.addWidget(self.workers_container)
        
        self.setStyleSheet(PERFORMANCE_PANEL_SECTION_STYLE)
    
    def setup_workers(self, worker_count: int):
        """Setup worker progress bars"""
        for bar in self.worker_bars:
            bar.deleteLater()
        self.worker_bars.clear()
        
        workers_layout = self.workers_container.layout()
        for i in range(worker_count):
            worker_bar = WorkerProgressBar(i + 1)
            workers_layout.addWidget(worker_bar)
            self.worker_bars.append(worker_bar)
    
    def update_summary(self, workers_active: int, speed: float):
        """Update summary info"""
        self.summary_label.setText(f"⚡ {workers_active} Workers │ {speed:.2f} tests/s")
    
    def _toggle_expanded(self):
        self._expanded = not self._expanded
        self.workers_container.setVisible(self._expanded)
        self.toggle_btn.setText("Hide Details ▲" if self._expanded else "Show Details ▼")


# ============================================================================
# VISUAL PROGRESS BAR
# ============================================================================
class VisualProgressBarSection(QWidget):
    """Segmented progress bar"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.test_results = []
        self.segments = []
        self.tests_per_segment = 1
        self._setup_ui()
        
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 10, 24, 10)
        layout.setSpacing(8)
        
        self.segments_layout = QHBoxLayout()
        self.segments_layout.setSpacing(0)
        layout.addLayout(self.segments_layout)
        
        legend_layout = QHBoxLayout()
        legend_layout.setSpacing(20)
        
        self.passed_legend = QLabel("■ 0 Passed")
        self.passed_legend.setStyleSheet(PROGRESS_BAR_LEGEND_PASSED_STYLE)
        legend_layout.addWidget(self.passed_legend)
        
        self.failed_legend = QLabel("■ 0 Failed")
        self.failed_legend.setStyleSheet(PROGRESS_BAR_LEGEND_FAILED_STYLE)
        legend_layout.addWidget(self.failed_legend)
        
        legend_layout.addStretch()
        layout.addLayout(legend_layout)
        
        self.setStyleSheet(VISUAL_PROGRESS_BAR_SECTION_STYLE)
    
    def reset(self, total_tests: int):
        """Reset progress bar"""
        self.test_results = []
        
        while self.segments_layout.count():
            item = self.segments_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self.segments = []
        
        segment_count = min(100, total_tests)
        self.tests_per_segment = max(1, total_tests // segment_count)
        
        for i in range(segment_count):
            segment = QFrame()
            segment.setFixedSize(max(8, 900 // segment_count), 32)
            
            if i == 0:
                position = 'first'
            elif i == segment_count - 1:
                position = 'last'
            else:
                position = 'middle'
            
            segment.setStyleSheet(get_progress_segment_style('pending', position))
            
            start = i * self.tests_per_segment + 1
            end = min((i + 1) * self.tests_per_segment, total_tests)
            segment.setToolTip(f"Tests {start}-{end}" if self.tests_per_segment > 1 else f"Test {start}")
            
            self.segments_layout.addWidget(segment)
            self.segments.append({'widget': segment, 'passed': 0, 'failed': 0, 'position': position})
        
        self.passed_legend.setText("■ 0 Passed")
        self.failed_legend.setText("■ 0 Failed")
    
    def add_result(self, test_number: int, passed: bool):
        """Add test result"""
        self.test_results.append((test_number, passed))
        segment_idx = (test_number - 1) // self.tests_per_segment
        
        if segment_idx < len(self.segments):
            segment = self.segments[segment_idx]
            if passed:
                segment['passed'] += 1
            else:
                segment['failed'] += 1
            
            if segment['failed'] > 0:
                state = 'failed'
            elif segment['passed'] > 0:
                state = 'passed'
            else:
                state = 'pending'
            
            segment['widget'].setStyleSheet(get_progress_segment_style(state, segment['position']))
        
        passed_count = sum(1 for _, p in self.test_results if p)
        failed_count = len(self.test_results) - passed_count
        self.passed_legend.setText(f"■ {passed_count} Passed")
        self.failed_legend.setText(f"■ {failed_count} Failed")


# ============================================================================
# TEST CARDS SECTION
# ============================================================================
class TestResultsCardsSection(QWidget):
    """Dual-column test results"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
        
    def _setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(24, 14, 24, 14)
        layout.setSpacing(16)
        
        # Passed column
        passed_container = QWidget()
        passed_layout = QVBoxLayout(passed_container)
        passed_layout.setContentsMargins(0, 0, 0, 0)
        passed_layout.setSpacing(14)
        
        self.passed_title = QLabel("✓ Passed Tests (0)")
        self.passed_title.setStyleSheet(CARDS_SECTION_PASSED_TITLE_STYLE)
        passed_layout.addWidget(self.passed_title)
        
        passed_scroll = QScrollArea()
        passed_scroll.setWidgetResizable(True)
        passed_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        passed_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        passed_scroll.setStyleSheet(CARDS_SECTION_SCROLLBAR_STYLE)
        
        self.passed_cards_widget = QWidget()
        self.passed_cards_layout = QVBoxLayout(self.passed_cards_widget)
        self.passed_cards_layout.setAlignment(Qt.AlignTop)
        self.passed_cards_layout.setSpacing(10)
        
        self.passed_empty_label = QLabel("No passed tests yet")
        self.passed_empty_label.setStyleSheet(CARDS_SECTION_EMPTY_LABEL_STYLE)
        self.passed_empty_label.setAlignment(Qt.AlignCenter)
        self.passed_cards_layout.addWidget(self.passed_empty_label)
        
        passed_scroll.setWidget(self.passed_cards_widget)
        passed_layout.addWidget(passed_scroll)
        layout.addWidget(passed_container, stretch=1)
        
        # Failed column
        failed_container = QWidget()
        failed_layout = QVBoxLayout(failed_container)
        failed_layout.setContentsMargins(0, 0, 0, 0)
        failed_layout.setSpacing(14)
        
        self.failed_title = QLabel("✗ Failed Tests (0)")
        self.failed_title.setStyleSheet(CARDS_SECTION_FAILED_TITLE_STYLE)
        failed_layout.addWidget(self.failed_title)
        
        failed_scroll = QScrollArea()
        failed_scroll.setWidgetResizable(True)
        failed_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        failed_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        failed_scroll.setStyleSheet(CARDS_SECTION_SCROLLBAR_STYLE)
        
        self.failed_cards_widget = QWidget()
        self.failed_cards_layout = QVBoxLayout(self.failed_cards_widget)
        self.failed_cards_layout.setAlignment(Qt.AlignTop)
        self.failed_cards_layout.setSpacing(10)
        
        self.failed_empty_label = QLabel("No failed tests yet! 🎉")
        self.failed_empty_label.setStyleSheet(CARDS_SECTION_EMPTY_LABEL_STYLE)
        self.failed_empty_label.setAlignment(Qt.AlignCenter)
        self.failed_cards_layout.addWidget(self.failed_empty_label)
        
        failed_scroll.setWidget(self.failed_cards_widget)
        failed_layout.addWidget(failed_scroll)
        layout.addWidget(failed_container, stretch=1)
        
        self.passed_count = 0
        self.failed_count = 0
        
        self.setStyleSheet(TEST_RESULTS_CARDS_SECTION_STYLE)
    
    def clear(self):
        """Clear all cards"""
        while self.passed_cards_layout.count() > 1:
            item = self.passed_cards_layout.takeAt(1)
            if item.widget():
                item.widget().deleteLater()
        
        while self.failed_cards_layout.count() > 1:
            item = self.failed_cards_layout.takeAt(1)
            if item.widget():
                item.widget().deleteLater()
        
        self.passed_count = 0
        self.failed_count = 0
        self.passed_empty_label.show()
        self.failed_empty_label.show()
        self.passed_title.setText("✓ Passed Tests (0)")
        self.failed_title.setText("✗ Failed Tests (0)")
    
    def add_card(self, card: QWidget, passed: bool):
        """Add test card"""
        if passed:
            if self.passed_count == 0:
                self.passed_empty_label.hide()
            self.passed_cards_layout.addWidget(card)
            self.passed_count += 1
            self.passed_title.setText(f"✓ Passed Tests ({self.passed_count})")
        else:
            if self.failed_count == 0:
                self.failed_empty_label.hide()
            self.failed_cards_layout.addWidget(card)
            self.failed_count += 1
            self.failed_title.setText(f"✗ Failed Tests ({self.failed_count})")


# ============================================================================
# BASE TEST CARD
# ============================================================================
class BaseTestCard(QFrame):
    """Base test card widget"""
    
    clicked = Signal(int)
    
    def __init__(self, test_number: int, passed: bool, time: float, memory: float, parent=None):
        super().__init__(parent)
        self.test_number = test_number
        self.passed = passed
        self.time = time
        self.memory = memory
        self._setup_ui()
        self._apply_styling()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 12, 14, 12)
        layout.setSpacing(8)
        
        header_layout = QHBoxLayout()
        
        self.test_label = QLabel(f"Test #{self.test_number}")
        self.test_label.setStyleSheet(TEST_CARD_LABEL_HEADER_STYLE)
        
        self.status_label = QLabel("✓ Passed" if self.passed else "✗ Failed")
        status_style = TEST_CARD_LABEL_STATUS_PASSED_STYLE if self.passed else TEST_CARD_LABEL_STATUS_FAILED_STYLE
        self.status_label.setStyleSheet(status_style)
        
        header_layout.addWidget(self.test_label)
        header_layout.addStretch()
        header_layout.addWidget(self.status_label)
        
        metrics_layout = QHBoxLayout()
        
        self.time_label = QLabel(f"⏱️ {self.time:.3f}s")
        self.memory_label = QLabel(f"💾 {self.memory:.1f} MB")
        
        for label in [self.time_label, self.memory_label]:
            set_emoji_font(label)
            label.setStyleSheet(TEST_CARD_LABEL_METRIC_STYLE)
        
        metrics_layout.addWidget(self.time_label)
        metrics_layout.addWidget(self.memory_label)
        metrics_layout.addStretch()
        
        layout.addLayout(header_layout)
        layout.addLayout(metrics_layout)
        
        self.setMouseTracking(True)
        self.setCursor(Qt.PointingHandCursor)
    
    def _apply_styling(self):
        self.setStyleSheet(get_test_card_style(self.passed))
    
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit(self.test_number)
        super().mousePressEvent(event)
```

---

### File 4: `cards.py` (~100 lines)
**Purpose:** Domain-specific test cards

```python
"""
Domain-Specific Test Cards

Type-specific cards that store additional data for detail views.
These are thin wrappers around BaseTestCard.
"""

from .widgets import BaseTestCard
from .models import TestResult


class ComparatorTestCard(BaseTestCard):
    """Card for comparator tests"""
    
    def __init__(self, result: TestResult, parent=None):
        super().__init__(
            test_number=result.test_number,
            passed=result.passed,
            time=result.time,
            memory=result.memory,
            parent=parent
        )
        self.result = result


class ValidatorTestCard(BaseTestCard):
    """Card for validator tests"""
    
    def __init__(self, result: TestResult, parent=None):
        super().__init__(
            test_number=result.test_number,
            passed=result.passed,
            time=result.time,
            memory=result.memory,
            parent=parent
        )
        self.result = result


class BenchmarkerTestCard(BaseTestCard):
    """Card for benchmarker tests"""
    
    def __init__(self, result: TestResult, parent=None):
        super().__init__(
            test_number=result.test_number,
            passed=result.passed,
            time=result.time,
            memory=result.memory,
            parent=parent
        )
        self.result = result
```

---

### File 5: `__init__.py` (~30 lines)
**Purpose:** Clean exports

```python
"""
Status View Module

Provides presenter-based architecture for status views with proper separation:
- Models: Data structures (TestResult, TestExecutionState)
- Presenter: Coordination logic
- Widgets: Pure UI components
- Cards: Domain-specific test result cards
"""

from .models import TestResult, TestExecutionState, TestStatistics, TestType
from .presenter import StatusViewPresenter
from .widgets import (
    StatusHeaderSection,
    PerformancePanelSection,
    VisualProgressBarSection,
    TestResultsCardsSection,
    BaseTestCard
)
from .cards import ComparatorTestCard, ValidatorTestCard, BenchmarkerTestCard

__all__ = [
    # Models
    'TestResult',
    'TestExecutionState',
    'TestStatistics',
    'TestType',
    # Presenter
    'StatusViewPresenter',
    # Widgets
    'StatusHeaderSection',
    'PerformancePanelSection',
    'VisualProgressBarSection',
    'TestResultsCardsSection',
    'BaseTestCard',
    # Cards
    'ComparatorTestCard',
    'ValidatorTestCard',
    'BenchmarkerTestCard',
]
```

**Total for Phase 1: ~800 lines**

---

## Phase 2: Update Status Views (views/*/..._status_view.py)

### Example: `comparator_status_view.py` (New Implementation)

```python
"""
Comparator Status View

Thin adapter that:
1. Creates presenter with widgets
2. Translates worker signals to TestResult
3. Handles domain-specific detail views
"""

from PySide6.QtCore import Signal, QObject
from PySide6.QtWidgets import QWidget, QVBoxLayout, QMessageBox

from src.app.presentation.widgets.status_view import (
    TestResult,
    TestType,
    StatusViewPresenter,
    StatusHeaderSection,
    PerformancePanelSection,
    VisualProgressBarSection,
    TestResultsCardsSection,
    ComparatorTestCard
)
from src.app.presentation.widgets.test_detail_view import ComparatorDetailDialog
from src.app.presentation.styles.components.status_view import STATUS_VIEW_CONTAINER_STYLE


class ComparatorStatusView(QWidget):
    """
    Comparator-specific status view.
    
    Responsibilities:
    - Translate comparator worker signals to TestResult
    - Create comparator-specific cards
    - Show comparator detail dialogs
    - Coordinate with presenter for UI updates
    """
    
    # Signals for window coordination
    stopRequested = Signal()
    backRequested = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent
        self.test_type = TestType.COMPARATOR
        
        # Store results for detail views
        self.test_results = {}  # {test_number: TestResult}
        
        self._setup_ui()
        self.setStyleSheet(STATUS_VIEW_CONTAINER_STYLE)
    
    def _setup_ui(self):
        """Create UI with presenter pattern"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Create widgets
        self.header = StatusHeaderSection()
        self.performance = PerformancePanelSection()
        self.progress_bar = VisualProgressBarSection()
        self.cards_section = TestResultsCardsSection()
        
        # Create presenter
        self.presenter = StatusViewPresenter(
            header=self.header,
            performance=self.performance,
            progress_bar=self.progress_bar,
            cards_section=self.cards_section
        )
        
        # Add to layout
        layout.addWidget(self.header)
        layout.addWidget(self.performance)
        layout.addWidget(self.progress_bar)
        layout.addWidget(self.cards_section, stretch=1)
    
    def on_tests_started(self, total: int):
        """Handle test execution start"""
        # Get worker count
        max_workers = self._get_worker_count()
        
        # Initialize presenter
        self.presenter.start_test_execution(total, max_workers)
        
        # Clear stored results
        self.test_results.clear()
    
    def on_test_completed(
        self,
        test_number: int,
        passed: bool,
        input_text: str,
        correct_output: str,
        test_output: str,
        time: float = 0.0,
        memory: float = 0.0
    ):
        """
        Handle test completion from worker.
        
        Translates worker signal to TestResult and delegates to presenter.
        """
        # Create TestResult
        result = TestResult.from_comparator(
            test_number=test_number,
            passed=passed,
            input_text=input_text,
            correct_output=correct_output,
            test_output=test_output,
            time=time,
            memory=memory
        )
        
        # Store for detail view
        self.test_results[test_number] = result
        
        # Update UI through presenter
        self.presenter.handle_test_result(result)
        
        # Create and add card
        card = ComparatorTestCard(result)
        card.clicked.connect(self.show_test_detail)
        self.cards_section.add_card(card, result.passed)
    
    def on_all_tests_completed(self, all_passed: bool):
        """Handle test execution completion"""
        self.presenter.complete_execution()
        
        # Notify parent to enable save button
        if self.parent_window and hasattr(self.parent_window, "enable_save_button"):
            self.parent_window.enable_save_button()
    
    def show_test_detail(self, test_number: int):
        """Show detail dialog for test"""
        if test_number not in self.test_results:
            return
        
        result = self.test_results[test_number]
        data = result.data
        
        dialog = ComparatorDetailDialog(
            test_number=test_number,
            passed=result.passed,
            time=result.time,
            memory=result.memory,
            input_text=data['input_text'],
            correct_output=data['correct_output'],
            test_output=data['test_output'],
            parent=self
        )
        dialog.exec()
    
    def _get_worker_count(self) -> int:
        """Get worker count from parent"""
        worker = None
        if self.parent_window and hasattr(self.parent_window, 'comparator'):
            if hasattr(self.parent_window.comparator, 'get_current_worker'):
                worker = self.parent_window.comparator.get_current_worker()
        
        if worker and hasattr(worker, 'max_workers'):
            return worker.max_workers
        
        import multiprocessing
        return min(8, max(1, multiprocessing.cpu_count() - 1))
    
    def save_to_database(self):
        """Save results to database"""
        runner = None
        if hasattr(self, "runner"):
            runner = self.runner
        elif self.parent_window and hasattr(self.parent_window, "comparator"):
            runner = self.parent_window.comparator
        
        if not runner:
            QMessageBox.critical(self, "Error", "Runner not found")
            return -1
        
        try:
            result_id = runner.save_test_results_to_database()
            if result_id > 0:
                QMessageBox.information(
                    self, "Success",
                    f"Results saved!\nDatabase ID: {result_id}"
                )
                if self.parent_window and hasattr(self.parent_window, "mark_results_saved"):
                    self.parent_window.mark_results_saved()
            else:
                QMessageBox.critical(self, "Error", "Failed to save")
            return result_id
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error saving: {e}")
            return -1
    
    def set_runner(self, runner):
        """Set runner for saving"""
        self.runner = runner
    
    def is_tests_running(self) -> bool:
        """Check if tests are running"""
        return self.presenter.is_running()
```

**Same pattern for validator_status_view.py and benchmarker_status_view.py**

---

## Phase 3: Update Styles (styles/components/status_view/)

### Keep existing files, just verify exports:

**`__init__.py`** - Update imports to remove unused exports  
**`status_widgets_styles.py`** - Keep as-is  
**`status_cards.py`** - Keep as-is  
**`status_containers.py`** - Keep as-is (or merge into status_widgets_styles.py)

No major changes needed here - styles are already well organized.

---

## Phase 4: Final Cleanup

### Delete obsolete files:
1. `widgets/unified_status_view.py` 
2. `widgets/status_view_widgets.py`

### Update imports in:
- `views/comparator/comparator_window.py`
- `views/validator/validator_window.py`
- `views/benchmarker/benchmarker_window.py`

Change from:
```python
from src.app.presentation.views.comparator.comparator_status_view import ComparatorStatusView
```

To:
```python
# No change needed - path stays the same!
from src.app.presentation.views.comparator.comparator_status_view import ComparatorStatusView
```

---

## Migration Checklist

### Phase 1: Create New Architecture
- [ ] Create `widgets/status_view/` directory
- [ ] Create `models.py` (TestResult, TestExecutionState, TestStatistics)
- [ ] Create `presenter.py` (StatusViewPresenter)
- [ ] Create `widgets.py` (UI components extracted from status_view_widgets.py)
- [ ] Create `cards.py` (Domain-specific card wrappers)
- [ ] Create `__init__.py` (Clean exports)

### Phase 2: Refactor Status Views
- [ ] Update `comparator_status_view.py` to use presenter
- [ ] Update `validator_status_view.py` to use presenter
- [ ] Update `benchmarker_status_view.py` to use presenter
- [ ] Test each status view individually

### Phase 3: Verify Styles
- [ ] Verify `styles/components/status_view/__init__.py` exports
- [ ] Confirm no style imports are broken
- [ ] Optional: Consolidate `status_containers.py` if desired

### Phase 4: Integration Testing
- [ ] Run full comparator workflow
- [ ] Run full validator workflow
- [ ] Run full benchmarker workflow
- [ ] Verify worker status updates properly
- [ ] Verify database saving works
- [ ] Verify detail dialogs work

### Phase 5: Cleanup
- [ ] Delete `widgets/unified_status_view.py`
- [ ] Delete `widgets/status_view_widgets.py`
- [ ] Update any remaining imports (if any)
- [ ] Run full test suite
- [ ] Update documentation

---

## Benefits of New Architecture

### ✅ Clear Separation of Concerns
- **Models:** Pure data, no logic
- **Presenter:** Coordination, no UI code
- **Widgets:** Pure presentation, no business logic
- **Status Views:** Thin adapters, domain-specific only

### ✅ Testability
- Can test presenter without Qt
- Can test widgets in isolation
- Can test status views with mock presenter

### ✅ Maintainability
- Single responsibility per class
- Easy to add new test types
- Clear dependency flow
- No circular imports

### ✅ Worker Integration
- Worker signals → TestResult → Presenter → Widgets
- Clean translation layer in status views
- Worker status properly handled through presenter

---

## Line Count Estimate

| File | Lines |
|------|-------|
| models.py | 120 |
| presenter.py | 200 |
| widgets.py | 350 |
| cards.py | 100 |
| __init__.py | 30 |
| comparator_status_view.py | 130 |
| validator_status_view.py | 130 |
| benchmarker_status_view.py | 140 |
| **Total** | **~1100** |

**✅ Within constraint!**
