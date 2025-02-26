from PyQt5.QtCore import QObject, pyqtSignal
from openai import OpenAI
import os
import json
import tempfile
from datetime import datetime
from modules.model.ResponseFilesParser import ResponseFilesParser
from modules.model.FileSyntaxCorrector import FileSyntaxCorrector  # Import the new class

class ProjectGPTModel(QObject):
    response_generated = pyqtSignal(str)  # Signal to send the generated response back to the view
    completed_job_list_updated = pyqtSignal(list, list)  # Signal to emit completed batches list along with descriptions
    status_changed = pyqtSignal(str)  # Signal to emit status updates

    def __init__(self):
        super().__init__()
        self.available_models = [
            "gpt-4o-mini", 
            "gpt-4o", 
            "o1-preview", 
            "o1-mini",
            "o1", 
            "o3-mini",
        ]
        self.api_key = self.load_api_key()  # Load the API key from the settings file
        self.client = OpenAI(api_key=self.api_key)
        self.project_dir = None
        self.chosen_files = []
        self.completed_batches = []  # List to store completed job IDs
        self.completed_jobs_descriptions = []  # List to store completed job descriptions
        self.jobs = None  # Variable to store jobs list
        self.syntax_corrector = FileSyntaxCorrector()  # Instantiate FileSyntaxCorrector
        self.additionalRequests = self.load_additional_requests()  # Load additional requests

    def set_project_files(self, project_dir, chosen_files):
        self.project_dir = project_dir
        self.chosen_files = chosen_files

    def load_api_key(self):
        # Load the API key from a JSON file
        settings_path = os.path.join('settings', 'key.json')
        if os.path.exists(settings_path):
            with open(settings_path, 'r') as f:
                data = json.load(f)
            return data.get('api_key', '')
        return ''

    def load_additional_requests(self):
        # Load additional requests from additionalRequests.json file
        additional_requests_path = os.path.join('additionalRequests.json')
        if os.path.exists(additional_requests_path):
            with open(additional_requests_path, 'r') as f:
                data = json.load(f)
            return data.get('requests', [])
        return []
    
    def get_additional_requests(self):
        # Return the loaded additional requests
        return self.additionalRequests

    def make_file_content_text(self, project_dir, chosen_files, editorMode):
        if not chosen_files:
            return ""

        file_contents = []
        header = "Here is my file" if len(chosen_files) == 1 else "Here are my files"
        file_contents.append(header)

        for relative_path in chosen_files:
            file_path = os.path.join(project_dir, relative_path)
            if os.path.exists(file_path):
                with open(file_path, 'r') as file:
                    content = file.read()

                    # Correct the file content syntax using FileSyntaxCorrector
                    content = self.syntax_corrector.prepare_for_encoding(content)

                file_contents.append(f"**{relative_path}**\n```\n{content}\n```\n")

        keepFilenamesRequest = (
            "Please return the content of each file with its corresponding file path. "
            "Each file path should be enclosed in double asterisks (**file_path**), followed by the modified content in a code block. "
            "Do not use ### before file path. "
            "Do not insert any strings between file path and it's content. "
            "The code block should not contain a language as first string. "
            "The content inside the code block should be the file content only, with no additional comments, explanations, or markers. "
            "Do not modify or omit the file paths.\n"
            "If any files are modified, provide the entire content of each modified file, including any unmodified sections. This should allow me to replace the previous content with your response directly. Only include files that were modified; if a file remains unchanged, do not include it in your response.\n\n"
        )

        out = "\n".join(file_contents) 
        if editorMode:
            out = out + "\n" + keepFilenamesRequest
            
        return out

    def generate_response(self, model, role_string, full_request, editor_mode):
        try:
            self.status_changed.emit("Sending the request ...")
            # Construct the messages for the GPT model, with the role_string as the system role
            file_content_text = self.make_file_content_text(self.project_dir, self.chosen_files, editor_mode)
            full_request_with_files = file_content_text + full_request

            messages = [
                {"role": self.get_role_for_model(model), "content": role_string},
                {"role": "user", "content": full_request_with_files}
            ]

            print("Model: " + model)
            print("Role: " + role_string)
            print("Editor Mode: " + str(editor_mode))
            print("Request: " + full_request_with_files)
            print("--------------")

            self.status_changed.emit("Waiting for the response ...")

            # Generate response using the selected model
            response = self.client.chat.completions.create(
                model=model,  # Use the selected model here
                messages=messages,
            )

            # Extract the generated response from the API result
            generated_response = response.choices[0].message.content

            print("Response choices:" + str(len(response.choices)))

            print("------------ USAGE ------")
            print(response.usage)
            self.status_changed.emit(str(response.usage))

            print("------------ UPDATE FILES ------")

            if editor_mode:
                # Create an instance of ResponseFilesParser and call the parsing function
                parser = ResponseFilesParser(self.project_dir)
                parser.parse_response_and_update_files_on_disk(generated_response)

            self.response_generated.emit(generated_response)

        except Exception as e:
            error_message = f"Error generating response: {str(e)}"
            self.response_generated.emit(error_message)

    def generate_batch_response(self, model, role_string, full_request, description, editor_mode):
        try:
            self.status_changed.emit("Uploading batch files ...")

            # Construct the messages for the GPT model, with the role_string as the system role
            file_content_text = self.make_file_content_text(self.project_dir, self.chosen_files, editor_mode)
            full_request_with_files = file_content_text + full_request

            print("==== Request text ====")
            print(full_request_with_files)
            print("======================")

            # Define the request body as per the API format
            messages = [
                {"role": self.get_role_for_model(model), "content": role_string},
                {"role": "user", "content": full_request_with_files}
            ]

            # Prepare the batch request in the required format
            batch_request = {
                "custom_id": f"{self.project_dir}|{editor_mode}",  # Store project dir and editor_mode, separated by a delimiter
                "method": "POST",  # HTTP method
                "url": "/v1/chat/completions",  # API endpoint URL
                "body": {
                    "model": model,  # The selected model
                    "messages": messages,  # The constructed messages
                }
            }

            # Ensure the "CWD/tmp/" directory exists
            tmp_dir = os.path.join(os.getcwd(), 'tmp')
            os.makedirs(tmp_dir, exist_ok=True)  # Create the directory if it doesn't exist

            # Save the JSON to a temporary file in CWD/tmp/
            with tempfile.NamedTemporaryFile(mode="w+", suffix=".jsonl", dir=tmp_dir, delete=False) as temp_file:
                temp_file.write(json.dumps(batch_request) + '\n')
                temp_file_path = temp_file.name

            print(f"Batch request JSON saved at: {temp_file_path}")

            # Upload the file to the API
            with open(temp_file_path, "rb") as file_to_upload:
                batch_input_file = self.client.files.create(
                    file=file_to_upload,
                    purpose="batch"
                )

            # Get the file ID from the uploaded file
            batch_input_file_id = batch_input_file.id
            print("Batch input file ID: " + str(batch_input_file_id))

            self.status_changed.emit("Waiting for the response ...")

            # Create a batch job using the uploaded file
            batch_obj = self.client.batches.create(
                input_file_id=batch_input_file_id,
                endpoint="/v1/chat/completions",
                completion_window="24h",
                metadata={
                    "description": description,  # Use the provided description
                }
            )

            print("Batch object:")
            print(batch_obj)

            # Emit the batch job as the generated response (for testing)
            self.response_generated.emit(str(batch_obj))

            self.status_changed.emit("Done")

        except Exception as e:
            error_message = f"Error generating batch response: {str(e)}"
            self.response_generated.emit(error_message)

    def get_completed_batch_jobs(self):
        try:
            self.status_changed.emit("Getting batches list ...")
            self.jobs = self.client.batches.list(limit=7)  # Store the jobs in self.jobs

            batch_dict = {}
            self.completed_batches = []
            self.completed_jobs_descriptions = []

            # Iterate over each batch object in the retrieved list
            for batch in self.jobs.data:
                batch_id = batch.id
                status = batch.status
                description = batch.metadata.get('description', 'No description')

                if (status == 'completed' or True) and batch_id not in self.completed_batches:
                    self.completed_batches.append(batch_id)
                    self.completed_jobs_descriptions.append(description)

                batch_dict[batch_id] = {'status': status, 'description': description}

            # Convert the dictionary into the desired string format
            current_time = datetime.now().strftime("%H:%M:%S")
            result_str = f"Current time: {current_time}\n"
            result_str += "\n".join([f"* {batch_id} -> {info['status']} // {info['description']};"
                                    for batch_id, info in batch_dict.items()])

            # Emit the result string
            self.response_generated.emit(result_str)

            # Emit the completed_batches list and their descriptions
            self.completed_job_list_updated.emit(self.completed_batches, self.completed_jobs_descriptions)

            self.status_changed.emit("Done")

        except Exception as e:
            error_message = f"Error retrieving completed batch jobs: {str(e)}"
            self.response_generated.emit(error_message)

    def get_batch_results(self, batch_id):
        """
        Retrieves the results for a specific batch job.

        Args:
            batch_id (str): The batch job ID for which to fetch the results.
        """
        try:
            # Find the batch in the stored jobs list
            if self.jobs is None:
                raise ValueError("No jobs available. Please call get_completed_batch_jobs first.")

            batch = next((job for job in self.jobs.data if job.id == batch_id), None)

            if not batch:
                raise ValueError(f"Batch job with ID {batch_id} not found.")

            self.status_changed.emit("Getting batch results ...")

            # Extract the description and output_file_id
            description = batch.metadata.get('description', 'No description')
            print("Description: " + description)

            output_file_id = batch.output_file_id

            file_response = self.client.files.content(output_file_id).text
            data = json.loads(file_response)

            custom_id = data['custom_id']  # Retrieve custom_id which contains both project_dir and editor_mode
            proj_dir, editor_mode_str = custom_id.split('|')
            editor_mode = editor_mode_str.lower() == 'true'  # Convert string back to boolean
            print("Proj dir: " + proj_dir)
            print("Editor Mode: " + str(editor_mode))

            # Extract choices[0] as response
            response = str(data['response']['body']['choices'][0]['message']['content'])

            # Emit the results
            self.response_generated.emit(response)

            if not os.path.exists(proj_dir):
                print("Project directory from batch custom_id field '" + str(proj_dir) + "' was not found. Using patch from GUI: " + str(self.project_dir))
                proj_dir = self.project_dir
                return

            if editor_mode:
                # Create an instance of ResponseFilesParser and call the parsing function
                parser = ResponseFilesParser(proj_dir)
                parser.parse_response_and_update_files_on_disk(response)

            usage = str(data['response']['body']['usage'])
            self.status_changed.emit(usage)

        except Exception as e:
            error_message = f"Error retrieving batch results: {str(e)}"
            self.response_generated.emit(error_message)

    def delete_batch_job(self, batch_id):
        # Delete batch job (stub implementation)
        print(f"Deleting batch job with ID: {batch_id}")

        try:
            # Find the batch in the stored jobs list
            if self.jobs is None:
                raise ValueError("No jobs available. Please call get_completed_batch_jobs first.")

            batch = next((job for job in self.jobs.data if job.id == batch_id), None)

            if not batch:
                raise ValueError(f"Batch job with ID {batch_id} not found.")

            input_file_id = batch.input_file_id
            output_file_id = batch.output_file_id

            print("Deleting job file " + input_file_id)
            self.client.files.delete(input_file_id)

            print("Deleting job file " + output_file_id)
            self.client.files.delete(output_file_id)

            try:
                print("Deleting job " + batch_id)
                self.client.batches.delete(output_file_id)
            except Exception:
                error_message = f"Files are deleted, but the batch can't be deleted since openAI API currently doesn't support it"
                self.response_generated.emit(error_message)

            print("Done")

        except Exception as e:
            error_message = f"Error deleting batch results: {str(e)}"
            self.response_generated.emit(error_message)

    def is_o1_model(self, model_name):
        # Assuming that "o1" models have a specific naming pattern, e.g., they contain "o1" in their names.
        return 'o1' in model_name.lower()

    def get_role_for_model(self, model_name):
        if self.is_o1_model(model_name):
            return 'assistant'
        else:
            return 'system'
