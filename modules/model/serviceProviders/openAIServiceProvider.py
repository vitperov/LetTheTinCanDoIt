from .serviceProviderBase import ServiceProviderBase

class OpenAIServiceProvider(ServiceProviderBase):
    def get_base_url(self):
        return "https://api.openai.com/v1"

    def get_api_key(self):
        # Specify the hardcoded variable name for the OpenAI API key
        return super().get_api_key('api_key')
