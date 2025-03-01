"""
Spell data handling module.
"""

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
        print("\n==== SPELL EXTRACTION STARTED ====")
        print("Extracting spells from JS content...")
        
        # Check if we have JS content
        if not self.js_content:
            print("No JavaScript content to extract spells from")
            self.spells = DEFAULT_SPELLS.copy()
            self.using_default_spells = True
            print("Using default spells instead")
            return
            
        # Using a similar approach to what works in GameDataItems._extract_magic_array
        # Pattern to find magic array
        pattern = r'mgc\s*:\s*\[\s*\{(.*?)\}\s*\]'
        all_spells = []
        
        try:
            matches = re.findall(pattern, self.js_content, re.DOTALL)
            if matches:
                print(f"Found mgc array with {len(matches)} matches")
                
                # Process the first magic array we found
                magic_contents = matches[0]
                print(f"Magic array content length: {len(magic_contents)} characters")
                
                # Split the content into individual spell objects
                magic_strings = re.split(r'\},\s*\{', magic_contents)
                print(f"Found {len(magic_strings)} potential spell objects")
                
                for i, magic_str in enumerate(magic_strings):
                    # Add back the curly braces that were removed in the split
                    if i > 0:
                        magic_str = '{' + magic_str
                    if i < len(magic_strings) - 1:
                        magic_str = magic_str + '}'
                    
                    print(f"\nProcessing spell candidate {i+1}...")
                    spell = self._parse_spell_properties(magic_str)
                    if spell:
                        all_spells.append(spell)
                        print(f"✅ Added spell: {spell['name']} (Type: {spell['type']}, Power: {spell['power']}, MP: {spell['mp_cost']}, Target: {spell['target']})")
                    else:
                        print(f"❌ Failed to parse spell candidate {i+1}")
                
                # If we found spells, save them
                if all_spells:
                    self.spells = all_spells
                    self.using_default_spells = False
                    print(f"\n✅ Successfully extracted {len(all_spells)} spells")
                    print("Spell names extracted:")
                    for i, spell in enumerate(all_spells):
                        print(f"  {i+1}. {spell['name']} ({spell['type']})")
                    return
                else:
                    print("No valid spells found in the mgc array")
            else:
                print("Could not find mgc array in the JS content")
        except Exception as e:
            print(f"Error extracting spells: {str(e)}")
        
        # Use defaults if we couldn't extract any spells
        print("\n❌ Could not extract any spells from game data, using defaults instead")
        self.spells = DEFAULT_SPELLS.copy()
        self.using_default_spells = True
        print("Default spell names:")
        for i, spell in enumerate(self.spells):
            print(f"  {i+1}. {spell['name']} ({spell['type']})")
        
        print("==== SPELL EXTRACTION COMPLETED ====\n")
        
    def _get_spell_image_file(self, act_id, effect_type):
        """Get the appropriate image file for a spell based on its action ID and effect type."""
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
        
        # Check if we have a player effect image for this action ID
        if act_id and act_id in player_effect_map:
            player_file = player_effect_map[act_id]
            if os.path.exists(f"img/sp/{player_file}"):
                return {'player_effect': player_file}
        
        # Check if we have an enemy effect image for this effect type
        result = {}
        if effect_type and effect_type in enemy_effect_map:
            enemy_file = enemy_effect_map[effect_type]
            if os.path.exists(f"img/sp/{enemy_file}"):
                result['enemy_effect'] = enemy_file
                
        return result
        
    def _parse_spell_properties(self, spell_str):
        """Parse spell properties from a string representation."""
        try:
            print("------- Parsing spell properties -------")
            spell = {}
            
            # Extract name if available
            name_match = re.search(r'name\s*:\s*["\']([^"\']*)["\']', spell_str)
            if name_match:
                spell['name'] = name_match.group(1)
                print(f"📝 Found name: {spell['name']}")
            else:
                # Skip spells without a name
                print("❌ No name found, skipping")
                return None
            
            # Check if this is actually a spell by looking for spell-specific properties
            # A real spell should have act.id, mlv (magic level), or job restrictions
            is_spell = False
            
            # Check for magic level
            mlv_match = re.search(r'mlv\s*:', spell_str)
            if mlv_match:
                is_spell = True
                print("✅ Found magic level indicator (mlv)")
            
            # Check for act.id which indicates an action
            act_id_match = re.search(r'act\s*:.*?id\s*:', spell_str, re.DOTALL)
            if act_id_match:
                # Also check that this is a magic action, not an item action
                if not re.search(r'battle\s*:', spell_str):  # Most items have battle flag
                    is_spell = True
                    print("✅ Found action ID indicator (act.id)")
                
            # Check for job restrictions (spells often have job restrictions)
            job_match = re.search(r'job\s*:\s*\[', spell_str)
            if job_match:
                is_spell = True
                print("✅ Found job restrictions")
            
            # If this doesn't appear to be a spell, skip it
            if not is_spell:
                print("❌ Object does not appear to be a spell, skipping")
                return None
            
            # Extract magic level (mlv)
            mlv_match = re.search(r'mlv\s*:\s*(\d+)', spell_str)
            if mlv_match:
                spell['level'] = int(mlv_match.group(1))
                print(f"📝 Found level: {spell['level']}")
            else:
                spell['level'] = 0
                print("📝 No level found, using default: 0")
            
            # Extract buy price for MP cost estimation
            buy_match = re.search(r'buy\s*:\s*(\d+)', spell_str)
            if buy_match:
                buy_price = int(buy_match.group(1))
                # MP cost is often correlated with buy price
                spell['mp_cost'] = max(1, min(20, buy_price // 20))
                print(f"📝 Found buy price: {buy_price}, estimated MP cost: {spell['mp_cost']}")
            else:
                spell['mp_cost'] = 5  # Default MP cost
                print("📝 No buy price found, using default MP cost: 5")
            
            # Extract act id (which corresponds to spell type)
            act_id = None
            act_id_match = re.search(r'act\s*:.*?id\s*:\s*["\']([^"\']*)["\']', spell_str, re.DOTALL)
            if act_id_match:
                act_id = act_id_match.group(1).lower()
                print(f"📝 Found action ID: {act_id}")
                
                # Map the act.id to spell types
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
                print(f"📝 Mapped to spell type: {spell['type']}")
            else:
                print("No action ID found, guessing type from name...")
                # Fallback: Try to guess from name
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
                    spell['type'] = 'Fire'  # Default
                print(f"📝 Guessed spell type from name: {spell['type']}")
            
            # Extract power/effect from val object or value
            # First try if val is a min/max object
            min_val_match = re.search(r'val\s*:\s*\{\s*min\s*:\s*(\d+)', spell_str)
            if min_val_match:
                spell['power'] = int(min_val_match.group(1))
                print(f"📝 Found power (min val): {spell['power']}")
            else:
                # Try if val is a direct number
                val_match = re.search(r'val\s*:\s*(\d+)', spell_str)
                if val_match:
                    spell['power'] = int(val_match.group(1))
                    print(f"📝 Found power (direct val): {spell['power']}")
                else:
                    # Default power based on level
                    spell['power'] = max(5, spell['level'] * 5 + 5)
                    print(f"📝 No power found, calculated from level: {spell['power']}")
            
            # Extract targeting from trg array
            trg_match = re.search(r'trg\s*:\s*\[\s*["\']([^"\']*)["\']', spell_str)
            if trg_match:
                target_type = trg_match.group(1).lower()
                print(f"📝 Found target type: {target_type}")
                
                # Extract target scope from second element in array
                scope_match = re.search(r'trg\s*:\s*\[\s*["\'][^"\']*["\'],\s*["\']([^"\']*)["\']', spell_str)
                target_scope = scope_match.group(1).lower() if scope_match else "single"
                print(f"📝 Found target scope: {target_scope}")
                
                # Map to expected target values in spell editor
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
                    # Default based on spell type
                    if spell['type'] in ['Heal', 'Cure', 'Buff']:
                        spell['target'] = 'Single Ally'
                    else:
                        spell['target'] = 'Single Enemy'
                print(f"📝 Mapped to target: {spell['target']}")
            else:
                print("No target information found, using defaults based on type...")
                # Default targeting based on spell type
                if spell['type'] in ['Heal', 'Cure', 'Buff']:
                    spell['target'] = 'Single Ally'
                else:
                    spell['target'] = 'Single Enemy'
                print(f"📝 Set default target: {spell['target']}")
            
            # Extract effect type for visual representation
            effect_type = None
            effect_type_match = re.search(r'effectType\s*:\s*["\']([^"\']*)["\']', spell_str)
            if effect_type_match:
                effect_type = effect_type_match.group(1)
                # Store for potential use in visualization
                spell['effect_type'] = effect_type
                print(f"📝 Found effect type: {effect_type}")
            
            # Extract flash color for visual representation
            flash_color_match = re.search(r'flashColor\s*:\s*["\']([^"\']*)["\']', spell_str)
            if flash_color_match:
                flash_color = flash_color_match.group(1)
                # Store for potential use in visualization
                spell['flash_color'] = flash_color
                print(f"📝 Found flash color: {flash_color}")
            
            # Extract description (from msg field in app.js)
            msg_match = re.search(r'msg\s*:\s*["\']([^"\']*)["\']', spell_str)
            if msg_match and msg_match.group(1):
                # Clean up HTML in the message
                msg = msg_match.group(1).replace('<br>', ' ')
                spell['description'] = msg
                print(f"📝 Found description: {msg[:30]}...")
            else:
                # Generate a simple description
                if spell['type'] in ['Heal', 'Cure']:
                    spell['description'] = f"A healing spell with power {spell['power']}."
                elif spell['type'] == 'Buff':
                    spell['description'] = f"A support spell that enhances abilities."
                else:
                    spell['description'] = f"An offensive {spell['type']} spell with power {spell['power']}."
                print(f"📝 Generated description: {spell['description']}")
            
            # Add image files based on action ID and effect type
            image_files = self._get_spell_image_file(act_id, effect_type)
            if image_files:
                spell['image_files'] = image_files
                print(f"📝 Found spell images: {image_files}")
            
            print("✅ Successfully parsed spell properties")
            return spell
        except Exception as e:
            print(f"❌ Error parsing spell: {str(e)}")
            return None
            
    def get_spell_by_name(self, name):
        """Get a spell by name."""
        for spell in self.spells:
            if spell.get('name') == name:
                return spell
        return None 