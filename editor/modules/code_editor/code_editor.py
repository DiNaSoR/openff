"""
Code Editor Tab for the OpenFF Game Editor.

This module provides a tab for editing JavaScript code.
"""

import os
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, 
                           QPushButton, QFileDialog, QLabel, QMessageBox,
                           QSplitter)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QFont, QFontMetrics, QColor, QTextCharFormat, QSyntaxHighlighter

class SimpleJsSyntaxHighlighter(QSyntaxHighlighter):
    """Simple syntax highlighter for JavaScript code."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.highlighting_rules = []
        
        # Keyword format
        keyword_format = QTextCharFormat()
        keyword_format.setForeground(QColor("#0000FF"))
        keyword_format.setFontWeight(QFont.Weight.Bold)
        keywords = [
            r'\bvar\b', r'\blet\b', r'\bconst\b', r'\bfunction\b', r'\breturn\b',
            r'\bif\b', r'\belse\b', r'\bfor\b', r'\bwhile\b', r'\bdo\b',
            r'\bswitch\b', r'\bcase\b', r'\bbreak\b', r'\bcontinue\b',
            r'\btry\b', r'\bcatch\b', r'\bthrow\b', r'\bnew\b', r'\bthis\b',
            r'\btypeof\b', r'\binstanceof\b', r'\bdelete\b', r'\bvoid\b',
            r'\bin\b', r'\bof\b', r'\btrue\b', r'\bfalse\b', r'\bnull\b',
            r'\bundefined\b', r'\bclass\b', r'\bextends\b', r'\bsuper\b',
            r'\bimport\b', r'\bexport\b', r'\basync\b', r'\bawait\b'
        ]
        for pattern in keywords:
            self.highlighting_rules.append((pattern, keyword_format))
        
        # Comment format
        comment_format = QTextCharFormat()
        comment_format.setForeground(QColor("#008000"))
        self.highlighting_rules.append((r'//[^\n]*', comment_format))
        
        # String format
        string_format = QTextCharFormat()
        string_format.setForeground(QColor("#A31515"))
        self.highlighting_rules.append((r'".*?"', string_format))
        self.highlighting_rules.append((r"'.*?'", string_format))
        
        # Number format
        number_format = QTextCharFormat()
        number_format.setForeground(QColor("#800080"))
        self.highlighting_rules.append((r'\b\d+\b', number_format))
    
    def highlightBlock(self, text):
        """Highlight the current block of text."""
        for pattern, format in self.highlighting_rules:
            # Using Python's string find to locate matches
            # (simplified approach; not using full regex)
            i = 0
            while i < len(text):
                if pattern.startswith(r'\b') and pattern.endswith(r'\b'):
                    # Word boundary matching (simplified)
                    word = pattern[2:-2]  # Remove \b from start and end
                    i = text.find(word, i)
                    if i >= 0 and (i == 0 or not text[i-1].isalnum()) and (i + len(word) == len(text) or not text[i + len(word)].isalnum()):
                        self.setFormat(i, len(word), format)
                        i += len(word)
                    else:
                        i += 1
                elif pattern.startswith('//'):
                    # Comment matching
                    i = text.find('//', i)
                    if i >= 0:
                        self.setFormat(i, len(text) - i, format)
                        break
                    else:
                        break
                else:
                    # Simple string matching (simplified)
                    quote = pattern[0]
                    i = text.find(quote, i)
                    if i >= 0:
                        end = text.find(quote, i + 1)
                        if end >= 0:
                            self.setFormat(i, end - i + 1, format)
                            i = end + 1
                        else:
                            break
                    else:
                        break

class CodeEditorTab(QWidget):
    """Tab for editing code files."""
    
    def __init__(self):
        super().__init__()
        self.current_file = None
        self.init_ui()
    
    def init_ui(self):
        """Initialize the user interface."""
        # Main layout
        main_layout = QVBoxLayout(self)
        
        # File info section
        file_info_layout = QHBoxLayout()
        self.file_path_label = QLabel("No file loaded")
        file_info_layout.addWidget(self.file_path_label)
        
        # Add buttons for file operations
        open_button = QPushButton("Open")
        open_button.clicked.connect(self.open_file)
        save_button = QPushButton("Save")
        save_button.clicked.connect(self.save_file)
        save_as_button = QPushButton("Save As")
        save_as_button.clicked.connect(self.save_file_as)
        
        file_info_layout.addWidget(open_button)
        file_info_layout.addWidget(save_button)
        file_info_layout.addWidget(save_as_button)
        
        main_layout.addLayout(file_info_layout)
        
        # Add text editor
        self.editor = QTextEdit()
        self.editor.setFont(QFont("Courier New", 10))
        self.editor.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)
        
        # Enable syntax highlighting
        self.highlighter = SimpleJsSyntaxHighlighter(self.editor.document())
        
        main_layout.addWidget(self.editor)
    
    def load_file(self, file_path):
        """Load a file into the editor."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            self.editor.setText(content)
            self.current_file = file_path
            self.file_path_label.setText(file_path)
            return True
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"Could not load file: {str(e)}"
            )
            return False
    
    def open_file(self):
        """Open a file dialog to select a file to edit."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Open File",
            "",
            "JavaScript Files (*.js);;All Files (*)"
        )
        if file_path:
            self.load_file(file_path)
    
    def save_file(self):
        """Save the current file."""
        if not self.current_file:
            self.save_file_as()
            return
        
        try:
            with open(self.current_file, 'w', encoding='utf-8') as f:
                f.write(self.editor.toPlainText())
            QMessageBox.information(
                self,
                "Success",
                "File saved successfully!"
            )
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"Could not save file: {str(e)}"
            )
    
    def save_file_as(self):
        """Save the current file with a new name."""
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save File As",
            "",
            "JavaScript Files (*.js);;All Files (*)"
        )
        if file_path:
            self.current_file = file_path
            self.file_path_label.setText(file_path)
            self.save_file() 