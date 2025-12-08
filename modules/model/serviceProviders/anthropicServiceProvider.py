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
        return ModelOptions(supportBatch=True)

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
        if not self.api_key:
            response_generated("Error: Anthropic API key not configured in settings/key.json")
            return
        if not self.client:
            self.client = anthropic.Anthropic(api_key=self.api_key)
        status_changed("Creating batch request ...")
        print(f"customId = {custom_id}")
        max_tokens = self.settings.get("max_tokens", 4096)
        request_item = {
            "custom_id": custom_id,
            "params": {
                "model": modelName,
                "messages": [{"role": "user", "content": full_request}],
                "max_tokens": max_tokens,
            },
        }
        batch = self.client.messages.batches.create(requests=[request_item])
        return batch

    def get_completed_batch_jobs(self, modelName, status_changed, response_generated, completed_job_list_updated, project_dir=None, chosen_files=None):
        if not self.api_key:
            response_generated("Error: Anthropic API key not configured in settings/key.json")
            return
        if not self.client:
            self.client = anthropic.Anthropic(api_key=self.api_key)
        try:
            status_changed("Getting batch jobs list ...")
            page = self.client.messages.batches.list()
            batches = getattr(page, 'data', []) or []
            batch_ids = []
            descriptions = []
            for b in batches:
                batch_ids.append(getattr(b, 'id', ''))
                status = getattr(b, 'processing_status', 'unknown')
                rc = getattr(b, 'request_counts', {}) or {}
                if hasattr(rc, 'get'):
                    succeeded = rc.get('succeeded', 0)
                    processing = rc.get('processing', 0)
                    errored = rc.get('errored', 0)
                    canceled = rc.get('canceled', 0)
                    expired = rc.get('expired', 0)
                else:
                    succeeded = getattr(rc, 'succeeded', 0)
                    processing = getattr(rc, 'processing', 0)
                    errored = getattr(rc, 'errored', 0)
                    canceled = getattr(rc, 'canceled', 0)
                    expired = getattr(rc, 'expired', 0)
                desc = (
                    f"Status: {status}, "
                    f"succeeded: {succeeded}, processing: {processing}, "
                    f"errored: {errored}, canceled: {canceled}, expired: {expired}"
                )
                descriptions.append(desc)
            if batch_ids:
                result_str = "\n".join([f"* {bid}: {desc}" for bid, desc in zip(batch_ids, descriptions)])
                response_generated(result_str)
            else:
                response_generated("No batch jobs found.")
            completed_job_list_updated(batch_ids, descriptions)
            status_changed("Done")
        except Exception as e:
            response_generated("Error retrieving batch jobs: " + str(e))

    def get_batch_results(self, modelName, batch_id, status_changed, response_generated, project_dir=None, chosen_files=None):
        if not self.api_key:
            return ("Error: Anthropic API key not configured in settings/key.json", "Error")
        if not self.client:
            self.client = anthropic.Anthropic(api_key=self.api_key)
        try:
            status_changed("Retrieving batch results ...")
            batch = self.client.messages.batches.retrieve(batch_id)
            responses = getattr(batch, 'responses', None) or getattr(batch, 'results', None)
            if not responses:
                raise Exception("No responses found in batch.")
            response = responses[0]
            generated_response = response.content[0].text
            usage_info = f"Input tokens: {response.usage.input_tokens}, Output tokens: {response.usage.output_tokens}"
            return (generated_response, usage_info)
        except Exception as e:
            return (f"Error retrieving batch results: {str(e)}", "Error")

    def delete_batch_job(self, modelName, batch_id, status_changed, response_generated, project_dir=None, chosen_files=None):
        if not self.api_key:
            response_generated("Error: Anthropic API key not configured in settings/key.json")
            return
        if not self.client:
            self.client = anthropic.Anthropic(api_key=self.api_key)
        try:
            status_changed(f"Deleting batch job {batch_id} ...")
            deleted = self.client.messages.batches.delete(batch_id)
            response_generated(f"Batch job {batch_id} deleted. Deleted id: {deleted.id}")
        except Exception as e:
            response_generated("Error deleting batch job: " + str(e))

    def cancel_batch_job(self, modelName, batch_id, status_changed, response_generated, project_dir=None, chosen_files=None):
        if not self.api_key:
            response_generated("Error: Anthropic API key not configured in settings/key.json")
            return
        if not self.client:
            self.client = anthropic.Anthropic(api_key=self.api_key)
        try:
            status_changed(f"Canceling batch job {batch_id} ...")
            canceled = self.client.messages.batches.cancel(batch_id)
            response_generated(f"Batch job {batch_id} canceled. Canceled id: {canceled.id}")
        except Exception as e:
            response_generated("Error canceling batch job: " + str(e))

    def delete_all_server_files(self, modelName, status_changed, response_generated, project_dir=None, chosen_files=None):
        response_generated("Batch functionality is not supported by AnthropicServiceProvider")
