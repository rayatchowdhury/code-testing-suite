#!/usr/bin/env python3
"""
Application entry point for Code Testing Suite.

This module can be executed as:
- python src/app/__main__.py
- python -m src.app
- python -m app (when src is in PYTHONPATH)

The entry point handles proper import path setup and graceful fallbacks
for different execution contexts during the migration process.
"""

import os
import sys
from pathlib import Path

# Add project root to path for import compatibility
project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Also add src directory for direct imports
src_root = project_root / "src"
if str(src_root) not in sys.path:
    sys.path.insert(0, str(src_root))

# Set Qt API before any Qt imports
os.environ["QT_API"] = "pyside6"


def setup_logging():
    """Initialize basic logging"""
    import logging

    logging.basicConfig(level=logging.WARNING)
    # Suppress noisy HTTP logs
    logging.getLogger("urllib3.connectionpool").setLevel(logging.ERROR)


def get_app_icon():
    """Get application icon with multiple fallbacks"""
    icon_paths = [
        "src/resources/icons/app_icon.png",
        "resources/icons/app_icon.png",
        "icons/app_icon.png",
    ]

    for icon_path in icon_paths:
        if Path(icon_path).exists():
            return str(icon_path)

    return None  # No icon found


def load_emoji_font():
    """Load Noto Color Emoji font for consistent emoji display across platforms"""
    from PySide6.QtGui import QFontDatabase
    
    # Try different possible paths for the emoji font
    font_paths = [
        "src/app/presentation/styles/fonts/NotoColorEmoji-subset.ttf",
        "src/app/presentation/styles/fonts/NotoColorEmoji.ttf",
    ]
    
    for font_path in font_paths:
        full_path = project_root / font_path
        if full_path.exists():
            font_id = QFontDatabase.addApplicationFont(str(full_path))
            if font_id != -1:
                families = QFontDatabase.applicationFontFamilies(font_id)
                print(f"✅ Loaded emoji font: {families}")
                return True
            else:
                print(f"⚠️ Failed to load font from: {font_path}")
    
    print("⚠️ Emoji font not found, emojis may display as blocks on some systems")
    return False


def create_main_window():
    """Create main window using src structure"""
    # Debug: Force reload any modules for testing
    import importlib

    modules_to_reload = [
        "src.app.presentation.views.main_window.main_window",
        "src.app.presentation.views.main_window.main_window_content",
    ]
    for module in modules_to_reload:
        if module in sys.modules:
            print(f"Reloading module: {module}")
            importlib.reload(sys.modules[module])

    try:
        # Use relative import within src.app package
        from src.app.presentation.views.main_window.main_window import MainWindow

        print(
            "Creating MainWindow from src.app.presentation.views.main_window.main_window"
        )
        return MainWindow()
    except ImportError as e:
        # If relative import fails, try absolute import
        try:
            from src.app.presentation.views.main_window.main_window import MainWindow

            print("Creating MainWindow from absolute import")
            return MainWindow()
        except ImportError:
            raise ImportError(f"Could not import MainWindow: {e}")


def main():
    """Main application entry point with comprehensive error handling"""
    try:
        # Initialize logging first
        setup_logging()

        # Initialize workspace structure before any windows open
        from src.app.shared.constants import WORKSPACE_DIR, ensure_user_data_dir
        from src.app.shared.utils.workspace_utils import ensure_workspace_structure

        ensure_user_data_dir()
        ensure_workspace_structure(WORKSPACE_DIR)

        # Import Qt components
        import asyncio

        import qasync
        from PySide6.QtCore import Qt
        from PySide6.QtGui import QIcon
        from PySide6.QtWidgets import QApplication

        # Set attributes before creating QApplication
        QApplication.setAttribute(Qt.AA_UseDesktopOpenGL)
        QApplication.setAttribute(Qt.AA_ShareOpenGLContexts)

        # Create application
        app = QApplication(sys.argv)
        app.setApplicationName("Code Testing Suite")
        app.setApplicationVersion("1.0.0")
        
        # Load emoji font for consistent display across platforms
        load_emoji_font()

        # Set application icon if available
        icon_path = get_app_icon()
        if icon_path:
            app.setWindowIcon(QIcon(icon_path))

        # Create event loop
        loop = qasync.QEventLoop(app)
        asyncio.set_event_loop(loop)

        # Create and show main window
        try:
            window = create_main_window()
            window.show()

            print("✅ Code Testing Suite started successfully")

            # Run the event loop
            with loop:
                loop.run_forever()

        except Exception as e:
            print(f"❌ Failed to create main window: {e}")
            import traceback

            traceback.print_exc()
            sys.exit(1)

    except ImportError as e:
        print(f"❌ Failed to import required modules: {e}")
        print("Make sure PySide6 and other dependencies are installed:")
        print("pip install PySide6 qasync")
        sys.exit(1)

    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
