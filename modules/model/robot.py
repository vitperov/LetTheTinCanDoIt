import os
import json
from PyQt5.QtCore import QObject, pyqtSignal

class RobotModel(QObject):
    response = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.scenarios = []
        self.load_scenarios()

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

    def runOneStep(self, initial_state):
        # stub implementation
        self.response.emit(initial_state)
