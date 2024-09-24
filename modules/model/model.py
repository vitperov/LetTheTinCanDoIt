from PyQt5.QtCore import QObject, pyqtSignal
from openai import OpenAI
import os
import json
import tempfile
from modules.model.ResponseFilesParser import ResponseFilesParser

class ProjectGPTModel(QObject):
    response_generated = pyqtSignal(str)  # Signal to send the generated response back to the view

    def __init__(self):
        super().__init__()
        self.available_models = ["gpt-4o-mini", "gpt-4o", "o1-preview", "o1-mini"]  # Available model list
        self.api_key = self.load_api_key()  # Load the API key from the settings file
        self.client = OpenAI(api_key=self.api_key)
        self.project_dir = None
        self.chosen_files = []

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

    def make_file_content_text(self, project_dir, chosen_files):
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

                    content = content.replace("`", "[BACKTICK]")

                file_contents.append(f"**{relative_path}**\n```\n{content}\n```\n")

        keepFilenamesRequest = "Please return the content of each file with its corresponding file path. Each file path should be enclosed in double asterisks (**file_path**), followed by the modified content in a code block. The code block should use triple backticks (```) without specifying a language. The content inside the code block should be the file content only, with no additional comments, explanations, or markers. Do not modify or omit the file paths.\n"

        return "\n".join(file_contents) + "\n" + keepFilenamesRequest

    def generate_response(self, model, role_string, full_request):
        """
        Generates a response using the selected model, role_string, project_dir, chosen_files, and full_request.
        """
        try:
            # Construct the messages for the GPT model, with the role_string as the system role
            file_content_text = self.make_file_content_text(self.project_dir, self.chosen_files)
            full_request_with_files = file_content_text + full_request

            messages = [
                {"role": "system", "content": role_string},
                {"role": "user", "content": full_request_with_files}
            ]

            print("Model: " + model)
            print("Role: " + role_string)
            print("Request: " + full_request_with_files)
            print("--------------")

            # Generate response using the selected model
            response = self.client.chat.completions.create(
                model=model,  # Use the selected model here
                messages=messages,
                #temperature=0,
                #max_tokens=16384,
                #n=1,
                #stop=None
            )

            # Extract the generated response from the API result
            generated_response = response.choices[0].message.content
            
            print("Response choices:" + str(len(response.choices)))
            
            print("------------ USAGE ------")
            print(response.usage)
            
            print("------------ UPDATE FILES ------")

            # Create an instance of ResponseFilesParser and call the parsing function
            parser = ResponseFilesParser(self.project_dir, self.chosen_files)
            parser.parse_response_and_update_files_on_disk(generated_response)

            self.response_generated.emit(generated_response)

        except Exception as e:
            error_message = f"Error generating response: {str(e)}"
            self.response_generated.emit(error_message)
            
    def generate_batch_response(self, model, role_string, full_request):
        """
        Generates a response using the batch interface for a single request and stores the temporary file in CWD/tmp/.
        """
        try:
            # Construct the messages for the GPT model, with the role_string as the system role
            file_content_text = self.make_file_content_text(self.project_dir, self.chosen_files)
            full_request_with_files = file_content_text + full_request

            # Define the request body as per the API format
            messages = [
                {"role": "system", "content": role_string},
                {"role": "user", "content": full_request_with_files}
            ]

            # Prepare the batch request in the required format
            batch_request = {
                "custom_id": "request-1",  # Custom ID for tracking the request
                "method": "POST",  # HTTP method
                "url": "/v1/chat/completions",  # API endpoint URL
                "body": {
                    "model": model,  # The selected model
                    "messages": messages,  # The constructed messages
                    #"max_tokens": 1000  # Optional: adjust based on your needs
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
            
            # Ugly batch interface, you need file descriptor and need to create temporary file instead of just passing content directly

            # Upload the file to the API
            with open(temp_file_path, "rb") as file_to_upload:
                batch_input_file = self.client.files.create(
                    file=file_to_upload,
                    purpose="batch"
                )

            # Get the file ID from the uploaded file
            batch_input_file_id = batch_input_file.id
            print("Batch input file ID: " + str(batch_input_file_id))

            # Create a batch job using the uploaded file
            batch_obj = self.client.batches.create(
                input_file_id=batch_input_file_id,
                endpoint="/v1/chat/completions",
                completion_window="24h",
                metadata={
                    "description": "nightly eval job _"
                }
            )

            print("Batch object:")
            print(batch_obj)

            # Emit the batch job as the generated response (for testing)
            self.response_generated.emit(str(batch_obj))

        except Exception as e:
            error_message = f"Error generating batch response: {str(e)}"
            self.response_generated.emit(error_message)
