from PyQt5.QtWidgets import QWidget, QVBoxLayout, QGroupBox, QComboBox, QLabel, QTextEdit, QPushButton, QHBoxLayout
from PyQt5.QtCore import pyqtSignal
from modules.view.RoleSelector import RoleSelector

class RequestPanel(QWidget):
    send_request_signal = pyqtSignal(str, str, str)  # Signal for sending a single request
    send_batch_request_signal = pyqtSignal(str, str, str)  # Signal for sending a batch request

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
        self.send_button.clicked.connect(self.handle_send)

        # Create "Send Batch" button for batch request
        self.send_batch_button = QPushButton('Send Batch')
        self.send_batch_button.clicked.connect(self.handle_send_batch)

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

    def handle_send(self):
        request = self.request_input.toPlainText()  # Use the toPlainText() method for QTextEdit
        if request:
            # Clear the input field
            self.request_input.clear()

            # Get the selected role string from RoleSelector
            role_description = self.role_selector.get_role_string()

            # Get the selected model from the dropdown
            selected_model = self.model_dropdown.currentText()

            # Combine the request without adding the role description
            full_request = request

            # Emit the signal for a single request
            self.send_request_signal.emit(selected_model, role_description, full_request)

    def handle_send_batch(self):
        request_template = self.request_input.toPlainText()  # Use the toPlainText() method for QTextEdit
        if request_template:
            # Clear the input field
            self.request_input.clear()

            # Get the selected role string from RoleSelector
            role_description = self.role_selector.get_role_string()

            # Get the selected model from the dropdown
            selected_model = self.model_dropdown.currentText()

            # Emit the signal for a batch request
            self.send_batch_request_signal.emit(selected_model, role_description, request_template)