"""
Syntax highlighting color schemes for the code editor
"""

# Modern Monokai-inspired color scheme for C++ syntax highlighting
SYNTAX_HIGHLIGHTING_COLORS = {
    'keyword': '#ff6c6c',      # Keywords (if, for, while, etc.)
    'class': '#66d9ef',        # Class names and types
    'function': '#a6e22e',     # Function names
    'operator': '#f92672',     # Operators (+, -, =, etc.)
    'brace': '#ffffff',        # Braces and brackets
    'string': '#e6db74',       # String literals
    'number': '#ae81ff',       # Numeric literals
    'comment': '#75715e',      # Comments
    'preprocessor': '#a6e22e', # Preprocessor directives
    'namespace': '#66d9ef',    # Namespace identifiers
    'std_class': '#66d9ef',    # Standard library classes
    'constant': '#ae81ff'      # Constants and macros
}

# Alternative color schemes can be added here in the future
SYNTAX_SCHEMES = {
    'monokai': SYNTAX_HIGHLIGHTING_COLORS,
    # 'dark': {...},
    # 'light': {...}
}

# Default scheme
DEFAULT_SYNTAX_SCHEME = 'monokai'
