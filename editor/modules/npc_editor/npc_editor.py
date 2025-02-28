import os
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QListWidget, 
                           QGroupBox, QFormLayout, QLabel, QLineEdit, 
                           QSpinBox, QComboBox, QPushButton, QTextEdit)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap

class NPCEditorTab(QWidget):
    """Tab for editing NPCs with visual elements."""
    
    def __init__(self, game_data):
        super().__init__()
        self.game_data = game_data
        self.current_npc = None
        
        self.init_ui()
        
    def init_ui(self):
        """Initialize the user interface."""
        # Main layout
        main_layout = QHBoxLayout(self)
        
        # Left side - NPC list
        left_layout = QVBoxLayout()
        
        # NPC list
        self.npc_list = QListWidget()
        self.npc_list.currentItemChanged.connect(self.on_npc_selected)
        left_layout.addWidget(QLabel("NPCs:"))
        left_layout.addWidget(self.npc_list)
        
        # Add/Remove buttons
        button_layout = QHBoxLayout()
        self.add_button = QPushButton("Add NPC")
        self.add_button.clicked.connect(self.add_npc)
        self.remove_button = QPushButton("Remove NPC")
        self.remove_button.clicked.connect(self.remove_npc)
        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.remove_button)
        left_layout.addLayout(button_layout)
        
        # Right side - NPC details
        right_layout = QVBoxLayout()
        
        # NPC image
        self.image_box = QGroupBox("NPC Appearance")
        image_layout = QVBoxLayout()
        self.npc_image = QLabel()
        self.npc_image.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.npc_image.setMinimumSize(128, 128)
        self.npc_image.setMaximumSize(256, 256)
        self.npc_image.setScaledContents(True)
        image_layout.addWidget(self.npc_image)
        
        # Sprite selection
        sprite_layout = QHBoxLayout()
        sprite_layout.addWidget(QLabel("NPC Sprite:"))
        self.sprite_combo = QComboBox()
        self.sprite_combo.addItems([
            "npc_king", "npc_shopkeeper", "npc_oldman", "npc_garland", 
            "npc_guard", "npc_mage", "npc_child", "npc_woman"
        ])
        self.sprite_combo.currentTextChanged.connect(self.on_sprite_changed)
        sprite_layout.addWidget(self.sprite_combo)
        image_layout.addLayout(sprite_layout)
        
        # Direction selection
        direction_layout = QHBoxLayout()
        direction_layout.addWidget(QLabel("Direction:"))
        self.direction_combo = QComboBox()
        self.direction_combo.addItems([
            "down", "up", "left", "right"
        ])
        direction_layout.addWidget(self.direction_combo)
        image_layout.addLayout(direction_layout)
        
        self.image_box.setLayout(image_layout)
        right_layout.addWidget(self.image_box)
        
        # NPC basic details
        self.details_box = QGroupBox("NPC Details")
        details_layout = QFormLayout()
        
        # ID field
        self.id_edit = QLineEdit()
        details_layout.addRow("ID:", self.id_edit)
        
        # Name field
        self.name_edit = QLineEdit()
        details_layout.addRow("Name:", self.name_edit)
        
        # Map field
        self.map_combo = QComboBox()
        # We'll populate this from game data later
        details_layout.addRow("Map:", self.map_combo)
        
        # Position fields
        position_layout = QHBoxLayout()
        self.x_spin = QSpinBox()
        self.x_spin.setRange(0, 100)
        position_layout.addWidget(QLabel("X:"))
        position_layout.addWidget(self.x_spin)
        
        self.y_spin = QSpinBox()
        self.y_spin.setRange(0, 100)
        position_layout.addWidget(QLabel("Y:"))
        position_layout.addWidget(self.y_spin)
        
        details_layout.addRow("Position:", position_layout)
        
        # Save button
        self.save_button = QPushButton("Save Changes")
        self.save_button.clicked.connect(self.save_npc)
        details_layout.addRow("", self.save_button)
        
        self.details_box.setLayout(details_layout)
        right_layout.addWidget(self.details_box)
        
        # NPC dialogue/behavior
        self.behavior_box = QGroupBox("Dialogue & Behavior")
        behavior_layout = QVBoxLayout()
        
        # Dialogue
        behavior_layout.addWidget(QLabel("Dialogue:"))
        self.dialogue_edit = QTextEdit()
        self.dialogue_edit.setPlaceholderText("Enter dialogue for this NPC...")
        behavior_layout.addWidget(self.dialogue_edit)
        
        # Behavior type
        behavior_type_layout = QHBoxLayout()
        behavior_type_layout.addWidget(QLabel("Behavior Type:"))
        self.behavior_combo = QComboBox()
        self.behavior_combo.addItems([
            "Static", "Wandering", "Following Path", "Reacting to Player"
        ])
        behavior_type_layout.addWidget(self.behavior_combo)
        behavior_layout.addLayout(behavior_type_layout)
        
        self.behavior_box.setLayout(behavior_layout)
        right_layout.addWidget(self.behavior_box)
        
        # Add layouts to main layout
        main_layout.addLayout(left_layout, 1)
        main_layout.addLayout(right_layout, 2)
        
        # Disable details until an NPC is selected
        self.enable_details(False)
        
    def update_data(self):
        """Update the UI with the latest game data."""
        # Clear the list
        self.npc_list.clear()
        
        # Add NPCs to the list
        for npc in self.game_data.npcs:
            self.npc_list.addItem(npc['name'])
            
        # Update map combo
        self.map_combo.clear()
        for map_data in self.game_data.maps:
            self.map_combo.addItem(map_data['name'])
            
        # Clear the current selection
        self.current_npc = None
        self.enable_details(False)
        
    def on_npc_selected(self, current, previous):
        """Handle selection of an NPC in the list."""
        if not current:
            self.current_npc = None
            self.enable_details(False)
            return
            
        # Get the selected NPC
        npc_name = current.text()
        self.current_npc = self.game_data.get_npc_by_name(npc_name)
        
        if self.current_npc:
            # Update the details
            self.id_edit.setText(self.current_npc['id'])
            self.name_edit.setText(self.current_npc['name'])
            
            # Set map
            map_index = self.map_combo.findText(self.current_npc.get('map', ''))
            if map_index >= 0:
                self.map_combo.setCurrentIndex(map_index)
                
            # Set position
            self.x_spin.setValue(self.current_npc.get('x', 0))
            self.y_spin.setValue(self.current_npc.get('y', 0))
            
            # Set sprite
            sprite_index = self.sprite_combo.findText(self.current_npc.get('sprite', ''))
            if sprite_index >= 0:
                self.sprite_combo.setCurrentIndex(sprite_index)
                
            # Set direction
            direction_index = self.direction_combo.findText(self.current_npc.get('direction', 'down'))
            if direction_index >= 0:
                self.direction_combo.setCurrentIndex(direction_index)
                
            # Set dialogue and behavior
            self.dialogue_edit.setText(self.current_npc.get('dialogue', ''))
            self.behavior_combo.setCurrentIndex(0)  # Default to static for now
            
            # Load the NPC image
            self.load_npc_image()
            
            # Enable the details
            self.enable_details(True)
            
    def on_sprite_changed(self, sprite_name):
        """Handle change of NPC sprite."""
        if not self.current_npc:
            return
            
        # Update the NPC's sprite
        self.current_npc['sprite'] = sprite_name
            
        # Reload the NPC image
        self.load_npc_image()
        
    def load_npc_image(self):
        """Load the NPC image based on the sprite."""
        if not self.current_npc:
            return
            
        # Get the sprite path
        sprite_name = self.current_npc.get('sprite', 'npc_king')
        sprite_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 
                                  '..', '..', '..', 'img', 'pc', 'gameSprite.png')
        
        # Load the image
        pixmap = QPixmap(sprite_path)
        if pixmap.isNull():
            # If image not found, try a default
            default_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 
                                      '..', '..', '..', 'img', 'pc', 'gameSprite.png')
            pixmap = QPixmap(default_path)
            
        # Set the image
        self.npc_image.setPixmap(pixmap)
        
    def enable_details(self, enabled):
        """Enable or disable the details widgets."""
        self.details_box.setEnabled(enabled)
        self.image_box.setEnabled(enabled)
        self.behavior_box.setEnabled(enabled)
        self.remove_button.setEnabled(enabled)
        
    def add_npc(self):
        """Add a new NPC."""
        # Create a new NPC with default values
        new_npc = {
            'id': 'npc_new',
            'name': "New NPC",
            'map': self.game_data.maps[0]['name'] if self.game_data.maps else "",
            'x': 5,
            'y': 5,
            'direction': 'down',
            'sprite': 'npc_king',
            'dialogue': "Hello adventurer!"
        }
        
        # Add to the game data
        self.game_data.npcs.append(new_npc)
        
        # Update the UI
        self.update_data()
        
        # Select the new NPC
        for i in range(self.npc_list.count()):
            if self.npc_list.item(i).text() == new_npc['name']:
                self.npc_list.setCurrentRow(i)
                break
                
    def remove_npc(self):
        """Remove the selected NPC."""
        if not self.current_npc:
            return
            
        # Remove from the game data
        self.game_data.npcs.remove(self.current_npc)
        
        # Update the UI
        self.update_data()
        
    def save_npc(self):
        """Save changes to the selected NPC."""
        if not self.current_npc:
            return
            
        # Update the NPC with the form values
        self.current_npc['id'] = self.id_edit.text()
        self.current_npc['name'] = self.name_edit.text()
        self.current_npc['map'] = self.map_combo.currentText()
        self.current_npc['x'] = self.x_spin.value()
        self.current_npc['y'] = self.y_spin.value()
        self.current_npc['sprite'] = self.sprite_combo.currentText()
        self.current_npc['direction'] = self.direction_combo.currentText()
        self.current_npc['dialogue'] = self.dialogue_edit.toPlainText()
        
        # Update the UI
        self.update_data()
        
        # Reselect the NPC
        for i in range(self.npc_list.count()):
            if self.npc_list.item(i).text() == self.current_npc['name']:
                self.npc_list.setCurrentRow(i)
                break
                
    def save_changes(self):
        """Save all changes to the game data."""
        return self.game_data.save_to_file() 