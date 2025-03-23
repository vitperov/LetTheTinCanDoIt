import os
import json
import tempfile
from datetime import datetime
from openai import OpenAI
from modules.model.ResponseFilesParser import ResponseFilesParser
from modules.model.FileContentFormatter import FileContentFormatter
from .openAiLikeBaseProvider import OpenAiLikeBaseProvider
from ..modelOptions import ModelOptions

class OpenAIServiceProvider(OpenAiLikeBaseProvider):
    def __init__(self):
        super().__init__()
        self.available_models = [
            "gpt-4o-mini", 
            "gpt-4o", 
            "o1-preview", 
            "o1-mini",
            "o1", 
            "o3-mini",
            "gpt-4.5-preview",
        ]

    def getBaseUrl(self):
        return "https://api.openai.com/v1"

    def get_api_key(self):
        return super().get_api_key('api_key')

    def getModelOptions(self, modelName):
        supportReasoningEffort = modelName in ["o3-mini", "o1"]
        return ModelOptions(supportBatch=True, supportReasoningEffort=supportReasoningEffort)
    
    def getRoleForModel(self, modelName):
        if "o1" in modelName.lower():
            return "assistant"
        else:
            return "system"

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

    def get_completed_batch_jobs(self, model_context):
        try:
            model_context["status_changed"]("Getting batches list ...")
            client = self.getClient(model_context)
            jobs = client.batches.list(limit=7)
            batch_dict = {}
            completed_batches = []
            completed_jobs_descriptions = []
            for batch in jobs.data:
                batch_id = batch.id
                status = batch.status
                description = batch.metadata.get('description', 'No description')
                if (status == 'completed' or True) and batch_id not in completed_batches:
                    completed_batches.append(batch_id)
                    completed_jobs_descriptions.append(description)
                batch_dict[batch_id] = {'status': status, 'description': description}
            current_time = datetime.now().strftime("%H:%M:%S")
            result_str = f"Current time: {current_time}\n" + "\n".join([f"* {bid} -> {info['status']} // {info['description']};" for bid, info in batch_dict.items()])
            model_context["response_generated"](result_str)
            model_context["completed_job_list_updated"](completed_batches, completed_jobs_descriptions)
            model_context["status_changed"]("Done")
            self.jobs = jobs
        except Exception as e:
            model_context["response_generated"]("Error retrieving completed batch jobs: " + str(e))

    def get_batch_results(self, model_context, batch_id):
        try:
            model_context["status_changed"]("Getting batch results ...")
            client = self.getClient(model_context)
            jobs = self.jobs
            if jobs is None:
                raise ValueError("No jobs available. Please call get_completed_batch_jobs first.")
            batch = next((job for job in jobs.data if job.id == batch_id), None)
            if not batch:
                raise ValueError(f"Batch job with ID {batch_id} not found.")
            description = batch.metadata.get('description', 'No description')
            print("Description: " + description)
            output_file_id = batch.output_file_id
            file_response = client.files.content(output_file_id).text
            data = json.loads(file_response)
            custom_id = data['custom_id']
            proj_dir, editor_mode_str = custom_id.split('|')
            editor_mode = editor_mode_str.lower() == 'true'
            print("Proj dir: " + proj_dir)
            print("Editor Mode: " + str(editor_mode))
            response_text = str(data['response']['body']['choices'][0]['message']['content'])
            model_context["response_generated"](response_text)
            if not os.path.exists(proj_dir):
                print("Project directory from batch custom_id field '" + str(proj_dir) + "' was not found. Using patch from GUI: " + str(model_context["project_dir"]))
                proj_dir = model_context["project_dir"]
            if editor_mode:
                parser = ResponseFilesParser(proj_dir)
                parser.parse_response_and_update_files_on_disk(response_text)
            usage = str(data['response']['body']['usage'])
            model_context["status_changed"](usage)
        except Exception as e:
            model_context["response_generated"]("Error retrieving batch results: " + str(e))

    def delete_batch_job(self, model_context, batch_id):
        print(f"Deleting batch job with ID: {batch_id}")
        try:
            jobs = self.jobs
            if jobs is None:
                raise ValueError("No jobs available. Please call get_completed_batch_jobs first.")
            batch = next((job for job in jobs.data if job.id == batch_id), None)
            if not batch:
                raise ValueError(f"Batch job with ID {batch_id} not found.")
            input_file_id = batch.input_file_id
            output_file_id = batch.output_file_id
            client = self.getClient(model_context)
            print("Deleting job file " + input_file_id)
            client.files.delete(input_file_id)
            print("Deleting job file " + output_file_id)
            client.files.delete(output_file_id)
            try:
                print("Deleting job " + batch_id)
                client.batches.delete(output_file_id)
            except Exception:
                model_context["response_generated"]("Files are deleted, but the batch can't be deleted since openAI API currently doesn't support it")
            print("Done")
        except Exception as e:
            model_context["response_generated"]("Error deleting batch results: " + str(e))
