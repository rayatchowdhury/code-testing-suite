"""
Enhanced Status View Widgets V2 - Glassmorphism Design
Based on status_view_demo_v2.py layout with circular progress ring and improved visual hierarchy.
Includes all visual features: confetti, glow effects, glassmorphism, animations.
"""

import random
from PySide6.QtCore import Qt, Property, QPropertyAnimation, QEasingCurve, QTimer, QRectF, Signal
from PySide6.QtGui import QPainter, QPen, QColor, QFont
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
    QGraphicsDropShadowEffect,
    QGraphicsBlurEffect,
)

from src.app.presentation.styles.constants.colors import MATERIAL_COLORS
from src.app.presentation.styles.fonts.emoji import set_emoji_font
from src.app.presentation.styles.components.status_view import (
    TEST_CARD_LABEL_HEADER_STYLE,
    TEST_CARD_LABEL_METRIC_STYLE,
    TEST_CARD_LABEL_STATUS_FAILED_STYLE,
    TEST_CARD_LABEL_STATUS_PASSED_STYLE,
    get_test_card_style,
)
from src.app.presentation.styles.components.status_view.status_widgets_styles import (
    STATUS_HEADER_TIME_LABEL_STYLE,
    STATUS_HEADER_ETA_LABEL_STYLE,
    STATUS_HEADER_SPEED_LABEL_STYLE,
    STATUS_HEADER_COMPLETION_LABEL_STYLE,
    STATUS_HEADER_PASSED_LABEL_STYLE,
    STATUS_HEADER_FAILED_LABEL_STYLE,
    STATUS_HEADER_SECTION_STYLE,
    PERFORMANCE_PANEL_SUMMARY_LABEL_STYLE,
    PERFORMANCE_PANEL_TOGGLE_BUTTON_STYLE,
    PERFORMANCE_PANEL_SECTION_STYLE,
    WORKER_LABEL_STYLE,
    WORKER_TEST_LABEL_IDLE_STYLE,
    WORKER_TEST_LABEL_ACTIVE_STYLE,
    WORKER_TIME_LABEL_IDLE_STYLE,
    WORKER_TIME_LABEL_ACTIVE_STYLE,
    PROGRESS_BAR_LEGEND_PASSED_STYLE,
    PROGRESS_BAR_LEGEND_FAILED_STYLE,
    VISUAL_PROGRESS_BAR_SECTION_STYLE,
    CARDS_SECTION_PASSED_TITLE_STYLE,
    CARDS_SECTION_FAILED_TITLE_STYLE,
    CARDS_SECTION_EMPTY_LABEL_STYLE,
    CARDS_SECTION_SCROLLBAR_STYLE,
    TEST_RESULTS_CARDS_SECTION_STYLE,
    get_worker_progress_container_style,
    get_progress_segment_style,
)


# ============================================================================
# CONFETTI PARTICLE SYSTEM
# ============================================================================
class ConfettiParticle:
    """Single confetti particle with physics"""
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.vx = random.uniform(-3, 3)
        self.vy = random.uniform(-8, -4)
        self.rotation = random.uniform(0, 360)
        self.rotation_speed = random.uniform(-10, 10)
        self.color = random.choice([
            MATERIAL_COLORS['success'],
            MATERIAL_COLORS['info'],
            MATERIAL_COLORS['warning'],
            MATERIAL_COLORS['accent'],
            '#FFD700',  # Gold
            '#FF69B4',  # Hot pink
        ])
        self.size = random.randint(6, 12)
        self.gravity = 0.3
        self.lifetime = 100
        self.alpha = 255
    
    def update(self):
        self.vy += self.gravity
        self.x += self.vx
        self.y += self.vy
        self.rotation += self.rotation_speed
        self.lifetime -= 1
        self.alpha = int((self.lifetime / 100) * 255)
        return self.lifetime > 0


class ConfettiOverlay(QWidget):
    """Confetti overlay widget for celebration"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.particles = []
        self.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.setAttribute(Qt.WA_TranslucentBackground)
        if parent:
            self.setGeometry(parent.rect())
        
        self.timer = QTimer()
        self.timer.timeout.connect(self._update_particles)
        
    def start_confetti(self):
        """Start confetti animation"""
        # Create particles from top center
        center_x = self.width() // 2
        for _ in range(80):
            self.particles.append(ConfettiParticle(
                center_x + random.randint(-100, 100),
                -20
            ))
        self.timer.start(16)  # 60 FPS
        
    def _update_particles(self):
        self.particles = [p for p in self.particles if p.update()]
        if not self.particles:
            self.timer.stop()
        self.update()
        
    def paintEvent(self, event):
        if not self.particles:
            return
            
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        for particle in self.particles:
            painter.save()
            painter.translate(particle.x, particle.y)
            painter.rotate(particle.rotation)
            
            color = QColor(particle.color)
            color.setAlpha(particle.alpha)
            painter.setBrush(color)
            painter.setPen(Qt.NoPen)
            
            # Draw rectangle confetti
            half_size = particle.size // 2
            painter.drawRect(-half_size, -half_size, particle.size, particle.size)
            
            painter.restore()


# ============================================================================
# CIRCULAR PROGRESS RING
# ============================================================================
class ProgressRing(QWidget):
    """Circular progress indicator with smooth animation and GLOW effect (matching demo exactly)"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._progress = 0.0
        self._animated_progress = 0.0  # For smooth animation
        self._passed = 0
        self._failed = 0
        self.setFixedSize(150, 150)
        
        # Animation for smooth progress
        self.progress_animation = QPropertyAnimation(self, b"animated_progress")
        self.progress_animation.setDuration(800)  # 800ms smooth animation
        self.progress_animation.setEasingCurve(QEasingCurve.OutCubic)
        
    @Property(float)
    def progress(self):
        return self._progress
    
    @progress.setter
    def progress(self, value):
        self._progress = value
        # Animate to new progress value
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
        
        # Background ring with glassmorphism
        pen = QPen(QColor(MATERIAL_COLORS['progress_track']), 15)
        pen.setCapStyle(Qt.RoundCap)
        painter.setPen(pen)
        painter.drawArc(rect, 0, 360 * 16)
        
        # Progress ring color with glow
        if self._failed > 0:
            color = QColor(MATERIAL_COLORS['error'])
        elif self._passed > 0:
            color = QColor(MATERIAL_COLORS['success'])
        else:
            color = QColor(MATERIAL_COLORS['info'])
        
        # Outer glow (3 layers for depth)
        for i in range(3):
            glow_color = QColor(color)
            glow_color.setAlpha(30 - i * 10)
            pen = QPen(glow_color, 15 + i * 3)
            pen.setCapStyle(Qt.RoundCap)
            painter.setPen(pen)
            span = int(self._animated_progress * 3.6 * 16)  # Use animated value
            painter.drawArc(rect.adjusted(-i*2, -i*2, i*2, i*2), 90 * 16, -span)
        
        # Main ring
        pen = QPen(color, 15)
        pen.setCapStyle(Qt.RoundCap)
        painter.setPen(pen)
        span_angle = int(self._animated_progress * 3.6 * 16)  # Use animated value
        painter.drawArc(rect, 90 * 16, -span_angle)
        
        # Percentage text
        painter.setPen(QColor(MATERIAL_COLORS['text_primary']))
        font = QFont("Segoe UI", 28, QFont.Bold)
        painter.setFont(font)
        painter.drawText(rect, Qt.AlignCenter, f"{int(self._animated_progress)}%")



# ============================================================================
# STATUS HEADER SECTION
# ============================================================================
class StatusHeaderSection(QWidget):
    """Header section with circular progress ring and stats in 3-column layout"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(190)
        self.start_time = None
        self._setup_ui()
        
    def _setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(40)
        
        # LEFT SECTION: Time stats (elapsed, remaining, speed) - RIGHT ALIGNED
        left_section = QWidget()
        left_layout = QVBoxLayout(left_section)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(8)
        left_layout.setAlignment(Qt.AlignVCenter | Qt.AlignRight)
        
        # Time elapsed
        self.time_label = QLabel("⏱ 0:00 elapsed")
        self.time_label.setAlignment(Qt.AlignRight)
        self.time_label.setStyleSheet(STATUS_HEADER_TIME_LABEL_STYLE)
        left_layout.addWidget(self.time_label)
        
        # ETA
        self.eta_label = QLabel("⏳ ~0:00 remaining")
        self.eta_label.setAlignment(Qt.AlignRight)
        self.eta_label.setStyleSheet(STATUS_HEADER_ETA_LABEL_STYLE)
        left_layout.addWidget(self.eta_label)
        
        # Speed
        self.speed_label = QLabel("⚡ 0.00 tests/sec")
        self.speed_label.setAlignment(Qt.AlignRight)
        self.speed_label.setStyleSheet(STATUS_HEADER_SPEED_LABEL_STYLE)
        left_layout.addWidget(self.speed_label)
        
        layout.addWidget(left_section, stretch=1)
        
        # CENTER SECTION: Progress ring
        ring_container = QWidget()
        ring_layout = QVBoxLayout(ring_container)
        ring_layout.setContentsMargins(0, 0, 0, 0)
        ring_layout.addStretch()
        self.progress_ring = ProgressRing()
        ring_layout.addWidget(self.progress_ring, alignment=Qt.AlignCenter)
        ring_layout.addStretch()
        layout.addWidget(ring_container)
        
        # RIGHT SECTION: Test completion and results - LEFT ALIGNED
        right_section = QWidget()
        right_layout = QVBoxLayout(right_section)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(8)
        right_layout.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)
        
        # Completion count
        self.completion_label = QLabel("0 / 0 tests")
        self.completion_label.setAlignment(Qt.AlignLeft)
        self.completion_label.setStyleSheet(STATUS_HEADER_COMPLETION_LABEL_STYLE)
        right_layout.addWidget(self.completion_label)
        
        # Pass count with percentage
        self.passed_label = QLabel("✓ 0 passed (0%)")
        self.passed_label.setAlignment(Qt.AlignLeft)
        self.passed_label.setStyleSheet(STATUS_HEADER_PASSED_LABEL_STYLE)
        right_layout.addWidget(self.passed_label)
        
        # Fail count with percentage
        self.failed_label = QLabel("✗ 0 failed (0%)")
        self.failed_label.setAlignment(Qt.AlignLeft)
        self.failed_label.setStyleSheet(STATUS_HEADER_FAILED_LABEL_STYLE)
        right_layout.addWidget(self.failed_label)
        
        layout.addWidget(right_section, stretch=1)
        
        # Glassmorphism background (exact demo styling)
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
# PERFORMANCE PANEL (COLLAPSIBLE)
# ============================================================================
class PerformancePanelSection(QWidget):
    """Collapsible performance metrics panel with worker details"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._expanded = False
        self._setup_ui()
        
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 10, 24, 10)
        layout.setSpacing(8)
        
        # Header
        header_layout = QHBoxLayout()
        
        self.summary_label = QLabel("⚡ 0 Workers │ 0.00 tests/s")
        self.summary_label.setStyleSheet(PERFORMANCE_PANEL_SUMMARY_LABEL_STYLE)
        header_layout.addWidget(self.summary_label)
        
        header_layout.addStretch()
        
        # Toggle button
        self.toggle_btn = QPushButton("Show Details ▼")
        self.toggle_btn.setStyleSheet(PERFORMANCE_PANEL_TOGGLE_BUTTON_STYLE)
        self.toggle_btn.clicked.connect(self._toggle_expanded)
        header_layout.addWidget(self.toggle_btn)
        
        layout.addLayout(header_layout)
        
        # Workers container
        self.workers_container = QWidget()
        workers_layout = QVBoxLayout(self.workers_container)
        workers_layout.setContentsMargins(0, 10, 0, 0)
        workers_layout.setSpacing(8)
        
        self.worker_bars = []
        self.workers_container.setVisible(False)
        layout.addWidget(self.workers_container)
        
        # Glassmorphism
        self.setStyleSheet(PERFORMANCE_PANEL_SECTION_STYLE)
    
    def setup_workers(self, worker_count: int):
        """Setup worker progress bars"""
        # Clear existing workers
        for bar in self.worker_bars:
            bar.deleteLater()
        self.worker_bars.clear()
        
        # Create new worker bars
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


class WorkerProgressBar(QWidget):
    """Individual worker progress bar with glassmorphism"""
    
    def __init__(self, worker_id, parent=None):
        super().__init__(parent)
        self.worker_id = worker_id
        self._setup_ui()
        
    def _setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)
        
        # Worker label
        self.worker_label = QLabel(f"Worker {self.worker_id}")
        self.worker_label.setFixedWidth(75)
        self.worker_label.setStyleSheet(WORKER_LABEL_STYLE)
        layout.addWidget(self.worker_label)
        
        # Test info
        self.test_label = QLabel("Idle")
        self.test_label.setFixedWidth(85)
        self.test_label.setStyleSheet(WORKER_TEST_LABEL_IDLE_STYLE)
        layout.addWidget(self.test_label)
        
        # Progress bar container
        self.progress_container = QWidget()
        self.progress_container.setFixedHeight(22)
        self.progress_container.setStyleSheet(get_worker_progress_container_style(idle=True, progress=0.0))
        layout.addWidget(self.progress_container, stretch=1)
        
        # Time label
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
            
            # Animated progress
            self.progress_container.setStyleSheet(get_worker_progress_container_style(idle=False, progress=progress))
        else:
            self.test_label.setText("Idle")
            self.test_label.setStyleSheet(WORKER_TEST_LABEL_IDLE_STYLE)
            self.time_label.setText("--")
            self.progress_container.setStyleSheet(get_worker_progress_container_style(idle=True, progress=0.0))


# ============================================================================
# VISUAL PROGRESS BAR SECTION
# ============================================================================
class VisualProgressBarSection(QWidget):
    """Segmented progress bar with glassmorphism and legend"""
    
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
        
        # Segments container
        self.segments_layout = QHBoxLayout()
        self.segments_layout.setSpacing(0)
        layout.addLayout(self.segments_layout)
        
        # Legend
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
        
        # Glassmorphism
        self.setStyleSheet(VISUAL_PROGRESS_BAR_SECTION_STYLE)
    
    def reset(self, total_tests: int):
        """Reset progress bar"""
        self.test_results = []
        
        # Clear existing segments
        while self.segments_layout.count():
            item = self.segments_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self.segments = []
        
        # Calculate segments
        segment_count = min(100, total_tests)
        self.tests_per_segment = max(1, total_tests // segment_count)
        
        # Create segments
        for i in range(segment_count):
            segment = QFrame()
            segment.setFixedSize(max(8, 900 // segment_count), 32)
            
            # Determine position for border radius
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
        
        # Reset legend
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
            
            # Update color and style using helper function
            if segment['failed'] > 0:
                state = 'failed'
            elif segment['passed'] > 0:
                state = 'passed'
            else:
                state = 'pending'
            
            segment['widget'].setStyleSheet(get_progress_segment_style(state, segment['position']))
        
        # Update legend
        passed_count = sum(1 for _, p in self.test_results if p)
        failed_count = len(self.test_results) - passed_count
        self.passed_legend.setText(f"■ {passed_count} Passed")
        self.failed_legend.setText(f"■ {failed_count} Failed")


# ============================================================================
# TEST RESULTS SECTION (CARDS)
# ============================================================================
class TestResultsCardsSection(QWidget):
    """Dual-column test results with custom scrollbars"""
    
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
        
        # Scrollbar style
        passed_scroll = QScrollArea()
        passed_scroll.setWidgetResizable(True)
        passed_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        passed_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        passed_scroll.setStyleSheet(CARDS_SECTION_SCROLLBAR_STYLE)
        
        self.passed_cards_widget = QWidget()
        self.passed_cards_layout = QVBoxLayout(self.passed_cards_widget)
        self.passed_cards_layout.setAlignment(Qt.AlignTop)
        self.passed_cards_layout.setSpacing(10)
        
        # Empty state
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
        
        # Empty state
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
        # Clear passed cards
        while self.passed_cards_layout.count() > 1:  # Keep empty label
            item = self.passed_cards_layout.takeAt(1)
            if item.widget():
                item.widget().deleteLater()
        
        # Clear failed cards
        while self.failed_cards_layout.count() > 1:  # Keep empty label
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
        """Add test card to appropriate column"""
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
# TEST CARDS (Individual Results)
# ============================================================================
class BaseTestCard(QFrame):
    """
    Base test card widget.

    Displays test number, pass/fail status, and time/memory metrics.
    Emits clicked signal when clicked to show detail view.
    """

    clicked = Signal(int)  # Emits test number when clicked

    def __init__(
        self, test_number: int, passed: bool, time: float, memory: float, parent=None
    ):
        """
        Initialize test card.

        Args:
            test_number: Test case number (1-indexed)
            passed: Whether test passed
            time: Execution time in seconds
            memory: Memory usage in MB
            parent: Parent widget
        """
        super().__init__(parent)
        self.test_number = test_number
        self.passed = passed
        self.time = time
        self.memory = memory

        self._setup_ui()
        self._apply_styling()

    def _setup_ui(self):
        """Setup card UI with header and metrics"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 12, 14, 12)
        layout.setSpacing(8)

        # Header row: Test # | Status
        header_layout = QHBoxLayout()

        self.test_label = QLabel(f"Test #{self.test_number}")
        self.test_label.setStyleSheet(TEST_CARD_LABEL_HEADER_STYLE)

        self.status_label = QLabel("✓ Passed" if self.passed else "✗ Failed")
        status_style = (
            TEST_CARD_LABEL_STATUS_PASSED_STYLE
            if self.passed
            else TEST_CARD_LABEL_STATUS_FAILED_STYLE
        )
        self.status_label.setStyleSheet(status_style)

        header_layout.addWidget(self.test_label)
        header_layout.addStretch()
        header_layout.addWidget(self.status_label)

        # Metrics row: Time | Memory
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

        # Make clickable
        self.setMouseTracking(True)
        self.setCursor(Qt.PointingHandCursor)

    def _apply_styling(self):
        """Apply card styling with gradient background based on pass/fail"""
        self.setStyleSheet(get_test_card_style(self.passed))

    def mousePressEvent(self, event):
        """Handle mouse click to emit signal"""
        if event.button() == Qt.LeftButton:
            self.clicked.emit(self.test_number)
        super().mousePressEvent(event)

    def update_metrics(self, time: float, memory: float):
        """
        Update time and memory metrics.

        Args:
            time: New execution time in seconds
            memory: New memory usage in MB
        """
        self.time = time
        self.memory = memory
        self.time_label.setText(f"⏱️ {self.time:.3f}s")
        self.memory_label.setText(f"💾 {self.memory:.1f} MB")
        set_emoji_font(self.time_label)
        set_emoji_font(self.memory_label)


class ComparatorTestCard(BaseTestCard):
    """
    Comparator-specific test card.

    Stores input, expected output, and actual output for comparison tests.
    """

    def __init__(
        self,
        test_number: int,
        passed: bool,
        time: float,
        memory: float,
        input_text: str,
        correct_output: str,
        test_output: str,
        parent=None,
    ):
        """
        Initialize comparator test card.

        Args:
            test_number: Test case number
            passed: Whether test passed
            time: Execution time in seconds
            memory: Memory usage in MB
            input_text: Test input
            correct_output: Expected output
            test_output: Actual program output
            parent: Parent widget
        """
        self.input_text = input_text
        self.correct_output = correct_output
        self.test_output = test_output
        super().__init__(test_number, passed, time, memory, parent)


class ValidatorTestCard(BaseTestCard):
    """
    Validator-specific test card.

    Stores expected output and actual output for validator tests.
    """

    def __init__(
        self,
        test_number: int,
        passed: bool,
        time: float,
        memory: float,
        expected_output: str,
        actual_output: str,
        parent=None,
    ):
        """
        Initialize validator test card.

        Args:
            test_number: Test case number
            passed: Whether test passed
            time: Execution time in seconds
            memory: Memory usage in MB
            expected_output: Expected output
            actual_output: Actual program output
            parent: Parent widget
        """
        self.expected_output = expected_output
        self.actual_output = actual_output
        super().__init__(test_number, passed, time, memory, parent)


class BenchmarkerTestCard(BaseTestCard):
    """
    Benchmarker-specific test card.

    Stores additional performance metrics for benchmark tests.
    """

    def __init__(
        self,
        test_number: int,
        passed: bool,
        time: float,
        memory: float,
        test_size: int,
        parent=None,
    ):
        """
        Initialize benchmarker test card.

        Args:
            test_number: Test case number
            passed: Whether test passed (time/memory within limits)
            time: Execution time in seconds
            memory: Memory usage in MB
            test_size: Size of test input
            parent: Parent widget
        """
        self.test_size = test_size
        super().__init__(test_number, passed, time, memory, parent)

