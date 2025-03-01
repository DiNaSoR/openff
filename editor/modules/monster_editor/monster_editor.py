import os
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QListWidget, 
                           QGroupBox, QFormLayout, QLabel, QLineEdit, 
                           QSpinBox, QComboBox, QPushButton, QListWidgetItem)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QPixmap, QColor
from editor.core.game_data_monsters import SPRITE_POSITION_MAP

class MonsterEditorTab(QWidget):
    """Tab for editing game monsters with visual elements."""
    
    def __init__(self, game_data):
        super().__init__()
        self.game_data = game_data
        self.current_monster = None
        self.sprite_sheets = {
            "monsters1": "enemySprite.png",
            "game": "gameSprite.png"
        }
        
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
        self.id_edit.setMaxLength(4)  # Allow IDs like "ms_04", "2b", etc.
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
        
        # Print a debug list of all monster IDs
        self.debug_monster_id_list()
        
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
        # Debug all monster IDs in game data
        print("\nDEBUG - All monster IDs in game_data.monsters:")
        for i, monster in enumerate(self.game_data.monsters):
            print(f"  Monster #{i+1}: ID={monster.get('id', 'Unknown')}, Name={monster.get('name', 'Unknown')}")
        print("")
        
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
            
            # Make sure the monster has an ID
            monster_id = self.current_monster.get('id', 'ms_00')
            self.id_edit.setText(monster_id)
            
            self.hp_spin.setValue(self.current_monster.get('hp', 100))
            
            # Use 'power' field if it exists, otherwise try 'attack' or 'pw', or default to 10
            power = self.current_monster.get('power', 
                   self.current_monster.get('attack', 
                   self.current_monster.get('pw', 10)))
            self.power_spin.setValue(power)
            
            # Look for 'exp' or 'ep' field
            exp = self.current_monster.get('exp', self.current_monster.get('ep', 20))
            self.exp_spin.setValue(exp)
            
            # Ensure the monster has a sprite with CSS position data if possible
            if 'sprite' not in self.current_monster or not self.current_monster['sprite']:
                # Get sprite data from our mapping
                sprite_data = self.get_sprite_for_id(monster_id)
                if sprite_data:
                    self.current_monster['sprite'] = sprite_data
                else:
                    # Default sprite if nothing found
                    self.current_monster['sprite'] = {
                        "sheet": "monsters1", 
                        "row": 0, 
                        "col": 0
                    }
            elif isinstance(self.current_monster['sprite'], dict) and 'css_position' not in self.current_monster['sprite']:
                # If sprite exists but doesn't have CSS position, try to add it
                sprite_data = self.get_sprite_for_id(monster_id)
                if sprite_data and 'css_position' in sprite_data:
                    # Update with CSS position data
                    self.current_monster['sprite'].update(sprite_data)
            
            print(f"Selected monster: {self.current_monster.get('name')} (ID: {monster_id})")
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
            
        # Update the monster's ID
        self.current_monster['id'] = text
        
        # Update the sprite based on ID
        if text.startswith("ms_") or len(text) <= 4:
            # Try to find sprite in the map
            sprite_data = self.get_sprite_for_id(text)
            if sprite_data:
                self.current_monster['sprite'] = sprite_data
            
        # Reload the monster image
        self.load_monster_image()
    
    def get_sprite_for_id(self, monster_id):
        """Get sprite data for a given monster ID."""
        # Import the function from the GameDataMonsters class
        from editor.core.game_data_monsters import GameDataMonsters
        
        # Create a temporary instance to use its get_sprite_for_id method
        monsters_handler = GameDataMonsters()
        return monsters_handler.get_sprite_for_id(monster_id)
        
    def load_monster_image(self):
        """Load and display the monster image based on the selected monster's sprite."""
        try:
            # Make sure we have a current monster
            if not self.current_monster:
                print("No current monster selected")
                return
                
            # Get the sprite information
            sprite_info = self.current_monster.get('sprite')
            if not sprite_info:
                print(f"No sprite information found for monster {self.current_monster.get('id', 'unknown')}")
                return
                
            # Clear the image display
            self.monster_image.clear()
            
            # Handle different sprite formats
            if isinstance(sprite_info, dict):
                # Dictionary format with sheet, row, col, or css_position
                sheet_name = sprite_info.get('sheet', 'monsters1')
                monster_id = self.current_monster.get('id', 'ms_00')
                
                # Look for the actual sprite sheet image
                sprite_path = os.path.join("static", "sprites", self.sprite_sheets.get(sheet_name, "enemySprite.png"))
                
                # Check if the file exists
                if os.path.exists(sprite_path):
                    pixmap = QPixmap(sprite_path)
                    
                    # The sprite sheet size from CSS
                    sheet_width = 498
                    sheet_height = 348
                    
                    # Check if we have CSS position data
                    if 'css_position' in sprite_info:
                        # Use CSS position data
                        css_x, css_y = sprite_info['css_position']
                        x = abs(css_x)  # CSS positions are negative, we need positive for pixmap.copy()
                        y = abs(css_y)
                        sprite_size = sprite_info.get('size', 96)
                        print(f"Using CSS position from sprite_info for {monster_id}: x={x}, y={y}, size={sprite_size}")
                    else:
                        # Use row/col or fall back to CSS position map
                        css_position_data = None
                        
                        # Try to get from our CSS position map
                        try:
                            sprite_data = self.get_sprite_for_id(monster_id)
                            if 'css_position' in sprite_data:
                                css_position_data = sprite_data
                                css_x, css_y = css_position_data['css_position']
                                x = abs(css_x)
                                y = abs(css_y)
                                sprite_size = css_position_data.get('size', 96)
                                
                                # Update the monster's sprite info with CSS position data
                                self.current_monster['sprite'].update({
                                    'css_position': css_position_data['css_position'],
                                    'size': sprite_size
                                })
                                
                                print(f"Using CSS position from map for {monster_id}: x={x}, y={y}, size={sprite_size}")
                        except Exception as e:
                            print(f"Error getting sprite data: {e}")
                            css_position_data = None
                        
                        # Fall back to row/col calculation
                        if not css_position_data:
                            row = sprite_info.get('row', 0)
                            col = sprite_info.get('col', 0)
                            sprite_size = 96
                            x = col * sprite_size
                            y = row * sprite_size
                            print(f"Using calculated position for {monster_id}: x={x}, y={y}, size={sprite_size}")
                    
                    # Extract the sprite from the sheet
                    try:
                        sprite_pixmap = pixmap.copy(x, y, sprite_size, sprite_size)
                        
                        # Scale it up for display
                        scaled_pixmap = sprite_pixmap.scaled(96, 96, Qt.AspectRatioMode.KeepAspectRatio)
                        self.monster_image.setPixmap(scaled_pixmap)
                        
                        # Show sprite information in the info label
                        if 'css_position' in sprite_info:
                            self.sprite_info_label.setText(f"ID: {monster_id}, Position: ({css_x}, {css_y}), Size: {sprite_size}x{sprite_size}")
                        else:
                            if css_position_data:
                                self.sprite_info_label.setText(f"ID: {monster_id}, Position: ({css_x}, {css_y}), Size: {sprite_size}x{sprite_size}")
                            else:
                                row = sprite_info.get('row', 0)
                                col = sprite_info.get('col', 0)
                                self.sprite_info_label.setText(f"Sheet: {sheet_name}, Row: {row}, Col: {col}")
                    except Exception as e:
                        print(f"Error extracting sprite: {e}")
                        self._create_placeholder_image(self.current_monster)
                        self.sprite_info_label.setText(f"Error extracting sprite at ({x}, {y}): {e}")
                else:
                    # Create a placeholder if sprite sheet not found
                    self._create_placeholder_image(self.current_monster)
                    self.sprite_info_label.setText(f"Sheet: {sheet_name} (File not found)")
                
            else:
                # Old format: string like "enemy-ms_XX"
                sprite_name = str(sprite_info)
                monster_id = self.current_monster.get('id', 'ms_00')
                
                # Try to extract the monster ID from the sprite name if it contains it
                if '_' in sprite_name:
                    # Format is typically enemy-ms_XX where XX is the ID
                    potential_id = sprite_name.split('_')[-1]
                    if potential_id.isalnum():  # Check if it's alphanumeric
                        monster_id = f"ms_{potential_id}"
                
                print(f"Loading monster image for monster ID: {monster_id}, sprite: {sprite_name}")
                
                # Try to get sprite position from our mapping
                sprite_data = self.get_sprite_for_id(monster_id)
                
                if sprite_data:
                    # If we have sprite data, update the monster sprite and reload
                    self.current_monster['sprite'] = sprite_data
                    # Recursively call to load with the new sprite format
                    self.load_monster_image()
                    return
                else:
                    # Create a placeholder image
                    self._create_placeholder_image(self.current_monster)
                    self.sprite_info_label.setText(f"ID: {monster_id} (Sprite not found)")
                    
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
            'id': 'ms_00',
            'name': "New Monster",
            'hp': 100,
            'power': 10,
            'exp': 20,
            'sprite': {
                "sheet": "monsters1", 
                "row": 0, 
                "col": 0
            },
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
            item = self.monster_list.item(i)
            if item.data(Qt.ItemDataRole.UserRole) == new_monster['id']:
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
        monster_id = self.current_monster['id']
        for i in range(self.monster_list.count()):
            if self.monster_list.item(i).data(Qt.ItemDataRole.UserRole) == monster_id:
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

    def debug_monster_id_list(self):
        """Debug method to print all monster IDs in the game data."""
        print("==== MONSTER ID LIST DEBUG ====")
        print(f"Total monster IDs: {len(self.game_data.monsters)}")
        
        for i, monster in enumerate(self.game_data.monsters):
            print(f"Monster #{i+1}: ID = {monster.get('id', 'Unknown')}")
        
        print("==== END MONSTER ID LIST DEBUG ====") 