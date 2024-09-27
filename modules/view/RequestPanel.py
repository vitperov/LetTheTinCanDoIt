from PyQt5.QtWidgets import QWidget, QVBoxLayout, QGroupBox, QComboBox, QLabel, QTextEdit, QPushButton, QHBoxLayout, QLineEdit
from PyQt5.QtCore import pyqtSignal
from modules.view.RoleSelector import RoleSelector

class RequestPanel(QWidget):
    send_request_signal = pyqtSignal(str, str, str)  # Signal for sending a single request (model, role, request)
    send_batch_request_signal = pyqtSignal(str, str, str, str)  # Signal for sending a batch request with description (model, role, request, description)

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

        # Create a layout for the "Send Batch" button and "Description" field
        batch_layout = QHBoxLayout()

        # Add "Description" label and input field
        self.description_label = QLabel('Description:')
        self.description_input = QLineEdit()  # Input for description

        # Create "Send Batch" button for batch request
        self.send_batch_button = QPushButton('Send Batch')
        self.send_batch_button.clicked.connect(self.handle_send_batch)

        # Add widgets to the batch layout
        batch_layout.addWidget(self.description_label)
        batch_layout.addWidget(self.description_input)
        batch_layout.addWidget(self.send_batch_button)

        # Create "Send" button for single request
        self.send_button = QPushButton('Send')
        self.send_button.clicked.connect(self.handle_send)

        # Create a layout to hold the "Send" button
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.send_button)

        # Add widgets to the request layout
        request_layout.addWidget(self.request_label)
        request_layout.addWidget(self.request_input)
        request_layout.addLayout(batch_layout)  # Add batch layout first (occupying the entire line)
        request_layout.addLayout(button_layout)  # Add Send button layout below batch layout

        # Set layout to the groupbox
        request_groupbox.setLayout(request_layout)
        layout.addWidget(request_groupbox)

        # Set the main layout for the RequestPanel
        self.setLayout(layout)

    def handle_send(self):
        self.handle_request(self.send_request_signal)

    def handle_send_batch(self):
        # Get the description text from the input field
        description_text = self.description_input.text()

        # Pass the description text as the last parameter of the send_batch_request_signal
        self.handle_request(self.send_batch_request_signal, description_text, True)

    def handle_request(self, signal, description_text='', is_batch=False):
        request_text = self.request_input.toPlainText()  # Use the toPlainText() method for QTextEdit
        if request_text:
            # Clear the input field
            self.request_input.clear()

            # Get the selected role string from RoleSelector
            role_description = self.role_selector.get_role_string()

            # Get the selected model from the dropdown
            selected_model = self.model_dropdown.currentText()

            # Emit the signal with description if it's for the batch request, else emit without description
            if is_batch:
                signal.emit(selected_model, role_description, request_text, description_text)
            else:
                signal.emit(selected_model, role_description, request_text)