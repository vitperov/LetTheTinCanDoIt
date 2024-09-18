import json
from openai import OpenAI
from PyQt5.QtCore import QObject, pyqtSignal

class ProjectGPTModel(QObject):
    response_generated = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        config_path='settings/key.json'
        api_key = self.load_api_key(config_path)
        self.client = OpenAI(
            api_key=api_key
        )

    def load_api_key(self, config_path):
        try:
            print(config_path)
            with open(config_path, 'r') as file:
                data = json.load(file)
                return data.get('api_key', None)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Error loading API key: {e}")
            return None

    def generate_response(self, prompt, chosenFiles):
        #if not self.api_key:
        #    self.response_generated.emit("Error: API key not found or invalid.")
        #    return
        
        print("Attaching files:" + str(chosenFiles))

        try:
            response = self.client.chat.completions.create(
                model="gpt-4-turbo-2024-04-09",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0,
                max_tokens=1024,
                n=1,
                stop=None
            )
            generated_response = response.choices[0].message.content
        except BaseException as e:
            generated_response = 'Error: ' + str(e)

        self.response_generated.emit(generated_response)
