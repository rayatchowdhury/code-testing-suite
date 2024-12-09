import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtGui import QIcon
from views.main_window import MainWindow
import qasync
import asyncio

def main():
    # Set attributes before creating QApplication
    QApplication.setAttribute(Qt.AA_UseDesktopOpenGL)
    QApplication.setAttribute(Qt.AA_ShareOpenGLContexts)  # Required for WebEngine
    
    app = QApplication(sys.argv)
    
    # Set application icon
    app.setWindowIcon(QIcon("resources/icons/app_icon.png"))
    
    # Create event loop
    loop = qasync.QEventLoop(app)
    asyncio.set_event_loop(loop)
    
    window = MainWindow()
    window.show()
    
    # Run the event loop
    with loop:
        loop.run_forever()

if __name__ == '__main__': 
    main()
