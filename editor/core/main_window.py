import os
import webbrowser
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                           QSplitter, QToolBar, QStatusBar, QMessageBox, 
                           QTabWidget, QMenu, QFileDialog)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QAction, QIcon, QKeySequence

from editor.core.file_explorer import FileExplorer
from editor.core.code_editor import CodeEditor
from editor.core.highlighters import JavaScriptHighlighter, CSSHighlighter, HTMLHighlighter
from editor.core.game_data_manager import GameDataManager
from editor.modules.character_editor.character_editor import CharacterEditorTab
from editor.modules.item_editor.item_editor import ItemEditorTab
from editor.modules.map_editor.map_editor import MapEditorTab
from editor.modules.battle_editor.battle_editor import BattleEditorTab
from editor.modules.spell_editor.spell_editor import SpellEditorTab
from editor.utils.themes import apply_dark_theme

class MainWindow(QMainWindow):
    """Main application window for OpenFF Game Editor."""
    
    def __init__(self):
        super().__init__()
        self.current_file = None
        self.editors = {}  # Map of file paths to editor widgets
        self.game_data = GameDataManager()
        
        self.initUI()
        self.load_game_data()
        
    def initUI(self):
        """Initialize the user interface."""
        # Set window properties
        self.setWindowTitle("OpenFF Game Editor")
        self.setGeometry(100, 100, 1280, 800)
        
        # Create the central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QHBoxLayout(central_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Create a splitter for the file tree and editor
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Create the file explorer
        self.file_explorer = FileExplorer()
        self.file_explorer.file_clicked.connect(self.open_file)
        
        # Create tab widget for multiple files and editors
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabsClosable(True)
        self.tab_widget.tabCloseRequested.connect(self.close_tab)
        
        # Add widgets to the splitter
        self.splitter.addWidget(self.file_explorer)
        self.splitter.addWidget(self.tab_widget)
        self.splitter.setSizes([250, 1030])
        
        # Add the splitter to the layout
        layout.addWidget(self.splitter)
        
        # Create toolbar
        self.create_toolbar()
        
        # Create status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")
        
        # Set up keyboard shortcuts
        self.setup_shortcuts()
        
        # Add initial tabs for game editors
        self.setup_game_editor_tabs()
        
        # Apply the theme (dark theme by default)
        apply_dark_theme(self)
        
    def create_toolbar(self):
        """Create the main toolbar."""
        toolbar = QToolBar("Main Toolbar")
        toolbar.setIconSize(QSize(24, 24))
        self.addToolBar(toolbar)
        
        # New file action
        new_action = QAction("New File", self)
        new_action.triggered.connect(self.new_file)
        toolbar.addAction(new_action)
        
        # Open file action
        open_action = QAction("Open File", self)
        open_action.triggered.connect(self.open_file_dialog)
        toolbar.addAction(open_action)
        
        # Save file action
        save_action = QAction("Save", self)
        save_action.triggered.connect(self.save_current_tab)
        toolbar.addAction(save_action)
        
        toolbar.addSeparator()
        
        # Run game action
        run_action = QAction("Run Game", self)
        run_action.triggered.connect(self.run_game)
        toolbar.addAction(run_action)
        
        # Reload data action
        reload_action = QAction("Reload Game Data", self)
        reload_action.triggered.connect(self.load_game_data)
        toolbar.addAction(reload_action)
        
    def setup_shortcuts(self):
        """Set up keyboard shortcuts for common actions."""
        # Save
        save_shortcut = QKeySequence("Ctrl+S")
        save_action = QAction("Save", self)
        save_action.setShortcut(save_shortcut)
        save_action.triggered.connect(self.save_current_tab)
        self.addAction(save_action)
        
        # Find
        find_shortcut = QKeySequence("Ctrl+F")
        find_action = QAction("Find", self)
        find_action.setShortcut(find_shortcut)
        find_action.triggered.connect(self.find_text)
        self.addAction(find_action)
        
        # Close tab
        close_shortcut = QKeySequence("Ctrl+W")
        close_action = QAction("Close Tab", self)
        close_action.setShortcut(close_shortcut)
        close_action.triggered.connect(self.close_current_tab)
        self.addAction(close_action)
        
        # Run game
        run_shortcut = QKeySequence("F5")
        run_action = QAction("Run Game", self)
        run_action.setShortcut(run_shortcut)
        run_action.triggered.connect(self.run_game)
        self.addAction(run_action)
        
    def setup_game_editor_tabs(self):
        """Set up the game editor tabs."""
        # Create game editor tabs
        self.character_editor = CharacterEditorTab(self.game_data)
        self.item_editor = ItemEditorTab(self.game_data)
        self.map_editor = MapEditorTab(self.game_data)
        self.battle_editor = BattleEditorTab(self.game_data)
        self.spell_editor = SpellEditorTab(self.game_data)
        
        # Add the tabs
        self.tab_widget.addTab(self.character_editor, "Characters")
        self.tab_widget.addTab(self.item_editor, "Items")
        self.tab_widget.addTab(self.map_editor, "Maps")
        self.tab_widget.addTab(self.battle_editor, "Battles")
        self.tab_widget.addTab(self.spell_editor, "Spells")
        
    def load_game_data(self):
        """Load game data from the app.js file."""
        # Find the app.js file
        js_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'js', 'app.js')
        
        try:
            if os.path.exists(js_path):
                # Load and parse game data
                self.game_data.load_from_file(js_path)
                
                # Update all editor tabs
                self.update_all_editors()
                
                self.status_bar.showMessage("Game data loaded successfully")
            else:
                self.status_bar.showMessage("Could not find app.js file")
                
        except Exception as e:
            self.status_bar.showMessage(f"Error loading game data: {str(e)}")
            QMessageBox.warning(self, "Loading Error", f"Failed to load game data: {str(e)}")
            
    def update_all_editors(self):
        """Update all game editor tabs with current game data."""
        # Update each editor tab with the latest game data
        self.character_editor.update_data()
        self.item_editor.update_data()
        self.map_editor.update_data()
        self.battle_editor.update_data()
        self.spell_editor.update_data()
        
    def get_highlighter_for_file(self, file_path):
        """Return the appropriate highlighter for the given file type."""
        extension = os.path.splitext(file_path)[1].lower()
        if extension == '.js':
            return JavaScriptHighlighter
        elif extension == '.css':
            return CSSHighlighter
        elif extension in ['.html', '.htm']:
            return HTMLHighlighter
        else:
            return None
        
    def open_file(self, file_path):
        """Open a file in the editor."""
        if not os.path.isfile(file_path):
            QMessageBox.warning(self, "Error", f"File not found: {file_path}")
            return
            
        # Check if file is already open in a tab
        if file_path in self.editors:
            # Switch to the existing tab
            for i in range(self.tab_widget.count()):
                if self.tab_widget.widget(i) == self.editors[file_path]:
                    self.tab_widget.setCurrentIndex(i)
                    self.current_file = file_path
                    break
            return
            
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Create a new tab with a text editor
            editor = CodeEditor()
            editor.setPlainText(content)
            
            # Set file path attribute on the editor
            editor.file_path = file_path
            
            # Set the highlighter based on file extension
            highlighter_class = self.get_highlighter_for_file(file_path)
            if highlighter_class:
                editor.setHighlighter(highlighter_class)
            
            # Add the new tab
            tab_name = os.path.basename(file_path)
            tab_index = self.tab_widget.addTab(editor, tab_name)
            self.tab_widget.setCurrentIndex(tab_index)
            
            # Store the mapping of file path to editor
            self.editors[file_path] = editor
            self.current_file = file_path
            
            self.status_bar.showMessage(f"Opened: {file_path}")
            
            # If opening app.js, also reload game data
            if file_path.endswith('app.js'):
                self.load_game_data()
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to open file:\n{str(e)}")
            
    def open_file_dialog(self):
        """Open a file using a file dialog."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, 
            "Open File", 
            "", 
            "All Files (*)"
        )
        if file_path:
            self.open_file(file_path)
            
    def save_current_tab(self):
        """Save the current tab's content to its file."""
        current_tab = self.tab_widget.currentWidget()
        if not current_tab:
            return
            
        # Handle different types of tab content
        if isinstance(current_tab, CodeEditor):
            # Get the file path associated with this tab
            file_path = getattr(current_tab, 'file_path', None)
            if not file_path:
                # If no file path, prompt for save location
                self.save_as()
                return
                
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(current_tab.toPlainText())
                self.status_bar.showMessage(f"Saved: {file_path}")
                
                # If saving app.js, update game data
                if file_path.endswith('app.js'):
                    self.load_game_data()
                    
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save file:\n{str(e)}")
        else:
            # This is a game editor tab, save its changes
            if hasattr(current_tab, 'save_changes'):
                try:
                    current_tab.save_changes()
                    self.status_bar.showMessage("Changes saved successfully")
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"Failed to save changes:\n{str(e)}")
            
    def save_as(self):
        """Save the current tab's content to a new file."""
        current_tab = self.tab_widget.currentWidget()
        if not current_tab or not isinstance(current_tab, CodeEditor):
            return
            
        file_path, _ = QFileDialog.getSaveFileName(
            self, 
            "Save As", 
            "", 
            "All Files (*)"
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(current_tab.toPlainText())
                    
                # Update the tab information
                old_file_path = getattr(current_tab, 'file_path', None)
                if old_file_path and old_file_path in self.editors:
                    del self.editors[old_file_path]
                    
                current_tab.file_path = file_path
                self.editors[file_path] = current_tab
                self.tab_widget.setTabText(self.tab_widget.currentIndex(), os.path.basename(file_path))
                self.status_bar.showMessage(f"Saved as: {file_path}")
                
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save file:\n{str(e)}")
                
    def find_text(self):
        """Find text in the current editor."""
        current_tab = self.tab_widget.currentWidget()
        if not current_tab or not isinstance(current_tab, CodeEditor):
            return
            
        current_tab.find_text_dialog()
        
    def new_file(self):
        """Create a new file."""
        file_path, _ = QFileDialog.getSaveFileName(
            self, 
            "New File", 
            "", 
            "All Files (*)"
        )
        if file_path:
            with open(file_path, 'w') as f:
                f.write("")
            self.open_file(file_path)
            
    def close_tab(self, index):
        """Close the tab at the given index."""
        if index < 0 or index >= self.tab_widget.count():
            return
            
        tab_widget = self.tab_widget.widget(index)
        
        # Don't allow closing game editor tabs
        if not isinstance(tab_widget, CodeEditor):
            return
            
        file_path = getattr(tab_widget, 'file_path', None)
        
        if file_path and file_path in self.editors:
            del self.editors[file_path]
            
        self.tab_widget.removeTab(index)
        
    def close_current_tab(self):
        """Close the currently active tab."""
        current_index = self.tab_widget.currentIndex()
        if current_index >= 0:
            self.close_tab(current_index)
            
    def run_game(self):
        """Run the OpenFF game in a web browser."""
        # First save any changes
        if self.current_file:
            self.save_current_tab()
            
        # Determine the game's HTML file path
        base_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..')
        index_path = os.path.join(base_dir, 'index.html')
        
        # If index.html exists, open it in the default browser
        if os.path.exists(index_path):
            url = f"file://{index_path}"
            try:
                webbrowser.open(url)
                self.status_bar.showMessage(f"Running game at {url}")
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Failed to open browser:\n{str(e)}")
        else:
            QMessageBox.warning(self, "Error", "Could not find index.html in the project directory.") 