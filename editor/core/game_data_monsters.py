"""
Monster data handling module.
"""

import re
from core.game_data import GameData
from core.default_game_data import DEFAULT_MONSTERS

class GameDataMonsters(GameData):
    """Handler for monster data in the game."""
    
    def __init__(self):
        """Initialize monster data handler."""
        super().__init__()
        self.monsters = []
        self.using_default_monsters = False
        
    def extract_monsters(self):
        """Extract monster data from the JavaScript content."""
        print("Extracting monsters...")
        
        # Look for monster data in the JavaScript content
        patterns = [
            # Look for monster array initialization
            r'this\.gl\.monster\s*=\s*\[(.*?)\]',
            r'this\.gl\.monsters\s*=\s*\[(.*?)\]',
            # Look for monster object
            r'monster\s*:\s*\{(.*?)\}',
            r'monsters\s*:\s*\{(.*?)\}'
        ]
        
        all_monsters = []
        
        for pattern in patterns:
            matches = re.findall(pattern, self.js_content, re.DOTALL)
            for match in matches:
                # Process each monster entry
                if '{' in match:  # If it's an object with multiple monsters
                    monster_entries = re.findall(r'([a-zA-Z0-9_]+)\s*:\s*\{(.*?)\}', match, re.DOTALL)
                    
                    for monster_id, monster_content in monster_entries:
                        monster = self._parse_monster_properties(monster_id, monster_content)
                        if monster:
                            all_monsters.append(monster)
                else:  # If it's an array of monster objects
                    monster_matches = re.findall(r'\{(.*?)\}', match, re.DOTALL)
                    for i, monster_str in enumerate(monster_matches):
                        monster = self._parse_monster_properties(f"monster{i}", monster_str)
                        if monster:
                            all_monsters.append(monster)
        
        # If we found monsters, save them
        if all_monsters:
            self.monsters = all_monsters
            self.using_default_monsters = False
            print(f"Successfully extracted {len(self.monsters)} monsters")
            return
            
        # If we couldn't extract monsters, use defaults
        print("Using default monster data")
        self.monsters = DEFAULT_MONSTERS.copy()
        self.using_default_monsters = True
        
    def _parse_monster_properties(self, monster_id, monster_content):
        """Parse monster properties from a string representation."""
        try:
            monster = {
                'id': monster_id
            }
            
            # Extract name if available
            name_match = re.search(r'name\s*:\s*["\']([^"\']*)["\']', monster_content)
            if name_match:
                monster['name'] = name_match.group(1)
            else:
                # Use ID as name if not specified
                monster['name'] = monster_id.replace('_', ' ').title()
                
            # Extract HP
            hp_match = re.search(r'hp\s*:\s*(\d+)', monster_content)
            if hp_match:
                monster['hp'] = int(hp_match.group(1))
            else:
                # Default HP based on monster name
                if 'boss' in monster['name'].lower():
                    monster['hp'] = 200  # Boss monsters have high HP
                elif 'dragon' in monster['name'].lower():
                    monster['hp'] = 150  # Dragons are tough
                else:
                    monster['hp'] = 50  # Default monster HP
                    
            # Extract attack power
            attack_match = re.search(r'attack\s*:\s*(\d+)', monster_content)
            if attack_match:
                monster['attack'] = int(attack_match.group(1))
            else:
                # Default attack based on HP
                monster['attack'] = max(5, monster['hp'] // 10)
                
            # Extract defense
            defense_match = re.search(r'defense\s*:\s*(\d+)', monster_content)
            if defense_match:
                monster['defense'] = int(defense_match.group(1))
            else:
                # Default defense based on HP
                monster['defense'] = max(2, monster['hp'] // 20)
                
            # Extract XP reward
            xp_match = re.search(r'exp\s*:\s*(\d+)', monster_content)
            if xp_match:
                monster['exp'] = int(xp_match.group(1))
            else:
                # Default XP based on HP
                monster['exp'] = monster['hp']
                
            # Extract gold reward
            gold_match = re.search(r'gold\s*:\s*(\d+)', monster_content)
            if gold_match:
                monster['gold'] = int(gold_match.group(1))
            else:
                # Default gold based on HP
                monster['gold'] = monster['hp'] // 2
                
            # Extract sprite/image if available
            sprite_match = re.search(r'sprite\s*:\s*["\']?([^"\',:]+)["\']?', monster_content)
            if sprite_match:
                monster['sprite'] = sprite_match.group(1)
            else:
                # Default sprite
                monster['sprite'] = f"monster{monster_id.replace('monster', '')}.png"
                
            # Extract weaknesses and resistances if available
            weaknesses_match = re.search(r'weakness\s*:\s*\[(.*?)\]', monster_content)
            if weaknesses_match:
                weaknesses_str = weaknesses_match.group(1)
                monster['weaknesses'] = re.findall(r'["\']([^"\']*)["\']', weaknesses_str)
            else:
                monster['weaknesses'] = []
                
            resistances_match = re.search(r'resist\s*:\s*\[(.*?)\]', monster_content)
            if resistances_match:
                resistances_str = resistances_match.group(1)
                monster['resistances'] = re.findall(r'["\']([^"\']*)["\']', resistances_str)
            else:
                monster['resistances'] = []
                
            return monster
        except Exception as e:
            print(f"Error parsing monster data: {str(e)}")
            return None
            
    def get_monster_by_name(self, name):
        """Get a monster by name."""
        for monster in self.monsters:
            if monster.get('name') == name:
                return monster
        return None 