import re
import json

def extract_equipment_array(js_content, equipment_type, array_key):
    """
    Extract equipment arrays like weapons and armor from the JavaScript content.
    
    Args:
        js_content (str): JavaScript content
        equipment_type (str): Type of equipment ('weapon' or 'armor')
        array_key (str): The key in the JS object ('wep' or 'arm')
        
    Returns:
        list: Extracted equipment items
    """
    # Pattern to find equipment arrays
    pattern = fr'{array_key}\s*:\s*\[\s*\{{(.*?)\}}\s*\]'
    
    extracted_items = []
    
    try:
        matches = re.findall(pattern, js_content, re.DOTALL)
        if matches:
            # Process the equipment array
            equipment_contents = matches[0]
            equipment_strings = re.split(r'\},\s*\{', equipment_contents)
            
            for i, equip_str in enumerate(equipment_strings):
                # Add back the curly braces that were removed in the split
                if i > 0:
                    equip_str = '{' + equip_str
                if i < len(equipment_strings) - 1:
                    equip_str = equip_str + '}'
                
                # Parse the equipment item
                item = parse_equipment_from_js(equip_str, equipment_type)
                if item:
                    extracted_items.append(item)
                    print(f"Found {equipment_type}: {item['name']}")
                    
    except Exception as e:
        print(f"Error extracting {equipment_type} array: {str(e)}")
        
    return extracted_items

def parse_equipment_from_js(equip_str, equipment_type):
    """
    Parse equipment (weapon/armor) from JavaScript.
    
    Args:
        equip_str (str): String representation of equipment
        equipment_type (str): 'weapon' or 'armor'
        
    Returns:
        dict: Parsed equipment item or None if parsing fails
    """
    try:
        # Extract basic properties
        idx_match = re.search(r'idx\s*:\s*(\d+)', equip_str)
        name_match = re.search(r'name\s*:\s*["\']([^"\']*)["\']', equip_str)
        ctg_match = re.search(r'ctg\s*:\s*["\']([^"\']*)["\']', equip_str)
        
        if not name_match:
            return None
            
        # Determine specific equipment type based on category
        specific_type = 'Weapon'
        category = 'Sword'  # Default
        
        if equipment_type == 'armor':
            specific_type = 'Armor'
            category = 'Medium'  # Default
            
            # Check if it's a different armor type
            if ctg_match:
                ctg = ctg_match.group(1)
                if ctg == 'head':
                    specific_type = 'Helmet'
                    category = 'Helm'
                elif ctg == 'shield':
                    specific_type = 'Shield'
                    category = 'Shield'
                elif ctg == 'acce' or ctg == 'accessory':
                    specific_type = 'Accessory'
                    category = 'Ring'
        
        if equipment_type == 'weapon' and ctg_match:
            ctg = ctg_match.group(1)
            if ctg == 'slash':
                category = 'Sword'
            elif ctg == 'pierce':
                category = 'Spear'
            elif ctg == 'blow':
                category = 'Axe'
            elif ctg == 'wand' or ctg == 'staff':
                category = 'Staff'
                
        # Create the equipment item
        item = {
            'name': name_match.group(1),
            'type': specific_type,
            'category': category,
            'power': 0,
            'price': 0,
            'description': f"A {specific_type.lower()}."
        }
        
        # Extract item ID if available
        if idx_match:
            item['id'] = int(idx_match.group(1))
        
        # Extract price information
        buy_match = re.search(r'buy\s*:\s*(\d+)', equip_str)
        sell_match = re.search(r'sell\s*:\s*(\d+)', equip_str)
        
        if buy_match:
            item['price'] = int(buy_match.group(1))
            
        # Extract job restrictions
        job_match = re.search(r'job\s*:\s*\[(.*?)\]', equip_str)
        if job_match:
            job_str = job_match.group(1)
            # Convert job indices to a list of integers
            job_values = [int(v.strip()) for v in job_str.split(',') if v.strip().isdigit()]
            item['job_restrictions'] = job_values
        else:
            item['job_restrictions'] = []
            
        # Extract stats based on equipment type
        st_match = re.search(r'st\s*:\s*\{(.*?)\}', equip_str, re.DOTALL)
        if st_match:
            st_str = st_match.group(1)
            
            # Initialize stat bonuses
            item['stat_bonuses'] = {'pw': 0, 'sp': 0, 'it': 0, 'st': 0, 'lk': 0}
            
            # For weapons, check weapon power
            if equipment_type == 'weapon':
                wp_match = re.search(r'wp\s*:\s*(\d+)', st_str)
                if wp_match:
                    item['power'] = int(wp_match.group(1))
                
                # Check critical hit rate
                crt_match = re.search(r'crt\s*:\s*(\d+)', st_str)
                if crt_match:
                    item['stat_bonuses']['lk'] = int(crt_match.group(1))
            
            # For armor, check armor and evasion
            elif equipment_type == 'armor':
                am_match = re.search(r'am\s*:\s*(\d+)', st_str)
                if am_match:
                    item['power'] = int(am_match.group(1))
                
                # Check evasion (might be negative)
                ev_match = re.search(r'ev\s*:\s*(-?\d+)', st_str)
                if ev_match:
                    item['stat_bonuses']['sp'] = int(ev_match.group(1))
        
        return item
    except Exception as e:
        print(f"Error parsing equipment: {str(e)}")
        return None

# Load the JavaScript file
with open('js/app.js', 'r', encoding='utf-8') as f:
    js_content = f.read()

# Extract weapons
weapons = extract_equipment_array(js_content, 'weapon', 'wep')
print(f"Found {len(weapons)} weapons")

# Extract armor (which includes body armor, helmets, shields, and accessories)
armor = extract_equipment_array(js_content, 'armor', 'arm')
print(f"Found {len(armor)} armor items")

# Count items by type
all_items = weapons + armor
types = {}
for item in all_items:
    item_type = item.get('type', 'Unknown')
    types[item_type] = types.get(item_type, 0) + 1

# Print type breakdown
print(f"Item types: {types}")

# Print a few items of each type as examples
examples = {}
for item in all_items:
    item_type = item.get('type', 'Unknown')
    if item_type not in examples:
        examples[item_type] = []
    if len(examples[item_type]) < 2:  # Show up to 2 examples per type
        examples[item_type].append(item)

print("\nExample items:")
for item_type, items in examples.items():
    print(f"\n{item_type}:")
    for item in items:
        print(f"  - {item['name']} (Price: {item.get('price', 0)})") 