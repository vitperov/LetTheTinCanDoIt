from .serviceProviderBase import ServiceProviderBase
from ..modelOptions import ModelOptions

class OpenAIServiceProvider(ServiceProviderBase):
    def __init__(self):
        self.available_models = [
            "gpt-4o-mini", 
            "gpt-4o", 
            "o1-preview", 
            "o1-mini",
            "o1", 
            "o3-mini",
            "gpt-4.5-preview",
        ]

    def get_base_url(self):
        return "https://api.openai.com/v1"

    def get_api_key(self):
        # Specify the hardcoded variable name for the OpenAI API key
        return super().get_api_key('api_key')

    def getModelOptions(self, modelName):
        supportReasoningEffort = modelName in ["o3-mini", "o1"]
        return ModelOptions(supportBatch=True, supportReasoningEffort=supportReasoningEffort)
