import json
import os

class ServiceProviderBase:
    def __init__(self):
        self.available_models = []

    def getBaseUrl(self):
        raise NotImplementedError("This method should be overridden in a derived class.")

    def get_api_key(self, key_name):
        # Load the API key from a JSON file with a specific key name
        settings_path = os.path.join('settings', 'key.json')
        if os.path.exists(settings_path):
            with open(settings_path, 'r') as f:
                data = json.load(f)
            return data.get(key_name, '')
        return ''
        
    def getAvailableModels(self):
        """
        Return the list of available models.
        """
        return self.available_models

    def hasModel(self, modelName):
        """
        Check if the given model belongs to this provider.
        """
        return modelName in self.available_models

    def getModelOptions(self, modelName):
        raise NotImplementedError("This method should be overridden in a derived class.")
    
    def getRoleForModel(self, modelName):
        raise NotImplementedError("This method should be overridden in a derived class.")
