import os
from PyQt5.QtWidgets import QWidget, QTreeView, QVBoxLayout, QFileSystemModel
from PyQt5.QtCore import QDir

class FilesPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        # Create layout for the left panel
        layout = QVBoxLayout()

        # Create the tree view for displaying the directory structure
        self.tree_view = QTreeView()

        # Set up the file system model to display the directory tree
        self.file_system_model = QFileSystemModel()
        self.file_system_model.setRootPath(QDir.rootPath())  # Set the root path to the root directory

        # Set the file system model on the tree view
        self.tree_view.setModel(self.file_system_model)

        # Optionally set a starting directory (e.g., user's home directory)
        home_directory = os.path.expanduser('~')
        self.tree_view.setRootIndex(self.file_system_model.index(home_directory))

        # Hide unwanted columns: Size (1), Type (2), and Last Modified (3)
        self.tree_view.hideColumn(1)  # Hide the Size column
        self.tree_view.hideColumn(2)  # Hide the Type column
        self.tree_view.hideColumn(3)  # Hide the Last Modified column

        # Add the tree view to the layout
        layout.addWidget(self.tree_view)

        # Set the layout for this widget
        self.setLayout(layout)

