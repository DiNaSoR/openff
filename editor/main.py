#!/usr/bin/env python3

"""
OpenFF Game Editor - Main Entry Point

This script launches the OpenFF Game Editor application.
"""

import sys
import os

# Add the parent directory to the path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)

from PyQt6.QtWidgets import QApplication, QSplashScreen
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt

# Try different import approaches
try:
    # Try direct import
    from main_window import MainWindow
    from utils.theme import apply_theme
except ImportError:
    # Try package import
    from editor.main_window import MainWindow
    from editor.utils.theme import apply_theme

def main():
    """Main entry point for the application."""
    # Create the application
    app = QApplication(sys.argv)
    apply_theme(app)
    
    # Show splash screen
    splash_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                             'img', 'editor_splash.png')
    
    # If splash image doesn't exist, create a blank pixmap
    if os.path.exists(splash_path):
        splash_pixmap = QPixmap(splash_path)
    else:
        splash_pixmap = QPixmap(400, 300)
        splash_pixmap.fill(Qt.GlobalColor.white)
    
    splash = QSplashScreen(splash_pixmap)
    splash.show()
    app.processEvents()
    
    # Display loading message
    splash.showMessage("Loading OpenFF Game Editor...", 
                      Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignCenter, 
                      Qt.GlobalColor.black)
    
    # Create and show the main window
    window = MainWindow()
    
    # Load game data
    splash.showMessage("Loading game data...", 
                      Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignCenter, 
                      Qt.GlobalColor.black)
    
    # Use try-except to handle potential errors during game data loading
    try:
        window.load_game_data()
    except Exception as e:
        print(f"Error loading game data: {str(e)}")
        # Still continue with the application even if game data loading fails
    
    # Show the window and close splash
    window.show()
    splash.finish(window)
    
    # Run the application
    sys.exit(app.exec())

if __name__ == "__main__":
    main() 