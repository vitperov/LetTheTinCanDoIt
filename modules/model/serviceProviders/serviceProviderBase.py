import json
import os
from abc import ABC, abstractmethod

class ServiceProviderBase(ABC):
    def __init__(self):
        self.available_models = []

    @abstractmethod
    def getBaseUrl(self):
        pass

    # get_api_key removed from here

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
    def _generate_response_sync(self, modelName, full_request, status_changed, response_generated, project_dir=None, chosen_files=None):
        pass

    @abstractmethod
    def _generate_batch_response_sync(self, modelName, full_request, description, custom_id, status_changed, response_generated, completed_job_list_updated, project_dir=None, chosen_files=None):
        pass

    @abstractmethod
    def get_completed_batch_jobs(self, modelName, status_changed, response_generated, completed_job_list_updated, project_dir=None, chosen_files=None):
        pass

    @abstractmethod
    def get_batch_results(self, modelName, batch_id, status_changed, response_generated, project_dir=None, chosen_files=None):
        pass

    @abstractmethod
    def delete_batch_job(self, modelName, batch_id, status_changed, response_generated, project_dir=None, chosen_files=None):
        pass

    @abstractmethod
    def cancel_batch_job(self, modelName, batch_id, status_changed, response_generated, project_dir=None, chosen_files=None):
        pass

    @abstractmethod
    def delete_all_server_files(self, modelName, status_changed, response_generated, project_dir=None, chosen_files=None):
        pass
