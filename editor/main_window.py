import os
import sys
import platform
from PyQt6.QtWidgets import (QMainWindow, QTabWidget, QFileDialog, QMessageBox,
                           QVBoxLayout, QHBoxLayout, QWidget, QSplitter, QApplication, 
                           QLabel, QPushButton, QTreeView, QTextEdit, QProgressBar)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QIcon, QAction

# Import utilities
try:
    from editor.utils.theme import apply_theme
    # Import core components
    from editor.core.game_data_manager import GameDataManager
    # Import editor modules
    from editor.modules.character_editor.character_editor import CharacterEditorTab
    from editor.modules.item_editor.item_editor import ItemEditorTab
    from editor.modules.map_editor.map_editor import MapEditorTab
    from editor.modules.battle_editor.battle_editor import BattleEditorTab
    from editor.modules.spell_editor.spell_editor import SpellEditorTab
    from editor.modules.monster_editor.monster_editor import MonsterEditorTab
    from editor.modules.npc_editor.npc_editor import NPCEditorTab
    from editor.modules.code_editor.code_editor import CodeEditorTab
except ImportError:
    # Local imports
    from utils.theme import apply_theme
    # Import core components
    from core.game_data_manager import GameDataManager
    # Try to import modules directly (they might not exist yet)
    try:
        from modules.character_editor.character_editor import CharacterEditorTab
        from modules.item_editor.item_editor import ItemEditorTab
        from modules.map_editor.map_editor import MapEditorTab
        from modules.battle_editor.battle_editor import BattleEditorTab
        from modules.spell_editor.spell_editor import SpellEditorTab
        from modules.monster_editor.monster_editor import MonsterEditorTab
        from modules.npc_editor.npc_editor import NPCEditorTab
        from modules.code_editor.code_editor import CodeEditorTab
    except ImportError:
        # If modules don't exist yet, we'll handle it in the UI
        pass

class MainWindow(QMainWindow):
    """Main window for the OpenFF Game Editor."""
    
    def __init__(self):
        super().__init__()
        
        # Initialize attributes
        self.game_data = GameDataManager()
        self.code_editor = None
        
        # Set up the UI
        self.init_ui()
        
        # Automatic loading removed - main.py will handle this
        # self.load_game_data()
    
    def init_ui(self):
        """Initialize the user interface."""
        # Set window properties
        self.setWindowTitle("OpenFF Game Editor")
        self.setGeometry(100, 100, 1200, 800)
        
        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        main_layout.addWidget(self.tab_widget)
        
        # Create tabs
        self.create_main_tab()
        
        # Set up menus
        self.setup_menus()
        
        # Set up status bar
        self.statusBar().showMessage("Ready")
        
        # Create editor tabs (requires game data to be loaded)
        self.create_editor_tabs()
    
    def create_main_tab(self):
        """Create the main tab with welcome information."""
        main_tab = QWidget()
        main_layout = QVBoxLayout(main_tab)
        
        # Add a welcome title
        title = QLabel("Welcome to OpenFF Game Editor")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        font = title.font()
        font.setPointSize(16)
        title.setFont(font)
        main_layout.addWidget(title)
        
        # Add information about the editor
        info_text = """
        <html>
        <body>
        <p>OpenFF Game Editor is a tool for creating and editing game data for your RPG.</p>
        <p>Use the tabs above to edit different aspects of your game:</p>
        <ul>
        <li><b>Characters</b> - Create and edit player characters</li>
        <li><b>Items</b> - Create and edit items, weapons, and equipment</li>
        <li><b>Maps</b> - Design game maps and environments</li>
        <li><b>Battles</b> - Set up battle encounters</li>
        <li><b>Spells</b> - Create magic spells and abilities</li>
        <li><b>Monsters</b> - Design enemy monsters</li>
        <li><b>NPCs</b> - Create non-player characters</li>
        <li><b>Code Editor</b> - Edit game scripts directly</li>
        </ul>
        <p>Game data is automatically loaded from <b>js/app.js</b> when the editor starts.</p>
        </body>
        </html>
        """
        
        info_label = QLabel(info_text)
        info_label.setWordWrap(True)
        info_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        main_layout.addWidget(info_label)
        
        # Add some space
        main_layout.addStretch()
        
        # Add the tab
        self.tab_widget.addTab(main_tab, "Home")
    
    def create_editor_tabs(self):
        """Create editor tabs for different game elements."""
        # Check if the modules exist before creating tabs
        try:
            # Character editor tab
            character_tab = CharacterEditorTab(self.game_data)
            self.tab_widget.addTab(character_tab, "Characters")
            
            # Item editor tab
            item_tab = ItemEditorTab(self.game_data)
            self.tab_widget.addTab(item_tab, "Items")
            
            # Map editor tab
            map_tab = MapEditorTab(self.game_data)
            self.tab_widget.addTab(map_tab, "Maps")
            
            # Battle editor tab
            battle_tab = BattleEditorTab(self.game_data)
            self.tab_widget.addTab(battle_tab, "Battles")
            
            # Spell editor tab
            spell_tab = SpellEditorTab(self.game_data)
            self.tab_widget.addTab(spell_tab, "Spells")
            
            # Monster editor tab
            monster_tab = MonsterEditorTab(self.game_data)
            self.tab_widget.addTab(monster_tab, "Monsters")
            
            # NPC editor tab
            npc_tab = NPCEditorTab(self.game_data)
            self.tab_widget.addTab(npc_tab, "NPCs")
            
            # Code editor tab
            self.code_editor = CodeEditorTab()
            self.tab_widget.addTab(self.code_editor, "Code Editor")
        except (NameError, AttributeError):
            # Fall back to a simpler character editor if modules don't exist
            self.create_character_editor_tab()
    
    def create_character_editor_tab(self):
        """Create a simplified character editor tab."""
        char_tab = QWidget()
        char_layout = QHBoxLayout(char_tab)
        
        # Create a left panel for character list
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_panel.setMaximumWidth(300)
        
        list_label = QLabel("Character List")
        list_label.setStyleSheet("font-weight: bold;")
        
        char_list = QTreeView()
        
        left_layout.addWidget(list_label)
        left_layout.addWidget(char_list)
        
        # Create a right panel for character details
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        
        details_label = QLabel("Character Details")
        details_label.setStyleSheet("font-weight: bold;")
        
        editor = QTextEdit()
        editor.setPlaceholderText("Character details will appear here")
        
        right_layout.addWidget(details_label)
        right_layout.addWidget(editor)
        
        # Add panels to layout
        char_layout.addWidget(left_panel)
        char_layout.addWidget(right_panel)
        
        self.tab_widget.addTab(char_tab, "Character Editor")
    
    def setup_menus(self):
        """Set up the application menus."""
        # File menu
        file_menu = self.menuBar().addMenu("&File")
        
        # New project action
        new_action = QAction("&New Project", self)
        new_action.setShortcut("Ctrl+N")
        new_action.triggered.connect(self.new_project)
        file_menu.addAction(new_action)
        
        # Save action
        save_action = QAction("&Save", self)
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self.save_game_data)
        file_menu.addAction(save_action)
        
        # Exit action
        exit_action = QAction("E&xit", self)
        exit_action.setShortcut("Alt+F4")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Edit menu
        edit_menu = self.menuBar().addMenu("&Edit")
        
        # Preferences action
        prefs_action = QAction("&Preferences", self)
        prefs_action.triggered.connect(self.show_preferences)
        edit_menu.addAction(prefs_action)
        
        # Help menu
        help_menu = self.menuBar().addMenu("&Help")
        
        # About action
        about_action = QAction("&About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def new_project(self):
        """Create a new project."""
        # Check if there are unsaved changes
        if self.game_data.has_changes():
            reply = QMessageBox.question(
                self, 
                "Unsaved Changes",
                "You have unsaved changes. Do you want to save before creating a new project?",
                QMessageBox.StandardButton.Save | QMessageBox.StandardButton.Discard | QMessageBox.StandardButton.Cancel
            )
            
            if reply == QMessageBox.StandardButton.Save:
                self.save_game_data()
            elif reply == QMessageBox.StandardButton.Cancel:
                return
        
        # Reset the game data
        self.game_data = GameDataManager()
        
        # Update the UI
        self.update_editor_tabs()
        self.statusBar().showMessage("New project created", 3000)
    
    def save_game_data(self):
        """Save the game data."""
        # If we have a js file path, save to that path
        app_js_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "js", "app.js")
        
        if os.path.exists(app_js_path):
            # Save the game data
            success = self.game_data.save_to_file(app_js_path)
            
            if success:
                self.statusBar().showMessage("Game data saved successfully", 3000)
            else:
                self.statusBar().showMessage("Failed to save game data", 3000)
                QMessageBox.warning(
                    self,
                    "Error Saving Game Data",
                    "Failed to save game data."
                )
        else:
            # Ask for a file path
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "Save Game Data",
                "",
                "JavaScript Files (*.js)"
            )
            
            if file_path:
                success = self.game_data.save_to_file(file_path)
                
                if success:
                    self.statusBar().showMessage("Game data saved successfully", 3000)
                else:
                    self.statusBar().showMessage("Failed to save game data", 3000)
                    QMessageBox.warning(
                        self,
                        "Error Saving Game Data",
                        "Failed to save game data."
                    )
    
    def show_preferences(self):
        """Show the preferences dialog."""
        QMessageBox.information(
            self,
            "Preferences",
            "Preferences dialog not implemented yet."
        )
    
    def show_about(self):
        """Show the about dialog."""
        QMessageBox.about(
            self,
            "About OpenFF Game Editor",
            "OpenFF Game Editor\n\nA tool for editing game data for OpenFF."
        )
    
    def load_game_data(self):
        """Load game data from js/app.js."""
        print("Loading game data...")
        
        # Define the path to app.js
        app_js_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "js", "app.js")
        
        # Check if the file exists
        if os.path.exists(app_js_path):
            # Load the game data
            success = self.game_data.load_from_file(app_js_path)
            
            if success:
                # Check if we're using default characters
                if self.game_data.using_default_characters:
                    self.statusBar().showMessage("Using default character data", 3000)
                    # Display message in a non-blocking way
                    QApplication.processEvents()
                    # Use a single-button message box that doesn't block the application flow
                    msg_box = QMessageBox(self)
                    msg_box.setWindowTitle("Using Default Characters")
                    msg_box.setText("The editor could not extract character data from your app.js file. "
                                   "This can happen because of minification or different code structure. "
                                   "Default characters have been created for you to edit.\n\n"
                                   "Any changes you make will be saved correctly.")
                    msg_box.setIcon(QMessageBox.Icon.Information)
                    msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
                    # Show non-modal message box
                    msg_box.setModal(False)
                    msg_box.show()
                else:
                    self.statusBar().showMessage("Game data loaded successfully", 3000)
                
                # Update the editor tabs with the loaded data
                self.update_editor_tabs()
            else:
                self.statusBar().showMessage("Failed to load game data", 3000)
                msg_box = QMessageBox(self)
                msg_box.setWindowTitle("Error Loading Game Data")
                msg_box.setText(f"Failed to load game data from {app_js_path}. Check the file format.")
                msg_box.setIcon(QMessageBox.Icon.Warning)
                msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
                msg_box.setModal(False)
                msg_box.show()
        else:
            self.statusBar().showMessage("app.js not found", 3000)
            msg_box = QMessageBox(self)
            msg_box.setWindowTitle("File Not Found")
            msg_box.setText(f"Could not find js/app.js at {app_js_path}. Default game data will be used.")
            msg_box.setIcon(QMessageBox.Icon.Warning)
            msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
            msg_box.setModal(False)
            msg_box.show()
    
    def update_editor_tabs(self):
        """Update all editor tabs with the loaded game data."""
        # Update each tab that has an update_data method
        for i in range(self.tab_widget.count()):
            tab = self.tab_widget.widget(i)
            if hasattr(tab, "update_data") and callable(tab.update_data):
                tab.update_data() 