from modules.model.serviceProviders.serviceProviderBase import ServiceProviderBase
from modules.model.modelOptions import ModelOptions
import google.generativeai as genai
import os
import json


class GeminiServiceProvider(ServiceProviderBase):
    def __init__(self, settings=None, api_key=None):
        """
        `settings` should come from get_provider_settings("gemini").
        """
        super().__init__()

        if settings is None:
            settings = {}
        if api_key is not None:
            settings["api_key"] = api_key

        self.settings = settings
        self.api_key = self.settings.get("api_key")

        self.available_models = [
            "gemini-2.0-flash",
            "gemini-2.5-pro-preview-05-06",
            "gemini-2.5-pro-exp-03-25",
            "gemini-2.5-flash-preview-04-17",
        ]
        if self.api_key:
            genai.configure(api_key=self.api_key)

    def getBaseUrl(self):
        return "https://generativelanguage.googleapis.com/v1beta/models"

    def getModelOptions(self, modelName):
        return ModelOptions(supportBatch=False)

    def _generate_response_sync(self, modelName, full_request, status_changed, response_generated, project_dir=None, chosen_files=None):
        try:
            if not self.api_key:
                return ("Error: Gemini API key not configured in settings/key.json", "Error")
            
            model = genai.GenerativeModel(modelName)
            response = model.generate_content(full_request)
            
            if not response.text:
                return ("Error: Empty response from Gemini API", "Error")
                
            return (response.text, "Usage information not available for Gemini")
            
        except Exception as e:
            return (f"Error generating response: {str(e)}", "Error")

    def _generate_batch_response_sync(self, modelName, full_request, description, custom_id, status_changed, response_generated, completed_job_list_updated, project_dir=None, chosen_files=None):
        response_generated("Batch functionality is not supported by GeminiServiceProvider")

    def get_completed_batch_jobs(self, modelName, status_changed, response_generated, completed_job_list_updated, project_dir=None, chosen_files=None):
        response_generated("Batch functionality is not supported by GeminiServiceProvider")

    def get_batch_results(self, modelName, batch_id, status_changed, response_generated, project_dir=None, chosen_files=None):
        response_generated("Batch functionality is not supported by GeminiServiceProvider")

    def delete_batch_job(self, modelName, batch_id, status_changed, response_generated, project_dir=None, chosen_files=None):
        response_generated("Batch functionality is not supported by GeminiServiceProvider")

    def cancel_batch_job(self, modelName, batch_id, status_changed, response_generated, project_dir=None, chosen_files=None):
        response_generated("Batch functionality is not supported by GeminiServiceProvider")

    def delete_all_server_files(self, modelName, status_changed, response_generated, project_dir=None, chosen_files=None):
        response_generated("Batch functionality is not supported by GeminiServiceProvider")
