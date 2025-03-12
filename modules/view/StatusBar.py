from PyQt5.QtWidgets import QWidget, QStatusBar, QVBoxLayout
from PyQt5.QtCore import Qt

class StatusBar(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.status_bar = QStatusBar()
        self.status_bar.showMessage("---")

        layout.addWidget(self.status_bar)
        self.setLayout(layout)

    def update_status(self, status):
        self.status_bar.showMessage(status)
