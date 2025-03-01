"""
Monster data handling module.
"""

import re
from core.game_data import GameData
from core.default_game_data import DEFAULT_MONSTERS

# Mapping of monster IDs to their sprite positions
SPRITE_POSITION_MAP = {
    # Map Japanese monster names/IDs to sprite positions
    "goblin": {"sheet": "monsters1", "row": 0, "col": 0},  # ゴブリン
    "wolf": {"sheet": "monsters1", "row": 0, "col": 1},    # ウルフ
    "skeleton": {"sheet": "monsters1", "row": 0, "col": 2}, # スケルトン
    "zombie": {"sheet": "monsters1", "row": 0, "col": 3},  # ゾンビ
    "orc": {"sheet": "monsters1", "row": 0, "col": 4},     # オーク
    "slime": {"sheet": "monsters1", "row": 1, "col": 0},   # スライム
    "bat": {"sheet": "monsters1", "row": 1, "col": 1},     # コウモリ
    "snake": {"sheet": "monsters1", "row": 1, "col": 2},   # ヘビ
    "scorpion": {"sheet": "monsters1", "row": 1, "col": 3}, # サソリ
    "spider": {"sheet": "monsters1", "row": 1, "col": 4},  # クモ
    "ghost": {"sheet": "monsters1", "row": 2, "col": 0},   # ゴースト
    "witch": {"sheet": "monsters1", "row": 2, "col": 1},   # ウィッチ
    "harpy": {"sheet": "monsters1", "row": 2, "col": 2},   # ハーピー
    "lizardman": {"sheet": "monsters1", "row": 2, "col": 3}, # リザードマン
    "golem": {"sheet": "monsters1", "row": 2, "col": 4},   # ゴーレム
    "dragon": {"sheet": "monsters1", "row": 3, "col": 0},  # ドラゴン
    
    # Additional mappings by possible IDs found in module 56
    "g1": {"sheet": "monsters1", "row": 0, "col": 0},      # Goblin
    "g2": {"sheet": "monsters1", "row": 0, "col": 1},      # Wolf
    "g3": {"sheet": "monsters1", "row": 0, "col": 2},      # Skeleton
    "g4": {"sheet": "monsters1", "row": 0, "col": 3},      # Zombie
    "g5": {"sheet": "monsters1", "row": 0, "col": 4},      # Orc
    "g6": {"sheet": "monsters1", "row": 1, "col": 0},      # Slime
    "g7": {"sheet": "monsters1", "row": 1, "col": 1},      # Bat
    "g8": {"sheet": "monsters1", "row": 1, "col": 2},      # Snake
    "g9": {"sheet": "monsters1", "row": 1, "col": 3},      # Scorpion
    "g10": {"sheet": "monsters1", "row": 1, "col": 4},     # Spider
    "g11": {"sheet": "monsters1", "row": 2, "col": 0},     # Ghost
    "g12": {"sheet": "monsters1", "row": 2, "col": 1},     # Witch
    "g13": {"sheet": "monsters1", "row": 2, "col": 2},     # Harpy
    "g14": {"sheet": "monsters1", "row": 2, "col": 3},     # Lizardman
    "g15": {"sheet": "monsters1", "row": 2, "col": 4},     # Golem
    "g16": {"sheet": "monsters1", "row": 3, "col": 0},     # Dragon
    
    # Numeric ID mappings
    "01": {"sheet": "monsters1", "row": 0, "col": 0},
    "02": {"sheet": "monsters1", "row": 0, "col": 1},
    "03": {"sheet": "monsters1", "row": 0, "col": 2},
    "04": {"sheet": "monsters1", "row": 0, "col": 3},
    "05": {"sheet": "monsters1", "row": 0, "col": 4},
    "06": {"sheet": "monsters1", "row": 1, "col": 0},
    "07": {"sheet": "monsters1", "row": 1, "col": 1},
    "08": {"sheet": "monsters1", "row": 1, "col": 2},
    "09": {"sheet": "monsters1", "row": 1, "col": 3},
    "10": {"sheet": "monsters1", "row": 1, "col": 4},
    "11": {"sheet": "monsters1", "row": 2, "col": 0},
    "12": {"sheet": "monsters1", "row": 2, "col": 1},
    "13": {"sheet": "monsters1", "row": 2, "col": 2},
    "14": {"sheet": "monsters1", "row": 2, "col": 3},
    "15": {"sheet": "monsters1", "row": 2, "col": 4},
    "16": {"sheet": "monsters1", "row": 3, "col": 0},
    
    # Japanese name mappings
    "ゴブリン": {"sheet": "monsters1", "row": 0, "col": 0},
    "ウルフ": {"sheet": "monsters1", "row": 0, "col": 1},
    "スケルトン": {"sheet": "monsters1", "row": 0, "col": 2},
    "ゾンビ": {"sheet": "monsters1", "row": 0, "col": 3},
    "オーク": {"sheet": "monsters1", "row": 0, "col": 4},
    "スライム": {"sheet": "monsters1", "row": 1, "col": 0},
    "コウモリ": {"sheet": "monsters1", "row": 1, "col": 1},
    "ヘビ": {"sheet": "monsters1", "row": 1, "col": 2},
    "サソリ": {"sheet": "monsters1", "row": 1, "col": 3},
    "クモ": {"sheet": "monsters1", "row": 1, "col": 4},
    "ゴースト": {"sheet": "monsters1", "row": 2, "col": 0},
    "ウィッチ": {"sheet": "monsters1", "row": 2, "col": 1},
    "ハーピー": {"sheet": "monsters1", "row": 2, "col": 2},
    "リザードマン": {"sheet": "monsters1", "row": 2, "col": 3},
    "ゴーレム": {"sheet": "monsters1", "row": 2, "col": 4},
    "ドラゴン": {"sheet": "monsters1", "row": 3, "col": 0},
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
                        monster = self._parse_monster_properties(monster_id, monster_content)
                        if monster:
                            all_monsters.append(monster)
                else:  # If it's an array of monster objects
                    monster_matches = re.findall(r'\{(.*?)\}', match, re.DOTALL)
                    print(f"Found {len(monster_matches)} monster entries in array format")
                    for i, monster_str in enumerate(monster_matches):
                        monster = self._parse_monster_properties(f"monster{i}", monster_str)
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
        monster_key = monster_id.lower()
        if monster_key in SPRITE_POSITION_MAP:
            monster['sprite'] = SPRITE_POSITION_MAP[monster_key]
        else:
            # Try to match by name if ID matching fails
            monster_name = monster.get('name', '').lower()
            for key, sprite_data in SPRITE_POSITION_MAP.items():
                if monster_name in key or key in monster_name:
                    monster['sprite'] = sprite_data
                    break
            
            # If still no match, set default sprite position
            if 'sprite' not in monster:
                monster['sprite'] = {"sheet": "monsters1", "row": 0, "col": 0}
        
        return monster
            
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