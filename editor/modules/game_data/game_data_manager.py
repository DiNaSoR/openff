import os
import json
import re

class GameDataManager:
    """Manager for game data extraction and saving."""
    
    def __init__(self):
        # Game data
        self.characters = []
        self.items = []
        self.maps = []
        self.battles = []
        self.spells = []
        
        # File paths
        self.app_js_path = self._find_app_js()
        self.data_path = os.path.join(os.path.dirname(self.app_js_path), 'game_data.json') if self.app_js_path else None
        
    def _find_app_js(self):
        """Find the app.js file in the project."""
        # Start from the current directory
        current_dir = os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))
        
        # Look for app.js
        for root, dirs, files in os.walk(current_dir):
            if 'app.js' in files:
                return os.path.join(root, 'app.js')
                
        # Not found
        return None
        
    def load_from_file(self):
        """Load game data from file."""
        # Check if we have a data file
        if self.data_path and os.path.exists(self.data_path):
            try:
                # Load from the data file
                with open(self.data_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                # Set the data
                self.characters = data.get('characters', [])
                self.items = data.get('items', [])
                self.maps = data.get('maps', [])
                self.battles = data.get('battles', [])
                self.spells = data.get('spells', [])
                
                return True
            except Exception as e:
                print(f"Error loading game data: {str(e)}")
                
        # No data file or error loading, extract from app.js
        return self.extract_from_app_js()
        
    def save_to_file(self):
        """Save game data to file."""
        # Check if we have a data path
        if not self.data_path:
            return False
            
        try:
            # Create the data
            data = {
                'characters': self.characters,
                'items': self.items,
                'maps': self.maps,
                'battles': self.battles,
                'spells': self.spells
            }
            
            # Save to the data file
            with open(self.data_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
                
            # Update app.js
            self.update_app_js()
                
            return True
        except Exception as e:
            print(f"Error saving game data: {str(e)}")
            return False
            
    def extract_from_app_js(self):
        """Extract game data from app.js."""
        # Check if we have an app.js path
        if not self.app_js_path or not os.path.exists(self.app_js_path):
            return False
            
        try:
            # Read the file
            with open(self.app_js_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Extract characters
            self.characters = self.extract_characters(content)
            
            # Extract items
            self.items = self.extract_items(content)
            
            # Extract maps
            self.maps = self.extract_maps(content)
            
            # Extract battles
            self.battles = self.extract_battles(content)
            
            # Extract spells
            self.spells = self.extract_spells(content)
            
            return True
        except Exception as e:
            print(f"Error extracting game data: {str(e)}")
            return False
            
    def update_app_js(self):
        """Update app.js with the game data."""
        # Check if we have an app.js path
        if not self.app_js_path or not os.path.exists(self.app_js_path):
            return False
            
        try:
            # Read the file
            with open(self.app_js_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Update characters
            content = self.update_characters(content)
            
            # Update items
            content = self.update_items(content)
            
            # Update maps
            content = self.update_maps(content)
            
            # Update battles
            content = self.update_battles(content)
            
            # Update spells
            content = self.update_spells(content)
            
            # Write the file
            with open(self.app_js_path, 'w', encoding='utf-8') as f:
                f.write(content)
                
            return True
        except Exception as e:
            print(f"Error updating app.js: {str(e)}")
            return False
            
    def extract_characters(self, content):
        """Extract characters from app.js content."""
        # For now, return sample data
        return [
            {
                'name': 'Warrior',
                'hp': 100,
                'mp': 0,
                'strength': 10,
                'agility': 5,
                'intelligence': 1,
                'image': 'warrior.png'
            },
            {
                'name': 'Mage',
                'hp': 50,
                'mp': 100,
                'strength': 1,
                'agility': 5,
                'intelligence': 10,
                'image': 'mage.png'
            },
            {
                'name': 'Thief',
                'hp': 70,
                'mp': 30,
                'strength': 5,
                'agility': 10,
                'intelligence': 5,
                'image': 'thief.png'
            },
            {
                'name': 'Cleric',
                'hp': 80,
                'mp': 80,
                'strength': 3,
                'agility': 3,
                'intelligence': 8,
                'image': 'cleric.png'
            }
        ]
        
    def update_characters(self, content):
        """Update characters in app.js content."""
        # For now, just return the content unchanged
        return content
        
    def extract_items(self, content):
        """Extract items from app.js content."""
        # For now, return sample data
        return [
            {
                'name': 'Potion',
                'type': 'Consumable',
                'power': 50,
                'description': 'Restores 50 HP',
                'image': 'potion.png'
            },
            {
                'name': 'Sword',
                'type': 'Weapon',
                'power': 10,
                'description': 'A basic sword',
                'image': 'sword.png'
            },
            {
                'name': 'Shield',
                'type': 'Armor',
                'power': 5,
                'description': 'A basic shield',
                'image': 'shield.png'
            },
            {
                'name': 'Ether',
                'type': 'Consumable',
                'power': 30,
                'description': 'Restores 30 MP',
                'image': 'ether.png'
            }
        ]
        
    def update_items(self, content):
        """Update items in app.js content."""
        # For now, just return the content unchanged
        return content
        
    def extract_maps(self, content):
        """Extract maps from app.js content."""
        # For now, return sample data
        return [
            {
                'name': 'Overworld',
                'width': 20,
                'height': 15,
                'tileset': 'overworld',
                'tiles': [[0 for _ in range(20)] for _ in range(15)]
            },
            {
                'name': 'Castle',
                'width': 10,
                'height': 10,
                'tileset': 'castle',
                'tiles': [[1 for _ in range(10)] for _ in range(10)]
            },
            {
                'name': 'Cave',
                'width': 15,
                'height': 10,
                'tileset': 'cave',
                'tiles': [[2 for _ in range(15)] for _ in range(10)]
            }
        ]
        
    def update_maps(self, content):
        """Update maps in app.js content."""
        # For now, just return the content unchanged
        return content
        
    def extract_battles(self, content):
        """Extract battles from app.js content."""
        # For now, return sample data
        return [
            {
                'name': 'Goblin Encounter',
                'enemies': ['Goblin', 'Goblin', 'Goblin']
            },
            {
                'name': 'Wolf Pack',
                'enemies': ['Wolf', 'Wolf', 'Wolf', 'Wolf']
            },
            {
                'name': 'Guard Patrol',
                'enemies': ['Guard', 'Guard', 'Captain']
            },
            {
                'name': 'Undead Horde',
                'enemies': ['Skeleton', 'Zombie', 'Ghost']
            },
            {
                'name': 'Boss: Garland',
                'enemies': ['Garland']
            }
        ]
        
    def update_battles(self, content):
        """Update battles in app.js content."""
        # For now, just return the content unchanged
        return content
        
    def extract_spells(self, content):
        """Extract spells from app.js content."""
        # For now, return sample data
        return [
            {
                'name': 'Fire',
                'type': 'Fire',
                'power': 20,
                'mp_cost': 5,
                'target': 'Single Enemy'
            },
            {
                'name': 'Blizzard',
                'type': 'Ice',
                'power': 20,
                'mp_cost': 5,
                'target': 'Single Enemy'
            },
            {
                'name': 'Thunder',
                'type': 'Lightning',
                'power': 20,
                'mp_cost': 5,
                'target': 'Single Enemy'
            },
            {
                'name': 'Cure',
                'type': 'Cure',
                'power': 20,
                'mp_cost': 5,
                'target': 'Single Ally'
            },
            {
                'name': 'Haste',
                'type': 'Buff',
                'power': 10,
                'mp_cost': 10,
                'target': 'Single Ally'
            }
        ]
        
    def update_spells(self, content):
        """Update spells in app.js content."""
        # For now, just return the content unchanged
        return content
        
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