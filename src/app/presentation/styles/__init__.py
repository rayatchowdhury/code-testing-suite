from src.app.presentation.styles.components import (
    CONSOLE_STYLE,
    SCROLLBAR_STYLE,
    SIDEBAR_BUTTON_STYLE,
    SIDEBAR_STYLE,
    SPLITTER_STYLE,
)
from src.app.presentation.styles.components.console_colors import CONSOLE_COLORS
from src.app.presentation.styles.components.sidebar_dividers import (
    SIDEBAR_DIVIDER_CONTAINER_STYLE,
    SIDEBAR_DIVIDER_SPACE_STYLE,
    SIDEBAR_FOOTER_CONTAINER_STYLE,
    SIDEBAR_FOOTER_DIVIDER_STYLE,
    SIDEBAR_FOOTER_SPACE_STYLE,
    SIDEBAR_MAIN_DIVIDER_STYLE,
    SIDEBAR_VERTICAL_FOOTER_DIVIDER_STYLE,
)
from src.app.presentation.styles.components.syntax_highlighting import (
    SYNTAX_HIGHLIGHTING_COLORS,
)
from src.app.presentation.styles.constants import COLORS, MATERIAL_COLORS
from src.app.presentation.styles.constants.status_colors import (
    ERROR_COLOR_HEX,
    STATUS_COLORS,
    TEST_STATUS_COLORS,
)
from src.app.presentation.styles.style import DISPLAY_AREA_STYLE, get_tab_style

# Syntax Highlighters
from src.app.presentation.styles.syntaxhighlighter import (
    CPPSyntaxHighlighter,
    JavaSyntaxHighlighter,
    PythonSyntaxHighlighter,
)

__all__ = [
    "COLORS",
    "MATERIAL_COLORS",
    "SCROLLBAR_STYLE",
    "SIDEBAR_STYLE",
    "SIDEBAR_BUTTON_STYLE",
    "SPLITTER_STYLE",
    "DISPLAY_AREA_STYLE",
    "CONSOLE_STYLE",
    "get_tab_style",
    "CPPSyntaxHighlighter",
    "PythonSyntaxHighlighter",
    "JavaSyntaxHighlighter",
]
