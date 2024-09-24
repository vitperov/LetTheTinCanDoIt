from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QTextEdit, QPushButton, QVBoxLayout, QHBoxLayout, QComboBox, QSplitter, QGroupBox, QFormLayout
from PyQt5.QtCore import pyqtSignal, Qt
from modules.view.FilesPanel import FilesPanel
from modules.view.RoleSelector import RoleSelector
from modules.view.BatchesPanel import BatchesPanel  # Import the BatchesPanel

class ProjectGPTView(QWidget):
    # Signals for single and batch requests
    send_request = pyqtSignal(str, str, str, list, str)  # Single: model, role_string, project_dir, selected files, and full request
    send_batch_request = pyqtSignal(str, str, str, list, str)  # Batch: model, role_string, project_dir, file groups, and full request template
    get_completed_batch_jobs = pyqtSignal()  # Signal for getting completed batch jobs

    def __init__(self, available_models):
        super().__init__()
        self.available_models = available_models  # Store available models
        self.init_ui()

    def init_ui(self):
        # Create the main layout as a horizontal layout
        main_layout = QHBoxLayout()

        # Create a splitter to allow resizing between the left and right panels
        splitter = QSplitter(Qt.Horizontal)

        # Left-side layout which includes FilesPanel and BatchesPanel
        left_side_layout = QVBoxLayout()

        # Initialize the FilesPanel widget
        self.left_panel = FilesPanel()

        # Set a minimum width for the FilesPanel so it can't be collapsed completely
        self.left_panel.setMinimumWidth(200)

        # Initialize the BatchesPanel widget
        self.batches_panel = BatchesPanel()

        # Connect the BatchesPanel's get_completed_batch_jobs signal to the view's get_completed_batch_jobs signal
        self.batches_panel.get_completed_batch_jobs.connect(self.get_completed_batch_jobs.emit)

        # Add the FilesPanel and BatchesPanel to the left-side layout
        left_side_layout.addWidget(self.left_panel)
        left_side_layout.addWidget(self.batches_panel)

        # Create a widget to hold the left-side layout and add it to the splitter
        left_side_widget = QWidget()
        left_side_widget.setLayout(left_side_layout)
        splitter.addWidget(left_side_widget)

        # Right panel layout that includes both the "Parameters" and "Request" sections
        right_panel_layout = QVBoxLayout()

        # ---------- Parameters GroupBox ----------
        parameters_groupbox = QGroupBox("Parameters")
        parameters_layout = QVBoxLayout()

        # Create the dropdown for available models
        self.model_dropdown = QComboBox()
        self.model_dropdown.addItems(self.available_models)
        parameters_layout.addWidget(self.model_dropdown)

        # Set layout to the groupbox
        parameters_groupbox.setLayout(parameters_layout)
        right_panel_layout.addWidget(parameters_groupbox)

        # ---------- Request GroupBox ----------
        request_groupbox = QGroupBox("Request")
        request_layout = QVBoxLayout()

        # Add RoleSelector widget to the request layout
        self.role_selector = RoleSelector()
        request_layout.addWidget(self.role_selector)

        self.request_label = QLabel('Request:')
        self.request_input = QTextEdit()  # Change to QTextEdit for multiline input

        self.response_label = QLabel('Response:')
        self.response_display = QTextEdit()
        self.response_display.setReadOnly(True)

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
        request_layout.addWidget(self.response_label)
        request_layout.addWidget(self.response_display)
        request_layout.addLayout(button_layout)

        # Set layout to the groupbox
        request_groupbox.setLayout(request_layout)
        right_panel_layout.addWidget(request_groupbox)

        # Create a right panel widget to hold the right panel layout
        right_panel = QWidget()
        right_panel.setLayout(right_panel_layout)

        # Set a minimum width for the right panel
        right_panel.setMinimumWidth(300)  # Minimum width of 300px for the right panel

        # Add the right panel to the splitter
        splitter.addWidget(right_panel)

        # Set initial sizes for the panels (left panel 400px, right panel takes remaining space)
        splitter.setSizes([250, 800])

        # Prevent panels from collapsing completely by setting the minimum size for the splitter
        splitter.setHandleWidth(1)
        splitter.setChildrenCollapsible(False)  # Disable collapsing

        # Add the splitter to the main layout
        main_layout.addWidget(splitter)

        # Set the initial window size to 1000px wide
        self.resize(1000, 800)  # Set the initial window size to 1000x800px

        self.setLayout(main_layout)
        self.setWindowTitle('ChatGPT Application')
        self.show()

    def handle_send(self):
        request = self.request_input.toPlainText()  # Use the toPlainText() method for QTextEdit
        if request:
            # Clear the input field
            self.request_input.clear()

            # Retrieve the selected files and project directory from the FilesPanel
            project_dir, selected_files = self.left_panel.get_checked_files()

            # Get the selected role string from RoleSelector
            role_description = self.role_selector.get_role_string()

            # Get the selected model from the dropdown
            selected_model = self.model_dropdown.currentText()

            # Combine the request without adding the role description
            full_request = request

            # Show a "Sending request..." message in the response display
            self.response_display.setText('Sending request...')

            # Emit the signal for a single request
            self.send_request.emit(selected_model, role_description, project_dir, selected_files, full_request)

    def handle_send_batch(self):
        request_template = self.request_input.toPlainText()  # Use the toPlainText() method for QTextEdit
        if request_template:
            # Clear the input field
            self.request_input.clear()

            # Retrieve the selected files and project directory from the FilesPanel
            project_dir, selected_files = self.left_panel.get_checked_files()

            # Get the selected role string from RoleSelector
            role_description = self.role_selector.get_role_string()

            # Get the selected model from the dropdown
            selected_model = self.model_dropdown.currentText()

            # Show a "Sending batch request..." message in the response display
            self.response_display.setText('Sending batch request...')

            # Emit the signal for a batch request
            self.send_batch_request.emit(selected_model, role_description, project_dir, selected_files, request_template)

    def update_response(self, response):
        self.response_display.setText(response)
