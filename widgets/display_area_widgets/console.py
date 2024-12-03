from PySide6.QtWidgets import QWidget, QVBoxLayout, QTextEdit, QLineEdit, QScrollBar, QLabel
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QKeyEvent, QTextCharFormat, QColor, QTextCursor
from styles.style import MATERIAL_COLORS

class ConsoleOutput(QWidget):
    inputSubmitted = Signal(str)
    inputRequested = Signal()  # Add this signal

    def __init__(self):
        super().__init__()
        self.command_history = []
        self.history_index = 0
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)  # Remove spacing between widgets
        
        # Output title with center alignment and different styling
        output_title = QLabel("Console Output")
        output_title.setAlignment(Qt.AlignCenter)
        output_title.setFixedHeight(26)  # Reduced from default
        output_title.setStyleSheet(f"""
            QLabel {{
                background: {MATERIAL_COLORS['surface_dim']};
                color: {MATERIAL_COLORS['text_primary']};
                font-weight: bold;
                font-family: 'Segoe UI';
                font-size: 12px;
                padding: 6px;
                border-bottom: 1px solid {MATERIAL_COLORS['outline_variant']};
            }}
        """)
        self.layout.addWidget(output_title)
        
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
        
        # Input title with center alignment and matching style
        input_title = QLabel("Console Input")
        input_title.setAlignment(Qt.AlignCenter)
        input_title.setFixedHeight(26)  # Reduced from default
        input_title.setStyleSheet(f"""
            QLabel {{
                background: {MATERIAL_COLORS['surface_dim']};
                color: {MATERIAL_COLORS['text_primary']};
                font-weight: bold;
                font-family: 'Segoe UI';
                font-size: 12px;
                padding: 6px;
                border-top: 1px solid {MATERIAL_COLORS['outline_variant']};
                border-bottom: 1px solid {MATERIAL_COLORS['outline_variant']};
            }}
        """)
        self.layout.addWidget(input_title)
        
        # Input area with styling
        self.input = QTextEdit()  # Changed to QTextEdit for multiline input
        self.input.setFixedHeight(150)  # Set height for approximately 8 lines
        self.input.setStyleSheet(f"""
            QTextEdit {{
                background-color: {MATERIAL_COLORS['surface']};
                color: {MATERIAL_COLORS['text_primary']};
                border: 1px solid {MATERIAL_COLORS['outline']};
                border-radius: 4px;
                padding: 6px;
                font-family: 'Consolas', monospace;
                font-size: 12px;
                margin: 8px;
            }}
            QTextEdit[readOnly="false"]::placeholder {{
                color: {MATERIAL_COLORS['text_secondary']};
            }}
        """)
        self.input.setPlaceholderText("Type your input here and press Enter to submit")
        self.input.textChanged.connect(self._handle_text_change)
        self.layout.addWidget(self.input)
        
        self.setLayout(self.layout)
        self.waiting_for_input = False
        self.setup_text_formats()

    def setup_text_formats(self):
        """Setup different text formats for console output"""
        self.formats = {
            'default': self._create_format(MATERIAL_COLORS['text_primary']),
            'success': self._create_format('#4CAF50'),  # Green
            'error': self._create_format('#FF5252'),    # Red
            'info': self._create_format('#2196F3'),     # Blue
            'warning': self._create_format('#FFC107'),  # Amber
            'input': self._create_format('#E040FB'),    # Purple
            'prompt': self._create_format('#FF4081'),   # Pink
        }

    def _create_format(self, color):
        fmt = QTextCharFormat()
        fmt.setForeground(QColor(color))
        return fmt

    def append_formatted(self, text, format_type='default'):
        """Append text with specified format"""
        cursor = self.output.textCursor()
        cursor.movePosition(QTextCursor.End)
        cursor.insertText(text, self.formats[format_type])
        self.output.setTextCursor(cursor)
        # Scroll to bottom
        scrollbar = self.output.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def displayOutput(self, text, format_type='default'):
        """Display output with formatting"""
        if not text:
            return
        self.append_formatted(text.rstrip() + '\n', format_type)

    def _handle_text_change(self):
        """Handle text changes in input area"""
        if '\n' in self.input.toPlainText():
            text = self.input.toPlainText().strip()
            if text:
                lines = text.split('\n')
                formatted_text = '\n'.join(f"> {line}" for line in lines if line.strip())
                self.input.clear()
                if self.waiting_for_input:
                    self.waiting_for_input = False
                    self.input.setPlaceholderText("")
                    self.append_formatted(formatted_text + '\n', 'input')
                    self.inputSubmitted.emit(text)
                else:
                    self.command_history.append(text)
                    self.history_index = len(self.command_history)
                    self.append_formatted(formatted_text + '\n', 'input')
                    self.inputSubmitted.emit(text)

    def requestInput(self):
        """Called when program is waiting for input"""
        self.waiting_for_input = True
        self.input.clear()  # Clear any existing text
        self.input.setPlaceholderText("Program is waiting for input... Press Enter to submit")
        self.inputRequested.emit()
        self.input.setFocus()

    def setInputEnabled(self, enabled):
        """Enable/disable input field safely"""
        try:
            if not self.isDestroyed():
                self.input.setEnabled(enabled)
                if enabled:
                    self.input.setFocus()
        except (RuntimeError, AttributeError):
            pass

    def isDestroyed(self):
        """Check if widget is destroyed"""
        try:
            return not self.isVisible()
        except RuntimeError:
            return True

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