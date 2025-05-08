import json
import os
from abc import ABC, abstractmethod

class ServiceProviderBase(ABC):
    def __init__(self):
        self.available_models = []

    @abstractmethod
    def getBaseUrl(self):
        pass

    def get_api_key(self, key_name):
        settings_path = os.path.join('settings', 'key.json')
        if os.path.exists(settings_path):
            with open(settings_path, 'r') as f:
                data = json.load(f)
            return data.get(key_name, '')
        return ''

    def getAvailableModels(self):
        return self.available_models

    def hasModel(self, modelName):
        """
        Check if the given model belongs to this provider.
        """
        return modelName in self.available_models

    @abstractmethod
    def getModelOptions(self, modelName):
        pass

    @abstractmethod
    def _generate_response_sync(self, model_context, full_request):
        pass

    @abstractmethod
    def _generate_batch_response_sync(self, model_context, full_request, description, custom_id):
        pass

    @abstractmethod
    def get_completed_batch_jobs(self, model_context):
        pass

    @abstractmethod
    def get_batch_results(self, model_context, batch_id):
        pass

    @abstractmethod
    def delete_batch_job(self, model_context, batch_id):
        pass

    @abstractmethod
    def cancel_batch_job(self, model_context, batch_id):
        pass

    @abstractmethod
    def delete_all_server_files(self, model_context):
        pass
