import os
import json
import tempfile
from datetime import datetime
from openai import OpenAI
from modules.model.ResponseFilesParser import ResponseFilesParser
from modules.model.FileContentFormatter import FileContentFormatter
from .serviceProviderBase import ServiceProviderBase

class OpenAiLikeBaseProvider(ServiceProviderBase):
    def __init__(self):
        super().__init__()
        self.jobs = None

    def getClient(self, model_context):
        api_key = self.get_api_key()
        return OpenAI(api_key=api_key, base_url=self.getBaseUrl())

    def make_file_content_text(self, project_dir, chosen_files, editorMode):
        formatter = FileContentFormatter()
        return formatter.make_file_content_text(project_dir, chosen_files, editorMode)

    def _generate_response_sync(self, model_context, role_string, full_request, editor_mode):
        print("Response thread: Sending...")
        file_content_text = self.make_file_content_text(model_context["project_dir"], model_context["chosen_files"], editor_mode)
        full_request_with_files = file_content_text + full_request
        messages = [
            {"role": self.getRoleForModel(model_context["modelName"]), "content": role_string},
            {"role": "user", "content": full_request_with_files}
        ]
        print("Model: " + model_context["modelName"])
        print("Role: " + role_string)
        print("Editor Mode: " + str(editor_mode))
        print("Request: " + full_request_with_files)
        print("--------------")
        model_context["status_changed"]("Waiting for the response ...")
        client = self.getClient(model_context)
        response = client.chat.completions.create(
            model=model_context["modelName"],
            messages=messages,
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
