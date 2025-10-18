"""
Status View Statistics and Inline Layout Styles.

Styles for the 3-row status layout:
- Row 1: Progress bar (in status_progress.py)
- Row 2: Stats row (percentage, time, counts, workers)
- Row 3: Individual worker status badges

Also includes styles for inline stats panel and empty state labels.
Uses Material Design colors and spacing constants.
"""

from src.app.presentation.styles.constants.colors import MATERIAL_COLORS
from src.app.presentation.styles.constants.spacing import SPACING, FONTS, BORDER_RADIUS, BORDER_WIDTH

# ============================================================================
# ROW 2: STATS ROW STYLES
# ============================================================================

STATS_ROW_PERCENTAGE_STYLE = f"""
QLabel {{
    color: {MATERIAL_COLORS['primary']};
    font-size: {FONTS['HEADER']}px;
    font-weight: {FONTS['WEIGHT_EXTRABOLD']};
    background: transparent;
}}
"""

STATS_ROW_TIME_STYLE = f"""
QLabel {{
    color: {MATERIAL_COLORS['on_surface']};
    font-size: {FONTS['TITLE']}px;
    font-weight: {FONTS['WEIGHT_SEMIBOLD']};
    background: transparent;
}}
"""

STATS_ROW_PROGRESS_STYLE = f"""
QLabel {{
    color: {MATERIAL_COLORS['on_surface']};
    font-size: {FONTS['TITLE']}px;
    font-weight: {FONTS['WEIGHT_SEMIBOLD']};
    background: transparent;
}}
"""

STATS_ROW_PASSED_STYLE = f"""
QLabel {{
    color: {MATERIAL_COLORS['primary']};
    font-size: {FONTS['TITLE']}px;
    font-weight: {FONTS['WEIGHT_BOLD']};
    background: transparent;
}}
"""

STATS_ROW_FAILED_STYLE = f"""
QLabel {{
    color: {MATERIAL_COLORS['error']};
    font-size: {FONTS['TITLE']}px;
    font-weight: {FONTS['WEIGHT_BOLD']};
    background: transparent;
}}
"""

STATS_ROW_WORKERS_ACTIVE_STYLE = f"""
QLabel {{
    color: {MATERIAL_COLORS['secondary']};
    font-size: {FONTS['TITLE']}px;
    font-weight: {FONTS['WEIGHT_BOLD']};
    background: transparent;
}}
"""

# ============================================================================
# ROW 3: WORKER STATUS BADGES
# ============================================================================

WORKER_BADGE_IDLE_STYLE = f"""
QLabel {{
    color: {MATERIAL_COLORS['on_surface_variant']};
    font-size: {FONTS['BODY_LG']}px;
    font-weight: {FONTS['WEIGHT_MEDIUM']};
    background: {MATERIAL_COLORS['surface_variant']};
    border: {BORDER_WIDTH['THIN']}px solid {MATERIAL_COLORS['outline_variant']};
    border-radius: {BORDER_RADIUS['SM']}px;
    padding: {SPACING['SM']}px {SPACING['MD']}px;
}}
"""

WORKER_BADGE_ACTIVE_STYLE = f"""
QLabel {{
    color: {MATERIAL_COLORS['on_primary_container']};
    font-size: {FONTS['BODY_LG']}px;
    font-weight: {FONTS['WEIGHT_BOLD']};
    background: {MATERIAL_COLORS['primary_container']};
    border: {BORDER_WIDTH['MEDIUM']}px solid {MATERIAL_COLORS['primary']};
    border-radius: {BORDER_RADIUS['SM']}px;
    padding: {SPACING['SM']}px {SPACING['MD']}px;
}}
"""

# ============================================================================
# INLINE STATS PANEL STYLES
# ============================================================================

STATS_INLINE_DIVIDER_STYLE = f"""
QLabel {{
    color: {MATERIAL_COLORS['outline']};
    font-size: {FONTS['TITLE_SM']}px;
    font-weight: {FONTS['WEIGHT_LIGHT']};
    background: transparent;
    padding: 0px {SPACING['SM']}px;
}}
"""

STATS_INLINE_PERCENTAGE_STYLE = f"""
QLabel {{
    color: {MATERIAL_COLORS['primary']};
    font-size: {FONTS['DISPLAY']}px;
    font-weight: {FONTS['WEIGHT_EXTRABOLD']};
    background: transparent;
    letter-spacing: -0.5px;
}}
"""

STATS_INLINE_PROGRESS_STYLE = f"""
QLabel {{
    color: {MATERIAL_COLORS['on_surface']};
    font-size: {FONTS['SUBTITLE']}px;
    font-weight: {FONTS['WEIGHT_SEMIBOLD']};
    background: transparent;
}}
"""

STATS_INLINE_COUNTS_STYLE = f"""
QLabel {{
    color: {MATERIAL_COLORS['on_surface_variant']};
    font-size: {FONTS['BODY']}px;
    font-weight: {FONTS['WEIGHT_MEDIUM']};
    background: transparent;
}}
"""

STATS_INLINE_WORKER_STYLE = f"""
QLabel {{
    color: {MATERIAL_COLORS['primary']};
    font-size: {FONTS['BODY']}px;
    font-weight: {FONTS['WEIGHT_BOLD']};
    background: transparent;
    letter-spacing: 0.3px;
}}
"""

# ============================================================================
# EMPTY STATE LABELS
# ============================================================================

EMPTY_STATE_LABEL_STYLE = f"""
QLabel {{
    color: {MATERIAL_COLORS['on_surface_variant']};
    font-size: {FONTS['BODY_LG']}px;
    font-weight: {FONTS['WEIGHT_MEDIUM']};
    font-style: italic;
    padding: {SPACING['XL'] * 2}px {SPACING['XL']}px;
    background: transparent;
}}
"""
