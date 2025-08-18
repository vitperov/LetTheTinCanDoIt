from PyQt5.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QTabWidget,
    QWidget,
    QGroupBox,
    QFormLayout,
    QLineEdit,
    QLabel,
    QDialogButtonBox,
    QMessageBox,
    QPushButton,
    QHBoxLayout,
    QCheckBox,
)
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
        self.settings_file = os.path.join(
            os.path.dirname(__file__), "..", "..", "settings", "key.json"
        )
        self.keys = self.load_keys()
        self.init_ui()

    # ------------------------------------------------------------------ #
    # Settings helpers
    # ------------------------------------------------------------------ #
    def _default_keys(self):
        """
        Return default *flat* keys structure used internally by the dialog.
        """
        return {
            "api_key": "",
            "deepseek_api_key": "",
            "gemini_api_key": "",
            "openai_hide_models": "",
            "deepseek_hide_models": "",
            "gemini_hide_models": "",
            "ollama_hide_models": "",
            "openai_enabled": True,
            "deepseek_enabled": True,
            "gemini_enabled": True,
            "ollama_enabled": True,
        }

    def _flatten_nested_keys(self, data):
        """
        Convert a *nested* provider-centric structure (the new one used by
        LLMModel) into the *flat* structure that the dialog expects.
        """
        return {
            "api_key": data.get("openai", {}).get("api_key", ""),
            "deepseek_api_key": data.get("deepseek", {}).get("api_key", ""),
            "gemini_api_key": data.get("gemini", {}).get("api_key", ""),
            "openai_hide_models": data.get("openai", {}).get("hide_models", ""),
            "deepseek_hide_models": data.get("deepseek", {}).get("hide_models", ""),
            "gemini_hide_models": data.get("gemini", {}).get("hide_models", ""),
            "ollama_hide_models": data.get("ollama", {}).get("hide_models", ""),
            "openai_enabled": data.get("openai", {}).get("enabled", True),
            "deepseek_enabled": data.get("deepseek", {}).get("enabled", True),
            "gemini_enabled": data.get("gemini", {}).get("enabled", True),
            "ollama_enabled": data.get("ollama", {}).get("enabled", True),
        }

    def load_keys(self):
        """
        Load settings from disk and return them in the *flat* format used by the
        dialog. Both the legacy flat structure and the new nested structure are
        supported.
        """
        if not os.path.exists(self.settings_file):
            return self._default_keys()

        try:
            with open(self.settings_file, "r") as f:
                data = json.load(f)

            # Heuristic: if at least one top-level value is a dict we assume
            # the new nested structure.
            if any(isinstance(v, dict) for v in data.values()):
                return self._flatten_nested_keys(data)

            # Legacy flat structure – just ensure all expected keys exist.
            defaults = self._default_keys()
            defaults.update({k: data.get(k, "") for k in defaults})
            return defaults
        except Exception:
            # In case of corrupted file fall back to defaults.
            return self._default_keys()

    # ------------------------------------------------------------------ #
    # UI
    # ------------------------------------------------------------------ #
    def init_ui(self):
        layout = QVBoxLayout(self)
        self.tab_widget = QTabWidget(self)

        # Models Tab
        models_tab = QWidget()
        models_layout = QVBoxLayout()

        # -------------------- OpenAI -------------------- #
        self.chatgpt_group = QGroupBox("OpenAI")
        chatgpt_layout = QFormLayout()

        self.chatgpt_enabled_checkbox = QCheckBox()
        self.chatgpt_enabled_checkbox.setChecked(self.keys.get("openai_enabled", True))
        chatgpt_layout.addRow("Enabled:", self.chatgpt_enabled_checkbox)

        self.chatgpt_key_edit = QLineEdit()
        self.chatgpt_key_edit.setText(self.keys.get("api_key", ""))
        chatgpt_layout.addRow("API Key:", self.chatgpt_key_edit)

        self.chatgpt_hide_edit = QLineEdit()
        self.chatgpt_hide_edit.setText(self.keys.get("openai_hide_models", ""))
        chatgpt_layout.addRow("Hide models:", self.chatgpt_hide_edit)

        self.delete_button = QPushButton("Delete all server files")
        self.delete_button.clicked.connect(self.on_delete_all_server_files)
        chatgpt_layout.addRow(self.delete_button)
        self.chatgpt_group.setLayout(chatgpt_layout)
        models_layout.addWidget(self.chatgpt_group)

        # -------------------- DeepSeek -------------------- #
        self.deepseek_group = QGroupBox("DeepSeek")
        deepseek_layout = QFormLayout()

        self.deepseek_enabled_checkbox = QCheckBox()
        self.deepseek_enabled_checkbox.setChecked(self.keys.get("deepseek_enabled", True))
        deepseek_layout.addRow("Enabled:", self.deepseek_enabled_checkbox)

        self.deepseek_key_edit = QLineEdit()
        self.deepseek_key_edit.setText(self.keys.get("deepseek_api_key", ""))
        deepseek_layout.addRow("API Key:", self.deepseek_key_edit)

        self.deepseek_hide_edit = QLineEdit()
        self.deepseek_hide_edit.setText(self.keys.get("deepseek_hide_models", ""))
        deepseek_layout.addRow("Hide models:", self.deepseek_hide_edit)

        self.deepseek_group.setLayout(deepseek_layout)
        models_layout.addWidget(self.deepseek_group)

        # -------------------- Gemini -------------------- #
        self.gemini_group = QGroupBox("Gemini")
        gemini_layout = QFormLayout()

        self.gemini_enabled_checkbox = QCheckBox()
        self.gemini_enabled_checkbox.setChecked(self.keys.get("gemini_enabled", True))
        gemini_layout.addRow("Enabled:", self.gemini_enabled_checkbox)

        self.gemini_key_edit = QLineEdit()
        self.gemini_key_edit.setText(self.keys.get("gemini_api_key", ""))
        gemini_layout.addRow("API Key:", self.gemini_key_edit)

        self.gemini_hide_edit = QLineEdit()
        self.gemini_hide_edit.setText(self.keys.get("gemini_hide_models", ""))
        gemini_layout.addRow("Hide models:", self.gemini_hide_edit)

        self.gemini_group.setLayout(gemini_layout)
        models_layout.addWidget(self.gemini_group)

        # -------------------- Ollama -------------------- #
        self.ollama_group = QGroupBox("Ollama")
        ollama_layout = QFormLayout()

        self.ollama_enabled_checkbox = QCheckBox()
        self.ollama_enabled_checkbox.setChecked(self.keys.get("ollama_enabled", True))
        ollama_layout.addRow("Enabled:", self.ollama_enabled_checkbox)

        ollama_label = QLabel("No API key required.")
        ollama_layout.addRow(ollama_label)

        self.ollama_hide_edit = QLineEdit()
        self.ollama_hide_edit.setText(self.keys.get("ollama_hide_models", ""))
        ollama_layout.addRow("Hide models:", self.ollama_hide_edit)

        self.ollama_group.setLayout(ollama_layout)
        models_layout.addWidget(self.ollama_group)

        models_tab.setLayout(models_layout)
        self.tab_widget.addTab(models_tab, "Models")
        layout.addWidget(self.tab_widget)

        self.button_box = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        self.button_box.accepted.connect(self.save_settings)
        self.button_box.rejected.connect(self.reject)
        layout.addWidget(self.button_box)

    # ------------------------------------------------------------------ #
    # Actions
    # ------------------------------------------------------------------ #
    def save_settings(self):
        # Update flat in-memory representation
        self.keys["api_key"] = self.chatgpt_key_edit.text()
        self.keys["deepseek_api_key"] = self.deepseek_key_edit.text()
        self.keys["gemini_api_key"] = self.gemini_key_edit.text()

        self.keys["openai_hide_models"] = self.chatgpt_hide_edit.text()
        self.keys["deepseek_hide_models"] = self.deepseek_hide_edit.text()
        self.keys["gemini_hide_models"] = self.gemini_hide_edit.text()
        self.keys["ollama_hide_models"] = self.ollama_hide_edit.text()

        self.keys["openai_enabled"] = self.chatgpt_enabled_checkbox.isChecked()
        self.keys["deepseek_enabled"] = self.deepseek_enabled_checkbox.isChecked()
        self.keys["gemini_enabled"] = self.gemini_enabled_checkbox.isChecked()
        self.keys["ollama_enabled"] = self.ollama_enabled_checkbox.isChecked()

        # Convert to *nested* structure expected by LLMModel/get_provider_settings
        nested = {
            "openai": {
                "api_key": self.keys["api_key"],
                "hide_models": self.keys["openai_hide_models"],
                "enabled": self.keys["openai_enabled"],
            },
            "deepseek": {
                "api_key": self.keys["deepseek_api_key"],
                "hide_models": self.keys["deepseek_hide_models"],
                "enabled": self.keys["deepseek_enabled"],
            },
            "gemini": {
                "api_key": self.keys["gemini_api_key"],
                "hide_models": self.keys["gemini_hide_models"],
                "enabled": self.keys["gemini_enabled"],
            },
            "ollama": {
                "hide_models": self.keys["ollama_hide_models"],
                "enabled": self.keys["ollama_enabled"],
            },
        }

        os.makedirs(os.path.dirname(self.settings_file), exist_ok=True)
        with open(self.settings_file, "w") as f:
            json.dump(nested, f, indent=4)

        self.accept()

    def on_delete_all_server_files(self):
        reply = QMessageBox.question(
            self,
            "Confirm Deletion",
            "Are you sure you want to delete all server files?",
            QMessageBox.Yes | QMessageBox.No,
        )
        if reply != QMessageBox.Yes:
            if self.model is not None:
                self.model.response_generated.emit("Deletion canceled.")
            return

        owner = self.parent().window()
        model = self.model
        if model is None and hasattr(owner, "model"):
            model = owner.model

        if model is None:
            if self.model is not None:
                self.model.response_generated.emit("No model found.")
            return

        for provider in model.llm_model.service_providers:
            try:
                model_name = provider.available_models[0] if provider.available_models else "default"
                provider.delete_all_server_files(
                    modelName=model_name,
                    status_changed=lambda msg, p=provider: model.response_generated.emit(
                        f"Status ({p.__class__.__name__}): {msg}"
                    ),
                    response_generated=lambda msg, p=provider: model.response_generated.emit(
                        f"{p.__class__.__name__}: {msg}"
                    ),
                    project_dir=model.project_dir,
                    chosen_files=model.chosen_files,
                )
            except Exception as e:
                model.response_generated.emit(
                    f"Error deleting files from {provider.__class__.__name__}: {str(e)}"
                )
