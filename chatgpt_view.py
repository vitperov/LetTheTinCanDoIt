import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QTextEdit, QHBoxLayout
from PyQt5.QtCore import pyqtSignal
from FilesPanel import *

class ChatGPTView(QWidget):
    send_request = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        # Create the main layout as a horizontal layout
        main_layout = QHBoxLayout()

        self.left_panel = FilesPanel()
        main_layout.addWidget(self.left_panel)

        self.request_label = QLabel('Request:')
        self.request_input = QLineEdit()

        self.response_label = QLabel('Response:')
        self.response_display = QTextEdit()
        self.response_display.setReadOnly(True)

        self.send_button = QPushButton('Send')
        self.send_button.clicked.connect(self.handle_send)

        # Add widgets to the right panel layout
        right_panel_layout = QVBoxLayout()
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
            self.request_input.clear()
            self.response_display.setText('Sending request...')
            self.send_request.emit(request)

    def update_response(self, response):
        self.response_display.setText(response)
