from PySide6.QtWidgets import (QWidget, QVBoxLayout, QPlainTextEdit, QLineEdit,
                              QTextEdit, QFileDialog, QHBoxLayout, QPushButton,
                              QMessageBox, QDialog, QScrollArea, QLabel, QFrame)
from PySide6.QtGui import QFont, QColor, QPainter, QTextFormat, QTextCursor, QKeySequence, QShortcut
from PySide6.QtCore import Qt, QRect, QSize, QTimer, Signal, QObject
from widgets.display_area_widgets.syntaxhighlighter import CPPSyntaxHighlighter, PythonSyntaxHighlighter, JavaSyntaxHighlighter
import os
from styles.constants.editor_colors import EDITOR_COLORS
from styles.components.editor import get_editor_style, EDITOR_WIDGET_STYLE, AI_PANEL_STYLE, AI_DIALOG_STYLE
from utils.file_operations import FileOperations
from tools.editor_ai import EditorAI
import asyncio
import qasync
from qasync import asyncSlot, QEventLoop

class CodeEditor(QPlainTextEdit):
    def __init__(self):
        super().__init__()
        self._setup_editor()
        self._setup_line_numbers()
        self.current_highlighter = None

    def _setup_editor(self):
        # Default values
        self.setFont(QFont('Consolas', 12))
        self.tab_spaces = 4
        self.auto_indent = True
        self.bracket_matching = True
        self.setStyleSheet(get_editor_style())
        
        self.bracket_pairs = {'{': '}', '[': ']', '(': ')', '"': '"', "'": "'"}

    def _setup_line_numbers(self):
        self.lineNumberArea = LineNumberArea(self)
        self.document().blockCountChanged.connect(self.updateLineNumberAreaWidth)
        self.updateRequest.connect(self.updateLineNumberArea)
        self.cursorPositionChanged.connect(self.highlightCurrentLine)
        self.updateLineNumberAreaWidth(0)
        self.highlightCurrentLine()

    def _setup_syntax_highlighting(self, file_path=None):
        """Setup syntax highlighting based on file extension"""
        if self.current_highlighter:
            self.current_highlighter.setDocument(None)
            self.current_highlighter = None
            
        if not file_path:
            return

        highlighter_map = {
            'cpp': CPPSyntaxHighlighter,
            'h': CPPSyntaxHighlighter,
            'hpp': CPPSyntaxHighlighter,
            'py': PythonSyntaxHighlighter,
            'java': JavaSyntaxHighlighter
        }
        
        ext = file_path.lower().split('.')[-1]
        if ext in highlighter_map:
            self.current_highlighter = highlighter_map[ext](self.document())

    def lineNumberAreaWidth(self):
        digits = len(str(max(1, self.blockCount())))
        space = 10 + self.fontMetrics().horizontalAdvance('9') * digits
        return space

    def updateLineNumberAreaWidth(self, _):
        self.setViewportMargins(self.lineNumberAreaWidth(), 0, 0, 0)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        cr = self.contentsRect()
        self.lineNumberArea.setGeometry(
            QRect(cr.left(), cr.top(), self.lineNumberAreaWidth(), cr.height()))

    def highlightCurrentLine(self):
        extraSelections = []
        if not self.isReadOnly():
            selection = QTextEdit.ExtraSelection()
            selection.format.setBackground(QColor(EDITOR_COLORS['current_line']))
            selection.format.setProperty(QTextFormat.FullWidthSelection, True)
            selection.cursor = self.textCursor()
            selection.cursor.clearSelection()
            extraSelections.append(selection)
        self.setExtraSelections(extraSelections)

    def updateLineNumberArea(self, rect, dy):
        if dy:
            self.lineNumberArea.scroll(0, dy)
        else:
            self.lineNumberArea.update(
                0, rect.y(), self.lineNumberArea.width(), rect.height())
        if rect.contains(self.viewport().rect()):
            self.updateLineNumberAreaWidth(0)

    def lineNumberAreaPaintEvent(self, event):
        painter = QPainter(self.lineNumberArea)
        painter.fillRect(event.rect(), QColor(EDITOR_COLORS['background_darker']))

        block = self.firstVisibleBlock()
        blockNumber = block.blockNumber()
        top = round(self.blockBoundingGeometry(
            block).translated(self.contentOffset()).top())
        bottom = top + round(self.blockBoundingRect(block).height())

        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                number = str(blockNumber + 1)
                painter.setPen(QColor(EDITOR_COLORS['line_number']))
                painter.drawText(0, top, self.lineNumberArea.width() - 5,
                                 self.fontMetrics().height(), Qt.AlignRight, number)
            block = block.next()
            top = bottom
            bottom = top + round(self.blockBoundingRect(block).height())
            blockNumber += 1

    def keyPressEvent(self, event):
        # Special handling for curly braces with multi-line formatting
        if self.bracket_matching and event.text() == '{':
            cursor = self.textCursor()
            pos = cursor.positionInBlock()
            current_line = cursor.block().text()
            indent = self.get_line_indentation(current_line)
            
            # Insert opening brace
            super().keyPressEvent(event)
            
            # Create formatted structure
            cursor = self.textCursor()
            cursor.insertText('\n' + indent + ' ' * self.tab_spaces)  # Middle line
            middle_line_position = cursor.position()
            cursor.insertText('\n' + indent + '}')  # Closing brace
            
            # Move cursor to middle line
            cursor.setPosition(middle_line_position)
            self.setTextCursor(cursor)
            return
            
        if (self.bracket_matching and
                event.text() in ['[', '(', '"', "'"]):
            # Regular single-line bracket handling for other types
            cursor = self.textCursor()
            super().keyPressEvent(event)
            self.insertPlainText(self.bracket_pairs[event.text()])
            cursor.movePosition(QTextCursor.Left)
            self.setTextCursor(cursor)
            return

        # Handle new line with indentation
        if event.key() == Qt.Key_Return and self.auto_indent:
            cursor = self.textCursor()
            current_line = cursor.block().text()
            indent = self.get_line_indentation(current_line)
            super().keyPressEvent(event)
            self.insertPlainText(indent)
            return

        if (event.key() == Qt.Key_Tab and
                not event.modifiers() & Qt.ShiftModifier):
            # Insert spaces instead of tab
            self.insertPlainText(" " * self.tab_spaces)
            return

        # Handle backspace with tab awareness
        if event.key() == Qt.Key_Backspace:
            cursor = self.textCursor()
            if not cursor.hasSelection():
                pos = cursor.positionInBlock()
                current_line = cursor.block().text()
                if pos > 0 and all(current_line[pos-i-1] == ' ' for i in range(min(self.tab_spaces, pos))):
                    # If previous characters are spaces, delete up to tab width
                    for _ in range(min(self.tab_spaces, pos)):
                        cursor.deletePreviousChar()
                    return

        super().keyPressEvent(event)

    def get_line_indentation(self, line):
        """Return the indentation string of the given line"""
        indent = ""
        for char in line:
            if char in [' ', '\t']:
                indent += char
            else:
                break
        return indent


class LineNumberArea(QWidget):
    def __init__(self, editor):
        super().__init__(editor)
        self.codeEditor = editor

    def sizeHint(self):
        return QSize(self.codeEditor.lineNumberAreaWidth(), 0)

    def paintEvent(self, event):
        self.codeEditor.lineNumberAreaPaintEvent(event)


class EditorWidget(QWidget):
    filePathChanged = Signal()

    def __init__(self):
        super().__init__()
        self.setObjectName("editor_widget")
        self.setStyleSheet(EDITOR_WIDGET_STYLE)
        self.editor_ai = EditorAI()
        self._setup_ui()
        self._setup_file_handling()
        self._connect_ai_buttons()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Add editor first
        self.codeEditor = CodeEditor()
        layout.addWidget(self.codeEditor)

        # Add AI panel container below editor
        self.ai_panel_container = QWidget()
        self.ai_panel_container.setObjectName("ai_panel_container")
        self.ai_panel_container.setStyleSheet(AI_PANEL_STYLE)
        
        ai_panel = QHBoxLayout(self.ai_panel_container)
        ai_panel.setContentsMargins(5, 5, 5, 5)
        ai_panel.setSpacing(5)

        # Add normal AI buttons on the left
        button_container = QWidget()
        button_layout = QHBoxLayout(button_container)
        button_layout.setContentsMargins(0, 0, 0, 0)
        button_layout.setSpacing(5)
        
        ai_buttons = ['Explain', 'Fix', 'Optimize', 'Document']
        self.ai_buttons = {}
        for btn_text in ai_buttons:
            btn = QPushButton(btn_text)
            btn.setObjectName("ai_button")
            btn.setFixedHeight(30)
            self.ai_buttons[btn_text] = btn
            button_layout.addWidget(btn)
        
        ai_panel.addWidget(button_container)

        # Add custom command input that takes remaining space
        self.command_input = QLineEdit()
        self.command_input.setObjectName("ai_command_input")
        self.command_input.setPlaceholderText("Type custom AI command and press Enter")
        self.command_input.returnPressed.connect(self._handle_custom_command)
        self.command_input.setMinimumWidth(170)
        ai_panel.addWidget(self.command_input, 1)  # 1 is the stretch factor

        layout.addWidget(self.ai_panel_container)

    def _handle_custom_command(self):
        """Handle custom AI command"""
        command = self.command_input.text().strip()
        if command:
            self._process_ai_request(
                lambda code: self.editor_ai.custom_command(command, code),
                "Custom Command"
            )
            self.command_input.clear()

    def _connect_ai_buttons(self):
        """Connect AI buttons to their respective actions"""
        self.ai_buttons['Explain'].clicked.connect(self._explain_code)
        self.ai_buttons['Fix'].clicked.connect(self._fix_code)
        self.ai_buttons['Optimize'].clicked.connect(self._optimize_code)
        self.ai_buttons['Document'].clicked.connect(self._document_code)

    def _show_ai_response(self, response: str, title: str):
        """Show AI response in a custom dialog with scrollable content"""
        dialog = QDialog(self)
        dialog.setWindowTitle(title)
        dialog.setMinimumSize(800, 600)  # Larger default size
        dialog.setStyleSheet(AI_DIALOG_STYLE)

        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Create scroll area with custom styling
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.NoFrame)  # Remove frame border

        # Create content widget with proper styling
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(0, 0, 0, 0)

        # Create label with styled text
        content_label = QLabel(response)
        content_label.setWordWrap(True)
        content_label.setTextInteractionFlags(
            Qt.TextSelectableByMouse | 
            Qt.TextSelectableByKeyboard
        )
        content_label.setFont(QFont('Segoe UI', 12))
        content_layout.addWidget(content_label)

        scroll_area.setWidget(content_widget)
        layout.addWidget(scroll_area)

        # Create button container
        button_container = QWidget()
        button_layout = QHBoxLayout(button_container)
        button_layout.setContentsMargins(0, 0, 0, 0)
        button_layout.setSpacing(10)
        button_layout.addStretch()  # Push buttons to the right

        # Add buttons
        ok_button = QPushButton("OK")
        ok_button.setDefault(True)
        ok_button.clicked.connect(dialog.accept)
        button_layout.addWidget(ok_button)

        if title in ["Documentation", "Custom Command"]:
            apply_button = QPushButton("Apply Changes")
            apply_button.clicked.connect(lambda: self._apply_changes(response))
            button_layout.addWidget(apply_button)

        layout.addWidget(button_container)
        
        dialog.exec()

    def _apply_changes(self, text):
        """Apply changes without closing dialog"""
        self.codeEditor.setPlainText(text)

    def _process_ai_request(self, action, title):
        """Process AI request with loading state"""
        for btn in self.ai_buttons.values():
            btn.setEnabled(False)
        
        async def process_request():
            try:
                code = self.getCode()
                response = await action(code)
                if not response:
                    response = "AI service not available. Please check your API key configuration."
                self._show_ai_response(response, title)
            except Exception as e:
                self._show_ai_response(f"Error: {str(e)}", "Error")
            finally:
                for btn in self.ai_buttons.values():
                    btn.setEnabled(True)

        task = asyncio.create_task(process_request())
        return task

    @asyncSlot()
    async def _explain_code(self):
        if not self.editor_ai.model:
            self._show_ai_response("AI service not available. Please check your API key configuration.", "Error")
            return
        await self._process_ai_request(self.editor_ai.explain_code, "Code Explanation")

    @asyncSlot()
    async def _fix_code(self):
        await self._process_ai_request(self.editor_ai.fix_code, "Code Fixes")

    @asyncSlot()
    async def _optimize_code(self):
        await self._process_ai_request(self.editor_ai.optimize_code, "Code Optimizations")

    @asyncSlot()
    async def _document_code(self):
        await self._process_ai_request(self.editor_ai.document_code, "Documentation")

    def _setup_file_handling(self):
        self.currentFilePath = None
        self.setupShortcuts()

    def setupShortcuts(self):
        # Bind shortcuts to saveFile/saveFileAs directly
        QShortcut(QKeySequence.Save, self).activated.connect(self.saveFile)
        QShortcut(QKeySequence.SaveAs, self).activated.connect(self.saveFileAs)

    def saveFile(self):
        """Save to current path or prompt for new path if none exists"""
        if not self.currentFilePath:
            return self.saveFileAs()
        return self._save_to_path(self.currentFilePath)

    def saveFileAs(self):
        """Always prompt for new save location"""
        new_path = FileOperations.save_file_as(self, self.getCode(), self.currentFilePath)
        if new_path:
            self.currentFilePath = new_path
            self.filePathChanged.emit()
            return self._save_to_path(new_path)
        return False

    def _save_to_path(self, path):
        """Internal method to save file and update editor state"""
        if FileOperations.save_file(path, self.getCode(), self):
            self.codeEditor.document().setModified(False)
            self.codeEditor._setup_syntax_highlighting(path)
            return True
        return False

    def getCode(self):
        return self.codeEditor.toPlainText()
