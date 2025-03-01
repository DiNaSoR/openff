"""
Default game data for when extraction from app.js fails.
Contains default values for characters, items, spells, monsters, etc.
"""

# Default character data
DEFAULT_CHARACTERS = [
    {
        'id': "char0",
        'name': "Cecil",
        'job': 0,
        'job_name': "Fighter",
        'level': 1,
        'hp': 100,
        'mp': [0, 0, 0, 0, 0, 0, 0, 0],
        'stats': {
            'pw': 10,  # Power
            'sp': 10,  # Speed
            'it': 10,  # Intelligence
            'st': 10,  # Stamina
            'lk': 10,  # Luck
            'wp': 5,   # Weapon Power
            'dx': 5,   # Dexterity
            'am': 5,   # Armor
            'ev': 5    # Evasion
        },
        'mhp': 100,
        'mmp': [0, 0, 0, 0, 0, 0, 0, 0],
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
        'sprite': "job0"
    },
    {
        'id': "char1",
        'name': "Edge",
        'job': 1,
        'job_name': "Thief",
        'level': 1,
        'hp': 110,
        'mp': [0, 0, 0, 0, 0, 0, 0, 0],
        'stats': {
            'pw': 10,
            'sp': 12,
            'it': 9,
            'st': 10,
            'lk': 11,
            'wp': 6,
            'dx': 7,
            'am': 5,
            'ev': 6
        },
        'mhp': 110,
        'mmp': [0, 0, 0, 0, 0, 0, 0, 0],
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
        'sprite': "job1"
    },
    {
        'id': "char2",
        'name': "Vivi",
        'job': 2,
        'job_name': "Black Mage",
        'level': 1,
        'hp': 90,
        'mp': [9, 9, 9, 9, 9, 9, 9, 9],
        'stats': {
            'pw': 8,
            'sp': 9,
            'it': 13,
            'st': 9,
            'lk': 10,
            'wp': 4,
            'dx': 6,
            'am': 4,
            'ev': 5
        },
        'mhp': 90,
        'mmp': [9, 9, 9, 9, 9, 9, 9, 9],
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
        'sprite': "job2"
    },
    {
        'id': "char3",
        'name': "Rosa",
        'job': 3,
        'job_name': "White Mage",
        'level': 1,
        'hp': 95,
        'mp': [9, 9, 9, 9, 9, 9, 9, 9],
        'stats': {
            'pw': 8,
            'sp': 10,
            'it': 12,
            'st': 11,
            'lk': 10,
            'wp': 4,
            'dx': 5,
            'am': 6,
            'ev': 6
        },
        'mhp': 95,
        'mmp': [9, 9, 9, 9, 9, 9, 9, 9],
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
        'sprite': "job3"
    }
]

# Define job name to sprite ID mapping
JOB_SPRITE_MAP = {
    "Fighter": 0,
    "Thief": 1,
    "Black Mage": 2,
    "White Mage": 3,
    "Red Mage": 4,
    "Monk": 5,
    "Knight": 6
}

# Default item data
DEFAULT_ITEMS = [
    {
        'name': 'Sword', 
        'type': 'Weapon', 
        'power': 10,
        'price': 100,
        'quantity': 1,
        'description': "A basic sword for beginners.",
        'effect': {
            'target': 'Enemy',
            'type': 'Damage',
            'strength': 10,
            'status': {'poison': False, 'paralyze': False}
        },
        'job_restrictions': [2, 3],  # Can't be used by Black Mage and White Mage
        'stat_bonuses': {'pw': 3, 'sp': 0, 'it': 0, 'st': 0, 'lk': 0}
    },
    {
        'name': 'Staff', 
        'type': 'Weapon', 
        'power': 5,
        'price': 80,
        'quantity': 1,
        'description': "A magical staff that enhances spellcasting.",
        'effect': {
            'target': 'Enemy',
            'type': 'Damage',
            'strength': 5,
            'status': {'poison': False, 'paralyze': False}
        },
        'job_restrictions': [0],  # Can't be used by Fighter
        'stat_bonuses': {'pw': 0, 'sp': 0, 'it': 3, 'st': 0, 'lk': 0}
    },
    {
        'name': 'Potion', 
        'type': 'Consumable', 
        'power': 50,
        'price': 30,
        'quantity': 5,
        'description': "Restores 50 HP to a single ally.",
        'effect': {
            'target': 'Single',
            'type': 'Restore HP',
            'strength': 50,
            'status': {'poison': False, 'paralyze': False}
        },
        'job_restrictions': [],
        'stat_bonuses': {'pw': 0, 'sp': 0, 'it': 0, 'st': 0, 'lk': 0}
    },
    {
        'name': 'Ether', 
        'type': 'Consumable', 
        'power': 30,
        'price': 50,
        'quantity': 3,
        'description': "Restores 30 MP to a single ally.",
        'effect': {
            'target': 'Single',
            'type': 'Restore MP',
            'strength': 30,
            'status': {'poison': False, 'paralyze': False}
        },
        'job_restrictions': [],
        'stat_bonuses': {'pw': 0, 'sp': 0, 'it': 0, 'st': 0, 'lk': 0}
    },
    {
        'name': 'Leather Armor', 
        'type': 'Armor', 
        'power': 15,
        'price': 120,
        'quantity': 1,
        'description': "Basic armor that provides moderate protection.",
        'effect': {
            'target': 'Self',
            'type': 'None',
            'strength': 0,
            'status': {'poison': False, 'paralyze': False}
        },
        'job_restrictions': [2, 3],  # Can't be used by Black Mage and White Mage
        'stat_bonuses': {'pw': 0, 'sp': 0, 'it': 0, 'st': 2, 'lk': 0}
    },
    {
        'name': 'Robe', 
        'type': 'Armor', 
        'power': 8,
        'price': 90,
        'quantity': 1,
        'description': "A magical robe that enhances spellcasting.",
        'effect': {
            'target': 'Self',
            'type': 'None',
            'strength': 0,
            'status': {'poison': False, 'paralyze': False}
        },
        'job_restrictions': [0, 1],  # Can't be used by Fighter and Thief
        'stat_bonuses': {'pw': 0, 'sp': 0, 'it': 2, 'st': 1, 'lk': 0}
    },
    {
        'name': 'Crystal Key', 
        'type': 'Key Item', 
        'power': 0,
        'price': 0,
        'quantity': 1,
        'description': "A mysterious key that opens ancient doors.",
        'effect': {
            'target': 'None',
            'type': 'None',
            'strength': 0,
            'status': {'poison': False, 'paralyze': False}
        },
        'job_restrictions': [],
        'stat_bonuses': {'pw': 0, 'sp': 0, 'it': 0, 'st': 0, 'lk': 0}
    },
    {
        'name': 'Antidote', 
        'type': 'Consumable', 
        'power': 0,
        'price': 25,
        'quantity': 5,
        'description': "Cures poison status.",
        'effect': {
            'target': 'Single',
            'type': 'Cure Status',
            'strength': 0,
            'status': {'poison': True, 'paralyze': False}
        },
        'job_restrictions': [],
        'stat_bonuses': {'pw': 0, 'sp': 0, 'it': 0, 'st': 0, 'lk': 0}
    },
    {
        'name': 'Gold Ring', 
        'type': 'Accessory', 
        'power': 0,
        'price': 200,
        'quantity': 1,
        'description': "A ring that increases luck.",
        'effect': {
            'target': 'Self',
            'type': 'None',
            'strength': 0,
            'status': {'poison': False, 'paralyze': False}
        },
        'job_restrictions': [],
        'stat_bonuses': {'pw': 0, 'sp': 0, 'it': 0, 'st': 0, 'lk': 5}
    },
    {
        'name': 'Iron Sword', 
        'type': 'Weapon', 
        'power': 15,
        'price': 200,
        'quantity': 1,
        'description': "A stronger sword with better durability.",
        'effect': {
            'target': 'Enemy',
            'type': 'Damage',
            'strength': 15,
            'status': {'poison': False, 'paralyze': False}
        },
        'job_restrictions': [2, 3],
        'stat_bonuses': {'pw': 5, 'sp': 0, 'it': 0, 'st': 1, 'lk': 0}
    },
    {
        'name': 'Chain Mail', 
        'type': 'Armor', 
        'power': 20,
        'price': 250,
        'quantity': 1,
        'description': "Chain armor that offers good protection.",
        'effect': {
            'target': 'Self',
            'type': 'None',
            'strength': 0,
            'status': {'poison': False, 'paralyze': False}
        },
        'job_restrictions': [2, 3],
        'stat_bonuses': {'pw': 0, 'sp': -1, 'it': 0, 'st': 4, 'lk': 0}
    },
    {
        'name': 'Hi-Potion', 
        'type': 'Consumable', 
        'power': 100,
        'price': 100,
        'quantity': 2,
        'description': "Restores 100 HP to a single ally.",
        'effect': {
            'target': 'Single',
            'type': 'Restore HP',
            'strength': 100,
            'status': {'poison': False, 'paralyze': False}
        },
        'job_restrictions': [],
        'stat_bonuses': {'pw': 0, 'sp': 0, 'it': 0, 'st': 0, 'lk': 0}
    }
]

# Default spell data
DEFAULT_SPELLS = [
    {
        'name': 'Fire', 
        'type': 'Fire', 
        'power': 15, 
        'mp_cost': 5, 
        'target': 'Single Enemy',
        'description': 'A basic fire spell that deals fire damage to a single enemy.'
    },
    {
        'name': 'Thunder', 
        'type': 'Lightning', 
        'power': 20, 
        'mp_cost': 8, 
        'target': 'Single Enemy',
        'description': 'A lightning spell that deals lightning damage to a single enemy.'
    },
    {
        'name': 'Blizzard', 
        'type': 'Ice', 
        'power': 18, 
        'mp_cost': 7, 
        'target': 'Single Enemy',
        'description': 'An ice spell that deals ice damage to a single enemy.'
    },
    {
        'name': 'Cure', 
        'type': 'Heal', 
        'power': 25, 
        'mp_cost': 6, 
        'target': 'Single Ally',
        'description': 'A healing spell that restores HP to a single ally.'
    },
    {
        'name': 'Dia', 
        'type': 'Heal', 
        'power': 15, 
        'mp_cost': 8, 
        'target': 'All Enemies',
        'description': 'A light-based spell that damages undead enemies.'
    },
    {
        'name': 'Protect', 
        'type': 'Buff', 
        'power': 0, 
        'mp_cost': 10, 
        'target': 'Single Ally',
        'description': 'Increases physical defense of a single ally.'
    }
]

# Default monster data
DEFAULT_MONSTERS = [
    {'name': 'Goblin', 'hp': 30, 'attack': 8, 'defense': 3, 'sprite': 'monster0.png'},
    {'name': 'Wolf', 'hp': 40, 'attack': 12, 'defense': 2, 'sprite': 'monster1.png'},
    {'name': 'Skeleton', 'hp': 45, 'attack': 10, 'defense': 8, 'sprite': 'monster2.png'},
    {'name': 'Zombie', 'hp': 60, 'attack': 7, 'defense': 10, 'sprite': 'monster3.png'},
    {'name': 'Dragon', 'hp': 200, 'attack': 30, 'defense': 25, 'sprite': 'monster4.png'}
]

# Default map data
DEFAULT_MAPS = [
    {'name': 'Cornelia Town', 'width': 30, 'height': 20, 'tileset': 'town'},
    {'name': 'Cornelia Castle', 'width': 25, 'height': 25, 'tileset': 'castle'},
    {'name': 'Western Forest', 'width': 40, 'height': 30, 'tileset': 'forest'},
    {'name': 'Chaos Shrine', 'width': 20, 'height': 20, 'tileset': 'dungeon'}
]

# Default battle data
DEFAULT_BATTLES = [
    {'name': 'Forest Encounter', 'enemies': ['Goblin', 'Wolf']},
    {'name': 'Castle Guards', 'enemies': ['Guard', 'Guard', 'Captain']},
    {'name': 'Chaos Shrine', 'enemies': ['Skeleton', 'Zombie', 'Ghost']},
    {'name': 'Boss: Garland', 'enemies': ['Garland']}
]

# Default NPC data
DEFAULT_NPCS = [
    {'name': 'Mayor', 'role': 'Village Leader', 'dialogue': 'Welcome to our village!', 'sprite': 'npc0.png'},
    {'name': 'Shopkeeper', 'role': 'Merchant', 'dialogue': 'What would you like to buy?', 'sprite': 'npc1.png'},
    {'name': 'Guard', 'role': 'Protector', 'dialogue': 'Keep out of trouble!', 'sprite': 'npc2.png'},
    {'name': 'Old Man', 'role': 'Quest Giver', 'dialogue': 'I need your help with something...', 'sprite': 'npc3.png'},
    {'name': 'Child', 'role': 'Villager', 'dialogue': 'Do you want to play?', 'sprite': 'npc4.png'}
] 