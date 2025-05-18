from PyQt5.QtWidgets import QWidget, QLabel, QHBoxLayout, QPushButton, QStyle
from PyQt5.QtGui import QPixmap

class TopPanel(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        self.icon_label = QLabel()
        pixmap = QPixmap('resources/tinCan.png')
        self.icon_label.setPixmap(pixmap)
        layout.addWidget(self.icon_label)

        self.choose_dir_button = QPushButton("Open Project")
        self.choose_dir_button.setIcon(self.style().standardIcon(QStyle.SP_DirIcon))
        layout.addWidget(self.choose_dir_button)

        self.last_projects_button = QPushButton("Last projects")
        layout.addWidget(self.last_projects_button)

        self.settings_button = QPushButton("Settings")
        layout.addWidget(self.settings_button)

        self.project_settings_button = QPushButton("Project settings")
        layout.addWidget(self.project_settings_button)

        self.label = QLabel("Project directory:")
        layout.addWidget(self.label)

        self.setLayout(layout)

    def update_directory(self, directory):
        self.label.setText(f"Project directory: {directory}")
