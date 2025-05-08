import os
import json
import tempfile
from datetime import datetime
from openai import OpenAI
from modules.model.ResponseFilesParser import ResponseFilesParser
from modules.model.FileContentFormatter import FileContentFormatter
from modules.model.serviceProviders.serviceProviderBase import ServiceProviderBase
from ..modelOptions import ModelOptions

class OpenAIServiceProvider(ServiceProviderBase):
    def __init__(self):
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

    def getBaseUrl(self):
        return "https://api.openai.com/v1"

    def get_api_key(self):
        return super().get_api_key('api_key')

    def getModelOptions(self, modelName):
        return ModelOptions(supportBatch=True)
    
    def getRoleForModel(self, modelName):
        if "o1" in modelName.lower():
            return "assistant"
        else:
            return "system"

    def getClient(self, model_context):
        api_key = self.get_api_key()
        return OpenAI(api_key=api_key, base_url=self.getBaseUrl())

    def make_file_content_text(self, project_dir, chosen_files, editorMode):
        formatter = FileContentFormatter()
        return formatter.make_file_content_text(project_dir, chosen_files, editorMode)

    def _generate_response_sync(self, model_context, full_request, editor_mode):
        print("Response thread: Sending...")
        messages = [
            {"role": "user", "content": full_request},
        ]
        print("Model: " + model_context["modelName"])
        print("Editor Mode: " + str(editor_mode))
        print("Request: " + full_request)
        print("--------------")
        model_context["status_changed"]("Waiting for the response ...")
        client = self.getClient(model_context)

        model_name = model_context["modelName"]
        api_model_name = model_name
        used_reasoning_effort = None

        if model_name == "o3-mini-high":
            api_model_name = "o3-mini"
            used_reasoning_effort = "high"
        elif model_name == "o3-mini":
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
        model_context["status_changed"](str(response.usage))
        if editor_mode:
            parser = ResponseFilesParser(model_context["project_dir"])
            parser.parse_response_and_update_files_on_disk(generated_response)
        return (generated_response, response.usage)

    def _generate_batch_response_sync(self, model_context, full_request, description, editor_mode):
        model_context["status_changed"]("Uploading batch files ...")
        messages = [
            {"role": "user", "content": full_request},
        ]
        print("==== Request text ====")
        print(full_request)
        print("======================")
        model_name = model_context["modelName"]
        api_model_name = model_name
        used_reasoning_effort = None
        if model_name == "o3-mini-high":
            api_model_name = "o3-mini"
            used_reasoning_effort = "high"
        elif model_name == "o3-mini":
            used_reasoning_effort = "medium"

        batch_request = {
            "custom_id": f"{model_context['project_dir']}|{editor_mode}",
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
            usage = str(data['response']['body']['usage'])
            print("------------ USAGE ------")
            print(usage)
            model_context["response_generated"](response_text)
            if not os.path.exists(proj_dir):
                print("Project directory from batch custom_id field '" + str(proj_dir) + "' was not found. Using patch from GUI: " + str(model_context["project_dir"]))
                proj_dir = model_context["project_dir"]
            if editor_mode:
                parser = ResponseFilesParser(proj_dir)
                parser.parse_response_and_update_files_on_disk(response_text)
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

    def cancel_batch_job(self, model_context, batch_id):
        try:
            model_context["status_changed"]("Canceling batch job ...")
            client = self.getClient(model_context)
            client.batches.cancel(batch_id)
            model_context["status_changed"]("Batch job canceled successfully")
        except Exception as e:
            model_context["response_generated"]("Error canceling batch job: " + str(e))

    def delete_all_server_files(self, model_context):
        try:
            model_context["status_changed"]("Listing server files ...")
            client = self.getClient(model_context)
            files_list = client.files.list()
            print("Files list:", files_list)
            files = files_list.data
            total = len(files)
            for idx, file_obj in enumerate(files, start=1):
                file_id = file_obj.id
                client.files.delete(file_id)
                msg = f"Deleting file [{idx}/{total}] - OK"
                print(msg)
                model_context["response_generated"](msg)
            model_context["status_changed"]("All files deleted.")
        except Exception as e:
            model_context["response_generated"]("Error deleting server files: " + str(e))
