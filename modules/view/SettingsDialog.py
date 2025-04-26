import os
import json
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QTabWidget, QWidget, QGroupBox, QFormLayout, QLineEdit, QLabel, QDialogButtonBox

class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.resize(400, 300)
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

        # ChatGPT GroupBox
        self.chatgpt_group = QGroupBox("ChatGPT")
        chatgpt_layout = QFormLayout()
        self.chatgpt_key_edit = QLineEdit()
        self.chatgpt_key_edit.setText(self.keys.get("api_key", ""))
        chatgpt_layout.addRow("API Key:", self.chatgpt_key_edit)
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
