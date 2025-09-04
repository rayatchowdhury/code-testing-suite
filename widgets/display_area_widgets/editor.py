from PySide6.QtWidgets import (QWidget, QVBoxLayout, QPlainTextEdit, QLineEdit,
                              QTextEdit, QFileDialog, QHBoxLayout, QPushButton,
                              QMessageBox, QDialog, QScrollArea, QLabel, QFrame)
from PySide6.QtGui import (QFont, QColor, QPainter, QTextFormat, QTextCursor, 
                          QKeySequence, QShortcut)
from PySide6.QtCore import Qt, QRect, QSize, QTimer, Signal, QObject
import os
import asyncio
import qasync
from qasync import asyncSlot, QEventLoop

from styles.constants.editor_colors import EDITOR_COLORS
from styles.constants.colors import MATERIAL_COLORS
from styles.components.editor import (EDITOR_WIDGET_STYLE, get_editor_style,
                                    AI_DIALOG_STYLE)
from styles.components.ai_panel import AI_PANEL_STYLE
from utils.file_operations import FileOperations

# Lazy imports for heavy components
_markdown = None
_pygments_highlight = None
_pygments_formatter = None
_pygments_lexer = None
_syntax_highlighters = None
_editor_ai = None
_ai_panel = None

def _import_markdown():
    global _markdown
    if _markdown is None:
        from markdown import markdown
        _markdown = markdown
    return _markdown

def _import_pygments():
    global _pygments_highlight, _pygments_formatter, _pygments_lexer
    if _pygments_highlight is None:
        from pygments import highlight
        from pygments.formatters import HtmlFormatter
        from pygments.lexers import get_lexer_by_name
        _pygments_highlight = highlight
        _pygments_formatter = HtmlFormatter
        _pygments_lexer = get_lexer_by_name
    return _pygments_highlight, _pygments_formatter, _pygments_lexer

def _import_syntax_highlighters():
    global _syntax_highlighters
    if _syntax_highlighters is None:
        from .syntaxhighlighter import (CPPSyntaxHighlighter, PythonSyntaxHighlighter, 
                                       JavaSyntaxHighlighter)
        _syntax_highlighters = {
            'cpp': CPPSyntaxHighlighter,
            'python': PythonSyntaxHighlighter,
            'java': JavaSyntaxHighlighter
        }
    return _syntax_highlighters

def _import_editor_ai():
    global _editor_ai
    if _editor_ai is None:
        from ai.core.editor_ai import EditorAI
        _editor_ai = EditorAI
    return _editor_ai

def _import_ai_panel():
    global _ai_panel
    if _ai_panel is None:
        from .ai_panel import AIPanel
        _ai_panel = AIPanel
    return _ai_panel

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

        # Lazy load syntax highlighters
        highlighters = _import_syntax_highlighters()
        highlighter_map = {
            'cpp': highlighters['cpp'],
            'h': highlighters['cpp'],
            'hpp': highlighters['cpp'],
            'py': highlighters['python'],
            'java': highlighters['java']
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
            self.lineNumberArea.update(0, rect.y(), self.lineNumberArea.width(), rect.height())
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
        self.editor_ai = None  # Lazy load when needed
        self._setup_ui()
        self._setup_file_handling()
        
        # Remove _connect_ai_buttons() call from here

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Add editor first
        self.codeEditor = CodeEditor()
        layout.addWidget(self.codeEditor)

        # Create and add AI panel with connections to editor functions (lazy load)
        self.ai_panel = None
        self._ai_panel_initialized = False

        # Map AI actions to methods
        self.ai_actions = {
            'analysis': ('Code Explanation', self._process_explanation),
            'issues': ('Potential Issues', self._process_explanation),
            'tips': ('Improvement Tips', self._process_explanation),
            'document': ('Documentation', self._process_code),
            'generate': ('Generated Code', self._process_code),
            'custom': ('Custom Command', self._process_code)
        }

        self.codeEditor.document().modificationChanged.connect(self._handle_modification_changed)

    def _init_ai_panel(self):
        """Initialize AI panel when first needed"""
        if not self._ai_panel_initialized:
            ai_panel_class = _import_ai_panel()
            self.ai_panel = ai_panel_class(panel_type="editor", parent=self)
            self.ai_panel.analysisRequested.connect(self._analysis_code)
            self.ai_panel.issuesRequested.connect(self._find_issues)
            self.ai_panel.tipsRequested.connect(self._get_tips)
            self.ai_panel.documentRequested.connect(self._document_code)
            self.ai_panel.generateRequested.connect(self._generate_code)
            self.ai_panel.customCommandRequested.connect(self._handle_custom_command)
            self.layout().addWidget(self.ai_panel)
            self._ai_panel_initialized = True
            # Force layout update
            self.update()

    def _get_editor_ai(self):
        """Get EditorAI instance, creating if necessary"""
        if self.editor_ai is None:
            editor_ai_class = _import_editor_ai()
            self.editor_ai = editor_ai_class()
        return self.editor_ai

    def get_ai_panel(self):
        """Get AI panel, initializing if necessary"""
        if not self._ai_panel_initialized:
            self._init_ai_panel()
        return self.ai_panel

    def _get_editor_ai(self):
        """Get EditorAI instance, creating it if needed"""
        if self.editor_ai is None:
            editor_ai_class = _import_editor_ai()
            self.editor_ai = editor_ai_class()
        return self.editor_ai

    def _handle_modification_changed(self, modified):
        if not modified:  # Document returned to unmodified state
            self.filePathChanged.emit()

    def _handle_custom_command(self, command: str, code: str = None):
        """Handle custom AI command"""
        if code is None:
            code = self.getCode()
        asyncio.create_task(
            self._process_code('custom', code, command=command)
        )

    def _clean_code_response(self, text: str) -> str:
        """Strip everything but the actual code."""
        # First, clean any markdown artifacts
        markdown_patterns = [
            '```python', '```cpp', '```java', '```c', '```',
            '```c++', '```javascript', '```txt',
            '---', '===', '###'
        ]
        
        cleaned = text.strip()
        for pattern in markdown_patterns:
            cleaned = cleaned.replace(pattern, '')
        
        # Clean up whitespace and empty lines
        cleaned = '\n'.join(line.rstrip() for line in cleaned.splitlines())
        while '\n\n\n' in cleaned:
            cleaned = cleaned.replace('\n\n\n', '\n\n')
            
        return cleaned.strip()

    def _apply_changes(self, text: str, dialog: QDialog):
        """Apply code changes with undo support."""
        cleaned_code = self._clean_code_response(text)
        
        # Verify we have actual code
        if not cleaned_code or cleaned_code.isspace():
            return
        
        # Create a cursor and preserve selection/position
        cursor = self.codeEditor.textCursor()
        position = cursor.position()
        
        # Begin editing block for undo
        cursor.beginEditBlock()
        cursor.select(QTextCursor.Document)
        cursor.insertText(cleaned_code)
        cursor.endEditBlock()
        
        # Restore cursor position if possible
        if position < len(cleaned_code):
            cursor.setPosition(position)
        self.codeEditor.setTextCursor(cursor)
        
        # Setup syntax highlighting
        self.codeEditor._setup_syntax_highlighting(self.currentFilePath)
        
        # Automatically save the file
        self.saveFile()
        
        dialog.accept()

    def _format_ai_response(self, response: str, title: str) -> str:
        """Format AI response with proper styling."""
        # Only wrap code responses in code blocks for display
        if title in ["Documentation", "Generated Code", "Custom Command"]:
            file_type = self.currentFilePath.split('.')[-1] if self.currentFilePath else 'cpp'
            return f"```{file_type}\n{self._clean_code_response(response)}\n```"
        return response

    def _show_ai_response(self, response: str, title: str):
        """Show AI response with enhanced styling."""
        dialog = QDialog(self)
        dialog.setWindowTitle(f"AI Assistant - {title}")
        dialog.setMinimumSize(900, 650)
        dialog.setStyleSheet(AI_DIALOG_STYLE)

        # Main layout with zero margins for full-bleed design
        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Scroll area setup
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.NoFrame)

        # Content widget with proper margins
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)

        # Format content and add to layout
        formatted_response = self._format_ai_response(response, title)
        
        # Lazy load markdown and pygments
        markdown_func = _import_markdown()
        highlight, formatter_class, lexer = _import_pygments()
        
        html_content = markdown_func(
            formatted_response,
            extensions=['fenced_code', 'codehilite', 'tables']
        )
        
        # Add syntax highlighting CSS
        formatter = formatter_class(style='monokai')
        css = formatter.get_style_defs('.codehilite')
        html_content = f"<style>{css}</style>{html_content}"

        # Create and setup content label
        content_label = QLabel(html_content)
        content_label.setTextFormat(Qt.RichText)
        content_label.setTextInteractionFlags(
            Qt.TextSelectableByMouse | 
            Qt.TextSelectableByKeyboard
        )
        content_layout.addWidget(content_label)

        # Set content in scroll area
        scroll_area.setWidget(content_widget)
        layout.addWidget(scroll_area)

        # Button container with styling
        button_container = QWidget()
        button_container.setObjectName("button_container")
        button_layout = QHBoxLayout(button_container)
        button_layout.setContentsMargins(20, 15, 20, 15)
        button_layout.addStretch()

        # Add buttons
        ok_button = QPushButton("Close")
        ok_button.setObjectName("cancel_button")
        ok_button.clicked.connect(dialog.accept)
        button_layout.addWidget(ok_button)

        # Add apply button for code-returning functions
        if title in ["Documentation", "Generated Code", "Custom Command"]:
            apply_button = QPushButton("Apply Changes")
            apply_button.setObjectName("apply_button")
            apply_button.setDefault(True)
            apply_button.clicked.connect(
                lambda: self._apply_changes(response, dialog)
            )
            button_layout.addWidget(apply_button)

        layout.addWidget(button_container)
        
        dialog.exec()

    def _process_ai_request(self, action, title):
        """Process AI request with loading state"""
        self.ai_panel.set_enabled(False)  # Use ai_panel's method instead of direct button access
        
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
                self.ai_panel.set_enabled(True)  # Re-enable through ai_panel

        task = asyncio.create_task(process_request())
        return task

    async def _process_explanation(self, action: str, code: str = None):
        """Handle explanation-type AI requests."""
        if code is None:
            code = self.getCode()
        editor_ai = self._get_editor_ai()
        await self._process_ai_request(
            lambda c: editor_ai.process_explanation(action, c),
            self.ai_actions[action][0]
        )

    async def _process_code(self, action: str, code: str = None, **kwargs):
        """Handle code-modification AI requests."""
        if code is None:
            code = self.getCode()
        editor_ai = self._get_editor_ai()
        await self._process_ai_request(
            lambda c: editor_ai.process_code(action, c, **kwargs),
            self.ai_actions[action][0]
        )

    # Simplified action methods
    @asyncSlot()
    async def _analysis_code(self, code=None):
        self._init_ai_panel()  # Ensure AI panel is initialized
        await self._process_explanation('analysis', code)

    @asyncSlot()
    async def _find_issues(self, code=None):
        self._init_ai_panel()  # Ensure AI panel is initialized
        await self._process_explanation('issues', code)

    @asyncSlot()
    async def _get_tips(self, code=None):
        self._init_ai_panel()  # Ensure AI panel is initialized
        await self._process_explanation('tips', code)

    @asyncSlot()
    async def _document_code(self, code=None):
        self._init_ai_panel()  # Ensure AI panel is initialized
        await self._process_code('document', code)

    @asyncSlot()
    async def _generate_code(self, code=None):
        self._init_ai_panel()  # Ensure AI panel is initialized
        await self._process_code('generate', code, 
                               type=self.currentFilePath or "generator.cpp")

    def _setup_file_handling(self):
        self.currentFilePath = None
        self.setupShortcuts()
        QShortcut(QKeySequence("Ctrl+I"), self).activated.connect(self._openFilePicker)

    def setupShortcuts(self):
        # Bind shortcuts to saveFile/saveFileAs directly
        QShortcut(QKeySequence.Save, self).activated.connect(self.saveFile)
        QShortcut(QKeySequence.SaveAs, self).activated.connect(self.saveFileAs)

    def _handle_file_button(self, button_name):
        # Update active button state
        if self.current_button:
            self.current_button.setProperty("isActive", False)
            self.current_button.style().unpolish(self.current_button)
            self.current_button.style().polish(self.current_button)
        
        clicked_button = self.file_buttons[button_name]
        clicked_button.setProperty("isActive", True)
        clicked_button.style().unpolish(clicked_button)
        clicked_button.style().polish(clicked_button)
        self.current_button = clicked_button

        file_map = {
            'Generator': 'generator.cpp',
            'Correct Code': 'correct.cpp',
            'Test Code': 'test.cpp'
        }
        
        file_path = os.path.join(self.workspace_dir, file_map[button_name])
        
        # Create file if it doesn't exist
        if not os.path.exists(file_path):
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write('// Add your code here\n')
        
        # Load file content
        content = FileOperations.load_file(file_path, self)
        if content is not None:
            self.editor.currentFilePath = file_path
            self.editor.codeEditor.setPlainText(content)
            self.editor.codeEditor._setup_syntax_highlighting(file_path)

    def _openFilePicker(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Insert File Content", "", "All Files (*)")
        if file_path:
            content = FileOperations.load_file(file_path, self)
            if content is not None:
                # Overwrite current file's content without changing currentFilePath
                self.codeEditor.setPlainText(content)

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
            self.codeEditor.document().setModified(False)  # This will trigger modificationChanged
            self.codeEditor._setup_syntax_highlighting(path)
            return True
        return False

    def getCode(self):
        return self.codeEditor.toPlainText()