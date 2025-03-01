"""
Game Data Manager - Main module that integrates all game data components.
"""

import os
import re
import json

from core.game_data import GameData
from core.game_data_characters import GameDataCharacters
from core.game_data_items import GameDataItems
from core.game_data_spells import GameDataSpells
from core.game_data_maps import GameDataMaps
from core.game_data_battles import GameDataBattles
from core.game_data_monsters import GameDataMonsters
from core.game_data_npcs import GameDataNPCs

class GameDataManager:
    """Main manager for all game data components."""
    
    def __init__(self):
        """Initialize the game data manager."""
        # Create data handlers for each type of game data
        self.character_data = GameDataCharacters()
        self.item_data = GameDataItems()
        self.spell_data = GameDataSpells()
        self.map_data = GameDataMaps()
        self.battle_data = GameDataBattles()
        self.monster_data = GameDataMonsters()
        self.npc_data = GameDataNPCs()
        
        # Working variables
        self.js_path = ""
        self.js_content = ""
        self._has_changes = False
        
    def load_from_file(self, js_path):
        """Load game data from the specified JavaScript file."""
        self.js_path = js_path
        
        try:
            print(f"Loading game data from {js_path}...")
            with open(js_path, 'r', encoding='utf-8') as f:
                self.js_content = f.read()
                
            # Distribute the JS content to all data handlers
            self._distribute_js_content()
                
            # Parse the game data
            self.parse_game_data()
            
            # Reset changes flag after loading
            self._has_changes = False
            
            return True
        except Exception as e:
            print(f"Error loading game data: {str(e)}")
            return False
    
    def _distribute_js_content(self):
        """Distribute the loaded JS content to all data handlers."""
        handlers = [
            self.character_data,
            self.item_data,
            self.spell_data,
            self.map_data,
            self.battle_data,
            self.monster_data,
            self.npc_data
        ]
        
        for handler in handlers:
            handler.load_js_content(self.js_content, self.js_path)
            
    def has_changes(self):
        """Check if there are unsaved changes in any data component."""
        # Check if the main manager has changes
        if self._has_changes:
            return True
            
        # Check if any of the data handlers have changes
        return (self.character_data.has_changes() or
                self.item_data.has_changes() or
                self.spell_data.has_changes() or
                self.map_data.has_changes() or
                self.battle_data.has_changes() or
                self.monster_data.has_changes() or
                self.npc_data.has_changes())
        
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
            # Create a backup of the original file if it exists
            if os.path.exists(file_path):
                backup_path = file_path + ".bak"
                try:
                    import shutil
                    shutil.copy2(file_path, backup_path)
                    print(f"Created backup at {backup_path}")
                except Exception as e:
                    print(f"Warning: Could not create backup: {str(e)}")
            
            # For now, just print what would be saved
            print(f"Saving {len(self.characters)} characters, {len(self.items)} items, "
                  f"{len(self.maps)} maps, {len(self.battles)} battles, {len(self.spells)} spells, "
                  f"{len(self.monsters)} monsters, and {len(self.npcs)} NPCs to {file_path}")
            
            # In a real implementation, you would update the actual file here
            # This would involve complex JavaScript generation based on the data
            
            # Reset changes flag for all components
            self._reset_changes()
            
            return True
        except Exception as e:
            print(f"Error saving game data: {str(e)}")
            return False
            
    def _reset_changes(self):
        """Reset the changes flag for all components."""
        self._has_changes = False
        
        # Reset changes for all data handlers
        handlers = [
            self.character_data,
            self.item_data,
            self.spell_data,
            self.map_data,
            self.battle_data,
            self.monster_data,
            self.npc_data
        ]
        
        for handler in handlers:
            handler._has_changes = False
            
    def parse_game_data(self):
        """Parse game data from the loaded JavaScript content."""
        print("Parsing game data...")
        
        # Extract different game elements using their respective handlers
        self.character_data.extract_characters()
        self.item_data.extract_items()
        self.map_data.extract_maps()
        self.battle_data.extract_battles()
        self.spell_data.extract_spells()
        self.monster_data.extract_monsters()
        self.npc_data.extract_npcs()
        
        print("Game data parsing complete")
    
    # Properties to access data from different handlers
    @property
    def characters(self):
        return self.character_data.characters
        
    @characters.setter
    def characters(self, value):
        self.character_data.characters = value
        self.character_data.mark_as_changed()
    
    @property
    def items(self):
        return self.item_data.items
        
    @items.setter
    def items(self, value):
        self.item_data.items = value
        self.item_data.mark_as_changed()
    
    @property
    def spells(self):
        return self.spell_data.spells
        
    @spells.setter
    def spells(self, value):
        self.spell_data.spells = value
        self.spell_data.mark_as_changed()
    
    @property
    def maps(self):
        return self.map_data.maps
        
    @maps.setter
    def maps(self, value):
        self.map_data.maps = value
        self.map_data.mark_as_changed()
    
    @property
    def battles(self):
        return self.battle_data.battles
        
    @battles.setter
    def battles(self, value):
        self.battle_data.battles = value
        self.battle_data.mark_as_changed()
    
    @property
    def monsters(self):
        return self.monster_data.monsters
        
    @monsters.setter
    def monsters(self, value):
        self.monster_data.monsters = value
        self.monster_data.mark_as_changed()
    
    @property
    def npcs(self):
        return self.npc_data.npcs
        
    @npcs.setter
    def npcs(self, value):
        self.npc_data.npcs = value
        self.npc_data.mark_as_changed()
    
    # Properties for "using default" flags
    @property
    def using_default_characters(self):
        return self.character_data.using_default_characters
    
    @property
    def using_default_items(self):
        return self.item_data.using_default_items
    
    @property
    def using_default_spells(self):
        return self.spell_data.using_default_spells
    
    @property
    def using_default_maps(self):
        return self.map_data.using_default_maps
    
    @property
    def using_default_battles(self):
        return self.battle_data.using_default_battles
    
    @property
    def using_default_monsters(self):
        return self.monster_data.using_default_monsters
    
    @property
    def using_default_npcs(self):
        return self.npc_data.using_default_npcs
    
    # Convenience methods that delegate to the appropriate handler
    def get_character_by_name(self, name):
        """Get a character by name."""
        return self.character_data.get_character_by_name(name)
        
    def get_item_by_name(self, name):
        """Get an item by name."""
        return self.item_data.get_item_by_name(name)
        
    def get_spell_by_name(self, name):
        """Get a spell by name."""
        return self.spell_data.get_spell_by_name(name)
        
    def get_map_by_name(self, name):
        """Get a map by name."""
        return self.map_data.get_map_by_name(name)
        
    def get_battle_by_name(self, name):
        """Get a battle by name."""
        return self.battle_data.get_battle_by_name(name)
        
    def get_monster_by_name(self, name):
        """Get a monster by name."""
        return self.monster_data.get_monster_by_name(name)
        
    def get_npc_by_name(self, name):
        """Get an NPC by name."""
        return self.npc_data.get_npc_by_name(name) 