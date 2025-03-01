"""
Map data handling module.
"""

import re
from core.game_data import GameData
from core.default_game_data import DEFAULT_MAPS

class GameDataMaps(GameData):
    """Handler for map data in the game."""
    
    def __init__(self):
        """Initialize map data handler."""
        super().__init__()
        self.maps = []
        self.using_default_maps = False
        
    def extract_maps(self):
        """Extract map data from the JavaScript content."""
        print("Extracting maps...")
        
        # Look for map data in the JavaScript content
        patterns = [
            # Look for map array or object initialization
            r'this\.gl\.map\s*=\s*\{(.*?)\}',
            r'this\.gl\.maps\s*=\s*\[(.*?)\]',
            r'maps\s*:\s*\{(.*?)\}'
        ]
        
        all_maps = []
        
        for pattern in patterns:
            matches = re.findall(pattern, self.js_content, re.DOTALL)
            for match in matches:
                # Try to extract individual map entries
                map_entries = re.findall(r'([a-zA-Z0-9_]+)\s*:\s*\{(.*?)\}', match, re.DOTALL)
                
                for map_id, map_content in map_entries:
                    map_data = self._parse_map_properties(map_id, map_content)
                    if map_data:
                        all_maps.append(map_data)
        
        # If we found maps, save them
        if all_maps:
            self.maps = all_maps
            self.using_default_maps = False
            print(f"Successfully extracted {len(self.maps)} maps")
            return
            
        # If we couldn't extract maps, use defaults
        print("Using default map data")
        self.maps = DEFAULT_MAPS.copy()
        self.using_default_maps = True
        
    def _parse_map_properties(self, map_id, map_content):
        """Parse map properties from a string representation."""
        try:
            map_data = {
                'id': map_id
            }
            
            # Extract name if available
            name_match = re.search(r'name\s*:\s*["\']([^"\']*)["\']', map_content)
            if name_match:
                map_data['name'] = name_match.group(1)
            else:
                # Use ID as name if not specified
                map_data['name'] = map_id.replace('_', ' ').title()
                
            # Extract dimensions
            width_match = re.search(r'width\s*:\s*(\d+)', map_content)
            height_match = re.search(r'height\s*:\s*(\d+)', map_content)
            
            if width_match:
                map_data['width'] = int(width_match.group(1))
            else:
                map_data['width'] = 20  # Default width
                
            if height_match:
                map_data['height'] = int(height_match.group(1))
            else:
                map_data['height'] = 15  # Default height
                
            # Extract tileset if available
            tileset_match = re.search(r'tileset\s*:\s*["\']?([^"\',:]+)["\']?', map_content)
            if tileset_match:
                map_data['tileset'] = tileset_match.group(1)
            else:
                # Try to guess tileset from map name or ID
                if 'castle' in map_id.lower() or 'castle' in map_data['name'].lower():
                    map_data['tileset'] = 'castle'
                elif 'town' in map_id.lower() or 'town' in map_data['name'].lower() or 'village' in map_id.lower():
                    map_data['tileset'] = 'town'
                elif 'dungeon' in map_id.lower() or 'cave' in map_id.lower():
                    map_data['tileset'] = 'dungeon'
                elif 'forest' in map_id.lower():
                    map_data['tileset'] = 'forest'
                else:
                    map_data['tileset'] = 'field'  # Default tileset
                    
            # Extract battle background if available
            bg_match = re.search(r'battleBg\s*:\s*["\']?([^"\',:]+)["\']?', map_content)
            if bg_match:
                map_data['battle_background'] = bg_match.group(1)
            else:
                # Default battle background based on tileset
                if map_data['tileset'] == 'field':
                    map_data['battle_background'] = 'field'
                elif map_data['tileset'] == 'forest':
                    map_data['battle_background'] = 'forest'
                elif map_data['tileset'] == 'dungeon':
                    map_data['battle_background'] = 'dungeon'
                else:
                    map_data['battle_background'] = 'field'  # Default
                    
            # Extract encounter rate if available
            rate_match = re.search(r'encounterRate\s*:\s*(\d+)', map_content)
            if rate_match:
                map_data['encounter_rate'] = int(rate_match.group(1))
            else:
                # Default encounter rate based on map type
                if 'town' in map_data['tileset'] or 'castle' in map_data['tileset']:
                    map_data['encounter_rate'] = 0  # No encounters in towns
                elif 'dungeon' in map_data['tileset']:
                    map_data['encounter_rate'] = 10  # High rate in dungeons
                else:
                    map_data['encounter_rate'] = 5  # Medium rate in fields/forests
                    
            return map_data
        except Exception as e:
            print(f"Error parsing map data: {str(e)}")
            return None
            
    def get_map_by_name(self, name):
        """Get a map by name."""
        for map_data in self.maps:
            if map_data.get('name') == name:
                return map_data
        return None 