from .openAiLikeBaseProvider import OpenAiLikeBaseProvider
from ..modelOptions import ModelOptions

class DeepSeekServiceProvider(OpenAiLikeBaseProvider):
    def __init__(self):
        super().__init__()
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

    def _generate_batch_response_sync(self, model_context, role_string, full_request, description, editor_mode):
        model_context["response_generated"]("Batch functionality is not supported by DeepSeekServiceProvider")

    def get_completed_batch_jobs(self, model_context):
        model_context["response_generated"]("Batch functionality is not supported by DeepSeekServiceProvider")

    def get_batch_results(self, model_context, batch_id):
        model_context["response_generated"]("Batch functionality is not supported by DeepSeekServiceProvider")

    def delete_batch_job(self, model_context, batch_id):
        model_context["response_generated"]("Batch functionality is not supported by DeepSeekServiceProvider")
