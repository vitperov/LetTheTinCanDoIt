from PyQt5.QtWidgets import QWidget, QComboBox, QLabel, QVBoxLayout

class RoleSelector(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        # Create layout
        layout = QVBoxLayout()

        # Create and add label
        self.label = QLabel('You are senior ')
        layout.addWidget(self.label)

        # Create first dropdown for programming languages
        self.language_dropdown = QComboBox()
        self.language_dropdown.addItems(['python', 'C++', 'java', 'php', 'QA'])
        layout.addWidget(self.language_dropdown)

        # Create second dropdown for roles
        self.role_dropdown = QComboBox()
        self.role_dropdown.addItems(['developer', 'engineer'])
        layout.addWidget(self.role_dropdown)

        # Set layout
        self.setLayout(layout)

    def get_role_string(self):
        """Returns the string 'You are senior {chosen_language} {chosen_role}'."""
        chosen_language = self.language_dropdown.currentText()
        chosen_role = self.role_dropdown.currentText()
        return f'You are senior {chosen_language} {chosen_role}.'
