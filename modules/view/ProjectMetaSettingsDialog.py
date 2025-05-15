from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QGroupBox, QLabel, QLineEdit, QPushButton, QInputDialog, QComboBox

class ProjectMetaSettingsDialog(QDialog):
    def __init__(self, project_meta, parent=None):
        super().__init__(parent)
        self.project_meta = project_meta
        self.init_ui()
        self.load_settings()

    def init_ui(self):
        self.setWindowTitle("Project Meta Settings")
        main_layout = QVBoxLayout()

        settings_group = QGroupBox("Settings")
        settings_layout = QVBoxLayout()
        self.label = QLabel("Index extensions (comma-separated):")
        settings_layout.addWidget(self.label)
        self.line_edit = QLineEdit()
        settings_layout.addWidget(self.line_edit)
        self.dir_label = QLabel("Index directories (comma-separated):")
        settings_layout.addWidget(self.dir_label)
        self.dir_line_edit = QLineEdit()
        settings_layout.addWidget(self.dir_line_edit)
        self.model_label = QLabel("Indexing model:")
        settings_layout.addWidget(self.model_label)
        self.model_combo = QComboBox()
        self.model_combo.addItems(self.project_meta.available_models)
        settings_layout.addWidget(self.model_combo)
        self.save_button = QPushButton("Save")
        settings_layout.addWidget(self.save_button)
        settings_group.setLayout(settings_layout)
        main_layout.addWidget(settings_group)

        actions_group = QGroupBox("Actions")
        actions_layout = QHBoxLayout()
        self.stats_button = QPushButton("Stats")
        actions_layout.addWidget(self.stats_button)
        self.index_all_button = QPushButton("Index all")
        actions_layout.addWidget(self.index_all_button)
        self.index_one_button = QPushButton("Index one")
        actions_layout.addWidget(self.index_one_button)
        actions_group.setLayout(actions_layout)
        main_layout.addWidget(actions_group)

        self.setLayout(main_layout)

        self.save_button.clicked.connect(self.save_settings)
        self.stats_button.clicked.connect(self.run_stats)
        self.index_all_button.clicked.connect(self.run_index_all)
        self.index_one_button.clicked.connect(self.run_index_one)

    def save_settings(self):
        ext_text = self.line_edit.text()
        index_extensions = [ext.strip() for ext in ext_text.split(",") if ext.strip()]
        dir_text = self.dir_line_edit.text()
        index_directories = [d.strip() for d in dir_text.split(",") if d.strip()]
        model = self.model_combo.currentText()
        print(f"\n[GUI] Saving index extensions: {index_extensions}")
        print(f"[GUI] Saving index directories: {index_directories}")
        print(f"[GUI] Saving indexing model: {model}")
        self.project_meta.save_settings(index_extensions, index_directories, model)
        print("[GUI] Settings saved successfully")

    def load_settings(self):
        print("\n[GUI] Loading settings")
        index_extensions, index_directories = self.project_meta.load_settings()
        print(f"[GUI] Retrieved extensions: {index_extensions}")
        print(f"[GUI] Retrieved directories: {index_directories}")
        self.line_edit.setText(", ".join(index_extensions))
        self.dir_line_edit.setText(", ".join(index_directories))
        model = getattr(self.project_meta, 'indexing_model', None)
        print(f"[GUI] Retrieved indexing model: {model}")
        if model:
            idx = self.model_combo.findText(model)
            if idx >= 0:
                self.model_combo.setCurrentIndex(idx)
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
