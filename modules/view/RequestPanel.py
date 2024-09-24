from PyQt5.QtWidgets import QWidget, QVBoxLayout, QGroupBox, QComboBox, QLabel, QTextEdit, QPushButton, QHBoxLayout
from modules.view.RoleSelector import RoleSelector

class RequestPanel(QWidget):
    def __init__(self, available_models):
        super().__init__()
        self.available_models = available_models
        self.init_ui()

    def init_ui(self):
        # Main layout for the RequestPanel
        layout = QVBoxLayout()

        # ---------- Parameters GroupBox ----------
        parameters_groupbox = QGroupBox("Parameters")
        parameters_layout = QVBoxLayout()

        # Create the dropdown for available models
        self.model_dropdown = QComboBox()
        self.model_dropdown.addItems(self.available_models)
        parameters_layout.addWidget(self.model_dropdown)

        # Set layout to the groupbox
        parameters_groupbox.setLayout(parameters_layout)
        layout.addWidget(parameters_groupbox)

        # ---------- Request GroupBox ----------
        request_groupbox = QGroupBox("Request")
        request_layout = QVBoxLayout()

        # Add RoleSelector widget to the request layout
        self.role_selector = RoleSelector()
        request_layout.addWidget(self.role_selector)

        self.request_label = QLabel('Request:')
        self.request_input = QTextEdit()  # Change to QTextEdit for multiline input

        # Create "Send" button for single request
        self.send_button = QPushButton('Send')

        # Create "Send Batch" button for batch request
        self.send_batch_button = QPushButton('Send Batch')

        # Create a layout to hold both buttons (Send and Send Batch)
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.send_button)
        button_layout.addWidget(self.send_batch_button)

        # Add widgets to the request layout
        request_layout.addWidget(self.request_label)
        request_layout.addWidget(self.request_input)
        request_layout.addLayout(button_layout)  # Move buttons before the response

        # Set layout to the groupbox
        request_groupbox.setLayout(request_layout)
        layout.addWidget(request_groupbox)

        # Set the main layout for the RequestPanel
        self.setLayout(layout)
