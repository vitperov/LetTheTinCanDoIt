from PyQt5.QtCore import QObject, pyqtSignal
import os
import json
import tempfile
from datetime import datetime
from openai import OpenAI
from modules.model.ResponseFilesParser import ResponseFilesParser
from modules.model.ThreadManager import ThreadManager
from modules.model.FileContentFormatter import FileContentFormatter

class LLMModel(QObject):
    response_generated = pyqtSignal(str)
    completed_job_list_updated = pyqtSignal(list, list)
    status_changed = pyqtSignal(str)

    def __init__(self, provider, modelName):
        super().__init__()
        self.provider = provider
        self.modelName = modelName
        self.thread_manager = ThreadManager()
        self.project_dir = None
        self.chosen_files = []
        self.completed_batches = []
        self.completed_jobs_descriptions = []

    # REMOVED get_api_key - handled in model.py and passed to providers via constructor

    def set_project_files(self, project_dir, chosen_files):
        self.project_dir = project_dir
        self.chosen_files = chosen_files

    def make_file_content_text(self, project_dir, chosen_files, editorMode):
        formatter = FileContentFormatter()
        return formatter.make_file_content_text(project_dir, chosen_files, editorMode)

    def generate_response_async(self, role_string, full_request, editor_mode):
        try:
            self.status_changed.emit("Sending the request ...")
            print("Sending the request in a new thread")
            user_message = role_string + "\n\n"
            if self.project_dir and self.chosen_files and editor_mode:
                formatter = FileContentFormatter()
                user_message += formatter.make_file_content_text(self.project_dir, self.chosen_files, editor_mode)
            user_message += full_request
            self.thread_manager.execute_async(
                lambda: self.provider._generate_response_sync(
                    self.modelName, 
                    user_message, 
                    self.status_changed.emit, 
                    self.response_generated.emit,
                    self.project_dir,
                    self.chosen_files
                ),
                lambda result: self._handle_generated_response(result, editor_mode),
                lambda e: self.response_generated.emit("Error generating response: " + str(e))
            )
            print("Done. Waiting for the result")
        except Exception as e:
            self.response_generated.emit("Error generating response: " + str(e))

    def _handle_generated_response(self, result, editor_mode):
        generated_response, usage = result
        if editor_mode:
            parser = ResponseFilesParser(self.project_dir)
            parser.parse_response_and_update_files_on_disk(generated_response)
        self.response_generated.emit(generated_response)
        self.status_changed.emit(str(usage))

    def generate_batch_response_async(self, role_string, full_request, description, editor_mode):
        try:
            user_message = role_string + "\n\n"
            if self.project_dir and self.chosen_files and editor_mode:
                formatter = FileContentFormatter()
                user_message += formatter.make_file_content_text(self.project_dir, self.chosen_files, editor_mode)
            user_message += full_request
            # Compose custom_id here with proper editor_mode value
            custom_id = f"{self.project_dir}|{editor_mode}"
            self.thread_manager.execute_async(
                lambda: self.provider._generate_batch_response_sync(
                    self.modelName,
                    user_message,
                    description,
                    custom_id,
                    self.status_changed.emit,
                    self.response_generated.emit,
                    self.completed_job_list_updated.emit,
                    self.project_dir,
                    self.chosen_files
                ),
                lambda result: self.response_generated.emit(str(result)),
                lambda e: self.response_generated.emit("Error generating batch response: " + str(e))
            )
        except Exception as e:
            self.response_generated.emit("Error generating batch response: " + str(e))

    def get_completed_batch_jobs(self):
        try:
            self.provider.get_completed_batch_jobs(
                self.modelName,
                self.status_changed.emit,
                self.response_generated.emit,
                self.completed_job_list_updated.emit,
                self.project_dir,
                self.chosen_files
            )
        except Exception as e:
            self.response_generated.emit("Error retrieving completed batch jobs: " + str(e))

    def get_batch_results(self, batch_id):
        try:
            def _handle_results(response_text, usage, editor_mode):
                if editor_mode:
                    parser = ResponseFilesParser(self.project_dir)
                    parser.parse_response_and_update_files_on_disk(response_text)
                self.response_generated.emit(response_text)
                self.status_changed.emit(usage)
            # Now, get_batch_results will return response_text, usage, editor_mode
            result = self.provider.get_batch_results(
                self.modelName,
                batch_id,
                self.status_changed.emit,
                self.response_generated.emit,
                self.project_dir,
                self.chosen_files
            )
            if result:
                response_text, usage, editor_mode = result
                _handle_results(response_text, usage, editor_mode)
        except Exception as e:
            self.response_generated.emit("Error retrieving batch results: " + str(e))

    def delete_batch_job(self, batch_id):
        try:
            self.provider.delete_batch_job(
                self.modelName,
                batch_id,
                self.status_changed.emit,
                self.response_generated.emit,
                self.project_dir,
                self.chosen_files
            )
        except Exception as e:
            self.response_generated.emit("Error deleting batch results: " + str(e))
