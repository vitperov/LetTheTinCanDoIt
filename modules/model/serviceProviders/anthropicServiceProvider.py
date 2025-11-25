from modules.model.serviceProviders.serviceProviderBase import ServiceProviderBase
from modules.model.modelOptions import ModelOptions
import anthropic
import os
import json


class AnthropicServiceProvider(ServiceProviderBase):
    def __init__(self, settings=None, api_key=None):
        """
        `settings` should come from get_provider_settings("anthropic").
        """
        super().__init__()

        if settings is None:
            settings = {}
        if api_key is not None:
            settings["api_key"] = api_key

        self.settings = settings
        self.api_key = self.settings.get("api_key")

        self.available_models = [
            "claude-sonnet-4-5",
            "claude-haiku-4-5",
            "claude-opus-4-5",
        ]

        if self.api_key:
            self.client = anthropic.Anthropic(api_key=self.api_key)
        else:
            self.client = None

    def getBaseUrl(self):
        return "https://api.anthropic.com"

    def getModelOptions(self, modelName):
        return ModelOptions(supportBatch=False)

    def _generate_response_sync(self, modelName, full_request, status_changed, response_generated, project_dir=None, chosen_files=None):
        try:
            if not self.api_key:
                return ("Error: Anthropic API key not configured in settings/key.json", "Error")
            
            if not self.client:
                self.client = anthropic.Anthropic(api_key=self.api_key)
            
            status_changed("Waiting for the response ...")
            
            response = self.client.messages.create(
                model=modelName,
                max_tokens=4096,
                messages=[
                    {"role": "user", "content": full_request}
                ]
            )
            
            generated_response = response.content[0].text
            
            # Construct usage information similar to other providers
            usage_info = f"Input tokens: {response.usage.input_tokens}, Output tokens: {response.usage.output_tokens}"
            
            return (generated_response, usage_info)
            
        except Exception as e:
            return (f"Error generating response: {str(e)}", "Error")

    def _generate_batch_response_sync(self, modelName, full_request, description, custom_id, status_changed, response_generated, completed_job_list_updated, project_dir=None, chosen_files=None):
        response_generated("Batch functionality is not supported by AnthropicServiceProvider")

    def get_completed_batch_jobs(self, modelName, status_changed, response_generated, completed_job_list_updated, project_dir=None, chosen_files=None):
        response_generated("Batch functionality is not supported by AnthropicServiceProvider")

    def get_batch_results(self, modelName, batch_id, status_changed, response_generated, project_dir=None, chosen_files=None):
        response_generated("Batch functionality is not supported by AnthropicServiceProvider")

    def delete_batch_job(self, modelName, batch_id, status_changed, response_generated, project_dir=None, chosen_files=None):
        response_generated("Batch functionality is not supported by AnthropicServiceProvider")

    def cancel_batch_job(self, modelName, batch_id, status_changed, response_generated, project_dir=None, chosen_files=None):
        response_generated("Batch functionality is not supported by AnthropicServiceProvider")

    def delete_all_server_files(self, modelName, status_changed, response_generated, project_dir=None, chosen_files=None):
        response_generated("Batch functionality is not supported by AnthropicServiceProvider")
