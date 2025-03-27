import subprocess
import re
from modules.model.serviceProviders.serviceProviderBase import ServiceProviderBase
from modules.model.modelOptions import ModelOptions

def remove_ansi_escape(text):
	ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
	return ansi_escape.sub('', text)


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
                # Skip header line and parse each subsequent line
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

    def get_api_key(self):
        return ""

    def getModelOptions(self, modelName):
        return ModelOptions(supportBatch=False, supportReasoningEffort=False)

    def getRoleForModel(self, modelName):
        return "assistant"
        
    def _generate_response_sync(self, model_context, role_string, full_request, editor_mode, reasoning_effort):
        print("OllamaServiceProvider: Generating response...")
        try:
            model_name = model_context["modelName"].replace("ollama-", "", 1)
            combined_prompt = f"{role_string}\n\n{full_request}"
            
            command = ["ollama", "run", model_name, combined_prompt]
            
            output = subprocess.check_output(
                command,
                stderr=subprocess.STDOUT,
                universal_newlines=True
            )
            
            output = remove_ansi_escape(output)
            
            generated_response = output.strip()
            model_context["status_changed"]("OllamaServiceProvider: Response generated.")
            return (generated_response, "Usage information not available for ollama")
            
        except subprocess.CalledProcessError as e:
            error_msg = f"Ollama command failed: {e.output.strip()}"
            return (error_msg, "Error")
        except Exception as e:
            error_msg = f"Error generating response: {str(e)}"
            return (error_msg, "Error")

    def _generate_batch_response_sync(self, model_context, role_string, full_request, description, editor_mode, reasoning_effort):
        model_context["response_generated"]("Batch functionality is not supported by OllamaServiceProvider")

    def get_completed_batch_jobs(self, model_context):
        model_context["response_generated"]("Batch functionality is not supported by OllamaServiceProvider")

    def get_batch_results(self, model_context, batch_id):
        model_context["response_generated"]("Batch functionality is not supported by OllamaServiceProvider")

    def delete_batch_job(self, model_context, batch_id):
        model_context["response_generated"]("Batch functionality is not supported by OllamaServiceProvider")
