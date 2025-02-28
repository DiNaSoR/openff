#!/usr/bin/env python3

"""
Script to check if all required editor modules exist and can be imported.
"""

import os
import sys
import importlib
import traceback

# Add parent directory to path
parent_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, parent_dir)

def check_module(module_path):
    """Check if a module can be imported."""
    try:
        module = importlib.import_module(module_path)
        print(f"✓ Successfully imported {module_path}")
        return None
    except Exception as e:
        print(f"✗ Failed to import {module_path}: {type(e).__name__}: {str(e)}")
        return (module_path, type(e).__name__, str(e))

def main():
    """Main entry point."""
    print("Checking editor modules...")
    
    modules_to_check = [
        # Core modules
        "editor.core.game_data_manager",
        
        # Utility modules
        "editor.utils.theme",
        
        # Editor modules
        "editor.modules.character_editor.character_editor",
        "editor.modules.item_editor.item_editor",
        "editor.modules.map_editor.map_editor",
        "editor.modules.battle_editor.battle_editor",
        "editor.modules.spell_editor.spell_editor",
        "editor.modules.monster_editor.monster_editor",
        "editor.modules.npc_editor.npc_editor",
        "editor.modules.code_editor.code_editor",
        "editor.modules.file_explorer.file_explorer",
        "editor.modules.game_data.game_data_manager"
    ]
    
    failed_modules = []
    
    for module in modules_to_check:
        result = check_module(module)
        if result:
            failed_modules.append(result)
    
    success_count = len(modules_to_check) - len(failed_modules)
    print(f"\nSummary: Successfully imported {success_count}/{len(modules_to_check)} modules")
    
    if not failed_modules:
        print("All modules are working correctly!")
    else:
        print("\nModules that need to be fixed:")
        for module, error_type, error_msg in failed_modules:
            print(f"  - {module}: {error_type}: {error_msg}")
    
if __name__ == "__main__":
    main() 