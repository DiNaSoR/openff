"""
File Explorer Widget for the OpenFF Game Editor.

This module provides a widget for exploring the file system.
"""

import os
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QTreeView, QPushButton, 
                           QFileDialog, QLabel, QHBoxLayout, QMenu, QMessageBox,
                           QInputDialog)
from PyQt6.QtCore import Qt, QDir, pyqtSignal, QModelIndex
from PyQt6.QtGui import QFileSystemModel

class FileExplorerWidget(QWidget):
    """Widget for exploring the file system."""
    
    # Signal emitted when a file is selected
    fileSelected = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.current_dir = ""
        self.init_ui()
        
    def init_ui(self):
        """Initialize the user interface."""
        # Main layout
        main_layout = QVBoxLayout(self)
        
        # Add controls at the top
        controls_layout = QHBoxLayout()
        
        # Add label for current directory
        self.dir_label = QLabel("No directory selected")
        self.dir_label.setWordWrap(True)
        controls_layout.addWidget(self.dir_label)
        
        # Add button to select directory
        select_dir_button = QPushButton("Select Directory")
        select_dir_button.clicked.connect(self.select_directory)
        controls_layout.addWidget(select_dir_button)
        
        main_layout.addLayout(controls_layout)
        
        # Add file system tree view
        self.model = QFileSystemModel()
        self.model.setReadOnly(True)
        
        self.tree_view = QTreeView()
        self.tree_view.setModel(self.model)
        self.tree_view.setSortingEnabled(True)
        self.tree_view.sortByColumn(0, Qt.SortOrder.AscendingOrder)
        self.tree_view.setAnimated(True)
        self.tree_view.setIndentation(20)
        self.tree_view.setColumnWidth(0, 250)
        
        # Hide unnecessary columns
        for i in range(1, self.model.columnCount()):
            self.tree_view.hideColumn(i)
        
        # Connect signals
        self.tree_view.clicked.connect(self.on_item_clicked)
        
        main_layout.addWidget(self.tree_view)
        
        # Set initial directory
        self.set_directory(os.getcwd())
        
    def select_directory(self):
        """Open a dialog to select a directory."""
        directory = QFileDialog.getExistingDirectory(
            self, 
            "Select Directory",
            self.current_dir if self.current_dir else os.getcwd()
        )
        
        if directory:
            self.set_directory(directory)
            
    def set_directory(self, directory):
        """Set the current directory for the file explorer."""
        if not os.path.isdir(directory):
            return
            
        self.current_dir = directory
        self.dir_label.setText(directory)
        
        # Set the root path for the model
        self.model.setRootPath(directory)
        self.tree_view.setRootIndex(self.model.index(directory))
        
    def on_item_clicked(self, index):
        """Handle when an item in the tree view is clicked."""
        # Get the file path
        file_path = self.model.filePath(index)
        
        # Emit the signal if it's a file
        if os.path.isfile(file_path):
            self.fileSelected.emit(file_path)
            
    def refresh(self):
        """Refresh the file explorer view."""
        if self.current_dir:
            # Re-set the current directory to refresh the view
            self.set_directory(self.current_dir)
        else:
            # Set the current working directory if no directory is selected
            self.set_directory(os.getcwd())

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