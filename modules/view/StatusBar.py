from PyQt5.QtWidgets import QWidget, QStatusBar, QVBoxLayout, QLabel
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QMovie

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

        self.spinner = QLabel()
        self.movie = QMovie("spinner.gif")
        self.spinner.setMovie(self.movie)
        self.spinner.hide()

        self.status_bar.addPermanentWidget(self.spinner)

        layout.addWidget(self.status_bar)
        self.setLayout(layout)

    def update_status(self, status):
        self.status_bar.showMessage(status)
        if "Waiting for" in status or "Uploading" in status or "Sending" in status:
            self.movie.start()
            self.spinner.show()
        else:
            self.movie.stop()
            self.spinner.hide()
