import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from views.main_window import MainWindow

def main():
    QApplication.setAttribute(Qt.AA_UseDesktopOpenGL)
    app = QApplication(sys.argv)
    
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()