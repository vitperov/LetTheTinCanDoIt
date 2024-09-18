from PyQt5.QtCore import QObject, pyqtSignal
from openai import OpenAI
import os
import json

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

    def generate_response(self, model, role_string, chosen_files, full_request):
        """
        Generates a response using the selected model, role_string, chosen_files, and full_request.
        """
        try:
            # Construct the messages for the GPT model, with the role_string as the system role
            messages = [
                {"role": "system", "content": role_string},
                {"role": "user", "content": full_request}
            ]
            
            print("Model: " + model)
            print("Role: " + role_string)
            print("Request: " + full_request)
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
            self.response_generated.emit(generated_response)

        except Exception as e:
            error_message = f"Error generating response: {str(e)}"
            self.response_generated.emit(error_message)
