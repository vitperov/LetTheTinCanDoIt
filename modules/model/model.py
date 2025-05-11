from PyQt5.QtCore import QObject, pyqtSignal
import os
import json
from modules.model.LLMModel import LLMModel
from modules.model.FileSyntaxCorrector import FileSyntaxCorrector
from modules.model.serviceProviders.openAIServiceProvider import OpenAIServiceProvider
from modules.model.serviceProviders.deepSeekServiceProvider import DeepSeekServiceProvider
from modules.model.serviceProviders.ollamaServiceProvider import OllamaServiceProvider
from modules.model.HistoryModel import HistoryModel
from modules.model.RequestHistoryModel import RequestHistoryModel
from modules.model.ProjectMeta.ProjectMeta import ProjectMeta

def get_api_key(key_name):
    settings_path = os.path.join('settings', 'key.json')
    if os.path.exists(settings_path):
        with open(settings_path, 'r') as f:
            data = json.load(f)
        return data.get(key_name, '')
    return ''

class ProjectGPTModel(QObject):
    response_generated = pyqtSignal(str)
    completed_job_list_updated = pyqtSignal(list, list)
    status_changed = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.available_models = []
        self.project_dir = None
        self.chosen_files = []
        self.completed_batches = []
        self.completed_jobs_descriptions = []
        self.syntax_corrector = FileSyntaxCorrector()
        self.additionalRequests = self.load_additional_requests()
        self.service_providers = []
        openai_api_key = get_api_key("api_key")
        deepseek_api_key = get_api_key("deepseek_api_key")
        self.service_providers.append(OpenAIServiceProvider(api_key=openai_api_key))
        self.service_providers.append(DeepSeekServiceProvider(api_key=deepseek_api_key))
        self.service_providers.append(OllamaServiceProvider())
        for provider in self.service_providers:
            self.available_models.extend(provider.getAvailableModels())

        self.llm_model = LLMModel(self.service_providers)
        self.llm_model.response_generated.connect(self.response_generated.emit)
        self.llm_model.completed_job_list_updated.connect(self.completed_job_list_updated.emit)
        self.llm_model.status_changed.connect(self.status_changed.emit)

        self.historyModel = HistoryModel()
        self.requestHistoryModel = RequestHistoryModel()

        last_project_directory = self.historyModel.get_last_project_directory()
        self.project_meta = ProjectMeta(last_project_directory)

    def set_project_files(self, project_dir, chosen_files):
        self.llm_model.set_project_files(project_dir, chosen_files)
        self.project_meta = ProjectMeta(project_dir)
        self.project_dir = project_dir
        self.chosen_files = chosen_files

    def load_additional_requests(self):
        additional_requests_path = os.path.join('additionalRequests.json')
        if os.path.exists(additional_requests_path):
            with open(additional_requests_path, 'r') as f:
                data = json.load(f)
            return data.get('requests', [])
        return []

    def get_additional_requests(self):
        return self.additionalRequests

    def getCurrentModel(self):
        return self.llm_model

    def get_model_options(self, model_name):
        for provider in self.service_providers:
            if provider.hasModel(model_name):
                return provider.getModelOptions(model_name)
        raise ValueError(f"Model options for model {model_name} not found.")
