from PyQt6.QtWidgets import QPlainTextEdit, QWidget, QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton
from PyQt6.QtCore import Qt, QRect, QSize, pyqtSignal
from PyQt6.QtGui import QFont, QColor, QTextFormat, QPainter, QTextCursor, QSyntaxHighlighter

class LineNumberArea(QWidget):
    """Line number area widget for the code editor."""
    
    def __init__(self, editor):
        super().__init__(editor)
        self.editor = editor
        
    def sizeHint(self):
        """Return the size hint for the line number area."""
        return QSize(self.editor.line_number_area_width(), 0)
        
    def paintEvent(self, event):
        """Paint the line number area."""
        self.editor.lineNumberAreaPaintEvent(event)

class CodeEditor(QPlainTextEdit):
    """Enhanced code editor with line numbers and syntax highlighting."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFont(QFont("Courier New", 10))
        self.file_path = None
        self.highlighter = None
        
        # Set up line numbers
        self.line_number_area = LineNumberArea(self)
        self.blockCountChanged.connect(self.update_line_number_area_width)
        self.updateRequest.connect(self.update_line_number_area)
        self.update_line_number_area_width(0)
        
        # Set tab width
        font_metrics = self.fontMetrics()
        self.setTabStopDistance(4 * font_metrics.horizontalAdvance(' '))
        
        # Set editor properties
        self.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)
        
    def line_number_area_width(self):
        """Calculate the width of the line number area."""
        digits = 1
        max_num = max(1, self.blockCount())
        while max_num >= 10:
            max_num //= 10
            digits += 1
            
        space = 3 + self.fontMetrics().horizontalAdvance('9') * digits
        return space
        
    def update_line_number_area_width(self, _):
        """Update the width of the line number area."""
        self.setViewportMargins(self.line_number_area_width(), 0, 0, 0)
        
    def update_line_number_area(self, rect, dy):
        """Update the line number area when the editor viewport is scrolled."""
        if dy:
            self.line_number_area.scroll(0, dy)
        else:
            self.line_number_area.update(0, rect.y(), self.line_number_area.width(), rect.height())
            
        if rect.contains(self.viewport().rect()):
            self.update_line_number_area_width(0)
            
    def resizeEvent(self, event):
        """Handle resize events to adjust the line number area."""
        super().resizeEvent(event)
        
        cr = self.contentsRect()
        self.line_number_area.setGeometry(QRect(cr.left(), cr.top(), self.line_number_area_width(), cr.height()))
        
    def lineNumberAreaPaintEvent(self, event):
        """Paint the line number area with line numbers."""
        painter = QPainter(self.line_number_area)
        painter.fillRect(event.rect(), QColor(53, 53, 53))
        
        block = self.firstVisibleBlock()
        block_number = block.blockNumber()
        top = round(self.blockBoundingGeometry(block).translated(self.contentOffset()).top())
        bottom = top + round(self.blockBoundingRect(block).height())
        
        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                number = str(block_number + 1)
                painter.setPen(QColor(120, 120, 120))
                painter.drawText(0, top, self.line_number_area.width() - 2, self.fontMetrics().height(),
                                Qt.AlignmentFlag.AlignRight, number)
                                
            block = block.next()
            top = bottom
            bottom = top + round(self.blockBoundingRect(block).height())
            block_number += 1
            
    def setContent(self, content):
        """Set the content of the editor."""
        self.setPlainText(content)
        
    def setHighlighter(self, highlighter_class, *args, **kwargs):
        """Set the syntax highlighter for the editor."""
        if self.highlighter:
            self.highlighter.setDocument(None)
            
        self.highlighter = highlighter_class(self.document(), *args, **kwargs)
        
    def find_text_dialog(self):
        """Show a dialog to find text in the editor."""
        dialog = QDialog(self)
        dialog.setWindowTitle("Find Text")
        dialog.setMinimumWidth(300)
        
        layout = QVBoxLayout(dialog)
        
        # Create search input
        search_layout = QHBoxLayout()
        search_label = QLabel("Find:")
        self.search_input = QLineEdit()
        search_layout.addWidget(search_label)
        search_layout.addWidget(self.search_input)
        
        # Create buttons
        button_layout = QHBoxLayout()
        find_button = QPushButton("Find Next")
        find_button.clicked.connect(lambda: self.find_next(self.search_input.text()))
        close_button = QPushButton("Close")
        close_button.clicked.connect(dialog.close)
        button_layout.addWidget(find_button)
        button_layout.addWidget(close_button)
        
        layout.addLayout(search_layout)
        layout.addLayout(button_layout)
        
        dialog.setLayout(layout)
        dialog.show()
        
    def find_next(self, text):
        """Find the next occurrence of the specified text."""
        if not text:
            return
            
        # Start from the current cursor position
        cursor = self.textCursor()
        
        # If text is already selected, start from the end of the selection
        if cursor.hasSelection():
            cursor.setPosition(cursor.selectionEnd())
            
        # Find the text
        cursor = self.document().find(text, cursor)
        
        if cursor.isNull():
            # If not found from current position, try from the beginning
            cursor = self.document().find(text, QTextCursor.MoveOperation.Start)
            
        if not cursor.isNull():
            self.setTextCursor(cursor)
        else:
            # Not found
            pass 