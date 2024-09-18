from PyQt5.QtCore import QObject, pyqtSignal
from modules.model import *
from modules.view.view import *

class ProjectGPTController(QObject):
    send_request = pyqtSignal(str, list)

    def __init__(self):
        super().__init__()
        self.model = ProjectGPTModel()
        self.view = ProjectGPTView()

        self.view.send_request.connect(self.handle_send_request)
        self.send_request.connect(self.model.generate_response)
        self.model.response_generated.connect(self.view.update_response)

    def handle_send_request(self, request, chosenFiles):
        self.send_request.emit(request, chosenFiles)
