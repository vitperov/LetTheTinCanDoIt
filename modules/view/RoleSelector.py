from PyQt5.QtWidgets import QWidget, QComboBox, QLabel, QVBoxLayout, QHBoxLayout, QCheckBox
from PyQt5.QtCore import Qt

class RoleSelector(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        # Create main vertical layout
        layout = QVBoxLayout()

        # Create a horizontal layout for widgets
        main_horizontal_layout = QHBoxLayout()

        # Create checkbox
        self.role_checkbox = QCheckBox()
        main_horizontal_layout.addWidget(self.role_checkbox)
        self.role_checkbox.setChecked(True)

        # Create and add label
        self.label = QLabel('You are senior ')
        main_horizontal_layout.addWidget(self.label)


        # Create first dropdown for programming languages
        self.language_dropdown = QComboBox()
        self.language_dropdown.addItems(['python', 'C++', 'java', 'php', 'QA', 'C#', 'Unity', 'Matlab', 'TypeScript', 'javascript'])
        main_horizontal_layout.addWidget(self.language_dropdown)

        # Create second dropdown for roles
        self.role_dropdown = QComboBox()
        self.role_dropdown.addItems(['developer', 'engineer'])
        main_horizontal_layout.addWidget(self.role_dropdown)

        main_horizontal_layout.setAlignment(Qt.AlignLeft)

        # Add dropdown layout to main layout
        layout.addLayout(main_horizontal_layout)

        # Set layout
        self.setLayout(layout)

    def get_role_string(self):
        """Returns the string 'You are senior {chosen_language} {chosen_role}'."""
        if self.role_checkbox.isChecked():
            chosen_language = self.language_dropdown.currentText()
            chosen_role = self.role_dropdown.currentText()
            return f'You are senior {chosen_language} {chosen_role}.'
        else:
            return ""
