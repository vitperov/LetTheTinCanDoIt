from .serviceProviderBase import ServiceProviderBase

class OpenAIServiceProvider(ServiceProviderBase):
    def get_base_url(self):
        return "https://api.openai.com/v1"
