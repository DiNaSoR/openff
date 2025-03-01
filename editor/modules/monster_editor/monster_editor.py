import os
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QListWidget, 
                           QGroupBox, QFormLayout, QLabel, QLineEdit, 
                           QSpinBox, QComboBox, QPushButton, QListWidgetItem)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QPixmap, QColor

class MonsterEditorTab(QWidget):
    """Tab for editing game monsters with visual elements."""
    
    def __init__(self, game_data):
        super().__init__()
        self.game_data = game_data
        self.current_monster = None
        
        self.init_ui()
        
    def init_ui(self):
        """Initialize the user interface."""
        # Main layout
        main_layout = QHBoxLayout(self)
        
        # Left side - Monster list
        left_layout = QVBoxLayout()
        
        # Monster list
        self.monster_list = QListWidget()
        self.monster_list.currentItemChanged.connect(self.on_monster_selected)
        left_layout.addWidget(QLabel("Monsters:"))
        left_layout.addWidget(self.monster_list)
        
        # Add/Remove buttons
        button_layout = QHBoxLayout()
        self.add_button = QPushButton("Add Monster")
        self.add_button.clicked.connect(self.add_monster)
        self.remove_button = QPushButton("Remove Monster")
        self.remove_button.clicked.connect(self.remove_monster)
        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.remove_button)
        left_layout.addLayout(button_layout)
        
        # Right side - Monster details
        right_layout = QVBoxLayout()
        
        # Image display
        self.image_box = QGroupBox("Monster Image")
        image_layout = QVBoxLayout()
        
        self.monster_image = QLabel()
        self.monster_image.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.monster_image.setMinimumSize(128, 128)
        self.monster_image.setMaximumSize(256, 256)
        self.monster_image.setStyleSheet("background-color: #444; border: 1px solid #666; border-radius: 4px;")
        self.monster_image.setScaledContents(False)  # Don't stretch, preserve aspect ratio
        image_layout.addWidget(self.monster_image)
        
        # Add sprite info label
        self.sprite_info_label = QLabel("No sprite loaded")
        self.sprite_info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        image_layout.addWidget(self.sprite_info_label)
        
        # ID control for easy editing of ID/sprite
        id_layout = QHBoxLayout()
        id_layout.addWidget(QLabel("Monster ID:"))
        self.id_edit = QLineEdit()
        self.id_edit.setMaxLength(2)  # Limit to 2 chars for IDs like 00, 01, 2b, etc.
        self.id_edit.textChanged.connect(self.on_id_changed)
        id_layout.addWidget(self.id_edit)
        image_layout.addLayout(id_layout)
        
        self.image_box.setLayout(image_layout)
        right_layout.addWidget(self.image_box)
        
        # Monster details
        self.details_box = QGroupBox("Monster Details")
        details_layout = QFormLayout()
        
        # Name field
        self.name_edit = QLineEdit()
        details_layout.addRow("Name:", self.name_edit)
        
        # HP field
        self.hp_spin = QSpinBox()
        self.hp_spin.setRange(1, 9999)
        details_layout.addRow("HP:", self.hp_spin)
        
        # Power field
        self.power_spin = QSpinBox()
        self.power_spin.setRange(1, 999)
        details_layout.addRow("Power:", self.power_spin)
        
        # EXP field
        self.exp_spin = QSpinBox()
        self.exp_spin.setRange(0, 9999)
        details_layout.addRow("EXP:", self.exp_spin)
        
        # Save button
        self.save_button = QPushButton("Save Changes")
        self.save_button.clicked.connect(self.save_monster)
        details_layout.addRow("", self.save_button)
        
        self.details_box.setLayout(details_layout)
        right_layout.addWidget(self.details_box)
        
        # Battle/AI Settings
        self.battle_box = QGroupBox("Battle Settings")
        battle_layout = QFormLayout()
        
        # Attack types
        self.attack_combo = QComboBox()
        self.attack_combo.addItems([
            "Physical", "Fire", "Ice", "Thunder", "Status"
        ])
        battle_layout.addRow("Attack Type:", self.attack_combo)
        
        # Weakness
        self.weakness_combo = QComboBox()
        self.weakness_combo.addItems([
            "None", "Fire", "Ice", "Thunder", "Physical"
        ])
        battle_layout.addRow("Weakness:", self.weakness_combo)
        
        # AI behavior 
        self.behavior_combo = QComboBox()
        self.behavior_combo.addItems([
            "Aggressive", "Defensive", "Random", "Smart"
        ])
        battle_layout.addRow("AI Behavior:", self.behavior_combo)
        
        self.battle_box.setLayout(battle_layout)
        right_layout.addWidget(self.battle_box)
        
        # Add layouts to main layout
        main_layout.addLayout(left_layout, 1)
        main_layout.addLayout(right_layout, 2)
        
        # Disable details until a monster is selected
        self.enable_details(False)
        
    def update_data(self):
        """Update the UI with the latest game data."""
        # Clear the list
        self.monster_list.clear()
        
        # Add monsters to the list
        for i, monster in enumerate(self.game_data.monsters):
            # Format: Name (ID: XX)
            name = monster.get('name', 'Unknown Monster')
            monster_id = monster.get('id', '??')
            
            # Create a nicely formatted display string
            display_text = f"{name} (ID: {monster_id})"
            
            # Create the item and store the monster ID as user data
            item = QListWidgetItem(display_text)
            item.setData(Qt.ItemDataRole.UserRole, monster_id)
            self.monster_list.addItem(item)
            
            # Debug: Print the data stored in each list item
            print(f"Added list item #{i+1}: Display={display_text}, Data={monster_id}")
            
        # Clear the current selection
        self.current_monster = None
        self.enable_details(False)
        
        # Show a count of monsters found
        print(f"Updated monster list with {len(self.game_data.monsters)} monsters")
        
    def debug_monster_list(self):
        """Debug method to print all monsters in the game data."""
        print("==== MONSTER LIST DEBUG ====")
        print(f"Total monsters: {len(self.game_data.monsters)}")
        
        for i, monster in enumerate(self.game_data.monsters):
            print(f"Monster #{i+1}:")
            print(f"  Name: {monster.get('name', 'Unknown')}")
            print(f"  ID: {monster.get('id', 'Unknown')}")
            print(f"  Sprite: {monster.get('sprite', 'Unknown')}")
            print(f"  HP: {monster.get('hp', 0)}")
            print(f"  Attack: {monster.get('attack', 0)}")
            print(f"  Power: {monster.get('power', 0)}")
            print(f"  Defense: {monster.get('defense', 0)}")
            print(f"  XP: {monster.get('exp', 0)}")
            print(f"  Gold: {monster.get('gold', 0)}")
            print(f"  Weaknesses: {monster.get('weaknesses', [])}")
            print(f"  Resistances: {monster.get('resistances', [])}")
            print(f"  Attack Type: {monster.get('attack_type', 'Unknown')}")
            print(f"  Behavior: {monster.get('behavior', 'Unknown')}")
            print("")
        
        print("==== END MONSTER LIST DEBUG ====")
        
    def tab_activated(self):
        """Called when the tab is activated."""
        # Refresh data
        self.update_data()
        
        # Debug the monster list
        self.debug_monster_list()
        
        # Force a reload of all images to ensure proper alignment
        self.reload_monster_images()
        
    def on_monster_selected(self, current, previous):
        """Handle selection of a monster in the list."""
        if not current:
            self.current_monster = None
            self.enable_details(False)
            return
            
        # Get the selected monster ID
        monster_id = current.data(Qt.ItemDataRole.UserRole)
        
        # Debug: print all information about the selected item
        display_text = current.text()
        print(f"\nDEBUG - Selected item: Text='{display_text}', ID stored='{monster_id}'")
        
        # Find the monster by ID
        self.current_monster = None
        for monster in self.game_data.monsters:
            if monster.get('id') == monster_id:
                self.current_monster = monster
                print(f"DEBUG - Found monster with ID '{monster_id}': {monster.get('name')}")
                break
        
        if self.current_monster:
            # Update the details - use .get() to provide defaults for missing keys
            self.name_edit.setText(self.current_monster.get('name', 'Unknown Monster'))
            
            # Make sure the monster has an ID, generate one if missing
            if 'id' not in self.current_monster:
                self.current_monster['id'] = '00'
            self.id_edit.setText(self.current_monster.get('id', '00'))
            
            self.hp_spin.setValue(self.current_monster.get('hp', 100))
            
            # Use 'power' field if it exists, otherwise try 'attack', or default to 10
            power = self.current_monster.get('power', self.current_monster.get('attack', 10))
            self.power_spin.setValue(power)
            
            self.exp_spin.setValue(self.current_monster.get('exp', 20))
            
            # Make sure the monster has a sprite, generate one if missing
            if 'sprite' not in self.current_monster:
                monster_id = self.current_monster.get('id', '00')
                self.current_monster['sprite'] = f"enemy-ms_{monster_id}"
            
            print(f"Selected monster: {self.current_monster.get('name')} (ID: {self.current_monster.get('id')})")
            print(f"Sprite: {self.current_monster.get('sprite')}")
            
            # Load the monster image
            self.load_monster_image()
            
            # Set battle settings based on monster properties or defaults
            
            # Set attack type
            attack_type = self.current_monster.get('attack_type', 'Physical')
            index = self.attack_combo.findText(attack_type)
            self.attack_combo.setCurrentIndex(max(index, 0))  # Use 0 (Physical) if not found
            
            # Set weakness
            weakness = "None"
            if 'weaknesses' in self.current_monster and self.current_monster['weaknesses']:
                weakness = str(self.current_monster['weaknesses'][0]).capitalize()
            index = self.weakness_combo.findText(weakness)
            self.weakness_combo.setCurrentIndex(max(index, 0))  # Use 0 (None) if not found
            
            # Set behavior
            behavior = self.current_monster.get('behavior', 'Aggressive')
            index = self.behavior_combo.findText(behavior)
            self.behavior_combo.setCurrentIndex(max(index, 0))  # Use 0 (Aggressive) if not found
            
            # Enable the details
            self.enable_details(True)
        else:
            print(f"Error: Could not find monster with ID '{monster_id}'")
            self.enable_details(False)
        
    def on_id_changed(self, text):
        """Handle change of monster ID."""
        if not self.current_monster:
            return
            
        # Ensure text is at least 2 characters, pad with zeros if needed
        if len(text) < 2:
            text = text.zfill(2)
            self.id_edit.setText(text)
            
        # Update the monster's ID
        self.current_monster['id'] = text
        
        # Update the sprite based on ID - use dictionary format for consistency
        self.current_monster['sprite'] = {
            "sheet": "monsters1", 
            "row": 0, 
            "col": 0
        }
            
        # Reload the monster image
        self.load_monster_image()
        
    def load_monster_image(self):
        """Load and display the monster image based on the selected monster's sprite."""
        try:
            # Get the selected monster
            selected_items = self.monster_list.selectedItems()
            if not selected_items:
                return
                
            # Get the monster data
            monster_id = selected_items[0].data(Qt.ItemDataRole.UserRole)
            
            # Find the monster by ID
            monster = None
            for m in self.game_data.monsters:
                if m.get('id') == monster_id:
                    monster = m
                    break
                    
            if not monster:
                print(f"Could not find monster with ID: {monster_id}")
                return
                
            # Get the sprite information
            sprite_info = monster.get('sprite')
            if not sprite_info:
                print(f"No sprite information found for monster {monster_id}")
                return
                
            # Clear the image display
            self.monster_image.clear()
            
            # Handle different sprite formats
            if isinstance(sprite_info, dict):
                # New format: dictionary with sheet, row, col
                sheet_name = sprite_info.get('sheet', 'monsters1')
                row = sprite_info.get('row', 0)
                col = sprite_info.get('col', 0)
                
                # Create a placeholder image since we don't have sprite sheets yet
                self._create_placeholder_image(monster)
                
                # Show sprite information in the info label
                self.sprite_info_label.setText(f"Sheet: {sheet_name}, Row: {row}, Col: {col}")
                
            else:
                # Old format: string like "enemy-ms_XX"
                sprite_name = str(sprite_info)
                monster_id = '00'
                
                # Extract the monster ID from the sprite name
                if '_' in sprite_name:
                    # Format is typically enemy-ms_XX where XX is the ID
                    monster_id = sprite_name.split('_')[-1]
                elif len(sprite_name) >= 2 and sprite_name[-2:].isdigit():
                    # Just in case it's formatted differently
                    monster_id = sprite_name[-2:]
                    
                print(f"Loading monster image for monster ID: {monster_id}, sprite: {sprite_name}")
                
                # Create a placeholder image
                self._create_placeholder_image(monster)
                
                # Update the sprite info label
                self.sprite_info_label.setText(f"ID: {monster_id} (Placeholder)")
                
        except Exception as e:
            print(f"Error loading monster image: {str(e)}")
            import traceback
            traceback.print_exc()
            self.monster_image.setText(f"Error: {str(e)}")
            self.sprite_info_label.setText("Error loading sprite")
            
    def _create_placeholder_image(self, monster):
        """Create a placeholder image for the monster with its name."""
        # Create a colored pixmap
        pixmap = QPixmap(96, 96)
        
        # Use a consistent color based on the monster's name
        name = monster.get('name', 'Unknown')
        # Generate a deterministic color based on the name
        color_seed = sum(ord(c) for c in name)
        r = (color_seed * 23) % 200 + 55  # 55-255
        g = (color_seed * 37) % 200 + 55  # 55-255
        b = (color_seed * 51) % 200 + 55  # 55-255
        
        pixmap.fill(QColor(r, g, b))
        
        # Set the pixmap
        self.monster_image.setPixmap(pixmap)
        self.monster_image.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
    def enable_details(self, enabled):
        """Enable or disable the details widgets."""
        self.details_box.setEnabled(enabled)
        self.image_box.setEnabled(enabled)
        self.battle_box.setEnabled(enabled)
        self.remove_button.setEnabled(enabled)
        
    def add_monster(self):
        """Add a new monster."""
        # Create a new monster with default values
        new_monster = {
            'id': '00',
            'name': "New Monster",
            'hp': 100,
            'power': 10,
            'exp': 20,
            'sprite': "enemy-ms_00",
            'attack_type': "Physical",
            'weaknesses': [],
            'resistances': [],
            'behavior': "Aggressive"
        }
        
        # Add to the game data
        self.game_data.monsters.append(new_monster)
        
        # Update the UI
        self.update_data()
        
        # Select the new monster
        for i in range(self.monster_list.count()):
            if self.monster_list.item(i).text() == new_monster['name']:
                self.monster_list.setCurrentRow(i)
                break
                
    def remove_monster(self):
        """Remove the selected monster."""
        if not self.current_monster:
            return
            
        # Remove from the game data
        self.game_data.monsters.remove(self.current_monster)
        
        # Update the UI
        self.update_data()
        
    def save_monster(self):
        """Save changes to the selected monster."""
        if not self.current_monster:
            return
            
        # Update the monster with the form values
        self.current_monster['name'] = self.name_edit.text()
        self.current_monster['id'] = self.id_edit.text()
        self.current_monster['hp'] = self.hp_spin.value()
        self.current_monster['power'] = self.power_spin.value()
        self.current_monster['exp'] = self.exp_spin.value()
        
        # Update battle settings
        self.current_monster['attack_type'] = self.attack_combo.currentText()
        
        # Update weakness - convert to list since weaknesses is stored as a list
        weakness = self.weakness_combo.currentText()
        if weakness != "None":
            self.current_monster['weaknesses'] = [weakness.lower()]
        else:
            self.current_monster['weaknesses'] = []
            
        self.current_monster['behavior'] = self.behavior_combo.currentText()
        
        # Mark the game data as changed
        try:
            self.game_data.mark_as_changed()
        except:
            pass
        
        # Update the UI
        self.update_data()
        
        # Reselect the monster
        for i in range(self.monster_list.count()):
            if self.monster_list.item(i).text() == self.current_monster['name']:
                self.monster_list.setCurrentRow(i)
                break
                
    def save_changes(self):
        """Save all changes to the game data."""
        return self.game_data.save_to_file()

    def reload_monster_images(self):
        """Reload all monster images based on current game data."""
        # Reload the current monster image if one is selected
        if self.current_monster:
            self.load_monster_image() 