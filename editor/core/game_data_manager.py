import os
import re
import json
from core.default_game_data import (
    DEFAULT_ITEMS,
    DEFAULT_CHARACTERS,
    DEFAULT_SPELLS,
    DEFAULT_MONSTERS,
    DEFAULT_MAPS,
    DEFAULT_BATTLES,
    DEFAULT_NPCS,
    JOB_SPRITE_MAP
)

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
        self.using_default_characters = False
        self.using_default_items = False
        self.using_default_spells = False
        self.using_default_maps = False
        self.using_default_battles = False
        self.using_default_monsters = False
        self.using_default_npcs = False
        self.job_sprite_map = JOB_SPRITE_MAP.copy()
        
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
        
    def _try_extract_characters_direct(self):
        """Try a more direct approach to extract character data."""
        try:
            print("Attempting direct character extraction method...")
            
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
                print("Found exact character creation pattern!")
                id_var = creation_match.group(1)  # 't' in the example
                ids_str = creation_match.group(2)  # '"a", "b", "c", "d"'
                counter_var = creation_match.group(3)  # 'i' in the example
                count = int(creation_match.group(4))  # '4' in the example
                class_name = creation_match.group(5)  # 'a' in the example
                
                # Extract character IDs
                char_ids = re.findall(r'"([^"]+)"', ids_str)
                if not char_ids:
                    char_ids = re.findall(r'\'([^\']+)\'', ids_str)
                
                print(f"Found character creation with {count} characters, IDs: {char_ids}")
                
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
                    print(f"Created character: {character['name']}, Job: {character['job_name']}")
                
                print(f"Successfully extracted {len(self.characters)} characters with direct pattern match")
                self.using_default_characters = False
                return True
                
            # If the exact pattern doesn't match, try a more flexible approach
            # Look for a more general pattern
            general_pattern = r'this\.gl\.charaSt\.push\(new\s+[a-zA-Z]+\(\{\s*id:\s*[^,]+,\s*job:\s*(\d+)'
            job_matches = re.findall(general_pattern, self.js_content)
            
            if job_matches:
                print(f"Found {len(job_matches)} character creation statements with job IDs")
                
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
                    print(f"Created character: {character['name']}, Job: {character['job_name']}")
                
                print(f"Successfully extracted {len(self.characters)} characters with general pattern match")
                self.using_default_characters = False
                return True
            
            # If the more flexible approach doesn't work, try the previous approaches
            # Pattern 1: Looking for charaSt array initialization
            char_array_pattern1 = r'this\.charaSt\s*=\s*\[(.*?)\]'
            
            # Pattern 2: Character update pattern 
            char_array_pattern2 = r'this\.state\.charaSt\s*=\s*(.*?),'
            
            # Pattern 3: Specific character definitions
            char_array_pattern3 = r'var\s+c\s*=\s*\[(.*?)\]'
            
            # Additional patterns for newer formats
            char_array_pattern4 = r'charaStatus\s*=\s*\[(.*?)\]'
            char_array_pattern5 = r'characters\s*:\s*\[(.*?)\]'
            
            # Try all patterns
            found_data = False
            for i, pattern in enumerate([char_array_pattern1, char_array_pattern2, char_array_pattern3, 
                                         char_array_pattern4, char_array_pattern5]):
                char_array_match = re.search(pattern, self.js_content, re.DOTALL)
                if char_array_match:
                    print(f"Found character data with pattern {i+1}")
                    chars_data = char_array_match.group(1)
                    print(f"Found character array data (length: {len(chars_data)} bytes)")
                    
                    # Check if the data is meaningful (not just empty array)
                    if len(chars_data.strip()) > 2:  # More than just "[]"
                        print(f"Sample of character data: {chars_data[:300]}...")
                        found_data = True
                        break
                    else:
                        print("Found empty character array []")
                
            if not found_data:
                # If no match was found with any pattern or only empty arrays
                print("Could not find non-empty character array with any pattern")
                
                # Let's try to find individual character objects directly
                char_obj_pattern = r'\{\s*name\s*:\s*["\']([^"\']+)["\']'
                char_obj_matches = re.findall(char_obj_pattern, self.js_content)
                
                if char_obj_matches:
                    print(f"Found {len(char_obj_matches)} character objects directly")
                    print(f"Character names: {char_obj_matches}")
                    
                    # Try to extract character data this way
                    job_pattern = r'name\s*:\s*["\']([^"\']+)["\'][^}]*?job\s*:\s*(\d+)'
                    job_matches = re.findall(job_pattern, self.js_content, re.DOTALL)
                    
                    if job_matches:
                        print(f"Found {len(job_matches)} character job matches")
                        
                        # Create characters from these matches
                        job_names = ["Fighter", "Thief", "Black Mage", "White Mage", "Red Mage", "Monk"]
                        self.characters = []
                        
                        for i, (name, job_str) in enumerate(job_matches):
                            job_id = int(job_str) if job_str.isdigit() else i % len(job_names)
                            
                            character = {
                                'id': f"char{i}",
                                'name': name,
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
                            print(f"Created character: {character['name']}, Job: {character['job_name']}")
                        
                        print(f"Successfully extracted {len(self.characters)} characters with direct object method")
                        return True
                    
                # Look for character definitions in other formats
                print("Looking for character definitions in other formats...")
                sample_patterns = [
                    r'startPosition\s*=\s*\[\s*\{[^}]*?\}\s*\]',
                    r'charaStatus\s*=\s*\{(.*?)\}',
                    r'characters:\s*\[\s*\{.*?\}\s*\]',
                    r'player\s*:\s*\{[^}]*?\}'
                ]
                
                for i, pattern in enumerate(sample_patterns):
                    matches = re.findall(pattern, self.js_content, re.DOTALL)
                    if matches:
                        print(f"Found match with sample pattern {i+1}: {len(matches)} matches")
                        print(f"First match sample: {matches[0][:200]}...")
                
                return False
                
            # From here, we have chars_data from one of the patterns
            # Try to extract individual character entries
            try:
                # Try to find name patterns
                name_pattern = r'name\s*:\s*["\']([^"\']+)["\']'
                names = re.findall(name_pattern, chars_data)
                
                # Try alternative name pattern with double quotes
                if not names:
                    name_pattern2 = r'"name"\s*:\s*"([^"]+)"'
                    names = re.findall(name_pattern2, chars_data)
                
                # Try to find job patterns
                job_pattern = r'job\s*:\s*(\d+)'
                jobs = re.findall(job_pattern, chars_data)
                
                # Try alternative job pattern
                if not jobs:
                    job_pattern2 = r'"job"\s*:\s*(\d+)'
                    jobs = re.findall(job_pattern2, chars_data)
                
                # Try to find level patterns
                level_pattern = r'level\s*:\s*(\d+)'
                levels = re.findall(level_pattern, chars_data)
                
                # Try alternative level pattern
                if not levels:
                    level_pattern2 = r'"level"\s*:\s*(\d+)'
                    levels = re.findall(level_pattern2, chars_data)
                
                print(f"After regex search:")
                print(f"Found {len(names)} character names: {names}")
                print(f"Found {len(jobs)} character jobs: {jobs}")
                print(f"Found {len(levels)} character levels: {levels}")
                
                if names and len(names) > 0:
                    job_names = ["Fighter", "Thief", "Black Mage", "White Mage", "Red Mage", "Monk"]
                    self.characters = []
                    
                    # Create characters with what we've found
                    for i in range(len(names)):
                        job_id = int(jobs[i]) if i < len(jobs) and jobs[i].isdigit() else i % len(job_names)
                        level = int(levels[i]) if i < len(levels) and levels[i].isdigit() else 1
                        
                        character = {
                            'id': f"char{i}",
                            'name': names[i],
                            'job': job_id,
                            'job_name': job_names[job_id % len(job_names)],
                            'level': level,
                            'hp': 100 + (job_id * 10 + level * 5),
                            'mp': [9, 9, 9, 9, 9, 9, 9, 9] if job_id in [2, 3, 4] else [0, 0, 0, 0, 0, 0, 0, 0],
                            'stats': {
                                'pw': 10 + (job_id % 3) + (level // 2),
                                'sp': 10 + ((job_id + 1) % 3) + (level // 3),
                                'it': 10 + ((job_id + 2) % 3) + (level // 3),
                                'st': 10 + (job_id % 3) + (level // 2),
                                'lk': 10 + (job_id % 2) + (level // 4),
                                'wp': 5 + (job_id % 4) + (level // 3),
                                'dx': 5 + ((job_id + 1) % 4) + (level // 3),
                                'am': 5 + ((job_id + 2) % 4) + (level // 3),
                                'ev': 5 + (job_id % 3) + (level // 4)
                            },
                            'mhp': 100 + (job_id * 10 + level * 5),
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
                        print(f"Created character: {character['name']}, Job: {character['job_name']}")
                    
                    print(f"Successfully extracted {len(self.characters)} characters with direct method")
                    return True
            except Exception as e:
                print(f"Error parsing character properties: {str(e)}")
                
            return False
        except Exception as e:
            print(f"Error in direct character extraction: {str(e)}")
            return False
            
    def extract_characters(self):
        """Extract character data from the JavaScript content."""
        try:
            print("Attempting to extract characters from app.js...")
            
            # First try the direct extraction method which might work better for some formats
            if self._try_extract_characters_direct():
                self.using_default_characters = False
                return
            
            # If direct method failed, try the pattern-based approach
            import re
            
            # First, try to get job names from app.js
            job_pattern = r'var\s+s\s*=\s*t\(["\']\.\.\/variables\/_job["\']'
            job_names = list(self.job_sprite_map.keys())
            
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
                    self.using_default_characters = False
                    
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
                        
                        # Add character to list
                        self.characters.append(character)
                        
                    print(f"Successfully extracted {len(self.characters)} characters")
                    return
                    
            # If we couldn't extract characters using any method, use default characters
            print("Could not extract characters from app.js, using default characters")
            self.characters = DEFAULT_CHARACTERS.copy()
            self.using_default_characters = True
            return
            
        except Exception as e:
            print(f"Error extracting characters: {str(e)}")
            print("Using default characters")
            self.characters = DEFAULT_CHARACTERS.copy()
            self.using_default_characters = True
    
    def extract_items(self):
        """Extract item data from the JavaScript content."""
        self.items = []
        
        print("Extracting items from app.js...")
        items_found = False
        
        # Pattern 1: Look for weapon items (wep array)
        wep_pattern = r'wep\s*:\s*\[\s*\{(.*?)\}\s*\],'
        wep_match = re.search(wep_pattern, self.js_content, re.DOTALL)
        
        if wep_match:
            print("Found weapon items array")
            wep_content = wep_match.group(1)
            
            # Extract individual weapon items
            item_pattern = r'\{\s*idx\s*:\s*(\d+),([^}]+)\}'
            item_matches = re.findall(item_pattern, wep_content, re.DOTALL)
            
            for idx_str, item_str in item_matches:
                try:
                    # Parse weapon properties
                    name_match = re.search(r'name\s*:\s*["\']([^"\']+)["\']', item_str)
                    buy_match = re.search(r'buy\s*:\s*(\d+)', item_str)
                    sell_match = re.search(r'sell\s*:\s*(\d+)', item_str)
                    
                    if name_match:
                        # Try to determine the weapon category
                        weapon_type = "Sword"  # Default
                        if "knife" in item_str.lower() or "dagger" in item_str.lower():
                            weapon_type = "Dagger"
                        elif "axe" in item_str.lower():
                            weapon_type = "Axe"
                        elif "spear" in item_str.lower() or "lance" in item_str.lower():
                            weapon_type = "Spear"
                        elif "bow" in item_str.lower():
                            weapon_type = "Bow"
                        elif "staff" in item_str.lower() or "rod" in item_str.lower():
                            weapon_type = "Staff"
                        elif "wand" in item_str.lower():
                            weapon_type = "Wand"
                        elif "fist" in item_str.lower() or "claw" in item_str.lower():
                            weapon_type = "Fist"
                        elif "gun" in item_str.lower():
                            weapon_type = "Gun"
                        
                        item = {
                            'name': name_match.group(1),
                            'type': 'Weapon',
                            'category': weapon_type,
                            'power': 0,
                            'price': int(buy_match.group(1)) if buy_match else 0,
                            'quantity': 1,
                            'rarity': 'Common',  # Default rarity
                            'description': f"A basic {name_match.group(1)}",
                            'effect': {
                                'target': 'Self',
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
                            'job_restrictions': [],
                            'stat_bonuses': {
                                'pw': 0, 'sp': 0, 'it': 0, 'st': 0, 'lk': 0, 'ma': 0
                            }
                        }
                        
                        # Set rarity based on item power or price
                        rarity_value = 0
                        if buy_match:
                            rarity_value = int(buy_match.group(1))
                        
                        if rarity_value > 20000:
                            item['rarity'] = 'Legendary'
                        elif rarity_value > 10000:
                            item['rarity'] = 'Epic'
                        elif rarity_value > 5000:
                            item['rarity'] = 'Rare'
                        elif rarity_value > 1000:
                            item['rarity'] = 'Uncommon'
                            
                        # Parse job restrictions
                        job_match = re.search(r'job\s*:\s*\[(.*?)\]', item_str)
                        if job_match:
                            job_str = job_match.group(1)
                            all_job_ids = list(range(7))  # Assuming 7 jobs (0-6)
                            
                            # Parse included job IDs
                            included_job_ids = [int(job_id) for job_id in re.findall(r'(\d+)', job_str)]
                            
                            # If job list is specified, any job not in the list is restricted
                            excluded_job_ids = [job_id for job_id in all_job_ids if job_id not in included_job_ids]
                            item['job_restrictions'] = excluded_job_ids
                        
                        # Parse stat bonuses
                        st_match = re.search(r'st\s*:\s*\{([^}]+)\}', item_str)
                        if st_match:
                            st_str = st_match.group(1)
                            
                            # In the JS, wp = weapon power, dx = dexterity/accuracy, crt = critical hit rate
                            wp_match = re.search(r'wp\s*:\s*(\d+)', st_str)
                            dx_match = re.search(r'dx\s*:\s*(\d+)', st_str)
                            crt_match = re.search(r'crt\s*:\s*(\d+)', st_str)
                            
                            if wp_match:
                                item['power'] = int(wp_match.group(1))
                                item['stat_bonuses']['pw'] = int(wp_match.group(1)) // 2
                            
                            if dx_match:
                                item['stat_bonuses']['sp'] = int(dx_match.group(1)) // 5
                            
                            if crt_match:
                                item['stat_bonuses']['lk'] = int(crt_match.group(1))
                        
                        self.items.append(item)
                        items_found = True
                except Exception as e:
                    print(f"Error parsing weapon item: {str(e)}")
        
        # Pattern 2: Look for armor items (arm array)
        arm_pattern = r'arm\s*:\s*\[\s*\{(.*?)\}\s*\],'
        arm_match = re.search(arm_pattern, self.js_content, re.DOTALL)
        
        if arm_match:
            print("Found armor items array")
            arm_content = arm_match.group(1)
            
            # Extract individual armor items
            item_pattern = r'\{\s*idx\s*:\s*(\d+),([^}]+)\}'
            item_matches = re.findall(item_pattern, arm_content, re.DOTALL)
            
            for idx_str, item_str in item_matches:
                try:
                    # Parse armor properties
                    name_match = re.search(r'name\s*:\s*["\']([^"\']+)["\']', item_str)
                    buy_match = re.search(r'buy\s*:\s*(\d+)', item_str)
                    sell_match = re.search(r'sell\s*:\s*(\d+)', item_str)
                    
                    if name_match:
                        # Determine the armor type
                        item_name = name_match.group(1).lower()
                        item_type = "Armor"
                        category = "Medium"  # Default
                        
                        if "helmet" in item_name or "hat" in item_name or "cap" in item_name or "crown" in item_name:
                            item_type = "Helmet"
                            if "hat" in item_name or "cap" in item_name:
                                category = "Hat"
                            elif "crown" in item_name:
                                category = "Crown"
                            else:
                                category = "Helm"
                        elif "shield" in item_name or "buckler" in item_name:
                            item_type = "Shield"
                            if "buckler" in item_name:
                                category = "Buckler"
                            else:
                                category = "Shield"
                        elif "robe" in item_name or "cloak" in item_name:
                            category = "Robe"
                        elif "leather" in item_name or "vest" in item_name:
                            category = "Light"
                        elif "plate" in item_name or "chainmail" in item_name or "mail" in item_name:
                            category = "Heavy"
                            
                        # Set rarity based on item power or price
                        rarity = 'Common'  # Default rarity
                        rarity_value = 0
                        if buy_match:
                            rarity_value = int(buy_match.group(1))
                        
                        if rarity_value > 20000:
                            rarity = 'Legendary'
                        elif rarity_value > 10000:
                            rarity = 'Epic'
                        elif rarity_value > 5000:
                            rarity = 'Rare'
                        elif rarity_value > 1000:
                            rarity = 'Uncommon'
                        
                        item = {
                            'name': name_match.group(1),
                            'type': item_type,
                            'category': category,
                            'power': 0,
                            'price': int(buy_match.group(1)) if buy_match else 0,
                            'quantity': 1,
                            'rarity': rarity,
                            'description': f"A basic {name_match.group(1)}",
                            'effect': {
                                'target': 'Self',
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
                            'job_restrictions': [],
                            'stat_bonuses': {
                                'pw': 0, 'sp': 0, 'it': 0, 'st': 0, 'lk': 0, 'ma': 0
                            }
                        }
                        
                        # Parse job restrictions
                        job_match = re.search(r'job\s*:\s*\[(.*?)\]', item_str)
                        if job_match:
                            job_str = job_match.group(1)
                            all_job_ids = list(range(7))  # Assuming 7 jobs (0-6)
                            
                            # Parse included job IDs
                            included_job_ids = [int(job_id) for job_id in re.findall(r'(\d+)', job_str)]
                            
                            # If job list is specified, any job not in the list is restricted
                            excluded_job_ids = [job_id for job_id in all_job_ids if job_id not in included_job_ids]
                            item['job_restrictions'] = excluded_job_ids
                        
                        # Parse stat bonuses
                        st_match = re.search(r'st\s*:\s*\{([^}]+)\}', item_str)
                        if st_match:
                            st_str = st_match.group(1)
                            
                            # In the JS, am = armor, ev = evasion
                            am_match = re.search(r'am\s*:\s*(\d+)', st_str)
                            ev_match = re.search(r'ev\s*:\s*(-?\d+)', st_str)
                            
                            if am_match:
                                item['power'] = int(am_match.group(1))
                                item['stat_bonuses']['st'] = int(am_match.group(1)) // 3
                            
                            if ev_match:
                                ev_value = int(ev_match.group(1))
                                if ev_value < 0:
                                    item['stat_bonuses']['sp'] = ev_value // 5  # Negative impact on speed
                        
                        self.items.append(item)
                        items_found = True
                except Exception as e:
                    print(f"Error parsing armor item: {str(e)}")
        
        # Pattern 3: Look for magic/consumable items (mgc array)
        mgc_pattern = r'mgc\s*:\s*\[\s*\{(.*?)\}\s*\],'
        mgc_match = re.search(mgc_pattern, self.js_content, re.DOTALL)
        
        if mgc_match:
            print("Found magic/consumable items array")
            mgc_content = mgc_match.group(1)
            
            # Extract individual magic items - which can also be treated as consumable items
            item_pattern = r'\{\s*idx\s*:\s*(\d+),([^}]+)\}'
            item_matches = re.findall(item_pattern, mgc_content, re.DOTALL)
            
            for idx_str, item_str in item_matches:
                try:
                    # Parse magic properties
                    name_match = re.search(r'name\s*:\s*["\']([^"\']+)["\']', item_str)
                    buy_match = re.search(r'buy\s*:\s*(\d+)', item_str)
                    
                    if name_match:
                        # Look for the act object which contains effect information
                        act_match = re.search(r'act\s*:\s*\{([^}]+)\}', item_str)
                        effect_target = 'Single'
                        effect_type = 'None'
                        effect_strength = 0
                        
                        # Determine consumable category
                        category = "Potion"  # Default
                        item_name = name_match.group(1).lower()
                        
                        if "ether" in item_name or "mp" in item_name:
                            category = "Ether"
                        elif "elixir" in item_name:
                            category = "Elixir"
                        elif "antidote" in item_name or "poison" in item_name:
                            category = "Antidote"
                        elif "phoenix" in item_name or "revive" in item_name or "life" in item_name:
                            category = "Phoenix Down"
                        elif "tent" in item_name or "cottage" in item_name:
                            category = "Tent"
                        elif "scroll" in item_name or "book" in item_name:
                            category = "Scroll"
                        
                        # Set status effects (all false by default)
                        status_effects = {
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
                        
                        if act_match:
                            act_str = act_match.group(1)
                            
                            # Parse effect properties
                            id_match = re.search(r'id\s*:\s*["\']([^"\']+)["\']', act_str)
                            effect_id = id_match.group(1) if id_match else ""
                            
                            # Determine effect type based on effect ID
                            if 'heal' in effect_id:
                                effect_type = 'Restore HP'
                            elif 'mp' in effect_id or 'ether' in effect_id:
                                effect_type = 'Restore MP'
                            elif 'fire' in effect_id or 'dia' in effect_id:
                                effect_type = 'Damage'
                            elif 'protes' in effect_id or 'blink' in effect_id:
                                effect_type = 'Buff Stats'
                            elif 'life' in effect_id or 'phoenix' in effect_id:
                                effect_type = 'Revive'
                            elif 'poison' in effect_id:
                                effect_type = 'Cure Status'
                                # This is likely a cure for poison
                                category = "Antidote"
                            elif 'sleep' in effect_id:
                                # Check if it's causing or curing sleep
                                if 'cure' in effect_id or 'heal' in effect_id:
                                    effect_type = 'Cure Status'
                                else:
                                    effect_type = 'Cause Status'
                                    status_effects['sleep'] = True
                            elif 'blind' in effect_id:
                                # Check if it's causing or curing blindness
                                if 'cure' in effect_id or 'heal' in effect_id:
                                    effect_type = 'Cure Status'
                                else:
                                    effect_type = 'Cause Status'
                                    status_effects['blind'] = True
                            elif 'slow' in effect_id:
                                effect_type = 'Cause Status'
                                status_effects['slow'] = True
                            elif 'stone' in effect_id or 'petrif' in effect_id:
                                effect_type = 'Cause Status'
                                status_effects['stone'] = True
                            elif 'confus' in effect_id:
                                effect_type = 'Cause Status'
                                status_effects['confusion'] = True
                            
                            # Parse target
                            trg_match = re.search(r'trg\s*:\s*\[\s*["\']([^"\']+)["\'],\s*["\']([^"\']+)["\']', act_str)
                            if trg_match:
                                target_type = trg_match.group(1)
                                target_scope = trg_match.group(2)
                                
                                if target_type == 'enemy':
                                    effect_target = 'Enemy' if target_scope == 'single' else 'All Enemies'
                                elif target_type == 'player':
                                    if target_scope == 'self':
                                        effect_target = 'Self'
                                    elif target_scope == 'single':
                                        effect_target = 'Single'
                                    else:
                                        effect_target = 'All'
                            
                            # Parse effect strength
                            val_match = re.search(r'val\s*:\s*\{\s*min\s*:\s*(\d+),\s*max\s*:\s*(\d+)\s*\}', act_str)
                            if val_match:
                                min_val = int(val_match.group(1))
                                max_val = int(val_match.group(2))
                                effect_strength = (min_val + max_val) // 2
                            else:
                                val_match = re.search(r'val\s*:\s*(\d+)', act_str)
                                if val_match:
                                    effect_strength = int(val_match.group(1))
                        
                        # Set rarity based on effect strength or price
                        rarity = 'Common'  # Default rarity
                        rarity_value = effect_strength
                        if buy_match:
                            rarity_value = max(rarity_value, int(buy_match.group(1)))
                        
                        if rarity_value > 500:
                            rarity = 'Legendary'
                        elif rarity_value > 300:
                            rarity = 'Epic'
                        elif rarity_value > 100:
                            rarity = 'Rare'
                        elif rarity_value > 50:
                            rarity = 'Uncommon'
                        
                        item = {
                            'name': name_match.group(1),
                            'type': 'Consumable',
                            'category': category,
                            'power': effect_strength,
                            'price': int(buy_match.group(1)) if buy_match else 0,
                            'quantity': 1,
                            'rarity': rarity,
                            'description': f"A magical item with {effect_type.lower()} effects.",
                            'effect': {
                                'target': effect_target,
                                'type': effect_type,
                                'strength': effect_strength,
                                'status': status_effects
                            },
                            'job_restrictions': [],
                            'stat_bonuses': {'pw': 0, 'sp': 0, 'it': 0, 'st': 0, 'lk': 0, 'ma': 0}
                        }
                        
                        # Parse job restrictions
                        job_match = re.search(r'job\s*:\s*\[(.*?)\]', item_str)
                        if job_match:
                            job_str = job_match.group(1)
                            all_job_ids = list(range(7))  # Assuming 7 jobs (0-6)
                            
                            # Parse included job IDs
                            included_job_ids = [int(job_id) for job_id in re.findall(r'(\d+)', job_str)]
                            
                            # If job list is specified, any job not in the list is restricted
                            excluded_job_ids = [job_id for job_id in all_job_ids if job_id not in included_job_ids]
                            item['job_restrictions'] = excluded_job_ids
                        
                        self.items.append(item)
                        items_found = True
                except Exception as e:
                    print(f"Error parsing magic/consumable item: {str(e)}")
        
        # Pattern 4: Look for other items (like Key Items, etc.)
        other_item_pattern = r'({[^{}]*?name\s*:\s*["\'][^"\']+["\'][^{}]*?type\s*:\s*["\'](?:item|key)["\'][^{}]*?})'
        other_item_matches = re.findall(other_item_pattern, self.js_content, re.DOTALL)
        
        for item_str in other_item_matches:
            try:
                # Parse item properties
                name_match = re.search(r'name\s*:\s*["\']([^"\']+)["\']', item_str)
                type_match = re.search(r'type\s*:\s*["\']([^"\']+)["\']', item_str)
                
                if name_match:
                    item_type = 'Key Item'
                    if type_match:
                        if 'key' in type_match.group(1):
                            item_type = 'Key Item'
                        elif 'item' in type_match.group(1):
                            item_type = 'Misc'
                    
                    # Determine category based on name and context
                    category = "Quest"  # Default for key items
                    item_name = name_match.group(1).lower()
                    
                    if 'key' in item_name:
                        category = 'Access'
                    elif 'crystal' in item_name or 'orb' in item_name:
                        category = 'Story'
                    elif 'collection' in item_name or 'trophy' in item_name:
                        category = 'Collectible'
                    elif item_type == 'Misc':
                        if 'material' in item_name or 'ore' in item_name or 'wood' in item_name:
                            category = 'Material'
                        elif 'gold' in item_name or 'jewel' in item_name or 'gem' in item_name:
                            category = 'Valuable'
                        elif 'craft' in item_name:
                            category = 'Crafting'
                        else:
                            category = 'Junk'
                    
                    # Set rarity
                    rarity = 'Common'
                    if item_type == 'Key Item':
                        if 'crystal' in item_name or 'legendary' in item_name:
                            rarity = 'Legendary'
                        else:
                            rarity = 'Rare'  # Most key items are at least rare
                    
                    item = {
                        'name': name_match.group(1),
                        'type': item_type,
                        'category': category,
                        'power': 0,
                        'price': 0,
                        'quantity': 1,
                        'rarity': rarity,
                        'description': f"A special {item_type.lower()}.",
                        'effect': {
                            'target': 'None',
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
                        'job_restrictions': [],
                        'stat_bonuses': {'pw': 0, 'sp': 0, 'it': 0, 'st': 0, 'lk': 0, 'ma': 0}
                    }
                    
                    # Parse message/description
                    msg_match = re.search(r'msg\s*:\s*["\']([^"\']+)["\']', item_str)
                    if msg_match:
                        item['description'] = msg_match.group(1)
                    
                    self.items.append(item)
                    items_found = True
            except Exception as e:
                print(f"Error parsing other item: {str(e)}")
        
        # If no items found, use the default items
        if not items_found:
            print("No items found in app.js, using default items")
            self.items = DEFAULT_ITEMS.copy()
        
        print(f"Successfully extracted {len(self.items)} items")
        return
        
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
                
        # If no maps found, use the default maps
        if not self.maps:
            print("No maps found in app.js, using default maps")
            self.maps = DEFAULT_MAPS.copy()
            self.using_default_maps = True
            
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
                
        # If no battles found, use default battles
        if not self.battles:
            print("No battles found in app.js, using default battles")
            self.battles = DEFAULT_BATTLES.copy()
            self.using_default_battles = True
            
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
                
        # If no spells found, use default spells
        if not self.spells:
            print("No spells found in app.js, using default spells")
            self.spells = DEFAULT_SPELLS.copy()
            self.using_default_spells = True
            
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
                
        # If no monsters found, use default monsters
        if not self.monsters:
            print("No monsters found in app.js, using default monsters")
            self.monsters = DEFAULT_MONSTERS.copy()
            self.using_default_monsters = True
            
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
                
        # If no NPCs found, use default NPCs
        if not self.npcs:
            print("No NPCs found in app.js, using default NPCs")
            self.npcs = DEFAULT_NPCS.copy()
            self.using_default_npcs = True
            
    def extract_item_subcategories(self, item_type, item_str):
        """Extract and determine item subcategory based on item type and properties."""
        # Default subcategories for each type
        default_categories = {
            "Weapon": "Sword",
            "Armor": "Light",
            "Helmet": "Hat",
            "Shield": "Shield",
            "Accessory": "Ring",
            "Consumable": "Potion",
            "Key Item": "Quest",
            "Relic": "Ancient",
            "Misc": "Valuable"
        }
        
        # Check for weapon type
        if item_type == "Weapon":
            # Try to guess weapon type from name
            name_hints = {
                "sword": "Sword", "blade": "Sword", "sabre": "Sword", "saber": "Sword",
                "dagger": "Dagger", "knife": "Dagger", "dirk": "Dagger",
                "axe": "Axe", "battleaxe": "Axe",
                "spear": "Spear", "lance": "Spear", "halberd": "Spear",
                "bow": "Bow", "crossbow": "Bow", "longbow": "Bow",
                "staff": "Staff", "rod": "Staff",
                "wand": "Wand",
                "fist": "Fist", "knuckle": "Fist", "claw": "Fist",
                "gun": "Gun", "pistol": "Gun", "rifle": "Gun"
            }
            
            item_name_lower = item_str.lower()
            for hint, category in name_hints.items():
                if hint in item_name_lower:
                    return category
                    
        # Check for consumable type
        elif item_type == "Consumable":
            # Try to guess consumable type from effects and name
            if "Restore HP" in item_str:
                return "Potion"
            elif "Restore MP" in item_str:
                return "Ether"
            elif "Revive" in item_str or "phoenix" in item_str.lower():
                return "Phoenix Down"
            elif "poison" in item_str.lower():
                return "Antidote"
            elif "tent" in item_str.lower():
                return "Tent"
            elif "scroll" in item_str.lower():
                return "Scroll"
                
        # Check for armor type
        elif item_type == "Armor":
            if "robe" in item_str.lower() or "cloth" in item_str.lower():
                return "Robe"
            elif "light" in item_str.lower() or "leather" in item_str.lower():
                return "Light"
            elif "heavy" in item_str.lower() or "plate" in item_str.lower():
                return "Heavy"
                
        # Return default category if cannot be determined
        return default_categories.get(item_type, "Misc")
            
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