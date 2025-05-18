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

        row1 = QHBoxLayout()
        row1.addWidget(QLabel("Scenario"))
        self.scenario_combo = QComboBox()
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
