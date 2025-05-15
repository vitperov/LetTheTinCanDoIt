from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QInputDialog

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

        self.dir_label = QLabel("Index directories (comma-separated):")
        layout.addWidget(self.dir_label)

        self.dir_line_edit = QLineEdit()
        layout.addWidget(self.dir_line_edit)

        button_layout = QHBoxLayout()
        self.save_button = QPushButton("Save")
        self.load_button = QPushButton("Load")
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.load_button)
        layout.addLayout(button_layout)

        actions_layout = QHBoxLayout()
        self.stats_button = QPushButton("Stats")
        self.index_all_button = QPushButton("Index all")
        self.index_one_button = QPushButton("Index one")
        actions_layout.addWidget(self.stats_button)
        actions_layout.addWidget(self.index_all_button)
        actions_layout.addWidget(self.index_one_button)
        layout.addLayout(actions_layout)

        self.setLayout(layout)

        self.save_button.clicked.connect(self.save_settings)
        self.load_button.clicked.connect(self.load_settings)
        self.stats_button.clicked.connect(self.run_stats)
        self.index_all_button.clicked.connect(self.run_index_all)
        self.index_one_button.clicked.connect(self.run_index_one)

    def save_settings(self):
        ext_text = self.line_edit.text()
        index_extensions = [ext.strip() for ext in ext_text.split(",") if ext.strip()]
        dir_text = self.dir_line_edit.text()
        index_directories = [d.strip() for d in dir_text.split(",") if d.strip()]
        print(f"\n[GUI] Saving index extensions: {index_extensions}")
        print(f"[GUI] Saving index directories: {index_directories}")
        self.project_meta.save_settings(index_extensions, index_directories)
        print("[GUI] Settings saved successfully")

    def load_settings(self):
        print("\n[GUI] Loading settings")
        index_extensions, index_directories = self.project_meta.load_settings()
        print(f"[GUI] Retrieved extensions: {index_extensions}")
        print(f"[GUI] Retrieved directories: {index_directories}")
        self.line_edit.setText(", ".join(index_extensions))
        self.dir_line_edit.setText(", ".join(index_directories))
        print("[GUI] Settings loaded into UI")

    def run_stats(self):
        print("\n[GUI] Running stats")
        self.project_meta.stat_descriptions()

    def run_index_all(self):
        print("\n[GUI] Running index all")
        self.project_meta.update_descriptions()
        print("[GUI] Index all completed")

    def run_index_one(self):
        files = self.project_meta.getAll_project_files()
        file, ok = QInputDialog.getItem(self, "Select File", "File:", files, 0, False)
        if ok and file:
            print(f"\n[GUI] Indexing one file: {file}")
            self.project_meta.update_description(file)
            print("[GUI] Index one completed")
