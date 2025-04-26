from PyQt5.QtWidgets import QDialog, QVBoxLayout, QTabWidget, QWidget, QGroupBox, QFormLayout, QLineEdit, QLabel, QDialogButtonBox, QMessageBox, QPushButton, QHBoxLayout
from PyQt5.QtCore import Qt
import os
import json

class SettingsDialog(QDialog):
    def __init__(self, parent=None, model=None):
        super().__init__(parent)
        self.model = model
        self.setWindowTitle("Settings")
        self.resize(400, 300)
        self.setSizeGripEnabled(True)
        self.settings_file = os.path.join(os.path.dirname(__file__), '..', '..', 'settings', 'key.json')
        self.keys = self.load_keys()
        self.init_ui()

    def load_keys(self):
        if os.path.exists(self.settings_file):
            try:
                with open(self.settings_file, 'r') as f:
                    return json.load(f)
            except Exception:
                pass
        return {"api_key": "", "deepseek_api_key": ""}

    def init_ui(self):
        layout = QVBoxLayout(self)
        self.tab_widget = QTabWidget(self)

        # Models Tab
        models_tab = QWidget()
        models_layout = QVBoxLayout()

        # OpenAI GroupBox (renamed from ChatGPT)
        self.chatgpt_group = QGroupBox("OpenAI")
        chatgpt_layout = QFormLayout()
        self.chatgpt_key_edit = QLineEdit()
        self.chatgpt_key_edit.setText(self.keys.get("api_key", ""))
        chatgpt_layout.addRow("API Key:", self.chatgpt_key_edit)
        self.delete_button = QPushButton("Delete all server files")
        self.delete_button.clicked.connect(self.on_delete_all_server_files)
        chatgpt_layout.addRow(self.delete_button)
        self.chatgpt_group.setLayout(chatgpt_layout)
        models_layout.addWidget(self.chatgpt_group)

        # DeepSeek GroupBox
        self.deepseek_group = QGroupBox("DeepSeek")
        deepseek_layout = QFormLayout()
        self.deepseek_key_edit = QLineEdit()
        self.deepseek_key_edit.setText(self.keys.get("deepseek_api_key", ""))
        deepseek_layout.addRow("API Key:", self.deepseek_key_edit)
        self.deepseek_group.setLayout(deepseek_layout)
        models_layout.addWidget(self.deepseek_group)

        # Ollama GroupBox
        self.ollama_group = QGroupBox("Ollama")
        ollama_layout = QVBoxLayout()
        ollama_label = QLabel("No API key required.")
        ollama_layout.addWidget(ollama_label)
        self.ollama_group.setLayout(ollama_layout)
        models_layout.addWidget(self.ollama_group)

        # Removed debug output field

        models_tab.setLayout(models_layout)
        self.tab_widget.addTab(models_tab, "Models")
        layout.addWidget(self.tab_widget)

        self.button_box = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        self.button_box.accepted.connect(self.save_settings)
        self.button_box.rejected.connect(self.reject)
        layout.addWidget(self.button_box)
        
    def save_settings(self):
        self.keys["api_key"] = self.chatgpt_key_edit.text()
        self.keys["deepseek_api_key"] = self.deepseek_key_edit.text()
        os.makedirs(os.path.dirname(self.settings_file), exist_ok=True)
        with open(self.settings_file, 'w') as f:
            json.dump(self.keys, f, indent=4)
        self.accept()

    def on_delete_all_server_files(self):
        reply = QMessageBox.question(self, "Confirm Deletion", "Are you sure you want to delete all server files?", QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            owner = self.parent().window()
            model = self.model
            if model is None and hasattr(owner, "model"):
                model = owner.model
            if model is not None:
                if hasattr(model.getCurrentModel().provider, "delete_all_server_files"):
                    model_context = {
                        "project_dir": model.project_dir,
                        "chosen_files": model.chosen_files,
                        "modelName": model.getCurrentModel().modelName,
                        "status_changed": lambda msg: self.model.response_generated.emit("Status: " + msg),
                        "response_generated": lambda msg: self.model.response_generated.emit(msg)
                    }
                    model.getCurrentModel().provider.delete_all_server_files(model_context)
                else:
                    self.model.response_generated.emit("Delete all server files not supported for current model.")
            else:
                self.model.response_generated.emit("No model found.")
        else:
            self.model.response_generated.emit("Deletion canceled.")
