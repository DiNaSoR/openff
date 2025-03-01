"""
Character data handling module.
"""

import re
from core.game_data import GameData
from core.default_game_data import DEFAULT_CHARACTERS, JOB_SPRITE_MAP

class GameDataCharacters(GameData):
    """Handler for character data in the game."""
    
    def __init__(self, debug=False):
        """Initialize character data handler."""
        super().__init__()
        self.characters = []
        self.using_default_characters = False
        self.job_sprite_map = JOB_SPRITE_MAP.copy()
        self.debug = debug
        
    def _log(self, message):
        """Log a debug message if debugging is enabled."""
        if self.debug:
            print(message)
            
    def extract_characters(self):
        """Extract character data from the JavaScript content."""
        # First try the direct extraction approach
        if self._try_extract_characters_direct():
            return
            
        # If that fails, try other approaches or use defaults
        self._log("Direct extraction failed, trying alternative methods...")
        
        # Try some other patterns or approaches here...
        
        # If all extraction methods fail, use default data
        if not self.characters:
            self._log("Using default character data")
            self.characters = DEFAULT_CHARACTERS.copy()
            self.using_default_characters = True
    
    def _try_extract_characters_direct(self):
        """Try a more direct approach to extract character data."""
        try:
            self._log("Attempting direct character extraction method...")
            
            # NEW APPROACH: Look for the specific pattern where characters are created in app.js
            # The exact pattern we found in app.js is:
            # for (var t = ["a", "b", "c", "d"], i = 0; i < 4; i++) this.gl.charaSt.push(new a({
            #     id: t[i],
            #     job: i
            # }));
            
            # Look for the exact character creation pattern
            char_creation_pattern = r'for\s*\(\s*var\s+([a-zA-Z]+)\s*=\s*\[(.*?)\],\s*([a-zA-Z]+)\s*=\s*0;\s*\3\s*<\s*(\d+);\s*\3\+\+\)\s*this\.gl\.charaSt\.push\(new\s+([a-zA-Z]+)\(\{[^}]*?id:\s*\1\[\3\],\s*job:\s*\3[^}]*?\}\)\)'
            
            creation_match = re.search(char_creation_pattern, self.js_content, re.DOTALL)
            
            if creation_match:
                self._log("Found exact character creation pattern!")
                id_var = creation_match.group(1)  # 't' in the example
                ids_str = creation_match.group(2)  # '"a", "b", "c", "d"'
                counter_var = creation_match.group(3)  # 'i' in the example
                count = int(creation_match.group(4))  # '4' in the example
                class_name = creation_match.group(5)  # 'a' in the example
                
                # Extract character IDs
                char_ids = re.findall(r'"([^"]+)"', ids_str)
                if not char_ids:
                    char_ids = re.findall(r'\'([^\']+)\'', ids_str)
                
                self._log(f"Found character creation with {count} characters, IDs: {char_ids}")
                
                # Create default names based on FF tradition
                char_names = ["Warrior", "Thief", "Black Mage", "White Mage"]
                job_names = ["Fighter", "Thief", "Black Mage", "White Mage", "Red Mage", "Monk"]
                
                # Create characters from the pattern
                self.characters = []
                for i in range(count):
                    job_id = i % len(job_names)
                    char_id = char_ids[i] if i < len(char_ids) else f"char{i}"
                    char_name = char_names[i] if i < len(char_names) else f"Character {i+1}"
                    
                    character = {
                        'id': char_id,
                        'name': char_name,
                        'job': job_id,
                        'job_name': job_names[job_id % len(job_names)],
                        'level': 1,
                        'hp': 100 + (job_id * 10),
                        'mp': [9, 9, 9, 9, 9, 9, 9, 9] if job_id in [2, 3, 4] else [0, 0, 0, 0, 0, 0, 0, 0],
                        'stats': {
                            'pw': 10 + (job_id % 3),
                            'sp': 10 + ((job_id + 1) % 3),
                            'it': 10 + ((job_id + 2) % 3),
                            'st': 10 + (job_id % 3),
                            'lk': 10 + (job_id % 2),
                            'wp': 5 + (job_id % 4),
                            'dx': 5 + ((job_id + 1) % 4),
                            'am': 5 + ((job_id + 2) % 4),
                            'ev': 5 + (job_id % 3)
                        },
                        'mhp': 100 + (job_id * 10),
                        'mmp': [9, 9, 9, 9, 9, 9, 9, 9] if job_id in [2, 3, 4] else [0, 0, 0, 0, 0, 0, 0, 0],
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
                        'sprite': f"job{job_id}"
                    }
                    self.characters.append(character)
                    self._log(f"Created character: {character['name']}, Job: {character['job_name']}")
                
                self._log(f"Successfully extracted {len(self.characters)} characters with direct pattern match")
                self.using_default_characters = False
                return True
                
            # If the exact pattern doesn't match, try a more flexible approach
            # Look for a more general pattern
            general_pattern = r'this\.gl\.charaSt\.push\(new\s+[a-zA-Z]+\(\{\s*id:\s*[^,]+,\s*job:\s*(\d+)'
            job_matches = re.findall(general_pattern, self.js_content)
            
            if job_matches:
                self._log(f"Found {len(job_matches)} character creation statements with job IDs")
                
                # Create default names based on FF tradition
                char_names = ["Warrior", "Thief", "Black Mage", "White Mage"]
                job_names = ["Fighter", "Thief", "Black Mage", "White Mage", "Red Mage", "Monk"]
                
                # Create characters from the job IDs we found
                self.characters = []
                for i, job_str in enumerate(job_matches):
                    job_id = int(job_str) if job_str.isdigit() else i
                    
                    char_name = char_names[i] if i < len(char_names) else f"Character {i+1}"
                    
                    character = {
                        'id': f"char{i}",
                        'name': char_name,
                        'job': job_id,
                        'job_name': job_names[job_id % len(job_names)],
                        'level': 1,
                        'hp': 100 + (job_id * 10),
                        'mp': [9, 9, 9, 9, 9, 9, 9, 9] if job_id in [2, 3, 4] else [0, 0, 0, 0, 0, 0, 0, 0],
                        'stats': {
                            'pw': 10 + (job_id % 3),
                            'sp': 10 + ((job_id + 1) % 3),
                            'it': 10 + ((job_id + 2) % 3),
                            'st': 10 + (job_id % 3),
                            'lk': 10 + (job_id % 2),
                            'wp': 5 + (job_id % 4),
                            'dx': 5 + ((job_id + 1) % 4),
                            'am': 5 + ((job_id + 2) % 4),
                            'ev': 5 + (job_id % 3)
                        },
                        'mhp': 100 + (job_id * 10),
                        'mmp': [9, 9, 9, 9, 9, 9, 9, 9] if job_id in [2, 3, 4] else [0, 0, 0, 0, 0, 0, 0, 0],
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
                        'sprite': f"job{job_id}"
                    }
                    self.characters.append(character)
                
                self._log(f"Successfully extracted {len(self.characters)} characters with flexible pattern match")
                self.using_default_characters = False
                return True
                
            return False
        except Exception as e:
            self._log(f"Error in direct character extraction: {str(e)}")
            return False
    
    def get_character_by_name(self, name):
        """Get a character by name."""
        for character in self.characters:
            if character.get('name') == name:
                return character
        return None
