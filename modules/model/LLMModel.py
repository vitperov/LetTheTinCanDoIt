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
            model_context = {
                "project_dir": self.project_dir,
                "chosen_files": self.chosen_files,
                "modelName": self.modelName,
                "status_changed": self.status_changed.emit,
                "response_generated": self.response_generated.emit,
            }
            self.thread_manager.execute_async(
                lambda: self.provider._generate_response_sync(model_context, user_message, editor_mode),
                lambda result: self._handle_generated_response(result),
                lambda e: self.response_generated.emit("Error generating response: " + str(e))
            )
            print("Done. Waiting for the result")
        except Exception as e:
            self.response_generated.emit("Error generating response: " + str(e))

    def _handle_generated_response(self, result):
        generated_response, usage = result
        self.response_generated.emit(generated_response)
        self.status_changed.emit(str(usage))

    def generate_batch_response_async(self, role_string, full_request, description, editor_mode):
        try:
            user_message = role_string + "\n\n"
            if self.project_dir and self.chosen_files and editor_mode:
                formatter = FileContentFormatter()
                user_message += formatter.make_file_content_text(self.project_dir, self.chosen_files, editor_mode)
            user_message += full_request
            model_context = {
                "project_dir": self.project_dir,
                "chosen_files": self.chosen_files,
                "modelName": self.modelName,
                "status_changed": self.status_changed.emit,
                "response_generated": self.response_generated.emit,
                "completed_job_list_updated": self.completed_job_list_updated.emit,
            }
            self.thread_manager.execute_async(
                lambda: self.provider._generate_batch_response_sync(model_context, user_message, description, editor_mode),
                lambda result: self.response_generated.emit(str(result)),
                lambda e: self.response_generated.emit("Error generating batch response: " + str(e))
            )
        except Exception as e:
            self.response_generated.emit("Error generating batch response: " + str(e))

    def get_completed_batch_jobs(self):
        try:
            model_context = {
                "project_dir": self.project_dir,
                "chosen_files": self.chosen_files,
                "modelName": self.modelName,
                "status_changed": self.status_changed.emit,
                "response_generated": self.response_generated.emit,
                "completed_job_list_updated": self.completed_job_list_updated.emit,
            }
            self.provider.get_completed_batch_jobs(model_context)
        except Exception as e:
            self.response_generated.emit("Error retrieving completed batch jobs: " + str(e))

    def get_batch_results(self, batch_id):
        try:
            model_context = {
                "project_dir": self.project_dir,
                "chosen_files": self.chosen_files,
                "modelName": self.modelName,
                "status_changed": self.status_changed.emit,
                "response_generated": self.response_generated.emit,
            }
            self.provider.get_batch_results(model_context, batch_id)
        except Exception as e:
            self.response_generated.emit("Error retrieving batch results: " + str(e))

    def delete_batch_job(self, batch_id):
        try:
            model_context = {
                "project_dir": self.project_dir,
                "chosen_files": self.chosen_files,
                "modelName": self.modelName,
                "status_changed": self.status_changed.emit,
                "response_generated": self.response_generated.emit,
            }
            self.provider.delete_batch_job(model_context, batch_id)
        except Exception as e:
            self.response_generated.emit("Error deleting batch results: " + str(e))
