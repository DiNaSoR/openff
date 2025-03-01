"""
Battle data handling module.
"""

import re
from core.game_data import GameData
from core.default_game_data import DEFAULT_BATTLES

class GameDataBattles(GameData):
    """Handler for battle data in the game."""
    
    def __init__(self):
        """Initialize battle data handler."""
        super().__init__()
        self.battles = []
        self.using_default_battles = False
        
    def extract_battles(self):
        """Extract battle data from the JavaScript content."""
        print("Extracting battles...")
        
        # Look for battle data in the JavaScript content
        patterns = [
            # Look for battle array initialization
            r'this\.gl\.battle\s*=\s*\[(.*?)\]',
            r'this\.gl\.battles\s*=\s*\[(.*?)\]',
            # Look for battle object
            r'battle\s*:\s*\{(.*?)\}'
        ]
        
        all_battles = []
        
        for pattern in patterns:
            matches = re.findall(pattern, self.js_content, re.DOTALL)
            for match in matches:
                # Process each battle entry
                if '{' in match:  # If it's an object with multiple battles
                    battle_entries = re.findall(r'([a-zA-Z0-9_]+)\s*:\s*\{(.*?)\}', match, re.DOTALL)
                    
                    for battle_id, battle_content in battle_entries:
                        battle = self._parse_battle_properties(battle_id, battle_content)
                        if battle:
                            all_battles.append(battle)
                else:  # If it's an array of battle objects
                    battle_matches = re.findall(r'\{(.*?)\}', match, re.DOTALL)
                    for i, battle_str in enumerate(battle_matches):
                        battle = self._parse_battle_properties(f"battle{i}", battle_str)
                        if battle:
                            all_battles.append(battle)
        
        # If we found battles, save them
        if all_battles:
            self.battles = all_battles
            self.using_default_battles = False
            print(f"Successfully extracted {len(self.battles)} battles")
            return
            
        # If we couldn't extract battles, use defaults
        print("Using default battle data")
        self.battles = DEFAULT_BATTLES.copy()
        self.using_default_battles = True
        
    def _parse_battle_properties(self, battle_id, battle_content):
        """Parse battle properties from a string representation."""
        try:
            battle = {
                'id': battle_id
            }
            
            # Extract name if available
            name_match = re.search(r'name\s*:\s*["\']([^"\']*)["\']', battle_content)
            if name_match:
                battle['name'] = name_match.group(1)
            else:
                # Use ID as name if not specified
                battle['name'] = battle_id.replace('_', ' ').title()
                
            # Extract enemies
            enemies_match = re.search(r'enemies\s*:\s*\[(.*?)\]', battle_content, re.DOTALL)
            if enemies_match:
                enemies_str = enemies_match.group(1)
                # Extract enemy names
                enemy_names = re.findall(r'["\']([^"\']*)["\']', enemies_str)
                
                if enemy_names:
                    battle['enemies'] = enemy_names
                else:
                    # Try to extract enemy IDs if names aren't available
                    enemy_ids = re.findall(r'\b(\d+)\b', enemies_str)
                    if enemy_ids:
                        battle['enemies'] = [f"Enemy{id}" for id in enemy_ids]
                    else:
                        battle['enemies'] = ["Unknown Enemy"]
            else:
                # Default enemies based on battle name
                if 'boss' in battle['name'].lower():
                    battle['enemies'] = ["Boss Monster"]
                else:
                    battle['enemies'] = ["Goblin", "Wolf"]  # Default random encounter
                    
            # Extract background if available
            bg_match = re.search(r'background\s*:\s*["\']?([^"\',:]+)["\']?', battle_content)
            if bg_match:
                battle['background'] = bg_match.group(1)
            else:
                # Default background based on battle name
                if 'cave' in battle['name'].lower() or 'dungeon' in battle['name'].lower():
                    battle['background'] = 'dungeon'
                elif 'castle' in battle['name'].lower():
                    battle['background'] = 'castle'
                elif 'forest' in battle['name'].lower():
                    battle['background'] = 'forest'
                else:
                    battle['background'] = 'field'  # Default
                    
            # Extract special battle flags if available
            if 'boss' in battle_content.lower():
                battle['is_boss'] = True
            if 'noEscape' in battle_content.lower() or 'no_escape' in battle_content.lower():
                battle['can_escape'] = False
            else:
                battle['can_escape'] = True
                
            return battle
        except Exception as e:
            print(f"Error parsing battle data: {str(e)}")
            return None
            
    def get_battle_by_name(self, name):
        """Get a battle by name."""
        for battle in self.battles:
            if battle.get('name') == name:
                return battle
        return None 