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
from src.app.presentation.styles.components.status_view.status_widgets_styles import (
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
    VISUAL_PROGRESS_BAR_SECTION_STYLE,
    PROGRESS_BAR_LEGEND_PASSED_STYLE,
    PROGRESS_BAR_LEGEND_FAILED_STYLE,
    get_progress_segment_style,
    CARDS_SECTION_PASSED_TITLE_STYLE,
    CARDS_SECTION_FAILED_TITLE_STYLE,
    CARDS_SECTION_EMPTY_LABEL_STYLE,
    CARDS_SECTION_SCROLLBAR_STYLE,
    TEST_RESULTS_CARDS_SECTION_STYLE,
)
from src.app.presentation.styles.components.status_view import (
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
    """Individual worker progress bar with pipeline stages"""
    
    def __init__(self, worker_id, parent=None):
        super().__init__(parent)
        self.worker_id = worker_id
        self.current_stage = None
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
        
        # Pipeline container with segmented stages
        self.pipeline_container = QWidget()
        self.pipeline_container.setFixedHeight(22)
        pipeline_layout = QHBoxLayout(self.pipeline_container)
        pipeline_layout.setContentsMargins(0, 0, 0, 0)
        pipeline_layout.setSpacing(2)
        
        # Create stage segments
        self.stages = {}
        self.stage_labels = {}
        
        # Define stages based on test type (will be set dynamically)
        self._create_idle_state()
        
        layout.addWidget(self.pipeline_container, stretch=1)
        
        self.time_label = QLabel("--")
        self.time_label.setFixedWidth(65)
        self.time_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.time_label.setStyleSheet(WORKER_TIME_LABEL_IDLE_STYLE)
        layout.addWidget(self.time_label)
    
    def _create_idle_state(self):
        """Show idle state (single gray segment)"""
        # Clear existing stages
        layout = self.pipeline_container.layout()
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        self.stages.clear()
        self.stage_labels.clear()
        
        # Single idle segment
        idle_segment = QLabel("Waiting for test...")
        idle_segment.setAlignment(Qt.AlignCenter)
        idle_segment.setStyleSheet("""
            QLabel {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgba(100, 100, 100, 0.15),
                    stop:1 rgba(80, 80, 80, 0.15));
                border: 1px solid rgba(255, 255, 255, 0.08);
                border-radius: 4px;
                color: rgba(255, 255, 255, 0.35);
                font-size: 11px;
                font-weight: 500;
                padding: 2px;
            }
        """)
        layout.addWidget(idle_segment, stretch=1)
    
    def _create_pipeline_stages(self, test_type: str):
        """Create pipeline stages based on test type"""
        # Clear existing
        layout = self.pipeline_container.layout()
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        self.stages.clear()
        self.stage_labels.clear()
        
        # Define stages per test type with CONSISTENT color palette
        # Using app's MATERIAL_COLORS design language:
        # - Primary (cyan blue) for generation
        # - Purple for middle/execution stages
        # - Accent (pink/magenta) for final evaluation
        GENERATE_COLOR = "#0096C7"  # primary - consistent blue for all generation
        MIDDLE_COLOR = "#B565D8"     # purple - for middle/execution stages
        FINAL_COLOR = "#F72585"      # accent - pink/magenta for final stages
        
        if test_type == "comparator":
            stages_config = [
                ("generate", "Generating Input", GENERATE_COLOR, 1),
                ("correct", "Expected Output", MIDDLE_COLOR, 1),
                ("evaluate", "Evaluating Test", FINAL_COLOR, 1)
            ]
        elif test_type == "validator":
            stages_config = [
                ("generate", "Generating Input", GENERATE_COLOR, 1),
                ("execute", "Running Test", MIDDLE_COLOR, 1),
                ("validate", "Validating", FINAL_COLOR, 1)
            ]
        elif test_type == "benchmarker":
            stages_config = [
                ("generate", "Generating Input", GENERATE_COLOR, 1),  # Equal size (1:1)
                ("benchmark", "Benchmarking", FINAL_COLOR, 1)         # Equal size (1:1)
            ]
        else:
            # Default generic pipeline
            stages_config = [
                ("prepare", "Preparing", GENERATE_COLOR, 1),
                ("execute", "Executing", MIDDLE_COLOR, 1),
                ("finalize", "Finalizing", FINAL_COLOR, 1)
            ]
        
        # Create segments
        for stage_id, stage_name, color, stretch in stages_config:
            segment = QLabel(stage_name)
            segment.setAlignment(Qt.AlignCenter)
            segment.setProperty("stage_id", stage_id)
            segment.setProperty("base_color", color)
            
            # Inactive style initially
            self._set_stage_style(segment, color, active=False)
            
            self.stages[stage_id] = segment
            self.stage_labels[stage_id] = stage_name
            layout.addWidget(segment, stretch=stretch)
    
    def _set_stage_style(self, segment: QLabel, color: str, active: bool):
        """Apply style to stage segment - inspired by titlebar but appropriate for small segments"""
        if active:
            # Check stage type for special styling
            is_primary = color.upper() == "#0096C7"     # Primary blue
            is_purple = color.upper() == "#B565D8"      # Purple
            is_accent = color.upper() == "#F72585"      # Accent pink
            
            if is_accent:
                # Accent/Final stage: subtle dark base with pink accent glow
                segment.setStyleSheet("""
                    QLabel {
                        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                            stop:0 rgba(32, 32, 34, 0.9),
                            stop:0.4 rgba(247, 37, 133, 0.5),
                            stop:0.6 rgba(216, 27, 96, 0.5),
                            stop:1 rgba(32, 32, 34, 0.9));
                        border: 1px solid rgba(247, 37, 133, 0.6);
                        border-radius: 4px;
                        color: rgba(255, 255, 255, 0.95);
                        font-size: 11px;
                        font-weight: 500;
                        padding: 2px;
                    }
                """)
            elif is_primary:
                # Primary stage: subtle dark base with cyan blue accent
                segment.setStyleSheet("""
                    QLabel {
                        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                            stop:0 rgba(32, 32, 34, 0.9),
                            stop:0.4 rgba(0, 150, 199, 0.5),
                            stop:0.6 rgba(0, 119, 182, 0.5),
                            stop:1 rgba(32, 32, 34, 0.9));
                        border: 1px solid rgba(64, 169, 212, 0.6);
                        border-radius: 4px;
                        color: rgba(255, 255, 255, 0.95);
                        font-size: 11px;
                        font-weight: 500;
                        padding: 2px;
                    }
                """)
            elif is_purple:
                # Purple stage: subtle dark base with purple accent
                segment.setStyleSheet("""
                    QLabel {
                        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                            stop:0 rgba(32, 32, 34, 0.9),
                            stop:0.4 rgba(181, 101, 216, 0.5),
                            stop:0.6 rgba(156, 75, 196, 0.5),
                            stop:1 rgba(32, 32, 34, 0.9));
                        border: 1px solid rgba(199, 125, 221, 0.6);
                        border-radius: 4px;
                        color: rgba(255, 255, 255, 0.95);
                        font-size: 11px;
                        font-weight: 500;
                        padding: 2px;
                    }
                """)
            else:
                # Fallback: simple gradient
                segment.setStyleSheet(f"""
                    QLabel {{
                        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                            stop:0 {color}DD,
                            stop:1 {color}AA);
                        border: 1px solid {color}BB;
                        border-radius: 4px;
                        color: rgba(255, 255, 255, 0.95);
                        font-size: 11px;
                        font-weight: 500;
                        padding: 2px;
                    }}
                """)
        else:
            # Inactive: ALL segments use same gray from design system
            segment.setStyleSheet("""
                QLabel {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 rgba(75, 85, 99, 0.25),
                        stop:1 rgba(55, 65, 81, 0.20));
                    border: 1px solid rgba(63, 63, 63, 0.5);
                    border-radius: 4px;
                    color: rgba(179, 179, 179, 0.5);
                    font-size: 11px;
                    font-weight: 500;
                    padding: 2px;
                }
            """)
    
    def set_status(self, test_number=None, progress=0.0, elapsed=0.0, stage: str = None, test_type: str = "comparator"):
        """
        Update worker status with pipeline stage.
        
        Args:
            test_number: Test number or None for idle
            progress: Progress 0.0-1.0 (used to determine stage)
            elapsed: Elapsed time
            stage: Explicit stage name ("generate", "correct", "evaluate", etc.)
            test_type: Type of test ("comparator", "validator", "benchmarker")
        """
        if test_number:
            self.test_label.setText(f"Test #{test_number}")
            self.test_label.setStyleSheet(WORKER_TEST_LABEL_ACTIVE_STYLE)
            self.time_label.setText(f"{elapsed:.1f}s")
            self.time_label.setStyleSheet(WORKER_TIME_LABEL_ACTIVE_STYLE)
            
            # Create pipeline if needed
            if not self.stages:
                self._create_pipeline_stages(test_type)
            
            # Determine active stage from progress if not explicit
            if stage is None:
                stage_count = len(self.stages)
                if progress < 0.33:
                    stage_idx = 0
                elif progress < 0.66:
                    stage_idx = 1
                else:
                    stage_idx = 2 if stage_count > 2 else 1
                stage = list(self.stages.keys())[min(stage_idx, stage_count - 1)]
            
            # Update stage visuals
            for stage_id, segment in self.stages.items():
                color = segment.property("base_color")
                is_active = (stage_id == stage)
                self._set_stage_style(segment, color, active=is_active)
            
            self.current_stage = stage
        else:
            # Idle state
            self.test_label.setText("Idle")
            self.test_label.setStyleSheet(WORKER_TEST_LABEL_IDLE_STYLE)
            self.time_label.setText("--")
            self.time_label.setStyleSheet(WORKER_TIME_LABEL_IDLE_STYLE)
            self._create_idle_state()
            self.current_stage = None

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
