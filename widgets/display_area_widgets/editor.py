from PySide6.QtWidgets import (QWidget, QVBoxLayout, QPlainTextEdit, 
                              QTextEdit, QFileDialog)
from PySide6.QtGui import QFont, QColor, QPainter, QTextFormat, QTextCursor, QKeySequence, QShortcut
from PySide6.QtCore import Qt, QRect, QSize, QTimer, Signal
from widgets.display_area_widgets.syntaxhighlighter import CPPSyntaxHighlighter, PythonSyntaxHighlighter, JavaSyntaxHighlighter
import os
from styles.constants.editor_colors import EDITOR_COLORS
from styles.components.editor import get_editor_style, EDITOR_WIDGET_STYLE
from utils.file_operations import FileOperations

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
        self._setup_ui()
        self._setup_file_handling()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        self.codeEditor = CodeEditor()
        layout.addWidget(self.codeEditor)

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
