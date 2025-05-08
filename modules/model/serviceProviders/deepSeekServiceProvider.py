from modules.model.serviceProviders.serviceProviderBase import ServiceProviderBase
from modules.model.modelOptions import ModelOptions
from openai import OpenAI
import os
import json
import tempfile
from modules.model.ResponseFilesParser import ResponseFilesParser

class DeepSeekServiceProvider(ServiceProviderBase):
    def __init__(self):
        super().__init__()
        self.available_models = [
            "deepseek-chat",
            "deepseek-reasoner",
        ]
        self.jobs = None

    def getBaseUrl(self) -> str:
        return "https://api.deepseek.com/v1"

    def get_api_key(self) -> str:
        return super().get_api_key('deepseek_api_key')

    def getModelOptions(self, modelName) -> ModelOptions:  # override
        return ModelOptions(supportBatch=False, supportReasoningEffort=False)
    
    def getClient(self, model_context):
        api_key = self.get_api_key()
        return OpenAI(api_key=api_key, base_url=self.getBaseUrl())

    def _generate_response_sync(self, model_context, full_request):  # override
        print("Response thread: Sending...")
        messages = [
            {"role": "user", "content": full_request}
        ]
        print("Model: " + model_context["modelName"])
        print("Request: " + full_request)
        print("--------------")
        model_context["status_changed"]("Waiting for the response ...")
        client = self.getClient(model_context)
        response = client.chat.completions.create(
            model=model_context["modelName"],
            messages=messages
        )
        generated_response = response.choices[0].message.content
        print("Response choices:" + str(len(response.choices)))
        print("------------ USAGE ------")
        print(response.usage)
        model_context["status_changed"](str(response.usage))
        return (generated_response, response.usage)

    def _generate_batch_response_sync(self, model_context, full_request, description, custom_id):  # override
        model_context["response_generated"]("Batch functionality is not supported by DeepSeekServiceProvider")

    def get_completed_batch_jobs(self, model_context):  # override
        model_context["response_generated"]("Batch functionality is not supported by DeepSeekServiceProvider")

    def get_batch_results(self, model_context, batch_id):  # override
        model_context["response_generated"]("Batch functionality is not supported by DeepSeekServiceProvider")

    def delete_batch_job(self, model_context, batch_id):  # override
        model_context["response_generated"]("Batch functionality is not supported by DeepSeekServiceProvider")

    def cancel_batch_job(self, model_context, batch_id):  # override
        model_context["response_generated"]("Batch functionality is not supported by DeepSeekServiceProvider")

    def delete_all_server_files(self, model_context):  # override
        model_context["response_generated"]("Batch functionality is not supported by DeepSeekServiceProvider")
