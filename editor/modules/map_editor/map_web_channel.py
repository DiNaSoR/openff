"""
Web channel for communication between PyQt and the PixiJS map editor.
"""

from PyQt6.QtCore import QObject, pyqtSlot, pyqtSignal
import json

class MapWebChannel(QObject):
    """Handles communication between PyQt and the PixiJS map editor."""
    
    # Signals for map updates
    tileUpdated = pyqtSignal(int, int, int)  # x, y, type
    
    def __init__(self, parent=None):
        super().__init__(parent)
    
    @pyqtSlot(str, str, str)
    def handleMessage(self, action, data, callback):
        """Handle messages from JavaScript."""
        try:
            data_obj = json.loads(data)
            
            if action == "tileClicked":
                x = data_obj.get("x", 0)
                y = data_obj.get("y", 0)
                tile_type = data_obj.get("type", 0)
                self.tileUpdated.emit(x, y, tile_type)
                callback("true")
            else:
                callback("false")
        except Exception as e:
            print(f"Error handling message: {str(e)}")
            callback("false")
    
    @pyqtSlot(int, int, int)
    def tileClicked(self, x, y, tile_type):
        """Handle tile click events from JavaScript."""
        self.tileUpdated.emit(x, y, tile_type) 