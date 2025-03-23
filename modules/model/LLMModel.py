from PyQt5.QtCore import QObject, pyqtSignal
import os
import json
import tempfile
from datetime import datetime
from openai import OpenAI
from modules.model.ResponseFilesParser import ResponseFilesParser
from modules.model.ThreadManager import ThreadManager
from modules.model.FileContentFormatter import FileContentFormatter

class LLMModel(QObject):
    response_generated = pyqtSignal(str)
    completed_job_list_updated = pyqtSignal(list, list)
    status_changed = pyqtSignal(str)

    def __init__(self, provider, modelName):
        super().__init__()
        self.provider = provider
        self.modelName = modelName
        self.thread_manager = ThreadManager()
        self.project_dir = None
        self.chosen_files = []
        self.jobs = None
        self.completed_batches = []
        self.completed_jobs_descriptions = []

    def getClient(self):
        api_key = self.provider.get_api_key()
        return OpenAI(api_key=api_key, base_url=self.provider.getBaseUrl())

    def make_file_content_text(self, project_dir, chosen_files, editorMode):
        formatter = FileContentFormatter()
        return formatter.make_file_content_text(project_dir, chosen_files, editorMode)

    def do_generate_response(self, role_string, full_request, editor_mode):
        print("Response thread: Sending...")
        file_content_text = self.make_file_content_text(self.project_dir, self.chosen_files, editor_mode)
        full_request_with_files = file_content_text + full_request
        messages = [
            {"role": self.provider.getRoleForModel(self.modelName), "content": role_string},
            {"role": "user", "content": full_request_with_files}
        ]
        print("Model: " + self.modelName)
        print("Role: " + role_string)
        print("Editor Mode: " + str(editor_mode))
        print("Request: " + full_request_with_files)
        print("--------------")
        self.status_changed.emit("Waiting for the response ...")
        client = self.getClient()
        response = client.chat.completions.create(
            model=self.modelName,
            messages=messages,
        )
        generated_response = response.choices[0].message.content
        print("Response choices:" + str(len(response.choices)))
        print("------------ USAGE ------")
        print(response.usage)
        self.status_changed.emit(str(response.usage))
        if editor_mode:
            parser = ResponseFilesParser(self.project_dir)
            parser.parse_response_and_update_files_on_disk(generated_response)
        return (generated_response, response.usage)

    def generate_response(self, role_string, full_request, editor_mode):
        try:
            self.status_changed.emit("Sending the request ...")
            print("Sending the request in a new tread")
            self.thread_manager.execute_async(
                lambda: self.do_generate_response(role_string, full_request, editor_mode),
                lambda result: self.handle_generate_response(result),
                lambda e: self.response_generated.emit("Error generating response: " + str(e))
            )
            print("Done. Waiting for the result")
        except Exception as e:
            self.response_generated.emit("Error generating response: " + str(e))

    def handle_generate_response(self, result):
        generated_response, usage = result
        self.response_generated.emit(generated_response)
        self.status_changed.emit(str(usage))

    def do_generate_batch_response(self, role_string, full_request, description, editor_mode):
        self.status_changed.emit("Uploading batch files ...")
        file_content_text = self.make_file_content_text(self.project_dir, self.chosen_files, editor_mode)
        full_request_with_files = file_content_text + full_request
        messages = [
            {"role": self.provider.getRoleForModel(self.modelName), "content": role_string},
            {"role": "user", "content": full_request_with_files}
        ]
        print("==== Request text ====")
        print(full_request_with_files)
        print("======================")
        batch_request = {
            "custom_id": f"{self.project_dir}|{editor_mode}",
            "method": "POST",
            "url": "/v1/chat/completions",
            "body": {
                "model": self.modelName,
                "messages": messages,
            }
        }
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
        self.status_changed.emit("Waiting for the response ...")
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

    def generate_batch_response(self, role_string, full_request, description, editor_mode):
        try:
            self.thread_manager.execute_async(
                lambda: self.do_generate_batch_response(role_string, full_request, description, editor_mode),
                lambda result: self.response_generated.emit(str(result)),
                lambda e: self.response_generated.emit("Error generating batch response: " + str(e))
            )
        except Exception as e:
            self.response_generated.emit("Error generating batch response: " + str(e))

    def get_completed_batch_jobs(self):
        try:
            self.status_changed.emit("Getting batches list ...")
            client = self.getClient()
            self.jobs = client.batches.list(limit=7)
            batch_dict = {}
            self.completed_batches = []
            self.completed_jobs_descriptions = []
            for batch in self.jobs.data:
                batch_id = batch.id
                status = batch.status
                description = batch.metadata.get('description', 'No description')
                if (status == 'completed' or True) and batch_id not in self.completed_batches:
                    self.completed_batches.append(batch_id)
                    self.completed_jobs_descriptions.append(description)
                batch_dict[batch_id] = {'status': status, 'description': description}
            current_time = datetime.now().strftime("%H:%M:%S")
            result_str = f"Current time: {current_time}\n" + "\n".join([f"* {bid} -> {info['status']} // {info['description']};" for bid, info in batch_dict.items()])
            self.response_generated.emit(result_str)
            self.completed_job_list_updated.emit(self.completed_batches, self.completed_jobs_descriptions)
            self.status_changed.emit("Done")
        except Exception as e:
            self.response_generated.emit("Error retrieving completed batch jobs: " + str(e))

    def get_batch_results(self, batch_id):
        try:
            if self.jobs is None:
                raise ValueError("No jobs available. Please call get_completed_batch_jobs first.")
            batch = next((job for job in self.jobs.data if job.id == batch_id), None)
            if not batch:
                raise ValueError(f"Batch job with ID {batch_id} not found.")
            self.status_changed.emit("Getting batch results ...")
            description = batch.metadata.get('description', 'No description')
            print("Description: " + description)
            output_file_id = batch.output_file_id
            client = self.getClient()
            file_response = client.files.content(output_file_id).text
            data = json.loads(file_response)
            custom_id = data['custom_id']
            proj_dir, editor_mode_str = custom_id.split('|')
            editor_mode = editor_mode_str.lower() == 'true'
            print("Proj dir: " + proj_dir)
            print("Editor Mode: " + str(editor_mode))
            response = str(data['response']['body']['choices'][0]['message']['content'])
            self.response_generated.emit(response)
            if not os.path.exists(proj_dir):
                print("Project directory from batch custom_id field '" + str(proj_dir) + "' was not found. Using patch from GUI: " + str(self.project_dir))
                proj_dir = self.project_dir
                return
            if editor_mode:
                parser = ResponseFilesParser(proj_dir)
                parser.parse_response_and_update_files_on_disk(response)
            usage = str(data['response']['body']['usage'])
            self.status_changed.emit(usage)
        except Exception as e:
            self.response_generated.emit("Error retrieving batch results: " + str(e))

    def delete_batch_job(self, batch_id):
        print(f"Deleting batch job with ID: {batch_id}")
        try:
            if self.jobs is None:
                raise ValueError("No jobs available. Please call get_completed_batch_jobs first.")
            batch = next((job for job in self.jobs.data if job.id == batch_id), None)
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
                self.response_generated.emit("Files are deleted, but the batch can't be deleted since openAI API currently doesn't support it")
            print("Done")
        except Exception as e:
            self.response_generated.emit("Error deleting batch results: " + str(e))
