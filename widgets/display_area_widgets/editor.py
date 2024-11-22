from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QPlainTextEdit, QTextEdit
from PySide6.QtGui import QFont, QColor, QPainter, QTextFormat, QTextCursor
from PySide6.QtCore import Qt, QRect, QSize
from widgets.display_area_widgets.syntaxhighlighter import CPPSyntaxHighlighter
from styles.style import MATERIAL_COLORS


class CodeEditor(QPlainTextEdit):
    def __init__(self):
        super().__init__()
        # Default values
        font_size = 12
        font_family = 'Consolas'
        tab_spaces = 4
        auto_indent = True
        bracket_matching = True

        self.setFont(QFont(font_family, font_size))
        self.tab_spaces = tab_spaces
        self.auto_indent = auto_indent
        self.bracket_matching = bracket_matching

        # Use material colors instead of hardcoded values
        self.setStyleSheet(f"""
            QPlainTextEdit {{
                background-color: {MATERIAL_COLORS['surface']};
                color: {MATERIAL_COLORS['text_primary']};
            }}
        """)

        # Add syntax highlighter
        self.highlighter = CPPSyntaxHighlighter(self.document())

        # Line number area setup
        self.lineNumberArea = LineNumberArea(self)
        self.document().blockCountChanged.connect(self.updateLineNumberAreaWidth)
        self.updateRequest.connect(self.updateLineNumberArea)
        self.cursorPositionChanged.connect(self.highlightCurrentLine)
        self.updateLineNumberAreaWidth(0)
        self.highlightCurrentLine()

        self.bracket_pairs = {
            '{': '}',
            '[': ']',
            '(': ')',
            '"': '"',
            "'": "'"
        }

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
            lineColor = QColor('#2d2d30')
            selection.format.setBackground(lineColor)
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
        painter.fillRect(event.rect(), QColor('#1e1e1e'))

        block = self.firstVisibleBlock()
        blockNumber = block.blockNumber()
        top = round(self.blockBoundingGeometry(block).translated(self.contentOffset()).top())
        bottom = top + round(self.blockBoundingRect(block).height())

        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                number = str(blockNumber + 1)
                painter.setPen(QColor('#858585'))
                painter.drawText(0, top, self.lineNumberArea.width() - 5,
                                 self.fontMetrics().height(), Qt.AlignRight, number)
            block = block.next()
            top = bottom
            bottom = top + round(self.blockBoundingRect(block).height())
            blockNumber += 1

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Return and self.auto_indent:
            # Handle new line with indentation
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

        if (self.bracket_matching and
                event.text() in self.bracket_pairs):
            # Handle bracket autocompletion
            cursor = self.textCursor()
            super().keyPressEvent(event)
            self.insertPlainText(self.bracket_pairs[event.text()])
            cursor.movePosition(QTextCursor.Left)
            self.setTextCursor(cursor)
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
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)  # Pass self directly to QVBoxLayout
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Create CodeEditor instance
        self.codeEditor = CodeEditor()
        self.loadDefaultFile()

        layout.addWidget(self.codeEditor)

    def loadDefaultFile(self):
        try:
            with open('src/temp.cpp', 'r') as file:
                code = file.read()
                self.codeEditor.setPlainText(code)
        except FileNotFoundError:
            pass  # If temp.cpp doesn't exist, do nothing

    def getCode(self):
        return self.codeEditor.toPlainText()
