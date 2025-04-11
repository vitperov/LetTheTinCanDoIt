from PyQt5.QtCore import QObject, pyqtSignal, QThread, QTimer
from openai import OpenAI
import os
import json
import tempfile
from datetime import datetime
from modules.model.ResponseFilesParser import ResponseFilesParser
from modules.model.FileSyntaxCorrector import FileSyntaxCorrector
from modules.model.FileContentFormatter import FileContentFormatter
from modules.model.serviceProviders.openAIServiceProvider import OpenAIServiceProvider
from modules.model.serviceProviders.deepSeekServiceProvider import DeepSeekServiceProvider
from modules.model.serviceProviders.ollamaServiceProvider import OllamaServiceProvider
from modules.model.ThreadManager import ThreadManager

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
        self.jobs = None
        self.syntax_corrector = FileSyntaxCorrector()
        self.additionalRequests = self.load_additional_requests()
        self.service_providers = []
        self.service_providers.append(OpenAIServiceProvider())
        self.service_providers.append(DeepSeekServiceProvider())
        self.service_providers.append(OllamaServiceProvider())
        for service_provider in self.service_providers:
            self.available_models.extend(service_provider.getAvailableModels())
        self.thread_manager = ThreadManager()
        self.currentModel = None
        if self.available_models:
            self.switchModel(self.available_models[0])

    def set_project_files(self, project_dir, chosen_files):
        self.project_dir = project_dir
        self.chosen_files = chosen_files
        if self.currentModel:
            self.currentModel.project_dir = project_dir
            self.currentModel.chosen_files = chosen_files

    def load_additional_requests(self):
        additional_requests_path = os.path.join('additionalRequests.json')
        if os.path.exists(additional_requests_path):
            with open(additional_requests_path, 'r') as f:
                data = json.load(f)
            return data.get('requests', [])
        return []

    def get_additional_requests(self):
        return self.additionalRequests

    def switchModel(self, modelName):
        for provider in self.service_providers:
            if provider.hasModel(modelName):
                from modules.model.LLMModel import LLMModel
                self.currentModel = LLMModel(provider, modelName)
                self.currentModel.project_dir = self.project_dir
                self.currentModel.chosen_files = self.chosen_files
                self.currentModel.response_generated.connect(self.response_generated.emit)
                self.currentModel.completed_job_list_updated.connect(self.completed_job_list_updated.emit)
                self.currentModel.status_changed.connect(self.status_changed.emit)
                return
        raise ValueError(f"No service provider found for model: {modelName}")

    def getCurrentModel(self):
        return self.currentModel

    def get_model_options(self, model_name):
        for service_provider in self.service_providers:
            if service_provider.hasModel(model_name):
                return service_provider.getModelOptions(model_name)
        raise ValueError(f"Model options for model {model_name} not found.")
