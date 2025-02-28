from PyQt6.QtGui import QPalette, QColor
from PyQt6.QtCore import Qt

def apply_dark_theme(widget):
    """Apply a dark theme to the given widget and its children."""
    # Create a dark palette
    palette = QPalette()
    
    # Set colors for different roles
    palette.setColor(QPalette.ColorRole.Window, QColor(53, 53, 53))
    palette.setColor(QPalette.ColorRole.WindowText, Qt.GlobalColor.white)
    palette.setColor(QPalette.ColorRole.Base, QColor(35, 35, 35))
    palette.setColor(QPalette.ColorRole.AlternateBase, QColor(53, 53, 53))
    palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(25, 25, 25))
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
    for child in widget.findChildren(object):
        if hasattr(child, 'setPalette'):
            child.setPalette(palette)
            
def apply_light_theme(widget):
    """Apply a light theme to the given widget and its children."""
    # Create a light palette
    palette = QPalette()
    
    # Set colors for different roles
    palette.setColor(QPalette.ColorRole.Window, QColor(240, 240, 240))
    palette.setColor(QPalette.ColorRole.WindowText, Qt.GlobalColor.black)
    palette.setColor(QPalette.ColorRole.Base, QColor(255, 255, 255))
    palette.setColor(QPalette.ColorRole.AlternateBase, QColor(245, 245, 245))
    palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(255, 255, 255))
    palette.setColor(QPalette.ColorRole.ToolTipText, Qt.GlobalColor.black)
    palette.setColor(QPalette.ColorRole.Text, Qt.GlobalColor.black)
    palette.setColor(QPalette.ColorRole.Button, QColor(240, 240, 240))
    palette.setColor(QPalette.ColorRole.ButtonText, Qt.GlobalColor.black)
    palette.setColor(QPalette.ColorRole.BrightText, Qt.GlobalColor.red)
    palette.setColor(QPalette.ColorRole.Link, QColor(0, 0, 255))
    palette.setColor(QPalette.ColorRole.Highlight, QColor(42, 130, 218))
    palette.setColor(QPalette.ColorRole.HighlightedText, Qt.GlobalColor.white)
    
    # Set the palette
    widget.setPalette(palette)
    
    # Apply to all children
    for child in widget.findChildren(object):
        if hasattr(child, 'setPalette'):
            child.setPalette(palette)
            
def get_game_style_sheet():
    """Return a stylesheet for game-specific UI elements."""
    return """
    QTabWidget::pane {
        border: 1px solid #444;
        border-radius: 3px;
        padding: 5px;
    }
    
    QTabBar::tab {
        background-color: #3a3a3a;
        color: #ddd;
        border: 1px solid #444;
        border-bottom: none;
        border-top-left-radius: 4px;
        border-top-right-radius: 4px;
        padding: 5px 10px;
        margin-right: 2px;
    }
    
    QTabBar::tab:selected {
        background-color: #444;
        color: #fff;
    }
    
    QTabBar::tab:hover {
        background-color: #444;
    }
    
    QListWidget {
        background-color: #2a2a2a;
        border: 1px solid #444;
        border-radius: 3px;
    }
    
    QListWidget::item {
        padding: 5px;
        border-bottom: 1px solid #333;
    }
    
    QListWidget::item:selected {
        background-color: #3a6ea5;
        color: white;
    }
    
    QGroupBox {
        border: 1px solid #444;
        border-radius: 3px;
        margin-top: 1ex;
        padding-top: 10px;
    }
    
    QGroupBox::title {
        subcontrol-origin: margin;
        subcontrol-position: top center;
        padding: 0 5px;
        color: #ddd;
    }
    
    QPushButton {
        background-color: #3a3a3a;
        color: #ddd;
        border: 1px solid #555;
        border-radius: 3px;
        padding: 5px 10px;
    }
    
    QPushButton:hover {
        background-color: #444;
        border: 1px solid #666;
    }
    
    QPushButton:pressed {
        background-color: #2a2a2a;
    }
    
    QLineEdit, QTextEdit, QPlainTextEdit {
        background-color: #2a2a2a;
        color: #ddd;
        border: 1px solid #444;
        border-radius: 3px;
        padding: 3px;
    }
    
    QComboBox {
        background-color: #3a3a3a;
        color: #ddd;
        border: 1px solid #444;
        border-radius: 3px;
        padding: 3px 5px;
    }
    
    QComboBox::drop-down {
        subcontrol-origin: padding;
        subcontrol-position: top right;
        width: 15px;
        border-left: 1px solid #444;
    }
    
    QComboBox QAbstractItemView {
        background-color: #2a2a2a;
        color: #ddd;
        selection-background-color: #3a6ea5;
        selection-color: white;
    }
    
    QSpinBox, QDoubleSpinBox {
        background-color: #2a2a2a;
        color: #ddd;
        border: 1px solid #444;
        border-radius: 3px;
        padding: 3px;
    }
    
    QLabel {
        color: #ddd;
    }
    
    QToolBar {
        background-color: #3a3a3a;
        border: 1px solid #444;
        spacing: 3px;
    }
    
    QToolButton {
        background-color: transparent;
        border: 1px solid transparent;
        border-radius: 3px;
        padding: 3px;
    }
    
    QToolButton:hover {
        background-color: #444;
        border: 1px solid #555;
    }
    
    QToolButton:pressed {
        background-color: #2a2a2a;
    }
    
    QStatusBar {
        background-color: #3a3a3a;
        color: #ddd;
    }
    """ 