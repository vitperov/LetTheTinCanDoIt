from modules.model.serviceProviders.serviceProviderBase import ServiceProviderBase
from modules.model.modelOptions import ModelOptions
from openai import OpenAI
import os
import json
import tempfile
from modules.model.ResponseFilesParser import ResponseFilesParser

class DeepSeekServiceProvider(ServiceProviderBase):
    def __init__(self, api_key=None):
        super().__init__()
        self.available_models = [
            "deepseek-chat",
            "deepseek-reasoner",
        ]
        self.jobs = None
        self.api_key = api_key

    def getBaseUrl(self) -> str:
        return "https://api.deepseek.com/v1"

    def getModelOptions(self, modelName) -> ModelOptions:
        return ModelOptions(supportBatch=False)

    def getClient(self):
        return OpenAI(api_key=self.api_key, base_url=self.getBaseUrl())

    def _generate_response_sync(self, modelName, full_request, status_changed, response_generated, project_dir=None, chosen_files=None):
        print("Response thread: Sending...")
        messages = [
            {"role": "user", "content": full_request}
        ]
        print("Model: " + modelName)
        print("Request: " + full_request)
        print("--------------")
        status_changed("Waiting for the response ...")
        client = self.getClient()
        response = client.chat.completions.create(
            model=modelName,
            messages=messages
        )
        generated_response = response.choices[0].message.content
        print("Response choices:" + str(len(response.choices)))
        print("------------ USAGE ------")
        print(response.usage)
        status_changed(str(response.usage))
        return (generated_response, response.usage)

    def _generate_batch_response_sync(self, modelName, full_request, description, custom_id, status_changed, response_generated, completed_job_list_updated, project_dir=None, chosen_files=None):
        response_generated("Batch functionality is not supported by DeepSeekServiceProvider")

    def get_completed_batch_jobs(self, modelName, status_changed, response_generated, completed_job_list_updated, project_dir=None, chosen_files=None):
        response_generated("Batch functionality is not supported by DeepSeekServiceProvider")

    def get_batch_results(self, modelName, batch_id, status_changed, response_generated, project_dir=None, chosen_files=None):
        response_generated("Batch functionality is not supported by DeepSeekServiceProvider")

    def delete_batch_job(self, modelName, batch_id, status_changed, response_generated, project_dir=None, chosen_files=None):
        response_generated("Batch functionality is not supported by DeepSeekServiceProvider")

    def cancel_batch_job(self, modelName, batch_id, status_changed, response_generated, project_dir=None, chosen_files=None):
        response_generated("Batch functionality is not supported by DeepSeekServiceProvider")

    def delete_all_server_files(self, modelName, status_changed, response_generated, project_dir=None, chosen_files=None):
        response_generated("Batch functionality is not supported by DeepSeekServiceProvider")
