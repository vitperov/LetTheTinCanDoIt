import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QTextEdit, QPushButton, QVBoxLayout, QHBoxLayout, QComboBox, QSplitter
from PyQt5.QtCore import pyqtSignal, Qt
from modules.view.FilesPanel import FilesPanel
from modules.view.RoleSelector import RoleSelector

class ProjectGPTView(QWidget):
    send_request = pyqtSignal(str, str, list, str)  # Signal with selected model, role_string, selected files, and full request

    def __init__(self, available_models):
        super().__init__()
        self.available_models = available_models  # Store available models
        self.init_ui()

    def init_ui(self):
        # Create the main layout as a horizontal layout
        main_layout = QHBoxLayout()

        # Create a splitter to allow resizing between the left and right panels
        splitter = QSplitter(Qt.Horizontal)

        # Initialize the left panel with FilesPanel widget
        self.left_panel = FilesPanel()

        # Set a minimum width for the left panel so it can't be collapsed completely
        self.left_panel.setMinimumWidth(200)  # Minimum width of 200px for the left panel

        # Add the left panel to the splitter
        splitter.addWidget(self.left_panel)

        # Right panel layout that includes the RoleSelector and other input fields
        right_panel_layout = QVBoxLayout()

        # Create the dropdown for available models
        self.model_dropdown = QComboBox()
        self.model_dropdown.addItems(self.available_models)
        right_panel_layout.addWidget(self.model_dropdown)  # Add the dropdown to the layout

        # Add RoleSelector widget to the right panel layout
        self.role_selector = RoleSelector()
        right_panel_layout.addWidget(self.role_selector)

        self.request_label = QLabel('Request:')
        self.request_input = QTextEdit()  # Change to QTextEdit for multiline input

        self.response_label = QLabel('Response:')
        self.response_display = QTextEdit()
        self.response_display.setReadOnly(True)

        self.send_button = QPushButton('Send')
        self.send_button.clicked.connect(self.handle_send)

        # Add widgets to the right panel layout
        right_panel_layout.addWidget(self.request_label)
        right_panel_layout.addWidget(self.request_input)  # Add the QTextEdit instead of QLineEdit
        right_panel_layout.addWidget(self.response_label)
        right_panel_layout.addWidget(self.response_display)
        right_panel_layout.addWidget(self.send_button)

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

            # Retrieve the selected files from the FilesPanel
            selected_files = self.left_panel.get_checked_files()

            # Get the selected role string from RoleSelector
            role_description = self.role_selector.get_role_string()

            # Get the selected model from the dropdown
            selected_model = self.model_dropdown.currentText()

            # Combine the request without adding the role description
            full_request = request

            # Show a "Sending request..." message in the response display
            self.response_display.setText('Sending request...')

            # Emit the signal with the selected model, role_description, selected_files, and full_request
            self.send_request.emit(selected_model, role_description, selected_files, full_request)

    def update_response(self, response):
        self.response_display.setText(response)
