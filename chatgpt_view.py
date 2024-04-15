import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QTextEdit
from PyQt5.QtCore import pyqtSignal

class ChatGPTView(QWidget):
    send_request = pyqtSignal(str, str)

    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.token_label = QLabel('Access Token Key:')
        self.token_input = QLineEdit()

        self.request_label = QLabel('Request:')
        self.request_input = QLineEdit()

        self.response_label = QLabel('Response:')
        self.response_display = QTextEdit()
        self.response_display.setReadOnly(True)

        self.send_button = QPushButton('Send')
        self.send_button.clicked.connect(self.handle_send)

        layout = QVBoxLayout()
        layout.addWidget(self.token_label)
        layout.addWidget(self.token_input)
        layout.addWidget(self.request_label)
        layout.addWidget(self.request_input)
        layout.addWidget(self.response_label)
        layout.addWidget(self.response_display)
        layout.addWidget(self.send_button)

        self.setLayout(layout)
        self.setWindowTitle('ChatGPT Application')
        self.show()

    def handle_send(self):
        request = self.request_input.text()
        if request:
            self.request_input.clear()
            self.response_display.setText('Sending request...')
            self.send_request.emit(request, self.token_input.text())

    def update_response(self, response):
        self.response_display.setText(response)
