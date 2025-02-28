#!/usr/bin/env python3
"""
Test script to verify that PyQt6 is installed and working correctly.
"""

import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel

def main():
    """Main entry point for the application."""
    # Create the application
    app = QApplication(sys.argv)
    
    # Create the main window
    window = QMainWindow()
    window.setWindowTitle("PyQt6 Test")
    window.setGeometry(100, 100, 400, 200)
    
    # Create a label
    label = QLabel("If you see this message, PyQt6 is working correctly.", window)
    label.setGeometry(50, 50, 300, 100)
    
    # Show the window
    window.show()
    
    # Run the application
    sys.exit(app.exec())

if __name__ == "__main__":
    main() 