import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
import qasync
import asyncio
from absl import logging as absl_logging
from constants import APP_ICON

def main():
    # Initialize absl logging before anything else
    absl_logging.use_absl_handler()
    absl_logging.set_verbosity(absl_logging.WARNING)
    
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
