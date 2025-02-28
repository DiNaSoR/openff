from PyQt6.QtCore import Qt, QRegularExpression
from PyQt6.QtGui import QSyntaxHighlighter, QTextCharFormat, QFont, QColor

class JavaScriptHighlighter(QSyntaxHighlighter):
    """Syntax highlighter for JavaScript code."""
    
    def __init__(self, parent=None, game_specific=True):
        super().__init__(parent)
        
        self.highlighting_rules = []
        
        # Define formats for different syntax elements
        keyword_format = QTextCharFormat()
        keyword_format.setForeground(QColor("#569CD6"))
        keyword_format.setFontWeight(QFont.Weight.Bold)
        
        keywords = [
            "break", "case", "catch", "class", "const", "continue", "debugger",
            "default", "delete", "do", "else", "export", "extends", "false",
            "finally", "for", "function", "if", "import", "in", "instanceof",
            "new", "null", "return", "super", "switch", "this", "throw", "true",
            "try", "typeof", "var", "void", "while", "with", "let", "yield"
        ]
        
        # Add keyword patterns
        for word in keywords:
            pattern = QRegularExpression(r'\b' + word + r'\b')
            self.highlighting_rules.append((pattern, keyword_format))
            
        # Number format
        number_format = QTextCharFormat()
        number_format.setForeground(QColor("#B5CEA8"))
        pattern = QRegularExpression(r'\b[0-9]+\b')
        self.highlighting_rules.append((pattern, number_format))
        
        # String format
        string_format = QTextCharFormat()
        string_format.setForeground(QColor("#CE9178"))
        pattern = QRegularExpression(r'"[^"]*"|\'[^\']*\'')
        self.highlighting_rules.append((pattern, string_format))
        
        # Comment format
        comment_format = QTextCharFormat()
        comment_format.setForeground(QColor("#6A9955"))
        pattern = QRegularExpression(r'//[^\n]*')
        self.highlighting_rules.append((pattern, comment_format))
        
        # Multi-line comment format
        self.multi_line_comment_format = QTextCharFormat()
        self.multi_line_comment_format.setForeground(QColor("#6A9955"))
        
        self.comment_start_expression = QRegularExpression(r'/\*')
        self.comment_end_expression = QRegularExpression(r'\*/')
        
        # Function format
        function_format = QTextCharFormat()
        function_format.setForeground(QColor("#DCDCAA"))
        pattern = QRegularExpression(r'\b[A-Za-z0-9_]+(?=\s*\()')
        self.highlighting_rules.append((pattern, function_format))
        
        # Game-specific highlighting
        if game_specific:
            game_keyword_format = QTextCharFormat()
            game_keyword_format.setForeground(QColor("#C586C0"))
            game_keyword_format.setFontWeight(QFont.Weight.Bold)
            
            game_keywords = [
                "character", "item", "map", "battle", "spell", "enemy",
                "player", "game", "inventory", "equipment", "stats", "level",
                "hp", "mp", "attack", "defense", "magic", "speed"
            ]
            
            for word in game_keywords:
                pattern = QRegularExpression(r'\b' + word + r'\b')
                self.highlighting_rules.append((pattern, game_keyword_format))
        
    def highlightBlock(self, text):
        """Apply syntax highlighting to the given block of text."""
        # Apply regular expression highlighting rules
        for pattern, format in self.highlighting_rules:
            match_iterator = pattern.globalMatch(text)
            while match_iterator.hasNext():
                match = match_iterator.next()
                self.setFormat(match.capturedStart(), match.capturedLength(), format)
                
        # Handle multi-line comments
        self.setCurrentBlockState(0)
        
        start_index = 0
        if self.previousBlockState() != 1:
            start_index = text.indexOf(self.comment_start_expression)
            
        while start_index >= 0:
            match = self.comment_end_expression.match(text, start_index)
            end_index = match.capturedStart()
            comment_length = 0
            
            if end_index == -1:
                self.setCurrentBlockState(1)
                comment_length = len(text) - start_index
            else:
                comment_length = end_index - start_index + match.capturedLength()
                
            self.setFormat(start_index, comment_length, self.multi_line_comment_format)
            start_index = text.indexOf(self.comment_start_expression, start_index + comment_length)

class CSSHighlighter(QSyntaxHighlighter):
    """Syntax highlighter for CSS code."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.highlighting_rules = []
        
        # Define formats for different syntax elements
        selector_format = QTextCharFormat()
        selector_format.setForeground(QColor("#D7BA7D"))
        selector_format.setFontWeight(QFont.Weight.Bold)
        
        # Selector pattern
        pattern = QRegularExpression(r'[.#]?[\w-]+(?=[^}]*{)')
        self.highlighting_rules.append((pattern, selector_format))
        
        # Property format
        property_format = QTextCharFormat()
        property_format.setForeground(QColor("#9CDCFE"))
        pattern = QRegularExpression(r'[\w-]+(?=\s*:)')
        self.highlighting_rules.append((pattern, property_format))
        
        # Value format
        value_format = QTextCharFormat()
        value_format.setForeground(QColor("#CE9178"))
        pattern = QRegularExpression(r':\s*[^;]+')
        self.highlighting_rules.append((pattern, value_format))
        
        # Number format
        number_format = QTextCharFormat()
        number_format.setForeground(QColor("#B5CEA8"))
        pattern = QRegularExpression(r'\b[0-9]+(?:px|em|rem|%|vh|vw|pt|pc|in|cm|mm|ex|ch)?\b')
        self.highlighting_rules.append((pattern, number_format))
        
        # Color format
        color_format = QTextCharFormat()
        color_format.setForeground(QColor("#D69D85"))
        pattern = QRegularExpression(r'#[0-9A-Fa-f]{3,6}')
        self.highlighting_rules.append((pattern, color_format))
        
        # Comment format
        comment_format = QTextCharFormat()
        comment_format.setForeground(QColor("#6A9955"))
        
        self.comment_start_expression = QRegularExpression(r'/\*')
        self.comment_end_expression = QRegularExpression(r'\*/')
        self.multi_line_comment_format = comment_format
        
    def highlightBlock(self, text):
        """Apply syntax highlighting to the given block of text."""
        # Apply regular expression highlighting rules
        for pattern, format in self.highlighting_rules:
            match_iterator = pattern.globalMatch(text)
            while match_iterator.hasNext():
                match = match_iterator.next()
                self.setFormat(match.capturedStart(), match.capturedLength(), format)
                
        # Handle multi-line comments
        self.setCurrentBlockState(0)
        
        start_index = 0
        if self.previousBlockState() != 1:
            start_index = text.indexOf(self.comment_start_expression)
            
        while start_index >= 0:
            match = self.comment_end_expression.match(text, start_index)
            end_index = match.capturedStart()
            comment_length = 0
            
            if end_index == -1:
                self.setCurrentBlockState(1)
                comment_length = len(text) - start_index
            else:
                comment_length = end_index - start_index + match.capturedLength()
                
            self.setFormat(start_index, comment_length, self.multi_line_comment_format)
            start_index = text.indexOf(self.comment_start_expression, start_index + comment_length)

class HTMLHighlighter(QSyntaxHighlighter):
    """Syntax highlighter for HTML code."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.highlighting_rules = []
        
        # Define formats for different syntax elements
        tag_format = QTextCharFormat()
        tag_format.setForeground(QColor("#569CD6"))
        tag_format.setFontWeight(QFont.Weight.Bold)
        
        # Tag pattern
        pattern = QRegularExpression(r'</?[a-zA-Z0-9]+(?:\s+[a-zA-Z0-9]+(?:="[^"]*")?)*\s*/?>')
        self.highlighting_rules.append((pattern, tag_format))
        
        # Attribute format
        attribute_format = QTextCharFormat()
        attribute_format.setForeground(QColor("#9CDCFE"))
        pattern = QRegularExpression(r'\b[a-zA-Z0-9_-]+(?=\s*=)')
        self.highlighting_rules.append((pattern, attribute_format))
        
        # Attribute value format
        value_format = QTextCharFormat()
        value_format.setForeground(QColor("#CE9178"))
        pattern = QRegularExpression(r'"[^"]*"')
        self.highlighting_rules.append((pattern, value_format))
        
        # Comment format
        comment_format = QTextCharFormat()
        comment_format.setForeground(QColor("#6A9955"))
        
        self.comment_start_expression = QRegularExpression(r'<!--')
        self.comment_end_expression = QRegularExpression(r'-->')
        self.multi_line_comment_format = comment_format
        
    def highlightBlock(self, text):
        """Apply syntax highlighting to the given block of text."""
        # Apply regular expression highlighting rules
        for pattern, format in self.highlighting_rules:
            match_iterator = pattern.globalMatch(text)
            while match_iterator.hasNext():
                match = match_iterator.next()
                self.setFormat(match.capturedStart(), match.capturedLength(), format)
                
        # Handle multi-line comments
        self.setCurrentBlockState(0)
        
        start_index = 0
        if self.previousBlockState() != 1:
            start_index = text.indexOf(self.comment_start_expression)
            
        while start_index >= 0:
            match = self.comment_end_expression.match(text, start_index)
            end_index = match.capturedStart()
            comment_length = 0
            
            if end_index == -1:
                self.setCurrentBlockState(1)
                comment_length = len(text) - start_index
            else:
                comment_length = end_index - start_index + match.capturedLength()
                
            self.setFormat(start_index, comment_length, self.multi_line_comment_format)
            start_index = text.indexOf(self.comment_start_expression, start_index + comment_length) 