from src.app.presentation.styles.constants.colors import MATERIAL_COLORS

RESULTS_COMBO_STYLE = f"""
QComboBox {{
    background-color: {MATERIAL_COLORS['surface_variant']};
    border: 1px solid {MATERIAL_COLORS['outline']};
    border-radius: 8px;
    padding: 8px 12px;
    color: {MATERIAL_COLORS['on_surface']};
    font-size: 13px;
    min-width: 120px;
}}
QComboBox:hover {{
    border-color: {MATERIAL_COLORS['primary']};
    background-color: {MATERIAL_COLORS['surface_bright']};
}}
QComboBox::drop-down {{
    border: none;
    width: 20px;
}}
QComboBox::down-arrow {{
    image: none;
    border-left: 5px solid transparent;
    border-right: 5px solid transparent;
    border-top: 5px solid {MATERIAL_COLORS['on_surface']};
    margin-right: 5px;
}}
"""

RESULTS_BUTTON_STYLE = f"""
QPushButton {{
    background-color: {MATERIAL_COLORS['primary']};
    border: none;
    border-radius: 8px;
    color: {MATERIAL_COLORS['on_primary']};
    padding: 10px 20px;
    font-weight: 500;
    font-size: 13px;
}}
QPushButton:hover {{
    background-color: {MATERIAL_COLORS['primary_container']};
    color: {MATERIAL_COLORS['on_primary_container']};
}}
QPushButton:pressed {{
    background-color: {MATERIAL_COLORS['surface_dim']};
}}
"""

RESULTS_TAB_WIDGET_STYLE = f"""
QTabWidget::pane {{
    background-color: {MATERIAL_COLORS['surface_variant']};
    border: 1px solid {MATERIAL_COLORS['outline_variant']};
    border-radius: 8px;
    margin-top: -1px;
}}
QTabBar::tab {{
    background-color: {MATERIAL_COLORS['surface_variant']};
    border: 1px solid {MATERIAL_COLORS['outline_variant']};
    border-bottom: none;
    border-top-left-radius: 8px;
    border-top-right-radius: 8px;
    padding: 10px 20px;
    margin-right: 2px;
    color: {MATERIAL_COLORS['on_surface_variant']};
    font-weight: 500;
}}
QTabBar::tab:selected {{
    background-color: {MATERIAL_COLORS['primary_container']};
    color: {MATERIAL_COLORS['on_primary_container']};
    border-color: {MATERIAL_COLORS['primary']};
}}
QTabBar::tab:hover:!selected {{
    background-color: {MATERIAL_COLORS['surface_bright']};
    color: {MATERIAL_COLORS['on_surface']};
}}
"""

RESULTS_TABLE_STYLE = f"""
QTableWidget {{
    background-color: {MATERIAL_COLORS['surface']};
    border: 1px solid {MATERIAL_COLORS['outline_variant']};
    border-radius: 8px;
    gridline-color: {MATERIAL_COLORS['outline_variant']};
    color: {MATERIAL_COLORS['on_surface']};
    font-size: 13px;
}}
QTableWidget::item {{
    padding: 8px;
    border-bottom: 1px solid {MATERIAL_COLORS['outline_variant']};
}}
QTableWidget::item:selected {{
    background-color: {MATERIAL_COLORS['primary_container']};
    color: {MATERIAL_COLORS['on_primary_container']};
}}
QTableWidget::item:alternate {{
    background-color: {MATERIAL_COLORS['surface_variant']};
}}
QHeaderView::section {{
    background-color: {MATERIAL_COLORS['surface_bright']};
    border: 1px solid {MATERIAL_COLORS['outline']};
    padding: 8px 12px;
    color: {MATERIAL_COLORS['on_surface']};
    font-weight: 600;
    font-size: 13px;
}}
"""

RESULTS_TABLE_SMALL_STYLE = f"""
QTableWidget {{
    background-color: {MATERIAL_COLORS['surface']};
    border: 1px solid {MATERIAL_COLORS['outline_variant']};
    border-radius: 8px;
    gridline-color: {MATERIAL_COLORS['outline_variant']};
    color: {MATERIAL_COLORS['on_surface']};
    font-size: 12px;
}}
QTableWidget::item {{
    padding: 6px;
    border-bottom: 1px solid {MATERIAL_COLORS['outline_variant']};
}}
QTableWidget::item:selected {{
    background-color: {MATERIAL_COLORS['primary_container']};
    color: {MATERIAL_COLORS['on_primary_container']};
}}
QHeaderView::section {{
    background-color: {MATERIAL_COLORS['surface_bright']};
    border: 1px solid {MATERIAL_COLORS['outline']};
    padding: 6px 8px;
    color: {MATERIAL_COLORS['on_surface']};
    font-weight: 600;
    font-size: 12px;
}}
"""

RESULTS_TEXT_EDIT_STYLE = f"""
QTextEdit {{
    background-color: {MATERIAL_COLORS['surface_variant']};
    border: 1px solid {MATERIAL_COLORS['outline']};
    border-radius: 8px;
    padding: 12px;
    color: {MATERIAL_COLORS['on_surface']};
    font-size: 13px;
    font-family: 'Consolas', 'Monaco', monospace;
}}
QTextEdit:focus {{
    border-color: {MATERIAL_COLORS['primary']};
    background-color: {MATERIAL_COLORS['surface_bright']};
}}
"""

RESULTS_PROGRESS_BAR_STYLE = f"""
QProgressBar {{
    background-color: {MATERIAL_COLORS['surface_variant']};
    border: 1px solid {MATERIAL_COLORS['outline']};
    border-radius: 8px;
    text-align: center;
    color: {MATERIAL_COLORS['on_surface']};
    font-weight: 500;
    height: 20px;
}}
QProgressBar::chunk {{
    background-color: {MATERIAL_COLORS['primary']};
    border-radius: 7px;
    margin: 1px;
}}
"""

RESULTS_FILTERS_PANEL_STYLE = f"""
QWidget {{
    background-color: {MATERIAL_COLORS['surface_variant']};
    border: 1px solid {MATERIAL_COLORS['outline_variant']};
    border-radius: 12px;
}}
"""

RESULTS_CARD_STYLE = f"""
QWidget {{
    background-color: {MATERIAL_COLORS['surface_variant']};
    border: 1px solid {MATERIAL_COLORS['outline_variant']};
    border-radius: 12px;
}}
"""

RESULTS_LABEL_TITLE_STYLE = f"""
color: {MATERIAL_COLORS['on_surface']};
font-weight: 600;
font-size: 16px;
margin-bottom: 8px;
"""

RESULTS_LABEL_FILTER_STYLE = f"""
color: {MATERIAL_COLORS['on_surface']};
font-weight: 500;
"""

RESULTS_LABEL_STAT_STYLE = f"""
color: {MATERIAL_COLORS['on_surface']};
font-size: 14px;
padding: 4px 0px;
"""

RESULTS_LABEL_DETAILS_STYLE = f"""
color: {MATERIAL_COLORS['on_surface']};
font-weight: 600;
font-size: 14px;
margin-top: 8px;
"""


# Error Label Styles
ERROR_LABEL_STYLE = f"""
color: {MATERIAL_COLORS['error']};
"""

ERROR_LABEL_BOLD_STYLE = f"""
color: {MATERIAL_COLORS['error']};
font-weight: 600;
font-size: 14px;
"""


def create_error_label(text: str, bold: bool = False) -> "QLabel":
    """
    Create a QLabel with error styling.
    
    Args:
        text: The error message text
        bold: If True, use bold styling
    
    Returns:
        Configured QLabel with error styling
    """
    from PySide6.QtWidgets import QLabel
    
    label = QLabel(text)
    if bold:
        label.setStyleSheet(ERROR_LABEL_BOLD_STYLE)
    else:
        label.setStyleSheet(ERROR_LABEL_STYLE)
    return label

