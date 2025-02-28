import os
import sys
import json
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                            QTreeView, QFileSystemModel, QTextEdit, QSplitter, QAction, 
                            QToolBar, QStatusBar, QFileDialog, QMessageBox, QInputDialog,
                            QLineEdit, QMenu, QShortcut)
from PyQt6.QtCore import Qt, QDir, QModelIndex, QFileInfo
from PyQt6.QtGui import QFont, QSyntaxHighlighter, QTextCharFormat, QColor, QKeySequence
import re

class JavaScriptHighlighter(QSyntaxHighlighter):
    """Syntax highlighter for JavaScript code."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.highlighting_rules = []
        
        # Keywords
        keyword_format = QTextCharFormat()
        keyword_format.setForeground(QColor(120, 120, 250))
        keyword_format.setFontWeight(QFont.Weight.Bold)
        keywords = [
            'break', 'case', 'catch', 'class', 'const', 'continue', 'debugger', 
            'default', 'delete', 'do', 'else', 'export', 'extends', 'finally', 
            'for', 'function', 'if', 'import', 'in', 'instanceof', 'new', 'return', 
            'super', 'switch', 'this', 'throw', 'try', 'typeof', 'var', 'void', 
            'while', 'with', 'yield', 'let'
        ]
        for word in keywords:
            pattern = r'\b' + word + r'\b'
            self.highlighting_rules.append((re.compile(pattern), keyword_format))
        
        # Number format
        number_format = QTextCharFormat()
        number_format.setForeground(QColor(200, 120, 50))
        self.highlighting_rules.append((re.compile(r'\b[0-9]+\b'), number_format))
        
        # String format
        string_format = QTextCharFormat()
        string_format.setForeground(QColor(50, 150, 50))
        self.highlighting_rules.append((re.compile(r'".*?"'), string_format))
        self.highlighting_rules.append((re.compile(r"'.*?'"), string_format))
        
        # Comment format
        comment_format = QTextCharFormat()
        comment_format.setForeground(QColor(100, 100, 100))
        self.highlighting_rules.append((re.compile(r'//.*'), comment_format))
        
        # Function format
        function_format = QTextCharFormat()
        function_format.setForeground(QColor(220, 150, 50))
        self.highlighting_rules.append((re.compile(r'\b[A-Za-z0-9_]+(?=\s*\()'), function_format))
    
    def highlightBlock(self, text):
        """Apply highlighting to the given block of text."""
        for pattern, format in self.highlighting_rules:
            for match in pattern.finditer(text):
                start, end = match.span()
                self.setFormat(start, end - start, format)

class CodeEditor(QTextEdit):
    """Custom QTextEdit with line numbers and JavaScript syntax highlighting."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFont(QFont("Courier New", 10))
        self.highlighter = JavaScriptHighlighter(self.document())
        
    def setContent(self, content):
        """Set the content of the editor."""
        self.setPlainText(content)

class OpenFFEditor(QMainWindow):
    """Main application window for OpenFF editor."""
    
    def __init__(self):
        super().__init__()
        self.current_file = None
        self.initUI()
        
    def initUI(self):
        """Initialize the user interface."""
        # Set window properties
        self.setWindowTitle("OpenFF Script Editor")
        self.setGeometry(100, 100, 1200, 800)
        
        # Create the central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QHBoxLayout(central_widget)
        
        # Create a splitter for the file tree and editor
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Create the file system model and view
        self.file_model = QFileSystemModel()
        self.file_model.setRootPath(os.path.dirname(os.path.abspath(__file__)))
        self.file_tree = QTreeView()
        self.file_tree.setModel(self.file_model)
        self.file_tree.setRootIndex(self.file_model.index(os.path.dirname(os.path.abspath(__file__))))
        self.file_tree.setColumnWidth(0, 250)
        self.file_tree.clicked.connect(self.file_clicked)
        
        # Create the code editor
        self.editor = CodeEditor()
        
        # Add widgets to the splitter
        splitter.addWidget(self.file_tree)
        splitter.addWidget(self.editor)
        splitter.setSizes([250, 950])
        
        # Add the splitter to the layout
        layout.addWidget(splitter)
        
        # Create toolbar
        self.create_toolbar()
        
        # Create status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")
        
        # Set up context menu for the file tree
        self.file_tree.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.file_tree.customContextMenuRequested.connect(self.show_context_menu)
        
        # Set up keyboard shortcuts
        QShortcut(QKeySequence("Ctrl+S"), self, self.save_file)
        QShortcut(QKeySequence("Ctrl+F"), self, self.find_text)
        
    def create_toolbar(self):
        """Create the toolbar with actions."""
        toolbar = QToolBar("Main Toolbar")
        self.addToolBar(toolbar)
        
        # Open file action
        open_action = QAction("Open", self)
        open_action.triggered.connect(self.open_file)
        toolbar.addAction(open_action)
        
        # Save file action
        save_action = QAction("Save", self)
        save_action.triggered.connect(self.save_file)
        toolbar.addAction(save_action)
        
        # Find text action
        find_action = QAction("Find", self)
        find_action.triggered.connect(self.find_text)
        toolbar.addAction(find_action)
        
        # Add new file action
        new_file_action = QAction("New File", self)
        new_file_action.triggered.connect(self.new_file)
        toolbar.addAction(new_file_action)
        
    def file_clicked(self, index):
        """Handle file selection in the tree view."""
        file_path = self.file_model.filePath(index)
        if QFileInfo(file_path).isFile():
            self.open_file_from_path(file_path)
    
    def open_file_from_path(self, file_path):
        """Open a file from the given path."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            self.editor.setContent(content)
            self.current_file = file_path
            self.status_bar.showMessage(f"Opened: {file_path}")
            self.setWindowTitle(f"OpenFF Script Editor - {os.path.basename(file_path)}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to open file:\n{str(e)}")
            
    def open_file(self):
        """Open a file using a file dialog."""
        file_path, _ = QFileDialog.getOpenFileName(self, "Open File", "", "JavaScript Files (*.js);;All Files (*)")
        if file_path:
            self.open_file_from_path(file_path)
    
    def save_file(self):
        """Save the current file."""
        if self.current_file:
            try:
                with open(self.current_file, 'w', encoding='utf-8') as f:
                    f.write(self.editor.toPlainText())
                self.status_bar.showMessage(f"Saved: {self.current_file}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save file:\n{str(e)}")
        else:
            self.save_file_as()
    
    def save_file_as(self):
        """Save the current file with a new name."""
        file_path, _ = QFileDialog.getSaveFileName(self, "Save File As", "", "JavaScript Files (*.js);;All Files (*)")
        if file_path:
            self.current_file = file_path
            self.save_file()
    
    def find_text(self):
        """Find text in the editor."""
        text, ok = QInputDialog.getText(self, "Find Text", "Enter text to find:", QLineEdit.EchoMode.Normal)
        if ok and text:
            cursor = self.editor.document().find(text)
            if not cursor.isNull():
                self.editor.setTextCursor(cursor)
            else:
                self.status_bar.showMessage(f"Text '{text}' not found")
    
    def new_file(self):
        """Create a new file."""
        file_name, ok = QInputDialog.getText(self, "New File", "Enter file name:", QLineEdit.EchoMode.Normal)
        if ok and file_name:
            if not file_name.endswith('.js'):
                file_name += '.js'
                
            base_dir = os.path.dirname(os.path.abspath(__file__))
            file_path = os.path.join(base_dir, file_name)
            
            try:
                # Check if file exists
                if os.path.exists(file_path):
                    reply = QMessageBox.question(self, "File Exists", 
                                              f"File {file_name} already exists. Overwrite?",
                                              QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.No)
                    if reply == QMessageBox.StandardButton.No:
                        return
                
                # Create new empty file
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write("// New JavaScript file\n")
                
                # Open the file
                self.open_file_from_path(file_path)
                
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to create file:\n{str(e)}")
    
    def show_context_menu(self, position):
        """Show context menu for file tree."""
        index = self.file_tree.indexAt(position)
        if not index.isValid():
            return
            
        file_path = self.file_model.filePath(index)
        
        # Create context menu
        context_menu = QMenu()
        
        # Add actions based on whether it's a file or directory
        if QFileInfo(file_path).isFile():
            open_action = context_menu.addAction("Open")
            open_action.triggered.connect(lambda: self.open_file_from_path(file_path))
            
            delete_action = context_menu.addAction("Delete")
            delete_action.triggered.connect(lambda: self.delete_file(file_path))
        else:
            new_file_action = context_menu.addAction("New File Here")
            new_file_action.triggered.connect(lambda: self.new_file_in_dir(file_path))
        
        # Show the menu
        context_menu.exec(self.file_tree.viewport().mapToGlobal(position))
    
    def new_file_in_dir(self, directory):
        """Create a new file in the specified directory."""
        file_name, ok = QInputDialog.getText(self, "New File", "Enter file name:", QLineEdit.EchoMode.Normal)
        if ok and file_name:
            if not file_name.endswith('.js'):
                file_name += '.js'
                
            file_path = os.path.join(directory, file_name)
            
            try:
                # Check if file exists
                if os.path.exists(file_path):
                    reply = QMessageBox.question(self, "File Exists", 
                                              f"File {file_name} already exists. Overwrite?",
                                              QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.No)
                    if reply == QMessageBox.StandardButton.No:
                        return
                
                # Create new empty file
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write("// New JavaScript file\n")
                
                # Open the file
                self.open_file_from_path(file_path)
                
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to create file:\n{str(e)}")
    
    def delete_file(self, file_path):
        """Delete the specified file."""
        reply = QMessageBox.question(self, "Delete File", 
                                 f"Are you sure you want to delete {os.path.basename(file_path)}?",
                                 QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            try:
                os.remove(file_path)
                if self.current_file == file_path:
                    self.current_file = None
                    self.editor.clear()
                    self.setWindowTitle("OpenFF Script Editor")
                self.status_bar.showMessage(f"Deleted: {file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to delete file:\n{str(e)}")

def main():
    """Main function to run the application."""
    app = QApplication(sys.argv)
    editor = OpenFFEditor()
    editor.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
