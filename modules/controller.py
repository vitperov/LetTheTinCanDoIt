from PyQt5.QtCore import QObject, pyqtSignal
from modules.model import ProjectGPTModel
from modules.view.view import ProjectGPTView

class ProjectGPTController(QObject):
    send_request = pyqtSignal(str, str, list, str)  # Signal with model, role_string, chosen files, and full request

    def __init__(self):
        super().__init__()
        self.model = ProjectGPTModel()
        self.view = ProjectGPTView(self.model.available_models)  # Pass available models to the view

        # Connect signals between the view, controller, and model
        self.view.send_request.connect(self.handle_send_request)
        self.send_request.connect(self.model.generate_response)
        self.model.response_generated.connect(self.view.update_response)

    def handle_send_request(self, model, role_string, chosen_files, full_request):
        # Pass all received arguments to the model via the signal
        self.send_request.emit(model, role_string, chosen_files, full_request)
