from PyQt5.QtCore import QObject, pyqtSignal
from chatgpt_model import ChatGPTModel
from chatgpt_view import ChatGPTView

class ChatGPTController(QObject):
    send_request = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.model = ChatGPTModel('')
        self.view = ChatGPTView()

        self.view.send_request.connect(self.handle_send_request)
        self.send_request.connect(self.model.generate_response)
        self.model.response_generated.connect(self.view.update_response)

    def handle_send_request(self, request, api_key):
        self.model.api_key = api_key
        self.send_request.emit(request)
