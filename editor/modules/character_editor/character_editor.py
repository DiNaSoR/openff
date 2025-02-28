import os
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QListWidget, 
                           QGroupBox, QFormLayout, QLabel, QLineEdit, 
                           QSpinBox, QComboBox, QPushButton, QTabWidget,
                           QCheckBox, QDialog, QFileDialog, QDialogButtonBox)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QPixmap

class SpriteSheetDialog(QDialog):
    """Dialog for viewing and managing the full sprite sheet."""
    
    def __init__(self, parent=None, sprite_path=None):
        super().__init__(parent)
        self.sprite_path = sprite_path
        self.init_ui()
        
    def init_ui(self):
        """Initialize the dialog UI."""
        self.setWindowTitle("Sprite Sheet Viewer")
        self.setMinimumSize(600, 500)
        
        # Main layout
        layout = QVBoxLayout(self)
        
        # Sprite display
        self.sprite_label = QLabel()
        self.sprite_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.sprite_label.setScaledContents(False)  # Don't scale to preserve pixel art quality
        
        # Load the sprite
        if self.sprite_path and os.path.exists(self.sprite_path):
            pixmap = QPixmap(self.sprite_path)
            if not pixmap.isNull():
                self.sprite_label.setPixmap(pixmap)
        
        # Scroll area to contain the sprite
        layout.addWidget(self.sprite_label)
        
        # Buttons for import/export
        button_layout = QHBoxLayout()
        
        self.import_button = QPushButton("Import Sprite Sheet")
        self.import_button.clicked.connect(self.import_sprite)
        button_layout.addWidget(self.import_button)
        
        self.export_button = QPushButton("Export Sprite Sheet")
        self.export_button.clicked.connect(self.export_sprite)
        button_layout.addWidget(self.export_button)
        
        layout.addLayout(button_layout)
        
        # Dialog buttons
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        
    def import_sprite(self):
        """Import a new sprite sheet."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Import Sprite Sheet", "", "Images (*.png *.jpg *.jpeg)"
        )
        
        if file_path:
            # Load the new sprite sheet
            pixmap = QPixmap(file_path)
            if not pixmap.isNull():
                # Replace the current sprite sheet
                import shutil
                try:
                    shutil.copy(file_path, self.sprite_path)
                    self.sprite_label.setPixmap(pixmap)
                except Exception as e:
                    print(f"Error importing sprite sheet: {e}")
    
    def export_sprite(self):
        """Export the current sprite sheet."""
        if not self.sprite_path or not os.path.exists(self.sprite_path):
            return
            
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Export Sprite Sheet", "", "PNG (*.png)"
        )
        
        if file_path:
            # Export the sprite sheet
            try:
                import shutil
                shutil.copy(self.sprite_path, file_path)
            except Exception as e:
                print(f"Error exporting sprite sheet: {e}")

class CharacterEditorTab(QWidget):
    """Tab for editing game characters with visual elements."""
    
    def __init__(self, game_data):
        super().__init__()
        self.game_data = game_data
        self.current_character = None
        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(self.update_animation_frame)
        self.animation_frame = 0
        self.animation_frames = []
        self.current_animation = "front"
        
        # Define job name to sprite index mapping
        self.job_sprite_map = {
            "Fighter": 0,
            "Thief": 1,
            "Black Mage": 2,
            "White Mage": 3,
            "Red Mage": 4,
            "Monk": 5,
            "Knight": 6  # If there's a Knight class
        }
        
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
        
        # Character image - Enhanced with animation support
        self.image_box = QGroupBox("Character Sprite Viewer")
        image_layout = QVBoxLayout()
        
        # Character image - Now using actual sprite size
        self.character_image = QLabel()
        self.character_image.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # Set to default walking sprite size, will be updated when loaded
        self.character_image.setFixedSize(54, 54)  # Match sprite size
        self.character_image.setScaledContents(False)  # Don't scale to preserve pixel art quality
        image_layout.addWidget(self.character_image)
        
        # Animation controls
        animation_layout = QHBoxLayout()
        
        # Animation type dropdown
        animation_layout.addWidget(QLabel("Animation:"))
        self.animation_combo = QComboBox()
        self.animation_combo.addItems([
            "Front (Standing)", "Front (Walking)", 
            "Back (Standing)", "Back (Walking)",
            "Left (Standing)", "Left (Walking)",
            "Right (Standing)", "Right (Walking)",
            "Battle", "Attack", "Magic", "Damaged", "Win"
        ])
        self.animation_combo.currentIndexChanged.connect(self.on_animation_changed)
        animation_layout.addWidget(self.animation_combo)
        
        # Toggle animation button
        self.animate_button = QPushButton("Toggle Animation")
        self.animate_button.setCheckable(True)
        self.animate_button.toggled.connect(self.toggle_animation)
        animation_layout.addWidget(self.animate_button)
        
        image_layout.addLayout(animation_layout)
        
        # Add a button to open the full sprite sheet
        self.view_sprite_button = QPushButton("View/Edit Full Sprite Sheet")
        self.view_sprite_button.clicked.connect(self.open_sprite_dialog)
        image_layout.addWidget(self.view_sprite_button)
        
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
            
        # Update sprite property based on job using the sprite mapping
        sprite_id = self.job_sprite_map.get(job_name, index)  # Fallback to index if mapping not found
        sprite_base = f"job{sprite_id}"
        
        if 'sprite' not in self.current_character or not self.current_character['sprite']:
            self.current_character['sprite'] = sprite_base
        elif self.current_character['sprite'].startswith('job'):
            # Only update if it's a job-based sprite (preserves custom sprites)
            self.current_character['sprite'] = sprite_base
        
        # Reload the character image to show the new job's sprite
        self.load_character_image()
        
        # Mark the game data as changed
        self.game_data.mark_as_changed()
    
    def on_animation_changed(self, index):
        """Handle changes to the animation dropdown."""
        animation_map = {
            0: ("front", False),    # Front (Standing)
            1: ("front", True),     # Front (Walking)
            2: ("back", False),     # Back (Standing)
            3: ("back", True),      # Back (Walking)
            4: ("left", False),     # Left (Standing)
            5: ("left", True),      # Left (Walking)
            6: ("right", False),    # Right (Standing)
            7: ("right", True),     # Right (Walking)
            8: ("battle", False),   # Battle
            9: ("attack", False),   # Attack
            10: ("magic", False),   # Magic
            11: ("damage", False),  # Damaged
            12: ("win", False),     # Win
        }
        
        if index in animation_map:
            self.current_animation, should_animate = animation_map[index]
            self.load_character_image()
            
            # If walking animation is selected, start the animation
            if should_animate and not self.animate_button.isChecked():
                self.animate_button.setChecked(True)
            elif not should_animate and self.animate_button.isChecked():
                self.animate_button.setChecked(False)
    
    def toggle_animation(self, enabled):
        """Start or stop the sprite animation."""
        if enabled:
            self.animation_timer.start(300)  # Animation speed (300ms)
        else:
            self.animation_timer.stop()
    
    def update_animation_frame(self):
        """Update the animation frame for the sprite."""
        if not self.current_character:
            return
            
        # Get the next frame index
        self.animation_frame = (self.animation_frame + 1) % len(self.animation_frames)
        
        # Display the current frame
        if self.animation_frames:
            self.character_image.setPixmap(self.animation_frames[self.animation_frame])
    
    def load_character_image(self):
        """Load the character image based on the sprite and animation type."""
        if not self.current_character:
            return
            
        # Stop any ongoing animation
        if self.animation_timer.isActive():
            self.animation_timer.stop()
            
        # Reset animation frames
        self.animation_frames = []
        self.animation_frame = 0
            
        # Get the job information
        job_id = self.current_character.get('job', 0)
        if isinstance(job_id, list) and len(job_id) > 0:
            job_id = job_id[0]
            
        # Get job name
        job_name = ""
        if 'job_name' in self.current_character and self.current_character['job_name']:
            job_name = self.current_character['job_name']
        elif isinstance(job_id, int):
            job_names = [self.job_combo.itemText(i) for i in range(self.job_combo.count())]
            if 0 <= job_id < len(job_names):
                job_name = job_names[job_id]
        
        # Determine the sprite filename based on the character's sprite property or job
        sprite_name = ""
        sprite_id = None
        
        # First check if there's a sprite property and use that
        if 'sprite' in self.current_character and self.current_character['sprite']:
            if self.current_character['sprite'].startswith('job'):
                try:
                    # Extract sprite ID from job{id}
                    sprite_id = int(self.current_character['sprite'].replace('job', ''))
                    sprite_name = f"job{sprite_id}.png"
                except ValueError:
                    sprite_name = f"{self.current_character['sprite']}.png"
            else:
                sprite_name = f"{self.current_character['sprite']}.png"
        else:
            # Map job to correct sprite index
            if job_name and job_name in self.job_sprite_map:
                sprite_id = self.job_sprite_map[job_name]
            else:
                # Fallback to job ID matching sprite ID
                sprite_id = job_id
                
            sprite_name = f"job{sprite_id}.png"
        
        # Add .png extension if not present
        if not sprite_name.endswith('.png'):
            sprite_name += '.png'
            
        sprite_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 
                                  '..', '..', '..', 'img', 'pc', sprite_name)
        
        self.current_sprite_path = sprite_path  # Save for dialog use
        
        # Create QPixmap for the sprite
        pixmap = QPixmap(sprite_path)
        if pixmap.isNull():
            # If image not found, try a default
            default_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 
                                      '..', '..', '..', 'img', 'pc', 'job0.png')
            pixmap = QPixmap(default_path)
            self.current_sprite_path = default_path
        
        # Handle different animation types and adjust label size accordingly
        is_battle_animation = False
        frame_width = 54  # Default walking sprite width
        frame_height = 54  # Default walking sprite height
        
        if "walking" in self.animation_combo.currentText().lower():
            # Create animation frames
            if "front" in self.current_animation:
                # Extract the two frames from the sprite sheet for front walking
                frame1 = pixmap.copy(0, 96, 54, 54)  # Frame 1 position
                frame2 = pixmap.copy(54, 96, 54, 54)  # Frame 2 position
                self.animation_frames = [frame1, frame2]
            elif "back" in self.current_animation:
                frame1 = pixmap.copy(108, 96, 54, 54)  # Frame 1 position
                frame2 = pixmap.copy(162, 96, 54, 54)  # Frame 2 position
                self.animation_frames = [frame1, frame2]
            elif "left" in self.current_animation:
                frame1 = pixmap.copy(324, 96, 54, 54)  # Frame 1 position
                frame2 = pixmap.copy(378, 96, 54, 54)  # Frame 2 position
                self.animation_frames = [frame1, frame2]
            elif "right" in self.current_animation:
                frame1 = pixmap.copy(216, 96, 54, 54)  # Frame 1 position
                frame2 = pixmap.copy(270, 96, 54, 54)  # Frame 2 position
                self.animation_frames = [frame1, frame2]
                
            # Start with the first frame
            if self.animation_frames:
                self.character_image.setPixmap(self.animation_frames[0])
                # Start animation if button is checked
                if self.animate_button.isChecked():
                    self.animation_timer.start(300)
        else:
            # Static images for different poses/states
            if self.current_animation == "front":
                frame = pixmap.copy(0, 96, 54, 54)
            elif self.current_animation == "back":
                frame = pixmap.copy(108, 96, 54, 54)
            elif self.current_animation == "left":
                frame = pixmap.copy(324, 96, 54, 54)
            elif self.current_animation == "right":
                frame = pixmap.copy(216, 96, 54, 54)
            elif self.current_animation == "battle":
                frame = pixmap.copy(0, 0, 96, 96)
                is_battle_animation = True
                frame_width = 96
                frame_height = 96
            elif self.current_animation == "attack":
                frame = pixmap.copy(96, 0, 96, 96)
                is_battle_animation = True
                frame_width = 96
                frame_height = 96
            elif self.current_animation == "magic":
                frame = pixmap.copy(192, 0, 96, 96)
                is_battle_animation = True
                frame_width = 96
                frame_height = 96
            elif self.current_animation == "damage":
                frame = pixmap.copy(288, 0, 96, 96)
                is_battle_animation = True
                frame_width = 96
                frame_height = 96
            elif self.current_animation == "win":
                frame = pixmap.copy(384, 0, 96, 96)
                is_battle_animation = True
                frame_width = 96
                frame_height = 96
            else:
                # Default to front view
                frame = pixmap.copy(0, 96, 54, 54)
                
            self.character_image.setPixmap(frame)
        
        # Update the QLabel size to match the sprite's natural dimensions
        self.character_image.setFixedSize(frame_width, frame_height)
            
    def open_sprite_dialog(self):
        """Open the sprite sheet dialog for viewing and editing."""
        if hasattr(self, 'current_sprite_path'):
            dialog = SpriteSheetDialog(self, self.current_sprite_path)
            if dialog.exec():
                # Reload the character image if changes were made
                self.load_character_image()
    
    def enable_details(self, enabled):
        """Enable or disable the details widgets."""
        self.details_tabs.setEnabled(enabled)
        self.image_box.setEnabled(enabled)
        self.remove_button.setEnabled(enabled)
        
    def add_character(self):
        """Add a new character."""
        # Get default job name and sprite ID
        default_job_name = "Fighter"
        default_job_index = 0
        default_sprite_id = self.job_sprite_map.get(default_job_name, default_job_index)
        
        # Create a new character with default values
        new_character = {
            'name': "New Character",
            'job': default_job_index,  # Use index for consistency
            'job_name': default_job_name,  # Add job_name field
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
            'sprite': f"job{default_sprite_id}"  # Use correctly mapped sprite ID
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
        job_index = self.job_combo.currentIndex()
        
        if isinstance(self.current_character['job'], int):
            # If the original job was an int, store it as an int
            self.current_character['job'] = job_index
            # Also update job_name if it exists
            if 'job_name' in self.current_character:
                self.current_character['job_name'] = job_name
        else:
            # Otherwise store it as a string
            self.current_character['job'] = job_name
            
        # Update sprite property based on job using the sprite mapping
        sprite_id = self.job_sprite_map.get(job_name, job_index)  # Fallback to index if mapping not found
        sprite_base = f"job{sprite_id}"
        
        if 'sprite' not in self.current_character or not self.current_character['sprite']:
            self.current_character['sprite'] = sprite_base
        elif self.current_character['sprite'].startswith('job'):
            # Only update if it's a job-based sprite
            self.current_character['sprite'] = sprite_base
        
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