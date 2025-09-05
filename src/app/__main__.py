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

import sys
import os
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
os.environ['QT_API'] = 'pyside6'

def setup_logging():
    """Initialize logging configuration early"""
    try:
        from src.app.utils.logging_config import LoggingConfig
        LoggingConfig.initialize()
    except ImportError:
        try:
            from app.utils.logging_config import LoggingConfig
            LoggingConfig.initialize()
        except ImportError:
            try:
                from .utils.logging_config import LoggingConfig
                LoggingConfig.initialize()
            except ImportError:
                # Fallback to basic logging
                import logging
                logging.basicConfig(level=logging.INFO)

def get_app_icon():
    """Get application icon with multiple fallbacks"""
    icon_paths = [
        "src/resources/icons/app_icon.png",
        "resources/icons/app_icon.png", 
        "icons/app_icon.png"
    ]
    
    for icon_path in icon_paths:
        if Path(icon_path).exists():
            return str(icon_path)
    
    return None  # No icon found

def create_main_window():
    """Create main window using src structure"""
    try:
        # Use relative import within src.app package
        from .views.main_window import MainWindow
        return MainWindow()
    except ImportError as e:
        # If relative import fails, try absolute import
        try:
            from src.app.views.main_window import MainWindow
            return MainWindow()
        except ImportError:
            raise ImportError(f"Could not import MainWindow: {e}")

def main():
    """Main application entry point with comprehensive error handling"""
    try:
        # Initialize logging first
        setup_logging()
        
        # Import Qt components
        from PySide6.QtWidgets import QApplication
        from PySide6.QtCore import Qt
        from PySide6.QtGui import QIcon
        import qasync
        import asyncio
        
        # Set attributes before creating QApplication
        QApplication.setAttribute(Qt.AA_UseDesktopOpenGL)
        QApplication.setAttribute(Qt.AA_ShareOpenGLContexts)
        
        # Create application
        app = QApplication(sys.argv)
        app.setApplicationName("Code Testing Suite")
        app.setApplicationVersion("1.0.0")
        
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

if __name__ == '__main__':
    main()
