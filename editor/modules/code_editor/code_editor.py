import os
from PyQt6.Qsci import QsciScintilla, QsciLexerJavaScript, QsciLexerHTML, QsciLexerCSS, QsciLexerPython
from PyQt6.QtGui import QFont, QColor
from PyQt6.QtCore import Qt

class CodeEditor(QsciScintilla):
    """Code editor widget with syntax highlighting."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # File path
        self.file_path = None
        
        # Set up the editor
        self.setup_editor()
        
    def setup_editor(self):
        """Set up the editor with default settings."""
        # Set the font
        font = QFont("Consolas", 10)
        self.setFont(font)
        self.setMarginsFont(font)
        
        # Set the margin for line numbers
        fontmetrics = self.fontMetrics()
        self.setMarginWidth(0, fontmetrics.horizontalAdvance("00000") + 5)
        self.setMarginLineNumbers(0, True)
        self.setMarginsBackgroundColor(QColor("#f0f0f0"))
        
        # Set brace matching
        self.setBraceMatching(QsciScintilla.BraceMatch.SloppyBraceMatch)
        
        # Set auto indentation
        self.setAutoIndent(True)
        self.setIndentationGuides(True)
        self.setIndentationsUseTabs(False)
        self.setIndentationWidth(4)
        
        # Set the caret
        self.setCaretWidth(2)
        self.setCaretForegroundColor(QColor("#000000"))
        self.setCaretLineVisible(True)
        self.setCaretLineBackgroundColor(QColor("#ffe4e4"))
        
        # Set selection color
        self.setSelectionBackgroundColor(QColor("#c0c0ff"))
        
        # Set the edge mode
        self.setEdgeMode(QsciScintilla.EdgeMode.EdgeLine)
        self.setEdgeColumn(80)
        self.setEdgeColor(QColor("#dddddd"))
        
        # Set the wrap mode
        self.setWrapMode(QsciScintilla.WrapMode.WrapWord)
        
        # Set the lexer based on the file extension
        self.set_lexer()
        
    def set_lexer(self):
        """Set the lexer based on the file extension."""
        if not self.file_path:
            # Default to JavaScript
            lexer = QsciLexerJavaScript(self)
            self.setLexer(lexer)
            return
            
        # Get the file extension
        _, ext = os.path.splitext(self.file_path)
        ext = ext.lower()
        
        # Set the lexer based on the extension
        if ext == '.js':
            lexer = QsciLexerJavaScript(self)
        elif ext == '.html' or ext == '.htm':
            lexer = QsciLexerHTML(self)
        elif ext == '.css':
            lexer = QsciLexerCSS(self)
        elif ext == '.py':
            lexer = QsciLexerPython(self)
        else:
            # Default to JavaScript
            lexer = QsciLexerJavaScript(self)
            
        # Set the lexer
        self.setLexer(lexer)
        
        # Set the lexer font
        lexer.setFont(QFont("Consolas", 10))
        
    def set_file_path(self, file_path):
        """Set the file path and update the lexer."""
        self.file_path = file_path
        self.set_lexer() 