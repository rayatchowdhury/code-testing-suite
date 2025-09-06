
SPLITTER_STYLE = """
QSplitter::handle {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 rgba(255, 255, 255, 0),
                stop:0.5 rgba(255, 255, 255, 0.1),
                stop:1 rgba(255, 255, 255, 0));
    width: 2px;
    margin: 2px 0px;
}

QSplitter::handle:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 rgba(0, 150, 199, 0),
                stop:0.5 rgba(0, 150, 199, 0.3),
                stop:1 rgba(0, 150, 199, 0));
}
"""
