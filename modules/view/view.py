import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QTextEdit, QHBoxLayout
from PyQt5.QtCore import pyqtSignal
from modules.view.FilesPanel import *
from modules.view.RoleSelector import *

class ProjectGPTView(QWidget):
    send_request = pyqtSignal(str, list)  # Signal with request and chosen files

    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        # Create the main layout as a horizontal layout
        main_layout = QHBoxLayout()

        # Initialize the left panel with FilesPanel widget
        self.left_panel = FilesPanel()
        main_layout.addWidget(self.left_panel)

        # Right panel layout that includes the RoleSelector and other input fields
        right_panel_layout = QVBoxLayout()

        # Add RoleSelector widget to the right panel layout
        self.role_selector = RoleSelector()
        right_panel_layout.addWidget(self.role_selector)

        self.request_label = QLabel('Request:')
        self.request_input = QLineEdit()

        self.response_label = QLabel('Response:')
        self.response_display = QTextEdit()
        self.response_display.setReadOnly(True)

        self.send_button = QPushButton('Send')
        self.send_button.clicked.connect(self.handle_send)

        # Add widgets to the right panel layout
        right_panel_layout.addWidget(self.request_label)
        right_panel_layout.addWidget(self.request_input)
        right_panel_layout.addWidget(self.response_label)
        right_panel_layout.addWidget(self.response_display)
        right_panel_layout.addWidget(self.send_button)

        # Create a right panel widget to hold the right panel layout
        right_panel = QWidget()
        right_panel.setLayout(right_panel_layout)

        # Add the right panel to the main layout
        main_layout.addWidget(right_panel)

        self.setLayout(main_layout)
        self.setWindowTitle('ChatGPT Application')
        self.show()

    def handle_send(self):
        request = self.request_input.text()
        if request:
            # Clear the input field
            self.request_input.clear()

            # Retrieve the selected files from the FilesPanel
            selected_files = self.left_panel.get_checked_files()

            # Get the selected role string from RoleSelector
            role_description = self.role_selector.get_role_string()

            # Combine the role description with the request
            full_request = f"{role_description} {request}"

            # Show a "Sending request..." message in the response display
            self.response_display.setText('Sending request...')

            # Emit the signal with the full request and selected files
            self.send_request.emit(full_request, selected_files)

    def update_response(self, response):
        self.response_display.setText(response)
