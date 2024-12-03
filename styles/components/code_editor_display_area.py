from ..constants.colors import MATERIAL_COLORS

SPLITTER_STYLE = """
QSplitter::handle {
    background: transparent;
    width: 2px;
}
"""

OUTER_PANEL_STYLE = """
    background: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1,
        stop:0.0 #1A0611,
        stop:0.1 #200714,
        stop:0.2 #260817,
        stop:0.3 #200714,
        stop:0.4 #1A0611,
        stop:0.5 #260817,
        stop:0.6 #1A0611,
        stop:0.7 #200714,
        stop:0.8 #260817,
        stop:0.9 #200714,
        stop:1.0 #1A0611
    );
    padding: 3px;
"""

# Remove duplicate get_tab_style() as it's now in editor.py