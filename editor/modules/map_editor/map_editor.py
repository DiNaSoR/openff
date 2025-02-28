import os
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QListWidget, 
                           QGroupBox, QFormLayout, QLabel, QLineEdit, 
                           QSpinBox, QComboBox, QPushButton, QScrollArea,
                           QGridLayout)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QPixmap, QPainter, QColor, QBrush, QPen, QIcon

class TileButton(QPushButton):
    """Custom button for map tiles."""
    
    def __init__(self, x, y, tile_type=0, parent=None):
        super().__init__(parent)
        self.x = x
        self.y = y
        self.tile_type = tile_type
        self.setFixedSize(32, 32)
        self.setCheckable(True)
        self.update_appearance()
        
    def update_appearance(self):
        """Update the button appearance based on tile type."""
        # Define colors for different tile types
        colors = {
            0: QColor(0, 128, 0),    # Grass
            1: QColor(139, 69, 19),  # Dirt
            2: QColor(0, 0, 255),    # Water
            3: QColor(128, 128, 128), # Stone
            4: QColor(210, 180, 140), # Sand
            5: QColor(0, 0, 0)       # Wall
        }
        
        # Create a pixmap for the tile
        pixmap = QPixmap(32, 32)
        painter = QPainter(pixmap)
        
        # Fill with the tile color
        color = colors.get(self.tile_type, QColor(255, 255, 255))
        painter.fillRect(0, 0, 32, 32, color)
        
        # Draw a border
        painter.setPen(QPen(QColor(0, 0, 0)))
        painter.drawRect(0, 0, 31, 31)
        
        painter.end()
        
        # Set the pixmap as the button's icon (convert to QIcon first)
        self.setIcon(QIcon(pixmap))
        self.setIconSize(QSize(32, 32))

class MapEditorTab(QWidget):
    """Tab for editing game maps with visual elements."""
    
    def __init__(self, game_data):
        super().__init__()
        self.game_data = game_data
        self.current_map = None
        self.current_tile_type = 0
        self.map_tiles = []
        
        self.init_ui()
        
    def init_ui(self):
        """Initialize the user interface."""
        # Main layout
        main_layout = QHBoxLayout(self)
        
        # Left side - Map list and details
        left_layout = QVBoxLayout()
        
        # Map list
        self.map_list = QListWidget()
        self.map_list.currentItemChanged.connect(self.on_map_selected)
        left_layout.addWidget(QLabel("Maps:"))
        left_layout.addWidget(self.map_list)
        
        # Add/Remove buttons
        button_layout = QHBoxLayout()
        self.add_button = QPushButton("Add Map")
        self.add_button.clicked.connect(self.add_map)
        self.remove_button = QPushButton("Remove Map")
        self.remove_button.clicked.connect(self.remove_map)
        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.remove_button)
        left_layout.addLayout(button_layout)
        
        # Map details
        self.details_box = QGroupBox("Map Details")
        details_layout = QFormLayout()
        
        # Name field
        self.name_edit = QLineEdit()
        details_layout.addRow("Name:", self.name_edit)
        
        # Width field
        self.width_spin = QSpinBox()
        self.width_spin.setRange(10, 100)
        self.width_spin.valueChanged.connect(self.on_size_changed)
        details_layout.addRow("Width:", self.width_spin)
        
        # Height field
        self.height_spin = QSpinBox()
        self.height_spin.setRange(10, 100)
        self.height_spin.valueChanged.connect(self.on_size_changed)
        details_layout.addRow("Height:", self.height_spin)
        
        # Tileset field
        self.tileset_combo = QComboBox()
        self.tileset_combo.addItems(["town", "castle", "forest", "dungeon"])
        details_layout.addRow("Tileset:", self.tileset_combo)
        
        # Save button
        self.save_button = QPushButton("Save Changes")
        self.save_button.clicked.connect(self.save_map)
        details_layout.addRow("", self.save_button)
        
        self.details_box.setLayout(details_layout)
        left_layout.addWidget(self.details_box)
        
        # Right side - Map editor
        right_layout = QVBoxLayout()
        
        # Tile palette
        self.palette_box = QGroupBox("Tile Palette")
        palette_layout = QHBoxLayout()
        
        # Create tile buttons for the palette
        for i in range(6):  # 6 tile types
            tile_button = TileButton(0, 0, i)
            tile_button.clicked.connect(lambda checked, tile_type=i: self.set_current_tile_type(tile_type))
            palette_layout.addWidget(tile_button)
            
        self.palette_box.setLayout(palette_layout)
        right_layout.addWidget(self.palette_box)
        
        # Map grid
        self.map_box = QGroupBox("Map Editor")
        self.map_layout = QVBoxLayout()
        
        # Create a scroll area for the map
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        
        # Create a widget to hold the map grid
        self.map_widget = QWidget()
        self.grid_layout = QGridLayout(self.map_widget)
        self.grid_layout.setSpacing(0)
        self.scroll_area.setWidget(self.map_widget)
        
        self.map_layout.addWidget(self.scroll_area)
        self.map_box.setLayout(self.map_layout)
        right_layout.addWidget(self.map_box)
        
        # Add layouts to main layout
        main_layout.addLayout(left_layout, 1)
        main_layout.addLayout(right_layout, 2)
        
        # Disable details until a map is selected
        self.enable_details(False)
        
    def update_data(self):
        """Update the UI with the latest game data."""
        # Clear the list
        self.map_list.clear()
        
        # Add maps to the list
        for map_data in self.game_data.maps:
            self.map_list.addItem(map_data['name'])
            
        # Clear the current selection
        self.current_map = None
        self.enable_details(False)
        
    def on_map_selected(self, current, previous):
        """Handle selection of a map in the list."""
        if not current:
            self.current_map = None
            self.enable_details(False)
            return
            
        # Get the selected map
        map_name = current.text()
        self.current_map = self.game_data.get_map_by_name(map_name)
        
        if self.current_map:
            # Update the details
            self.name_edit.setText(self.current_map['name'])
            self.width_spin.setValue(self.current_map['width'])
            self.height_spin.setValue(self.current_map['height'])
            
            # Set the tileset
            tileset_index = self.tileset_combo.findText(self.current_map['tileset'])
            if tileset_index >= 0:
                self.tileset_combo.setCurrentIndex(tileset_index)
                
            # Create the map grid
            self.create_map_grid()
            
            # Enable the details
            self.enable_details(True)
            
    def on_size_changed(self):
        """Handle change of map size."""
        if not self.current_map:
            return
            
        # Update the map size
        self.current_map['width'] = self.width_spin.value()
        self.current_map['height'] = self.height_spin.value()
        
        # Recreate the map grid
        self.create_map_grid()
        
    def create_map_grid(self):
        """Create the grid of tiles for the map."""
        # Clear the existing grid
        self.map_tiles = []
        
        # Remove all widgets from the grid layout
        while self.grid_layout.count():
            item = self.grid_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
                
        # Create new tile buttons
        for y in range(self.current_map['height']):
            row = []
            for x in range(self.current_map['width']):
                # Create a tile button
                tile_button = TileButton(x, y)
                tile_button.clicked.connect(lambda checked, x=x, y=y: self.on_tile_clicked(x, y))
                self.grid_layout.addWidget(tile_button, y, x)
                row.append(tile_button)
            self.map_tiles.append(row)
            
    def on_tile_clicked(self, x, y):
        """Handle click on a map tile."""
        if not self.current_map or y >= len(self.map_tiles) or x >= len(self.map_tiles[y]):
            return
            
        # Set the tile type
        tile_button = self.map_tiles[y][x]
        tile_button.tile_type = self.current_tile_type
        tile_button.update_appearance()
        
    def set_current_tile_type(self, tile_type):
        """Set the current tile type for painting."""
        self.current_tile_type = tile_type
        
    def enable_details(self, enabled):
        """Enable or disable the details widgets."""
        self.details_box.setEnabled(enabled)
        self.palette_box.setEnabled(enabled)
        self.map_box.setEnabled(enabled)
        self.remove_button.setEnabled(enabled)
        
    def add_map(self):
        """Add a new map."""
        # Create a new map with default values
        new_map = {
            'name': "New Map",
            'width': 20,
            'height': 15,
            'tileset': "town"
        }
        
        # Add to the game data
        self.game_data.maps.append(new_map)
        
        # Update the UI
        self.update_data()
        
        # Select the new map
        for i in range(self.map_list.count()):
            if self.map_list.item(i).text() == new_map['name']:
                self.map_list.setCurrentRow(i)
                break
                
    def remove_map(self):
        """Remove the selected map."""
        if not self.current_map:
            return
            
        # Remove from the game data
        self.game_data.maps.remove(self.current_map)
        
        # Update the UI
        self.update_data()
        
    def save_map(self):
        """Save changes to the selected map."""
        if not self.current_map:
            return
            
        # Update the map with the form values
        self.current_map['name'] = self.name_edit.text()
        self.current_map['width'] = self.width_spin.value()
        self.current_map['height'] = self.height_spin.value()
        self.current_map['tileset'] = self.tileset_combo.currentText()
        
        # Update the UI
        self.update_data()
        
        # Reselect the map
        for i in range(self.map_list.count()):
            if self.map_list.item(i).text() == self.current_map['name']:
                self.map_list.setCurrentRow(i)
                break
                
    def save_changes(self):
        """Save all changes to the game data."""
        # This would be called from the main window
        return self.game_data.save_to_file() 