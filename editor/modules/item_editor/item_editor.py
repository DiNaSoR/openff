import os
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QListWidget, 
                           QGroupBox, QFormLayout, QLabel, QLineEdit, 
                           QSpinBox, QComboBox, QPushButton, QTextEdit,
                           QCheckBox, QMessageBox, QTabWidget, QTreeWidget,
                           QTreeWidgetItem, QSplitter)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap, QPainter, QColor, QFont, QPen, QBrush, QIcon, QLinearGradient, QRadialGradient

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
            "Misc": QColor(128, 128, 128),    # Gray
            "Helmet": QColor(169, 169, 169),  # Dark Silver
            "Shield": QColor(230, 232, 250),  # Light Steel Blue
            "Relic": QColor(75, 0, 130)       # Indigo
        }
        
        # Define item type icons
        self.type_icons = {
            "Weapon": "⚔️",
            "Armor": "🛡️",
            "Consumable": "🧪",
            "Key Item": "🔑",
            "Accessory": "💍",
            "Misc": "📦",
            "Helmet": "👑",
            "Shield": "🛡️",
            "Relic": "🔮"
        }
        
        # Define item secondary type/category
        self.sub_categories = {
            "Weapon": ["Sword", "Dagger", "Axe", "Spear", "Bow", "Staff", "Wand", "Fist", "Gun"],
            "Armor": ["Light", "Medium", "Heavy", "Robe"],
            "Helmet": ["Hat", "Cap", "Helm", "Crown"],
            "Shield": ["Buckler", "Shield", "Large Shield"],
            "Accessory": ["Ring", "Amulet", "Earring", "Bracelet", "Belt"],
            "Consumable": ["Potion", "Ether", "Elixir", "Antidote", "Phoenix Down", "Tent", "Scroll"],
            "Key Item": ["Quest", "Access", "Story", "Collectible"],
            "Relic": ["Ancient", "Cursed", "Blessed", "Legendary"],
            "Misc": ["Crafting", "Material", "Valuable", "Junk"]
        }
        
        self.init_ui()
        
    def init_ui(self):
        """Initialize the user interface."""
        # Main layout
        main_layout = QHBoxLayout(self)
        
        # Left side - Item list
        left_layout = QVBoxLayout()
        
        # Category filter
        category_layout = QHBoxLayout()
        category_layout.addWidget(QLabel("Filter by Type:"))
        self.category_filter = QComboBox()
        self.category_filter.addItem("All Types")
        for item_type in sorted(self.type_colors.keys()):
            self.category_filter.addItem(self.type_icons.get(item_type, "") + " " + item_type)
        self.category_filter.currentIndexChanged.connect(self.on_category_filter_changed)
        category_layout.addWidget(self.category_filter)
        left_layout.addLayout(category_layout)
        
        # Item tree with categories
        self.item_tree = QTreeWidget()
        self.item_tree.setHeaderLabels(["Items by Category"])
        self.item_tree.setColumnCount(1)
        self.item_tree.setAlternatingRowColors(True)
        self.item_tree.itemSelectionChanged.connect(self.on_tree_item_selected)
        left_layout.addWidget(self.item_tree)
        
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
            "Weapon", "Armor", "Consumable", "Key Item", "Accessory", 
            "Helmet", "Shield", "Relic", "Misc"
        ])
        self.type_combo.currentIndexChanged.connect(self.on_type_changed)
        type_layout.addWidget(self.type_combo)
        image_layout.addLayout(type_layout)
        
        # Subtype/category selection
        subtype_layout = QHBoxLayout()
        subtype_layout.addWidget(QLabel("Category:"))
        self.subtype_combo = QComboBox()
        subtype_layout.addWidget(self.subtype_combo)
        image_layout.addLayout(subtype_layout)
        
        # Update subtypes based on initial type
        self.update_subtype_combo("Weapon")
        self.type_combo.currentTextChanged.connect(self.update_subtype_combo)
        
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
        
        # Rarity field
        self.rarity_combo = QComboBox()
        self.rarity_combo.addItems(["Common", "Uncommon", "Rare", "Epic", "Legendary", "Unique"])
        basic_layout.addRow("Rarity:", self.rarity_combo)
        
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
            "None", "Restore HP", "Restore MP", "Damage", "Cure Status", "Cause Status",
            "Buff Stats", "Debuff Enemy", "Revive", "Escape"
        ])
        effects_layout.addRow("Effect:", self.effect_combo)
        
        # Effect strength
        self.effect_spin = QSpinBox()
        self.effect_spin.setRange(0, 999)
        effects_layout.addRow("Strength:", self.effect_spin)
        
        # Status effects
        status_group = QGroupBox("Status Effects:")
        status_layout = QVBoxLayout()
        
        self.status_checks = {
            "poison": QCheckBox("Poison"),
            "paralyze": QCheckBox("Paralyze"),
            "sleep": QCheckBox("Sleep"),
            "blind": QCheckBox("Blind"),
            "silence": QCheckBox("Silence"),
            "stone": QCheckBox("Stone/Petrify"),
            "curse": QCheckBox("Curse"),
            "confusion": QCheckBox("Confusion"),
            "slow": QCheckBox("Slow")
        }
        
        for check in self.status_checks.values():
            status_layout.addWidget(check)
            
        status_group.setLayout(status_layout)
        effects_layout.addRow(status_group)
        
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
            "lk": QSpinBox(),  # Luck
            "ma": QSpinBox()   # Magic
        }
        
        # Set range to allow negative values for stat penalties
        for stat_spin in self.stat_bonuses.values():
            stat_spin.setRange(-99, 99)
            
        stats_layout.addRow("Power:", self.stat_bonuses["pw"])
        stats_layout.addRow("Speed:", self.stat_bonuses["sp"])
        stats_layout.addRow("Intelligence:", self.stat_bonuses["it"])
        stats_layout.addRow("Stamina:", self.stat_bonuses["st"])
        stats_layout.addRow("Luck:", self.stat_bonuses["lk"])
        stats_layout.addRow("Magic:", self.stat_bonuses["ma"])
        
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
        
    def update_subtype_combo(self, item_type):
        """Update the subtype combo box based on the selected item type."""
        self.subtype_combo.clear()
        if item_type in self.sub_categories:
            self.subtype_combo.addItems(self.sub_categories[item_type])
        
    def update_data(self):
        """Update the UI with the latest game data."""
        # Clear the tree
        self.item_tree.clear()
        
        # Create root category items
        category_nodes = {}
        
        # Make sure we have All Types and all item types as categories
        for item_type in sorted(self.type_colors.keys()):
            icon_text = self.type_icons.get(item_type, "")
            category_node = QTreeWidgetItem([f"{icon_text} {item_type}"])
            category_node.setData(0, Qt.ItemDataRole.UserRole, {"type": "category", "value": item_type})
            category_nodes[item_type] = category_node
            self.item_tree.addTopLevelItem(category_node)
        
        # Add subcategories under each type
        subcategory_nodes = {}
        for item_type, subcategories in self.sub_categories.items():
            if item_type in category_nodes:
                for subcategory in subcategories:
                    subcat_node = QTreeWidgetItem([subcategory])
                    subcat_node.setData(0, Qt.ItemDataRole.UserRole, 
                                       {"type": "subcategory", "value": subcategory, "parent": item_type})
                    category_nodes[item_type].addChild(subcat_node)
                    subcategory_nodes[(item_type, subcategory)] = subcat_node
        
        # Add items to appropriate categories and subcategories
        for item in self.game_data.items:
            item_type = item.get('type', 'Misc')
            item_name = item.get('name', 'Unknown Item')
            item_category = item.get('category', '')
            
            # Create item node
            item_node = QTreeWidgetItem([item_name])
            item_node.setData(0, Qt.ItemDataRole.UserRole, {"type": "item", "value": item_name})
            
            # Add to specific subcategory if available
            if item_category and (item_type, item_category) in subcategory_nodes:
                subcategory_nodes[(item_type, item_category)].addChild(item_node)
            # Otherwise add to main category
            elif item_type in category_nodes:
                category_nodes[item_type].addChild(item_node)
            # Fallback to Misc if type not found
            elif 'Misc' in category_nodes:
                category_nodes['Misc'].addChild(item_node)
        
        # Expand all categories
        self.item_tree.expandAll()
        
        # Clear the current selection
        self.current_item = None
        self.enable_details(False)
        
    def on_category_filter_changed(self, index):
        """Handle when user changes category filter dropdown."""
        filter_text = self.category_filter.currentText().strip()
        
        # If "All Types" is selected, show everything
        if index == 0 or "All Types" in filter_text:
            for i in range(self.item_tree.topLevelItemCount()):
                self.item_tree.topLevelItem(i).setHidden(False)
            return
        
        # Extract just the category name without icon
        category = filter_text.split(" ", 1)[-1] if " " in filter_text else filter_text
        
        # Hide all categories except the selected one
        for i in range(self.item_tree.topLevelItemCount()):
            item = self.item_tree.topLevelItem(i)
            item_text = item.text(0).split(" ", 1)[-1] if " " in item.text(0) else item.text(0)
            item.setHidden(item_text != category)

    def on_tree_item_selected(self):
        """Handle when user selects an item in the tree."""
        selected_items = self.item_tree.selectedItems()
        if not selected_items:
            self.current_item = None
            self.enable_details(False)
            return
        
        # Get the selected item data
        item_data = selected_items[0].data(0, Qt.ItemDataRole.UserRole)
        
        # If it's a category or subcategory header, don't select anything
        if not item_data or item_data.get('type') != 'item':
            self.current_item = None
            self.enable_details(False)
            return
        
        # Get the selected item name
        item_name = item_data.get('value', '')
        self.current_item = self.game_data.get_item_by_name(item_name)
        
        if self.current_item:
            # Update UI with item details
            self.name_edit.setText(self.current_item['name'])
            self.power_spin.setValue(self.current_item.get('power', 0))
            
            # Set the type
            type_index = self.type_combo.findText(self.current_item.get('type', 'Misc'))
            if type_index >= 0:
                self.type_combo.setCurrentIndex(type_index)
                
            # Set the subtype if available
            category = self.current_item.get('category', '')
            if category:
                sub_index = self.subtype_combo.findText(category)
                if sub_index >= 0:
                    self.subtype_combo.setCurrentIndex(sub_index)
            
            # Set price and quantity if available
            self.price_spin.setValue(self.current_item.get('price', 0))
            self.quantity_spin.setValue(self.current_item.get('quantity', 1))
            
            # Set rarity if available
            rarity = self.current_item.get('rarity', 'Common')
            rarity_index = self.rarity_combo.findText(rarity)
            if rarity_index >= 0:
                self.rarity_combo.setCurrentIndex(rarity_index)
            
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
            for status_name, checkbox in self.status_checks.items():
                checkbox.setChecked(status.get(status_name, False))
            
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
                    check.setChecked(i not in job_restrictions)
                    
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
        item_type = self.type_combo.currentText()
        self.current_item['type'] = item_type
        
        # Update the subtype combo
        self.update_subtype_combo(item_type)
        
        # Regenerate the item image
        self.generate_item_image()
        
        # Enable/disable appropriate tabs based on item type
        item_type = self.type_combo.currentText()
        
        # Determine effects tab index and equip tab index
        effects_index = 1  # Effects tab index (0-based)
        equip_index = 3    # Equipment tab index (0-based)
        
        if item_type in ["Consumable", "Key Item"]:
            # Enable effects tab for consumables
            self.details_tabs.setTabEnabled(effects_index, True)
            # Disable equipment tab for consumables
            self.details_tabs.setTabEnabled(equip_index, False)
        elif item_type in ["Weapon", "Armor", "Helmet", "Shield", "Accessory", "Relic"]:
            # Disable effects tab for equipment
            self.details_tabs.setTabEnabled(effects_index, False)
            # Enable equipment tab for equipment
            self.details_tabs.setTabEnabled(equip_index, True)
        else:
            # Default behavior for other types
            self.details_tabs.setTabEnabled(effects_index, True)
            self.details_tabs.setTabEnabled(equip_index, True)
        
    def generate_item_image(self):
        """Generate an image for the item based on its type and properties."""
        if not self.current_item:
            return
            
        # Get the item type and other properties
        item_type = self.current_item.get('type', 'Misc')
        item_name = self.current_item.get('name', 'Unknown Item')
        item_power = self.current_item.get('power', 0)
        item_price = self.current_item.get('price', 0)
        item_rarity = self.current_item.get('rarity', 'Common')
        
        # Get the color for this type
        base_color = self.type_colors.get(item_type, QColor(128, 128, 128))
        
        # Adjust color based on rarity
        rarity_brightness = {
            'Common': 1.0,
            'Uncommon': 1.1,
            'Rare': 1.2,
            'Epic': 1.3,
            'Legendary': 1.5,
            'Unique': 1.7
        }
        
        brightness = rarity_brightness.get(item_rarity, 1.0)
        color = QColor(
            min(255, int(base_color.red() * brightness)),
            min(255, int(base_color.green() * brightness)),
            min(255, int(base_color.blue() * brightness))
        )
        
        # Get the icon for this type
        icon = self.type_icons.get(item_type, "📦")
        
        # Create a pixmap
        pixmap = QPixmap(128, 128)
        pixmap.fill(Qt.GlobalColor.transparent)
        
        # Create a painter
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Create gradient background based on item type and rarity
        if item_rarity in ['Legendary', 'Unique']:
            # Create a radial gradient for special items
            gradient = QRadialGradient(64, 64, 80)
            gradient.setColorAt(0, QColor(255, 255, 230))  # Light center
            gradient.setColorAt(0.8, color)                # Type color
            gradient.setColorAt(1, QColor(40, 40, 40))     # Dark edge
            painter.setBrush(QBrush(gradient))
        else:
            # Create a linear gradient for normal items
            gradient = QLinearGradient(0, 0, 0, 128)
            gradient.setColorAt(0, color.lighter(120))
            gradient.setColorAt(1, color.darker(120))
            painter.setBrush(QBrush(gradient))
        
        # Draw a rounded rectangle with the type color
        painter.setPen(QPen(Qt.GlobalColor.black, 2))
        painter.drawRoundedRect(4, 4, 120, 120, 15, 15)
        
        # Draw a decorative border based on rarity
        if item_rarity in ['Epic', 'Legendary', 'Unique']:
            painter.setPen(QPen(QColor(212, 175, 55), 3))  # Gold for high rarity
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawRoundedRect(8, 8, 112, 112, 12, 12)
        elif item_rarity in ['Rare']:
            painter.setPen(QPen(QColor(70, 130, 180), 2))  # Steel blue for rare
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawRoundedRect(8, 8, 112, 112, 12, 12)
        
        # Draw the item name with shadow effect
        painter.setPen(QPen(Qt.GlobalColor.black))
        font = QFont("Arial", 11, QFont.Weight.Bold)
        painter.setFont(font)
        
        # Draw shadow
        painter.drawText(pixmap.rect().adjusted(2, 2, 0, 0), Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter, item_name)
        
        # Draw text
        painter.setPen(QPen(Qt.GlobalColor.white))
        painter.drawText(pixmap.rect().adjusted(0, 0, 0, 0), Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter, item_name)
        
        # Draw the icon
        font = QFont("Arial", 32)
        painter.setFont(font)
        painter.drawText(pixmap.rect().adjusted(0, -15, 0, 0), Qt.AlignmentFlag.AlignCenter, icon)
        
        # Draw different details based on item type
        painter.setPen(QPen(Qt.GlobalColor.white))
        font = QFont("Arial", 9)
        painter.setFont(font)
        
        # For weapons and armor, show power/defense
        if item_type in ["Weapon", "Armor", "Helmet", "Shield"]:
            label = "ATK:" if item_type == "Weapon" else "DEF:"
            painter.drawText(pixmap.rect().adjusted(0, 40, 0, 0), Qt.AlignmentFlag.AlignCenter, 
                          f"{label} {item_power}")
            # Price if available
            if item_price > 0:
                painter.drawText(pixmap.rect().adjusted(0, 60, 0, 0), Qt.AlignmentFlag.AlignCenter, 
                              f"{item_price}G")
        # For consumables, show effect
        elif item_type == "Consumable":
            effect = self.current_item.get('effect', {})
            effect_type = effect.get('type', 'None')
            strength = effect.get('strength', 0)
            if effect_type != 'None':
                painter.drawText(pixmap.rect().adjusted(0, 40, 0, 0), Qt.AlignmentFlag.AlignCenter, 
                              f"{effect_type}")
                painter.drawText(pixmap.rect().adjusted(0, 55, 0, 0), Qt.AlignmentFlag.AlignCenter, 
                              f"Power: {strength}")
            # Price if available
            if item_price > 0:
                painter.drawText(pixmap.rect().adjusted(0, 75, 0, 0), Qt.AlignmentFlag.AlignCenter, 
                              f"Price: {item_price}G")
        # For other types, just show basic info
        else:
            painter.drawText(pixmap.rect().adjusted(0, 40, 0, 0), Qt.AlignmentFlag.AlignCenter, 
                          f"{item_type}")
            
        # Draw rarity at bottom
        font = QFont("Arial", 8, QFont.Weight.Bold)
        painter.setFont(font)
        
        # Set color based on rarity
        rarity_colors = {
            'Common': QColor(200, 200, 200),
            'Uncommon': QColor(100, 255, 100),
            'Rare': QColor(50, 150, 255),
            'Epic': QColor(200, 100, 255),
            'Legendary': QColor(255, 215, 0),
            'Unique': QColor(255, 50, 50)
        }
        painter.setPen(QPen(rarity_colors.get(item_rarity, QColor(255, 255, 255))))
        
        painter.drawText(pixmap.rect().adjusted(0, 85, 0, -5), Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignHCenter, 
                      f"{item_rarity}")
        
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
        # Get the currently selected category from the filter
        selected_category = "Misc"  # Default
        
        filter_text = self.category_filter.currentText()
        if filter_text != "All Types":
            selected_category = filter_text.split(" ", 1)[-1] if " " in filter_text else filter_text
        
        # Create a new item with default values
        new_item = {
            'name': "New Item",
            'type': selected_category,
            'category': self.sub_categories.get(selected_category, [""])[0],
            'power': 0,
            'price': 0,
            'quantity': 1,
            'rarity': "Common",
            'description': "A new item.",
            'effect': {
                'target': 'Single',
                'type': 'None',
                'strength': 0,
                'status': {
                    'poison': False,
                    'paralyze': False,
                    'sleep': False,
                    'blind': False,
                    'silence': False,
                    'stone': False,
                    'curse': False,
                    'confusion': False,
                    'slow': False
                }
            },
            'job_restrictions': [],  # Empty means all jobs can use it
            'stat_bonuses': {
                'pw': 0,
                'sp': 0,
                'it': 0,
                'st': 0,
                'lk': 0,
                'ma': 0
            }
        }
        
        # Add to the game data
        self.game_data.items.append(new_item)
        
        # Mark data as changed
        self.game_data.mark_as_changed()
        
        # Update the UI
        self.update_data()
        
        # Select the new item
        self.select_item_by_name(new_item['name'])
        
    def remove_item(self):
        """Remove the currently selected item."""
        # Check if an item is selected
        if not self.current_item:
            return
        
        # Get the name of the selected item
        item_name = self.current_item.get('name', '')
        
        # Confirm deletion
        reply = QMessageBox.question(self, "Confirm Delete",
                                 f"Are you sure you want to delete '{item_name}'?",
                                 QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                 QMessageBox.StandardButton.No)
                                 
        if reply == QMessageBox.StandardButton.Yes:
            # Remove from the game data
            self.game_data.items = [item for item in self.game_data.items if item.get('name') != item_name]
            
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
            
        # Store the original name for finding the item later
        original_name = self.current_item['name']
        original_type = self.current_item.get('type', 'Misc')
        original_category = self.current_item.get('category', '')
            
        # Update the item with the form values
        self.current_item['name'] = self.name_edit.text()
        self.current_item['power'] = self.power_spin.value()
        self.current_item['type'] = self.type_combo.currentText()
        
        # Update additional fields
        self.current_item['category'] = self.subtype_combo.currentText()
        self.current_item['price'] = self.price_spin.value()
        self.current_item['quantity'] = self.quantity_spin.value()
        self.current_item['rarity'] = self.rarity_combo.currentText()
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
            
        for status_name, checkbox in self.status_checks.items():
            self.current_item['effect']['status'][status_name] = checkbox.isChecked()
        
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
        
        # Check if the type or category changed
        type_changed = original_type != self.current_item['type']
        category_changed = original_category != self.current_item['category']
        name_changed = original_name != self.current_item['name']
        
        # If any categorization data changed, we need to rebuild the tree
        if type_changed or category_changed or name_changed:
            # Update the UI
            self.update_data()
            
            # Reselect the item by its new name
            self.select_item_by_name(self.current_item['name'])
        else:
            # Otherwise, just update the current item node's text
            selected_items = self.item_tree.selectedItems()
            if selected_items:
                selected_items[0].setText(0, self.current_item['name'])
        
    def select_item_by_name(self, item_name):
        """Find and select an item in the tree by its name."""
        # Expand all items to ensure we can find the item
        self.item_tree.expandAll()
        
        # Find the item in the tree
        for i in range(self.item_tree.topLevelItemCount()):
            category = self.item_tree.topLevelItem(i)
            
            # Check each child of the category
            for j in range(category.childCount()):
                child = category.child(j)
                
                # If this is a subcategory, check its children
                child_data = child.data(0, Qt.ItemDataRole.UserRole)
                if child_data and child_data.get('type') == 'subcategory':
                    for k in range(child.childCount()):
                        item = child.child(k)
                        item_data = item.data(0, Qt.ItemDataRole.UserRole)
                        if item_data and item_data.get('type') == 'item' and item_data.get('value') == item_name:
                            self.item_tree.setCurrentItem(item)
                            return
                # If this is an item directly under category
                elif child_data and child_data.get('type') == 'item' and child_data.get('value') == item_name:
                    self.item_tree.setCurrentItem(child)
                    return
        
    def save_changes(self):
        """Save all changes to the game data."""
        # This would be called from the main window
        return self.game_data.save_to_file() 