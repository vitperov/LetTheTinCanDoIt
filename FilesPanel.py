import os
from PyQt5.QtWidgets import QWidget, QTreeView, QVBoxLayout, QPushButton, QFileSystemModel, QFileDialog, QHBoxLayout
from PyQt5.QtCore import QDir, Qt

class CustomFileSystemModel(QFileSystemModel):
    def __init__(self, parent=None):
        super().__init__(parent)
        # Store the checked state of files
        self.checked_files = {}

    # Override the flags method to add checkable state only for files
    def flags(self, index):
        default_flags = super().flags(index)
        if not self.isDir(index):
            return default_flags | Qt.ItemIsUserCheckable | Qt.ItemIsEnabled
        else:
            return default_flags

    # Override the data method to handle the check state for files
    def data(self, index, role):
        if role == Qt.CheckStateRole and not self.isDir(index):
            file_path = self.filePath(index)
            return Qt.Checked if self.checked_files.get(file_path, False) else Qt.Unchecked
        return super().data(index, role)

    # Override the setData method to update the check state when toggled
    def setData(self, index, value, role):
        if role == Qt.CheckStateRole and not self.isDir(index):
            file_path = self.filePath(index)
            self.checked_files[file_path] = (value == Qt.Checked)
            self.dataChanged.emit(index, index)
            return True
        return super().setData(index, value, role)


class FilesPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        # Create the main layout for the left panel
        main_layout = QVBoxLayout()

        # Create the "Choose Project Directory" button
        self.choose_dir_button = QPushButton('Choose Project Directory')
        self.choose_dir_button.clicked.connect(self.choose_directory)

        # Create the tree view for displaying the directory structure
        self.tree_view = QTreeView()

        # Set up the custom file system model to display the directory tree with checkboxes
        self.file_system_model = CustomFileSystemModel()
        self.file_system_model.setRootPath(QDir.rootPath())

        # Set the file system model on the tree view
        self.tree_view.setModel(self.file_system_model)

        # Optionally set a starting directory (e.g., user's home directory)
        home_directory = os.path.expanduser('~')
        self.tree_view.setRootIndex(self.file_system_model.index(home_directory))

        # Hide unwanted columns: Size (1), Type (2), and Last Modified (3)
        self.tree_view.hideColumn(1)  # Hide the Size column
        self.tree_view.hideColumn(2)  # Hide the Type column
        self.tree_view.hideColumn(3)  # Hide the Last Modified column

        # Add the button and tree view to the layout
        main_layout.addWidget(self.choose_dir_button)  # Add the button above the tree view
        main_layout.addWidget(self.tree_view)

        # Set the layout for this widget
        self.setLayout(main_layout)

    def choose_directory(self):
        # Open a QFileDialog to select a directory
        selected_dir = QFileDialog.getExistingDirectory(self, "Choose Project Directory", os.path.expanduser('~'))

        # If the user selected a directory, update the root path of the tree view
        if selected_dir:
            self.tree_view.setRootIndex(self.file_system_model.index(selected_dir))
            self.file_system_model.setRootPath(selected_dir)

    # Example function to retrieve the selected files (checked files)
    def get_checked_files(self):
        return [file_path for file_path, checked in self.file_system_model.checked_files.items() if checked]
