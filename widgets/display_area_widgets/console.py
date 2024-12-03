from PySide6.QtWidgets import (QWidget, QVBoxLayout, QPlainTextEdit, QLabel, 
                              QPushButton, QScrollBar, QSizePolicy)
from PySide6.QtCore import Qt, Signal, QTimer
from PySide6.QtGui import QKeyEvent, QTextCharFormat, QColor, QTextCursor
from styles import CONSOLE_STYLE, MATERIAL_COLORS

class ConsoleOutput(QWidget):
    inputSubmitted = Signal(str)
    inputRequested = Signal()  # Add this signal

    def __init__(self):
        super().__init__()
        self.setObjectName("console_widget")
        self.setStyleSheet(CONSOLE_STYLE)  # Single style import includes container
        
        # Create a container with dark glassmorphism
        self.container = QWidget()
        self.container.setObjectName("console_container")
        
        container_layout = QVBoxLayout(self.container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        
        # Setup the console UI inside the container
        self.setObjectName("console_widget")
        
        # Initialize layout
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        
        # Create a container widget for content
        content_widget = QWidget()
        content_widget.setObjectName("console_content")
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)
        
        # Console title
        console_title = QLabel("CONSOLE")  # Changed to uppercase
        console_title.setObjectName("console_title")
        console_title.setFixedHeight(65)  # Increased from 36 to 64
        console_title.setAlignment(Qt.AlignCenter)  # Changed to center alignment
        
        # Output title with center alignment and different styling
        output_title = QLabel("Output")
        output_title.setObjectName("output_title")  # Add this line
        output_title.setAlignment(Qt.AlignCenter)
        output_title.setFixedHeight(26)  # Reduced from default
        
        # Output area with styling and buffer management
        self.output = QPlainTextEdit()
        self.output.setObjectName("console_output")  # Add this line
        self.output.setReadOnly(True)
        self.output.setMaximumBlockCount(1000)  # Limit the number of blocks
        self.output.document().setMaximumBlockCount(1000)  # Ensure both are set
        
        # Input title with center alignment and matching style
        input_title = QLabel("Input")
        input_title.setObjectName("input_title")  # Add this line
        input_title.setAlignment(Qt.AlignCenter)
        input_title.setFixedHeight(26)  # Reduced from default
        
        # Input area with styling
        self.input = QPlainTextEdit()  # Changed to QPlainTextEdit for multiline input
        self.input.setObjectName("console_input")  # Add this line
        self.input.setFixedHeight(150)  # Set height for approximately 8 lines
        self.input.setMaximumBlockCount(100)  # Limit input history
        self.input.setPlaceholderText("Type your input here and press Enter to submit")
        self.input.textChanged.connect(self._handle_text_change)
        
        # Compile & Run button with modern gradient and glow effect
        self.compile_run_btn = QPushButton()
        self.compile_run_btn.setObjectName("compile_run_btn")
        self.compile_run_btn.setText("Compile && Run ⚡")  # Set text explicitly
        self.compile_run_btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.compile_run_btn.setFixedHeight(40)
        self.compile_run_btn.setCursor(Qt.PointingHandCursor)  # Add hand cursor
        
        content_layout.addWidget(console_title)
        content_layout.addWidget(output_title)
        content_layout.addWidget(self.output)
        content_layout.addWidget(input_title)
        content_layout.addWidget(self.input)
        content_layout.addWidget(self.compile_run_btn)
        content_layout.addSpacing(5)
        
        # Add content widget to main layout
        self.layout.addWidget(content_widget)
        
        # Add console to container
        container_layout.addLayout(self.layout)
        
        # Set up main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(self.container)
        
        self.waiting_for_input = False
        self.command_history = []  # Add this line
        self.history_index = 0     # Add this line
        self.setup_text_formats()

        # Add text buffer and update timer
        self.text_buffer = []
        self.buffer_timer = QTimer()
        self.buffer_timer.timeout.connect(self.flush_buffer)
        self.buffer_timer.setInterval(10)  # Update every 100ms
        self.buffer_timer.start()

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
        """Buffer text for batch processing"""
        self.text_buffer.append((text, format_type))
        if not self.buffer_timer.isActive():
            self.buffer_timer.start()

    def flush_buffer(self):
        """Process buffered text in batches"""
        if not self.text_buffer:
            self.buffer_timer.stop()
            return

        # Process up to 10 items at a time
        batch = self.text_buffer[:10]
        self.text_buffer = self.text_buffer[10:]

        cursor = self.output.textCursor()
        cursor.movePosition(QTextCursor.End)  # Fixed: Use QTextCursor.End instead of cursor.End
        
        # Batch insert texts
        for text, format_type in batch:
            cursor.insertText(text, self.formats[format_type])

        self.output.setTextCursor(cursor)
        self.output.ensureCursorVisible()

        # Only scroll if we're near the bottom
        scrollbar = self.output.verticalScrollBar()
        if scrollbar.value() >= scrollbar.maximum() - 10:
            scrollbar.setValue(scrollbar.maximum())

    def displayOutput(self, text, format_type='default'):
        """Buffer output for display"""
        if not text:
            return
        self.append_formatted(text.rstrip() + '\n', format_type)

    def _handle_text_change(self):
        """Handle text changes in input area with improved performance"""
        text = self.input.toPlainText()
        if '\n' in text:
            text = text.strip()
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
                    if len(self.command_history) > 100:  # Limit command history
                        self.command_history.pop(0)
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

    def clear(self):
        """Clear both output and input areas"""
        self.output.clear()
        self.input.clear()
        self.text_buffer.clear()  # Clear any pending text in buffer

    def keyPressEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key_Up and self.command_history:
            self.history_index = max(0, self.history_index - 1)
            self.input.setText(self.command_history[self.history_index])
        elif event.key() == Qt.Key_Down and self.command_history:
            self.history_index