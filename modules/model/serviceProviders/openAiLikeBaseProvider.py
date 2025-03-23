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

    def _generate_response_sync(self, model_context, role_string, full_request, editor_mode, reasoning_effort):
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
        model_context["status_changed"]("Uploading batch files ...")
        file_content_text = self.make_file_content_text(model_context["project_dir"], model_context["chosen_files"], editor_mode)
        full_request_with_files = file_content_text + full_request
        messages = [
            {"role": self.getRoleForModel(model_context["modelName"]), "content": role_string},
            {"role": "user", "content": full_request_with_files}
        ]
        print("==== Request text ====")
        print(full_request_with_files)
        print("======================")
        batch_request = {
            "custom_id": f"{model_context['project_dir']}|{editor_mode}",
            "method": "POST",
            "url": "/v1/chat/completions",
            "body": {
                "model": model_context["modelName"],
                "messages": messages,
            }
        }
        if reasoning_effort:
            batch_request["body"]["reasoning_effort"] = reasoning_effort
        tmp_dir = os.path.join(os.getcwd(), 'tmp')
        os.makedirs(tmp_dir, exist_ok=True)
        with tempfile.NamedTemporaryFile(mode="w+", suffix=".jsonl", dir=tmp_dir, delete=False) as temp_file:
            temp_file.write(json.dumps(batch_request) + '\n')
            temp_file_path = temp_file.name
        print(f"Batch request JSON saved at: {temp_file_path}")
        client = self.getClient(model_context)
        with open(temp_file_path, "rb") as file_to_upload:
            batch_input_file = client.files.create(
                file=file_to_upload,
                purpose="batch"
            )
        batch_input_file_id = batch_input_file.id
        print("Batch input file ID: " + str(batch_input_file_id))
        model_context["status_changed"]("Waiting for the response ...")
        batch_obj = client.batches.create(
            input_file_id=batch_input_file_id,
            endpoint="/v1/chat/completions",
            completion_window="24h",
            metadata={
                "description": description,
            }
        )
        print("Batch object:")
        print(batch_obj)
        return batch_obj
