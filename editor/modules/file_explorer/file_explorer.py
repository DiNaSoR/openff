import os
from PyQt6.QtWidgets import (QTreeView, QFileSystemModel, QMenu, QMessageBox,
                           QInputDialog, QFileDialog)
from PyQt6.QtCore import Qt, QDir, pyqtSignal, QModelIndex

class FileExplorer(QTreeView):
    """File explorer widget for navigating project files."""
    
    # Signal emitted when a file is selected
    file_selected = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Set up the model
        self.model = QFileSystemModel()
        self.model.setRootPath(QDir.rootPath())
        self.setModel(self.model)
        
        # Hide columns except for the name
        self.setColumnHidden(1, True)  # Size
        self.setColumnHidden(2, True)  # Type
        self.setColumnHidden(3, True)  # Modified
        
        # Set the root path to the current directory
        self.root_path = os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))
        self.setRootIndex(self.model.index(self.root_path))
        
        # Set up the view
        self.setAnimated(False)
        self.setIndentation(20)
        self.setSortingEnabled(True)
        self.setEditTriggers(QTreeView.EditTrigger.NoEditTriggers)
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)
        
        # Connect signals
        self.doubleClicked.connect(self.on_double_click)
        
    def on_double_click(self, index):
        """Handle double-click on an item."""
        # Get the file path
        file_path = self.model.filePath(index)
        
        # Check if it's a file
        if os.path.isfile(file_path):
            # Emit the signal
            self.file_selected.emit(file_path)
            
    def show_context_menu(self, position):
        """Show the context menu."""
        # Get the index at the position
        index = self.indexAt(position)
        
        # Check if the index is valid
        if not index.isValid():
            return
            
        # Get the file path
        file_path = self.model.filePath(index)
        
        # Create the menu
        menu = QMenu()
        
        # Add actions
        if os.path.isdir(file_path):
            # Directory actions
            new_file_action = menu.addAction("New File")
            new_dir_action = menu.addAction("New Directory")
            menu.addSeparator()
            
        open_action = menu.addAction("Open")
        menu.addSeparator()
        rename_action = menu.addAction("Rename")
        delete_action = menu.addAction("Delete")
        
        # Show the menu and get the selected action
        action = menu.exec(self.viewport().mapToGlobal(position))
        
        # Handle the action
        if action == open_action:
            self.on_double_click(index)
        elif os.path.isdir(file_path) and action == new_file_action:
            self.create_new_file(file_path)
        elif os.path.isdir(file_path) and action == new_dir_action:
            self.create_new_directory(file_path)
        elif action == rename_action:
            self.rename_item(index)
        elif action == delete_action:
            self.delete_item(index)
            
    def create_new_file(self, directory):
        """Create a new file in the given directory."""
        # Ask for the file name
        file_name, ok = QInputDialog.getText(
            self, "New File", "Enter file name:"
        )
        
        if ok and file_name:
            # Create the file
            file_path = os.path.join(directory, file_name)
            try:
                with open(file_path, 'w') as f:
                    pass
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Could not create file: {str(e)}")
                
    def create_new_directory(self, directory):
        """Create a new directory in the given directory."""
        # Ask for the directory name
        dir_name, ok = QInputDialog.getText(
            self, "New Directory", "Enter directory name:"
        )
        
        if ok and dir_name:
            # Create the directory
            dir_path = os.path.join(directory, dir_name)
            try:
                os.makedirs(dir_path, exist_ok=True)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Could not create directory: {str(e)}")
                
    def rename_item(self, index):
        """Rename the item at the given index."""
        # Get the file path
        file_path = self.model.filePath(index)
        
        # Ask for the new name
        new_name, ok = QInputDialog.getText(
            self, "Rename", "Enter new name:",
            text=os.path.basename(file_path)
        )
        
        if ok and new_name:
            # Rename the item
            new_path = os.path.join(os.path.dirname(file_path), new_name)
            try:
                os.rename(file_path, new_path)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Could not rename item: {str(e)}")
                
    def delete_item(self, index):
        """Delete the item at the given index."""
        # Get the file path
        file_path = self.model.filePath(index)
        
        # Ask for confirmation
        reply = QMessageBox.question(
            self, "Delete",
            f"Are you sure you want to delete {os.path.basename(file_path)}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                if os.path.isdir(file_path):
                    # Remove the directory
                    import shutil
                    shutil.rmtree(file_path)
                else:
                    # Remove the file
                    os.remove(file_path)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Could not delete item: {str(e)}")
                
    def set_root_path(self, path):
        """Set the root path of the file explorer."""
        self.root_path = path
        self.setRootIndex(self.model.index(path)) 