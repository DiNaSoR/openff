import os
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QListWidget, 
                           QGroupBox, QFormLayout, QLabel, QLineEdit, 
                           QSpinBox, QComboBox, QPushButton, QTextEdit,
                           QCheckBox, QMessageBox, QTabWidget)
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
            "Accessory": QColor(147, 112, 219), # Purple
            "Misc": QColor(128, 128, 128)     # Gray
        }
        
        # Define item type icons
        self.type_icons = {
            "Weapon": "⚔️",
            "Armor": "🛡️",
            "Consumable": "🧪",
            "Key Item": "🔑",
            "Accessory": "💍",
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
            "Weapon", "Armor", "Consumable", "Key Item", "Accessory", "Misc"
        ])
        self.type_combo.currentIndexChanged.connect(self.on_type_changed)
        type_layout.addWidget(self.type_combo)
        image_layout.addLayout(type_layout)
        
        self.image_box.setLayout(image_layout)
        right_layout.addWidget(self.image_box)
        
        # Item details using TabWidget for better organization
        self.details_tabs = QTabWidget()
        
        # Basic details tab
        basic_tab = QWidget()
        basic_layout = QFormLayout(basic_tab)
        
        # Name field
        self.name_edit = QLineEdit()
        basic_layout.addRow("Name:", self.name_edit)
        
        # Power field
        self.power_spin = QSpinBox()
        self.power_spin.setRange(0, 999)
        basic_layout.addRow("Power:", self.power_spin)
        
        # Price field
        self.price_spin = QSpinBox()
        self.price_spin.setRange(0, 99999)
        self.price_spin.setSingleStep(10)
        basic_layout.addRow("Price:", self.price_spin)
        
        # Quantity field (for inventory/shops)
        self.quantity_spin = QSpinBox()
        self.quantity_spin.setRange(0, 99)
        basic_layout.addRow("Quantity:", self.quantity_spin)
        
        # Effects tab
        effects_tab = QWidget()
        effects_layout = QFormLayout(effects_tab)
        
        # Effect target
        self.target_combo = QComboBox()
        self.target_combo.addItems([
            "Single", "All", "Self", "Enemy", "All Enemies"
        ])
        effects_layout.addRow("Target:", self.target_combo)
        
        # Effect type
        self.effect_combo = QComboBox()
        self.effect_combo.addItems([
            "None", "Restore HP", "Restore MP", "Damage", "Cure Status", "Cause Status"
        ])
        effects_layout.addRow("Effect:", self.effect_combo)
        
        # Effect strength
        self.effect_spin = QSpinBox()
        self.effect_spin.setRange(0, 999)
        effects_layout.addRow("Strength:", self.effect_spin)
        
        # Status effects
        self.poison_check = QCheckBox("Poison")
        self.paralyze_check = QCheckBox("Paralyze")
        effects_layout.addRow("Status:", self.poison_check)
        effects_layout.addRow("", self.paralyze_check)
        
        # Description 
        description_tab = QWidget()
        description_layout = QVBoxLayout(description_tab)
        
        # Description field
        self.description_edit = QTextEdit()
        self.description_edit.setPlaceholderText("Enter item description...")
        description_layout.addWidget(self.description_edit)

        # Equipment tab (for weapons/armor)
        equip_tab = QWidget()
        equip_layout = QFormLayout(equip_tab)
        
        # Job restrictions
        self.job_restrictions = []
        job_layout = QVBoxLayout()
        job_names = ["Fighter", "Thief", "Black Mage", "White Mage", "Red Mage", "Monk", "Knight"]
        
        for job in job_names:
            check = QCheckBox(job)
            check.setChecked(True)  # Default to usable by all jobs
            self.job_restrictions.append(check)
            job_layout.addWidget(check)
            
        equip_group = QGroupBox("Usable by Jobs:")
        equip_group.setLayout(job_layout)
        equip_layout.addRow(equip_group)
        
        # Stats bonuses (for equipment)
        stats_layout = QFormLayout()
        
        self.stat_bonuses = {
            "pw": QSpinBox(),  # Power
            "sp": QSpinBox(),  # Speed
            "it": QSpinBox(),  # Intelligence
            "st": QSpinBox(),  # Stamina
            "lk": QSpinBox()   # Luck
        }
        
        # Set range to allow negative values for stat penalties
        for stat_spin in self.stat_bonuses.values():
            stat_spin.setRange(-99, 99)
            
        stats_layout.addRow("Power:", self.stat_bonuses["pw"])
        stats_layout.addRow("Speed:", self.stat_bonuses["sp"])
        stats_layout.addRow("Intelligence:", self.stat_bonuses["it"])
        stats_layout.addRow("Stamina:", self.stat_bonuses["st"])
        stats_layout.addRow("Luck:", self.stat_bonuses["lk"])
        
        stats_group = QGroupBox("Stat Bonuses:")
        stats_group.setLayout(stats_layout)
        equip_layout.addRow(stats_group)
        
        # Add all tabs
        self.details_tabs.addTab(basic_tab, "Basic")
        self.details_tabs.addTab(effects_tab, "Effects")
        self.details_tabs.addTab(description_tab, "Description")
        self.details_tabs.addTab(equip_tab, "Equipment")
        
        right_layout.addWidget(self.details_tabs)
        
        # Save button
        self.save_button = QPushButton("Save Changes")
        self.save_button.clicked.connect(self.save_item)
        right_layout.addWidget(self.save_button)
        
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
            # Update the basic details
            self.name_edit.setText(self.current_item['name'])
            self.power_spin.setValue(self.current_item.get('power', 0))
            
            # Set the type
            type_index = self.type_combo.findText(self.current_item.get('type', 'Misc'))
            if type_index >= 0:
                self.type_combo.setCurrentIndex(type_index)
                
            # Set price and quantity if available
            self.price_spin.setValue(self.current_item.get('price', 0))
            self.quantity_spin.setValue(self.current_item.get('quantity', 1))
            
            # Set effect values if available
            effect_data = self.current_item.get('effect', {})
            
            # Set target
            target_value = effect_data.get('target', 'Single')
            target_index = self.target_combo.findText(target_value)
            if target_index >= 0:
                self.target_combo.setCurrentIndex(target_index)
                
            # Set effect type
            effect_type = effect_data.get('type', 'None')
            effect_index = self.effect_combo.findText(effect_type)
            if effect_index >= 0:
                self.effect_combo.setCurrentIndex(effect_index)
                
            # Set effect strength
            self.effect_spin.setValue(effect_data.get('strength', 0))
            
            # Set status effects
            status = effect_data.get('status', {})
            self.poison_check.setChecked(status.get('poison', False))
            self.paralyze_check.setChecked(status.get('paralyze', False))
            
            # Set description
            self.description_edit.setText(self.current_item.get('description', ''))
            
            # Set job restrictions
            job_restrictions = self.current_item.get('job_restrictions', [])
            
            # If job_restrictions is empty, assume all jobs can use it
            if not job_restrictions:
                for check in self.job_restrictions:
                    check.setChecked(True)
            else:
                for i, check in enumerate(self.job_restrictions):
                    check.setChecked(i in job_restrictions)
                    
            # Set stat bonuses
            stat_bonuses = self.current_item.get('stat_bonuses', {})
            for stat, spin in self.stat_bonuses.items():
                spin.setValue(stat_bonuses.get(stat, 0))
                
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
        
        # Enable/disable appropriate tabs based on item type
        item_type = self.type_combo.currentText()
        
        # Hide/show effects tab based on type
        effects_index = self.details_tabs.indexOf(self.details_tabs.findChild(QWidget, "", Qt.FindChildOption.FindDirectChildrenOnly))
        equip_index = 3  # Equipment tab index
        
        if item_type in ["Consumable", "Key Item"]:
            # Enable effects tab for consumables
            if effects_index >= 0:
                self.details_tabs.setTabEnabled(effects_index, True)
            # Disable equipment tab for consumables
            self.details_tabs.setTabEnabled(equip_index, False)
        elif item_type in ["Weapon", "Armor", "Accessory"]:
            # Disable effects tab for equipment
            if effects_index >= 0:
                self.details_tabs.setTabEnabled(effects_index, False)
            # Enable equipment tab for equipment
            self.details_tabs.setTabEnabled(equip_index, True)
        else:
            # Default behavior for other types
            if effects_index >= 0:
                self.details_tabs.setTabEnabled(effects_index, True)
            self.details_tabs.setTabEnabled(equip_index, True)
        
    def generate_item_image(self):
        """Generate an image for the item based on its type and properties."""
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
        
        # Draw different details based on item type
        painter.setPen(QPen(Qt.GlobalColor.white))
        font = QFont("Arial", 10)
        painter.setFont(font)
        
        # For weapons and armor, show power/defense
        if item_type in ["Weapon", "Armor"]:
            painter.drawText(pixmap.rect().adjusted(0, 40, 0, 0), Qt.AlignmentFlag.AlignCenter, 
                          f"{item_type}: {self.current_item.get('power', 0)}")
            # Price if available
            if 'price' in self.current_item and self.current_item['price'] > 0:
                painter.drawText(pixmap.rect().adjusted(0, 60, 0, 0), Qt.AlignmentFlag.AlignCenter, 
                              f"Price: {self.current_item['price']}G")
        # For consumables, show effect
        elif item_type == "Consumable":
            effect = self.current_item.get('effect', {})
            effect_type = effect.get('type', 'None')
            strength = effect.get('strength', 0)
            if effect_type != 'None':
                painter.drawText(pixmap.rect().adjusted(0, 40, 0, 0), Qt.AlignmentFlag.AlignCenter, 
                              f"{effect_type}: {strength}")
            # Price if available
            if 'price' in self.current_item and self.current_item['price'] > 0:
                painter.drawText(pixmap.rect().adjusted(0, 60, 0, 0), Qt.AlignmentFlag.AlignCenter, 
                              f"Price: {self.current_item['price']}G")
        # For other types, just show basic info
        else:
            painter.drawText(pixmap.rect().adjusted(0, 40, 0, 0), Qt.AlignmentFlag.AlignCenter, 
                          f"{item_type}")
        
        # End painting
        painter.end()
        
        # Set the pixmap
        self.item_image.setPixmap(pixmap)
        
    def enable_details(self, enabled):
        """Enable or disable the details widgets."""
        self.details_tabs.setEnabled(enabled)
        self.image_box.setEnabled(enabled)
        self.remove_button.setEnabled(enabled)
        
    def add_item(self):
        """Add a new item."""
        # Create a new item with default values
        new_item = {
            'name': "New Item",
            'type': "Misc",
            'power': 0,
            'price': 0,
            'quantity': 1,
            'description': "A new item.",
            'effect': {
                'target': 'Single',
                'type': 'None',
                'strength': 0,
                'status': {
                    'poison': False,
                    'paralyze': False
                }
            },
            'job_restrictions': [],  # Empty means all jobs can use it
            'stat_bonuses': {
                'pw': 0,
                'sp': 0,
                'it': 0,
                'st': 0,
                'lk': 0
            }
        }
        
        # Add to the game data
        self.game_data.items.append(new_item)
        
        # Mark data as changed
        self.game_data.mark_as_changed()
        
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
            
        # Confirm with the user
        reply = QMessageBox.question(
            self, 
            "Confirm Deletion", 
            f"Are you sure you want to delete '{self.current_item['name']}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            # Remove from the game data
            self.game_data.items.remove(self.current_item)
            
            # Mark data as changed
            self.game_data.mark_as_changed()
            
            # Update the UI
            self.update_data()
        
    def save_item(self):
        """Save changes to the selected item."""
        if not self.current_item:
            return
            
        # Check for valid name
        if not self.name_edit.text().strip():
            QMessageBox.warning(self, "Invalid Input", "Item name cannot be empty!")
            return
            
        # Update the item with the form values
        self.current_item['name'] = self.name_edit.text()
        self.current_item['power'] = self.power_spin.value()
        self.current_item['type'] = self.type_combo.currentText()
        
        # Update additional fields
        self.current_item['price'] = self.price_spin.value()
        self.current_item['quantity'] = self.quantity_spin.value()
        self.current_item['description'] = self.description_edit.toPlainText()
        
        # Update effect data
        if 'effect' not in self.current_item:
            self.current_item['effect'] = {}
            
        self.current_item['effect']['target'] = self.target_combo.currentText()
        self.current_item['effect']['type'] = self.effect_combo.currentText()
        self.current_item['effect']['strength'] = self.effect_spin.value()
        
        # Update status effects
        if 'status' not in self.current_item['effect']:
            self.current_item['effect']['status'] = {}
            
        self.current_item['effect']['status']['poison'] = self.poison_check.isChecked()
        self.current_item['effect']['status']['paralyze'] = self.paralyze_check.isChecked()
        
        # Update job restrictions
        job_restrictions = []
        for i, check in enumerate(self.job_restrictions):
            if not check.isChecked():
                job_restrictions.append(i)
        self.current_item['job_restrictions'] = job_restrictions
        
        # Update stat bonuses
        if 'stat_bonuses' not in self.current_item:
            self.current_item['stat_bonuses'] = {}
            
        for stat, spin in self.stat_bonuses.items():
            self.current_item['stat_bonuses'][stat] = spin.value()
        
        # Mark the game data as changed
        self.game_data.mark_as_changed()
        
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