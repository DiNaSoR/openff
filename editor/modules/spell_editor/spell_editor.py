import os
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QListWidget, 
                           QGroupBox, QFormLayout, QLabel, QLineEdit, 
                           QPushButton, QListWidgetItem, QComboBox, QSpinBox)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap, QPainter, QColor, QFont, QPen, QBrush, QLinearGradient

class SpellEditorTab(QWidget):
    """Tab for editing game spells with visual elements."""
    
    def __init__(self, game_data):
        super().__init__()
        self.game_data = game_data
        self.current_spell = None
        
        # Define spell type colors for visualization
        self.spell_colors = {
            "Fire": (QColor(255, 100, 0), QColor(255, 200, 0)),    # Orange to yellow
            "Ice": (QColor(100, 200, 255), QColor(200, 240, 255)),  # Light blue to white
            "Lightning": (QColor(255, 255, 0), QColor(200, 200, 255)),  # Yellow to light purple
            "Earth": (QColor(139, 69, 19), QColor(160, 120, 60)),   # Brown to tan
            "Poison": (QColor(0, 180, 0), QColor(150, 255, 150)),   # Green to light green
            "Heal": (QColor(255, 255, 255), QColor(100, 255, 100)), # White to light green
            "Cure": (QColor(200, 255, 200), QColor(255, 255, 255)), # Light green to white
            "Buff": (QColor(200, 200, 255), QColor(255, 255, 255))  # Light blue to white
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
        self.type_combo.addItems([
            "Fire", "Ice", "Lightning", "Earth", 
            "Poison", "Heal", "Cure", "Buff"
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
        
        # Add spells to the list
        for spell in self.game_data.spells:
            self.spell_list.addItem(spell['name'])
            
        # Clear the current selection
        self.current_spell = None
        self.enable_details(False)
        
    def on_spell_selected(self, current, previous):
        """Handle selection of a spell in the list."""
        if not current:
            self.current_spell = None
            self.enable_details(False)
            return
            
        # Get the selected spell
        spell_name = current.text()
        self.current_spell = self.game_data.get_spell_by_name(spell_name)
        
        if self.current_spell:
            # Update the details
            self.name_edit.setText(self.current_spell['name'])
            
            # Set the type
            index = self.type_combo.findText(self.current_spell['type'])
            if index >= 0:
                self.type_combo.setCurrentIndex(index)
                
            # Set the power
            self.power_spin.setValue(self.current_spell['power'])
            
            # Set the MP cost
            self.mp_cost_spin.setValue(self.current_spell['mp_cost'])
            
            # Set the target
            index = self.target_combo.findText(self.current_spell['target'])
            if index >= 0:
                self.target_combo.setCurrentIndex(index)
            
            # Generate the spell preview
            self.generate_spell_preview()
            
            # Enable the details
            self.enable_details(True)
            
    def on_type_changed(self, spell_type):
        """Handle change of spell type to update the preview."""
        if self.current_spell:
            self.generate_spell_preview()
            
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
        
        # Get the spell colors
        start_color, end_color = self.spell_colors.get(
            spell_type, (QColor(200, 200, 200), QColor(255, 255, 255))
        )
        
        # Draw based on spell type
        if spell_type in ["Fire", "Ice", "Lightning", "Earth", "Poison"]:
            # Offensive spell - draw as a projectile
            self.draw_offensive_spell(painter, start_color, end_color)
        elif spell_type in ["Heal", "Cure"]:
            # Healing spell - draw as a glow
            self.draw_healing_spell(painter, start_color, end_color)
        else:  # Buff
            # Buff spell - draw as an aura
            self.draw_buff_spell(painter, start_color, end_color)
            
        # Draw the spell name
        painter.setPen(QPen(Qt.GlobalColor.white))
        font = QFont("Arial", 12, QFont.Weight.Bold)
        painter.setFont(font)
        painter.drawText(0, 0, 300, 30, 
                        Qt.AlignmentFlag.AlignCenter, self.current_spell['name'])
        
        # Draw the spell power
        power_text = f"Power: {self.power_spin.value()}"
        painter.drawText(0, 170, 300, 30, 
                        Qt.AlignmentFlag.AlignCenter, power_text)
        
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
            painter.drawEllipse(150 - size/2, 100 - size/2, size, size)
            
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
            painter.drawEllipse(150 - size/2, 100 - size/2, size, size)
            
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
            'target': "Single Enemy"
        }
        
        # Add to the game data
        self.game_data.spells.append(new_spell)
        
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