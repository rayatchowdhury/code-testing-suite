from PySide6.QtWidgets import QWidget, QVBoxLayout, QTextEdit, QLineEdit, QScrollBar, QLabel, QPushButton
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
        
        # Console title
        console_title = QLabel("Console")
        console_title.setFixedHeight(36)  # Match tab height
        console_title.setAlignment(Qt.AlignCenter)
        console_title.setStyleSheet(f"""
            QLabel {{
                background: {MATERIAL_COLORS['surface_variant']};
                color: {MATERIAL_COLORS['text_primary']};
                font-weight: bold;
                font-family: 'Segoe UI';
                font-size: 16px;
                border-bottom: 1px solid {MATERIAL_COLORS['outline_variant']};
            }}
        """)
        self.layout.addWidget(console_title)
        
        # Output title with center alignment and different styling
        output_title = QLabel("Console Output")
        output_title.setAlignment(Qt.AlignCenter)
        output_title.setFixedHeight(26)  # Reduced from default
        output_title.setStyleSheet(f"""
            QLabel {{
                background: {MATERIAL_COLORS['surface_dim']};
                color: {MATERIAL_COLORS['text_primary']};
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
                border: 1px solid {MATERIAL_COLORS['outline']};
                border-radius: 4px;
                padding: 6px;
                font-family: 'Consolas', monospace;
                font-size: 12px;
                margin: 8px;
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
                font-family: 'Segoe UI';
                font-size: 12px;
                padding: 6px;
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
        
        # Compile & Run button with modern gradient and glow effect
        self.compile_run_btn = QPushButton("▶ Compile && Run")
        self.compile_run_btn.setObjectName("compile_run_btn")
        self.compile_run_btn.setFlat(True)
        self.compile_run_btn.setFixedHeight(40)
        self.compile_run_btn.setStyleSheet(f"""
            QPushButton#compile_run_btn {{
                background: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0,
                    stop:0 #1A4D2E,
                    stop:0.3 #2D6A4F,
                    stop:0.7 #2D6A4F,
                    stop:1 #1A4D2E
                );
                color: #E9F5DB;
                border: 1px solid #2D6A4F;
                border-radius: 6px;
                font-weight: bold;
                font-family: 'Segoe UI';
                font-size: 13px;
                margin: 8px;
                padding: 4px 16px;
            }}
            QPushButton#compile_run_btn:hover {{
                background: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0,
                    stop:0 #2D6A4F,
                    stop:0.3 #40916C,
                    stop:0.7 #40916C,
                    stop:1 #2D6A4F
                );
                border: 1px solid #40916C;
                color: white;
            }}
            QPushButton#compile_run_btn:pressed {{
                background: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0,
                    stop:0 #1A4D2E,
                    stop:0.3 #2D6A4F,
                    stop:0.7 #2D6A4F,
                    stop:1 #1A4D2E
                );
                border: 1px solid #1A4D2E;
                padding: 5px 17px 3px 15px;
            }}
            QPushButton#compile_run_btn:disabled {{
                background: #1A1A1A;
                border: 1px solid #2A2A2A;
                color: #666666;
            }}
        """)
        self.layout.addWidget(self.compile_run_btn)

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