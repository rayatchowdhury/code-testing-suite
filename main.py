import sys
import os
# Set Qt API before any Qt imports
os.environ['QT_API'] = 'pyside6'

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
import qasync
import asyncio
from constants import APP_ICON

# Initialize logging configuration early (handles all third-party noise)
from utils.logging_config import LoggingConfig
LoggingConfig.initialize()

def main():
    # Set attributes before creating QApplication
    QApplication.setAttribute(Qt.AA_UseDesktopOpenGL)
    QApplication.setAttribute(Qt.AA_ShareOpenGLContexts)
    
    app = QApplication(sys.argv)
    
    # Set application icon
    app.setWindowIcon(QIcon(APP_ICON))
    
    # Create event loop
    loop = qasync.QEventLoop(app)
    asyncio.set_event_loop(loop)
    
    # Lazy import MainWindow to reduce startup time
    from views.main_window import MainWindow
    window = MainWindow()
    window.show()
    
    # Run the event loop
    with loop:
        loop.run_forever()

if __name__ == '__main__': 
    main()
