import os
import sys
from PyQt6.QtWidgets import (QMainWindow, QTabWidget, QFileDialog, QMessageBox,
                           QVBoxLayout, QWidget, QSplitter, QApplication)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QIcon, QAction

from editor.modules.file_explorer.file_explorer import FileExplorer
from editor.modules.code_editor.code_editor import CodeEditor
from editor.modules.game_data.game_data_manager import GameDataManager
from editor.modules.character_editor.character_editor import CharacterEditorTab
from editor.modules.item_editor.item_editor import ItemEditorTab
from editor.modules.map_editor.map_editor import MapEditorTab
from editor.modules.battle_editor.battle_editor import BattleEditorTab
from editor.modules.spell_editor.spell_editor import SpellEditorTab
from editor.utils.theme import apply_theme

class MainWindow(QMainWindow):
    """Main window for the OpenFF Game Editor."""
    
    def __init__(self):
        super().__init__()
        
        # Initialize game data manager
        self.game_data = GameDataManager()
        
        # Set up the UI
        self.init_ui()
        
        # Apply theme
        apply_theme(self)
        
    def init_ui(self):
        """Initialize the user interface."""
        # Set window properties
        self.setWindowTitle("OpenFF Game Editor")
        self.setMinimumSize(1200, 800)
        
        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Create splitter for file explorer and editors
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Create file explorer
        self.file_explorer = FileExplorer()
        self.file_explorer.file_selected.connect(self.open_file)
        self.splitter.addWidget(self.file_explorer)
        
        # Create tab widget for editors
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabsClosable(True)
        self.tab_widget.tabCloseRequested.connect(self.close_tab)
        self.splitter.addWidget(self.tab_widget)
        
        # Set splitter sizes
        self.splitter.setSizes([200, 1000])
        
        # Add splitter to main layout
        main_layout.addWidget(self.splitter)
        
        # Create menu bar
        self.create_menu_bar()
        
        # Create status bar
        self.statusBar().showMessage("Ready")
        
        # Initialize editor tabs
        self.code_editors = {}  # Maps file paths to code editor instances
        self.game_editor_tabs = {}  # Maps tab names to game editor instances
        
        # Create game editor tabs
        self.create_game_editor_tabs()
        
    def create_menu_bar(self):
        """Create the menu bar with actions."""
        # File menu
        file_menu = self.menuBar().addMenu("&File")
        
        # New file action
        new_action = QAction("&New File", self)
        new_action.setShortcut("Ctrl+N")
        new_action.triggered.connect(self.new_file)
        file_menu.addAction(new_action)
        
        # Open file action
        open_action = QAction("&Open File", self)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self.open_file_dialog)
        file_menu.addAction(open_action)
        
        # Save action
        save_action = QAction("&Save", self)
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self.save_file)
        file_menu.addAction(save_action)
        
        # Save As action
        save_as_action = QAction("Save &As", self)
        save_as_action.setShortcut("Ctrl+Shift+S")
        save_as_action.triggered.connect(self.save_file_as)
        file_menu.addAction(save_as_action)
        
        file_menu.addSeparator()
        
        # Exit action
        exit_action = QAction("E&xit", self)
        exit_action.setShortcut("Alt+F4")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Edit menu
        edit_menu = self.menuBar().addMenu("&Edit")
        
        # Undo action
        undo_action = QAction("&Undo", self)
        undo_action.setShortcut("Ctrl+Z")
        undo_action.triggered.connect(self.undo)
        edit_menu.addAction(undo_action)
        
        # Redo action
        redo_action = QAction("&Redo", self)
        redo_action.setShortcut("Ctrl+Y")
        redo_action.triggered.connect(self.redo)
        edit_menu.addAction(redo_action)
        
        edit_menu.addSeparator()
        
        # Cut action
        cut_action = QAction("Cu&t", self)
        cut_action.setShortcut("Ctrl+X")
        cut_action.triggered.connect(self.cut)
        edit_menu.addAction(cut_action)
        
        # Copy action
        copy_action = QAction("&Copy", self)
        copy_action.setShortcut("Ctrl+C")
        copy_action.triggered.connect(self.copy)
        edit_menu.addAction(copy_action)
        
        # Paste action
        paste_action = QAction("&Paste", self)
        paste_action.setShortcut("Ctrl+V")
        paste_action.triggered.connect(self.paste)
        edit_menu.addAction(paste_action)
        
        # Game menu
        game_menu = self.menuBar().addMenu("&Game")
        
        # Load Game Data action
        load_data_action = QAction("&Load Game Data", self)
        load_data_action.triggered.connect(self.load_game_data)
        game_menu.addAction(load_data_action)
        
        # Save Game Data action
        save_data_action = QAction("&Save Game Data", self)
        save_data_action.triggered.connect(self.save_game_data)
        game_menu.addAction(save_data_action)
        
        # Help menu
        help_menu = self.menuBar().addMenu("&Help")
        
        # About action
        about_action = QAction("&About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
        
    def create_game_editor_tabs(self):
        """Create tabs for game element editors."""
        # Load game data first
        self.game_data.load_from_file()
        
        # Create character editor tab
        character_tab = CharacterEditorTab(self.game_data)
        self.tab_widget.addTab(character_tab, "Characters")
        self.game_editor_tabs["Characters"] = character_tab
        
        # Create item editor tab
        item_tab = ItemEditorTab(self.game_data)
        self.tab_widget.addTab(item_tab, "Items")
        self.game_editor_tabs["Items"] = item_tab
        
        # Create map editor tab
        map_tab = MapEditorTab(self.game_data)
        self.tab_widget.addTab(map_tab, "Maps")
        self.game_editor_tabs["Maps"] = map_tab
        
        # Create battle editor tab
        battle_tab = BattleEditorTab(self.game_data)
        self.tab_widget.addTab(battle_tab, "Battles")
        self.game_editor_tabs["Battles"] = battle_tab
        
        # Create spell editor tab
        spell_tab = SpellEditorTab(self.game_data)
        self.tab_widget.addTab(spell_tab, "Spells")
        self.game_editor_tabs["Spells"] = spell_tab
        
        # Update all tabs with game data
        self.update_game_editor_tabs()
        
    def update_game_editor_tabs(self):
        """Update all game editor tabs with the latest game data."""
        for tab in self.game_editor_tabs.values():
            tab.update_data()
            
    def new_file(self):
        """Create a new file."""
        # Create a new code editor
        editor = CodeEditor()
        
        # Add to tab widget
        index = self.tab_widget.addTab(editor, "Untitled")
        self.tab_widget.setCurrentIndex(index)
        
        # Set focus to the editor
        editor.setFocus()
        
    def open_file_dialog(self):
        """Open a file dialog to select a file to open."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open File", "", "All Files (*)"
        )
        
        if file_path:
            self.open_file(file_path)
            
    def open_file(self, file_path):
        """Open a file in a new tab or switch to it if already open."""
        # Check if file is already open
        if file_path in self.code_editors:
            # Switch to the tab
            index = self.tab_widget.indexOf(self.code_editors[file_path])
            self.tab_widget.setCurrentIndex(index)
            return
            
        # Create a new code editor
        editor = CodeEditor()
        
        try:
            # Read the file
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Set the content
            editor.setPlainText(content)
            
            # Set the file path
            editor.file_path = file_path
            
            # Add to tab widget
            file_name = os.path.basename(file_path)
            index = self.tab_widget.addTab(editor, file_name)
            self.tab_widget.setCurrentIndex(index)
            
            # Add to code editors
            self.code_editors[file_path] = editor
            
            # Set focus to the editor
            editor.setFocus()
            
            # Update status bar
            self.statusBar().showMessage(f"Opened {file_path}")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not open file: {str(e)}")
            
    def save_file(self):
        """Save the current file."""
        # Get the current tab
        current_tab = self.tab_widget.currentWidget()
        
        # Check if it's a code editor
        if isinstance(current_tab, CodeEditor):
            # Check if the file has a path
            if current_tab.file_path:
                try:
                    # Write the content to the file
                    with open(current_tab.file_path, 'w', encoding='utf-8') as f:
                        f.write(current_tab.toPlainText())
                        
                    # Update status bar
                    self.statusBar().showMessage(f"Saved {current_tab.file_path}")
                    
                    # Mark as not modified
                    current_tab.document().setModified(False)
                    
                    # Update tab text (remove asterisk if present)
                    index = self.tab_widget.currentIndex()
                    tab_text = self.tab_widget.tabText(index)
                    if tab_text.endswith('*'):
                        self.tab_widget.setTabText(index, tab_text[:-1])
                        
                    # If this is app.js, update game data
                    if current_tab.file_path.endswith('app.js'):
                        self.game_data.load_from_file()
                        self.update_game_editor_tabs()
                        self.statusBar().showMessage(f"Saved {current_tab.file_path} and updated game data")
                        
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"Could not save file: {str(e)}")
            else:
                # No file path, use save as
                self.save_file_as()
        elif current_tab in self.game_editor_tabs.values():
            # Save game data
            self.save_game_data()
            
    def save_file_as(self):
        """Save the current file with a new name."""
        # Get the current tab
        current_tab = self.tab_widget.currentWidget()
        
        # Check if it's a code editor
        if isinstance(current_tab, CodeEditor):
            # Open a file dialog
            file_path, _ = QFileDialog.getSaveFileName(
                self, "Save File As", "", "All Files (*)"
            )
            
            if file_path:
                # Set the file path
                current_tab.file_path = file_path
                
                # Save the file
                self.save_file()
                
                # Update tab text
                index = self.tab_widget.currentIndex()
                self.tab_widget.setTabText(index, os.path.basename(file_path))
                
                # Update code editors dictionary
                self.code_editors[file_path] = current_tab
                
    def close_tab(self, index):
        """Close the tab at the given index."""
        # Get the widget
        widget = self.tab_widget.widget(index)
        
        # Check if it's a code editor and has unsaved changes
        if isinstance(widget, CodeEditor) and widget.document().isModified():
            # Ask for confirmation
            reply = QMessageBox.question(
                self, "Unsaved Changes",
                "This file has unsaved changes. Do you want to save them?",
                QMessageBox.StandardButton.Save | QMessageBox.StandardButton.Discard | QMessageBox.StandardButton.Cancel
            )
            
            if reply == QMessageBox.StandardButton.Save:
                # Save the file
                self.tab_widget.setCurrentIndex(index)
                self.save_file()
                
            elif reply == QMessageBox.StandardButton.Cancel:
                # Cancel closing
                return
                
        # Remove from code editors if it's a code editor
        if isinstance(widget, CodeEditor) and widget.file_path in self.code_editors:
            del self.code_editors[widget.file_path]
            
        # Close the tab
        self.tab_widget.removeTab(index)
        
    def undo(self):
        """Undo the last action in the current editor."""
        current_tab = self.tab_widget.currentWidget()
        if isinstance(current_tab, CodeEditor):
            current_tab.undo()
            
    def redo(self):
        """Redo the last undone action in the current editor."""
        current_tab = self.tab_widget.currentWidget()
        if isinstance(current_tab, CodeEditor):
            current_tab.redo()
            
    def cut(self):
        """Cut the selected text in the current editor."""
        current_tab = self.tab_widget.currentWidget()
        if isinstance(current_tab, CodeEditor):
            current_tab.cut()
            
    def copy(self):
        """Copy the selected text in the current editor."""
        current_tab = self.tab_widget.currentWidget()
        if isinstance(current_tab, CodeEditor):
            current_tab.copy()
            
    def paste(self):
        """Paste text from the clipboard into the current editor."""
        current_tab = self.tab_widget.currentWidget()
        if isinstance(current_tab, CodeEditor):
            current_tab.paste()
            
    def load_game_data(self):
        """Load game data from file."""
        try:
            self.game_data.load_from_file()
            self.update_game_editor_tabs()
            self.statusBar().showMessage("Game data loaded successfully")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not load game data: {str(e)}")
            
    def save_game_data(self):
        """Save game data to file."""
        try:
            # Save changes from all tabs
            for tab in self.game_editor_tabs.values():
                if hasattr(tab, 'save_changes'):
                    tab.save_changes()
                    
            # Save to file
            self.game_data.save_to_file()
            self.statusBar().showMessage("Game data saved successfully")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not save game data: {str(e)}")
            
    def show_about(self):
        """Show the about dialog."""
        QMessageBox.about(
            self,
            "About OpenFF Game Editor",
            "OpenFF Game Editor\n\n"
            "A specialized editor for the OpenFF game project.\n"
            "This editor provides tools for editing game elements like characters, "
            "items, maps, battles, and spells, as well as code editing capabilities."
        )
        
    def closeEvent(self, event):
        """Handle the window close event."""
        # Check for unsaved changes in code editors
        for editor in self.code_editors.values():
            if editor.document().isModified():
                # Ask for confirmation
                reply = QMessageBox.question(
                    self, "Unsaved Changes",
                    "There are unsaved changes. Do you want to save them before exiting?",
                    QMessageBox.StandardButton.Save | QMessageBox.StandardButton.Discard | QMessageBox.StandardButton.Cancel
                )
                
                if reply == QMessageBox.StandardButton.Save:
                    # Save all modified files
                    for i in range(self.tab_widget.count()):
                        widget = self.tab_widget.widget(i)
                        if isinstance(widget, CodeEditor) and widget.document().isModified():
                            self.tab_widget.setCurrentIndex(i)
                            self.save_file()
                    break
                    
                elif reply == QMessageBox.StandardButton.Cancel:
                    # Cancel closing
                    event.ignore()
                    return
                    
                # If discard, just continue with closing
                break
                
        # Check for unsaved game data changes
        try:
            # Ask for confirmation
            reply = QMessageBox.question(
                self, "Save Game Data",
                "Do you want to save game data changes before exiting?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No | QMessageBox.StandardButton.Cancel
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                # Save game data
                self.save_game_data()
                
            elif reply == QMessageBox.StandardButton.Cancel:
                # Cancel closing
                event.ignore()
                return
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not save game data: {str(e)}")
            
        # Accept the event (close the window)
        event.accept() 