import sys
sys.path.append('.')  # Add current directory to path

from editor.core.game_data_items import GameDataItems

# Create an item handler and load the JS file
item_handler = GameDataItems()
item_handler.load_js('js/app.js')

# Extract items
item_handler.extract_items()

# Print results
print(f"Total items found: {len(item_handler.items)}")

# Count items by type
types = {}
for item in item_handler.items:
    item_type = item.get('type', 'Unknown')
    types[item_type] = types.get(item_type, 0) + 1

# Print type breakdown
print(f"Item types: {types}")

# Print a few items of each type as examples
examples = {}
for item in item_handler.items:
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