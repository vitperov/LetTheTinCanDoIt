from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QComboBox, QGroupBox, QHBoxLayout
from PyQt5.QtCore import pyqtSignal

class BatchesPanel(QWidget):
    # Signal to trigger the action of getting completed batch jobs
    get_completed_batch_jobs = pyqtSignal()

    # Signal to trigger the action of fetching results for a selected batch job
    get_results = pyqtSignal(str)

    # Signal to trigger the action of deleting a selected batch job
    delete_job = pyqtSignal(str)

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

        # Horizontal layout to hold both "Get Results" and "Delete Job" buttons
        buttons_layout = QHBoxLayout()

        # "Get Results" button
        self.get_results_button = QPushButton("Get Results")
        buttons_layout.addWidget(self.get_results_button)

        # "Delete Job" button
        self.delete_job_button = QPushButton("Delete Job")
        buttons_layout.addWidget(self.delete_job_button)

        # Add the buttons layout to the groupbox layout
        groupbox_layout.addLayout(buttons_layout)

        # Connect the button click signal to the "get_completed_batch_jobs" signal
        self.get_jobs_button.clicked.connect(self.get_completed_batch_jobs.emit)

        # Connect the "Get Results" button to the method that emits the get_results signal
        self.get_results_button.clicked.connect(self.emit_selected_batch_id_for_results)

        # Connect the "Delete Job" button to the method that emits the delete_job signal
        self.delete_job_button.clicked.connect(self.emit_selected_batch_id_for_deletion)

        # Set the layout to the groupbox
        batch_groupbox.setLayout(groupbox_layout)

        # Add the groupbox to the main layout
        layout.addWidget(batch_groupbox)

        # Set the layout to the panel
        self.setLayout(layout)

    def completed_job_list_updated(self, completed_batches):
        """
        Updates the batch dropdown with the list of completed batch jobs.

        Args:
            completed_batches (list of str): A list of completed batch job IDs.
        """
        print("Completed job list updated:", completed_batches)

        # Clear the current items in the dropdown
        self.batch_dropdown.clear()

        # Add new items to the dropdown if the completed_batches list is not empty
        if (completed_batches):
            self.batch_dropdown.addItems(completed_batches)
        else:
            # If the list is empty add a placeholder to indicate no jobs
            self.batch_dropdown.addItem("No completed jobs available")

    def emit_selected_batch_id_for_results(self):
        """
        Emits the 'get_results' signal with the currently selected batch job ID.
        """
        # Get the currently selected batch job ID from the dropdown
        selected_batch_id = self.batch_dropdown.currentText()

        # Emit the 'get_results' signal with the selected batch job ID
        if selected_batch_id != "No completed jobs available":
            self.get_results.emit(selected_batch_id)

    def emit_selected_batch_id_for_deletion(self):
        """
        Emits the 'delete_job' signal with the currently selected batch job ID.
        """
        # Get the currently selected batch job ID from the dropdown
        selected_batch_id = self.batch_dropdown.currentText()

        # Emit the 'delete_job' signal with the selected batch job ID
        if selected_batch_id != "No completed jobs available":
            self.delete_job.emit(selected_batch_id)
