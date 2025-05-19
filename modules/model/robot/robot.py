import os
import json
from PyQt5.QtCore import QObject, pyqtSignal

class RobotModel(QObject):
    response = pyqtSignal(str)

    def __init__(self, llm_model=None):
        super().__init__()
        self.llm_model = llm_model
        self.available_models = self.llm_model.available_models if self.llm_model else []
        self.scenarios = []
        self.load_scenarios()

    def getModelNames(self):
        return self.available_models

    def load_scenarios(self):
        path = os.path.join('settings', 'robot.json')
        if os.path.exists(path):
            try:
                with open(path, 'r') as f:
                    data = json.load(f)
                self.scenarios = data
            except:
                self.scenarios = []
        else:
            self.scenarios = []

    def getScenarioNames(self):
        return [item.get('name', '') for item in self.scenarios]

    def getInitialState(self, scenario_name):
        for item in self.scenarios:
            if item.get('name', '') == scenario_name:
                return item.get('initial_state', '')
        return ''

    def runOneStep(self, model_name, scenario_name, initial_state):
        # find the scenario definition
        scenario = next((s for s in self.scenarios if s.get('name') == scenario_name), None)
        if not scenario:
            self.response.emit(f"ERROR: Scenario '{scenario_name}' not found.")
            return

        base_request = scenario.get('request', '')
        full_request = base_request + "\n\n" + initial_state

        if not self.llm_model:
            self.response.emit("ERROR: No LLM model configured.")
            return

        try:
            response_text, _usage = self.llm_model.generate_simple_response_sync(model_name, full_request)
            parsed = self.parseResponse(response_text)
            self.response.emit(parsed)
        except Exception as e:
            self.response.emit(f"ERROR: Exception during LLM call: {e}")

    def parseResponse(self, response_str):
        # parse ACTION and STATE lines if present
        action = ""
        state = ""
        lines = response_str.splitlines()
        for line in lines:
            if line.startswith("ACTION:"):
                action = line[len("ACTION:"):].strip()
            if line.startswith("STATE:"):
                state = line[len("STATE:"):].strip()
        if action or state:
            return f"ACTION: {action}\nSTATE: {state}"
        return response_str
