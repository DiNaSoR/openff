import os
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QListWidget, 
                           QGroupBox, QFormLayout, QLabel, QLineEdit, 
                           QSpinBox, QComboBox, QPushButton)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap, QPainter, QColor, QFont, QPen, QBrush

class ItemEditorTab(QWidget):
    """Tab for editing game items with visual elements."""
    
    def __init__(self, game_data):
        super().__init__()
        self.game_data = game_data
        self.current_item = None
        
        # Define item type colors
        self.type_colors = {
            "Weapon": QColor(139, 69, 19),    # Brown
            "Armor": QColor(192, 192, 192),   # Silver
            "Consumable": QColor(220, 20, 60), # Red
            "Key Item": QColor(255, 215, 0),  # Gold
            "Misc": QColor(128, 128, 128)     # Gray
        }
        
        # Define item type icons
        self.type_icons = {
            "Weapon": "⚔️",
            "Armor": "🛡️",
            "Consumable": "🧪",
            "Key Item": "🔑",
            "Misc": "📦"
        }
        
        self.init_ui()
        
    def init_ui(self):
        """Initialize the user interface."""
        # Main layout
        main_layout = QHBoxLayout(self)
        
        # Left side - Item list
        left_layout = QVBoxLayout()
        
        # Item list
        self.item_list = QListWidget()
        self.item_list.currentItemChanged.connect(self.on_item_selected)
        left_layout.addWidget(QLabel("Items:"))
        left_layout.addWidget(self.item_list)
        
        # Add/Remove buttons
        button_layout = QHBoxLayout()
        self.add_button = QPushButton("Add Item")
        self.add_button.clicked.connect(self.add_item)
        self.remove_button = QPushButton("Remove Item")
        self.remove_button.clicked.connect(self.remove_item)
        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.remove_button)
        left_layout.addLayout(button_layout)
        
        # Right side - Item details
        right_layout = QVBoxLayout()
        
        # Item image
        self.image_box = QGroupBox("Item Image")
        image_layout = QVBoxLayout()
        self.item_image = QLabel()
        self.item_image.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.item_image.setMinimumSize(128, 128)
        self.item_image.setMaximumSize(256, 256)
        self.item_image.setScaledContents(True)
        image_layout.addWidget(self.item_image)
        
        # Type selection
        type_layout = QHBoxLayout()
        type_layout.addWidget(QLabel("Type:"))
        self.type_combo = QComboBox()
        self.type_combo.addItems([
            "Weapon", "Armor", "Consumable", "Key Item", "Misc"
        ])
        self.type_combo.currentIndexChanged.connect(self.on_type_changed)
        type_layout.addWidget(self.type_combo)
        image_layout.addLayout(type_layout)
        
        self.image_box.setLayout(image_layout)
        right_layout.addWidget(self.image_box)
        
        # Item details
        self.details_box = QGroupBox("Item Details")
        details_layout = QFormLayout()
        
        # Name field
        self.name_edit = QLineEdit()
        details_layout.addRow("Name:", self.name_edit)
        
        # Power field
        self.power_spin = QSpinBox()
        self.power_spin.setRange(0, 999)
        details_layout.addRow("Power:", self.power_spin)
        
        # Save button
        self.save_button = QPushButton("Save Changes")
        self.save_button.clicked.connect(self.save_item)
        details_layout.addRow("", self.save_button)
        
        self.details_box.setLayout(details_layout)
        right_layout.addWidget(self.details_box)
        
        # Add layouts to main layout
        main_layout.addLayout(left_layout, 1)
        main_layout.addLayout(right_layout, 2)
        
        # Disable details until an item is selected
        self.enable_details(False)
        
    def update_data(self):
        """Update the UI with the latest game data."""
        # Clear the list
        self.item_list.clear()
        
        # Add items to the list
        for item in self.game_data.items:
            self.item_list.addItem(item['name'])
            
        # Clear the current selection
        self.current_item = None
        self.enable_details(False)
        
    def on_item_selected(self, current, previous):
        """Handle selection of an item in the list."""
        if not current:
            self.current_item = None
            self.enable_details(False)
            return
            
        # Get the selected item
        item_name = current.text()
        self.current_item = self.game_data.get_item_by_name(item_name)
        
        if self.current_item:
            # Update the details
            self.name_edit.setText(self.current_item['name'])
            self.power_spin.setValue(self.current_item['power'])
            
            # Set the type
            type_index = self.type_combo.findText(self.current_item['type'])
            if type_index >= 0:
                self.type_combo.setCurrentIndex(type_index)
                
            # Generate and display the item image
            self.generate_item_image()
            
            # Enable the details
            self.enable_details(True)
            
    def on_type_changed(self, index):
        """Handle change of item type selection."""
        if not self.current_item:
            return
            
        # Update the item's type
        self.current_item['type'] = self.type_combo.currentText()
        
        # Regenerate the item image
        self.generate_item_image()
        
    def generate_item_image(self):
        """Generate an image for the item based on its type."""
        if not self.current_item:
            return
            
        # Get the item type
        item_type = self.current_item.get('type', 'Misc')
        
        # Get the color for this type
        color = self.type_colors.get(item_type, QColor(128, 128, 128))
        
        # Get the icon for this type
        icon = self.type_icons.get(item_type, "📦")
        
        # Create a pixmap
        pixmap = QPixmap(128, 128)
        pixmap.fill(Qt.GlobalColor.transparent)
        
        # Create a painter
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Draw a rounded rectangle with the type color
        painter.setPen(QPen(Qt.GlobalColor.black, 2))
        painter.setBrush(QBrush(color))
        painter.drawRoundedRect(10, 10, 108, 108, 10, 10)
        
        # Draw the item name
        painter.setPen(QPen(Qt.GlobalColor.white))
        font = QFont("Arial", 12, QFont.Weight.Bold)
        painter.setFont(font)
        painter.drawText(pixmap.rect(), Qt.AlignmentFlag.AlignCenter, self.current_item['name'])
        
        # Draw the icon
        font = QFont("Arial", 24)
        painter.setFont(font)
        painter.drawText(pixmap.rect().adjusted(0, -30, 0, 0), Qt.AlignmentFlag.AlignCenter, icon)
        
        # Draw the power
        painter.setPen(QPen(Qt.GlobalColor.white))
        font = QFont("Arial", 10)
        painter.setFont(font)
        painter.drawText(pixmap.rect().adjusted(0, 40, 0, 0), Qt.AlignmentFlag.AlignCenter, 
                        f"Power: {self.current_item['power']}")
        
        # End painting
        painter.end()
        
        # Set the pixmap
        self.item_image.setPixmap(pixmap)
        
    def enable_details(self, enabled):
        """Enable or disable the details widgets."""
        self.details_box.setEnabled(enabled)
        self.image_box.setEnabled(enabled)
        self.remove_button.setEnabled(enabled)
        
    def add_item(self):
        """Add a new item."""
        # Create a new item with default values
        new_item = {
            'name': "New Item",
            'type': "Misc",
            'power': 0
        }
        
        # Add to the game data
        self.game_data.items.append(new_item)
        
        # Update the UI
        self.update_data()
        
        # Select the new item
        for i in range(self.item_list.count()):
            if self.item_list.item(i).text() == new_item['name']:
                self.item_list.setCurrentRow(i)
                break
                
    def remove_item(self):
        """Remove the selected item."""
        if not self.current_item:
            return
            
        # Remove from the game data
        self.game_data.items.remove(self.current_item)
        
        # Update the UI
        self.update_data()
        
    def save_item(self):
        """Save changes to the selected item."""
        if not self.current_item:
            return
            
        # Update the item with the form values
        self.current_item['name'] = self.name_edit.text()
        self.current_item['power'] = self.power_spin.value()
        self.current_item['type'] = self.type_combo.currentText()
        
        # Update the UI
        self.update_data()
        
        # Reselect the item
        for i in range(self.item_list.count()):
            if self.item_list.item(i).text() == self.current_item['name']:
                self.item_list.setCurrentRow(i)
                break
                
    def save_changes(self):
        """Save all changes to the game data."""
        # This would be called from the main window
        return self.game_data.save_to_file() 