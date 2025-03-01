"""
Base game data module that provides core functionality for all data handlers.
"""

import os
import json


class GameData:
    """Base class for game data handling."""
    
    def __init__(self):
        """Initialize the game data handler."""
        self._has_changes = False
        self.js_content = ""
        self.js_path = ""
        
    def has_changes(self):
        """Check if there are unsaved changes."""
        return self._has_changes
        
    def mark_as_changed(self):
        """Mark the data as changed."""
        self._has_changes = True
        
    def load_js_content(self, js_content, js_path=""):
        """Load JavaScript content for parsing."""
        self.js_content = js_content
        self.js_path = js_path
        
    def load_from_file(self, js_path):
        """Load game data from the specified JavaScript file."""
        self.js_path = js_path
        
        try:
            with open(js_path, 'r', encoding='utf-8') as f:
                self.js_content = f.read()
            return True
        except Exception as e:
            print(f"Error loading game data: {str(e)}")
            return False
            
    def create_backup(self, file_path):
        """Create a backup of the specified file."""
        if os.path.exists(file_path):
            backup_path = file_path + ".bak"
            try:
                import shutil
                shutil.copy2(file_path, backup_path)
                return True
            except Exception as e:
                print(f"Warning: Could not create backup: {str(e)}")
                return False
        return False 