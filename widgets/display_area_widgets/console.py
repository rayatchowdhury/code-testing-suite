from PySide6.QtWidgets import QWidget, QVBoxLayout, QTextEdit, QLineEdit, QScrollBar
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QKeyEvent
from styles.style import MATERIAL_COLORS

class ConsoleOutput(QWidget):
    inputSubmitted = Signal(str)

    def __init__(self):
        super().__init__()
        self.command_history = []
        self.history_index = 0
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        
        # Output area with styling
        self.output = QTextEdit()
        self.output.setReadOnly(True)
        self.output.setStyleSheet(f"""
            QTextEdit {{
                background-color: {MATERIAL_COLORS['surface_dim']};
                color: {MATERIAL_COLORS['text_primary']};
                border: none;
                font-family: 'Consolas', monospace;
                font-size: 12px;
                padding: 8px;
            }}
        """)
        self.layout.addWidget(self.output)
        
        # Input area with styling
        self.input = QLineEdit()
        self.input.setStyleSheet(f"""
            QLineEdit {{
                background-color: {MATERIAL_COLORS['surface']};
                color: {MATERIAL_COLORS['text_primary']};
                border: 1px solid {MATERIAL_COLORS['outline']};
                border-radius: 4px;
                padding: 6px;
                font-family: 'Consolas', monospace;
                font-size: 12px;
            }}
        """)
        self.input.returnPressed.connect(self._handleInput)
        self.layout.addWidget(self.input)
        
        self.setLayout(self.layout)

    def displayOutput(self, text):
        self.output.append(text.rstrip())
        # Scroll to bottom
        scrollbar = self.output.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def _handleInput(self):
        text = self.input.text().strip()
        if text:
            self.command_history.append(text)
            self.history_index = len(self.command_history)
            self.displayOutput(f"> {text}")
            self.inputSubmitted.emit(text)
            self.input.clear()

    def keyPressEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key_Up and self.command_history:
            self.history_index = max(0, self.history_index - 1)
            self.input.setText(self.command_history[self.history_index])
        elif event.key() == Qt.Key_Down and self.command_history:
            self.history_index = min(len(self.command_history), self.history_index + 1)
            if self.history_index < len(self.command_history):
                self.input.setText(self.command_history[self.history_index])
            else:
                self.input.clear()
        else:
            super().keyPressEvent(event)

    def clear(self):
        self.output.clear()