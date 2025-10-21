"""
Status View Widgets Styles - Glassmorphism V2 Design.

All stylesheet strings extracted from status_view_widgets.py for better organization.
Uses MATERIAL_COLORS for consistency across the application.

Includes styles for:
- Status Header Section (time stats, progress ring, completion stats)
- Performance Panel (worker summary and details)  
- Worker Progress Bars
- Visual Progress Bar Section (segmented progress with legend)
- Test Results Cards Section (dual-column scrollable cards)
"""

from src.app.presentation.styles.constants.colors import MATERIAL_COLORS


# ============================================================================
# STATUS HEADER SECTION STYLES
# ============================================================================

STATUS_HEADER_TIME_LABEL_STYLE = f"""
font-size: 16px;
font-weight: 600;
color: {MATERIAL_COLORS['text_secondary']};
background: transparent;
"""

STATUS_HEADER_ETA_LABEL_STYLE = f"""
font-size: 16px;
font-weight: 600;
color: {MATERIAL_COLORS['text_secondary']};
background: transparent;
"""

STATUS_HEADER_SPEED_LABEL_STYLE = f"""
font-size: 16px;
font-weight: 600;
color: {MATERIAL_COLORS['info']};
background: transparent;
"""

STATUS_HEADER_COMPLETION_LABEL_STYLE = f"""
font-size: 22px;
font-weight: 700;
color: {MATERIAL_COLORS['text_primary']};
background: transparent;
letter-spacing: 0.3px;
"""

STATUS_HEADER_PASSED_LABEL_STYLE = f"""
font-size: 18px;
font-weight: 600;
color: {MATERIAL_COLORS['success']};
background: transparent;
"""

STATUS_HEADER_FAILED_LABEL_STYLE = f"""
font-size: 18px;
font-weight: 600;
color: {MATERIAL_COLORS['error']};
background: transparent;
"""

STATUS_HEADER_SECTION_STYLE = f"""
StatusHeaderSection {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 rgba(36, 36, 38, 0.95),
        stop:0.5 rgba(31, 31, 33, 0.98),
        stop:1 rgba(36, 36, 38, 0.95));
    border-bottom: 1px solid {MATERIAL_COLORS['border']};
    border-left: 3px solid {MATERIAL_COLORS['primary']};
}}
"""


# ============================================================================
"""

# Performance Panel Styles
# ============================================================================

PERFORMANCE_PANEL_SUMMARY_LABEL_STYLE = f"""
font-size: 13px;
font-weight: 600;
color: {MATERIAL_COLORS['text_secondary']};
background: transparent;
"""

PERFORMANCE_PANEL_TOGGLE_BUTTON_STYLE = f"""
QPushButton {{
    background: rgba(0, 150, 199, 0.1);
    border: 1px solid rgba(0, 150, 199, 0.3);
    color: {MATERIAL_COLORS['info']};
    font-size: 12px;
    font-weight: 600;
    padding: 6px 12px;
    border-radius: 6px;
}}
QPushButton:hover {{
    background: rgba(0, 150, 199, 0.2);
    border: 1px solid rgba(0, 150, 199, 0.5);
}}
QPushButton:pressed {{
    background: rgba(0, 150, 199, 0.15);
}}
"""

PERFORMANCE_PANEL_SECTION_STYLE = f"""
PerformancePanelSection {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 rgba(31, 31, 33, 0.92),
        stop:1 rgba(36, 36, 38, 0.90));
    border-bottom: 1px solid {MATERIAL_COLORS['border']};
    border-left: 3px solid {MATERIAL_COLORS['purple']};
}}
"""


# ============================================================================
# WORKER PROGRESS BAR STYLES
# ============================================================================

WORKER_LABEL_STYLE = f"""
font-size: 12px;
font-weight: 600;
color: {MATERIAL_COLORS['text_secondary']};
background: transparent;
"""

WORKER_TEST_LABEL_IDLE_STYLE = f"""
font-size: 12px;
color: {MATERIAL_COLORS['text_disabled']};
background: transparent;
"""

WORKER_TEST_LABEL_ACTIVE_STYLE = f"""
font-size: 12px;
color: {MATERIAL_COLORS['info']};
font-weight: 600;
background: transparent;
"""

WORKER_TIME_LABEL_IDLE_STYLE = f"""
font-size: 11px;
color: {MATERIAL_COLORS['text_disabled']};
background: transparent;
"""

WORKER_TIME_LABEL_ACTIVE_STYLE = f"""
font-size: 11px;
color: {MATERIAL_COLORS['text_secondary']};
background: transparent;
"""

# ============================================================================
# VISUAL PROGRESS BAR SECTION STYLES
# ============================================================================

PROGRESS_BAR_LEGEND_PASSED_STYLE = f"""
font-size: 12px;
color: {MATERIAL_COLORS['success']};
font-weight: 600;
background: transparent;
"""

PROGRESS_BAR_LEGEND_FAILED_STYLE = f"""
font-size: 12px;
color: {MATERIAL_COLORS['error']};
font-weight: 600;
background: transparent;
"""

VISUAL_PROGRESS_BAR_SECTION_STYLE = f"""
VisualProgressBarSection {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 rgba(31, 31, 33, 0.88),
        stop:1 rgba(36, 36, 38, 0.92));
    border-bottom: 1px solid {MATERIAL_COLORS['border']};
    border-left: 3px solid {MATERIAL_COLORS['accent']};
}}
"""

"""

def get_progress_segment_style(state: str, position: str = 'middle') -> str:
    """
    Get progress segment style based on state and position.
    
    Args:
        state: 'passed', 'failed', or 'default'
        position: 'first', 'last', or 'middle'
    """
    # Determine border radius based on position
    if position == 'first':
        border_radius = "border-radius: 8px 0 0 8px;"
    elif position == 'last':
        border_radius = "border-radius: 0 8px 8px 0;"
    else:
        border_radius = "border-radius: 0;"
    
    # Determine colors based on state
    if state == 'passed':
        color = MATERIAL_COLORS['success']
        border_color = 'rgba(76, 175, 80, 0.6)'
    elif state == 'failed':
        color = MATERIAL_COLORS['error']
        border_color = 'rgba(255, 107, 107, 0.6)'
    else:  # default
        color = MATERIAL_COLORS['surface_dim']
        border_color = MATERIAL_COLORS['outline']
    
    return f"""
        QFrame {{
            background: {color};
            border: 1px solid {border_color};
            {border_radius}
        }}
    """


# ============================================================================
# TEST RESULTS CARDS SECTION STYLES
# ============================================================================

CARDS_SECTION_PASSED_TITLE_STYLE = f"""
font-size: 16px;
font-weight: 700;
color: {MATERIAL_COLORS['success']};
background: transparent;
padding: 10px 0;
letter-spacing: 0.3px;
"""

CARDS_SECTION_FAILED_TITLE_STYLE = f"""
font-size: 16px;
font-weight: 700;
color: {MATERIAL_COLORS['error']};
background: transparent;
padding: 10px 0;
letter-spacing: 0.3px;
"""

CARDS_SECTION_EMPTY_LABEL_STYLE = f"""
font-size: 14px;
color: {MATERIAL_COLORS['text_disabled']};
background: transparent;
padding: 40px;
"""

CARDS_SECTION_SCROLLBAR_STYLE = f"""
QScrollArea {{
    border: none;
    background: transparent;
}}
QScrollBar:vertical {{
    background: {MATERIAL_COLORS['surface_dim']};
    width: 12px;
    border-radius: 6px;
    margin: 2px;
}}
QScrollBar::handle:vertical {{
    background: rgba(255, 255, 255, 0.25);
    border-radius: 6px;
    min-height: 40px;
}}
QScrollBar::handle:vertical:hover {{
    background: rgba(255, 255, 255, 0.35);
}}
QScrollBar::handle:vertical:pressed {{
    background: rgba(255, 255, 255, 0.45);
}}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0px;
}}
QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
    background: none;
}}
"""

TEST_RESULTS_CARDS_SECTION_STYLE = f"""
TestResultsCardsSection {{
    background: {MATERIAL_COLORS['background']};
}}
"""


# ============================================================================
# EXPORTS
# ============================================================================

__all__ = [
    # Status Header
    "STATUS_HEADER_TIME_LABEL_STYLE",
    "STATUS_HEADER_ETA_LABEL_STYLE",
    "STATUS_HEADER_SPEED_LABEL_STYLE",
    "STATUS_HEADER_COMPLETION_LABEL_STYLE",
    "STATUS_HEADER_PASSED_LABEL_STYLE",
    "STATUS_HEADER_FAILED_LABEL_STYLE",
    "STATUS_HEADER_SECTION_STYLE",
    # Performance Panel
    "PERFORMANCE_PANEL_SUMMARY_LABEL_STYLE",
    "PERFORMANCE_PANEL_TOGGLE_BUTTON_STYLE",
    "PERFORMANCE_PANEL_SECTION_STYLE",
    # Worker Progress
    "WORKER_LABEL_STYLE",
    "WORKER_TEST_LABEL_IDLE_STYLE",
    "WORKER_TEST_LABEL_ACTIVE_STYLE",
    "WORKER_TIME_LABEL_IDLE_STYLE",
    "WORKER_TIME_LABEL_ACTIVE_STYLE",
    # Visual Progress Bar
    "PROGRESS_BAR_LEGEND_PASSED_STYLE",
    "PROGRESS_BAR_LEGEND_FAILED_STYLE",
    "VISUAL_PROGRESS_BAR_SECTION_STYLE",
    "get_progress_segment_style",
    # Test Results Cards
    "CARDS_SECTION_PASSED_TITLE_STYLE",
    "CARDS_SECTION_FAILED_TITLE_STYLE",
    "CARDS_SECTION_EMPTY_LABEL_STYLE",
    "CARDS_SECTION_SCROLLBAR_STYLE",
    "TEST_RESULTS_CARDS_SECTION_STYLE",
]
