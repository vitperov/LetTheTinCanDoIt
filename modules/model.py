from PyQt5.QtCore import QObject, pyqtSignal
from openai import OpenAI
import os
import json

class ProjectGPTModel(QObject):
    response_generated = pyqtSignal(str)  # Signal to send the generated response back to the view

    def __init__(self):
        super().__init__()
        # Load the API key from a settings file
        self.api_key = self.load_api_key()
        self.client = OpenAI(api_key=self.api_key)

    def load_api_key(self):
        # Load the API key from a JSON file
        settings_path = os.path.join('settings', 'key.json')
        if os.path.exists(settings_path):
            with open(settings_path, 'r') as f:
                data = json.load(f)
            return data.get('api_key', '')
        return ''

    def generate_response(self, role_string, chosen_files, full_request):
        """
        Generates a response using the role_string, chosen_files, and full_request.
        The role_string will be used in the system message to define the assistant's role.
        """
        try:
            # Construct the messages for the GPT model, with the role_string as the system role
            messages = [
                {"role": "system", "content": role_string},
                {"role": "user", "content": full_request}
            ]
            
            # Generate response using OpenAI's GPT
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
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
