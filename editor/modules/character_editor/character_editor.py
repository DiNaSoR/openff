import os
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QListWidget, 
                           QGroupBox, QFormLayout, QLabel, QLineEdit, 
                           QSpinBox, QComboBox, QPushButton, QTabWidget,
                           QCheckBox)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap

class CharacterEditorTab(QWidget):
    """Tab for editing game characters with visual elements."""
    
    def __init__(self, game_data):
        super().__init__()
        self.game_data = game_data
        self.current_character = None
        
        self.init_ui()
        
    def init_ui(self):
        """Initialize the user interface."""
        # Main layout
        main_layout = QHBoxLayout(self)
        
        # Left side - Character list
        left_layout = QVBoxLayout()
        
        # Character list
        self.character_list = QListWidget()
        self.character_list.currentItemChanged.connect(self.on_character_selected)
        left_layout.addWidget(QLabel("Characters:"))
        left_layout.addWidget(self.character_list)
        
        # Add/Remove buttons
        button_layout = QHBoxLayout()
        self.add_button = QPushButton("Add Character")
        self.add_button.clicked.connect(self.add_character)
        self.remove_button = QPushButton("Remove Character")
        self.remove_button.clicked.connect(self.remove_character)
        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.remove_button)
        left_layout.addLayout(button_layout)
        
        # Right side - Character details
        right_layout = QVBoxLayout()
        
        # Character image
        self.image_box = QGroupBox("Character Image")
        image_layout = QVBoxLayout()
        self.character_image = QLabel()
        self.character_image.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.character_image.setMinimumSize(128, 128)
        self.character_image.setMaximumSize(256, 256)
        self.character_image.setScaledContents(True)
        image_layout.addWidget(self.character_image)
        
        # Job selection
        job_layout = QHBoxLayout()
        job_layout.addWidget(QLabel("Job:"))
        self.job_combo = QComboBox()
        self.job_combo.addItems([
            "Fighter", "Black Mage", "White Mage", "Thief", 
            "Monk", "Red Mage", "Knight", "Ninja"
        ])
        self.job_combo.currentIndexChanged.connect(self.on_job_changed)
        job_layout.addWidget(self.job_combo)
        image_layout.addLayout(job_layout)
        
        self.image_box.setLayout(image_layout)
        right_layout.addWidget(self.image_box)
        
        # Character details - using tab widget to organize
        self.details_tabs = QTabWidget()
        
        # Tab 1: Basic Info
        basic_tab = QWidget()
        basic_layout = QFormLayout(basic_tab)
        
        # Name field
        self.name_edit = QLineEdit()
        basic_layout.addRow("Name:", self.name_edit)
        
        # Level field
        self.level_spin = QSpinBox()
        self.level_spin.setRange(1, 99)
        basic_layout.addRow("Level:", self.level_spin)
        
        # Experience Points
        self.exp_spin = QSpinBox()
        self.exp_spin.setRange(0, 9999999)
        self.exp_spin.setSingleStep(100)
        basic_layout.addRow("Experience:", self.exp_spin)
        
        # Next level exp
        self.next_level_spin = QSpinBox()
        self.next_level_spin.setRange(0, 9999999)
        self.next_level_spin.setSingleStep(100)
        basic_layout.addRow("Next Level:", self.next_level_spin)
        
        # HP fields
        hp_layout = QHBoxLayout()
        self.hp_spin = QSpinBox()
        self.hp_spin.setRange(1, 9999)
        hp_layout.addWidget(self.hp_spin)
        hp_layout.addWidget(QLabel("/"))
        self.max_hp_spin = QSpinBox()
        self.max_hp_spin.setRange(1, 9999)
        hp_layout.addWidget(self.max_hp_spin)
        basic_layout.addRow("HP:", hp_layout)
        
        # MP field
        mp_layout = QHBoxLayout()
        self.mp_spin = QSpinBox()
        self.mp_spin.setRange(0, 999)
        mp_layout.addWidget(self.mp_spin)
        mp_layout.addWidget(QLabel("/"))
        self.max_mp_spin = QSpinBox()
        self.max_mp_spin.setRange(0, 999)
        mp_layout.addWidget(self.max_mp_spin)
        basic_layout.addRow("MP:", mp_layout)
        
        # Tab 2: Stats
        stats_tab = QWidget()
        stats_layout = QFormLayout(stats_tab)
        
        # Power (Strength)
        self.pw_spin = QSpinBox()
        self.pw_spin.setRange(1, 99)
        stats_layout.addRow("Power:", self.pw_spin)
        
        # Speed (Agility)
        self.sp_spin = QSpinBox()
        self.sp_spin.setRange(1, 99)
        stats_layout.addRow("Speed:", self.sp_spin)
        
        # Intelligence
        self.it_spin = QSpinBox()
        self.it_spin.setRange(1, 99)
        stats_layout.addRow("Intelligence:", self.it_spin)
        
        # Stamina (Vitality)
        self.st_spin = QSpinBox()
        self.st_spin.setRange(1, 99)
        stats_layout.addRow("Stamina:", self.st_spin)
        
        # Luck
        self.lk_spin = QSpinBox()
        self.lk_spin.setRange(1, 99)
        stats_layout.addRow("Luck:", self.lk_spin)
        
        # Tab 3: Combat Stats
        combat_tab = QWidget()
        combat_layout = QFormLayout(combat_tab)
        
        # Weapon Power
        self.wp_spin = QSpinBox()
        self.wp_spin.setRange(0, 99)
        combat_layout.addRow("Weapon Power:", self.wp_spin)
        
        # Dexterity/Hit Rate
        self.dx_spin = QSpinBox()
        self.dx_spin.setRange(0, 99)
        combat_layout.addRow("Dexterity:", self.dx_spin)
        
        # Armor/Defense
        self.am_spin = QSpinBox()
        self.am_spin.setRange(0, 99)
        combat_layout.addRow("Armor:", self.am_spin)
        
        # Evasion
        self.ev_spin = QSpinBox()
        self.ev_spin.setRange(0, 99)
        combat_layout.addRow("Evasion:", self.ev_spin)
        
        # Tab 4: Status
        status_tab = QWidget()
        status_layout = QFormLayout(status_tab)
        
        # Status checkboxes
        self.poison_check = QCheckBox("Poisoned")
        status_layout.addRow("", self.poison_check)
        
        self.paralyze_check = QCheckBox("Paralyzed")
        status_layout.addRow("", self.paralyze_check)
        
        # Add tabs to tab widget
        self.details_tabs.addTab(basic_tab, "Basic")
        self.details_tabs.addTab(stats_tab, "Stats")
        self.details_tabs.addTab(combat_tab, "Combat")
        self.details_tabs.addTab(status_tab, "Status")
        
        right_layout.addWidget(self.details_tabs)
        
        # Save button
        self.save_button = QPushButton("Save Changes")
        self.save_button.clicked.connect(self.save_character)
        right_layout.addWidget(self.save_button)
        
        # Add layouts to main layout
        main_layout.addLayout(left_layout, 1)
        main_layout.addLayout(right_layout, 2)
        
        # Disable details until a character is selected
        self.enable_details(False)
        
    def update_data(self):
        """Update the UI with the latest game data."""
        # Clear the list
        self.character_list.clear()
        
        # Add characters to the list
        for character in self.game_data.characters:
            self.character_list.addItem(character['name'])
            
        # Clear the current selection
        self.current_character = None
        self.enable_details(False)
        
    def on_character_selected(self, current, previous):
        """Handle character selection from the list."""
        if not current:
            self.enable_details(False)
            return
        
        # Get the character name from the selected item
        character_name = current.text()
        self.current_character = self.game_data.get_character_by_name(character_name)
        
        if self.current_character:
            # Update basic info
            self.name_edit.setText(self.current_character['name'])
            self.level_spin.setValue(self.current_character.get('level', 1))
            
            # Set experience if available
            if 'ep' in self.current_character:
                self.exp_spin.setValue(self.current_character['ep'])
            else:
                self.exp_spin.setValue(0)
                
            # Set next level experience if available
            if 'next' in self.current_character:
                self.next_level_spin.setValue(self.current_character['next'])
            else:
                self.next_level_spin.setValue(1000)
            
            # Set HP values
            self.hp_spin.setValue(self.current_character.get('hp', 0))
            self.max_hp_spin.setValue(self.current_character.get('mhp', self.current_character.get('hp', 0)))
            
            # Handle MP as a list - use the first MP value or 0 if empty
            mp_value = 0
            if 'mp' in self.current_character:
                if isinstance(self.current_character['mp'], list) and len(self.current_character['mp']) > 0:
                    mp_value = self.current_character['mp'][0]
                elif isinstance(self.current_character['mp'], (int, float)):
                    mp_value = self.current_character['mp']
            self.mp_spin.setValue(mp_value)
            
            # Set Max MP values
            max_mp_value = mp_value
            if 'mmp' in self.current_character:
                if isinstance(self.current_character['mmp'], list) and len(self.current_character['mmp']) > 0:
                    max_mp_value = self.current_character['mmp'][0]
                elif isinstance(self.current_character['mmp'], (int, float)):
                    max_mp_value = self.current_character['mmp']
            self.max_mp_spin.setValue(max_mp_value)
            
            # Set main stats
            stats = self.current_character.get('stats', {})
            self.pw_spin.setValue(stats.get('pw', 10))  # Power/Strength
            self.sp_spin.setValue(stats.get('sp', 10))  # Speed/Agility
            self.it_spin.setValue(stats.get('it', 10))  # Intelligence
            self.st_spin.setValue(stats.get('st', 10))  # Stamina/Vitality
            self.lk_spin.setValue(stats.get('lk', 10))  # Luck
            
            # Set combat stats
            self.wp_spin.setValue(stats.get('wp', 5))   # Weapon Power
            self.dx_spin.setValue(stats.get('dx', 5))   # Dexterity/Hit Rate
            self.am_spin.setValue(stats.get('am', 5))   # Armor/Defense
            self.ev_spin.setValue(stats.get('ev', 5))   # Evasion
            
            # Set status conditions
            status = self.current_character.get('status', {})
            self.poison_check.setChecked(status.get('poison', False))
            self.paralyze_check.setChecked(status.get('paralyze', False))
            
            # Set the job - handle both int or string values
            if 'job_name' in self.current_character and self.current_character['job_name']:
                job_name = self.current_character['job_name']
            elif isinstance(self.current_character['job'], str):
                job_name = self.current_character['job']
            else:
                # Convert job index to job name
                job_names = [self.job_combo.itemText(i) for i in range(self.job_combo.count())]
                job_index = self.current_character['job']
                job_name = job_names[job_index] if 0 <= job_index < len(job_names) else "Fighter"
                
            job_index = self.job_combo.findText(job_name)
            if job_index >= 0:
                self.job_combo.setCurrentIndex(job_index)
                
            # Load the character image
            self.load_character_image()
            
            # Enable the details
            self.enable_details(True)
            
    def on_job_changed(self, index):
        """Handle change of job selection."""
        if not self.current_character:
            return
            
        # Get the job name from the combo box
        job_name = self.job_combo.currentText()
        
        # Update the character's job - maintain original type
        if isinstance(self.current_character['job'], int):
            # If the original job was an int, store it as an int
            self.current_character['job'] = index
            # Also update job_name if it exists
            if 'job_name' in self.current_character:
                self.current_character['job_name'] = job_name
        else:
            # Otherwise store it as a string
            self.current_character['job'] = job_name
        
        # Update the sprite based on job
        if index >= 0 and index < 8:  # Assuming 8 jobs
            self.current_character['sprite'] = f"job{index}.png"
            
        # Reload the character image
        self.load_character_image()
        
        # Mark the game data as changed
        self.game_data.mark_as_changed()
        
    def load_character_image(self):
        """Load the character image based on the sprite."""
        if not self.current_character:
            return
            
        # Get the sprite path
        sprite_name = self.current_character.get('sprite', 'job0.png')
        sprite_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 
                                  '..', '..', '..', 'img', 'pc', sprite_name)
        
        # Load the image
        pixmap = QPixmap(sprite_path)
        if pixmap.isNull():
            # If image not found, try a default
            default_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 
                                      '..', '..', '..', 'img', 'pc', 'job0.png')
            pixmap = QPixmap(default_path)
            
        # Set the image
        self.character_image.setPixmap(pixmap)
        
    def enable_details(self, enabled):
        """Enable or disable the details widgets."""
        self.details_tabs.setEnabled(enabled)
        self.image_box.setEnabled(enabled)
        self.remove_button.setEnabled(enabled)
        
    def add_character(self):
        """Add a new character."""
        # Create a new character with default values
        new_character = {
            'name': "New Character",
            'job': 0,  # Use index for consistency
            'job_name': "Fighter",  # Add job_name field
            'level': 1,
            'hp': 100,
            'mhp': 100,  # Max HP
            'mp': [0],   # MP as list for consistency
            'mmp': [0],  # Max MP as list
            'ep': 0,     # Experience points
            'next': 1000, # Experience for next level
            'stats': {
                'pw': 10,  # Power
                'sp': 10,  # Speed
                'it': 10,  # Intelligence
                'st': 10,  # Stamina
                'lk': 10,  # Luck
                'wp': 5,   # Weapon Power
                'dx': 5,   # Dexterity
                'am': 5,   # Armor
                'ev': 5    # Evasion
            },
            'equipment': {
                'weapon': -1,
                'armor': -1,
                'helmet': -1,
                'accessory': -1
            },
            'status': {
                'poison': False,
                'paralyze': False
            },
            'sprite': "job0.png"
        }
        
        # Add to the game data
        self.game_data.characters.append(new_character)
        
        # Mark the game data as changed
        self.game_data.mark_as_changed()
        
        # Update the UI
        self.update_data()
        
        # Select the new character
        for i in range(self.character_list.count()):
            if self.character_list.item(i).text() == new_character['name']:
                self.character_list.setCurrentRow(i)
                break
                
    def remove_character(self):
        """Remove the selected character."""
        if not self.current_character:
            return
            
        # Remove from the game data
        self.game_data.characters.remove(self.current_character)
        
        # Mark the game data as changed
        self.game_data.mark_as_changed()
        
        # Update the UI
        self.update_data()
        
    def save_character(self):
        """Save changes to the selected character."""
        if not self.current_character:
            return
            
        # Update the basic character information
        self.current_character['name'] = self.name_edit.text()
        self.current_character['level'] = self.level_spin.value()
        self.current_character['hp'] = self.hp_spin.value()
        
        # Set max HP
        self.current_character['mhp'] = self.max_hp_spin.value()
        
        # Set MP (maintain original format)
        if isinstance(self.current_character.get('mp', []), list):
            # If it was a list, update the first element or create a new list
            mp_list = self.current_character.get('mp', [0])
            if len(mp_list) > 0:
                mp_list[0] = self.mp_spin.value()
            else:
                mp_list = [self.mp_spin.value()]
            self.current_character['mp'] = mp_list
        else:
            # If it wasn't a list, just set it directly
            self.current_character['mp'] = self.mp_spin.value()
        
        # Set max MP (maintain original format)
        if isinstance(self.current_character.get('mmp', []), list):
            # If it was a list, update the first element or create a new list
            mmp_list = self.current_character.get('mmp', [0])
            if len(mmp_list) > 0:
                mmp_list[0] = self.max_mp_spin.value()
            else:
                mmp_list = [self.max_mp_spin.value()]
            self.current_character['mmp'] = mmp_list
        else:
            # If it wasn't a list, just set it directly
            self.current_character['mmp'] = self.max_mp_spin.value()
        
        # Set experience and next level
        self.current_character['ep'] = self.exp_spin.value()
        self.current_character['next'] = self.next_level_spin.value()
        
        # Initialize stats dictionary if it doesn't exist
        if 'stats' not in self.current_character:
            self.current_character['stats'] = {}
            
        # Update main stats
        self.current_character['stats']['pw'] = self.pw_spin.value()  # Power
        self.current_character['stats']['sp'] = self.sp_spin.value()  # Speed
        self.current_character['stats']['it'] = self.it_spin.value()  # Intelligence
        self.current_character['stats']['st'] = self.st_spin.value()  # Stamina
        self.current_character['stats']['lk'] = self.lk_spin.value()  # Luck
        
        # Update combat stats
        self.current_character['stats']['wp'] = self.wp_spin.value()  # Weapon Power
        self.current_character['stats']['dx'] = self.dx_spin.value()  # Dexterity
        self.current_character['stats']['am'] = self.am_spin.value()  # Armor
        self.current_character['stats']['ev'] = self.ev_spin.value()  # Evasion
        
        # Initialize status dictionary if it doesn't exist
        if 'status' not in self.current_character:
            self.current_character['status'] = {}
            
        # Update status conditions
        self.current_character['status']['poison'] = self.poison_check.isChecked()
        self.current_character['status']['paralyze'] = self.paralyze_check.isChecked()
        
        # Handle the job field - check original type and maintain it
        job_name = self.job_combo.currentText()
        if isinstance(self.current_character['job'], int):
            # If the original job was an int, store it as an int
            job_index = self.job_combo.currentIndex()
            self.current_character['job'] = job_index
            # Also update job_name if it exists
            if 'job_name' in self.current_character:
                self.current_character['job_name'] = job_name
        else:
            # Otherwise store it as a string
            self.current_character['job'] = job_name
        
        # Mark the game data as changed
        self.game_data.mark_as_changed()
        
        # Update the UI
        self.update_data()
        
        # Reselect the character
        for i in range(self.character_list.count()):
            if self.character_list.item(i).text() == self.current_character['name']:
                self.character_list.setCurrentRow(i)
                break
                
    def save_changes(self):
        """Save all changes to the game data."""
        # This would be called from the main window
        return self.game_data.save_to_file() 