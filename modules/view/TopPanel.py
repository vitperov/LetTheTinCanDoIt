from PyQt5.QtWidgets import QWidget, QLabel, QHBoxLayout

class TopPanel(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        # Create a layout and label for the panel with margins minimized
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self.label = QLabel("Project directory:")
        layout.addWidget(self.label)

        # Set the layout to the widget
        self.setLayout(layout)

    def update_directory(self, directory):
        """
        Slot to update the project directory label text.
        """
        self.label.setText(f"Project directory: {directory}")
