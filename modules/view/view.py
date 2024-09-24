from PyQt5.QtWidgets import QApplication, QWidget, QTextEdit, QVBoxLayout, QHBoxLayout, QSplitter, QGroupBox
from PyQt5.QtCore import pyqtSignal, Qt
from modules.view.FilesPanel import FilesPanel
from modules.view.BatchesPanel import BatchesPanel  # Import the BatchesPanel
from modules.view.RequestPanel import RequestPanel  # Import the new RequestPanel

class ProjectGPTView(QWidget):
    # Signals for single and batch requests
    send_request = pyqtSignal(str, str, str)  # Single: model, role_string, and full request
    send_batch_request = pyqtSignal(str, str, str)  # Batch: model, role_string, and full request
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

        # Create the RequestPanel and add it to the right panel
        self.request_panel = RequestPanel(self.available_models)

        # Connect signals from RequestPanel to ProjectGPTView
        self.request_panel.send_button.clicked.connect(self.handle_send)
        self.request_panel.send_batch_button.clicked.connect(self.handle_send_batch)

        # Right panel layout that includes both the RequestPanel and Response section
        right_panel_layout = QVBoxLayout()

        # Add RequestPanel to right layout
        right_panel_layout.addWidget(self.request_panel)

        # ---------- Response GroupBox ----------
        response_groupbox = QGroupBox("Response")
        response_layout = QVBoxLayout()

        self.response_display = QTextEdit()
        self.response_display.setReadOnly(True)

        # Add response display to the response layout
        response_layout.addWidget(self.response_display)

        # Set layout to the groupbox
        response_groupbox.setLayout(response_layout)
        right_panel_layout.addWidget(response_groupbox)

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
        request = self.request_panel.request_input.toPlainText()  # Use the toPlainText() method for QTextEdit
        if request:
            # Clear the input field
            self.request_panel.request_input.clear()

            # Get the selected role string from RoleSelector
            role_description = self.request_panel.role_selector.get_role_string()

            # Get the selected model from the dropdown
            selected_model = self.request_panel.model_dropdown.currentText()

            # Combine the request without adding the role description
            full_request = request

            # Show a "Sending request..." message in the response display
            self.response_display.setText('Sending request...')

            # Emit the signal for a single request
            self.send_request.emit(selected_model, role_description, full_request)

    def handle_send_batch(self):
        request_template = self.request_panel.request_input.toPlainText()  # Use the toPlainText() method for QTextEdit
        if request_template:
            # Clear the input field
            self.request_panel.request_input.clear()

            # Get the selected role string from RoleSelector
            role_description = self.request_panel.role_selector.get_role_string()

            # Get the selected model from the dropdown
            selected_model = self.request_panel.model_dropdown.currentText()

            # Show a "Sending batch request..." message in the response display
            self.response_display.setText('Sending batch request...')

            # Emit the signal for a batch request
            self.send_batch_request.emit(selected_model, role_description, request_template)

    def update_response(self, response):
        self.response_display.setText(response)
