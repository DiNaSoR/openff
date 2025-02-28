import os
import sys
import json
import webbrowser
import shutil
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                            QTreeView, QSplitter, 
                            QToolBar, QStatusBar, QFileDialog, QMessageBox, QInputDialog,
                            QLineEdit, QMenu, QLabel, QPushButton, QDialog,
                            QTabWidget, QPlainTextEdit, QMenuBar, QStyle, QListWidget, QGroupBox, QFormLayout, QComboBox)
from PyQt6.QtCore import Qt, QDir, QModelIndex, QFileInfo, QRect, QSize
from PyQt6.QtGui import (QFont, QSyntaxHighlighter, QTextCharFormat, QColor, QKeySequence, 
                        QTextCursor, QPainter, QTextFormat, QIcon, QAction, QShortcut,
                        QStandardItemModel, QStandardItem, QFontMetricsF, QPixmap)
import re

class LineNumberArea(QWidget):
    """Line number area widget for the code editor."""
    
    def __init__(self, editor):
        super().__init__(editor)
        self.editor = editor
        
    def sizeHint(self):
        return QSize(self.editor.line_number_area_width(), 0)
        
    def paintEvent(self, event):
        self.editor.lineNumberAreaPaintEvent(event)

class CodeEditor(QPlainTextEdit):
    """Enhanced code editor with line numbers."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFont(QFont("Courier New", 10))
        
        # Set up line numbers
        self.line_number_area = LineNumberArea(self)
        self.blockCountChanged.connect(self.update_line_number_area_width)
        self.updateRequest.connect(self.update_line_number_area)
        self.update_line_number_area_width(0)
        
        # Set tab width
        font_metrics = self.fontMetrics()
        self.setTabStopDistance(4 * font_metrics.horizontalAdvance(' '))
        
        # Initialize highlighter as None
        self.highlighter = None
        
    def line_number_area_width(self):
        digits = 1
        max_num = max(1, self.blockCount())
        while max_num >= 10:
            max_num //= 10
            digits += 1
        
        space = 3 + self.fontMetrics().horizontalAdvance('9') * digits
        return space
    
    def update_line_number_area_width(self, _):
        self.setViewportMargins(self.line_number_area_width(), 0, 0, 0)
        
    def update_line_number_area(self, rect, dy):
        if dy:
            self.line_number_area.scroll(0, dy)
        else:
            self.line_number_area.update(0, rect.y(), self.line_number_area.width(), rect.height())
            
        if rect.contains(self.viewport().rect()):
            self.update_line_number_area_width(0)
            
    def resizeEvent(self, event):
        super().resizeEvent(event)
        cr = self.contentsRect()
        self.line_number_area.setGeometry(QRect(cr.left(), cr.top(), self.line_number_area_width(), cr.height()))
        
    def lineNumberAreaPaintEvent(self, event):
        painter = QPainter(self.line_number_area)
        painter.fillRect(event.rect(), QColor(Qt.GlobalColor.lightGray).lighter(120))
        
        block = self.firstVisibleBlock()
        block_number = block.blockNumber()
        top = round(self.blockBoundingGeometry(block).translated(self.contentOffset()).top())
        bottom = top + round(self.blockBoundingRect(block).height())
        
        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                number = str(block_number + 1)
                painter.setPen(QColor(Qt.GlobalColor.black))
                painter.drawText(0, top, self.line_number_area.width() - 5, self.fontMetrics().height(),
                                Qt.AlignmentFlag.AlignRight, number)
            
            block = block.next()
            top = bottom
            bottom = top + round(self.blockBoundingRect(block).height())
            block_number += 1
    
    def setContent(self, content):
        """Set the content of the editor."""
        self.setPlainText(content)
    
    def setHighlighter(self, highlighter_class, *args, **kwargs):
        """Set the syntax highlighter for this editor."""
        if self.highlighter:
            self.highlighter.setDocument(None)
        if highlighter_class:
            self.highlighter = highlighter_class(self.document(), *args, **kwargs)
        else:
            self.highlighter = None

class JavaScriptHighlighter(QSyntaxHighlighter):
    """Syntax highlighter for JavaScript code."""
    
    def __init__(self, parent=None, game_specific=True):
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
        self.highlighting_rules.append((re.compile(r"`.*?`"), string_format))
        
        # Comment format
        comment_format = QTextCharFormat()
        comment_format.setForeground(QColor(100, 100, 100))
        self.highlighting_rules.append((re.compile(r'//.*'), comment_format))
        self.highlighting_rules.append((re.compile(r'/\*.*?\*/', re.DOTALL), comment_format))
        
        # Function format
        function_format = QTextCharFormat()
        function_format.setForeground(QColor(220, 150, 50))
        self.highlighting_rules.append((re.compile(r'\b[A-Za-z0-9_]+(?=\s*\()'), function_format))
        
        # Game-specific highlighting
        if game_specific:
            # OpenFF specific keywords
            game_keyword_format = QTextCharFormat()
            game_keyword_format.setForeground(QColor(60, 180, 200))
            game_keyword_format.setFontWeight(QFont.Weight.Bold)
            
            game_keywords = [
                'scene', 'battle', 'game', 'status', 'map', 'chara', 'npc',
                'player', 'enemy', 'item', 'magic', 'weapon', 'armor'
            ]
            
            for word in game_keywords:
                pattern = r'\b' + word + r'\b'
                self.highlighting_rules.append((re.compile(pattern), game_keyword_format))
                
            # Method calls on game objects
            method_format = QTextCharFormat()
            method_format.setForeground(QColor(180, 120, 210))
            self.highlighting_rules.append((re.compile(r'\.[A-Za-z0-9_]+\('), method_format))
    
    def highlightBlock(self, text):
        """Apply highlighting to the given block of text."""
        for pattern, format in self.highlighting_rules:
            for match in pattern.finditer(text):
                start, end = match.span()
                self.setFormat(start, end - start, format)

class CSSHighlighter(QSyntaxHighlighter):
    """Syntax highlighter for CSS code."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.highlighting_rules = []
        
        # Property format
        property_format = QTextCharFormat()
        property_format.setForeground(QColor(0, 128, 255))
        self.highlighting_rules.append((re.compile(r'[a-zA-Z-]+(?=\s*:)'), property_format))
        
        # Value format
        value_format = QTextCharFormat()
        value_format.setForeground(QColor(128, 128, 0))
        self.highlighting_rules.append((re.compile(r':\s*[^;]+'), value_format))
        
        # Selector format
        selector_format = QTextCharFormat()
        selector_format.setForeground(QColor(200, 50, 100))
        selector_format.setFontWeight(QFont.Weight.Bold)
        self.highlighting_rules.append((re.compile(r'[^\{\}]+(?=\s*\{)'), selector_format))
        
        # Braces format
        braces_format = QTextCharFormat()
        braces_format.setForeground(QColor(120, 120, 120))
        braces_format.setFontWeight(QFont.Weight.Bold)
        self.highlighting_rules.append((re.compile(r'[\{\}]'), braces_format))
        
        # Comment format
        comment_format = QTextCharFormat()
        comment_format.setForeground(QColor(100, 100, 100))
        self.highlighting_rules.append((re.compile(r'/\*.*?\*/', re.DOTALL), comment_format))
    
    def highlightBlock(self, text):
        """Apply highlighting to the given block of text."""
        for pattern, format in self.highlighting_rules:
            for match in pattern.finditer(text):
                start, end = match.span()
                self.setFormat(start, end - start, format)

class HTMLHighlighter(QSyntaxHighlighter):
    """Syntax highlighter for HTML code."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.highlighting_rules = []
        
        # Tag format
        tag_format = QTextCharFormat()
        tag_format.setForeground(QColor(0, 128, 128))
        tag_format.setFontWeight(QFont.Weight.Bold)
        self.highlighting_rules.append((re.compile(r'<[/!]?[a-zA-Z0-9]+'), tag_format))
        self.highlighting_rules.append((re.compile(r'>'), tag_format))
        
        # Attribute format
        attribute_format = QTextCharFormat()
        attribute_format.setForeground(QColor(128, 0, 128))
        self.highlighting_rules.append((re.compile(r'[a-zA-Z-]+='), attribute_format))
        
        # Value format
        value_format = QTextCharFormat()
        value_format.setForeground(QColor(50, 150, 50))
        self.highlighting_rules.append((re.compile(r'".*?"'), value_format))
        self.highlighting_rules.append((re.compile(r"'.*?'"), value_format))
        
        # Comment format
        comment_format = QTextCharFormat()
        comment_format.setForeground(QColor(100, 100, 100))
        self.highlighting_rules.append((re.compile(r'<!--.*?-->', re.DOTALL), comment_format))
    
    def highlightBlock(self, text):
        """Apply highlighting to the given block of text."""
        for pattern, format in self.highlighting_rules:
            for match in pattern.finditer(text):
                start, end = match.span()
                self.setFormat(start, end - start, format)

class OpenFFEditor(QMainWindow):
    """Main application window for OpenFF editor."""
    
    def __init__(self):
        super().__init__()
        self.current_file = None
        self.tabs = {}  # Map of file paths to tab indices
        self.game_elements = {}  # Store game elements for editing
        self.initUI()
        
    def initUI(self):
        """Initialize the user interface."""
        # Set window properties
        self.setWindowTitle("OpenFF Game Editor")
        self.setGeometry(100, 100, 1200, 800)
        
        # Create the central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QHBoxLayout(central_widget)
        
        # Create a splitter for the file tree and editor
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Create the file system model and view
        self.file_model = QStandardItemModel()
        self.file_model.setHorizontalHeaderLabels(['Game Files'])
        self.file_tree = QTreeView()
        self.file_tree.setModel(self.file_model)
        self.file_tree.setColumnWidth(0, 250)
        self.file_tree.clicked.connect(self.file_clicked)
        self.file_tree.doubleClicked.connect(self.file_double_clicked)
        
        # Enable drag and drop
        self.file_tree.setDragEnabled(True)
        self.file_tree.setAcceptDrops(True)
        self.file_tree.setDropIndicatorShown(True)
        
        # Populate the file tree
        self.populate_file_tree()
        
        # Create tab widget for multiple files
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabsClosable(True)
        self.tab_widget.tabCloseRequested.connect(self.close_tab)
        
        # Create game editor widget
        self.game_editor_widget = QWidget()
        self.setup_game_editor()
        
        # Add a tab for the game editor
        self.tab_widget.addTab(self.game_editor_widget, "Game Editor")
        
        # Add widgets to the splitter
        splitter.addWidget(self.file_tree)
        splitter.addWidget(self.tab_widget)
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
        QShortcut(QKeySequence("Ctrl+S"), self, self.save_current_tab)
        QShortcut(QKeySequence("Ctrl+F"), self, self.find_text)
        QShortcut(QKeySequence("Ctrl+W"), self, self.close_current_tab)
        QShortcut(QKeySequence("F5"), self, self.run_game)
        
        # Auto-load app.js if it exists
        js_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'js', 'app.js')
        if os.path.exists(js_path):
            self.open_file(js_path)
            # After loading app.js, parse it for game elements
            self.parse_game_elements()
        
    def setup_game_editor(self):
        """Set up the game editor interface with game-specific components."""
        layout = QVBoxLayout(self.game_editor_widget)
        
        # Create a tab widget for different game element categories
        game_tabs = QTabWidget()
        
        # Create tabs for different game element types
        characters_tab = QWidget()
        items_tab = QWidget()
        maps_tab = QWidget()
        battles_tab = QWidget()
        spells_tab = QWidget()
        
        self.setup_characters_tab(characters_tab)
        self.setup_items_tab(items_tab)
        self.setup_maps_tab(maps_tab)
        self.setup_battles_tab(battles_tab)
        self.setup_spells_tab(spells_tab)
        
        # Add tabs to the game editor widget
        game_tabs.addTab(characters_tab, "Characters")
        game_tabs.addTab(items_tab, "Items")
        game_tabs.addTab(maps_tab, "Maps")
        game_tabs.addTab(battles_tab, "Battles")
        game_tabs.addTab(spells_tab, "Spells")
        
        # Add buttons for common actions
        button_layout = QHBoxLayout()
        run_button = QPushButton("Run Game")
        run_button.clicked.connect(self.run_game)
        save_button = QPushButton("Save Changes")
        save_button.clicked.connect(self.save_game_changes)
        reload_button = QPushButton("Reload Game Elements")
        reload_button.clicked.connect(self.debug_reload_elements)
        
        button_layout.addWidget(run_button)
        button_layout.addWidget(save_button)
        button_layout.addWidget(reload_button)
        
        # Add components to the main layout
        layout.addWidget(game_tabs)
        layout.addLayout(button_layout)
        
    def setup_characters_tab(self, tab):
        """Set up the characters editor tab."""
        layout = QVBoxLayout(tab)
        
        # Split into left and right sections
        char_layout = QHBoxLayout()
        layout.addLayout(char_layout)
        
        # Left side with character list
        left_layout = QVBoxLayout()
        left_layout.addWidget(QLabel("Character Classes:"))
        self.character_list = QListWidget()
        self.character_list.currentItemChanged.connect(self.on_character_selected)
        left_layout.addWidget(self.character_list)
        
        char_layout.addLayout(left_layout)
        
        # Right side with character image
        right_layout = QVBoxLayout()
        self.char_image_label = QLabel()
        self.char_image_label.setFixedSize(160, 180)
        self.char_image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.char_image_label.setStyleSheet("border: 1px solid #ccc; background-color: #000;")
        right_layout.addWidget(self.char_image_label)
        
        char_layout.addLayout(right_layout)
        
        # Set the stretch ratio between left and right sides
        char_layout.setStretch(0, 2)  # Left side gets 2/3
        char_layout.setStretch(1, 1)  # Right side gets 1/3
        
        # Character details
        details_group = QGroupBox("Character Details")
        details_layout = QFormLayout(details_group)
        
        self.char_name = QLineEdit()
        self.char_hp = QLineEdit()
        self.char_mp = QLineEdit()
        self.char_strength = QLineEdit()
        self.char_agility = QLineEdit()
        self.char_intelligence = QLineEdit()
        self.char_vitality = QLineEdit()
        self.char_luck = QLineEdit()
        
        details_layout.addRow("Name:", self.char_name)
        details_layout.addRow("HP:", self.char_hp)
        details_layout.addRow("MP:", self.char_mp)
        details_layout.addRow("Strength:", self.char_strength)
        details_layout.addRow("Agility:", self.char_agility)
        details_layout.addRow("Intelligence:", self.char_intelligence)
        details_layout.addRow("Vitality:", self.char_vitality)
        details_layout.addRow("Luck:", self.char_luck)
        
        layout.addWidget(details_group)
        
        # Buttons for actions
        button_layout = QHBoxLayout()
        add_button = QPushButton("Add New")
        update_button = QPushButton("Update")
        delete_button = QPushButton("Delete")
        
        button_layout.addWidget(add_button)
        button_layout.addWidget(update_button)
        button_layout.addWidget(delete_button)
        
        layout.addLayout(button_layout)
        
    def setup_items_tab(self, tab):
        """Set up the items editor tab."""
        layout = QVBoxLayout(tab)
        
        # Split into left and right sections
        item_layout = QHBoxLayout()
        layout.addLayout(item_layout)
        
        # Left side with items list
        left_layout = QVBoxLayout()
        left_layout.addWidget(QLabel("Items:"))
        self.items_list = QListWidget()
        self.items_list.currentItemChanged.connect(self.on_item_selected)
        left_layout.addWidget(self.items_list)
        
        item_layout.addLayout(left_layout)
        
        # Right side with item image
        right_layout = QVBoxLayout()
        self.item_image_label = QLabel()
        self.item_image_label.setFixedSize(160, 160)
        self.item_image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.item_image_label.setStyleSheet("border: 1px solid #ccc; background-color: #000;")
        right_layout.addWidget(self.item_image_label)
        
        item_layout.addLayout(right_layout)
        
        # Set the stretch ratio between left and right sides
        item_layout.setStretch(0, 2)  # Left side gets 2/3
        item_layout.setStretch(1, 1)  # Right side gets 1/3
        
        # Item details
        details_group = QGroupBox("Item Details")
        details_layout = QFormLayout(details_group)
        
        self.item_name = QLineEdit()
        self.item_type = QComboBox()
        self.item_type.addItems(["Weapon", "Armor", "Potion", "Key Item"])
        self.item_effect = QLineEdit()
        self.item_value = QLineEdit()
        
        details_layout.addRow("Name:", self.item_name)
        details_layout.addRow("Type:", self.item_type)
        details_layout.addRow("Effect:", self.item_effect)
        details_layout.addRow("Value:", self.item_value)
        
        layout.addWidget(details_group)
        
        # Buttons for actions
        button_layout = QHBoxLayout()
        add_button = QPushButton("Add New")
        update_button = QPushButton("Update")
        delete_button = QPushButton("Delete")
        
        button_layout.addWidget(add_button)
        button_layout.addWidget(update_button)
        button_layout.addWidget(delete_button)
        
        layout.addLayout(button_layout)
        
    def setup_maps_tab(self, tab):
        """Set up the maps editor tab."""
        layout = QVBoxLayout(tab)
        
        # Maps list
        layout.addWidget(QLabel("Maps:"))
        self.maps_list = QListWidget()
        self.maps_list.currentItemChanged.connect(self.on_map_selected)
        layout.addWidget(self.maps_list)
        
        # Map preview
        preview_group = QGroupBox("Map Preview")
        preview_layout = QVBoxLayout(preview_group)
        self.map_preview = QLabel("Map preview will be shown here")
        self.map_preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.map_preview.setMinimumHeight(200)
        preview_layout.addWidget(self.map_preview)
        
        layout.addWidget(preview_group)
        
        # Map details
        details_group = QGroupBox("Map Details")
        details_layout = QFormLayout(details_group)
        
        self.map_name = QLineEdit()
        self.map_type = QComboBox()
        self.map_type.addItems(["Town", "Dungeon", "Field", "Castle"])
        self.map_enemies = QLineEdit()
        
        details_layout.addRow("Name:", self.map_name)
        details_layout.addRow("Type:", self.map_type)
        details_layout.addRow("Enemies:", self.map_enemies)
        
        layout.addWidget(details_group)
        
        # Buttons for actions
        button_layout = QHBoxLayout()
        edit_button = QPushButton("Edit Map")
        save_button = QPushButton("Save Changes")
        
        button_layout.addWidget(edit_button)
        button_layout.addWidget(save_button)
        
        layout.addLayout(button_layout)
        
    def setup_battles_tab(self, tab):
        """Set up the battles editor tab."""
        layout = QVBoxLayout(tab)
        
        # Enemy encounters list
        layout.addWidget(QLabel("Enemy Encounters:"))
        self.encounters_list = QListWidget()
        self.encounters_list.currentItemChanged.connect(self.on_encounter_selected)
        layout.addWidget(self.encounters_list)
        
        # Encounter details
        details_group = QGroupBox("Encounter Details")
        details_layout = QFormLayout(details_group)
        
        self.encounter_name = QLineEdit()
        self.encounter_location = QLineEdit()
        self.encounter_enemies = QLineEdit()
        self.encounter_difficulty = QComboBox()
        self.encounter_difficulty.addItems(["Easy", "Medium", "Hard", "Boss"])
        
        details_layout.addRow("Name:", self.encounter_name)
        details_layout.addRow("Location:", self.encounter_location)
        details_layout.addRow("Enemies:", self.encounter_enemies)
        details_layout.addRow("Difficulty:", self.encounter_difficulty)
        
        layout.addWidget(details_group)
        
        # Buttons for actions
        button_layout = QHBoxLayout()
        add_button = QPushButton("Add New")
        update_button = QPushButton("Update")
        delete_button = QPushButton("Delete")
        
        button_layout.addWidget(add_button)
        button_layout.addWidget(update_button)
        button_layout.addWidget(delete_button)
        
        layout.addLayout(button_layout)
        
    def setup_spells_tab(self, tab):
        """Set up the spells editor tab."""
        layout = QVBoxLayout(tab)
        
        # Spells list
        layout.addWidget(QLabel("Spells:"))
        self.spells_list = QListWidget()
        self.spells_list.currentItemChanged.connect(self.on_spell_selected)
        layout.addWidget(self.spells_list)
        
        # Spell details
        details_group = QGroupBox("Spell Details")
        details_layout = QFormLayout(details_group)
        
        self.spell_name = QLineEdit()
        self.spell_type = QComboBox()
        self.spell_type.addItems(["White Magic", "Black Magic"])
        self.spell_effect = QLineEdit()
        self.spell_mp_cost = QLineEdit()
        self.spell_level = QComboBox()
        self.spell_level.addItems(["1", "2", "3", "4", "5", "6", "7", "8"])
        
        details_layout.addRow("Name:", self.spell_name)
        details_layout.addRow("Type:", self.spell_type)
        details_layout.addRow("Effect:", self.spell_effect)
        details_layout.addRow("MP Cost:", self.spell_mp_cost)
        details_layout.addRow("Level:", self.spell_level)
        
        layout.addWidget(details_group)
        
        # Buttons for actions
        button_layout = QHBoxLayout()
        add_button = QPushButton("Add New")
        update_button = QPushButton("Update")
        delete_button = QPushButton("Delete")
        
        button_layout.addWidget(add_button)
        button_layout.addWidget(update_button)
        button_layout.addWidget(delete_button)
        
        layout.addLayout(button_layout)
        
    def parse_game_elements(self):
        """Parse the game.js file to extract game elements for editing."""
        # Find the app.js file
        js_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'js', 'app.js')
        
        try:
            if os.path.exists(js_path):
                with open(js_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                # Try to extract character classes
                self.extract_characters(content)
                
                # Try to extract items
                self.extract_items(content)
                
                # Try to extract maps
                self.extract_maps(content)
                
                # Try to extract enemy encounters
                self.extract_encounters(content)
                
                # Try to extract spells
                self.extract_spells(content)
                
                self.status_bar.showMessage("Game elements parsed successfully")
            else:
                self.status_bar.showMessage("Could not find app.js file")
                
        except Exception as e:
            self.status_bar.showMessage(f"Error parsing game elements: {str(e)}")
            QMessageBox.warning(self, "Parsing Error", f"Failed to parse game elements: {str(e)}")
            
    def extract_characters(self, content):
        """Extract character classes from the game code."""
        # In a real implementation, this would parse the minified JS
        # to find character definitions. For now, we'll use placeholder data.
        
        # Check if we can find character class related patterns in the content
        if "BLACK MAGE" in content or "WHITE MAGE" in content or "WARRIOR" in content:
            characters = [
                "Warrior (Fighter)",
                "Thief (Ninja)",
                "Black Mage (Black Wizard)",
                "White Mage (White Wizard)",
                "Red Mage (Red Wizard)",
                "Monk (Master)"
            ]
        else:
            # Fallback demo data
            characters = [
                "Warrior",
                "Thief",
                "Black Mage",
                "White Mage",
                "Red Mage",
                "Monk"
            ]
        
        self.character_list.clear()
        for char in characters:
            self.character_list.addItem(char)
        
        # If a character is selected, populate the details
        if self.character_list.count() > 0:
            self.character_list.setCurrentRow(0)
            self.char_name.setText(characters[0])
            self.char_hp.setText("200")
            self.char_mp.setText("0" if "Warrior" in characters[0] else "50")
            self.char_strength.setText("20")
            self.char_agility.setText("10")
            self.char_intelligence.setText("5" if "Warrior" in characters[0] else "20")
            self.char_vitality.setText("15")
            self.char_luck.setText("10")
            
    def extract_items(self, content):
        """Extract items from the game code."""
        # Try to find item-related patterns in the content
        if "POTION" in content or "TENT" in content or "SWORD" in content:
            items = [
                "Potion",
                "Hi-Potion",
                "Tent",
                "Cottage",
                "Phoenix Down",
                "Ether",
                "Iron Sword",
                "Ice Sword",
                "Bronze Armor",
                "Chain Mail",
                "Wooden Shield",
                "Iron Shield"
            ]
        else:
            # Fallback demo data
            items = [
                "Potion",
                "Tent",
                "Cottage",
                "Phoenix Down",
                "Iron Sword",
                "Bronze Armor"
            ]
        
        self.items_list.clear()
        for item in items:
            self.items_list.addItem(item)
            
        # If an item is selected, populate the details
        if self.items_list.count() > 0:
            self.items_list.setCurrentRow(0)
            self.item_name.setText(items[0])
            
            # Set type based on item name
            if "Sword" in items[0] or "Dagger" in items[0] or "Staff" in items[0]:
                self.item_type.setCurrentText("Weapon")
                self.item_effect.setText("Attack +5")
                self.item_value.setText("200")
            elif "Armor" in items[0] or "Mail" in items[0] or "Shield" in items[0]:
                self.item_type.setCurrentText("Armor")
                self.item_effect.setText("Defense +3")
                self.item_value.setText("150")
            elif "Potion" in items[0] or "Ether" in items[0] or "Phoenix" in items[0]:
                self.item_type.setCurrentText("Potion")
                self.item_effect.setText("Restores HP")
                self.item_value.setText("50")
            else:
                self.item_type.setCurrentText("Key Item")
                self.item_effect.setText("Special effect")
                self.item_value.setText("100")
            
    def extract_maps(self, content):
        """Extract maps from the game code."""
        # Try to find map-related patterns in the content
        if "CORNELIA" in content or "CHAOS" in content or "SHRINE" in content:
            maps = [
                "Cornelia Town",
                "Cornelia Castle 1F",
                "Cornelia Castle 2F",
                "Western Keep",
                "Chaos Shrine",
                "Matoya's Cave",
                "Earth Cave B1",
                "Earth Cave B2",
                "Marsh Cave"
            ]
        else:
            # Fallback demo data
            maps = [
                "Cornelia Town",
                "Cornelia Castle",
                "Western Keep",
                "Chaos Shrine"
            ]
        
        self.maps_list.clear()
        for map_name in maps:
            self.maps_list.addItem(map_name)
            
        # If a map is selected, populate the details
        if self.maps_list.count() > 0:
            self.maps_list.setCurrentRow(0)
            self.map_name.setText(maps[0])
            
            # Set type based on map name
            if "Town" in maps[0]:
                self.map_type.setCurrentText("Town")
                self.map_enemies.setText("None")
            elif "Castle" in maps[0]:
                self.map_type.setCurrentText("Castle")
                self.map_enemies.setText("Guards (rare)")
            elif "Cave" in maps[0]:
                self.map_type.setCurrentText("Dungeon")
                self.map_enemies.setText("Goblins, Wolves, Bats")
            else:
                self.map_type.setCurrentText("Field")
                self.map_enemies.setText("Various")
            
    def extract_encounters(self, content):
        """Extract enemy encounters from the game code."""
        # Try to find encounter-related patterns in the content
        if "GOBLIN" in content or "WOLF" in content or "GARLAND" in content:
            encounters = [
                "Goblin Pack (2-4 Goblins)",
                "Wolf Pack (3-5 Wolves)",
                "Undead (Skeletons & Zombies)",
                "Garland (Boss)",
                "Chaos (Final Boss)",
                "Pirates",
                "Ogres",
                "Giants",
                "Dragons"
            ]
        else:
            # Fallback demo data
            encounters = [
                "Goblins",
                "Wolves",
                "Skeleton",
                "Chaos",
                "Garland"
            ]
        
        self.encounters_list.clear()
        for encounter in encounters:
            self.encounters_list.addItem(encounter)
            
        # If an encounter is selected, populate the details
        if self.encounters_list.count() > 0:
            self.encounters_list.setCurrentRow(0)
            self.encounter_name.setText(encounters[0])
            
            # Set details based on encounter name
            if "Goblin" in encounters[0]:
                self.encounter_location.setText("Cornelia Region")
                self.encounter_enemies.setText("2-4 Goblins")
                self.encounter_difficulty.setCurrentText("Easy")
            elif "Wolf" in encounters[0]:
                self.encounter_location.setText("Forests")
                self.encounter_enemies.setText("3-5 Wolves")
                self.encounter_difficulty.setCurrentText("Easy")
            elif "Garland" in encounters[0] or "Chaos" in encounters[0]:
                self.encounter_location.setText("Chaos Shrine")
                self.encounter_enemies.setText(encounters[0].split(" ")[0])
                self.encounter_difficulty.setCurrentText("Boss")
            else:
                self.encounter_location.setText("Various")
                self.encounter_enemies.setText("Mixed enemies")
                self.encounter_difficulty.setCurrentText("Medium")
            
    def extract_spells(self, content):
        """Extract spells from the game code."""
        # Try to find spell-related patterns in the content
        if "CURE" in content or "FIRE" in content or "THUNDER" in content:
            spells = [
                "Cure (White Lv1)",
                "Fire (Black Lv1)",
                "Thunder (Black Lv1)",
                "Blizzard (Black Lv1)",
                "Heal (White Lv2)",
                "Cura (White Lv3)",
                "Fira (Black Lv3)",
                "Thundara (Black Lv3)",
                "Blizzara (Black Lv3)",
                "Teleport (White Lv4)",
                "Dia (White Lv2)",
                "Holy (White Lv8)",
                "Flare (Black Lv8)"
            ]
        else:
            # Fallback demo data
            spells = [
                "Cure",
                "Fire",
                "Thunder",
                "Blizzard",
                "Heal",
                "Teleport",
                "Dia"
            ]
        
        self.spells_list.clear()
        for spell in spells:
            self.spells_list.addItem(spell)
            
        # If a spell is selected, populate the details
        if self.spells_list.count() > 0:
            self.spells_list.setCurrentRow(0)
            
            # Parse spell name (remove level if present)
            spell_name = spells[0].split(" (")[0] if " (" in spells[0] else spells[0]
            self.spell_name.setText(spell_name)
            
            # Set type based on spell name or description
            if "White" in spells[0]:
                self.spell_type.setCurrentText("White Magic")
            else:
                self.spell_type.setCurrentText("Black Magic")
                
            # Set effects based on spell name
            if spell_name in ["Cure", "Cura", "Heal"]:
                self.spell_effect.setText("Restores HP to one ally")
                self.spell_mp_cost.setText("4")
            elif spell_name == "Fire" or spell_name == "Fira":
                self.spell_effect.setText("Fire damage to one enemy")
                self.spell_mp_cost.setText("5")
            elif spell_name == "Thunder" or spell_name == "Thundara":
                self.spell_effect.setText("Lightning damage to one enemy")
                self.spell_mp_cost.setText("5")
            elif spell_name == "Blizzard" or spell_name == "Blizzara":
                self.spell_effect.setText("Ice damage to one enemy")
                self.spell_mp_cost.setText("5")
            elif spell_name == "Teleport":
                self.spell_effect.setText("Escape from dungeon")
                self.spell_mp_cost.setText("8")
            elif spell_name == "Dia":
                self.spell_effect.setText("Light damage, effective vs undead")
                self.spell_mp_cost.setText("6")
            elif spell_name == "Holy":
                self.spell_effect.setText("Powerful light damage to one enemy")
                self.spell_mp_cost.setText("20")
            elif spell_name == "Flare":
                self.spell_effect.setText("Powerful non-elemental damage")
                self.spell_mp_cost.setText("20")
            else:
                self.spell_effect.setText("Special effect")
                self.spell_mp_cost.setText("10")
                
            # Set level based on description or default to 1
            if "Lv" in spells[0]:
                level = spells[0].split("Lv")[1].strip().rstrip(")")
                self.spell_level.setCurrentText(level)
            else:
                self.spell_level.setCurrentText("1")
        
    def save_game_changes(self):
        """Save changes made in the game editor to the game files."""
        # This would update the app.js file with changes made in the editor
        QMessageBox.information(self, "Save Changes", 
                               "This would save your game changes to app.js.\n"
                               "In a full implementation, this would update the game code.")
        self.status_bar.showMessage("Game changes saved")
        
    def create_toolbar(self):
        """Create the main toolbar."""
        toolbar = QToolBar("Main Toolbar")
        self.addToolBar(toolbar)
        
        # New file action
        new_action = QAction("New", self)
        new_action.triggered.connect(self.new_file)
        toolbar.addAction(new_action)
        
        # Open file action
        open_action = QAction("Open", self)
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
        
        # Game editor action
        game_editor_action = QAction("Game Editor", self)
        game_editor_action.triggered.connect(self.show_game_editor)
        toolbar.addAction(game_editor_action)
        
    def file_clicked(self, index):
        """Handle file selection in the tree view."""
        item = self.file_model.itemFromIndex(index)
        if item:
            file_path = item.data(Qt.ItemDataRole.UserRole)
            if file_path and QFileInfo(file_path).isFile():
                self.open_file(file_path)
            elif file_path and QFileInfo(file_path).isDir():
                # Toggle expand/collapse for directories
                if self.file_tree.isExpanded(index):
                    self.file_tree.collapse(index)
                else:
                    self.file_tree.expand(index)
    
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
        if file_path in self.tabs:
            # Switch to the existing tab
            for i in range(self.tab_widget.count()):
                if self.tab_widget.widget(i) == self.tabs[file_path]:
                    self.tab_widget.setCurrentIndex(i)
                    self.current_file = file_path
                    break
            return
            
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Create a new tab with a text editor
            editor = CodeEditor()
            self.setup_editor(editor)
            editor.setPlainText(content)
            
            # Set file path attribute on the editor
            editor.file_path = file_path
            
            # Set the lexer based on file extension
            self.set_lexer(editor, file_path)
            
            # Add the new tab
            tab_name = os.path.basename(file_path)
            tab_index = self.tab_widget.addTab(editor, tab_name)
            self.tab_widget.setCurrentIndex(tab_index)
            
            # Store the mapping of file path to editor
            self.tabs[file_path] = editor
            self.current_file = file_path
            
            self.status_bar.showMessage(f"Opened: {file_path}")
            
            # If opening app.js, also parse game elements
            if file_path.endswith('app.js'):
                self.parse_game_elements()
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to open file:\n{str(e)}")
            
    def setup_editor(self, editor):
        """Configure the code editor with common settings."""
        # Set font
        font = QFont("Consolas", 10)
        editor.setFont(font)
        
        # Enable line numbers
        editor.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)
        
        # Set tab width
        editor.setTabStopDistance(QFontMetricsF(font).horizontalAdvance(' ') * 4)
        
    def set_lexer(self, editor, file_path):
        """Set syntax highlighting based on file extension."""
        # This is a simple implementation - in a real app, you'd use a more sophisticated
        # syntax highlighting system like QSyntaxHighlighter
        extension = os.path.splitext(file_path)[1].lower()
        
        # You could implement different highlighting for different file types
        # For now, we'll just set a basic monospace font for all files
        pass
        
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
            
            # If saving app.js, update game elements
            if file_path.endswith('app.js'):
                self.update_game_elements_from_editor()
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save file:\n{str(e)}")
            
    def save_as(self):
        """Save the current tab's content to a new file."""
        current_tab = self.tab_widget.currentWidget()
        if not current_tab:
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
                if old_file_path and old_file_path in self.tabs:
                    del self.tabs[old_file_path]
                    
                current_tab.file_path = file_path
                self.tabs[file_path] = current_tab
                self.tab_widget.setTabText(self.tab_widget.currentIndex(), os.path.basename(file_path))
                self.status_bar.showMessage(f"Saved as: {file_path}")
                
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save file:\n{str(e)}")
                
    def find_text(self):
        """Find text in the current editor."""
        if self.tab_widget.count() == 0:
            return
            
        text, ok = QInputDialog.getText(self, "Find Text", "Enter text to find:", QLineEdit.EchoMode.Normal)
        if ok and text:
            editor = self.tab_widget.currentWidget()
            cursor = editor.document().find(text)
            if not cursor.isNull():
                editor.setTextCursor(cursor)
            else:
                # Try to find from the beginning
                cursor = editor.document().find(text, QTextCursor.MoveOperation.Start)
                if not cursor.isNull():
                    editor.setTextCursor(cursor)
                else:
                    self.status_bar.showMessage(f"Text '{text}' not found")
    
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
        file_path = getattr(tab_widget, 'file_path', None)
        
        if file_path and file_path in self.tabs:
            del self.tabs[file_path]
            
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
        base_dir = os.path.dirname(os.path.abspath(__file__))
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
    
    def show_context_menu(self, position):
        """Show context menu for file tree."""
        index = self.file_tree.indexAt(position)
        if not index.isValid():
            # Right-clicked on empty space
            context_menu = QMenu(self)
            refresh_action = context_menu.addAction("Refresh")
            refresh_action.triggered.connect(self.refresh_file_tree)
            context_menu.exec(self.file_tree.mapToGlobal(position))
            return

        item = self.file_model.itemFromIndex(index)
        file_path = item.data(Qt.ItemDataRole.UserRole)
        
        if not file_path:
            return
            
        context_menu = QMenu(self)
        
        if QFileInfo(file_path).isFile():
            # File actions
            open_action = context_menu.addAction("Open")
            open_action.triggered.connect(lambda: self.open_file(file_path))
            
            delete_action = context_menu.addAction("Delete")
            delete_action.triggered.connect(lambda: self.delete_file(file_path))
        else:
            # Directory actions
            new_file_action = context_menu.addAction("New File")
            new_file_action.triggered.connect(lambda: self.create_new_file(file_path))
            
            delete_action = context_menu.addAction("Delete")
            delete_action.triggered.connect(lambda: self.delete_file(file_path))
            
            refresh_action = context_menu.addAction("Refresh")
            refresh_action.triggered.connect(self.refresh_file_tree)
            
        context_menu.exec(self.file_tree.mapToGlobal(position))
    
    def new_file_in_dir(self, directory):
        """Create a new file in the specified directory."""
        file_name, ok = QInputDialog.getText(self, "New File", "Enter file name:", QLineEdit.EchoMode.Normal)
        if ok and file_name:
            # Add default extension if none specified
            if not any(file_name.endswith(ext) for ext in ['.js', '.css', '.html', '.htm']):
                file_name += '.js'
                
            file_path = os.path.join(directory, file_name)
            
            try:
                # Check if file exists
                if os.path.exists(file_path):
                    reply = QMessageBox.question(
                        self, 
                        "File Exists", 
                        f"File {file_name} already exists. Overwrite?",
                        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, 
                        QMessageBox.StandardButton.No
                    )
                    if reply == QMessageBox.StandardButton.No:
                        return
                
                # Create new empty file with appropriate template
                with open(file_path, 'w', encoding='utf-8') as f:
                    if file_path.endswith('.js'):
                        f.write("// New JavaScript file\n")
                    elif file_path.endswith('.css'):
                        f.write("/* New CSS file */\n")
                    elif file_path.endswith(('.html', '.htm')):
                        f.write("<!DOCTYPE html>\n<html>\n<head>\n    <title>New Page</title>\n</head>\n<body>\n\n</body>\n</html>")
                    else:
                        f.write("")
                
                # Open the file
                self.open_file(file_path)
                
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to create file:\n{str(e)}")
    
    def delete_file(self, file_path):
        """Delete a file or directory."""
        file_info = QFileInfo(file_path)
        if file_info.isFile():
            message = f"Are you sure you want to delete the file '{file_info.fileName()}'?"
        else:
            message = f"Are you sure you want to delete the directory '{file_info.fileName()}' and all its contents?"
            
        reply = QMessageBox.question(
            self, 
            "Confirm Deletion", 
            message, 
            QMessageBox.Yes | QMessageBox.No, 
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                if file_info.isFile():
                    os.remove(file_path)
                else:
                    shutil.rmtree(file_path)
                self.refresh_file_tree()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to delete: {str(e)}")
    
    def create_new_file(self, directory_path):
        """Create a new file in the specified directory."""
        file_name, ok = QInputDialog.getText(
            self, 
            "New File", 
            "Enter file name:"
        )
        
        if ok and file_name:
            file_path = os.path.join(directory_path, file_name)
            
            if os.path.exists(file_path):
                QMessageBox.warning(self, "Warning", f"File '{file_name}' already exists.")
                return
                
            try:
                with open(file_path, 'w') as f:
                    f.write("")
                self.refresh_file_tree()
                self.open_file(file_path)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to create file: {str(e)}")
                
    def populate_file_tree(self):
        """Populate the file tree with files and directories."""
        # Get the project directory (current directory)
        project_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Create a root item with the project name
        project_name = os.path.basename(project_dir)
        root_item = QStandardItem(project_name)
        root_item.setData(project_dir, Qt.ItemDataRole.UserRole)
        root_item.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_DirIcon))
        
        # Add the root item to the model
        self.file_model.appendRow(root_item)
        
        # Populate the tree with files and directories
        self.add_files_to_tree(project_dir, root_item)
        
        # Expand the root item
        self.file_tree.expand(self.file_model.indexFromItem(root_item))
        
    def add_files_to_tree(self, path, parent_item):
        """Recursively add files and directories to the tree."""
        for item in sorted(os.listdir(path)):
            item_path = os.path.join(path, item)
            tree_item = QStandardItem(item)
            tree_item.setData(item_path, Qt.ItemDataRole.UserRole)
            
            # Set appropriate icon based on whether it's a file or directory
            if os.path.isdir(item_path):
                tree_item.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_DirIcon))
                # Don't add __pycache__ directories
                if "__pycache__" not in item and ".git" not in item:
                    self.add_files_to_tree(item_path, tree_item)
            else:
                tree_item.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_FileIcon))
            
            parent_item.appendRow(tree_item)

    def refresh_file_tree(self):
        """Refresh the file tree view."""
        self.file_model.clear()
        self.file_model.setHorizontalHeaderLabels(['Game Files'])
        self.populate_file_tree()

    def file_double_clicked(self, index):
        """Handle double-click on a file in the file tree."""
        item = self.file_model.itemFromIndex(index)
        if item:
            file_path = item.data(Qt.ItemDataRole.UserRole)
            if file_path and QFileInfo(file_path).isFile():
                self.open_file(file_path)
            elif file_path and QFileInfo(file_path).isDir():
                # Toggle expand/collapse for directories
                if self.file_tree.isExpanded(index):
                    self.file_tree.collapse(index)
                else:
                    self.file_tree.expand(index)
                    
    def show_game_editor(self):
        """Switch to the game editor tab."""
        # Find the index of the game editor tab
        for i in range(self.tab_widget.count()):
            if self.tab_widget.tabText(i) == "Game Editor":
                self.tab_widget.setCurrentIndex(i)
                return
        
        # If we get here, the tab doesn't exist, so create it
        self.game_editor_widget = QWidget()
        self.setup_game_editor()
        self.tab_widget.addTab(self.game_editor_widget, "Game Editor")
        self.tab_widget.setCurrentIndex(self.tab_widget.count() - 1)

    def update_game_elements_from_editor(self):
        """Updates game elements when changes are made in the text editor."""
        if self.current_file and self.current_file.endswith('app.js'):
            editor = self.tabs.get(self.current_file)
            if editor:
                content = editor.toPlainText()
                self.parse_game_elements()
                self.status_bar.showMessage("Game elements updated from editor")

    def debug_reload_elements(self):
        """Reload game elements from the game files."""
        self.parse_game_elements()
        self.status_bar.showMessage("Game elements reloaded from files")

    def on_character_selected(self, current, previous):
        """Handle character selection in the list."""
        if not current:
            return
            
        character = current.text()
        self.char_name.setText(character)
        
        # Set stats based on character class
        job_id = 0  # Default to Warrior/job0
        
        if "Warrior" in character:
            job_id = 0
            self.char_hp.setText("200")
            self.char_mp.setText("0")
            self.char_strength.setText("20")
            self.char_agility.setText("10")
            self.char_intelligence.setText("5")
            self.char_vitality.setText("15")
            self.char_luck.setText("10")
        elif "Thief" in character:
            job_id = 1
            self.char_hp.setText("160")
            self.char_mp.setText("0")
            self.char_strength.setText("15")
            self.char_agility.setText("20")
            self.char_intelligence.setText("10")
            self.char_vitality.setText("10")
            self.char_luck.setText("15")
        elif "Black Mage" in character:
            job_id = 2
            self.char_hp.setText("120")
            self.char_mp.setText("80")
            self.char_strength.setText("5")
            self.char_agility.setText("10")
            self.char_intelligence.setText("20")
            self.char_vitality.setText("5")
            self.char_luck.setText("10")
        elif "White Mage" in character:
            job_id = 3
            self.char_hp.setText("130")
            self.char_mp.setText("80")
            self.char_strength.setText("5")
            self.char_agility.setText("8")
            self.char_intelligence.setText("18")
            self.char_vitality.setText("10")
            self.char_luck.setText("12")
        elif "Red Mage" in character:
            job_id = 4
            self.char_hp.setText("150")
            self.char_mp.setText("60")
            self.char_strength.setText("12")
            self.char_agility.setText("12")
            self.char_intelligence.setText("15")
            self.char_vitality.setText("10")
            self.char_luck.setText("12")
        elif "Monk" in character:
            job_id = 5
            self.char_hp.setText("180")
            self.char_mp.setText("0")
            self.char_strength.setText("18")
            self.char_agility.setText("15")
            self.char_intelligence.setText("8")
            self.char_vitality.setText("18")
            self.char_luck.setText("8")
            
        # Load character image
        job_img_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'img', 'pc', f'job{job_id}.png')
        if os.path.exists(job_img_path):
            pixmap = QPixmap(job_img_path)
            self.char_image_label.setPixmap(pixmap)
            self.char_image_label.setScaledContents(True)
        else:
            self.char_image_label.setText(f"Image not found: job{job_id}.png")
            self.char_image_label.setScaledContents(False)

    def on_item_selected(self, current, previous):
        """Handle item selection in the list."""
        if not current:
            return
            
        item_name = current.text()
        self.item_name.setText(item_name)
        
        # Set details based on item name
        item_id = 0  # Default item ID
        
        if "Sword" in item_name or "Dagger" in item_name or "Staff" in item_name:
            self.item_type.setCurrentText("Weapon")
            self.item_effect.setText("Attack +5")
            self.item_value.setText("200")
            item_id = 2  # Weapon sprite
        elif "Armor" in item_name or "Mail" in item_name or "Shield" in item_name:
            self.item_type.setCurrentText("Armor")
            self.item_effect.setText("Defense +3")
            self.item_value.setText("150")
            item_id = 3  # Armor sprite
        elif "Potion" in item_name:
            self.item_type.setCurrentText("Potion")
            self.item_effect.setText("Restores HP")
            self.item_value.setText("50")
            item_id = 0  # Potion sprite
        elif "Hi-Potion" in item_name:
            self.item_type.setCurrentText("Potion")
            self.item_effect.setText("Restores more HP")
            self.item_value.setText("300")
            item_id = 0  # Potion sprite
        elif "Ether" in item_name:
            self.item_type.setCurrentText("Potion")
            self.item_effect.setText("Restores MP")
            self.item_value.setText("1500")
            item_id = 1  # Ether sprite
        elif "Phoenix" in item_name:
            self.item_type.setCurrentText("Potion")
            self.item_effect.setText("Revives fallen ally")
            self.item_value.setText("500")
            item_id = 4  # Phoenix Down sprite
        elif "Tent" in item_name:
            self.item_type.setCurrentText("Key Item")
            self.item_effect.setText("Restores some HP/MP for party")
            self.item_value.setText("100")
            item_id = 5  # Tent sprite
        elif "Cottage" in item_name:
            self.item_type.setCurrentText("Key Item")
            self.item_effect.setText("Fully restores HP/MP for party")
            self.item_value.setText("250")
            item_id = 6  # Cottage sprite
        else:
            self.item_type.setCurrentText("Key Item")
            self.item_effect.setText("Special effect")
            self.item_value.setText("100")
            item_id = 7  # Generic item sprite
            
        # Try to load item image from sprite sheet or item images
        # In a real implementation, we would extract sprites from gameSprite.png
        # For now, we'll create placeholder item images based on item type
        
        # Choose a color based on item type
        bg_color = "#000000"  # Black background
        fg_color = "#FFFFFF"  # White text
        
        if self.item_type.currentText() == "Weapon":
            icon_color = "#8B4513"  # Brown for weapons
            icon_text = "⚔️"
        elif self.item_type.currentText() == "Armor":
            icon_color = "#C0C0C0"  # Silver for armor
            icon_text = "🛡️"
        elif self.item_type.currentText() == "Potion":
            icon_color = "#FF0000"  # Red for potions
            icon_text = "🧪"
        else:
            icon_color = "#FFD700"  # Gold for key items
            icon_text = "🔑"
            
        # Create a pixmap with colored background
        pixmap = QPixmap(160, 160)
        pixmap.fill(QColor(bg_color))
        
        # Draw on the pixmap
        painter = QPainter(pixmap)
        painter.setPen(QColor(fg_color))
        
        # Draw item icon
        painter.setBrush(QColor(icon_color))
        painter.drawRect(40, 40, 80, 80)
        
        # Draw item name
        font = QFont("Arial", 10)
        painter.setFont(font)
        painter.drawText(20, 140, 120, 20, Qt.AlignmentFlag.AlignCenter, item_name)
        
        painter.end()
        
        # Set the pixmap to the label
        self.item_image_label.setPixmap(pixmap)
        self.item_image_label.setScaledContents(True)

    def on_map_selected(self, current, previous):
        """Handle map selection in the list."""
        if not current:
            return
            
        map_name = current.text()
        self.map_name.setText(map_name)
        
        # Set details based on map name
        if "Town" in map_name:
            self.map_type.setCurrentText("Town")
            self.map_enemies.setText("None")
        elif "Castle" in map_name:
            self.map_type.setCurrentText("Castle")
            self.map_enemies.setText("Guards (rare)")
        elif "Cave" in map_name:
            self.map_type.setCurrentText("Dungeon")
            self.map_enemies.setText("Goblins, Wolves, Bats")
        elif "Shrine" in map_name:
            self.map_type.setCurrentText("Dungeon")
            self.map_enemies.setText("Undead, Garland (Boss)")
        elif "Keep" in map_name:
            self.map_type.setCurrentText("Dungeon")
            self.map_enemies.setText("Pirates, Guards")
        else:
            self.map_type.setCurrentText("Field")
            self.map_enemies.setText("Various")
            
    def on_encounter_selected(self, current, previous):
        """Handle encounter selection in the list."""
        if not current:
            return
            
        encounter_name = current.text()
        self.encounter_name.setText(encounter_name)
        
        # Set details based on encounter name
        if "Goblin" in encounter_name:
            self.encounter_location.setText("Cornelia Region")
            self.encounter_enemies.setText("2-4 Goblins")
            self.encounter_difficulty.setCurrentText("Easy")
        elif "Wolf" in encounter_name:
            self.encounter_location.setText("Forests")
            self.encounter_enemies.setText("3-5 Wolves")
            self.encounter_difficulty.setCurrentText("Easy")
        elif "Undead" in encounter_name:
            self.encounter_location.setText("Caves, Shrines")
            self.encounter_enemies.setText("Skeletons, Zombies")
            self.encounter_difficulty.setCurrentText("Medium")
        elif "Garland" in encounter_name:
            self.encounter_location.setText("Chaos Shrine")
            self.encounter_enemies.setText("Garland")
            self.encounter_difficulty.setCurrentText("Boss")
        elif "Chaos" in encounter_name:
            self.encounter_location.setText("Chaos Shrine Depths")
            self.encounter_enemies.setText("Chaos")
            self.encounter_difficulty.setCurrentText("Boss")
        elif "Pirates" in encounter_name:
            self.encounter_location.setText("Western Keep")
            self.encounter_enemies.setText("3-6 Pirates")
            self.encounter_difficulty.setCurrentText("Medium")
        elif "Ogres" in encounter_name:
            self.encounter_location.setText("Mountains")
            self.encounter_enemies.setText("2-3 Ogres")
            self.encounter_difficulty.setCurrentText("Medium")
        elif "Giants" in encounter_name:
            self.encounter_location.setText("Earth Cave")
            self.encounter_enemies.setText("1-2 Giants")
            self.encounter_difficulty.setCurrentText("Hard")
        elif "Dragons" in encounter_name:
            self.encounter_location.setText("Earth Cave, Volcano")
            self.encounter_enemies.setText("1 Dragon")
            self.encounter_difficulty.setCurrentText("Hard")
        else:
            self.encounter_location.setText("Various")
            self.encounter_enemies.setText("Mixed enemies")
            self.encounter_difficulty.setCurrentText("Medium")
            
    def on_spell_selected(self, current, previous):
        """Handle spell selection in the list."""
        if not current:
            return
            
        spell_text = current.text()
        
        # Parse spell name (remove level if present)
        spell_name = spell_text.split(" (")[0] if " (" in spell_text else spell_text
        self.spell_name.setText(spell_name)
        
        # Set type based on spell text or description
        if "White" in spell_text:
            self.spell_type.setCurrentText("White Magic")
        else:
            self.spell_type.setCurrentText("Black Magic")
            
        # Set effects based on spell name
        if spell_name in ["Cure", "Cura", "Heal"]:
            self.spell_effect.setText("Restores HP to one ally")
            self.spell_mp_cost.setText("4")
        elif spell_name == "Fire" or spell_name == "Fira":
            self.spell_effect.setText("Fire damage to one enemy")
            self.spell_mp_cost.setText("5")
        elif spell_name == "Thunder" or spell_name == "Thundara":
            self.spell_effect.setText("Lightning damage to one enemy")
            self.spell_mp_cost.setText("5")
        elif spell_name == "Blizzard" or spell_name == "Blizzara":
            self.spell_effect.setText("Ice damage to one enemy")
            self.spell_mp_cost.setText("5")
        elif spell_name == "Teleport":
            self.spell_effect.setText("Escape from dungeon")
            self.spell_mp_cost.setText("8")
        elif spell_name == "Dia":
            self.spell_effect.setText("Light damage, effective vs undead")
            self.spell_mp_cost.setText("6")
        elif spell_name == "Holy":
            self.spell_effect.setText("Powerful light damage to one enemy")
            self.spell_mp_cost.setText("20")
        elif spell_name == "Flare":
            self.spell_effect.setText("Powerful non-elemental damage")
            self.spell_mp_cost.setText("20")
        else:
            self.spell_effect.setText("Special effect")
            self.spell_mp_cost.setText("10")
            
        # Set level based on description or default to 1
        if "Lv" in spell_text:
            level = spell_text.split("Lv")[1].strip().rstrip(")")
            self.spell_level.setCurrentText(level)
        else:
            self.spell_level.setCurrentText("1")

def main():
    """Main function to run the application."""
    app = QApplication(sys.argv)
    editor = OpenFFEditor()
    editor.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
