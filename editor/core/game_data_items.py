"""
Item data handling module.
"""

import re
from core.game_data import GameData
from core.default_game_data import DEFAULT_ITEMS

class GameDataItems(GameData):
    """Handler for item data in the game."""
    
    def __init__(self):
        """Initialize item data handler."""
        super().__init__()
        self.items = []
        self.using_default_items = False
        
    def extract_items(self):
        """Extract item data from the JavaScript content."""
        print("Extracting items...")
        
        all_items = []
        
        # Extract regular items
        item_array = self._extract_item_array()
        if item_array:
            all_items.extend(item_array)
            
        # Extract weapons
        weapon_array = self._extract_equipment_array('weapon', 'wep')
        if weapon_array:
            all_items.extend(weapon_array)
            
        # Extract armor (which includes body armor, helmets, shields, and accessories)
        armor_array = self._extract_equipment_array('armor', 'arm')
        if armor_array:
            all_items.extend(armor_array)
            
        # Extract magic spells/abilities
        magic_array = self._extract_magic_array()
        if magic_array:
            all_items.extend(magic_array)
            
        # If we found items, save them
        if all_items:
            # Remove duplicates based on name
            unique_items = []
            item_names = set()
            for item in all_items:
                if item['name'] not in item_names:
                    unique_items.append(item)
                    item_names.add(item['name'])
            
            self.items = unique_items
            self.using_default_items = False
            print(f"Successfully extracted {len(self.items)} unique items")
            return
            
        # If we couldn't extract items, use defaults
        print("Using default item data")
        self.items = DEFAULT_ITEMS.copy()
        self.using_default_items = True
    
    def _extract_item_array(self):
        """Extract the regular item array from the JavaScript content."""
        # Main item array pattern in app.js (more precise based on actual structure)
        main_pattern = r'item\s*:\s*\[\s*\{(.*?)\}\s*\],'
        
        # Backup patterns if the main pattern doesn't work
        backup_patterns = [
            # Classic item array initialization
            r'this\.gl\.itemSt\s*=\s*\[(.*?)\];',
            # Item push calls
            r'this\.gl\.itemSt\.push\((.*?)\);',
            # Alternative name
            r'this\.gl\.items?\s*=\s*\[(.*?)\];',
            r'this\.gl\.items?\.push\((.*?)\);',
            # Common structure in RPG games
            r'var\s+items?\s*=\s*\[(.*?)\];',
            r'let\s+items?\s*=\s*\[(.*?)\];',
            r'const\s+items?\s*=\s*\[(.*?)\];',
            # Patterns from character initialization
            r'for\s*\(\s*var\s+[a-zA-Z]+\s*=\s*\[(.*?)\],\s*[a-zA-Z]+\s*=\s*0;\s*[a-zA-Z]+\s*<\s*\d+;\s*[a-zA-Z]+\+\+\)\s*this\.gl\.items?\.push\(.*?\);',
            # Object literals with item properties
            r'items?:\s*\[(.*?)\]',
        ]
        
        extracted_items = []
        
        # First try with the main pattern that matches the observed structure
        try:
            matches = re.findall(main_pattern, self.js_content, re.DOTALL)
            if matches:
                # The main pattern captures the content of the item array without the brackets
                # We need to split this into individual item objects
                item_contents = matches[0]
                
                # Split at closing brace + comma + opening brace pattern, which separates items
                item_strings = re.split(r'\},\s*\{', item_contents)
                
                for i, item_str in enumerate(item_strings):
                    # Add back the curly braces that were removed in the split
                    if i > 0:
                        item_str = '{' + item_str
                    if i < len(item_strings) - 1:
                        item_str = item_str + '}'
                    
                    # Parse the item
                    item = self._parse_item_from_js(item_str)
                    if item:
                        extracted_items.append(item)
                        print(f"Found item: {item['name']}")
        except Exception as e:
            print(f"Error in main pattern matching: {str(e)}")
        
        # If the main pattern didn't work, try the backup patterns
        if not extracted_items:
            print("Main pattern didn't match, trying backup patterns...")
            for pattern in backup_patterns:
                try:
                    matches = re.findall(pattern, self.js_content, re.DOTALL)
                    for match in matches:
                        # Try to find individual item objects
                        item_matches = re.findall(r'\{(.*?)\}', match, re.DOTALL)
                        for item_str in item_matches:
                            item = self._parse_item_properties(item_str)
                            if item:
                                extracted_items.append(item)
                                print(f"Found item with backup pattern: {item['name']}")
                except Exception as e:
                    print(f"Error in pattern matching: {str(e)}")
        
        # If we still don't have items, try an advanced regex to find the structure
        if not extracted_items:
            print("Trying more aggressive pattern matching...")
            try:
                # Look for a structure like e.exports = { item: [{ ... }] }
                advanced_pattern = r'(?:e\.exports|module\.exports)\s*=\s*\{.*?item\s*:\s*\[\s*\{(.*?)\}\s*\]'
                matches = re.findall(advanced_pattern, self.js_content, re.DOTALL)
                
                if matches:
                    # Process similar to the main pattern
                    item_contents = matches[0]
                    item_strings = re.split(r'\},\s*\{', item_contents)
                    
                    for i, item_str in enumerate(item_strings):
                        # Add back the curly braces that were removed in the split
                        if i > 0:
                            item_str = '{' + item_str
                        if i < len(item_strings) - 1:
                            item_str = item_str + '}'
                        
                        # Parse the item
                        item = self._parse_item_from_js(item_str)
                        if item:
                            extracted_items.append(item)
                            print(f"Found item with advanced pattern: {item['name']}")
            except Exception as e:
                print(f"Error in advanced pattern matching: {str(e)}")
        
        return extracted_items
        
    def _extract_equipment_array(self, equipment_type, array_key):
        """
        Extract equipment arrays like weapons and armor from the JavaScript content.
        
        Args:
            equipment_type (str): Type of equipment ('weapon' or 'armor')
            array_key (str): The key in the JS object ('wep' or 'arm')
            
        Returns:
            list: Extracted equipment items
        """
        # Pattern to find equipment arrays
        pattern = fr'{array_key}\s*:\s*\[\s*\{{(.*?)\}}\s*\]'
        
        extracted_items = []
        
        try:
            matches = re.findall(pattern, self.js_content, re.DOTALL)
            if matches:
                # Process the equipment array
                equipment_contents = matches[0]
                equipment_strings = re.split(r'\},\s*\{', equipment_contents)
                
                for i, equip_str in enumerate(equipment_strings):
                    # Add back the curly braces that were removed in the split
                    if i > 0:
                        equip_str = '{' + equip_str
                    if i < len(equipment_strings) - 1:
                        equip_str = equip_str + '}'
                    
                    # Parse the equipment item
                    item = self._parse_equipment_from_js(equip_str, equipment_type)
                    if item:
                        extracted_items.append(item)
                        print(f"Found {equipment_type}: {item['name']}")
                        
        except Exception as e:
            print(f"Error extracting {equipment_type} array: {str(e)}")
            
        return extracted_items
        
    def _parse_equipment_from_js(self, equip_str, equipment_type):
        """
        Parse equipment (weapon/armor) from JavaScript.
        
        Args:
            equip_str (str): String representation of equipment
            equipment_type (str): 'weapon' or 'armor'
            
        Returns:
            dict: Parsed equipment item or None if parsing fails
        """
        try:
            # Extract basic properties
            idx_match = re.search(r'idx\s*:\s*(\d+)', equip_str)
            name_match = re.search(r'name\s*:\s*["\']([^"\']*)["\']', equip_str)
            ctg_match = re.search(r'ctg\s*:\s*["\']([^"\']*)["\']', equip_str)
            
            if not name_match:
                return None
                
            # Determine specific equipment type based on category
            specific_type = 'Weapon'
            category = 'Sword'  # Default
            
            if equipment_type == 'armor':
                specific_type = 'Armor'
                category = 'Medium'  # Default
                
                # Check if it's a different armor type
                if ctg_match:
                    ctg = ctg_match.group(1)
                    if ctg == 'head':
                        specific_type = 'Helmet'
                        category = 'Helm'
                    elif ctg == 'shield':
                        specific_type = 'Shield'
                        category = 'Shield'
                    elif ctg == 'acce' or ctg == 'accessory':
                        specific_type = 'Accessory'
                        category = 'Ring'
            
            if equipment_type == 'weapon' and ctg_match:
                ctg = ctg_match.group(1)
                if ctg == 'slash':
                    category = 'Sword'
                elif ctg == 'pierce':
                    category = 'Spear'
                elif ctg == 'blow':
                    category = 'Axe'
                elif ctg == 'wand' or ctg == 'staff':
                    category = 'Staff'
                    
            # Create the equipment item
            item = {
                'name': name_match.group(1),
                'type': specific_type,
                'category': category,
                'power': 0,
                'price': 0,
                'description': f"A {specific_type.lower()}."
            }
            
            # Extract item ID if available
            if idx_match:
                item['id'] = int(idx_match.group(1))
            
            # Extract price information
            buy_match = re.search(r'buy\s*:\s*(\d+)', equip_str)
            sell_match = re.search(r'sell\s*:\s*(\d+)', equip_str)
            
            if buy_match:
                item['price'] = int(buy_match.group(1))
                
            # Extract job restrictions
            job_match = re.search(r'job\s*:\s*\[(.*?)\]', equip_str)
            if job_match:
                job_str = job_match.group(1)
                # Convert job indices to a list of integers
                job_values = [int(v.strip()) for v in job_str.split(',') if v.strip().isdigit()]
                item['job_restrictions'] = job_values
            else:
                item['job_restrictions'] = []
                
            # Extract stats based on equipment type
            st_match = re.search(r'st\s*:\s*\{(.*?)\}', equip_str, re.DOTALL)
            if st_match:
                st_str = st_match.group(1)
                
                # Initialize stat bonuses
                item['stat_bonuses'] = {'pw': 0, 'sp': 0, 'it': 0, 'st': 0, 'lk': 0}
                
                # For weapons, check weapon power
                if equipment_type == 'weapon':
                    wp_match = re.search(r'wp\s*:\s*(\d+)', st_str)
                    if wp_match:
                        item['power'] = int(wp_match.group(1))
                    
                    # Check critical hit rate
                    crt_match = re.search(r'crt\s*:\s*(\d+)', st_str)
                    if crt_match:
                        item['stat_bonuses']['lk'] = int(crt_match.group(1))
                
                # For armor, check armor and evasion
                elif equipment_type == 'armor':
                    am_match = re.search(r'am\s*:\s*(\d+)', st_str)
                    if am_match:
                        item['power'] = int(am_match.group(1))
                    
                    # Check evasion (might be negative)
                    ev_match = re.search(r'ev\s*:\s*(-?\d+)', st_str)
                    if ev_match:
                        item['stat_bonuses']['sp'] = int(ev_match.group(1))
            
            return item
        except Exception as e:
            print(f"Error parsing equipment: {str(e)}")
            return None
        
    def _parse_item_from_js(self, item_str):
        """Parse an item from its JavaScript object representation."""
        try:
            # Extract basic properties with more precise regex patterns
            idx_match = re.search(r'idx\s*:\s*(\d+)', item_str)
            name_match = re.search(r'name\s*:\s*["\']([^"\']*)["\']', item_str)
            
            if not name_match:
                return None
            
            item = {
                'name': name_match.group(1),
                'type': 'Consumable',  # Default type
                'power': 0,
                'price': 0,
                'description': f"A consumable item."
            }
            
            # Extract item ID if available
            if idx_match:
                item['id'] = int(idx_match.group(1))
            
            # Extract price information
            buy_match = re.search(r'buy\s*:\s*(\d+)', item_str)
            sell_match = re.search(r'sell\s*:\s*(\d+)', item_str)
            
            if buy_match:
                item['price'] = int(buy_match.group(1))
            
            # Extract maximum quantity
            max_match = re.search(r'max\s*:\s*(\d+)', item_str)
            if max_match:
                item['quantity'] = int(max_match.group(1))
            else:
                item['quantity'] = 1
            
            # Extract effect/action information
            act_match = re.search(r'act\s*:\s*\{(.*?)\}', item_str, re.DOTALL)
            if act_match:
                act_str = act_match.group(1)
                
                # Extract effect type
                effect_id_match = re.search(r'id\s*:\s*["\']([^"\']*)["\']', act_str)
                if effect_id_match:
                    effect_id = effect_id_match.group(1)
                    
                    # Set effect type based on id
                    if effect_id in ['heal', 'tent']:
                        item['effect'] = {
                            'type': 'Restore HP',
                            'target': 'Single',
                            'strength': 0,
                            'status': {}
                        }
                    elif effect_id == 'detox':
                        item['effect'] = {
                            'type': 'Cure Status',
                            'target': 'Single',
                            'strength': 0,
                            'status': {'poison': True}
                        }
                    else:
                        item['effect'] = {
                            'type': 'None',
                            'target': 'Self',
                            'strength': 0,
                            'status': {}
                        }
                    
                    # Extract effect value if present
                    val_match = re.search(r'val\s*:\s*(\d+)', act_str)
                    if val_match:
                        item['effect']['strength'] = int(val_match.group(1))
                    
                    # Extract target
                    trg_match = re.search(r'trg\s*:\s*\[\s*["\']([^"\']*)["\'],\s*["\']([^"\']*)["\']', act_str)
                    if trg_match:
                        target_type = trg_match.group(1)
                        target_scope = trg_match.group(2)
                        
                        if target_scope == 'all':
                            item['effect']['target'] = 'All' if target_type == 'player' else 'All Enemies'
                        else:
                            item['effect']['target'] = 'Single' if target_type == 'player' else 'Enemy'
            
            # Extract message as description
            msg_match = re.search(r'msg\s*:\s*["\']([^"\']*)["\']', item_str)
            if msg_match:
                # Clean up description by removing HTML tags
                description = msg_match.group(1).replace('<br>', ' ')
                item['description'] = description
            
            # Determine item type based on properties and name
            if 'テント' in item['name'] or 'خيمة' in item['name'] or 'tent' in item_str.lower():
                item['type'] = 'Consumable'
                item['category'] = 'Tent'
            elif 'ポーション' in item['name'] or 'شفاء' in item['name'] or 'heal' in item_str.lower():
                item['type'] = 'Consumable'
                item['category'] = 'Potion'
            elif 'どく' in item['name'] or 'نقي' in item['name'] or 'detox' in item_str.lower():
                item['type'] = 'Consumable'
                item['category'] = 'Antidote'
            elif 'battle' in item_str and '"battle":!1' in item_str:
                # Items that can't be used in battle are often key items
                item['type'] = 'Key Item'
            
            # Add default for remaining properties
            item['job_restrictions'] = []
            item['stat_bonuses'] = {'pw': 0, 'sp': 0, 'it': 0, 'st': 0, 'lk': 0}
            item['rarity'] = 'Common'
            
            return item
        except Exception as e:
            print(f"Error parsing item from JS: {str(e)}")
            return None
        
    def _parse_item_properties(self, item_str):
        """Parse item properties from a string representation."""
        try:
            item = {}
            
            # Extract name if available
            name_match = re.search(r'name\s*:\s*["\']([^"\']*)["\']', item_str)
            if name_match:
                item['name'] = name_match.group(1)
            else:
                # Try alternative formats
                alt_name_match = re.search(r'name\s*=\s*["\']([^"\']*)["\']', item_str)
                if alt_name_match:
                    item['name'] = alt_name_match.group(1)
                else:
                    # Skip items without a name
                    return None
                
            # Extract type
            type_match = re.search(r'type\s*:\s*["\']?([^"\',:;]+)["\']?', item_str)
            if not type_match:
                type_match = re.search(r'type\s*=\s*["\']?([^"\',:;]+)["\']?', item_str)
                
            if type_match:
                item['type'] = type_match.group(1)
            else:
                # Try to infer type from other properties or context
                if 'weapon' in item_str.lower() or 'sword' in item_str.lower() or 'atk' in item_str.lower():
                    item['type'] = 'Weapon'
                elif 'armor' in item_str.lower() or 'def' in item_str.lower():
                    item['type'] = 'Armor'
                elif 'potion' in item_str.lower() or 'heal' in item_str.lower():
                    item['type'] = 'Consumable'
                elif 'key' in item_str.lower():
                    item['type'] = 'Key Item'
                else:
                    item['type'] = 'Misc'
                
            # Extract power/effect
            power_match = re.search(r'power\s*:\s*(\d+)', item_str)
            if not power_match:
                # Try alternative property names
                power_match = re.search(r'(?:atk|attack|str|strength|def|defense)\s*:\s*(\d+)', item_str)
                
            if power_match:
                item['power'] = int(power_match.group(1))
            else:
                item['power'] = 0
                
            # Extract price
            price_match = re.search(r'price\s*:\s*(\d+)', item_str)
            if not price_match:
                price_match = re.search(r'(?:cost|value|gold|buy)\s*:\s*(\d+)', item_str)
                
            if price_match:
                item['price'] = int(price_match.group(1))
            else:
                item['price'] = 0
                
            # Extract description
            desc_match = re.search(r'(?:desc|description|msg)\s*:\s*["\']([^"\']*)["\']', item_str)
            if desc_match:
                item['description'] = desc_match.group(1).replace('<br>', ' ')
            else:
                item['description'] = f"A {item['type'].lower()}"
                
            # Set default values for other properties
            item['quantity'] = 1
            
            # Try to get max quantity
            max_match = re.search(r'max\s*:\s*(\d+)', item_str)
            if max_match:
                item['quantity'] = int(max_match.group(1))
                
            item['effect'] = {
                'target': 'Self',
                'type': 'None',
                'strength': 0,
                'status': {'poison': False, 'paralyze': False}
            }
            item['job_restrictions'] = []
            item['stat_bonuses'] = {'pw': 0, 'sp': 0, 'it': 0, 'st': 0, 'lk': 0}
            item['rarity'] = 'Common'
            
            # Extract effect/action information
            act_match = re.search(r'act\s*:\s*\{(.*?)\}', item_str, re.DOTALL)
            if act_match:
                act_str = act_match.group(1)
                
                # Extract effect type
                effect_id_match = re.search(r'id\s*:\s*["\']([^"\']*)["\']', act_str)
                if effect_id_match:
                    effect_id = effect_id_match.group(1)
                    
                    # Set effect type based on id
                    if effect_id in ['heal', 'tent']:
                        item['effect']['type'] = 'Restore HP'
                    elif effect_id == 'detox':
                        item['effect']['type'] = 'Cure Status'
                        item['effect']['status']['poison'] = True
                    
                    # Extract effect value if present
                    val_match = re.search(r'val\s*:\s*(\d+)', act_str)
                    if val_match:
                        item['effect']['strength'] = int(val_match.group(1))
                    
                    # Extract target
                    trg_match = re.search(r'trg\s*:\s*\[\s*["\']([^"\']*)["\'],\s*["\']([^"\']*)["\']', act_str)
                    if trg_match:
                        target_type = trg_match.group(1)
                        target_scope = trg_match.group(2)
                        
                        if target_scope == 'all':
                            item['effect']['target'] = 'All' if target_type == 'player' else 'All Enemies'
                        else:
                            item['effect']['target'] = 'Single' if target_type == 'player' else 'Enemy'
            
            # For weapons and armor, add job restrictions based on type
            if item['type'] == 'Weapon':
                # Default: Mages can't use heavy weapons
                item['job_restrictions'] = [2, 3]
            elif item['type'] == 'Armor':
                # Default: Mages can't use heavy armor
                item['job_restrictions'] = [2, 3]
            
            # Extract item subcategory if relevant
            if item['type'] in ['Weapon', 'Armor', 'Accessory', 'Consumable']:
                item['category'] = self.extract_item_subcategories(item['type'], item_str)
                
            return item
        except Exception as e:
            print(f"Error parsing item: {str(e)}")
            return None
            
    def extract_item_subcategories(self, item_type, item_str):
        """Extract subcategory for items based on type and properties."""
        if item_type == 'Weapon':
            # Logic to determine weapon type (sword, axe, etc.)
            if 'sword' in item_str.lower():
                return 'Sword'
            elif 'axe' in item_str.lower():
                return 'Axe'
            elif 'staff' in item_str.lower() or 'rod' in item_str.lower():
                return 'Staff'
            elif 'dagger' in item_str.lower() or 'knife' in item_str.lower():
                return 'Dagger'
            else:
                return 'Sword'  # Default
                
        elif item_type == 'Armor':
            # Logic to determine armor type
            if 'robe' in item_str.lower():
                return 'Robe'
            elif 'leather' in item_str.lower():
                return 'Light'
            elif 'plate' in item_str.lower() or 'mail' in item_str.lower():
                return 'Heavy'
            else:
                return 'Medium'  # Default
                
        elif item_type == 'Accessory':
            # Logic to determine accessory type
            if 'ring' in item_str.lower():
                return 'Ring'
            elif 'amulet' in item_str.lower() or 'pendant' in item_str.lower():
                return 'Amulet'
            elif 'bracelet' in item_str.lower() or 'bangle' in item_str.lower():
                return 'Bracelet'
            else:
                return 'Ring'  # Default
                
        elif item_type == 'Consumable':
            # Logic to determine consumable type
            if 'potion' in item_str.lower() or 'heal' in item_str.lower() or 'شفاء' in item_str:
                return 'Potion'
            elif 'ether' in item_str.lower() or 'mp' in item_str.lower():
                return 'Ether'
            elif 'elixir' in item_str.lower():
                return 'Elixir'
            elif 'antidote' in item_str.lower() or 'detox' in item_str.lower() or 'نقي' in item_str:
                return 'Antidote'
            elif 'tent' in item_str.lower() or 'テント' in item_str or 'خيمة' in item_str:
                return 'Tent'
            else:
                return 'Potion'  # Default
        
        return ""  # Empty string for types that don't have subcategories
            
    def get_item_by_name(self, name):
        """Get an item by name."""
        for item in self.items:
            if item.get('name') == name:
                return item
        return None

    def _extract_magic_array(self):
        """
        Extract magic items/spells from the JavaScript content.
        
        Returns:
            list: Extracted magic items
        """
        # Pattern to find magic array
        pattern = r'mgc\s*:\s*\[\s*\{(.*?)\}\s*\]'
        
        extracted_items = []
        
        try:
            matches = re.findall(pattern, self.js_content, re.DOTALL)
            if matches:
                # Process the magic array
                magic_contents = matches[0]
                magic_strings = re.split(r'\},\s*\{', magic_contents)
                
                for i, magic_str in enumerate(magic_strings):
                    # Add back the curly braces that were removed in the split
                    if i > 0:
                        magic_str = '{' + magic_str
                    if i < len(magic_strings) - 1:
                        magic_str = magic_str + '}'
                    
                    # Parse the magic item
                    item = self._parse_magic_from_js(magic_str)
                    if item:
                        extracted_items.append(item)
                        print(f"Found magic spell: {item['name']}")
                        
        except Exception as e:
            print(f"Error extracting magic array: {str(e)}")
            
        return extracted_items
        
    def _parse_magic_from_js(self, magic_str):
        """
        Parse magic spell/ability from JavaScript.
        
        Args:
            magic_str (str): String representation of magic spell
            
        Returns:
            dict: Parsed magic item or None if parsing fails
        """
        try:
            # Extract basic properties
            idx_match = re.search(r'idx\s*:\s*(\d+)', magic_str)
            name_match = re.search(r'name\s*:\s*["\']([^"\']*)["\']', magic_str)
            mlv_match = re.search(r'mlv\s*:\s*(\d+)', magic_str)
            
            if not name_match:
                return None
                
            # Create the magic item
            item = {
                'name': name_match.group(1),
                'type': 'Magic',
                'category': 'Spell',
                'power': 0,
                'price': 0,
                'description': "A magic spell."
            }
            
            # Extract item ID if available
            if idx_match:
                item['id'] = int(idx_match.group(1))
                
            # Extract magic level
            if mlv_match:
                item['magic_level'] = int(mlv_match.group(1))
            
            # Extract price information
            buy_match = re.search(r'buy\s*:\s*(\d+)', magic_str)
            if buy_match:
                item['price'] = int(buy_match.group(1))
                
            # Extract job restrictions
            job_match = re.search(r'job\s*:\s*\[(.*?)\]', magic_str)
            if job_match:
                job_str = job_match.group(1)
                # Convert job indices to a list of integers
                job_values = [int(v.strip()) for v in job_str.split(',') if v.strip().isdigit()]
                item['job_restrictions'] = job_values
            else:
                item['job_restrictions'] = []
                
            # Extract effect information
            act_match = re.search(r'act\s*:\s*\{(.*?)\}', magic_str, re.DOTALL)
            if act_match:
                act_str = act_match.group(1)
                
                # Default effect structure
                item['effect'] = {
                    'type': 'Magic Attack',
                    'target': 'Single',
                    'strength': 0,
                    'status': {}
                }
                
                # Extract effect ID
                effect_id_match = re.search(r'id\s*:\s*["\']([^"\']*)["\']', act_str)
                if effect_id_match:
                    effect_id = effect_id_match.group(1)
                    
                    # Set effect type based on id
                    if effect_id == 'heal':
                        item['effect']['type'] = 'Restore HP'
                        item['category'] = 'Healing'
                    elif effect_id == 'fire':
                        item['effect']['type'] = 'Fire Damage'
                        item['category'] = 'Black Magic'
                    elif effect_id == 'thunder':
                        item['effect']['type'] = 'Lightning Damage'
                        item['category'] = 'Black Magic'
                    elif effect_id in ['dia', 'holy']:
                        item['effect']['type'] = 'Holy Damage'
                        item['category'] = 'White Magic'
                    elif effect_id == 'blink':
                        item['effect']['type'] = 'Evasion Up'
                        item['category'] = 'Support'
                    elif effect_id == 'protes':
                        item['effect']['type'] = 'Defense Up'
                        item['category'] = 'Support'
                    elif effect_id == 'sripl':
                        item['effect']['type'] = 'Cause Status'
                        item['effect']['status'] = {'sleep': True}
                        item['category'] = 'Status'
                    elif effect_id == 'shape':
                        item['effect']['type'] = 'Morph'
                        item['category'] = 'Special'
                    else:
                        # Generic categorization based on effect ID
                        item['effect']['type'] = effect_id.title()
                        item['category'] = 'Other'
                
                # Extract target info
                trg_match = re.search(r'trg\s*:\s*\[\s*["\']([^"\']*)["\'],\s*["\']([^"\']*)["\']', act_str)
                if trg_match:
                    target_type = trg_match.group(1)
                    target_scope = trg_match.group(2)
                    
                    if target_scope == 'all':
                        item['effect']['target'] = 'All' if target_type == 'player' else 'All Enemies'
                    elif target_scope == 'single':
                        item['effect']['target'] = 'Single' if target_type == 'player' else 'Enemy'
                    elif target_scope == 'self':
                        item['effect']['target'] = 'Self'
                
                # Extract effect value
                val_match = re.search(r'val\s*:\s*(\d+)', act_str)
                if val_match:
                    item['effect']['strength'] = int(val_match.group(1))
                else:
                    # Try to extract min/max value range
                    min_max_match = re.search(r'val\s*:\s*\{\s*min\s*:\s*(\d+),\s*max\s*:\s*(\d+)', act_str)
                    if min_max_match:
                        min_val = int(min_max_match.group(1))
                        max_val = int(min_max_match.group(2))
                        # Use average as strength
                        item['effect']['strength'] = (min_val + max_val) // 2
                        # Store min/max separately
                        item['effect']['min_value'] = min_val
                        item['effect']['max_value'] = max_val
            
            # Extract description
            msg_match = re.search(r'msg\s*:\s*["\']([^"\']*)["\']', magic_str)
            if msg_match:
                description = msg_match.group(1).replace('<br>', ' ')
                item['description'] = description
            else:
                # Set a default description based on effect
                if 'effect' in item and 'type' in item['effect']:
                    item['description'] = f"A spell that {item['effect']['type'].lower()}."
            
            # Setup stat bonuses for consistency with other items
            item['stat_bonuses'] = {'pw': 0, 'sp': 0, 'it': 0, 'st': 0, 'lk': 0, 'ma': 0}
            
            # Set rarity based on magic level or other factors
            if 'magic_level' in item:
                if item['magic_level'] >= 7:
                    item['rarity'] = 'Legendary'
                elif item['magic_level'] >= 5:
                    item['rarity'] = 'Epic'
                elif item['magic_level'] >= 3:
                    item['rarity'] = 'Rare'
                elif item['magic_level'] >= 1:
                    item['rarity'] = 'Uncommon'
                else:
                    item['rarity'] = 'Common'
            else:
                item['rarity'] = 'Common'
            
            return item
        except Exception as e:
            print(f"Error parsing magic spell: {str(e)}")
            return None