import os
import json
from PyQt5.QtCore import QObject, pyqtSignal
from git import Repo
from git.exc import InvalidGitRepositoryError
from modules.model.ResponseFilesParser import ResponseFilesParser
from modules.model.ThreadManager import ThreadManager
from modules.model.FileContentFormatter import FileContentFormatter
from modules.model.ProjectMeta.ProjectMeta import ProjectMeta
from modules.model.serviceProviders.openAIServiceProvider import OpenAIServiceProvider
from modules.model.serviceProviders.deepSeekServiceProvider import DeepSeekServiceProvider
from modules.model.serviceProviders.ollamaServiceProvider import OllamaServiceProvider
from modules.model.serviceProviders.geminiServiceProvider import GeminiServiceProvider
from modules.model.serviceProviders.anthropicServiceProvider import AnthropicServiceProvider
from modules.model.constants import FILES_LIST_INTRO


def get_provider_settings(provider_name: str) -> dict:
    """
    Return configuration dictionary for the given provider.

    Expected JSON structure in settings/key.json:

    {
        "openai": {
            "api_key": "...",
            "hide_models": "...",
            "enabled": true
        },
        "deepseek": {
            "api_key": "...",
            "enabled": false
        },
        ...
    }
    """
    settings_path = os.path.join('settings', 'key.json')
    if os.path.exists(settings_path):
        try:
            with open(settings_path, 'r') as f:
                data = json.load(f)
            return data.get(provider_name.lower(), {})
        except Exception:
            # If file is corrupted or unreadable – return empty dict
            return {}
    return {}


class LLMModel(QObject):
    response_generated = pyqtSignal(str)
    completed_job_list_updated = pyqtSignal(list, list)
    status_changed = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.service_providers = []

        # Load settings for every provider
        openai_settings = get_provider_settings("openai")
        deepseek_settings = get_provider_settings("deepseek")
        gemini_settings = get_provider_settings("gemini")
        ollama_settings = get_provider_settings("ollama")
        anthropic_settings = get_provider_settings("anthropic")

        # Initialise providers with their settings dictionaries if enabled
        if openai_settings.get("enabled", True):
            self.service_providers.append(OpenAIServiceProvider(settings=openai_settings))

        if deepseek_settings.get("enabled", True):
            self.service_providers.append(DeepSeekServiceProvider(settings=deepseek_settings))

        if ollama_settings.get("enabled", True):
            # Ollama currently doesn't require settings argument
            self.service_providers.append(OllamaServiceProvider())

        if gemini_settings.get("enabled", True):
            self.service_providers.append(GeminiServiceProvider(settings=gemini_settings))

        if anthropic_settings.get("enabled", True):
            self.service_providers.append(AnthropicServiceProvider(settings=anthropic_settings))

        self.available_models = []
        for provider in self.service_providers:
            self.available_models.extend(provider.getAvailableModels())
        self.thread_manager = ThreadManager()
        self.project_dir = None
        self.chosen_files = []
        self.completed_batches = []
        self.completed_jobs_descriptions = []

    def get_provider_for_model(self, modelName):
        for provider in self.service_providers:
            if provider.hasModel(modelName):
                return provider
        raise ValueError(f"No service provider found for model: {modelName}")

    def get_model_options(self, model_name):
        provider = self.get_provider_for_model(model_name)
        return provider.getModelOptions(model_name)

    def set_project_dir(self, project_dir):
        self.project_dir = project_dir

    def set_project_files(self, chosen_files):
        self.chosen_files = chosen_files

    def make_file_content_text(self, project_dir, chosen_files, editorMode):
        formatter = FileContentFormatter()
        return formatter.make_file_content_text(project_dir, chosen_files, editorMode)

    def _build_user_message(self, role_string, full_request, editor_mode, include_files_list, attach_diff):
        parts = []
        if include_files_list:
            if self.project_dir:
                meta = ProjectMeta(self.project_dir)
                files = meta.getAll_project_files()
            else:
                files = []
            files_text = "\n".join(files)
            parts.append(FILES_LIST_INTRO + "\n" + files_text)
        if attach_diff:
            if self.project_dir:
                try:
                    repo = Repo(self.project_dir)
                    diff_text = repo.git.diff('HEAD~1', 'HEAD')
                    parts.append("Here is last commit diff:\n" + diff_text)
                except InvalidGitRepositoryError:
                    print(f"No git repository found at {self.project_dir}, cannot attach diff.")
                except Exception as e:
                    print(f"Error getting git diff: {e}")
        parts.append(role_string)
        if self.project_dir and self.chosen_files:
            formatter = FileContentFormatter()
            file_text = formatter.make_file_content_text(
                self.project_dir, self.chosen_files, editor_mode
            )
            if file_text:
                parts.append(file_text)
        parts.append(full_request)
        return "\n\n".join(parts)

    def generate_response_async(self, modelName, role_string, full_request, editor_mode, request_options):
        try:
            include = getattr(request_options, 'includeFilesList', False)
            print(f"Include files list in request: {include}")
            attach_diff = getattr(request_options, 'attachLastCommitDiff', False)
            print(f"Attach last commit diff in request: {attach_diff}")
            self.status_changed.emit("Sending the request ...")
            user_message = self._build_user_message(role_string, full_request, editor_mode, include, attach_diff)
            print(f"Model: {modelName}")
            print(f"Request: {user_message}")
            provider = self.get_provider_for_model(modelName)
            self.thread_manager.execute_async(
                lambda: provider._generate_response_sync(
                    modelName,
                    user_message,
                    self.status_changed.emit,
                    self.response_generated.emit,
                    self.project_dir,
                    self.chosen_files
                ),
                lambda result: self._handle_generated_response(result, editor_mode),
                lambda e: self.response_generated.emit("Error generating response: " + str(e))
            )
        except Exception as e:
            self.response_generated.emit("Error generating response: " + str(e))

    def _handle_generated_response(self, result, editor_mode):
        generated_response, usage = result
        if editor_mode:
            parser = ResponseFilesParser(self.project_dir)
            parser.parse_response_and_update_files_on_disk(generated_response)
        self.response_generated.emit(generated_response)
        self.status_changed.emit(str(usage))

    def generate_batch_response_async(self, modelName, role_string, full_request, description, editor_mode, request_options):
        try:
            include = getattr(request_options, 'includeFilesList', False)
            print(f"Include files list in batch request: {include}")
            attach_diff = getattr(request_options, 'attachLastCommitDiff', False)
            print(f"Attach last commit diff in batch request: {attach_diff}")
            user_message = self._build_user_message(role_string, full_request, editor_mode, include, attach_diff)
            custom_id = "true" if editor_mode else "false"
            provider = self.get_provider_for_model(modelName)
            self.thread_manager.execute_async(
                lambda: provider._generate_batch_response_sync(
                    modelName,
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

    def get_completed_batch_jobs(self, modelName):
        try:
            provider = self.get_provider_for_model(modelName)
            provider.get_completed_batch_jobs(
                modelName,
                self.status_changed.emit,
                self.response_generated.emit,
                self.completed_job_list_updated.emit,
                self.project_dir,
                self.chosen_files
            )
        except Exception as e:
            self.response_generated.emit("Error retrieving completed batch jobs: " + str(e))

    def get_batch_results(self, modelName, batch_id):
        try:
            def _handle_results(response_text, usage, editor_mode):
                if editor_mode:
                    parser = ResponseFilesParser(self.project_dir)
                    parser.parse_response_and_update_files_on_disk(response_text)
                self.response_generated.emit(response_text)
                self.status_changed.emit(usage)
            provider = self.get_provider_for_model(modelName)
            result = provider.get_batch_results(
                modelName,
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

    def delete_batch_job(self, modelName, batch_id):
        try:
            provider = self.get_provider_for_model(modelName)
            provider.delete_batch_job(
                modelName,
                batch_id,
                self.status_changed.emit,
                self.response_generated.emit,
                self.project_dir,
                self.chosen_files
            )
        except Exception as e:
            self.response_generated.emit("Error deleting batch results: " + str(e))

    def cancel_batch_job(self, modelName, batch_id):
        try:
            provider = self.get_provider_for_model(modelName)
            provider.cancel_batch_job(
                modelName,
                batch_id,
                self.status_changed.emit,
                self.response_generated.emit,
                self.project_dir,
                self.chosen_files
            )
        except Exception as e:
            self.response_generated.emit("Error canceling batch job: " + str(e))

    def generate_simple_response_sync(self, modelName, request, printRequest=True):
        if printRequest:
            print(f"Model: {modelName}")
            print(f"Request: {request}")
        provider = self.get_provider_for_model(modelName)
        return provider._generate_response_sync(
            modelName,
            request,
            lambda status: None,
            lambda response: None,
            None,
            None
        )

    def generate_simple_response_async(self, modelName, request):
        try:
            self.status_changed.emit("Sending simple request ...")
            print(f"Model: {modelName}")
            print(f"Request: {request}")
            provider = self.get_provider_for_model(modelName)
            def _run():
                return provider._generate_response_sync(
                    modelName,
                    request,
                    self.status_changed.emit,
                    self.response_generated.emit,
                    None,
                    None
                )
            def _handle_result(result):
                generated_response, usage = result
                self.response_generated.emit(generated_response)
                self.status_changed.emit(str(usage))
            def _handle_error(e):
                self.response_generated.emit("Error generating simple response: " + str(e))
            self.thread_manager.execute_async(_run, _handle_result, _handle_error)
        except Exception as e:
            self.response_generated.emit("Error generating simple response: " + str(e))
