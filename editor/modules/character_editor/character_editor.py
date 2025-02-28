import os
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QListWidget, 
                           QGroupBox, QFormLayout, QLabel, QLineEdit, 
                           QSpinBox, QComboBox, QPushButton)
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
        
        # Character details
        self.details_box = QGroupBox("Character Details")
        details_layout = QFormLayout()
        
        # Name field
        self.name_edit = QLineEdit()
        details_layout.addRow("Name:", self.name_edit)
        
        # Level field
        self.level_spin = QSpinBox()
        self.level_spin.setRange(1, 99)
        details_layout.addRow("Level:", self.level_spin)
        
        # HP field
        self.hp_spin = QSpinBox()
        self.hp_spin.setRange(1, 9999)
        details_layout.addRow("HP:", self.hp_spin)
        
        # MP field
        self.mp_spin = QSpinBox()
        self.mp_spin.setRange(0, 999)
        details_layout.addRow("MP:", self.mp_spin)
        
        # Save button
        self.save_button = QPushButton("Save Changes")
        self.save_button.clicked.connect(self.save_character)
        details_layout.addRow("", self.save_button)
        
        self.details_box.setLayout(details_layout)
        right_layout.addWidget(self.details_box)
        
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
        """Handle selection of a character in the list."""
        if not current:
            self.current_character = None
            self.enable_details(False)
            return
            
        # Get the selected character
        character_name = current.text()
        self.current_character = self.game_data.get_character_by_name(character_name)
        
        if self.current_character:
            # Update the details
            self.name_edit.setText(self.current_character['name'])
            self.level_spin.setValue(self.current_character['level'])
            self.hp_spin.setValue(self.current_character['hp'])
            self.mp_spin.setValue(self.current_character['mp'])
            
            # Set the job
            job_index = self.job_combo.findText(self.current_character['job'])
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
            
        # Update the character's job
        self.current_character['job'] = self.job_combo.currentText()
        
        # Update the sprite based on job
        job_index = index
        if job_index >= 0 and job_index < 8:  # Assuming 8 jobs
            self.current_character['sprite'] = f"job{job_index}.png"
            
        # Reload the character image
        self.load_character_image()
        
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
        self.details_box.setEnabled(enabled)
        self.image_box.setEnabled(enabled)
        self.remove_button.setEnabled(enabled)
        
    def add_character(self):
        """Add a new character."""
        # Create a new character with default values
        new_character = {
            'name': "New Character",
            'job': "Fighter",
            'level': 1,
            'hp': 100,
            'mp': 50,
            'sprite': "job0.png"
        }
        
        # Add to the game data
        self.game_data.characters.append(new_character)
        
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
        
        # Update the UI
        self.update_data()
        
    def save_character(self):
        """Save changes to the selected character."""
        if not self.current_character:
            return
            
        # Update the character with the form values
        self.current_character['name'] = self.name_edit.text()
        self.current_character['level'] = self.level_spin.value()
        self.current_character['hp'] = self.hp_spin.value()
        self.current_character['mp'] = self.mp_spin.value()
        self.current_character['job'] = self.job_combo.currentText()
        
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