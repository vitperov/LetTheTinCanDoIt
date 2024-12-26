from PyQt5.QtWidgets import QWidget, QVBoxLayout, QGroupBox, QComboBox, QLabel, QTextEdit, QPushButton, QHBoxLayout, QLineEdit, QRadioButton, QButtonGroup, QCheckBox, QScrollArea, QGridLayout
from PyQt5.QtCore import pyqtSignal
from modules.view.RoleSelector import RoleSelector

class RequestPanel(QWidget):
    send_request_signal = pyqtSignal(str, str, str, bool)  # Signal for sending a single request with editorMode
    send_batch_request_signal = pyqtSignal(str, str, str, str, bool)  # Signal for sending a batch request with description and editorMode

    def __init__(self, available_models):
        super().__init__()
        self.available_models = available_models
        self.additional_requests = []
        self.checkbox_list = []
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

        # Create radio buttons for mode selection
        mode_groupbox = QGroupBox("Mode")
        mode_layout = QHBoxLayout()  # Changed to QHBoxLayout to place buttons in one row

        self.mode_button_group = QButtonGroup()

        self.editor_mode_button = QRadioButton("Editor mode")
        self.editor_mode_button.setChecked(True)  # Default selection
        self.answer_mode_button = QRadioButton("Answer mode (do not modify my files)")

        self.mode_button_group.addButton(self.editor_mode_button)
        self.mode_button_group.addButton(self.answer_mode_button)

        mode_layout.addWidget(self.editor_mode_button)
        mode_layout.addWidget(self.answer_mode_button)

        mode_groupbox.setLayout(mode_layout)
        layout.addWidget(mode_groupbox)

        # ---------- Request GroupBox ----------
        request_groupbox = QGroupBox("Request")
        request_layout = QVBoxLayout()

        # Add RoleSelector widget to the request layout
        self.role_selector = RoleSelector()
        request_layout.addWidget(self.role_selector)

        self.request_label = QLabel('Request:')
        self.request_input = QTextEdit()  # Change to QTextEdit for multiline input
        # Set plain text format for request input
        self.request_input.setAcceptRichText(False)

        # ---------- Additional Requests GroupBox ----------
        self.additional_requests_checkbox_layout = QGridLayout()

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
        request_layout.addLayout(self.additional_requests_checkbox_layout)
        request_layout.addLayout(batch_layout)  # Add batch layout first (occupying the entire line)
        request_layout.addLayout(button_layout)  # Add Send button layout below batch layout

        # Set layout to the groupbox
        request_groupbox.setLayout(request_layout)
        layout.addWidget(request_groupbox)

        # Set the main layout for the RequestPanel
        self.setLayout(layout)

    def set_additional_requests(self, additional_requests):
        """
        Sets the additional requests and creates corresponding checkboxes.
        """
        self.additional_requests = additional_requests
        # Clear existing checkboxes
        for checkbox in self.checkbox_list:
            self.additional_requests_checkbox_layout.removeWidget(checkbox)
            checkbox.deleteLater()
        self.checkbox_list = []

        # Create new checkboxes in two columns
        for index, request in enumerate(self.additional_requests):
            checkbox = QCheckBox(request)
            row = index // 2  # Compute row index
            col = index % 2   # Compute column index
            self.additional_requests_checkbox_layout.addWidget(checkbox, row, col)
            self.checkbox_list.append(checkbox)

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
            # Get the selected role string from RoleSelector
            role_description = self.role_selector.get_role_string()

            # Get the selected model from the dropdown
            selected_model = self.model_dropdown.currentText()

            # Check which mode is selected
            editor_mode = self.editor_mode_button.isChecked()

            # Collect checked additional requests
            checked_additional_requests = [cb.text() for cb in self.checkbox_list if cb.isChecked()]

            # Append checked additional requests to the main request
            if checked_additional_requests:
                request_text += "\n\n" + "\n".join(checked_additional_requests)

            # Clear the input field
            self.request_input.clear()

            # Emit the signal with description if it's for the batch request, else emit without description
            if is_batch:
                signal.emit(selected_model, role_description, request_text, description_text, editor_mode)
            else:
                signal.emit(selected_model, role_description, request_text, editor_mode)
