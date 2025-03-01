import os
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QListWidget, 
                           QGroupBox, QFormLayout, QLabel, QLineEdit, 
                           QSpinBox, QComboBox, QPushButton, QScrollArea,
                           QGridLayout)
from PyQt6.QtCore import Qt, QSize, QUrl, QByteArray
from PyQt6.QtGui import QPixmap, QPainter, QColor, QBrush, QPen, QIcon
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEngineScript
from PyQt6.QtWebChannel import QWebChannel
import json

from .map_web_channel import MapWebChannel

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
        
        # Flag to indicate if we're using the old grid or the new PixiJS view
        self.using_pixi = True
        
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
        self.tileset_combo.currentTextChanged.connect(self.on_tileset_changed)
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
        
        # Map grid/web view container
        self.map_box = QGroupBox("Map Editor")
        self.map_layout = QVBoxLayout()
        
        if self.using_pixi:
            # Initialize web channel for communication with JavaScript
            self.web_channel = QWebChannel()
            self.map_handler = MapWebChannel()
            self.map_handler.tileUpdated.connect(self.on_web_tile_updated)
            self.web_channel.registerObject("mapHandler", self.map_handler)
            
            # Create a web view for the PixiJS map editor
            self.web_view = QWebEngineView()
            self.web_view.page().setWebChannel(self.web_channel)
            
            # Get the absolute path to the HTML file
            current_dir = os.path.dirname(os.path.abspath(__file__))
            html_path = os.path.join(current_dir, "pixi_map_editor.html")
            self.web_view.load(QUrl.fromLocalFile(html_path))
            
            # Connect JavaScript communication
            self.web_view.loadFinished.connect(self.on_web_view_loaded)
            
            # Add the web view to the layout
            self.map_layout.addWidget(self.web_view)
        else:
            # Create the traditional grid view (as a fallback)
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
        
    def on_web_view_loaded(self, success):
        """Handle web view loaded event."""
        if success and self.current_map:
            # Initialize the map in the web view
            self.init_pixi_map()
            
            # Set up JavaScript communication with web channel
            self.web_view.page().runJavaScript("""
                // Set up the connection to the Qt WebChannel
                if (typeof qt !== 'undefined' && typeof qt.webChannelTransport !== 'undefined') {
                    new QWebChannel(qt.webChannelTransport, function(channel) {
                        window.mapHandler = channel.objects.mapHandler;
                        
                        // Override the tile click event to use the web channel
                        document.addEventListener('tileClicked', function(e) {
                            var detail = JSON.parse(e.detail);
                            if (window.mapHandler) {
                                window.mapHandler.tileClicked(detail.x, detail.y, detail.type);
                            }
                        });
                    });
                }
            """)
    
    def on_web_tile_updated(self, x, y, tile_type):
        """Handle tile update from the web view."""
        if not self.current_map:
            return
        
        # Make sure the map has a tiles array
        if 'tiles' not in self.current_map:
            self.current_map['tiles'] = [[0 for _ in range(self.current_map['width'])] for _ in range(self.current_map['height'])]
        
        # Update the tile in the data structure
        if 0 <= y < len(self.current_map['tiles']) and 0 <= x < len(self.current_map['tiles'][y]):
            self.current_map['tiles'][y][x] = tile_type
    
    def init_pixi_map(self):
        """Initialize the PixiJS map with the current map data."""
        if not self.current_map or not self.using_pixi:
            return
            
        # Prepare map data for the web view
        map_data = {
            'width': self.current_map['width'],
            'height': self.current_map['height'],
            'tileset': self.current_map['tileset'],
            'tiles': [[0 for _ in range(self.current_map['width'])] for _ in range(self.current_map['height'])]
        }
        
        # If the map has tile data, use it
        if 'tiles' in self.current_map:
            map_data['tiles'] = self.current_map['tiles']
            
        # Send the map data to the web view
        message = json.dumps({"action": "init_map", "data": map_data})
        js_code = f"receiveMessageFromPython('{message}');"
        self.web_view.page().runJavaScript(js_code)
    
    def on_tileset_changed(self, tileset_name):
        """Handle tileset change."""
        if self.current_map:
            self.current_map['tileset'] = tileset_name
            
            if self.using_pixi:
                # Update the tileset in the web view
                message = json.dumps({"action": "load_tileset", "data": {"tileset": tileset_name}})
                js_code = f"receiveMessageFromPython('{message}');"
                self.web_view.page().runJavaScript(js_code)
        
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
            
            if self.using_pixi:
                # Initialize the PixiJS map
                self.init_pixi_map()
            else:
                # Create the traditional map grid
                self.create_map_grid()
            
            # Enable the details
            self.enable_details(True)
            
    def set_current_tile_type(self, tile_type):
        """Set the current tile type for painting."""
        self.current_tile_type = tile_type
        
        if self.using_pixi:
            # Update the current tile type in the web view
            message = json.dumps({"action": "set_tile_type", "data": {"tileType": tile_type}})
            js_code = f"receiveMessageFromPython('{message}');"
            self.web_view.page().runJavaScript(js_code)
            
    def on_size_changed(self):
        """Handle change of map size."""
        if not self.current_map:
            return
            
        # Update the map size
        self.current_map['width'] = self.width_spin.value()
        self.current_map['height'] = self.height_spin.value()
        
        if self.using_pixi:
            # Resize the map in the web view
            message = json.dumps({"action": "resize_map", "data": {"width": self.current_map["width"], "height": self.current_map["height"]}})
            js_code = f"receiveMessageFromPython('{message}');"
            self.web_view.page().runJavaScript(js_code)
        else:
            # Recreate the traditional map grid
            self.create_map_grid()
        
    def create_map_grid(self):
        """Create the grid of tiles for the map."""
        # This is used only when not using PixiJS
        if self.using_pixi:
            return
            
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
                # Get tile type if available
                tile_type = 0
                if 'tiles' in self.current_map and y < len(self.current_map['tiles']) and x < len(self.current_map['tiles'][y]):
                    tile_type = self.current_map['tiles'][y][x]
                
                # Create a tile button
                tile_button = TileButton(x, y, tile_type)
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
        
        # Update map tile data
        if 'tiles' not in self.current_map:
            self.current_map['tiles'] = [[0 for _ in range(self.current_map['width'])] for _ in range(self.current_map['height'])]
        
        if y < len(self.current_map['tiles']) and x < len(self.current_map['tiles'][y]):
            self.current_map['tiles'][y][x] = self.current_tile_type
        
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
            'tileset': "town",
            'tiles': [[0 for _ in range(20)] for _ in range(15)]
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
        
        # If using PixiJS, get the tile data from the web view
        if self.using_pixi:
            # Ask the web view for the current tile data
            self.web_view.page().runJavaScript(
                "JSON.stringify(mapGrid.map(row => row.map(tile => tile.tileData.type)))",
                self.update_map_tiles
            )
        
        # Update the UI
        self.update_data()
        
        # Reselect the map
        for i in range(self.map_list.count()):
            if self.map_list.item(i).text() == self.current_map['name']:
                self.map_list.setCurrentRow(i)
                break
    
    def update_map_tiles(self, tiles_json):
        """Update map tiles from JSON string."""
        if tiles_json and self.current_map:
            try:
                tiles = json.loads(tiles_json)
                self.current_map['tiles'] = tiles
            except json.JSONDecodeError:
                print("Error decoding tile data from PixiJS")
                
    def save_changes(self):
        """Save all changes to the game data."""
        # This would be called from the main window
        return self.game_data.save_to_file() 