#!/usr/bin/env python3
"""
OpenFF Game Editor - Main Entry Point (Simplified)

This script launches a simplified version of the OpenFF Game Editor application.
"""

import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget

class SimpleMainWindow(QMainWindow):
    """Simple main window for testing."""
    
    def __init__(self):
        super().__init__()
        
        # Set window properties
        self.setWindowTitle("OpenFF Game Editor (Simplified)")
        self.setGeometry(100, 100, 800, 600)
        
        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Create a label
        label = QLabel("OpenFF Game Editor (Simplified)")
        layout.addWidget(label)
        
        # Create another label with instructions
        instructions = QLabel(
            "This is a simplified version of the OpenFF Game Editor.\n"
            "The full version is still under development."
        )
        layout.addWidget(instructions)

def main():
    """Main entry point for the application."""
    # Create the application
    app = QApplication(sys.argv)
    
    # Create and show the main window
    window = SimpleMainWindow()
    window.show()
    
    # Run the application
    sys.exit(app.exec())

if __name__ == "__main__":
    main() 