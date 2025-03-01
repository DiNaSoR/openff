"""
NPC data handling module.
"""

import re
from core.game_data import GameData
from core.default_game_data import DEFAULT_NPCS

class GameDataNPCs(GameData):
    """Handler for NPC data in the game."""
    
    def __init__(self):
        """Initialize NPC data handler."""
        super().__init__()
        self.npcs = []
        self.using_default_npcs = False
        
    def extract_npcs(self):
        """Extract NPC data from the JavaScript content."""
        print("Extracting NPCs...")
        
        # Look for NPC data in the JavaScript content
        patterns = [
            # Look for NPC array initialization
            r'this\.gl\.npc\s*=\s*\[(.*?)\]',
            r'this\.gl\.npcs\s*=\s*\[(.*?)\]',
            # Look for NPC object
            r'npc\s*:\s*\{(.*?)\}',
            r'npcs\s*:\s*\{(.*?)\}'
        ]
        
        all_npcs = []
        
        for pattern in patterns:
            matches = re.findall(pattern, self.js_content, re.DOTALL)
            for match in matches:
                # Process each NPC entry
                if '{' in match:  # If it's an object with multiple NPCs
                    npc_entries = re.findall(r'([a-zA-Z0-9_]+)\s*:\s*\{(.*?)\}', match, re.DOTALL)
                    
                    for npc_id, npc_content in npc_entries:
                        npc = self._parse_npc_properties(npc_id, npc_content)
                        if npc:
                            all_npcs.append(npc)
                else:  # If it's an array of NPC objects
                    npc_matches = re.findall(r'\{(.*?)\}', match, re.DOTALL)
                    for i, npc_str in enumerate(npc_matches):
                        npc = self._parse_npc_properties(f"npc{i}", npc_str)
                        if npc:
                            all_npcs.append(npc)
        
        # If we found NPCs, save them
        if all_npcs:
            self.npcs = all_npcs
            self.using_default_npcs = False
            print(f"Successfully extracted {len(self.npcs)} NPCs")
            return
            
        # If we couldn't extract NPCs, use defaults
        print("Using default NPC data")
        self.npcs = DEFAULT_NPCS.copy()
        self.using_default_npcs = True
        
    def _parse_npc_properties(self, npc_id, npc_content):
        """Parse NPC properties from a string representation."""
        try:
            npc = {
                'id': npc_id
            }
            
            # Extract name if available
            name_match = re.search(r'name\s*:\s*["\']([^"\']*)["\']', npc_content)
            if name_match:
                npc['name'] = name_match.group(1)
            else:
                # Use ID as name if not specified
                npc['name'] = npc_id.replace('_', ' ').title()
                
            # Extract role/occupation if available
            role_match = re.search(r'role\s*:\s*["\']([^"\']*)["\']', npc_content)
            if role_match:
                npc['role'] = role_match.group(1)
            else:
                # Default role based on name
                if 'king' in npc['name'].lower() or 'queen' in npc['name'].lower():
                    npc['role'] = 'Royalty'
                elif 'merchant' in npc['name'].lower() or 'shop' in npc['name'].lower():
                    npc['role'] = 'Merchant'
                elif 'guard' in npc['name'].lower():
                    npc['role'] = 'Guard'
                else:
                    npc['role'] = 'Villager'  # Default role
                    
            # Extract dialogue/text if available
            dialogue_match = re.search(r'dialogue\s*:\s*["\']([^"\']*)["\']', npc_content)
            if not dialogue_match:
                dialogue_match = re.search(r'text\s*:\s*["\']([^"\']*)["\']', npc_content)
                
            if dialogue_match:
                npc['dialogue'] = dialogue_match.group(1)
            else:
                # Default dialogue based on role
                if npc['role'] == 'Merchant':
                    npc['dialogue'] = "Welcome to my shop! What would you like to buy?"
                elif npc['role'] == 'Guard':
                    npc['dialogue'] = "Halt! State your business."
                elif npc['role'] == 'Royalty':
                    npc['dialogue'] = "Greetings, traveler."
                else:
                    npc['dialogue'] = "Hello there!"  # Default dialogue
                    
            # Extract map location if available
            map_match = re.search(r'map\s*:\s*["\']?([^"\',:]+)["\']?', npc_content)
            if map_match:
                npc['map'] = map_match.group(1)
            else:
                npc['map'] = "town"  # Default map
                
            # Extract position if available
            x_match = re.search(r'x\s*:\s*(\d+)', npc_content)
            y_match = re.search(r'y\s*:\s*(\d+)', npc_content)
            
            if x_match:
                npc['x'] = int(x_match.group(1))
            else:
                npc['x'] = 10  # Default x position
                
            if y_match:
                npc['y'] = int(y_match.group(1))
            else:
                npc['y'] = 10  # Default y position
                
            # Extract sprite/image if available
            sprite_match = re.search(r'sprite\s*:\s*["\']?([^"\',:]+)["\']?', npc_content)
            if sprite_match:
                npc['sprite'] = sprite_match.group(1)
            else:
                # Default sprite
                npc['sprite'] = f"npc{npc_id.replace('npc', '')}.png"
                
            # Extract quest-related properties if available
            if 'quest' in npc_content.lower():
                npc['has_quest'] = True
                
                quest_id_match = re.search(r'questId\s*:\s*["\']?([^"\',:]+)["\']?', npc_content)
                if quest_id_match:
                    npc['quest_id'] = quest_id_match.group(1)
                else:
                    npc['quest_id'] = f"quest_{npc_id}"
            else:
                npc['has_quest'] = False
                
            return npc
        except Exception as e:
            print(f"Error parsing NPC data: {str(e)}")
            return None
            
    def get_npc_by_name(self, name):
        """Get an NPC by name."""
        for npc in self.npcs:
            if npc.get('name') == name:
                return npc
        return None 