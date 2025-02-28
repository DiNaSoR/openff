import os
from PyQt6.QtWidgets import QTreeView, QMenu, QMessageBox, QInputDialog
from PyQt6.QtCore import Qt, QDir, pyqtSignal, QModelIndex
from PyQt6.QtGui import QStandardItemModel, QStandardItem, QAction

class FileExplorer(QTreeView):
    """File explorer widget for navigating project files."""
    
    # Signal emitted when a file is clicked
    file_clicked = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)
        self.doubleClicked.connect(self.file_double_clicked)
        
        # Set up the model
        self.model = QStandardItemModel()
        self.model.setHorizontalHeaderLabels(["Project Files"])
        self.setModel(self.model)
        
        # Set up the root directory
        self.root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
        self.populate_file_tree()
        
        # Expand the root item
        self.expand(self.model.index(0, 0))
        
    def populate_file_tree(self):
        """Populate the file tree with files from the project directory."""
        self.model.clear()
        self.model.setHorizontalHeaderLabels(["Project Files"])
        
        # Create the root item
        root_item = QStandardItem(os.path.basename(self.root_dir))
        root_item.setData(self.root_dir, Qt.ItemDataRole.UserRole)
        self.model.appendRow(root_item)
        
        # Add files to the tree
        self.add_files_to_tree(self.root_dir, root_item)
        
    def add_files_to_tree(self, path, parent_item):
        """Add files and directories to the tree recursively."""
        try:
            # Get all files and directories in the path
            items = os.listdir(path)
            
            # Sort items (directories first, then files)
            items.sort(key=lambda x: (not os.path.isdir(os.path.join(path, x)), x.lower()))
            
            for item_name in items:
                # Skip hidden files and directories
                if item_name.startswith('.'):
                    continue
                    
                item_path = os.path.join(path, item_name)
                item = QStandardItem(item_name)
                item.setData(item_path, Qt.ItemDataRole.UserRole)
                
                parent_item.appendRow(item)
                
                # If it's a directory, add its contents recursively
                if os.path.isdir(item_path):
                    self.add_files_to_tree(item_path, item)
        except Exception as e:
            print(f"Error populating file tree: {str(e)}")
            
    def refresh_file_tree(self):
        """Refresh the file tree."""
        self.populate_file_tree()
        self.expand(self.model.index(0, 0))
        
    def file_double_clicked(self, index):
        """Handle double-click on a file in the tree."""
        item = self.model.itemFromIndex(index)
        if not item:
            return
            
        path = item.data(Qt.ItemDataRole.UserRole)
        if os.path.isfile(path):
            self.file_clicked.emit(path)
            
    def show_context_menu(self, position):
        """Show context menu for the file tree."""
        index = self.indexAt(position)
        if not index.isValid():
            return
            
        item = self.model.itemFromIndex(index)
        path = item.data(Qt.ItemDataRole.UserRole)
        
        menu = QMenu()
        
        if os.path.isdir(path):
            # Directory context menu
            new_file_action = QAction("New File", self)
            new_file_action.triggered.connect(lambda: self.new_file_in_dir(path))
            menu.addAction(new_file_action)
            
            new_dir_action = QAction("New Directory", self)
            new_dir_action.triggered.connect(lambda: self.new_directory_in_dir(path))
            menu.addAction(new_dir_action)
            
            menu.addSeparator()
            
        if os.path.isfile(path):
            # File context menu
            open_action = QAction("Open", self)
            open_action.triggered.connect(lambda: self.file_clicked.emit(path))
            menu.addAction(open_action)
            
            menu.addSeparator()
            
            delete_action = QAction("Delete", self)
            delete_action.triggered.connect(lambda: self.delete_file(path))
            menu.addAction(delete_action)
            
        refresh_action = QAction("Refresh", self)
        refresh_action.triggered.connect(self.refresh_file_tree)
        menu.addAction(refresh_action)
        
        menu.exec(self.viewport().mapToGlobal(position))
        
    def new_file_in_dir(self, directory):
        """Create a new file in the specified directory."""
        file_name, ok = QInputDialog.getText(
            self, 
            "New File", 
            "Enter file name:"
        )
        
        if ok and file_name:
            file_path = os.path.join(directory, file_name)
            
            # Check if file already exists
            if os.path.exists(file_path):
                QMessageBox.warning(
                    self, 
                    "File Exists", 
                    f"A file named '{file_name}' already exists in this directory."
                )
                return
                
            try:
                # Create the file
                with open(file_path, 'w') as f:
                    f.write("")
                    
                # Refresh the file tree
                self.refresh_file_tree()
                
                # Open the new file
                self.file_clicked.emit(file_path)
                
            except Exception as e:
                QMessageBox.critical(
                    self, 
                    "Error", 
                    f"Failed to create file:\n{str(e)}"
                )
                
    def new_directory_in_dir(self, directory):
        """Create a new directory in the specified directory."""
        dir_name, ok = QInputDialog.getText(
            self, 
            "New Directory", 
            "Enter directory name:"
        )
        
        if ok and dir_name:
            dir_path = os.path.join(directory, dir_name)
            
            # Check if directory already exists
            if os.path.exists(dir_path):
                QMessageBox.warning(
                    self, 
                    "Directory Exists", 
                    f"A directory named '{dir_name}' already exists in this location."
                )
                return
                
            try:
                # Create the directory
                os.makedirs(dir_path)
                
                # Refresh the file tree
                self.refresh_file_tree()
                
            except Exception as e:
                QMessageBox.critical(
                    self, 
                    "Error", 
                    f"Failed to create directory:\n{str(e)}"
                )
                
    def delete_file(self, file_path):
        """Delete the specified file."""
        # Confirm deletion
        reply = QMessageBox.question(
            self, 
            "Confirm Delete", 
            f"Are you sure you want to delete '{os.path.basename(file_path)}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                os.remove(file_path)
                self.refresh_file_tree()
            except Exception as e:
                QMessageBox.critical(
                    self, 
                    "Error", 
                    f"Failed to delete file:\n{str(e)}"
                ) 