from modules.model.serviceProviders.serviceProviderBase import ServiceProviderBase
from ..modelOptions import ModelOptions
from openai import OpenAI
import os
import json
import tempfile
from modules.model.FileContentFormatter import FileContentFormatter
from modules.model.ResponseFilesParser import ResponseFilesParser

class DeepSeekServiceProvider(ServiceProviderBase):
    def __init__(self):
        super().__init__()
        self.available_models = [
            "deepseek-chat",
            "deepseek-reasoner",
        ]
        self.jobs = None

    def getBaseUrl(self):
        return "https://api.deepseek.com/v1"

    def get_api_key(self):
        return super().get_api_key('deepseek_api_key')

    def getModelOptions(self, modelName):
        return ModelOptions(supportBatch=False, supportReasoningEffort=False)
    
    def getRoleForModel(self, modelName):
        return "system"

    def getClient(self, model_context):
        api_key = self.get_api_key()
        return OpenAI(api_key=api_key, base_url=self.getBaseUrl())

    def make_file_content_text(self, project_dir, chosen_files, editorMode):
        formatter = FileContentFormatter()
        return formatter.make_file_content_text(project_dir, chosen_files, editorMode)

    def _generate_response_sync(self, model_context, role_string, full_request, editor_mode, reasoning_effort):
        print("Response thread: Sending...")
        messages = [
            {"role": self.getRoleForModel(model_context["modelName"]), "content": role_string},
            {"role": "user", "content": full_request}
        ]
        print("Model: " + model_context["modelName"])
        print("Role: " + role_string)
        print("Editor Mode: " + str(editor_mode))
        print("Request: " + full_request)
        print("--------------")
        model_context["status_changed"]("Waiting for the response ...")
        client = self.getClient(model_context)
        if reasoning_effort:
            response = client.chat.completions.create(
                model=model_context["modelName"],
                messages=messages,
                reasoning_effort=reasoning_effort
            )
        else:
            response = client.chat.completions.create(
                model=model_context["modelName"],
                messages=messages
            )
        generated_response = response.choices[0].message.content
        print("Response choices:" + str(len(response.choices)))
        print("------------ USAGE ------")
        print(response.usage)
        model_context["status_changed"](str(response.usage))
        if editor_mode:
            parser = ResponseFilesParser(model_context["project_dir"])
            parser.parse_response_and_update_files_on_disk(generated_response)
        return (generated_response, response.usage)

    def _generate_batch_response_sync(self, model_context, role_string, full_request, description, editor_mode, reasoning_effort):
        model_context["response_generated"]("Batch functionality is not supported by DeepSeekServiceProvider")

    def get_completed_batch_jobs(self, model_context):
        model_context["response_generated"]("Batch functionality is not supported by DeepSeekServiceProvider")

    def get_batch_results(self, model_context, batch_id):
        model_context["response_generated"]("Batch functionality is not supported by DeepSeekServiceProvider")

    def delete_batch_job(self, model_context, batch_id):
        model_context["response_generated"]("Batch functionality is not supported by DeepSeekServiceProvider")

    def cancel_batch_job(self, model_context, batch_id):
        model_context["response_generated"]("Batch functionality is not supported by DeepSeekServiceProvider")

    def delete_all_server_files(self, model_context):
        model_context["response_generated"]("Batch functionality is not supported by DeepSeekServiceProvider")
