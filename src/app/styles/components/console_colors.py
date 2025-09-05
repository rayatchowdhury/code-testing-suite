"""
Console color definitions for different types of output
"""
from ...styles.constants.colors import MATERIAL_COLORS

# Console output color scheme
CONSOLE_COLORS = {
    'default': MATERIAL_COLORS['text_primary'],
    'success': '#4CAF50',    # Green - for successful operations
    'error': '#FF5252',      # Red - for errors
    'info': '#2196F3',       # Blue - for informational messages
    'warning': '#FFC107',    # Amber - for warnings
    'input': '#E040FB',      # Purple - for user input
    'prompt': '#FF4081',     # Pink - for command prompts
    'filename': '#FFA726',   # Orange - for filenames
    'executable': '#26C6DA', # Cyan - for executable paths
}

# Status-specific colors
CONSOLE_STATUS_COLORS = {
    'compilation_success': CONSOLE_COLORS['success'],
    'compilation_error': CONSOLE_COLORS['error'],
    'execution_success': CONSOLE_COLORS['info'],
    'execution_error': CONSOLE_COLORS['error'],
    'test_pass': CONSOLE_COLORS['success'],
    'test_fail': CONSOLE_COLORS['error'],
}
