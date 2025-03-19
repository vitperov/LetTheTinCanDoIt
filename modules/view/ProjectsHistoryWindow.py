from PyQt5.QtWidgets import QDialog, QVBoxLayout, QPushButton, QLabel
from PyQt5.QtCore import pyqtSignal
import json
import os

SETTINGS_FILE = 'settings/settings.json'

class ProjectsHistoryWindow(QDialog):
    project_selected = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Last opened projects")
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)

        last_projects = []
        if os.path.exists(SETTINGS_FILE):
            try:
                with open(SETTINGS_FILE, 'r') as f:
                    settings = json.load(f)
                    last_projects = settings.get('lastProjects', [])
            except:
                pass

        if not last_projects:
            label = QLabel("Projects history is empty")
            layout.addWidget(label)
        else:
            for project_path in last_projects:
                btn = QPushButton(project_path)
                btn.clicked.connect(lambda checked, path=project_path: self.on_project_selected(path))
                layout.addWidget(btn)

    def on_project_selected(self, project_path):
        self.project_selected.emit(project_path)
        self.close()
