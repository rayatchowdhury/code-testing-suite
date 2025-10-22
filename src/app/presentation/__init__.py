"""
Presentation module for the Code Testing Suite.

This module contains the user interface components and view logic.
"""

# Lazy imports to avoid circular dependencies
def get_main_window():
    """Lazy import of MainWindow"""
    from src.app.presentation.windows.main import MainWindow

    return MainWindow


# Lazy module access to avoid circular imports
def __getattr__(name):
    if name == "design_system":
        from src.app.presentation.shared import design_system
        return design_system
    elif name == "widgets":
        # Backward compatibility: redirect to shared.components
        from src.app.presentation.shared import components
        return components
    elif name == "dialogs":
        # Backward compatibility: redirect to shared.dialogs
        from src.app.presentation.shared import dialogs
        return dialogs
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = ["get_main_window", "design_system", "widgets", "dialogs"]
