import subprocess
import re
from modules.model.serviceProviders.serviceProviderBase import ServiceProviderBase
from modules.model.modelOptions import ModelOptions
from modules.model.FileContentFormatter import FileContentFormatter

def remove_ansi_escape(text):
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    return ansi_escape.sub('', text)

def remove_progress_symbols(text):
    return re.sub(r'[\u2800-\u28FF]', '', text)

class OllamaServiceProvider(ServiceProviderBase):
    def __init__(self):
        super().__init__()
        try:
            output = subprocess.check_output(["ollama", "list"], stderr=subprocess.STDOUT, universal_newlines=True)
            lines = output.strip().splitlines()
            if len(lines) < 2:
                print("Warning: No models found in ollama list output")
                self.available_models = []
            else:
                models = []
                for line in lines[1:]:
                    parts = line.split()
                    if parts:
                        model_name = parts[0]
                        models.append("ollama-" + model_name)
                self.available_models = models
        except Exception as e:
            print("Warning: Failed to retrieve ollama models: " + str(e))
            self.available_models = []

    def getBaseUrl(self):
        return ""

    def getModelOptions(self, modelName):
        return ModelOptions(supportBatch=False)

    def _generate_response_sync(self, modelName, full_request, status_changed, response_generated, project_dir=None, chosen_files=None):
        print("OllamaServiceProvider: Generating response...")
        combined_prompt = full_request
        try:
            model_name = modelName.replace("ollama-", "", 1)
            command = ["ollama", "run", model_name, combined_prompt]
            output = subprocess.check_output(
                command,
                stderr=subprocess.STDOUT,
                universal_newlines=True
            )
            output = remove_ansi_escape(output)
            output = remove_progress_symbols(output)
            generated_response = output.strip()
            status_changed("OllamaServiceProvider: Response generated.")
            return (generated_response, "Usage information not available for ollama")
        except subprocess.CalledProcessError as e:
            error_msg = f"Ollama command failed: {e.output.strip()}"
            return (error_msg, "Error")
        except Exception as e:
            error_msg = f"Error generating response: {str(e)}"
            return (error_msg, "Error")

    def _generate_batch_response_sync(self, modelName, full_request, description, custom_id, status_changed, response_generated, completed_job_list_updated, project_dir=None, chosen_files=None):
        response_generated("Batch functionality is not supported by OllamaServiceProvider")

    def get_completed_batch_jobs(self, modelName, status_changed, response_generated, completed_job_list_updated, project_dir=None, chosen_files=None):
        response_generated("Batch functionality is not supported by OllamaServiceProvider")

    def get_batch_results(self, modelName, batch_id, status_changed, response_generated, project_dir=None, chosen_files=None):
        response_generated("Batch functionality is not supported by OllamaServiceProvider")

    def delete_batch_job(self, modelName, batch_id, status_changed, response_generated, project_dir=None, chosen_files=None):
        response_generated("Batch functionality is not supported by OllamaServiceProvider")

    def cancel_batch_job(self, modelName, batch_id, status_changed, response_generated, project_dir=None, chosen_files=None):
        response_generated("Batch functionality is not supported by OllamaServiceProvider")

    def delete_all_server_files(self, modelName, status_changed, response_generated, project_dir=None, chosen_files=None):
        response_generated("Batch functionality is not supported by OllamaServiceProvider")
