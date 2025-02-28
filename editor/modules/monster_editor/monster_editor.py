import os
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QListWidget, 
                           QGroupBox, QFormLayout, QLabel, QLineEdit, 
                           QSpinBox, QComboBox, QPushButton)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap

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
        
        # Monster image
        self.image_box = QGroupBox("Monster Image")
        image_layout = QVBoxLayout()
        self.monster_image = QLabel()
        self.monster_image.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.monster_image.setMinimumSize(128, 128)
        self.monster_image.setMaximumSize(256, 256)
        self.monster_image.setScaledContents(True)
        image_layout.addWidget(self.monster_image)
        
        # Monster type selection
        id_layout = QHBoxLayout()
        id_layout.addWidget(QLabel("Monster ID:"))
        self.id_edit = QLineEdit()
        self.id_edit.setMaxLength(2)  # Usually monster IDs are 2 characters
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
        for monster in self.game_data.monsters:
            self.monster_list.addItem(monster['name'])
            
        # Clear the current selection
        self.current_monster = None
        self.enable_details(False)
        
    def on_monster_selected(self, current, previous):
        """Handle selection of a monster in the list."""
        if not current:
            self.current_monster = None
            self.enable_details(False)
            return
            
        # Get the selected monster
        monster_name = current.text()
        self.current_monster = self.game_data.get_monster_by_name(monster_name)
        
        if self.current_monster:
            # Update the details
            self.name_edit.setText(self.current_monster['name'])
            self.id_edit.setText(self.current_monster['id'])
            self.hp_spin.setValue(self.current_monster['hp'])
            self.power_spin.setValue(self.current_monster['power'])
            self.exp_spin.setValue(self.current_monster['exp'])
            
            # Load the monster image
            self.load_monster_image()
            
            # Set defaults for battle settings (since they're not in our model yet)
            self.attack_combo.setCurrentIndex(0)  # Physical
            self.weakness_combo.setCurrentIndex(0)  # None
            self.behavior_combo.setCurrentIndex(0)  # Aggressive
            
            # Enable the details
            self.enable_details(True)
            
    def on_id_changed(self, text):
        """Handle change of monster ID."""
        if not self.current_monster:
            return
            
        # Update the monster's ID
        self.current_monster['id'] = text
        
        # Update the sprite based on ID
        self.current_monster['sprite'] = f"enemy-ms_{text}"
            
        # Reload the monster image
        self.load_monster_image()
        
    def load_monster_image(self):
        """Load the monster image based on the sprite."""
        if not self.current_monster:
            return
            
        # Get the sprite path
        sprite_name = self.current_monster.get('sprite', 'enemy-ms_00')
        sprite_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 
                                  '..', '..', '..', 'img', 'pc', 'enemySprite.png')
        
        # Load the image
        pixmap = QPixmap(sprite_path)
        if pixmap.isNull():
            # If image not found, try a default
            default_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 
                                      '..', '..', '..', 'img', 'pc', 'enemySprite.png')
            pixmap = QPixmap(default_path)
            
        # Set the image
        self.monster_image.setPixmap(pixmap)
        
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
            'sprite': "enemy-ms_00"
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