from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton

class ProjectMetaSettingsDialog(QDialog):
    def __init__(self, project_meta, parent=None):
        super().__init__(parent)
        self.project_meta = project_meta
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Project Meta Settings")
        layout = QVBoxLayout()

        self.label = QLabel("Index extensions (comma-separated):")
        layout.addWidget(self.label)

        self.line_edit = QLineEdit()
        layout.addWidget(self.line_edit)

        button_layout = QHBoxLayout()
        self.save_button = QPushButton("Save")
        self.load_button = QPushButton("Load")
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.load_button)
        layout.addLayout(button_layout)

        self.setLayout(layout)

        self.save_button.clicked.connect(self.save_settings)
        self.load_button.clicked.connect(self.load_settings)

    def save_settings(self):
        text = self.line_edit.text()
        index_extensions = [ext.strip() for ext in text.split(",") if ext.strip()]
        print(f"\n[GUI] Saving index extensions: {index_extensions}")
        self.project_meta.save_settings(index_extensions)
        print("[GUI] Settings saved successfully")

    def load_settings(self):
        print("\n[GUI] Loading settings")
        index_extensions = self.project_meta.load_settings()
        print(f"[GUI] Retrieved settings: {index_extensions}")
        self.line_edit.setText(", ".join(index_extensions))
        print("[GUI] Settings loaded into UI")
