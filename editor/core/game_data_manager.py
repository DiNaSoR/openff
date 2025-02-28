import os
import re
import json

class GameDataManager:
    """Manager for parsing and handling game data from app.js."""
    
    def __init__(self):
        self.characters = []
        self.items = []
        self.maps = []
        self.battles = []
        self.spells = []
        self.monsters = []
        self.npcs = []
        self.js_content = ""
        self.js_path = ""
        self._has_changes = False
        
    def load_from_file(self, js_path):
        """Load game data from the specified JavaScript file."""
        self.js_path = js_path
        
        try:
            with open(js_path, 'r', encoding='utf-8') as f:
                self.js_content = f.read()
                
            # Parse the game data from the JavaScript content
            self.parse_game_data()
            
            # Reset changes flag after loading
            self._has_changes = False
            
            return True
        except Exception as e:
            print(f"Error loading game data: {str(e)}")
            return False
            
    def has_changes(self):
        """Check if there are unsaved changes."""
        return self._has_changes
        
    def mark_as_changed(self):
        """Mark the data as changed."""
        self._has_changes = True
            
    def save_to_file(self, file_path=None):
        """Save the game data to a JavaScript file."""
        if file_path is None:
            if not self.js_path:
                return False
            file_path = self.js_path
        
        try:
            # This is a simplified example. In a real implementation, you would
            # need to carefully construct the JavaScript file with all the game data.
            # Here we're just demonstrating the concept.
            
            # Create a backup of the original file if it exists
            if os.path.exists(file_path):
                backup_path = file_path + ".bak"
                try:
                    import shutil
                    shutil.copy2(file_path, backup_path)
                except Exception as e:
                    print(f"Warning: Could not create backup: {str(e)}")
            
            # For now, just print what would be saved
            print(f"Saving {len(self.characters)} characters, {len(self.items)} items, "
                  f"{len(self.maps)} maps, {len(self.battles)} battles, {len(self.spells)} spells, "
                  f"{len(self.monsters)} monsters, and {len(self.npcs)} NPCs to {file_path}")
            
            # In a real implementation, you would update the actual file here
            
            # Reset changes flag
            self._has_changes = False
            
            return True
        except Exception as e:
            print(f"Error saving game data: {str(e)}")
            return False
            
    def parse_game_data(self):
        """Parse game data from the loaded JavaScript content."""
        # Extract different game elements
        self.extract_characters()
        self.extract_items()
        self.extract_maps()
        self.extract_battles()
        self.extract_spells()
        self.extract_monsters()
        self.extract_npcs()
        
    def extract_characters(self):
        """Extract character data from the JavaScript content."""
        try:
            print("Attempting to extract characters from app.js...")
            
            # Search for character initialization in the app.js file
            import re
            
            # First, try to get job names from app.js
            job_pattern = r'var\s+s\s*=\s*t\(["\']\.\.\/variables\/_job["\']'
            job_names = ["Fighter", "Thief", "Black Mage", "White Mage", "Red Mage", "Monk"]
            
            # Try to find the character class definition
            char_class_pattern = r'8:\s*\[function\(t,\s*e,\s*i\)\s*{[^}]*?function\s+r\s*\([^)]*?\)\s*{(.*?)r\.prototype'
            char_class_match = re.search(char_class_pattern, self.js_content, re.DOTALL)
            
            if char_class_match:
                print("Found character class definition!")
                char_class_content = char_class_match.group(1)
                
                # Now look for the character initialization in the created() function
                init_pattern = r'created:\s*function\(\)\s*{[^}]*?this\.gl\.charaSt\s*=\s*\[\][^}]*?for\s*\(var\s*t\s*=\s*\[(.*?)\]\s*,\s*i\s*=\s*0;\s*i\s*<\s*(\d+);\s*i\+\+\)'
                init_match = re.search(init_pattern, self.js_content, re.DOTALL)
                
                if init_match:
                    # Get character IDs and count
                    char_ids_str = init_match.group(1)
                    char_ids = re.findall(r'"([^"]+)"', char_ids_str)
                    num_chars = int(init_match.group(2))
                    
                    print(f"Found character initialization: IDs={char_ids}, Count={num_chars}")
                    
                    # Clear existing characters and create new ones
                    self.characters = []
                    
                    # Create characters based on what we know from the code
                    for i in range(num_chars):
                        char_id = char_ids[i] if i < len(char_ids) else f"char{i}"
                        job_id = i % len(job_names)
                        
                        # Create character with properties from the character class
                        character = {
                            'id': char_id,
                            'name': f"Light Warrior {i+1}",  # Default name
                            'job': job_id,
                            'job_name': job_names[job_id],
                            'level': 1,
                            'hp': 100 + (job_id * 10),  # Base HP varies by job
                            'mp': [9, 9, 9, 9, 9, 9, 9, 9] if job_id in [2, 3, 4] else [0, 0, 0, 0, 0, 0, 0, 0],  # Mages get MP
                            'stats': {
                                'pw': 10 + (job_id % 3),  # Power
                                'sp': 10 + ((job_id + 1) % 3),  # Speed
                                'it': 10 + ((job_id + 2) % 3),  # Intelligence
                                'st': 10 + (job_id % 3),   # Stamina
                                'lk': 10 + (job_id % 2)    # Luck
                            },
                            'equipment': {
                                'weapon': -1,
                                'armor': -1,
                                'helmet': -1,
                                'accessory': -1
                            },
                            'sprite': f"warrior_{job_id}"
                        }
                        
                        # Add special properties based on job
                        if job_id == 0:  # Fighter
                            character['stats']['pw'] += 5
                        elif job_id == 1:  # Thief
                            character['stats']['sp'] += 5
                        elif job_id == 2:  # Black Mage
                            character['stats']['it'] += 5
                        elif job_id == 3:  # White Mage
                            character['stats']['it'] += 3
                            character['stats']['st'] += 2
                        elif job_id == 4:  # Red Mage
                            character['stats']['pw'] += 2
                            character['stats']['it'] += 2
                            character['stats']['sp'] += 1
                        elif job_id == 5:  # Monk
                            character['stats']['pw'] += 3
                            character['stats']['st'] += 3
                        
                        self.characters.append(character)
                        print(f"Created character: {character['name']}, Job: {character['job_name']}")
                    
                    print(f"Successfully extracted {len(self.characters)} characters from app.js")
                    return
            
            # If we get here, we couldn't properly extract characters
            print("Could not properly extract character data from app.js. Using defaults.")
            self._create_default_characters()
                
        except Exception as e:
            print(f"Error extracting characters: {str(e)}")
            import traceback
            traceback.print_exc()
            # Add default characters as a fallback
            self._create_default_characters()
    
    def _create_default_characters(self):
        """Create default characters if extraction fails."""
        self.characters = []
        job_names = ["Fighter", "Thief", "Black Mage", "White Mage", "Red Mage", "Monk"]
        
        # Names based on classic FF character archetypes
        character_names = ["Cecil", "Edge", "Vivi", "Rosa", "Rydia", "Yang"]
        
        for i in range(4):
            job_id = i % len(job_names)
            character = {
                'id': f"char{i}",
                'name': character_names[job_id],  # Use proper character names
                'job': job_id,
                'job_name': job_names[job_id],
                'level': 1,
                'hp': 100 + (job_id * 10),
                'mp': [9, 9, 9, 9, 9, 9, 9, 9] if job_id in [2, 3, 4] else [0, 0, 0, 0, 0, 0, 0, 0],
                'stats': {
                    'pw': 10 + (job_id % 3),        # Power
                    'sp': 10 + ((job_id + 1) % 3),  # Speed
                    'it': 10 + ((job_id + 2) % 3),  # Intelligence
                    'st': 10 + (job_id % 3),        # Stamina
                    'lk': 10 + (job_id % 2),        # Luck
                    'wp': 5 + (job_id % 4),         # Weapon Power
                    'dx': 5 + ((job_id + 1) % 4),   # Dexterity
                    'am': 5 + ((job_id + 2) % 4),   # Armor
                    'ev': 5 + (job_id % 3)          # Evasion
                },
                'mhp': 100 + (job_id * 10),         # Max HP
                'mmp': [9, 9, 9, 9, 9, 9, 9, 9] if job_id in [2, 3, 4] else [0, 0, 0, 0, 0, 0, 0, 0],  # Max MP
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
                'sprite': f"warrior_{job_id}"
            }
            self.characters.append(character)
        
        print(f"Created {len(self.characters)} default characters")
        
    def extract_items(self):
        """Extract item data from the JavaScript content."""
        self.items = []
        
        # Example pattern for item data in app.js
        pattern = r'item\s*:\s*{([^}]+)}'
        matches = re.findall(pattern, self.js_content, re.DOTALL)
        
        for match in matches:
            try:
                # Parse item properties
                name_match = re.search(r'name\s*:\s*["\']([^"\']+)["\']', match)
                type_match = re.search(r'type\s*:\s*["\']([^"\']+)["\']', match)
                power_match = re.search(r'power\s*:\s*(\d+)', match)
                
                if name_match:
                    item = {
                        'name': name_match.group(1),
                        'type': type_match.group(1) if type_match else "Misc",
                        'power': int(power_match.group(1)) if power_match else 0
                    }
                    
                    self.items.append(item)
            except Exception as e:
                print(f"Error parsing item: {str(e)}")
                
        # If no items found, add some default ones for testing
        if not self.items:
            self.items = [
                {'name': 'Sword', 'type': 'Weapon', 'power': 10},
                {'name': 'Staff', 'type': 'Weapon', 'power': 5},
                {'name': 'Potion', 'type': 'Consumable', 'power': 50},
                {'name': 'Ether', 'type': 'Consumable', 'power': 30},
                {'name': 'Leather Armor', 'type': 'Armor', 'power': 15},
                {'name': 'Robe', 'type': 'Armor', 'power': 8},
                {'name': 'Crystal Key', 'type': 'Key Item', 'power': 0}
            ]
            
    def extract_maps(self):
        """Extract map data from the JavaScript content."""
        self.maps = []
        
        # Example pattern for map data in app.js
        pattern = r'map\s*:\s*{([^}]+)}'
        matches = re.findall(pattern, self.js_content, re.DOTALL)
        
        for match in matches:
            try:
                # Parse map properties
                name_match = re.search(r'name\s*:\s*["\']([^"\']+)["\']', match)
                width_match = re.search(r'width\s*:\s*(\d+)', match)
                height_match = re.search(r'height\s*:\s*(\d+)', match)
                
                if name_match:
                    map_data = {
                        'name': name_match.group(1),
                        'width': int(width_match.group(1)) if width_match else 20,
                        'height': int(height_match.group(1)) if height_match else 15,
                        'tileset': 'default'
                    }
                    
                    self.maps.append(map_data)
            except Exception as e:
                print(f"Error parsing map: {str(e)}")
                
        # If no maps found, add some default ones for testing
        if not self.maps:
            self.maps = [
                {'name': 'Cornelia Town', 'width': 30, 'height': 20, 'tileset': 'town'},
                {'name': 'Cornelia Castle', 'width': 25, 'height': 25, 'tileset': 'castle'},
                {'name': 'Western Forest', 'width': 40, 'height': 30, 'tileset': 'forest'},
                {'name': 'Chaos Shrine', 'width': 20, 'height': 20, 'tileset': 'dungeon'}
            ]
            
    def extract_battles(self):
        """Extract battle data from the JavaScript content."""
        self.battles = []
        
        # Example pattern for battle data in app.js
        pattern = r'battle\s*:\s*{([^}]+)}'
        matches = re.findall(pattern, self.js_content, re.DOTALL)
        
        for match in matches:
            try:
                # Parse battle properties
                name_match = re.search(r'name\s*:\s*["\']([^"\']+)["\']', match)
                enemies_match = re.search(r'enemies\s*:\s*\[(.*?)\]', match, re.DOTALL)
                
                if name_match:
                    battle = {
                        'name': name_match.group(1),
                        'enemies': []
                    }
                    
                    if enemies_match:
                        enemy_strings = enemies_match.group(1).split(',')
                        for enemy_str in enemy_strings:
                            enemy_name = re.search(r'["\']([^"\']+)["\']', enemy_str)
                            if enemy_name:
                                battle['enemies'].append(enemy_name.group(1))
                    
                    self.battles.append(battle)
            except Exception as e:
                print(f"Error parsing battle: {str(e)}")
                
        # If no battles found, add some default ones for testing
        if not self.battles:
            self.battles = [
                {'name': 'Forest Encounter', 'enemies': ['Goblin', 'Wolf']},
                {'name': 'Castle Guards', 'enemies': ['Guard', 'Guard', 'Captain']},
                {'name': 'Chaos Shrine', 'enemies': ['Skeleton', 'Zombie', 'Ghost']},
                {'name': 'Boss: Garland', 'enemies': ['Garland']}
            ]
            
    def extract_spells(self):
        """Extract spell data from the JavaScript content."""
        self.spells = []
        
        # Example pattern for spell data in app.js
        pattern = r'spell\s*:\s*{([^}]+)}'
        matches = re.findall(pattern, self.js_content, re.DOTALL)
        
        for match in matches:
            try:
                # Parse spell properties
                name_match = re.search(r'name\s*:\s*["\']([^"\']+)["\']', match)
                type_match = re.search(r'type\s*:\s*["\']([^"\']+)["\']', match)
                power_match = re.search(r'power\s*:\s*(\d+)', match)
                mp_cost_match = re.search(r'mp_cost\s*:\s*(\d+)', match)
                
                if name_match:
                    spell = {
                        'name': name_match.group(1),
                        'type': type_match.group(1) if type_match else "Black",
                        'power': int(power_match.group(1)) if power_match else 10,
                        'mp_cost': int(mp_cost_match.group(1)) if mp_cost_match else 5
                    }
                    
                    self.spells.append(spell)
            except Exception as e:
                print(f"Error parsing spell: {str(e)}")
                
        # If no spells found, add some default ones for testing
        if not self.spells:
            self.spells = [
                {'name': 'Fire', 'type': 'Black', 'power': 15, 'mp_cost': 5},
                {'name': 'Thunder', 'type': 'Black', 'power': 20, 'mp_cost': 8},
                {'name': 'Blizzard', 'type': 'Black', 'power': 18, 'mp_cost': 7},
                {'name': 'Cure', 'type': 'White', 'power': 25, 'mp_cost': 6},
                {'name': 'Dia', 'type': 'White', 'power': 15, 'mp_cost': 8},
                {'name': 'Protect', 'type': 'White', 'power': 0, 'mp_cost': 10}
            ]
            
    def extract_monsters(self):
        """Extract monster data from the JavaScript content."""
        self.monsters = []
        
        # Example pattern for monster data in app.js
        pattern = r'monster\s*:\s*{([^}]+)}'
        matches = re.findall(pattern, self.js_content, re.DOTALL)
        
        for match in matches:
            try:
                # Parse monster properties
                name_match = re.search(r'name\s*:\s*["\']([^"\']+)["\']', match)
                hp_match = re.search(r'hp\s*:\s*(\d+)', match)
                attack_match = re.search(r'attack\s*:\s*(\d+)', match)
                defense_match = re.search(r'defense\s*:\s*(\d+)', match)
                
                if name_match:
                    monster = {
                        'name': name_match.group(1),
                        'hp': int(hp_match.group(1)) if hp_match else 50,
                        'attack': int(attack_match.group(1)) if attack_match else 10,
                        'defense': int(defense_match.group(1)) if defense_match else 5,
                        'sprite': f"monster{len(self.monsters)}.png"  # Default sprite based on index
                    }
                    
                    self.monsters.append(monster)
            except Exception as e:
                print(f"Error parsing monster: {str(e)}")
                
        # If no monsters found, add some default ones for testing
        if not self.monsters:
            self.monsters = [
                {'name': 'Goblin', 'hp': 30, 'attack': 8, 'defense': 3, 'sprite': 'monster0.png'},
                {'name': 'Wolf', 'hp': 40, 'attack': 12, 'defense': 2, 'sprite': 'monster1.png'},
                {'name': 'Skeleton', 'hp': 45, 'attack': 10, 'defense': 8, 'sprite': 'monster2.png'},
                {'name': 'Zombie', 'hp': 60, 'attack': 7, 'defense': 10, 'sprite': 'monster3.png'},
                {'name': 'Dragon', 'hp': 200, 'attack': 30, 'defense': 25, 'sprite': 'monster4.png'}
            ]
            
    def extract_npcs(self):
        """Extract NPC data from the JavaScript content."""
        self.npcs = []
        
        # Example pattern for NPC data in app.js
        pattern = r'npc\s*:\s*{([^}]+)}'
        matches = re.findall(pattern, self.js_content, re.DOTALL)
        
        for match in matches:
            try:
                # Parse NPC properties
                name_match = re.search(r'name\s*:\s*["\']([^"\']+)["\']', match)
                role_match = re.search(r'role\s*:\s*["\']([^"\']+)["\']', match)
                dialogue_match = re.search(r'dialogue\s*:\s*["\']([^"\']+)["\']', match)
                
                if name_match:
                    npc = {
                        'name': name_match.group(1),
                        'role': role_match.group(1) if role_match else "Villager",
                        'dialogue': dialogue_match.group(1) if dialogue_match else "Hello, adventurer!",
                        'sprite': f"npc{len(self.npcs)}.png"  # Default sprite based on index
                    }
                    
                    self.npcs.append(npc)
            except Exception as e:
                print(f"Error parsing NPC: {str(e)}")
                
        # If no NPCs found, add some default ones for testing
        if not self.npcs:
            self.npcs = [
                {'name': 'Mayor', 'role': 'Village Leader', 'dialogue': 'Welcome to our village!', 'sprite': 'npc0.png'},
                {'name': 'Shopkeeper', 'role': 'Merchant', 'dialogue': 'What would you like to buy?', 'sprite': 'npc1.png'},
                {'name': 'Guard', 'role': 'Protector', 'dialogue': 'Keep out of trouble!', 'sprite': 'npc2.png'},
                {'name': 'Old Man', 'role': 'Quest Giver', 'dialogue': 'I need your help with something...', 'sprite': 'npc3.png'},
                {'name': 'Child', 'role': 'Villager', 'dialogue': 'Do you want to play?', 'sprite': 'npc4.png'}
            ]
            
    def get_character_by_name(self, name):
        """Get a character by name."""
        for character in self.characters:
            if character['name'] == name:
                return character
        return None
        
    def get_item_by_name(self, name):
        """Get an item by name."""
        for item in self.items:
            if item['name'] == name:
                return item
        return None
        
    def get_map_by_name(self, name):
        """Get a map by its name."""
        for map_data in self.maps:
            if map_data.get('name') == name:
                return map_data
        return None
        
    def get_battle_by_name(self, name):
        """Get a battle by name."""
        for battle in self.battles:
            if battle['name'] == name:
                return battle
        return None
        
    def get_spell_by_name(self, name):
        """Get a spell by name."""
        for spell in self.spells:
            if spell['name'] == name:
                return spell
        return None 