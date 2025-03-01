import os
import math  # Import math for trig functions
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QListWidget, 
                           QGroupBox, QFormLayout, QLabel, QLineEdit, 
                           QPushButton, QListWidgetItem, QComboBox, QSpinBox)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QPixmap, QPainter, QColor, QFont, QPen, QBrush, QLinearGradient, QMovie

class SpellEditorTab(QWidget):
    """Tab for editing game spells with visual elements."""
    
    def __init__(self, game_data):
        super().__init__()
        self.game_data = game_data
        self.current_spell = None
        self.current_animation = {}  # Initialize as an empty dict
        
        # Define spell type colors for visualization
        self.spell_colors = {
            "Fire": (QColor(255, 100, 0), QColor(255, 200, 0)),    # Orange to yellow
            "Ice": (QColor(100, 200, 255), QColor(200, 240, 255)),  # Light blue to white
            "Lightning": (QColor(255, 255, 0), QColor(200, 200, 255)),  # Yellow to light purple
            "Earth": (QColor(139, 69, 19), QColor(160, 120, 60)),   # Brown to tan
            "Poison": (QColor(0, 180, 0), QColor(150, 255, 150)),   # Green to light green
            "Heal": (QColor(255, 255, 255), QColor(100, 255, 100)), # White to light green
            "Cure": (QColor(200, 255, 200), QColor(255, 255, 255)), # Light green to white
            "Buff": (QColor(200, 200, 255), QColor(255, 255, 255)),  # Light blue to white
            "Light": (QColor(255, 255, 200), QColor(255, 255, 100)), # Pale yellow to bright yellow
            "Status": (QColor(200, 100, 200), QColor(255, 180, 255))  # Purple to pink
        }
        
        self.init_ui()
        
    def init_ui(self):
        """Initialize the user interface."""
        # Main layout
        main_layout = QHBoxLayout(self)
        
        # Left side - Spell list
        left_layout = QVBoxLayout()
        
        # Spell list
        self.spell_list = QListWidget()
        self.spell_list.currentItemChanged.connect(self.on_spell_selected)
        left_layout.addWidget(QLabel("Spells:"))
        left_layout.addWidget(self.spell_list)
        
        # Add/Remove buttons
        button_layout = QHBoxLayout()
        self.add_button = QPushButton("Add Spell")
        self.add_button.clicked.connect(self.add_spell)
        self.remove_button = QPushButton("Remove Spell")
        self.remove_button.clicked.connect(self.remove_spell)
        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.remove_button)
        left_layout.addLayout(button_layout)
        
        # Right side - Spell details
        right_layout = QVBoxLayout()
        
        # Spell details
        self.details_box = QGroupBox("Spell Details")
        details_layout = QFormLayout()
        
        # Name field
        self.name_edit = QLineEdit()
        details_layout.addRow("Name:", self.name_edit)
        
        # Type field
        self.type_combo = QComboBox()
        # Ensure these spell types match the ones defined in self.spell_colors
        self.type_combo.addItems([
            "Fire", "Ice", "Lightning", "Earth", 
            "Poison", "Heal", "Cure", "Buff",
            "Light", "Status"
        ])
        self.type_combo.currentTextChanged.connect(self.on_type_changed)
        details_layout.addRow("Type:", self.type_combo)
        
        # Power field
        self.power_spin = QSpinBox()
        self.power_spin.setRange(1, 100)
        details_layout.addRow("Power:", self.power_spin)
        
        # MP Cost field
        self.mp_cost_spin = QSpinBox()
        self.mp_cost_spin.setRange(1, 50)
        details_layout.addRow("MP Cost:", self.mp_cost_spin)
        
        # Target type
        self.target_combo = QComboBox()
        self.target_combo.addItems([
            "Single Enemy", "All Enemies", "Single Ally", "All Allies", "Self"
        ])
        details_layout.addRow("Target:", self.target_combo)
        
        # Save button
        self.save_button = QPushButton("Save Changes")
        self.save_button.clicked.connect(self.save_spell)
        details_layout.addRow("", self.save_button)
        
        self.details_box.setLayout(details_layout)
        right_layout.addWidget(self.details_box)
        
        # Spell preview
        self.preview_box = QGroupBox("Spell Preview")
        preview_layout = QVBoxLayout()
        
        # Spell effect preview
        self.spell_effect = QLabel()
        self.spell_effect.setMinimumSize(300, 200)
        self.spell_effect.setAlignment(Qt.AlignmentFlag.AlignCenter)
        preview_layout.addWidget(self.spell_effect)
        
        # Spell animation preview
        self.animation_box = QGroupBox("Spell Animation")
        animation_layout = QHBoxLayout()
        
        # Player effect animation
        self.player_effect_label = QLabel("Player Effect:")
        self.player_effect = QLabel()
        self.player_effect.setMinimumSize(64, 64)
        self.player_effect.setAlignment(Qt.AlignmentFlag.AlignCenter)
        animation_layout.addWidget(self.player_effect_label)
        animation_layout.addWidget(self.player_effect)
        
        # Enemy effect animation
        self.enemy_effect_label = QLabel("Enemy Effect:")
        self.enemy_effect = QLabel()
        self.enemy_effect.setMinimumSize(64, 64)
        self.enemy_effect.setAlignment(Qt.AlignmentFlag.AlignCenter)
        animation_layout.addWidget(self.enemy_effect_label)
        animation_layout.addWidget(self.enemy_effect)
        
        self.animation_box.setLayout(animation_layout)
        preview_layout.addWidget(self.animation_box)
        
        self.preview_box.setLayout(preview_layout)
        right_layout.addWidget(self.preview_box)
        
        # Add layouts to main layout
        main_layout.addLayout(left_layout, 1)
        main_layout.addLayout(right_layout, 2)
        
        # Disable details until a spell is selected
        self.enable_details(False)
        
    def update_data(self):
        """Update the UI with the latest game data."""
        # Clear the list
        self.spell_list.clear()
        
        print("\n==== SPELL EDITOR DATA UPDATE ====")
        print(f"Loading {len(self.game_data.spells)} spells into editor")
        
        # Add spells to the list
        for spell in self.game_data.spells:
            self.spell_list.addItem(spell['name'])
            # Print details of each spell for debugging
            print(f"📋 Loaded spell: {spell['name']}")
            print(f"  - Type: {spell.get('type', 'Unknown')}")
            print(f"  - Power: {spell.get('power', 'Unknown')}")
            print(f"  - MP Cost: {spell.get('mp_cost', 'Unknown')}")
            print(f"  - Target: {spell.get('target', 'Unknown')}")
            
        # Clear the current selection
        self.current_spell = None
        self.enable_details(False)
        print("==== SPELL EDITOR UPDATE COMPLETED ====\n")
        
    def on_spell_selected(self, current, previous):
        """Handle selection of a spell in the list."""
        # Clear any existing animations first to prevent issues
        self.clear_animations()
        
        if not current:
            self.current_spell = None
            self.enable_details(False)
            print("Deselected current spell")
            return
            
        try:
            # Get the selected spell
            spell_name = current.text()
            self.current_spell = self.game_data.get_spell_by_name(spell_name)
            
            print(f"\n==== SPELL SELECTED: {spell_name} ====")
            
            if self.current_spell:
                # Print details for debugging
                print(f"Found spell details:")
                for key, value in self.current_spell.items():
                    print(f"  - {key}: {value}")
                    
                # Update the details
                self.name_edit.setText(self.current_spell['name'])
                
                # Set the type
                spell_type = self.current_spell.get('type', 'Fire')
                index = self.type_combo.findText(spell_type)
                if index >= 0:
                    self.type_combo.setCurrentIndex(index)
                    print(f"✅ Set type to: {spell_type}")
                else:
                    # If type doesn't match any in the combo, default to first option
                    self.type_combo.setCurrentIndex(0)
                    # Also update the spell with the correct type
                    self.current_spell['type'] = self.type_combo.currentText()
                    print(f"⚠️ Unknown type: {spell_type}, defaulted to: {self.type_combo.currentText()}")
                    
                # Set the power
                self.power_spin.setValue(self.current_spell.get('power', 10))
                print(f"✅ Set power to: {self.current_spell.get('power', 10)}")
                
                # Set the MP cost
                self.mp_cost_spin.setValue(self.current_spell.get('mp_cost', 5))
                print(f"✅ Set MP cost to: {self.current_spell.get('mp_cost', 5)}")
                
                # Set the target (with fallback to defaults)
                target = self.current_spell.get('target', 'Single Enemy')
                if target not in ["Single Enemy", "All Enemies", "Single Ally", "All Allies", "Self"]:
                    # Convert old target format if needed
                    if target == 'Enemy':
                        target = 'Single Enemy'
                        print(f"⚠️ Converted target from 'Enemy' to 'Single Enemy'")
                    elif target == 'Ally':
                        target = 'Single Ally'
                        print(f"⚠️ Converted target from 'Ally' to 'Single Ally'")
                    else:
                        # Default based on spell type
                        if spell_type in ['Heal', 'Cure', 'Buff']:
                            target = 'Single Ally'
                        else:
                            target = 'Single Enemy'
                        print(f"⚠️ Unknown target: {self.current_spell.get('target')}, defaulted to: {target}")
                    # Update the spell with the corrected target
                    self.current_spell['target'] = target
                    
                index = self.target_combo.findText(target)
                if index >= 0:
                    self.target_combo.setCurrentIndex(index)
                    print(f"✅ Set target to: {target}")
                else:
                    # If target doesn't match any in the combo, default to an appropriate option
                    if spell_type in ['Heal', 'Cure', 'Buff']:
                        self.target_combo.setCurrentIndex(2)  # Single Ally
                        print(f"⚠️ Invalid target, defaulted to 'Single Ally' for {spell_type} spell")
                    else:
                        self.target_combo.setCurrentIndex(0)  # Single Enemy
                        print(f"⚠️ Invalid target, defaulted to 'Single Enemy' for {spell_type} spell")
                    
                # Generate the spell preview
                self.generate_spell_preview()
                print("✅ Generated spell preview")
                
                # Load spell animations
                self.load_spell_animations()
                print("✅ Loaded spell animations")
                
                # Enable the details
                self.enable_details(True)
                print("✅ Enabled spell details panel")
            else:
                print(f"❌ Could not find spell with name: {spell_name}")
                self.enable_details(False)
            
            print(f"==== SPELL SELECTION COMPLETED ====\n")
        
        except Exception as e:
            print(f"❌ Error in on_spell_selected: {str(e)}")
            self.clear_animations()
            self.enable_details(False)
        
    def on_type_changed(self, spell_type):
        """Handle change of spell type to update the preview."""
        if self.current_spell:
            # Update the current spell with the new type
            self.current_spell['type'] = spell_type
            
            # For healing spells, suggest an appropriate target
            if spell_type in ['Heal', 'Cure']:
                index = self.target_combo.findText('Single Ally')
                if index >= 0 and self.current_spell.get('target', '') == 'Single Enemy':
                    self.target_combo.setCurrentIndex(index)
                    self.current_spell['target'] = 'Single Ally'
            
            # For offensive spells, suggest an appropriate target
            elif spell_type in ['Fire', 'Ice', 'Lightning', 'Earth', 'Poison', 'Light']:
                index = self.target_combo.findText('Single Enemy')
                if index >= 0 and self.current_spell.get('target', '') == 'Single Ally':
                    self.target_combo.setCurrentIndex(index)
                    self.current_spell['target'] = 'Single Enemy'
                    
            # For status spells, suggest an appropriate target
            elif spell_type in ['Status']:
                index = self.target_combo.findText('Single Enemy')
                if index >= 0 and self.current_spell.get('target', '') == 'Single Ally':
                    self.target_combo.setCurrentIndex(index)
                    self.current_spell['target'] = 'Single Enemy'
                    
            # Update the preview
            self.generate_spell_preview()
            
    def clear_animations(self):
        """Clear and stop any running animations."""
        try:
            # Stop any currently running animations
            if self.current_animation:
                for movie in self.current_animation.values():
                    if movie:
                        movie.stop()
            
            # Reset animation state
            self.current_animation = {}
            
            # Clear animation labels
            if hasattr(self, 'player_effect'):
                self.player_effect.clear()
            if hasattr(self, 'enemy_effect'):
                self.enemy_effect.clear()
                
        except Exception as e:
            print(f"❌ Error clearing animations: {str(e)}")
            
    def load_spell_animations(self):
        """Load spell animations from image files."""
        try:
            # Clear any existing animations first
            self.clear_animations()
            
            # Check if the spell has image files
            if not self.current_spell or 'image_files' not in self.current_spell:
                print("No image files found for spell")
                return
            
            image_files = self.current_spell['image_files']
            
            # Load player effect animation if available
            if 'player_effect' in image_files:
                player_file = image_files['player_effect']
                player_path = os.path.join("img", "sp", player_file)
                
                if os.path.exists(player_path):
                    try:
                        movie = QMovie(player_path)
                        if movie.isValid():  # Check if the movie is valid
                            movie.setScaledSize(QSize(64, 64))
                            self.player_effect.setMovie(movie)
                            movie.start()
                            self.current_animation['player'] = movie
                            print(f"✅ Loaded player effect animation: {player_file}")
                        else:
                            print(f"❌ Invalid animation file: {player_path}")
                    except Exception as e:
                        print(f"❌ Error loading player animation: {str(e)}")
                else:
                    print(f"❌ Player effect file not found: {player_path}")
            
            # Load enemy effect animation if available
            if 'enemy_effect' in image_files:
                enemy_file = image_files['enemy_effect']
                enemy_path = os.path.join("img", "sp", enemy_file)
                
                if os.path.exists(enemy_path):
                    try:
                        movie = QMovie(enemy_path)
                        if movie.isValid():  # Check if the movie is valid
                            movie.setScaledSize(QSize(64, 64))
                            self.enemy_effect.setMovie(movie)
                            movie.start()
                            self.current_animation['enemy'] = movie
                            print(f"✅ Loaded enemy effect animation: {enemy_file}")
                        else:
                            print(f"❌ Invalid animation file: {enemy_path}")
                    except Exception as e:
                        print(f"❌ Error loading enemy animation: {str(e)}")
                else:
                    print(f"❌ Enemy effect file not found: {enemy_path}")
        
        except Exception as e:
            print(f"❌ Error in load_spell_animations: {str(e)}")
            self.clear_animations()
        
    def generate_spell_preview(self):
        """Generate a preview image of the spell effect."""
        if not self.current_spell:
            return
            
        # Get the spell type
        spell_type = self.type_combo.currentText()
        
        # Create a pixmap for the spell effect
        pixmap = QPixmap(300, 200)
        pixmap.fill(Qt.GlobalColor.transparent)
        
        # Create a painter
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Get the spell colors with fallback for unknown types
        default_colors = (QColor(200, 200, 200), QColor(255, 255, 255))  # Default gray to white
        start_color, end_color = self.spell_colors.get(spell_type, default_colors)
        
        # Draw based on spell type
        if spell_type in ["Fire", "Ice", "Lightning", "Earth", "Poison", "Light"]:
            # Offensive spell - draw as a projectile
            self.draw_offensive_spell(painter, start_color, end_color)
        elif spell_type in ["Heal", "Cure"]:
            # Healing spell - draw as a glow
            self.draw_healing_spell(painter, start_color, end_color)
        elif spell_type == "Status":
            # Status spell - draw as a swirl
            self.draw_status_spell(painter, start_color, end_color)
        else:  # Buff or other types
            # Buff spell - draw as an aura
            self.draw_buff_spell(painter, start_color, end_color)
            
        # Draw the spell name
        painter.setPen(QPen(Qt.GlobalColor.white))
        font = QFont("Arial", 12, QFont.Weight.Bold)
        painter.setFont(font)
        painter.drawText(0, 0, 300, 30, 
                        Qt.AlignmentFlag.AlignCenter, self.current_spell.get('name', 'Unknown Spell'))
        
        # Draw the spell power
        power_text = f"Power: {self.power_spin.value()}"
        painter.drawText(0, 170, 300, 30, 
                        Qt.AlignmentFlag.AlignCenter, power_text)
        
        # If the spell has a flash color, add it as a border
        if 'flash_color' in self.current_spell:
            flash_color = QColor(self.current_spell['flash_color'])
            painter.setPen(QPen(flash_color, 4))
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawRect(5, 5, 290, 190)
            
        # End painting
        painter.end()
        
        # Set the pixmap
        self.spell_effect.setPixmap(pixmap)
        
    def draw_offensive_spell(self, painter, start_color, end_color):
        """Draw an offensive spell effect."""
        # Create a gradient
        gradient = QLinearGradient(150, 50, 150, 150)
        gradient.setColorAt(0, start_color)
        gradient.setColorAt(1, end_color)
        
        # Draw a projectile
        painter.setPen(QPen(Qt.GlobalColor.black, 1))
        painter.setBrush(QBrush(gradient))
        
        # Draw the main projectile
        painter.drawEllipse(100, 50, 100, 100)
        
        # Draw some particles
        for i in range(5):
            x = 120 + i * 15
            y = 70 + i * 10
            size = 20 - i * 3
            painter.drawEllipse(x, y, size, size)
            
    def draw_healing_spell(self, painter, start_color, end_color):
        """Draw a healing spell effect."""
        # Create a gradient
        gradient = QLinearGradient(150, 50, 150, 150)
        gradient.setColorAt(0, start_color)
        gradient.setColorAt(1, end_color)
        
        # Draw a glow
        painter.setPen(QPen(Qt.GlobalColor.transparent))
        painter.setBrush(QBrush(gradient))
        
        # Draw concentric circles
        for i in range(5):
            opacity = 0.8 - i * 0.15
            painter.setOpacity(opacity)
            size = 100 - i * 15
            # Convert float to int for drawing functions
            x = int(150 - size/2)
            y = int(100 - size/2)
            size = int(size)
            painter.drawEllipse(x, y, size, size)
            
        # Reset opacity
        painter.setOpacity(1.0)
        
        # Draw a cross in the center
        painter.setPen(QPen(Qt.GlobalColor.white, 3))
        painter.drawLine(140, 100, 160, 100)
        painter.drawLine(150, 90, 150, 110)
            
    def draw_buff_spell(self, painter, start_color, end_color):
        """Draw a buff spell effect."""
        # Create a gradient
        gradient = QLinearGradient(150, 50, 150, 150)
        gradient.setColorAt(0, start_color)
        gradient.setColorAt(1, end_color)
        
        # Draw an aura
        painter.setPen(QPen(Qt.GlobalColor.transparent))
        
        # Draw a character silhouette
        painter.setBrush(QBrush(QColor(50, 50, 50)))
        painter.drawEllipse(125, 60, 50, 50)  # Head
        painter.drawRect(135, 110, 30, 60)    # Body
        
        # Draw the aura
        painter.setBrush(QBrush(gradient))
        painter.setOpacity(0.5)
        
        # Draw aura waves
        for i in range(3):
            size = 80 + i * 20
            # Convert float to int for drawing functions
            x = int(150 - size/2)
            y = int(100 - size/2)
            size = int(size)
            painter.drawEllipse(x, y, size, size)
            
        # Reset opacity
        painter.setOpacity(1.0)
        
    def draw_status_spell(self, painter, start_color, end_color):
        """Draw a status effect spell."""
        # Create a gradient
        gradient = QLinearGradient(150, 50, 150, 150)
        gradient.setColorAt(0, start_color)
        gradient.setColorAt(1, end_color)
        
        # Draw an enemy silhouette
        painter.setPen(QPen(Qt.GlobalColor.transparent))
        painter.setBrush(QBrush(QColor(50, 50, 50)))
        painter.drawEllipse(125, 60, 50, 50)  # Head
        painter.drawRect(135, 110, 30, 60)    # Body
        
        # Draw status effect symbols
        painter.setPen(QPen(start_color, 3))
        painter.setOpacity(0.8)
        
        # Draw swirls and symbols around the target
        center_x, center_y = 150, 100
        radius = 60
        
        # Draw symbols at regular intervals around the target
        for i in range(0, 360, 45):
            angle_rad = i * math.pi / 180
            x = int(center_x + radius * 0.7 * math.cos(angle_rad))
            y = int(center_y + radius * 0.7 * math.sin(angle_rad))
            
            # Draw small stars or symbols
            star_size = 15
            painter.setBrush(QBrush(end_color))
            painter.drawEllipse(x - star_size//2, y - star_size//2, star_size, star_size)
        
        # Draw a few Z letters for sleep effect
        font = QFont("Arial", 14, QFont.Weight.Bold)
        painter.setFont(font)
        painter.drawText(100, 50, 30, 30, Qt.AlignmentFlag.AlignCenter, "Z")
        painter.drawText(180, 70, 30, 30, Qt.AlignmentFlag.AlignCenter, "Z")
        painter.drawText(80, 100, 30, 30, Qt.AlignmentFlag.AlignCenter, "Z")
        
        # Reset opacity
        painter.setOpacity(1.0)
        
    def enable_details(self, enabled):
        """Enable or disable the details widgets."""
        self.details_box.setEnabled(enabled)
        self.preview_box.setEnabled(enabled)
        self.remove_button.setEnabled(enabled)
        
    def add_spell(self):
        """Add a new spell."""
        # Create a new spell with default values
        new_spell = {
            'name': "New Spell",
            'type': "Fire",
            'power': 10,
            'mp_cost': 5,
            'target': "Single Enemy",
            'description': "A basic fire spell that deals damage to a single enemy."
        }
        
        # Add to the game data
        self.game_data.spells.append(new_spell)
        
        # Mark data as changed
        self.game_data.mark_as_changed()
        
        # Update the UI
        self.update_data()
        
        # Select the new spell
        for i in range(self.spell_list.count()):
            if self.spell_list.item(i).text() == new_spell['name']:
                self.spell_list.setCurrentRow(i)
                break
                
    def remove_spell(self):
        """Remove the selected spell."""
        if not self.current_spell:
            return
            
        # Remove from the game data
        self.game_data.spells.remove(self.current_spell)
        
        # Update the UI
        self.update_data()
        
    def save_spell(self):
        """Save changes to the selected spell."""
        if not self.current_spell:
            return
            
        # Update the spell with the form values
        self.current_spell['name'] = self.name_edit.text()
        self.current_spell['type'] = self.type_combo.currentText()
        self.current_spell['power'] = self.power_spin.value()
        self.current_spell['mp_cost'] = self.mp_cost_spin.value()
        self.current_spell['target'] = self.target_combo.currentText()
        
        # Add a description if it doesn't exist
        if 'description' not in self.current_spell:
            spell_type = self.current_spell['type']
            power = self.current_spell['power']
            target = self.current_spell['target']
            
            if spell_type in ['Heal', 'Cure']:
                self.current_spell['description'] = f"A healing spell that restores HP to {target.lower()}."
            elif spell_type == 'Buff':
                self.current_spell['description'] = f"A support spell that enhances abilities of {target.lower()}."
            else:
                self.current_spell['description'] = f"An offensive {spell_type.lower()} spell that deals damage to {target.lower()}."
        
        # Mark the game data as changed
        self.game_data.mark_as_changed()
        
        # Update the UI
        self.update_data()
        
        # Reselect the spell
        for i in range(self.spell_list.count()):
            if self.spell_list.item(i).text() == self.current_spell['name']:
                self.spell_list.setCurrentRow(i)
                break
                
    def save_changes(self):
        """Save all changes to the game data."""
        # This would be called from the main window
        return self.game_data.save_to_file() 