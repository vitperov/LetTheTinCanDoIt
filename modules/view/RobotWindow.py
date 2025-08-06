from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QComboBox, QTextEdit

class RobotWindow(QDialog):
    def __init__(self, model, parent=None):
        super().__init__(parent)
        self.model = model
        self.iteration = 0
        self.max_steps = 12
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Robot")
        main_layout = QVBoxLayout()

        # Model selection row
        model_row = QHBoxLayout()
        model_row.addWidget(QLabel("Model"))
        self.model_combo = QComboBox()
        self.model_combo.addItems(self.model.robotModel.getModelNames())
        model_row.addWidget(self.model_combo)
        main_layout.addLayout(model_row)

        # Scenario and Max steps row
        row1 = QHBoxLayout()
        row1.addWidget(QLabel("Scenario"))
        self.scenario_combo = QComboBox()
        self.scenario_combo.addItems(self.model.robotModel.getScenarioNames())
        row1.addWidget(self.scenario_combo)
        row1.addWidget(QLabel("Max steps"))
        self.max_steps_input = QLineEdit(str(self.max_steps))
        row1.addWidget(self.max_steps_input)
        main_layout.addLayout(row1)

        row2 = QHBoxLayout()
        self.run_button = QPushButton("Run")
        row2.addWidget(self.run_button)
        self.iteration_label = QLabel(f"Iteration: {self.iteration}/{self.max_steps}")
        row2.addWidget(self.iteration_label)
        main_layout.addLayout(row2)

        main_layout.addWidget(QLabel("Initial/Current state"))
        self.initial_state_text = QTextEdit()
        main_layout.addWidget(self.initial_state_text)

        main_layout.addWidget(QLabel("LastResponse"))
        self.last_response_text = QTextEdit()
        self.last_response_text.setReadOnly(True)
        main_layout.addWidget(self.last_response_text)

        self.setLayout(main_layout)

        self.scenario_combo.currentIndexChanged.connect(self.onScenarioChanged)
        self.run_button.clicked.connect(self.onRunClicked)
        self.model.robotModel.response.connect(self.onModelResponse)

        self.onScenarioChanged(self.scenario_combo.currentIndex())

    def onScenarioChanged(self, index):
        scenario_name = self.scenario_combo.currentText()
        initial_state = self.model.robotModel.getInitialState(scenario_name)
        self.initial_state_text.setPlainText(initial_state)

    def onRunClicked(self):
        model_name = self.model_combo.currentText()
        scenario_name = self.scenario_combo.currentText()
        initial_state = self.initial_state_text.toPlainText()
        self.model.robotModel.runOneStep(model_name, scenario_name, initial_state)

    def onModelResponse(self, response_str):
        self.last_response_text.setPlainText(response_str)
