import os
import json
from PyQt5.QtWidgets import QWidget, QTreeView, QVBoxLayout, QPushButton, QFileSystemModel, QFileDialog
from PyQt5.QtCore import QDir, Qt

# Path to the settings JSON file
SETTINGS_FILE = 'settings/settings.json'

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
        self.tree_view.setModel(self.file_system_model)  # Set the model first

        # Load the last project directory or default to the user's home directory
        last_project_dir = self.load_last_project_directory()

        # Set the root path in the file system model
        self.file_system_model.setRootPath(last_project_dir)
        # Set the root index in the tree view using the file system model
        self.tree_view.setRootIndex(self.file_system_model.index(last_project_dir))

        # Hide unwanted columns: Size (1), Type (2), and Last Modified (3)
        self.tree_view.hideColumn(1)  # Hide the Size column
        self.tree_view.hideColumn(2)  # Hide the Type column
        self.tree_view.hideColumn(3)  # Hide the Last Modified column

        # Add the button and tree view to the layout
        main_layout.addWidget(self.choose_dir_button)
        main_layout.addWidget(self.tree_view)

        # Set the layout for this widget
        self.setLayout(main_layout)

    def choose_directory(self):
        """Opens a dialog to choose a project directory and saves it to the settings file."""
        selected_dir = QFileDialog.getExistingDirectory(self, "Choose Project Directory", os.path.expanduser('~'))

        # If the user selected a directory, update the root path of the tree view and save it to settings
        if selected_dir:
            # Set the root path in the file system model first
            self.file_system_model.setRootPath(selected_dir)
            # Then update the root index in the tree view
            self.tree_view.setRootIndex(self.file_system_model.index(selected_dir))
            # Save the selected directory
            self.save_last_project_directory(selected_dir)

    def load_last_project_directory(self):
        """Loads the last project directory from the settings file or defaults to home directory."""
        home_directory = os.path.expanduser('~')  # Fallback to the user's home directory

        if os.path.exists(SETTINGS_FILE):
            try:
                with open(SETTINGS_FILE, 'r') as f:
                    settings = json.load(f)
                    # Return last_project_dir if it exists, otherwise return home directory
                    return settings.get('last_project_dir', home_directory)
            except (json.JSONDecodeError, IOError):
                # If the file is corrupted or cannot be read, fallback to home directory
                pass
        
        return home_directory

    def save_last_project_directory(self, directory):
        """Saves the selected directory to the settings file."""
        os.makedirs(os.path.dirname(SETTINGS_FILE), exist_ok=True)
        settings = {'last_project_dir': directory}
        with open(SETTINGS_FILE, 'w') as f:
            json.dump(settings, f)

    # Example function to retrieve the selected files (checked files)
    def get_checked_files(self):
        return [file_path for file_path, checked in self.file_system_model.checked_files.items() if checked]


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
