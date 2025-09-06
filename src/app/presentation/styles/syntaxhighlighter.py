from PySide6.QtGui import QSyntaxHighlighter, QTextCharFormat, QBrush, QColor
from PySide6.QtCore import Qt, QRegularExpression
import re
from src.app.presentation.styles.components.syntax_highlighting import SYNTAX_HIGHLIGHTING_COLORS

# Use centralized color scheme
STYLES = SYNTAX_HIGHLIGHTING_COLORS

class CPPSyntaxHighlighter(QSyntaxHighlighter):
    def __init__(self, document):
        super().__init__(document)  # Add this line to call parent's __init__
        self.highlighting_rules = []

        # Standard library classes
        std_classes = QTextCharFormat()
        std_classes.setForeground(QBrush(QColor(STYLES['std_class'])))
        std_classes.setFontWeight(75)
        self.highlighting_rules.append((
            QRegularExpression("\\b(string|vector|map|set|queue|stack|list|deque|array|pair|tuple|unique_ptr|shared_ptr|weak_ptr)\\b"),
            std_classes
        ))

        # Namespaces
        namespace_format = QTextCharFormat()
        namespace_format.setForeground(QBrush(QColor(STYLES['namespace'])))
        self.highlighting_rules.append((QRegularExpression("\\b(std|boost)\\b::"), namespace_format))

        # Numbers (including floating point and hex)
        number_format = QTextCharFormat()
        number_format.setForeground(QBrush(QColor(STYLES['number'])))
        self.highlighting_rules.append((
            QRegularExpression("\\b[0-9]+\\.[0-9]+\\b|\\b0x[0-9A-Fa-f]+\\b|\\b[0-9]+\\b"),
            number_format
        ))

        # Function calls and declarations
        function_format = QTextCharFormat()
        function_format.setForeground(QBrush(QColor(STYLES['function'])))
        self.highlighting_rules.append((
            QRegularExpression("\\b[A-Za-z0-9_]+(?=\\s*\\()"),
            function_format
        ))

        # Class names
        class_format = QTextCharFormat()
        class_format.setForeground(QBrush(QColor(STYLES['class'])))
        class_format.setFontWeight(75)
        self.highlighting_rules.append((
            QRegularExpression("\\bclass\\s+[A-Za-z0-9_]+\\b"),
            class_format
        ))

        # Strings with escape handling
        string_format = QTextCharFormat()
        string_format.setForeground(QBrush(QColor(STYLES['string'])))
        self.highlighting_rules.append((
            QRegularExpression('"(?:[^"\\\\]|\\\\.)*"'),
            string_format
        ))
        
        # Character literals
        self.highlighting_rules.append((
            QRegularExpression("'(?:[^'\\\\]|\\\\.)*'"),
            string_format
        ))

        # Constants
        constant_format = QTextCharFormat()
        constant_format.setForeground(QBrush(QColor(STYLES['constant'])))
        self.highlighting_rules.append((
            QRegularExpression("\\b[A-Z_][A-Z0-9_]*\\b"),
            constant_format
        ))

        # Keywords
        keyword_format = QTextCharFormat()
        keyword_format.setForeground(QBrush(QColor(STYLES['keyword'])))
        keyword_format.setFontWeight(75)
        keywords = [
            'alignas', 'alignof', 'and', 'and_eq', 'asm', 'auto', 'bitand', 'bitor',
            'bool', 'break', 'case', 'catch', 'char', 'char16_t', 'char32_t', 'class',
            'compl', 'const', 'constexpr', 'const_cast', 'continue', 'decltype', 'default',
            'delete', 'do', 'double', 'dynamic_cast', 'else', 'enum', 'explicit', 'export',
            'extern', 'false', 'final', 'float', 'for', 'friend', 'goto', 'if', 'inline',
            'int', 'long', 'mutable', 'namespace', 'new', 'noexcept', 'not', 'not_eq',
            'nullptr', 'operator', 'or', 'or_eq', 'override', 'private', 'protected',
            'public', 'register', 'reinterpret_cast', 'return', 'short', 'signed',
            'sizeof', 'static', 'static_assert', 'static_cast', 'struct', 'switch',
            'template', 'this', 'thread_local', 'throw', 'true', 'try', 'typedef',
            'typeid', 'typename', 'union', 'unsigned', 'using', 'virtual', 'void',
            'volatile', 'wchar_t', 'while', 'xor', 'xor_eq'
        ]
        self.highlighting_rules.extend(
            (QRegularExpression(f"\\b{keyword}\\b"), keyword_format)
            for keyword in keywords
        )

        # Operators
        operator_format = QTextCharFormat()
        operator_format.setForeground(QBrush(QColor(STYLES['operator'])))
        operators = [
            '=', '==', '!=', '<', '<=', '>', '>=',
            '\\+', '-', '\\*', '/', '//', '\\%', '\\*\\*',
            '\\+=', '-=', '\\*=', '/=', '\\%=',
            '\\^', '\\|', '\\&', '\\~', '>>', '<<'
        ]
        
        # Add operators as a single pattern
        operator_pattern = '|'.join(map(re.escape, operators))
        self.highlighting_rules.append(
            (QRegularExpression(operator_pattern), operator_format)
        )

        # Add braces separately
        self.highlighting_rules.append(
            (QRegularExpression(r"[\{\}\(\)\[\]]"), operator_format)
        )

        # Preprocessor directives
        preprocessor_format = QTextCharFormat()
        preprocessor_format.setForeground(QBrush(QColor(STYLES['preprocessor'])))
        self.highlighting_rules.append((
            QRegularExpression("#[A-Za-z]+"),
            preprocessor_format
        ))

        # Comments
        self.comment_format = QTextCharFormat()
        self.comment_format.setForeground(QBrush(QColor(STYLES['comment'])))
        self.comment_format.setFontItalic(True)

        # Single-line comments
        self.highlighting_rules.append((
            QRegularExpression("//[^\n]*"),
            self.comment_format
        ))

        # Multi-line comments (as member variables for use in highlightBlock)
        self.comment_start = QRegularExpression("/\\*")
        self.comment_end = QRegularExpression("\\*/")

    def highlightBlock(self, text):
        # Apply regular expression rules
        for pattern, format in self.highlighting_rules:
            match_iterator = pattern.globalMatch(text)
            while match_iterator.hasNext():
                match = match_iterator.next()
                self.setFormat(match.capturedStart(), match.capturedLength(), format)

        # Handle multi-line comments
        self.setCurrentBlockState(0)
        start_index = 0
        if self.previousBlockState() != 1:
            match = self.comment_start.match(text, start_index)
            start_index = match.capturedStart() if match.hasMatch() else -1

        while start_index >= 0:
            match = self.comment_end.match(text, start_index)
            if not match.hasMatch():
                self.setCurrentBlockState(1)
                comment_length = len(text) - start_index
            else:
                comment_length = match.capturedEnd() - start_index

            self.setFormat(start_index, comment_length, self.comment_format)
            match = self.comment_start.match(text, start_index + comment_length)
            start_index = match.capturedStart() if match.hasMatch() else -1

class PythonSyntaxHighlighter(QSyntaxHighlighter):
    def __init__(self, document):
        super().__init__(document)
        self.highlighting_rules = []

        # Built-in functions and types
        builtin_format = QTextCharFormat()
        builtin_format.setForeground(QBrush(QColor(STYLES['std_class'])))
        builtin_format.setFontWeight(75)
        builtins = [
            'abs', 'all', 'any', 'bin', 'bool', 'bytes', 'chr', 'dict', 'dir',
            'float', 'format', 'hex', 'input', 'int', 'len', 'list', 'map',
            'max', 'min', 'object', 'ord', 'print', 'range', 'reversed', 'set',
            'slice', 'sorted', 'str', 'sum', 'super', 'tuple', 'type', 'zip'
        ]
        self.highlighting_rules.append((
            QRegularExpression('\\b(' + '|'.join(builtins) + ')\\b'),
            builtin_format
        ))

        # Function definitions
        function_format = QTextCharFormat()
        function_format.setForeground(QBrush(QColor(STYLES['function'])))
        self.highlighting_rules.append((
            QRegularExpression('\\bdef\\s+[A-Za-z0-9_]+(?=\\s*\\()'),
            function_format
        ))

        # Class definitions
        class_format = QTextCharFormat()
        class_format.setForeground(QBrush(QColor(STYLES['class'])))
        class_format.setFontWeight(75)
        self.highlighting_rules.append((
            QRegularExpression('\\bclass\\s+[A-Za-z0-9_]+\\b'),
            class_format
        ))

        # Strings (single, double, and triple quotes)
        string_format = QTextCharFormat()
        string_format.setForeground(QBrush(QColor(STYLES['string'])))
        string_patterns = [
            '""".*?"""', "'''.*?'''", '"[^"\\\\]*(\\\\.[^"\\\\]*)*"',
            "'[^'\\\\]*(\\\\.[^'\\\\]*)*'"
        ]
        for pattern in string_patterns:
            self.highlighting_rules.append((
                QRegularExpression(pattern), string_format
            ))

        # Keywords
        keyword_format = QTextCharFormat()
        keyword_format.setForeground(QBrush(QColor(STYLES['keyword'])))
        keywords = [
            'and', 'as', 'assert', 'break', 'class', 'continue', 'def',
            'del', 'elif', 'else', 'except', 'False', 'finally', 'for',
            'from', 'global', 'if', 'import', 'in', 'is', 'lambda', 'None',
            'nonlocal', 'not', 'or', 'pass', 'raise', 'return', 'True',
            'try', 'while', 'with', 'yield'
        ]
        self.highlighting_rules.extend(
            (QRegularExpression(f'\\b{keyword}\\b'), keyword_format)
            for keyword in keywords
        )

        # Numbers
        number_format = QTextCharFormat()
        number_format.setForeground(QBrush(QColor(STYLES['number'])))
        self.highlighting_rules.append((
            QRegularExpression('\\b[0-9]+\\.[0-9]+\\b|\\b[0-9]+\\b'),
            number_format
        ))

        # Comments
        comment_format = QTextCharFormat()
        comment_format.setForeground(QBrush(QColor(STYLES['comment'])))
        comment_format.setFontItalic(True)
        self.highlighting_rules.append((
            QRegularExpression('#[^\n]*'),
            comment_format
        ))

    def highlightBlock(self, text):
        for pattern, format in self.highlighting_rules:
            match_iterator = pattern.globalMatch(text)
            while match_iterator.hasNext():
                match = match_iterator.next()
                self.setFormat(match.capturedStart(), match.capturedLength(), format)

class JavaSyntaxHighlighter(QSyntaxHighlighter):
    def __init__(self, document):
        super().__init__(document)
        self.highlighting_rules = []

        # Class names and packages
        class_format = QTextCharFormat()
        class_format.setForeground(QBrush(QColor(STYLES['class'])))
        class_format.setFontWeight(75)
        self.highlighting_rules.append((
            QRegularExpression('\\b[A-Z][A-Za-z0-9_]*\\b'),
            class_format
        ))

        # Function definitions
        function_format = QTextCharFormat()
        function_format.setForeground(QBrush(QColor(STYLES['function'])))
        self.highlighting_rules.append((
            QRegularExpression('\\b[a-z][A-Za-z0-9_]*(?=\\s*\\()'),
            function_format
        ))

        # Strings
        string_format = QTextCharFormat()
        string_format.setForeground(QBrush(QColor(STYLES['string'])))
        self.highlighting_rules.append((
            QRegularExpression('"[^"\\\\]*(\\\\.[^"\\\\]*)*"'),
            string_format
        ))

        # Keywords
        keyword_format = QTextCharFormat()
        keyword_format.setForeground(QBrush(QColor(STYLES['keyword'])))
        keywords = [
            'abstract', 'assert', 'boolean', 'break', 'byte', 'case', 'catch',
            'char', 'class', 'const', 'continue', 'default', 'do', 'double',
            'else', 'enum', 'extends', 'final', 'finally', 'float', 'for',
            'if', 'implements', 'import', 'instanceof', 'int', 'interface',
            'long', 'native', 'new', 'package', 'private', 'protected',
            'public', 'return', 'short', 'static', 'strictfp', 'super',
            'switch', 'synchronized', 'this', 'throw', 'throws', 'transient',
            'try', 'void', 'volatile', 'while', 'true', 'false', 'null'
        ]
        self.highlighting_rules.extend(
            (QRegularExpression(f'\\b{keyword}\\b'), keyword_format)
            for keyword in keywords
        )

        # Numbers
        number_format = QTextCharFormat()
        number_format.setForeground(QBrush(QColor(STYLES['number'])))
        self.highlighting_rules.append((
            QRegularExpression('\\b[0-9]+\\.[0-9]+[fd]?\\b|\\b[0-9]+[lL]?\\b'),
            number_format
        ))

        # Comments
        self.comment_format = QTextCharFormat()
        self.comment_format.setForeground(QBrush(QColor(STYLES['comment'])))
        self.comment_format.setFontItalic(True)

        # Single-line comments
        self.highlighting_rules.append((
            QRegularExpression('//[^\n]*'),
            self.comment_format
        ))

        # Multi-line comments
        self.comment_start = QRegularExpression('/\\*')
        self.comment_end = QRegularExpression('\\*/')

    def highlightBlock(self, text):
        # Apply regular expression rules
        for pattern, format in self.highlighting_rules:
            match_iterator = pattern.globalMatch(text)
            while match_iterator.hasNext():
                match = match_iterator.next()
                self.setFormat(match.capturedStart(), match.capturedLength(), format)

        # Handle multi-line comments
        self.setCurrentBlockState(0)
        start_index = 0
        if self.previousBlockState() != 1:
            match = self.comment_start.match(text, start_index)
            start_index = match.capturedStart() if match.hasMatch() else -1

        while start_index >= 0:
            match = self.comment_end.match(text, start_index)
            if not match.hasMatch():
                self.setCurrentBlockState(1)
                comment_length = len(text) - start_index
            else:
                comment_length = match.capturedEnd() - start_index

            self.setFormat(start_index, comment_length, self.comment_format)
            match = self.comment_start.match(text, start_index + comment_length)
            start_index = match.capturedStart() if match.hasMatch() else -1
