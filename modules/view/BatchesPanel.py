# BatchesPanel.py
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QComboBox, QGroupBox

from PyQt5.QtCore import pyqtSignal

class BatchesPanel(QWidget):
    # Signal to trigger the action of getting completed batch jobs
    get_completed_batch_jobs = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        # Create the main layout for the panel
        layout = QVBoxLayout()

        # Create a GroupBox titled "Batch results"
        batch_groupbox = QGroupBox("Batch results")
        groupbox_layout = QVBoxLayout()

        # First line: Button to get completed batch jobs
        self.get_jobs_button = QPushButton("Get completed batch jobs")
        groupbox_layout.addWidget(self.get_jobs_button)

        # Second line: Dropdown for displaying batch job IDs and "Get Results" button
        self.batch_dropdown = QComboBox()  # Dropdown for displaying batch jobs
        groupbox_layout.addWidget(self.batch_dropdown)

        self.get_results_button = QPushButton("Get Results")
        groupbox_layout.addWidget(self.get_results_button)

        # Connect the button click signal to the `get_completed_batch_jobs` signal
        self.get_jobs_button.clicked.connect(self.get_completed_batch_jobs.emit)

        # Set the layout to the groupbox
        batch_groupbox.setLayout(groupbox_layout)

        # Add the groupbox to the main layout
        layout.addWidget(batch_groupbox)

        # Set the layout to the panel
        self.setLayout(layout)
