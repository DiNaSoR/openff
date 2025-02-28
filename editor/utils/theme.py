from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QPalette, QColor
from PyQt6.QtCore import Qt

def apply_theme(widget):
    """Apply a dark theme to the application."""
    # Create a palette
    palette = QPalette()
    
    # Set colors
    palette.setColor(QPalette.ColorRole.Window, QColor(53, 53, 53))
    palette.setColor(QPalette.ColorRole.WindowText, Qt.GlobalColor.white)
    palette.setColor(QPalette.ColorRole.Base, QColor(25, 25, 25))
    palette.setColor(QPalette.ColorRole.AlternateBase, QColor(53, 53, 53))
    palette.setColor(QPalette.ColorRole.ToolTipBase, Qt.GlobalColor.white)
    palette.setColor(QPalette.ColorRole.ToolTipText, Qt.GlobalColor.white)
    palette.setColor(QPalette.ColorRole.Text, Qt.GlobalColor.white)
    palette.setColor(QPalette.ColorRole.Button, QColor(53, 53, 53))
    palette.setColor(QPalette.ColorRole.ButtonText, Qt.GlobalColor.white)
    palette.setColor(QPalette.ColorRole.BrightText, Qt.GlobalColor.red)
    palette.setColor(QPalette.ColorRole.Link, QColor(42, 130, 218))
    palette.setColor(QPalette.ColorRole.Highlight, QColor(42, 130, 218))
    palette.setColor(QPalette.ColorRole.HighlightedText, Qt.GlobalColor.black)
    
    # Set the palette
    widget.setPalette(palette)
    
    # Apply to all children
    for child in widget.findChildren(QApplication):
        child.setPalette(palette)
        
    # Set stylesheet
    widget.setStyleSheet("""
        QToolTip { 
            color: #ffffff; 
            background-color: #2a82da; 
            border: 1px solid white; 
        }
        
        QTabWidget::pane {
            border: 1px solid #444;
            top: -1px;
        }
        
        QTabBar::tab {
            background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                      stop: 0 #555, stop: 0.4 #444,
                                      stop: 0.5 #333, stop: 1.0 #222);
            color: #ffffff;
            padding: 5px;
            border: 1px solid #333;
            border-bottom-color: #444;
            border-top-left-radius: 4px;
            border-top-right-radius: 4px;
        }
        
        QTabBar::tab:selected, QTabBar::tab:hover {
            background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                      stop: 0 #777, stop: 0.4 #666,
                                      stop: 0.5 #555, stop: 1.0 #444);
        }
        
        QTabBar::tab:selected {
            border-color: #9B9B9B;
            border-bottom-color: #444;
        }
        
        QTabBar::tab:!selected {
            margin-top: 2px;
        }
    """) 