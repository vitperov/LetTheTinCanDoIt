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

        self.get_results_button = QPushButton("Get Results")
        buttons_layout.addWidget(self.get_results_button)

        self.delete_job_button = QPushButton("Delete Job")
        buttons_layout.addWidget(self.delete_job_button)

        groupbox_layout.addLayout(buttons_layout)

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

    def completed_job_list_updated(self, completed_batches, completed_descriptions):
        """
        Updates the batch dropdown with the list of completed batch jobs.

        Args:
            completed_batches (list of str): A list of completed batch job IDs.
            completed_descriptions (list of str): A list of completed job descriptions.
        """
        print("Completed job list updated:", completed_batches, completed_descriptions)

        # Clear the current items in the dropdown
        self.batch_dropdown.clear()

        # Add new items to the dropdown with descriptions as shown text
        if completed_batches and completed_descriptions and len(completed_batches) == len(completed_descriptions):
            for batch_id, description in zip(completed_batches, completed_descriptions):
                index = self.batch_dropdown.count()  # Get the current count to be used as an index
                self.batch_dropdown.addItem(description)  # Add the description as visible item text
                self.batch_dropdown.setItemData(index, batch_id)  # Store batch_id as the data associated with this item
        else:
            # If the list is empty add a placeholder to indicate no jobs
            self.batch_dropdown.addItem("No completed jobs available")

    def emit_selected_batch_id_for_results(self):
        """
        Emits the 'get_results' signal with the currently selected batch job ID.
        """
        # Get the currently selected index first
        selected_index = self.batch_dropdown.currentIndex()

        # Retrieve the batch ID using the selected index data
        selected_batch_id = self.batch_dropdown.itemData(selected_index)

        # Emit the 'get_results' signal if selected_batch_id is not None and not the placeholder text
        if selected_batch_id is not None:
            self.get_results.emit(selected_batch_id)

    def emit_selected_batch_id_for_deletion(self):
        """
        Emits the 'delete_job' signal with the currently selected batch job ID.
        """
        # Get the currently selected index first
        selected_index = self.batch_dropdown.currentIndex()

        # Retrieve the batch ID using the selected index data
        selected_batch_id = self.batch_dropdown.itemData(selected_index)

        # Emit the 'delete_job' signal if selected_batch_id is not None and not the placeholder text
        if selected_batch_id is not None:
            self.delete_job.emit(selected_batch_id)

    def set_batch_support(self, supportBatch):
        """
        Enables or disables the entire batch panel based on supportBatch.
        """
        self.setEnabled(supportBatch)
