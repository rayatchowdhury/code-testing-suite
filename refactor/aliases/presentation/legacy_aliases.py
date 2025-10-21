"""
Legacy Aliases - Temporary Import Compatibility Layer
Provides backward-compatible imports during migration.

REMOVE THIS FILE IN PHASE 4 (Cleanup).
"""

# ============================================================================
# PHASE 1: Style Consolidation Aliases
# ============================================================================

# Main style module
try:
    from src.app.presentation.design_system.styles.style import *
except ImportError:
    pass

# Common styles
try:
    from src.app.presentation.design_system.styles.common_styles import *
except ImportError:
    pass

# Inline styles
try:
    from src.app.presentation.design_system.styles.inline_styles import *
except ImportError:
    pass

# Syntax highlighter
try:
    from src.app.presentation.design_system.styles.syntaxhighlighter import *
except ImportError:
    pass

# Component styles
try:
    from src.app.presentation.design_system.styles.components.editor import *
except ImportError:
    pass

try:
    from src.app.presentation.design_system.styles.components.console import *
except ImportError:
    pass

try:
    from src.app.presentation.design_system.styles.components.sidebar import *
except ImportError:
    pass

try:
    from src.app.presentation.design_system.styles.components.scrollbar import *
except ImportError:
    pass

try:
    from src.app.presentation.design_system.styles.components.splitter import *
except ImportError:
    pass

try:
    from src.app.presentation.design_system.styles.components.results import *
except ImportError:
    pass

# ============================================================================
# PHASE 2: Navigation Unification Aliases
# ============================================================================

# Window Manager
try:
    from src.app.presentation.navigation.window_manager import WindowManager, WindowFactory
except ImportError:
    pass

# Router
try:
    from src.app.presentation.navigation.router import NavigationRouter
except ImportError:
    pass

# ============================================================================
# PHASE 3: Feature Pods Aliases
# ============================================================================

# Generally not needed as features should be self-contained
# Add specific aliases if cross-feature dependencies exist temporarily

# ============================================================================
# Backward Compatibility Mappings
# ============================================================================

# Map old style imports to new design_system imports
# Usage: from src.app.presentation.styles.style import get_style
#        will resolve via this alias

__all__ = [
    # Add exported symbols here as needed
    "WindowManager",
    "WindowFactory",
    "NavigationRouter",
]
