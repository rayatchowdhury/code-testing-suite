from PySide6.QtWidgets import (
    QApplication, QWidget, QHBoxLayout, QVBoxLayout,
    QToolButton, QMenu, QStackedWidget, QLabel
)
from PySide6.QtCore import Qt

app = QApplication([])

class TabButton(QToolButton):
    def __init__(self, label, parent=None):
        super().__init__(parent)
        self.setText(label)
        self.setCheckable(True)
        self.setToolButtonStyle(Qt.ToolButtonTextOnly)
        self.setPopupMode(QToolButton.MenuButtonPopup)

        # Dropdown menu for extensions
        menu = QMenu(self)
        for ext in ["cpp", "py", "java", "other"]:
            menu.addAction(ext, lambda ext=ext: self.set_extension(ext))
        self.setMenu(menu)

        self.extension = "cpp"  # default
        self.update_label()

    def set_extension(self, ext):
        self.extension = ext
        self.update_label()

    def update_label(self):
        self.setText(f"{self.text().split('.')[0]}.{self.extension}")

# Main window
window = QWidget()
layout = QVBoxLayout(window)

# Tab bar replacement
tab_bar = QHBoxLayout()
buttons = []
stack = QStackedWidget()

for name in ["gen", "cor", "tes"]:
    btn = TabButton(name)
    tab_bar.addWidget(btn)
    buttons.append(btn)

    page = QLabel(f"This is {name}.cpp page")
    page.setAlignment(Qt.AlignCenter)
    stack.addWidget(page)

# Toggle behavior: only one checked
def make_switcher(idx, btn):
    btn.clicked.connect(lambda: (
        [b.setChecked(False) for i, b in enumerate(buttons) if i != idx],
        stack.setCurrentIndex(idx)
    ))

for i, b in enumerate(buttons):
    make_switcher(i, b)

layout.addLayout(tab_bar)
layout.addWidget(stack)

window.resize(400, 250)
window.show()
app.exec()
