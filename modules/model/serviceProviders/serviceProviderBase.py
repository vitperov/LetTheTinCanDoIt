import json
import os

class ServiceProviderBase:
    def get_base_url(self):
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
