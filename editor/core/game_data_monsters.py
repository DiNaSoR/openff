"""
Monster data handling module.
"""

import re
from core.game_data import GameData
from core.default_game_data import DEFAULT_MONSTERS

# Mapping of monster IDs to their sprite positions
SPRITE_POSITION_MAP = {
    # Monster IDs from the hint list provided by user
    "ms_00": {"sheet": "monsters1", "row": 0, "col": 0},  # ゴブリン (Goblin)
    "ms_01": {"sheet": "monsters1", "row": 0, "col": 1},  # ゴブリンガード (Goblin Guard)
    "ms_02": {"sheet": "monsters1", "row": 0, "col": 2},  # ウルフ (Wolf)
    "ms_74": {"sheet": "monsters1", "row": 3, "col": 2},  # クレイジーホース (Crazy Horse)
    "ms_15": {"sheet": "monsters1", "row": 1, "col": 2},  # スケルトン (Skeleton)
    "ms_49": {"sheet": "monsters1", "row": 2, "col": 1},  # ブラックウィドウ (Black Widow)
    "ms_17": {"sheet": "monsters1", "row": 1, "col": 3},  # ギガースウォーム (Gigaworm)
    "ms_03": {"sheet": "monsters1", "row": 0, "col": 3},  # ウォーグウルフ (Worg)
    "ms_04": {"sheet": "monsters1", "row": 0, "col": 4},  # ウェアウルフ (Werewolf)
    "ms_2b": {"sheet": "monsters1", "row": 1, "col": 0},  # ゾンビ (Zombie)
    "ms_2c": {"sheet": "monsters1", "row": 1, "col": 1},  # グール (Ghoul)
    "ms_69": {"sheet": "monsters1", "row": 3, "col": 0},  # ガーランド (Garland)
    
    # Map by monster name (English)
    "goblin": {"sheet": "monsters1", "row": 0, "col": 0},
    "goblin_guard": {"sheet": "monsters1", "row": 0, "col": 1},
    "wolf": {"sheet": "monsters1", "row": 0, "col": 2},
    "worg": {"sheet": "monsters1", "row": 0, "col": 3},
    "werewolf": {"sheet": "monsters1", "row": 0, "col": 4},
    "zombie": {"sheet": "monsters1", "row": 1, "col": 0},
    "ghoul": {"sheet": "monsters1", "row": 1, "col": 1},
    "skeleton": {"sheet": "monsters1", "row": 1, "col": 2},
    "gigaworm": {"sheet": "monsters1", "row": 1, "col": 3},
    "spider": {"sheet": "monsters1", "row": 1, "col": 4},
    "ghost": {"sheet": "monsters1", "row": 2, "col": 0},
    "black_widow": {"sheet": "monsters1", "row": 2, "col": 1},
    "harpy": {"sheet": "monsters1", "row": 2, "col": 2},
    "lizardman": {"sheet": "monsters1", "row": 2, "col": 3},
    "golem": {"sheet": "monsters1", "row": 2, "col": 4},
    "dragon": {"sheet": "monsters1", "row": 3, "col": 0},
    "garland": {"sheet": "monsters1", "row": 3, "col": 0},
    "crazy_horse": {"sheet": "monsters1", "row": 3, "col": 2},
    
    # Japanese name mappings
    "ゴブリン": {"sheet": "monsters1", "row": 0, "col": 0},
    "ゴブリンガード": {"sheet": "monsters1", "row": 0, "col": 1},
    "ウルフ": {"sheet": "monsters1", "row": 0, "col": 2},
    "ウォーグウルフ": {"sheet": "monsters1", "row": 0, "col": 3},
    "ウェアウルフ": {"sheet": "monsters1", "row": 0, "col": 4},
    "ゾンビ": {"sheet": "monsters1", "row": 1, "col": 0},
    "グール": {"sheet": "monsters1", "row": 1, "col": 1},
    "スケルトン": {"sheet": "monsters1", "row": 1, "col": 2},
    "ギガースウォーム": {"sheet": "monsters1", "row": 1, "col": 3},
    "クモ": {"sheet": "monsters1", "row": 1, "col": 4},
    "ゴースト": {"sheet": "monsters1", "row": 2, "col": 0},
    "ブラックウィドウ": {"sheet": "monsters1", "row": 2, "col": 1},
    "ハーピー": {"sheet": "monsters1", "row": 2, "col": 2},
    "リザードマン": {"sheet": "monsters1", "row": 2, "col": 3},
    "ゴーレム": {"sheet": "monsters1", "row": 2, "col": 4},
    "ドラゴン": {"sheet": "monsters1", "row": 3, "col": 0},
    "ガーランド": {"sheet": "monsters1", "row": 3, "col": 0},
    "クレイジーホース": {"sheet": "monsters1", "row": 3, "col": 2},
    
    # Additional fallback mappings for common numeric IDs
    "00": {"sheet": "monsters1", "row": 0, "col": 0},
    "01": {"sheet": "monsters1", "row": 0, "col": 1},
    "02": {"sheet": "monsters1", "row": 0, "col": 2},
    "03": {"sheet": "monsters1", "row": 0, "col": 3},
    "04": {"sheet": "monsters1", "row": 0, "col": 4},
    "05": {"sheet": "monsters1", "row": 1, "col": 0},
    "06": {"sheet": "monsters1", "row": 1, "col": 1},
    "07": {"sheet": "monsters1", "row": 1, "col": 2},
    "08": {"sheet": "monsters1", "row": 1, "col": 3},
    "09": {"sheet": "monsters1", "row": 1, "col": 4},
    "10": {"sheet": "monsters1", "row": 2, "col": 0},
    "0a": {"sheet": "monsters1", "row": 2, "col": 1},
    "0b": {"sheet": "monsters1", "row": 2, "col": 2},
    "0c": {"sheet": "monsters1", "row": 2, "col": 3},
    "0d": {"sheet": "monsters1", "row": 2, "col": 4},
    "0e": {"sheet": "monsters1", "row": 3, "col": 0},
}

class GameDataMonsters(GameData):
    """Handler for monster data in the game."""
    
    def __init__(self):
        """Initialize monster data handler."""
        super().__init__()
        self.monsters = []
        self.using_default_monsters = False
        self.changed = False
        
    def extract_monsters(self):
        """Extract monster data from the JavaScript content."""
        print("Extracting monsters...")
        
        # Look for the module 56 which contains monster definitions
        module_56_pattern = r'56: \[function\(.*?e\.exports\s*=\s*\{(.*?)\}\s*,\s*\{\s*\}\s*\]'
        module_match = re.search(module_56_pattern, self.js_content, re.DOTALL)
        
        if module_match:
            print("Found monster data in module 56!")
            monster_data_str = module_match.group(1)
            
            # Extract each monster entry
            monster_entries = re.findall(r'([a-zA-Z0-9_]+):\s*\{(.*?)\},', monster_data_str, re.DOTALL)
            print(f"Found {len(monster_entries)} monster entries in module 56")
            
            all_monsters = []
            for monster_id, monster_content in monster_entries:
                # Format monster ID with ms_ prefix if it doesn't already have one
                if not monster_id.startswith("ms_") and not re.match(r'^[a-zA-Z]+$', monster_id):
                    monster_id = f"ms_{monster_id}"
                
                monster = self._parse_monster_properties(monster_id, monster_content)
                if monster:
                    all_monsters.append(monster)
            
            if all_monsters:
                # Sort monsters by name for better organization
                all_monsters.sort(key=lambda m: m.get('name', ''))
                
                self.monsters = all_monsters
                self.using_default_monsters = False
                print(f"Successfully extracted {len(self.monsters)} monsters")
                print(f"Monster IDs found: {[m.get('id', 'unknown') for m in all_monsters]}")
                return
        
        # Try the patterns from before if module 56 didn't work
        patterns = [
            # Look for monster array initialization
            r'this\.gl\.monster\s*=\s*\[(.*?)\]',
            r'this\.gl\.monsters\s*=\s*\[(.*?)\]',
            # Look for monster object
            r'monster\s*:\s*\{(.*?)\}',
            r'monsters\s*:\s*\{(.*?)\}',
            # Additional patterns for other monster data formats
            r'var\s+monsters?\s*=\s*\{(.*?)\}',
            r'const\s+monsters?\s*=\s*\{(.*?)\}',
            r'let\s+monsters?\s*=\s*\{(.*?)\}'
        ]
        
        all_monsters = []
        debug_info = {"patterns_matched": [], "total_matches": 0}
        
        for pattern in patterns:
            matches = re.findall(pattern, self.js_content, re.DOTALL)
            if matches:
                debug_info["patterns_matched"].append(pattern)
                debug_info["total_matches"] += len(matches)
                
            for match in matches:
                # Process each monster entry
                if '{' in match:  # If it's an object with multiple monsters
                    monster_entries = re.findall(r'([a-zA-Z0-9_]+)\s*:\s*\{(.*?)\}', match, re.DOTALL)
                    print(f"Found {len(monster_entries)} monster entries in object format")
                    
                    for monster_id, monster_content in monster_entries:
                        # Format monster ID with ms_ prefix if it's a numeric or special ID
                        if not monster_id.startswith("ms_") and not re.match(r'^[a-zA-Z]+$', monster_id):
                            monster_id = f"ms_{monster_id}"
                        
                        monster = self._parse_monster_properties(monster_id, monster_content)
                        if monster:
                            all_monsters.append(monster)
                else:  # If it's an array of monster objects
                    monster_matches = re.findall(r'\{(.*?)\}', match, re.DOTALL)
                    print(f"Found {len(monster_matches)} monster entries in array format")
                    for i, monster_str in enumerate(monster_matches):
                        monster_id = f"ms_{i:02d}"
                        monster = self._parse_monster_properties(monster_id, monster_str)
                        if monster:
                            all_monsters.append(monster)
        
        # If we found monsters, save them
        if all_monsters:
            print(f"Extraction results: {debug_info}")
            print(f"Monster IDs found: {[m.get('id', 'unknown') for m in all_monsters]}")
            
            # Sort monsters by name for better organization in the editor
            all_monsters.sort(key=lambda m: m.get('name', ''))
            
            self.monsters = all_monsters
            self.using_default_monsters = False
            print(f"Successfully extracted {len(self.monsters)} monsters")
            return
            
        # If we couldn't extract monsters, use defaults
        print("No monsters found in JavaScript content. Using default monster data.")
        print(f"Debug info: {debug_info}")
        self.monsters = DEFAULT_MONSTERS.copy()
        self.using_default_monsters = True
        
    def _parse_monster_properties(self, monster_id, content):
        """Parse monster properties from the monster definition content."""
        monster = {"id": monster_id}
        
        # Property mapping (JS property name -> our property name)
        property_map = {
            "name": "name",
            "type": "type",
            "size": "size",
            "ep": "exp",
            "gil": "gold",
            "hp": "hp",
            "atk": "attack",
            "pw": "power",  # Add pw as power
            "def": "defense",
            "mdef": "magic_defense",
            "dx": "dexterity",
            "sp": "speed",
            "it": "intelligence",
            "ev": "evasion",
            "act": "actions",
            "add": "status_effects",
            "drop": "drops",
            "weak": "weaknesses"
        }
        
        # Extract properties using regex matches
        for js_prop, our_prop in property_map.items():
            # Try different regex patterns to catch different property formats
            patterns = [
                r'{0}\s*:\s*(?:"([^"]*)"|\s*\'([^\']*)\'|([^,\}}]+))'.format(js_prop),  # Standard property
                r'"{0}"\s*:\s*(?:"([^"]*)"|\s*\'([^\']*)\'|([^,\}}]+))'.format(js_prop),  # Quoted key
                r'\'{0}\'\s*:\s*(?:"([^"]*)"|\s*\'([^\']*)\'|([^,\}}]+))'.format(js_prop),   # Single-quoted key
            ]
            
            for pattern in patterns:
                matches = re.search(pattern, content)
                if matches:
                    # Take the first non-None group from the match
                    value = next((g for g in matches.groups() if g is not None), "")
                    value = value.strip()
                    
                    # Handle arrays
                    if value.startswith('[') and value.endswith(']'):
                        # Extract array values
                        array_values = []
                        array_matches = re.findall(r'"([^"]*)"|\s*\'([^\']*)\'|([^,\[\]]+)', value)
                        for match in array_matches:
                            array_val = next((g for g in match if g is not None), "").strip()
                            if array_val and not array_val.isspace():
                                array_values.append(array_val)
                        monster[our_prop] = array_values
                    else:
                        # Handle numeric values
                        if value.replace('.', '', 1).isdigit():
                            if '.' in value:
                                monster[our_prop] = float(value)
                            else:
                                monster[our_prop] = int(value)
                        else:
                            monster[our_prop] = value
                    break
        
        # Ensure the monster has minimum required properties
        if 'name' not in monster or not monster['name']:
            monster['name'] = f"Monster {monster_id}"
        
        # Add sprite mapping based on monster ID if available
        sprite_data = self.get_sprite_for_id(monster_id)
        if sprite_data:
            monster['sprite'] = sprite_data
        else:
            # Default sprite position
            monster['sprite'] = {"sheet": "monsters1", "row": 0, "col": 0}
        
        return monster
    
    def get_sprite_for_id(self, monster_id):
        """Get sprite data for a given monster ID."""
        # Check for direct match in the sprite position map
        if monster_id in SPRITE_POSITION_MAP:
            return SPRITE_POSITION_MAP[monster_id]
        
        # Try without ms_ prefix if it has one
        if monster_id.startswith("ms_"):
            id_without_prefix = monster_id[3:]
            if id_without_prefix in SPRITE_POSITION_MAP:
                return SPRITE_POSITION_MAP[id_without_prefix]
        
        # Try with different formats
        for key in [monster_id.lower(), monster_id.upper()]:
            if key in SPRITE_POSITION_MAP:
                return SPRITE_POSITION_MAP[key]
        
        # Try to match by name for any monster with this ID
        monster = self.get_monster_by_id(monster_id)
        if monster and 'name' in monster:
            monster_name = monster['name'].lower()
            for key, sprite_data in SPRITE_POSITION_MAP.items():
                # Check if the monster name contains part of a key or vice versa
                if isinstance(key, str) and (monster_name in key.lower() or key.lower() in monster_name):
                    return sprite_data
        
        # Default sprite position as fallback
        return {"sheet": "monsters1", "row": 0, "col": 0}
            
    def get_monster_by_name(self, name):
        """Get a monster by name."""
        for monster in self.monsters:
            if monster.get('name') == name:
                return monster
        return None
        
    def get_monster_by_id(self, monster_id):
        """Get a monster by ID."""
        for monster in self.monsters:
            if monster.get('id') == monster_id:
                return monster
        return None
        
    def mark_as_changed(self):
        """Mark the monster data as changed."""
        self.changed = True
        
    def save_to_file(self):
        """Save monster data to file."""
        # Implementation would depend on how the game is storing monster data
        # This is a placeholder
        if self.changed:
            print("Saving monster data...")
            # Save logic would go here
            self.changed = False
            return True
        return False 