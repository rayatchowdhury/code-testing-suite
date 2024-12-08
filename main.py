import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtGui import QIcon
from views.main_window import MainWindow


def main():
    # Set attributes before creating QApplication
    QApplication.setAttribute(Qt.AA_UseDesktopOpenGL)
    QApplication.setAttribute(Qt.AA_ShareOpenGLContexts)  # Required for WebEngine
    
    app = QApplication(sys.argv)
    
    # Set application icon
    app.setWindowIcon(QIcon("resources/icons/app_icon.png"))
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == '__main__': 
    main()
