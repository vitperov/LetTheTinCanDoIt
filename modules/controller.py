from PyQt5.QtCore import QObject
from modules.model.model import ProjectGPTModel
from modules.view.view import ProjectGPTView

class ProjectGPTController(QObject):
    def __init__(self):
        super().__init__()
        self.model = ProjectGPTModel()
        self.view = ProjectGPTView(self.model.available_models)  # Pass available models to the view

        # Connect signals between the view, controller, and model
        self.view.send_request.connect(self.handle_send_request)
        self.view.send_batch_request.connect(self.handle_send_batch_request)

        # Connect the model's response generation signal to update the view
        self.model.response_generated.connect(self.view.update_response)

    def handle_send_request(self, model, role_string, full_request):
        """
        Handle single file request.
        """
        # Get the selected project directory and chosen files from the view
        project_dir, chosen_files = self.view.left_panel.get_checked_files()
        self.model.set_project_files(project_dir, chosen_files)

        # Directly call the model's method to generate a single response
        self.model.generate_response(model, role_string, full_request)

    def handle_send_batch_request(self, model, role_string, full_request_template):
        """
        Handle batch request for multiple sets of files.
        """
        # Get the selected project directory and chosen files from the view
        project_dir, chosen_files = self.view.left_panel.get_checked_files()
        self.model.set_project_files(project_dir, chosen_files)

        # Directly call the model's method to generate a batch response
        self.model.generate_batch_response(model, role_string, full_request_template)
