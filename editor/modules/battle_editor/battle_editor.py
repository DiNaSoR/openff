import os
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QListWidget, 
                           QGroupBox, QFormLayout, QLabel, QLineEdit, 
                           QPushButton, QListWidgetItem, QComboBox)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap, QPainter, QColor, QFont, QPen, QBrush

class BattleEditorTab(QWidget):
    """Tab for editing game battles with visual elements."""
    
    def __init__(self, game_data):
        super().__init__()
        self.game_data = game_data
        self.current_battle = None
        
        # Define enemy colors for visualization
        self.enemy_colors = {
            "Goblin": QColor(0, 128, 0),      # Green
            "Wolf": QColor(128, 128, 128),    # Gray
            "Guard": QColor(0, 0, 128),       # Blue
            "Captain": QColor(0, 0, 200),     # Bright Blue
            "Skeleton": QColor(255, 255, 255), # White
            "Zombie": QColor(0, 100, 0),      # Dark Green
            "Ghost": QColor(200, 200, 255),   # Light Blue
            "Garland": QColor(128, 0, 0)      # Dark Red
        }
        
        self.init_ui()
        
    def init_ui(self):
        """Initialize the user interface."""
        # Main layout
        main_layout = QHBoxLayout(self)
        
        # Left side - Battle list
        left_layout = QVBoxLayout()
        
        # Battle list
        self.battle_list = QListWidget()
        self.battle_list.currentItemChanged.connect(self.on_battle_selected)
        left_layout.addWidget(QLabel("Battles:"))
        left_layout.addWidget(self.battle_list)
        
        # Add/Remove buttons
        button_layout = QHBoxLayout()
        self.add_button = QPushButton("Add Battle")
        self.add_button.clicked.connect(self.add_battle)
        self.remove_button = QPushButton("Remove Battle")
        self.remove_button.clicked.connect(self.remove_battle)
        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.remove_button)
        left_layout.addLayout(button_layout)
        
        # Right side - Battle details
        right_layout = QVBoxLayout()
        
        # Battle details
        self.details_box = QGroupBox("Battle Details")
        details_layout = QFormLayout()
        
        # Name field
        self.name_edit = QLineEdit()
        details_layout.addRow("Name:", self.name_edit)
        
        # Save button
        self.save_button = QPushButton("Save Changes")
        self.save_button.clicked.connect(self.save_battle)
        details_layout.addRow("", self.save_button)
        
        self.details_box.setLayout(details_layout)
        right_layout.addWidget(self.details_box)
        
        # Battle preview
        self.preview_box = QGroupBox("Battle Preview")
        preview_layout = QVBoxLayout()
        
        # Battle scene preview
        self.battle_scene = QLabel()
        self.battle_scene.setMinimumSize(400, 200)
        self.battle_scene.setAlignment(Qt.AlignmentFlag.AlignCenter)
        preview_layout.addWidget(self.battle_scene)
        
        self.preview_box.setLayout(preview_layout)
        right_layout.addWidget(self.preview_box)
        
        # Enemy list
        self.enemies_box = QGroupBox("Enemies")
        enemies_layout = QVBoxLayout()
        
        # Enemy list
        self.enemy_list = QListWidget()
        enemies_layout.addWidget(self.enemy_list)
        
        # Add/Remove enemy buttons
        enemy_button_layout = QHBoxLayout()
        
        # Enemy selection
        self.enemy_combo = QComboBox()
        self.enemy_combo.addItems([
            "Goblin", "Wolf", "Guard", "Captain", 
            "Skeleton", "Zombie", "Ghost", "Garland"
        ])
        enemy_button_layout.addWidget(self.enemy_combo)
        
        # Add enemy button
        self.add_enemy_button = QPushButton("Add Enemy")
        self.add_enemy_button.clicked.connect(self.add_enemy)
        enemy_button_layout.addWidget(self.add_enemy_button)
        
        # Remove enemy button
        self.remove_enemy_button = QPushButton("Remove Enemy")
        self.remove_enemy_button.clicked.connect(self.remove_enemy)
        enemy_button_layout.addWidget(self.remove_enemy_button)
        
        enemies_layout.addLayout(enemy_button_layout)
        self.enemies_box.setLayout(enemies_layout)
        right_layout.addWidget(self.enemies_box)
        
        # Add layouts to main layout
        main_layout.addLayout(left_layout, 1)
        main_layout.addLayout(right_layout, 2)
        
        # Disable details until a battle is selected
        self.enable_details(False)
        
    def update_data(self):
        """Update the UI with the latest game data."""
        # Clear the list
        self.battle_list.clear()
        
        # Add battles to the list
        for battle in self.game_data.battles:
            self.battle_list.addItem(battle['name'])
            
        # Clear the current selection
        self.current_battle = None
        self.enable_details(False)
        
    def on_battle_selected(self, current, previous):
        """Handle selection of a battle in the list."""
        if not current:
            self.current_battle = None
            self.enable_details(False)
            return
            
        # Get the selected battle
        battle_name = current.text()
        self.current_battle = self.game_data.get_battle_by_name(battle_name)
        
        if self.current_battle:
            # Update the details
            self.name_edit.setText(self.current_battle['name'])
            
            # Update the enemy list
            self.update_enemy_list()
            
            # Generate the battle preview
            self.generate_battle_preview()
            
            # Enable the details
            self.enable_details(True)
            
    def update_enemy_list(self):
        """Update the enemy list with the current battle's enemies."""
        # Clear the list
        self.enemy_list.clear()
        
        # Add enemies to the list
        for enemy in self.current_battle['enemies']:
            self.enemy_list.addItem(enemy)
            
    def generate_battle_preview(self):
        """Generate a preview image of the battle scene."""
        if not self.current_battle:
            return
            
        # Create a pixmap for the battle scene
        pixmap = QPixmap(400, 200)
        pixmap.fill(QColor(50, 50, 100))  # Dark blue background
        
        # Create a painter
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Draw a ground line
        painter.setPen(QPen(QColor(100, 100, 100), 2))
        painter.drawLine(0, 150, 400, 150)
        
        # Draw enemies
        enemies = self.current_battle['enemies']
        num_enemies = len(enemies)
        
        if num_enemies > 0:
            # Calculate positions for enemies
            spacing = 400 / (num_enemies + 1)
            
            for i, enemy in enumerate(enemies):
                # Get the enemy color
                color = self.enemy_colors.get(enemy, QColor(200, 0, 0))
                
                # Calculate position
                x = spacing * (i + 1)
                y = 100
                
                # Draw the enemy (simple representation)
                painter.setPen(QPen(Qt.GlobalColor.black, 2))
                painter.setBrush(QBrush(color))
                painter.drawEllipse(x - 25, y - 25, 50, 50)
                
                # Draw the enemy name
                painter.setPen(QPen(Qt.GlobalColor.white))
                font = QFont("Arial", 8)
                painter.setFont(font)
                painter.drawText(x - 40, y + 40, 80, 20, 
                                Qt.AlignmentFlag.AlignCenter, enemy)
                
        # Draw player characters (simplified)
        for i in range(4):
            painter.setPen(QPen(Qt.GlobalColor.black, 2))
            painter.setBrush(QBrush(QColor(0, 0, 200)))
            painter.drawRect(50 + i * 80, 170, 30, 30)
            
        # End painting
        painter.end()
        
        # Set the pixmap
        self.battle_scene.setPixmap(pixmap)
        
    def enable_details(self, enabled):
        """Enable or disable the details widgets."""
        self.details_box.setEnabled(enabled)
        self.preview_box.setEnabled(enabled)
        self.enemies_box.setEnabled(enabled)
        self.remove_button.setEnabled(enabled)
        
    def add_battle(self):
        """Add a new battle."""
        # Create a new battle with default values
        new_battle = {
            'name': "New Battle",
            'enemies': ["Goblin"]
        }
        
        # Add to the game data
        self.game_data.battles.append(new_battle)
        
        # Update the UI
        self.update_data()
        
        # Select the new battle
        for i in range(self.battle_list.count()):
            if self.battle_list.item(i).text() == new_battle['name']:
                self.battle_list.setCurrentRow(i)
                break
                
    def remove_battle(self):
        """Remove the selected battle."""
        if not self.current_battle:
            return
            
        # Remove from the game data
        self.game_data.battles.remove(self.current_battle)
        
        # Update the UI
        self.update_data()
        
    def add_enemy(self):
        """Add an enemy to the current battle."""
        if not self.current_battle:
            return
            
        # Get the selected enemy
        enemy = self.enemy_combo.currentText()
        
        # Add to the battle
        self.current_battle['enemies'].append(enemy)
        
        # Update the UI
        self.update_enemy_list()
        self.generate_battle_preview()
        
    def remove_enemy(self):
        """Remove the selected enemy from the current battle."""
        if not self.current_battle:
            return
            
        # Get the selected enemy
        current_item = self.enemy_list.currentItem()
        if not current_item:
            return
            
        enemy = current_item.text()
        
        # Remove from the battle
        if enemy in self.current_battle['enemies']:
            self.current_battle['enemies'].remove(enemy)
            
        # Update the UI
        self.update_enemy_list()
        self.generate_battle_preview()
        
    def save_battle(self):
        """Save changes to the selected battle."""
        if not self.current_battle:
            return
            
        # Update the battle with the form values
        self.current_battle['name'] = self.name_edit.text()
        
        # Update the UI
        self.update_data()
        
        # Reselect the battle
        for i in range(self.battle_list.count()):
            if self.battle_list.item(i).text() == self.current_battle['name']:
                self.battle_list.setCurrentRow(i)
                break
                
    def save_changes(self):
        """Save all changes to the game data."""
        # This would be called from the main window
        return self.game_data.save_to_file() 