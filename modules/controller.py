from PyQt5.QtCore import QObject, pyqtSignal
from modules.model import ProjectGPTModel
from modules.view.view import ProjectGPTView

class ProjectGPTController(QObject):
    send_request = pyqtSignal(str, list, str)  # Signal with role_string, chosen_files, full_request

    def __init__(self):
        super().__init__()
        self.model = ProjectGPTModel()
        self.view = ProjectGPTView()

        # Connect view signal to controller method
        self.view.send_request.connect(self.handle_send_request)

        # Connect controller signal to model method
        self.send_request.connect(self.model.generate_response)

        # Connect model signal to view update method
        self.model.response_generated.connect(self.view.update_response)

    def handle_send_request(self, role_string, chosen_files, full_request):
        """
        Handles the request signal emitted from the view.
        Passes the role string, list of chosen files, and the full request to the model.
        """
        # Emit all three parameters to the model via the send_request signal
        self.send_request.emit(role_string, chosen_files, full_request)
