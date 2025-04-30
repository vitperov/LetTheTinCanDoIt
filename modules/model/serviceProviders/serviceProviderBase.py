import json
import os

class ServiceProviderBase:
    def __init__(self):
        self.available_models = []

    def getBaseUrl(self):
        raise NotImplementedError("getBaseUrl method must be implemented by the child class.")

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

    def getModelOptions(self, modelName):
        raise NotImplementedError("getModelOptions method must be implemented by the child class.")

    def getRoleForModel(self, modelName):
        raise NotImplementedError("getRoleForModel method must be implemented by the child class.")

    def _generate_response_sync(self, model_context, role_string, full_request, editor_mode, reasoning_effort):
        raise NotImplementedError("_generate_response_sync method must be implemented by the child class.")

    def _generate_batch_response_sync(self, model_context, role_string, full_request, description, editor_mode, reasoning_effort):
        raise NotImplementedError("_generate_batch_response_sync method must be implemented by the child class.")

    def get_completed_batch_jobs(self, model_context):
        raise NotImplementedError("get_completed_batch_jobs method must be implemented by the child class.")

    def get_batch_results(self, model_context, batch_id):
        raise NotImplementedError("get_batch_results method must be implemented by the child class.")

    def delete_batch_job(self, model_context, batch_id):
        raise NotImplementedError("delete_batch_job method must be implemented by the child class.")

    def cancel_batch_job(self, model_context, batch_id):
        raise NotImplementedError("cancel_batch_job method must be implemented by the child class.")

    def delete_all_server_files(self, model_context):
        raise NotImplementedError("delete_all_server_files method must be implemented by the child class.")
