from PyQt5.QtWidgets import QDialog, QVBoxLayout, QPushButton, QLabel
from PyQt5.QtCore import pyqtSignal

class ProjectsHistoryWindow(QDialog):
    project_selected = pyqtSignal(str)

    def __init__(self, history_model):
        super().__init__()
        self.setWindowTitle("Last opened projects")
        self.history_model = history_model
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)

        last_projects = self.history_model.get_last_projects() if self.history_model else []
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
