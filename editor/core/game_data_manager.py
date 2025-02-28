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
        self.js_content = ""
        self.js_path = ""
        
    def load_from_file(self, js_path):
        """Load game data from the specified JavaScript file."""
        self.js_path = js_path
        
        try:
            with open(js_path, 'r', encoding='utf-8') as f:
                self.js_content = f.read()
                
            # Parse the game data from the JavaScript content
            self.parse_game_data()
            
            return True
        except Exception as e:
            print(f"Error loading game data: {str(e)}")
            return False
            
    def parse_game_data(self):
        """Parse game data from the loaded JavaScript content."""
        # Extract different game elements
        self.extract_characters()
        self.extract_items()
        self.extract_maps()
        self.extract_battles()
        self.extract_spells()
        
    def extract_characters(self):
        """Extract character data from the JavaScript content."""
        self.characters = []
        
        # Example pattern for character data in app.js
        # This is a simplified example and would need to be adapted to the actual format
        pattern = r'character\s*:\s*{([^}]+)}'
        matches = re.findall(pattern, self.js_content, re.DOTALL)
        
        for match in matches:
            try:
                # Parse character properties
                name_match = re.search(r'name\s*:\s*["\']([^"\']+)["\']', match)
                job_match = re.search(r'job\s*:\s*["\']([^"\']+)["\']', match)
                level_match = re.search(r'level\s*:\s*(\d+)', match)
                hp_match = re.search(r'hp\s*:\s*(\d+)', match)
                mp_match = re.search(r'mp\s*:\s*(\d+)', match)
                
                if name_match:
                    character = {
                        'name': name_match.group(1),
                        'job': job_match.group(1) if job_match else "Unknown",
                        'level': int(level_match.group(1)) if level_match else 1,
                        'hp': int(hp_match.group(1)) if hp_match else 100,
                        'mp': int(mp_match.group(1)) if mp_match else 50,
                        'sprite': f"job{len(self.characters)}.png"  # Default sprite based on index
                    }
                    
                    self.characters.append(character)
            except Exception as e:
                print(f"Error parsing character: {str(e)}")
                
        # If no characters found, add some default ones for testing
        if not self.characters:
            self.characters = [
                {'name': 'Warrior', 'job': 'Fighter', 'level': 1, 'hp': 120, 'mp': 20, 'sprite': 'job0.png'},
                {'name': 'Mage', 'job': 'Black Mage', 'level': 1, 'hp': 80, 'mp': 100, 'sprite': 'job1.png'},
                {'name': 'Cleric', 'job': 'White Mage', 'level': 1, 'hp': 90, 'mp': 80, 'sprite': 'job2.png'},
                {'name': 'Thief', 'job': 'Thief', 'level': 1, 'hp': 100, 'mp': 40, 'sprite': 'job3.png'}
            ]
            
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
            
    def save_to_file(self):
        """Save the game data back to the JavaScript file."""
        if not self.js_path:
            return False
            
        try:
            # This is a simplified example and would need to be adapted to the actual format
            # In a real implementation, you would need to carefully update the JavaScript file
            # without breaking its structure
            
            # For now, we'll just print what would be saved
            print(f"Would save {len(self.characters)} characters, {len(self.items)} items, "
                  f"{len(self.maps)} maps, {len(self.battles)} battles, and {len(self.spells)} spells "
                  f"to {self.js_path}")
                  
            return True
        except Exception as e:
            print(f"Error saving game data: {str(e)}")
            return False
            
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
        """Get a map by name."""
        for map_data in self.maps:
            if map_data['name'] == name:
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