from PyQt5.QtWidgets import QWidget, QStatusBar, QVBoxLayout

class StatusBar(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        # Create a layout for the panel
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)  # Minimize margins for the status bar
        layout.setSpacing(0)  # Minimize spacing within the status bar

        # Create a QStatusBar instance
        self.status_bar = QStatusBar()
        self.status_bar.showMessage("---")  # Set default message

        # Add the QStatusBar to the layout
        layout.addWidget(self.status_bar)

        # Set the layout to the widget
        self.setLayout(layout)

    def update_status(self, status):
        """
        Slot to update the status bar message.
        """
        self.status_bar.showMessage(status)
