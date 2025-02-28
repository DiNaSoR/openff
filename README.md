# OpenFF Game Editor

A comprehensive editor for the OpenFF game engine that provides tools for editing game elements like characters, items, maps, battles, spells, monsters, and NPCs, as well as code editing capabilities.

## Features

- **Game Element Editors**:
  - **Character Editor**: Edit character attributes, stats, and images
  - **Item Editor**: Manage game items with visual representations
  - **Map Editor**: Create and edit game maps with a tile-based interface
  - **Battle Editor**: Design battle encounters with enemy placement
  - **Spell Editor**: Create and modify spells with visual effects
  - **Monster Editor**: Design and customize game monsters with attributes and battle properties
  - **NPC Editor**: Create and manage non-player characters with dialogue and quest options

- **Code Editing**:
  - Syntax highlighting for JavaScript and other file types
  - File explorer for navigating project files
  - Tabbed interface for editing multiple files

- **Game Data Management**:
  - Extract game data from app.js
  - Save changes back to the game files
  - Automatic updates when code files are modified

## Requirements

- Python 3.6+
- PyQt6
- QScintilla (for code editing)

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/openff-game-editor.git
   cd openff-game-editor
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage

Run the editor:
```
python main.py
```

### Editing Game Elements

1. Select the appropriate tab for the game element you want to edit (Characters, Items, Maps, Battles, Spells, Monsters, or NPCs).
2. Use the list on the left to select an existing element or click "Add" to create a new one.
3. Edit the element's properties in the form on the right.
4. Click "Save Changes" to save your changes to the selected element.
5. Use "Save Game Data" from the Game menu to save all changes back to the game files.

### Editing Code

1. Use the file explorer on the left to navigate to and open code files.
2. Edit the code in the editor.
3. Press Ctrl+S to save changes.
4. If you edit app.js, game data will be automatically updated.

## Project Structure

```
openff-game-editor/
├── editor/                  # Editor modules
│   ├── modules/             # Editor module components
│   │   ├── battle_editor/   # Battle editor module
│   │   ├── character_editor/ # Character editor module
│   │   ├── code_editor/     # Code editor module
│   │   ├── file_explorer/   # File explorer module
│   │   ├── game_data/       # Game data management module
│   │   ├── item_editor/     # Item editor module
│   │   ├── map_editor/      # Map editor module
│   │   ├── monster_editor/  # Monster editor module
│   │   ├── npc_editor/      # NPC editor module
│   │   └── spell_editor/    # Spell editor module
│   └── utils/               # Utility functions
├── resources/               # Application resources
├── main.py                  # Main entry point
└── README.md                # This file
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
