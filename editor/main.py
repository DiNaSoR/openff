import sys
from PyQt6.QtWidgets import QApplication

from editor.core.main_window import MainWindow

def main():
    """Main function to run the application."""
    app = QApplication(sys.argv)
    
    # Set application style
    app.setStyle('Fusion')
    
    # Create and show the main window
    window = MainWindow()
    window.show()
    
    # Run the application
    sys.exit(app.exec())

if __name__ == "__main__":
    main() 