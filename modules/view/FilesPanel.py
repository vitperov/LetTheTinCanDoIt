import os
import json
from PyQt5.QtWidgets import QWidget, QTreeView, QVBoxLayout, QPushButton, QFileSystemModel, QFileDialog, QHBoxLayout, QLabel
from PyQt5.QtCore import QDir, Qt, pyqtSignal
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtWidgets import QStyle

SETTINGS_FILE = 'settings/settings.json'

class FilesPanel(QWidget):
    proj_dir_changed = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.project_dir = self.load_last_project_directory()
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout()
        button_layout = QHBoxLayout()

        self.icon_label = QLabel()
        pixmap = QPixmap('resources/tinCan.png')
        self.icon_label.setPixmap(pixmap)

        self.choose_dir_button = QPushButton("Open Project")
        self.choose_dir_button.setIcon(self.style().standardIcon(QStyle.SP_DirIcon))
        self.choose_dir_button.clicked.connect(self.choose_directory)

        button_layout.addWidget(self.icon_label)
        button_layout.addWidget(self.choose_dir_button)

        self.tree_view = QTreeView()
        self.file_system_model = CustomFileSystemModel()
        self.tree_view.setModel(self.file_system_model)
        self.file_system_model.setRootPath(self.project_dir)
        self.tree_view.setRootIndex(self.file_system_model.index(self.project_dir))
        self.tree_view.hideColumn(1)
        self.tree_view.hideColumn(2)
        self.tree_view.hideColumn(3)

        main_layout.addLayout(button_layout)
        main_layout.addWidget(self.tree_view)
        self.setLayout(main_layout)

    def choose_directory(self):
        selected_dir = QFileDialog.getExistingDirectory(self, "Choose Project Directory", self.project_dir)
        if selected_dir:
            self.file_system_model.setRootPath(selected_dir)
            self.tree_view.setRootIndex(self.file_system_model.index(selected_dir))
            self.save_last_project_directory(selected_dir)
            self.project_dir = selected_dir
            self.proj_dir_changed.emit(selected_dir)
            self.clear_checked_files()  # Clear the checked files when changing directory

    def load_last_project_directory(self):
        home_directory = os.path.expanduser('~')

        if os.path.exists(SETTINGS_FILE):
            try:
                with open(SETTINGS_FILE, 'r') as f:
                    settings = json.load(f)
                    return settings.get('last_project_dir', home_directory)
            except (json.JSONDecodeError, IOError):
                pass
        
        return home_directory

    def save_last_project_directory(self, directory):
        os.makedirs(os.path.dirname(SETTINGS_FILE), exist_ok=True)
        settings = {'last_project_dir': directory}
        with open(SETTINGS_FILE, 'w') as f:
            json.dump(settings, f)

    def get_checked_files(self):
        relative_files = [os.path.relpath(file_path, self.project_dir) for file_path, checked in self.file_system_model.checked_files.items() if checked]
        return self.project_dir, relative_files

    def clear_checked_files(self):
        self.file_system_model.clear_checked_files()

class CustomFileSystemModel(QFileSystemModel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.checked_files = {}

    def clear_checked_files(self):  # Method to clear checked files
        self.checked_files = {}

    def flags(self, index):
        default_flags = super().flags(index)
        if not self.isDir(index):
            return default_flags | Qt.ItemIsUserCheckable | Qt.ItemIsEnabled
        else:
            return default_flags

    def data(self, index, role):
        if role == Qt.CheckStateRole and not self.isDir(index):
            file_path = self.filePath(index)
            return Qt.Checked if self.checked_files.get(file_path, False) else Qt.Unchecked
        return super().data(index, role)

    def setData(self, index, value, role):
        if role == Qt.CheckStateRole and not self.isDir(index):
            file_path = self.filePath(index)
            self.checked_files[file_path] = (value == Qt.Checked)
            self.dataChanged.emit(index, index)
            return True
        return super().setData(index, value, role)
