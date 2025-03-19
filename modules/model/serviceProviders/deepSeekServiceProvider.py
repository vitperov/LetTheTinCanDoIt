from .serviceProviderBase import ServiceProviderBase
from ..modelOptions import ModelOptions

class DeepSeekServiceProvider(ServiceProviderBase):
    def __init__(self):
        self.available_models = [
            "deepseek-chat",
            "deepseek-reasoner",
        ]

    def getBaseUrl(self):
        return "https://api.deepseek.com/v1"

    def get_api_key(self):
        return super().get_api_key('deepseek_api_key')

    def getModelOptions(self, modelName):
        return ModelOptions(supportBatch=False, supportReasoningEffort=False)
    
    def getRoleForModel(self, modelName):
        return "system"
