import os
import json
import tempfile
from datetime import datetime
from openai import OpenAI
from modules.model.ResponseFilesParser import ResponseFilesParser
from modules.model.serviceProviders.serviceProviderBase import ServiceProviderBase
from ..modelOptions import ModelOptions

class OpenAIServiceProvider(ServiceProviderBase):
    def __init__(self, api_key=None):
        super().__init__()
        self.available_models = [
            "gpt-4o-mini", 
            "gpt-4o", 
            "o1-preview", 
            "o1-mini",
            "o1", 
            "o3-mini",
            "o3-mini-high",
            "gpt-4.5-preview",
            "gpt-4.1",
            "gpt-4.1-mini",
            "gpt-4.1-nano",
            "o4-mini",
        ]
        self.jobs = None
        self.api_key = api_key

    # REMOVED get_api_key - handled in model.py and passed to providers via constructor

    def getBaseUrl(self):  # override
        return "https://api.openai.com/v1"

    def getModelOptions(self, modelName):  # override
        return ModelOptions(supportBatch=True)
    
    def getRoleForModel(self, modelName):
        if "o1" in modelName.lower():
            return "assistant"
        else:
            return "system"

    def getClient(self):
        return OpenAI(api_key=self.api_key, base_url=self.getBaseUrl())

    def _generate_response_sync(self, modelName, full_request, status_changed, response_generated, project_dir=None, chosen_files=None):  # override
        print("Response thread: Sending...")
        messages = [
            {"role": "user", "content": full_request},
        ]
        print("Model: " + modelName)
        print("Request: " + full_request)
        print("--------------")
        status_changed("Waiting for the response ...")
        client = self.getClient()

        api_model_name = modelName
        used_reasoning_effort = None

        if modelName == "o3-mini-high":
            api_model_name = "o3-mini"
            used_reasoning_effort = "high"
        elif modelName == "o3-mini":
            used_reasoning_effort = "medium"

        if used_reasoning_effort:
            response = client.chat.completions.create(
                model=api_model_name,
                messages=messages,
                reasoning_effort=used_reasoning_effort
            )
        else:
            response = client.chat.completions.create(
                model=api_model_name,
                messages=messages
            )
        generated_response = response.choices[0].message.content
        print("Response choices:" + str(len(response.choices)))
        print("------------ USAGE ------")
        print(response.usage)
        status_changed(str(response.usage))
        return (generated_response, response.usage)

    def _generate_batch_response_sync(self, modelName, full_request, description, custom_id, status_changed, response_generated, completed_job_list_updated, project_dir=None, chosen_files=None):  # override
        status_changed("Uploading batch files ...")
        messages = [
            {"role": "user", "content": full_request},
        ]
        print("==== Request text ====")
        print(full_request)
        print("======================")
        api_model_name = modelName
        used_reasoning_effort = None
        if modelName == "o3-mini-high":
            api_model_name = "o3-mini"
            used_reasoning_effort = "high"
        elif modelName == "o3-mini":
            used_reasoning_effort = "medium"

        batch_request = {
            "custom_id": custom_id,  # Passed directly
            "method": "POST",
            "url": "/v1/chat/completions",
            "body": {
                "model": api_model_name,
                "messages": messages,
            }
        }
        if used_reasoning_effort:
            batch_request["body"]["reasoning_effort"] = used_reasoning_effort
        tmp_dir = os.path.join(os.getcwd(), 'tmp')
        os.makedirs(tmp_dir, exist_ok=True)
        with tempfile.NamedTemporaryFile(mode="w+", suffix=".jsonl", dir=tmp_dir, delete=False) as temp_file:
            temp_file.write(json.dumps(batch_request) + '\n')
            temp_file_path = temp_file.name
        print(f"Batch request JSON saved at: {temp_file_path}")
        client = self.getClient()
        with open(temp_file_path, "rb") as file_to_upload:
            batch_input_file = client.files.create(
                file=file_to_upload,
                purpose="batch"
            )
        batch_input_file_id = batch_input_file.id
        print("Batch input file ID: " + str(batch_input_file_id))
        status_changed("Waiting for the response ...")
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

    def get_completed_batch_jobs(self, modelName, status_changed, response_generated, completed_job_list_updated, project_dir=None, chosen_files=None):  # override
        try:
            status_changed("Getting batches list ...")
            client = self.getClient()
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
            response_generated(result_str)
            completed_job_list_updated(completed_batches, completed_jobs_descriptions)
            status_changed("Done")
            self.jobs = jobs
        except Exception as e:
            response_generated("Error retrieving completed batch jobs: " + str(e))

    def get_batch_results(self, modelName, batch_id, status_changed, response_generated, project_dir=None, chosen_files=None):  # override
        try:
            status_changed("Getting batch results ...")
            client = self.getClient()
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
            usage = str(data['response']['body']['usage'])
            print("------------ USAGE ------")
            print(usage)
            return (response_text, usage, editor_mode)
        except Exception as e:
            return (f"Error retrieving batch results: {str(e)}", "Error", False)

    def delete_batch_job(self, modelName, batch_id, status_changed, response_generated, project_dir=None, chosen_files=None):  # override
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
            client = self.getClient()
            print("Deleting job file " + input_file_id)
            client.files.delete(input_file_id)
            print("Deleting job file " + output_file_id)
            client.files.delete(output_file_id)
            try:
                print("Deleting job " + batch_id)
                client.batches.delete(output_file_id)
            except Exception:
                response_generated("Files are deleted, but the batch can't be deleted since openAI API currently doesn't support it")
            print("Done")
        except Exception as e:
            response_generated("Error deleting batch results: " + str(e))

    def cancel_batch_job(self, modelName, batch_id, status_changed, response_generated, project_dir=None, chosen_files=None):  # override
        try:
            status_changed("Canceling batch job ...")
            client = self.getClient()
            client.batches.cancel(batch_id)
            status_changed("Batch job canceled successfully")
        except Exception as e:
            response_generated("Error canceling batch job: " + str(e))

    def delete_all_server_files(self, modelName, status_changed, response_generated, project_dir=None, chosen_files=None):  # override
        try:
            status_changed("Listing server files ...")
            client = self.getClient()
            files_list = client.files.list()
            print("Files list:", files_list)
            files = files_list.data
            total = len(files)
            for idx, file_obj in enumerate(files, start=1):
                file_id = file_obj.id
                client.files.delete(file_id)
                msg = f"Deleting file [{idx}/{total}] - OK"
                print(msg)
                response_generated(msg)
            status_changed("All files deleted.")
        except Exception as e:
            response_generated("Error deleting server files: " + str(e))
