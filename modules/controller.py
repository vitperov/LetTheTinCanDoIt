from PyQt5.QtCore import QObject
from modules.model.model import ProjectGPTModel
from modules.view.view import ProjectGPTView
from modules.view.FilesPanel import FilesPanel

class ProjectGPTController(QObject):
    def __init__(self):
        super().__init__()
        self.model = ProjectGPTModel()
        self.view = ProjectGPTView(self.model.available_models)
        self.view.set_model(self.model)

        self.view.left_panel.set_model(self.model)

        self.view.request_panel.send_request_signal.connect(self.handle_send_request)
        self.view.request_panel.send_batch_request_signal.connect(self.handle_send_batch_request)
        self.view.batches_panel.get_completed_batch_jobs.connect(self.handle_get_completed_batch_jobs)
        self.view.batches_panel.get_results.connect(self.handle_get_batch_results)
        self.view.batches_panel.delete_job.connect(self.handle_delete_batch_job)
        self.view.batches_panel.cancel_job.connect(self.handle_cancel_batch_job)

        self.model.response_generated.connect(self.view.update_response)
        self.model.completed_job_list_updated.connect(self.view.batches_panel.completed_job_list_updated)
        self.model.status_changed.connect(self.view.status_bar.update_status)
        self.view.left_panel.proj_dir_changed.connect(self.view.top_panel.update_directory)

        last_project_directory = self.model.historyModel.get_last_project_directory()
        self.view.top_panel.update_directory(last_project_directory)
        
        additional_requests = self.model.get_additional_requests()
        self.view.set_additional_requests(additional_requests)

        self.view.request_panel.model_dropdown.currentTextChanged.connect(self.handle_model_change)
        self.handle_model_change(self.view.request_panel.model_dropdown.currentText())

    def handle_send_request(self, model, role_string, full_request, editor_mode):
        project_dir, chosen_files = self.view.left_panel.get_checked_files()
        self.model.set_project_files(project_dir, chosen_files)
        self.model.requestHistoryModel.update_request_history(full_request)
        self.model.getCurrentModel().generate_response_async(role_string, full_request, editor_mode)

    def handle_send_batch_request(self, model, role_string, full_request_template, description, editor_mode):
        project_dir, chosen_files = self.view.left_panel.get_checked_files()
        self.model.set_project_files(project_dir, chosen_files)
        self.model.requestHistoryModel.update_request_history(full_request_template)
        self.model.getCurrentModel().generate_batch_response_async(role_string, full_request_template, description, editor_mode)

    def handle_get_completed_batch_jobs(self):
        self.model.getCurrentModel().get_completed_batch_jobs()

    def handle_get_batch_results(self, batch_id):
        self.model.getCurrentModel().get_batch_results(batch_id)

    def handle_delete_batch_job(self, batch_id):
        self.model.getCurrentModel().delete_batch_job(batch_id)
        
    def handle_cancel_batch_job(self, batch_id):
        self.model.cancel_batch_job(batch_id)
        
    def handle_model_change(self, model_name):
        self.model.switchModel(model_name)
        model_options = self.model.get_model_options(model_name)
        self.view.request_panel.set_batch_support(model_options.supportBatch)
        self.view.batches_panel.set_batch_support(model_options.supportBatch)
