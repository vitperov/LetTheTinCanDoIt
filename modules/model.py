from PyQt5.QtCore import QObject, pyqtSignal
from openai import OpenAI
import os
import json
import re

class ProjectGPTModel(QObject):
    response_generated = pyqtSignal(str)  # Signal to send the generated response back to the view

    def __init__(self):
        super().__init__()
        self.available_models = ["gpt-4o-mini", "gpt-4o", "o1-preview", "o1-mini"]  # Available model list
        self.api_key = self.load_api_key()  # Load the API key from the settings file
        self.client = OpenAI(api_key=self.api_key)

    def load_api_key(self):
        # Load the API key from a JSON file
        settings_path = os.path.join('settings', 'key.json')
        if os.path.exists(settings_path):
            with open(settings_path, 'r') as f:
                data = json.load(f)
            return data.get('api_key', '')
        return ''

    def make_file_content_text(self, chosen_files):
        """
        Creates a text block from the chosen files to be appended to the request.
        """
        if not chosen_files:
            return ""

        file_contents = []
        header = "Here is my file" if len(chosen_files) == 1 else "Here are my files"
        file_contents.append(header)

        for file_path in chosen_files:
            if os.path.exists(file_path):
                with open(file_path, 'r') as file:
                    content = file.read()
                file_contents.append(f"**{file_path}**\n```\n{content}\n```\n")
                
        keepFilenamesRequest = "Please display the filenames in your response exactly as I provide them before each file.\n"

        return "\n".join(file_contents) + "\n" + keepFilenamesRequest

    def generate_response(self, model, role_string, chosen_files, full_request):
        """
        Generates a response using the selected model, role_string, chosen_files, and full_request.
        """
        try:
            # Construct the messages for the GPT model, with the role_string as the system role
            file_content_text = self.make_file_content_text(chosen_files)
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
                temperature=0,
                max_tokens=1024,
                n=1,
                stop=None
            )

            # Extract the generated response from the API result
            generated_response = response.choices[0].message.content

            # Call the function to parse and update files on disk
            self.parse_response_and_update_files_on_disk(generated_response, chosen_files)

            self.response_generated.emit(generated_response)

        except Exception as e:
            error_message = f"Error generating response: {str(e)}"
            self.response_generated.emit(error_message)

    def parse_response_and_update_files_on_disk(self, response, chosen_files):
        """
        Parses the response to find modified files and updates them on disk.
        This is a stub function for now, but it will eventually be implemented.
        """
        print("Parsing response to update files...")
        print(response)
        
        # TODO: Implement the actual logic here to parse response and update files.
        # For now, we attempt to extract filenames from the response as a starting point.
        filenames_in_response = self.extract_filenames_from_response(response, chosen_files)
        print("Extracted filenames:", filenames_in_response)

    def extract_filenames_from_response(self, response, chosen_files):
        """
        Tries to extract filenames from the response. For now, we assume the response contains
        the filenames provided earlier, potentially in code blocks or as plain text.
        """
        extracted_files = []
        
        # Example: We'll assume the filenames appear in code blocks in the response, so we use a regex.
        for file_path in chosen_files:
            # We escape the file path to handle any special regex characters in file paths
            pattern = re.escape(file_path)
            if re.search(pattern, response):
                extracted_files.append(file_path)
        
        return extracted_files
