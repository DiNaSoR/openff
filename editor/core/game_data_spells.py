"""
Spell data handling module.
"""

DEBUG = False  # Set to False to disable debug print output

def dprint(*args, **kwargs):
    if DEBUG:
        print(*args, **kwargs)

import re
import os
from core.game_data import GameData
from core.default_game_data import DEFAULT_SPELLS

class GameDataSpells(GameData):
    """Handler for spell data in the game."""
    
    def __init__(self):
        """Initialize spell data handler."""
        super().__init__()
        self.spells = []
        self.using_default_spells = False
        
    def extract_spells(self):
        """Extract spell data from the JavaScript content."""
        dprint("\n==== SPELL EXTRACTION STARTED ====")
        dprint("Extracting spells from JS content...")
        
        # Check if we have JS content
        if not self.js_content:
            dprint("No JavaScript content to extract spells from")
            self.spells = DEFAULT_SPELLS.copy()
            self.using_default_spells = True
            dprint("Using default spells instead")
            return
            
        # Using a similar approach to what works in GameDataItems._extract_magic_array
        # Pattern to find magic array
        pattern = r'mgc\s*:\s*\[\s*\{(.*?)\}\s*\]'
        all_spells = []
        
        try:
            matches = re.findall(pattern, self.js_content, re.DOTALL)
            if matches:
                dprint(f"Found mgc array with {len(matches)} matches")
                
                # Process the first magic array we found
                magic_contents = matches[0]
                dprint(f"Magic array content length: {len(magic_contents)} characters")
                
                # Split the content into individual spell objects
                magic_strings = re.split(r'\},\s*\{', magic_contents)
                dprint(f"Found {len(magic_strings)} potential spell objects")
                
                for i, magic_str in enumerate(magic_strings):
                    # Add back the curly braces that were removed in the split
                    if i > 0:
                        magic_str = '{' + magic_str
                    if i < len(magic_strings) - 1:
                        magic_str = magic_str + '}'
                    
                    dprint(f"\nProcessing spell candidate {i+1}...")
                    spell = self._parse_spell_properties(magic_str)
                    if spell:
                        all_spells.append(spell)
                        dprint(f"✅ Added spell: {spell['name']} (Type: {spell['type']}, Power: {spell['power']}, MP: {spell['mp_cost']}, Target: {spell['target']})")
                    else:
                        dprint(f"❌ Failed to parse spell candidate {i+1}")
                
                # If we found spells, save them
                if all_spells:
                    self.spells = all_spells
                    self.using_default_spells = False
                    dprint(f"\n✅ Successfully extracted {len(all_spells)} spells")
                    dprint("Spell names extracted:")
                    for i, spell in enumerate(all_spells):
                        dprint(f"  {i+1}. {spell['name']} ({spell['type']})")
                    return
                else:
                    dprint("No valid spells found in the mgc array")
            else:
                dprint("Could not find mgc array in the JS content")
        except Exception as e:
            dprint(f"Error extracting spells: {str(e)}")
        
        # Use defaults if we couldn't extract any spells
        dprint("\n❌ Could not extract any spells from game data, using defaults instead")
        self.spells = DEFAULT_SPELLS.copy()
        self.using_default_spells = True
        dprint("Default spell names:")
        for i, spell in enumerate(self.spells):
            dprint(f"  {i+1}. {spell['name']} ({spell['type']})")
        
        dprint("==== SPELL EXTRACTION COMPLETED ====\n")
        
    def _get_spell_image_file(self, act_id, effect_type):
        """Get the appropriate image file for a spell based on its action ID and effect type."""
        try:
            # Map action IDs to player effect GIFs
            player_effect_map = {
                'fire': 'player_effect_magic_fire.gif',
                'thunder': 'player_effect_magic_thunder.gif',
                'heal': 'player_effect_magic_heal.gif',
                'dia': 'player_effect_magic_dia.gif',
                'protes': 'player_effect_magic_protes.gif',
                'blink': 'player_effect_magic_blink.gif',
                'shape': 'player_effect_magic_shape.gif',
                'sripl': 'player_effect_magic_sripl.gif',
            }
            
            # Map effect types to enemy effect GIFs
            enemy_effect_map = {
                'rd': 'enemy_effect_magic_rd.gif',  # Red effect
                'gr': 'enemy_effect_magic_gr.gif',  # Green effect
                'bl': 'enemy_effect_magic_bl.gif',  # Blue effect
                'yw': 'enemy_effect_magic_yw.gif',  # Yellow effect
            }
            
            result = {}
            
            # Check if we have a player effect image for this action ID
            if act_id and act_id.lower() in player_effect_map:
                player_file = player_effect_map[act_id.lower()]
                
                # First try the absolute path - based on where the application is run from
                base_path = os.path.abspath("img/sp")
                player_path = os.path.join(base_path, player_file)
                
                if os.path.exists(player_path):
                    result['player_effect'] = player_file
                    dprint(f"Found player effect image: {player_path}")
                else:
                    # Try alternate paths - sometimes the editor runs from a different directory
                    alternate_paths = [
                        os.path.abspath("../img/sp"),
                        os.path.abspath("../../img/sp"),
                    ]
                    
                    for path in alternate_paths:
                        alt_player_path = os.path.join(path, player_file)
                        if os.path.exists(alt_player_path):
                            result['player_effect'] = player_file
                            dprint(f"Found player effect image in alternate path: {alt_player_path}")
                            break
            
            # Check if we have an enemy effect image for this effect type
            if effect_type and effect_type.lower() in enemy_effect_map:
                enemy_file = enemy_effect_map[effect_type.lower()]
                
                # First try the absolute path
                base_path = os.path.abspath("img/sp")
                enemy_path = os.path.join(base_path, enemy_file)
                
                if os.path.exists(enemy_path):
                    result['enemy_effect'] = enemy_file
                    dprint(f"Found enemy effect image: {enemy_path}")
                else:
                    # Try alternate paths
                    alternate_paths = [
                        os.path.abspath("../img/sp"),
                        os.path.abspath("../../img/sp"),
                    ]
                    
                    for path in alternate_paths:
                        alt_enemy_path = os.path.join(path, enemy_file)
                        if os.path.exists(alt_enemy_path):
                            result['enemy_effect'] = enemy_file
                            dprint(f"Found enemy effect image in alternate path: {alt_enemy_path}")
                            break
            
            return result
        
        except Exception as e:
            dprint(f"Error finding spell images: {str(e)}")
            return {}
        
    def _parse_spell_properties(self, spell_str):
        """Parse spell properties from a string representation."""
        try:
            dprint("------- Parsing spell properties -------")
            spell = {}
            
            # Extract name if available
            name_match = re.search(r'name\s*:\s*["\']([^"\']*)["\']', spell_str)
            if name_match:
                spell['name'] = name_match.group(1)
                dprint(f"📝 Found name: {spell['name']}")
            else:
                dprint("❌ No name found, skipping")
                return None
            
            # Check if this is actually a spell by looking for spell-specific properties
            is_spell = False
            
            mlv_match = re.search(r'mlv\s*:', spell_str)
            if mlv_match:
                is_spell = True
                dprint("✅ Found magic level indicator (mlv)")
            
            act_id_match = re.search(r'act\s*:.*?id\s*:', spell_str, re.DOTALL)
            if act_id_match:
                if not re.search(r'battle\s*:', spell_str):
                    is_spell = True
                    dprint("✅ Found action ID indicator (act.id)")
                
            job_match = re.search(r'job\s*:\s*\[', spell_str)
            if job_match:
                is_spell = True
                dprint("✅ Found job restrictions")
            
            if not is_spell:
                dprint("❌ Object does not appear to be a spell, skipping")
                return None
            
            mlv_match = re.search(r'mlv\s*:\s*(\d+)', spell_str)
            if mlv_match:
                spell['level'] = int(mlv_match.group(1))
                dprint(f"📝 Found level: {spell['level']}")
            else:
                spell['level'] = 0
                dprint("📝 No level found, using default: 0")
            
            buy_match = re.search(r'buy\s*:\s*(\d+)', spell_str)
            if buy_match:
                buy_price = int(buy_match.group(1))
                spell['mp_cost'] = max(1, min(20, buy_price // 20))
                dprint(f"📝 Found buy price: {buy_price}, estimated MP cost: {spell['mp_cost']}")
            else:
                spell['mp_cost'] = 5
                dprint("📝 No buy price found, using default MP cost: 5")
            
            act_id = None
            act_id_match = re.search(r'act\s*:.*?id\s*:\s*["\']([^"\']*)["\']', spell_str, re.DOTALL)
            if act_id_match:
                act_id = act_id_match.group(1).lower()
                dprint(f"📝 Found action ID: {act_id}")
                
                spell_type_map = {
                    'fire': 'Fire',
                    'thunder': 'Lightning',
                    'heal': 'Heal',
                    'dia': 'Light',
                    'protes': 'Buff',
                    'blink': 'Buff',
                    'sripl': 'Status',
                    'shape': 'Status'
                }
                
                spell['type'] = spell_type_map.get(act_id, 'Fire')
                dprint(f"📝 Mapped to spell type: {spell['type']}")
            else:
                dprint("No action ID found, guessing type from name...")
                if 'cure' in spell['name'].lower() or 'heal' in spell['name'].lower() or 'ケアル' in spell['name']:
                    spell['type'] = 'Heal'
                elif 'fire' in spell['name'].lower() or 'ファイア' in spell['name']:
                    spell['type'] = 'Fire'
                elif 'thunder' in spell['name'].lower() or 'lightning' in spell['name'].lower() or 'サンダー' in spell['name']:
                    spell['type'] = 'Lightning'
                elif 'blizzard' in spell['name'].lower() or 'ice' in spell['name'].lower():
                    spell['type'] = 'Ice'
                elif 'protect' in spell['name'].lower() or 'shell' in spell['name'].lower() or 'haste' in spell['name'].lower() or 'プロテス' in spell['name']:
                    spell['type'] = 'Buff'
                else:
                    spell['type'] = 'Fire'
                dprint(f"📝 Guessed spell type from name: {spell['type']}")
            
            min_val_match = re.search(r'val\s*:\s*\{\s*min\s*:\s*(\d+)', spell_str)
            if min_val_match:
                spell['power'] = int(min_val_match.group(1))
                dprint(f"📝 Found power (min val): {spell['power']}")
            else:
                val_match = re.search(r'val\s*:\s*(\d+)', spell_str)
                if val_match:
                    spell['power'] = int(val_match.group(1))
                    dprint(f"📝 Found power (direct val): {spell['power']}")
                else:
                    spell['power'] = max(5, spell['level'] * 5 + 5)
                    dprint(f"📝 No power found, calculated from level: {spell['power']}")
            
            trg_match = re.search(r'trg\s*:\s*\[\s*["\']([^"\']*)["\']', spell_str)
            if trg_match:
                target_type = trg_match.group(1).lower()
                dprint(f"📝 Found target type: {target_type}")
                
                scope_match = re.search(r'trg\s*:\s*\[\s*["\'][^"\']*["\'],\s*["\']([^"\']*)["\']', spell_str)
                target_scope = scope_match.group(1).lower() if scope_match else "single"
                dprint(f"📝 Found target scope: {target_scope}")
                
                if target_type == 'enemy' and target_scope == 'all':
                    spell['target'] = 'All Enemies'
                elif target_type == 'player' and target_scope == 'all':
                    spell['target'] = 'All Allies'
                elif target_scope == 'self':
                    spell['target'] = 'Self'
                elif target_type == 'player':
                    spell['target'] = 'Single Ally'
                elif target_type == 'enemy':
                    spell['target'] = 'Single Enemy'
                else:
                    if spell['type'] in ['Heal', 'Cure', 'Buff']:
                        spell['target'] = 'Single Ally'
                    else:
                        spell['target'] = 'Single Enemy'
                dprint(f"📝 Mapped to target: {spell['target']}")
            else:
                dprint("No target information found, using defaults based on type...")
                if spell['type'] in ['Heal', 'Cure', 'Buff']:
                    spell['target'] = 'Single Ally'
                else:
                    spell['target'] = 'Single Enemy'
                dprint(f"📝 Set default target: {spell['target']}")
            
            effect_type = None
            effect_type_match = re.search(r'effectType\s*:\s*["\']([^"\']*)["\']', spell_str)
            if effect_type_match:
                effect_type = effect_type_match.group(1)
                spell['effect_type'] = effect_type
                dprint(f"📝 Found effect type: {effect_type}")
            
            flash_color_match = re.search(r'flashColor\s*:\s*["\']([^"\']*)["\']', spell_str)
            if flash_color_match:
                flash_color = flash_color_match.group(1)
                spell['flash_color'] = flash_color
                dprint(f"📝 Found flash color: {flash_color}")
            
            msg_match = re.search(r'msg\s*:\s*["\']([^"\']*)["\']', spell_str)
            if msg_match and msg_match.group(1):
                msg = msg_match.group(1).replace('<br>', ' ')
                spell['description'] = msg
                dprint(f"📝 Found description: {msg[:30]}...")
            else:
                if spell['type'] in ['Heal', 'Cure']:
                    spell['description'] = f"A healing spell with power {spell['power']}."
                elif spell['type'] == 'Buff':
                    spell['description'] = f"A support spell that enhances abilities."
                else:
                    spell['description'] = f"An offensive {spell['type']} spell with power {spell['power']}."
                dprint(f"📝 Generated description: {spell['description']}")
            
            image_files = self._get_spell_image_file(act_id, effect_type)
            if image_files:
                spell['image_files'] = image_files
                dprint(f"📝 Found spell images: {image_files}")
            
            dprint("✅ Successfully parsed spell properties")
            return spell
        except Exception as e:
            dprint(f"❌ Error parsing spell: {str(e)}")
            return None
            
    def get_spell_by_name(self, name):
        """Get a spell by name."""
        for spell in self.spells:
            if spell.get('name') == name:
                return spell
        return None
