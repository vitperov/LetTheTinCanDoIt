from .serviceProviderBase import ServiceProviderBase

class OpenAIServiceProvider(ServiceProviderBase):
    def __init__(self):
        self.available_models = [
            "gpt-4o-mini", 
            "gpt-4o", 
            "o1-preview", 
            "o1-mini",
            "o1", 
            "o3-mini",
        ]

    def get_base_url(self):
        return "https://api.openai.com/v1"

    def get_api_key(self):
        # Specify the hardcoded variable name for the OpenAI API key
        return super().get_api_key('api_key')
