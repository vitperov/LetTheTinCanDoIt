from PyQt5.QtCore import QObject, pyqtSignal
from modules.model import ProjectGPTModel
from modules.view.view import ProjectGPTView

class ProjectGPTController(QObject):
    send_request = pyqtSignal(str, str, str, list, str)  # For single response: model, role_string, project_dir, chosen files, full request
    send_batch_request = pyqtSignal(str, str, str, list, str)  # For batch response: model, role_string, project_dir, file groups, full request template

    def __init__(self):
        super().__init__()
        self.model = ProjectGPTModel()
        self.view = ProjectGPTView(self.model.available_models)  # Pass available models to the view

        # Connect signals between the view, controller, and model
        self.view.send_request.connect(self.handle_send_request)
        self.view.send_batch_request.connect(self.handle_send_batch_request)

        # Single response request
        self.send_request.connect(self.model.generate_response)

        # Batch response request
        self.send_batch_request.connect(self.model.generate_batch_response)

        self.model.response_generated.connect(self.view.update_response)

    def handle_send_request(self, model, role_string, project_dir, chosen_files, full_request):
        """
        Handle single file request.
        """
        # Pass all received arguments to the model via the signal for a single response
        self.send_request.emit(model, role_string, project_dir, chosen_files, full_request)

    def handle_send_batch_request(self, model, role_string, project_dir, chosen_files, full_request_template):
        """
        Handle batch request for multiple sets of files.
        """
        # Emit signal for batch response with multiple file groups
        self.send_batch_request.emit(model, role_string, project_dir, chosen_files, full_request_template)

