import openai
from PyQt5.QtCore import QObject, pyqtSignal

class ChatGPTModel(QObject):
    response_generated = pyqtSignal(str)

    def __init__(self, api_key):
        super().__init__()
        openai.api_key = api_key

    def generate_response(self, prompt):
        response = openai.Completion.create(
            engine="text-davinci-002",
            prompt=prompt,
            max_tokens=100
        )
        generated_response = response.choices[0].text.strip()
        self.response_generated.emit(generated_response)
