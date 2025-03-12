from PyQt5.QtWidgets import QApplication, QWidget, QTextEdit, QVBoxLayout, QHBoxLayout, QSplitter, QGroupBox, QSizePolicy
from PyQt5.QtCore import Qt
from modules.view.FilesPanel import FilesPanel
from modules.view.BatchesPanel import BatchesPanel
from modules.view.RequestPanel import RequestPanel
from modules.view.TopPanel import TopPanel  # Import the new TopPanel
from modules.view.StatusBar import StatusBar  # Import the new StatusBar

class ProjectGPTView(QWidget):
    def __init__(self, available_models):
        super().__init__()
        self.available_models = available_models
        self.init_ui()

    def init_ui(self):
        # Main layout for the entire view
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(10, 10, 0, 10)  # Set 10px margins on top and bottom
        main_layout.setSpacing(0)  # Minimize spacing between widgets

        # Add the TopPanel at the top
        self.top_panel = TopPanel()  # Create the TopPanel instance
        self.top_panel.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        main_layout.addWidget(self.top_panel)

        # Create a splitter for the main middle section
        splitter = QSplitter(Qt.Horizontal)

        # Left side layout with FilesPanel and BatchesPanel
        left_side_layout = QVBoxLayout()
        self.left_panel = FilesPanel()
        self.left_panel.setMinimumWidth(200)
        self.batches_panel = BatchesPanel()
        left_side_layout.addWidget(self.left_panel)
        left_side_layout.addWidget(self.batches_panel)

        left_side_widget = QWidget()
        left_side_widget.setLayout(left_side_layout)
        splitter.addWidget(left_side_widget)

        # Right side layout with RequestPanel and Response display
        right_panel_layout = QVBoxLayout()
        self.request_panel = RequestPanel(self.available_models)
        right_panel_layout.addWidget(self.request_panel)

        response_groupbox = QGroupBox("Response")
        response_layout = QVBoxLayout()
        self.response_display = QTextEdit()
        self.response_display.setReadOnly(True)
        response_layout.addWidget(self.response_display)
        response_groupbox.setLayout(response_layout)
        right_panel_layout.addWidget(response_groupbox)

        right_panel = QWidget()
        right_panel.setLayout(right_panel_layout)
        right_panel.setMinimumWidth(300)
        splitter.addWidget(right_panel)

        # Set sizes for the splitter panels
        splitter.setSizes([300, 700])
        splitter.setHandleWidth(1)
        splitter.setChildrenCollapsible(False)

        # Add the splitter to the main layout
        main_layout.addWidget(splitter)

        # Add the StatusBar at the bottom
        self.status_bar = StatusBar()  # Create the StatusBar instance
        self.status_bar.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        main_layout.addWidget(self.status_bar)

        # Set the layout and window properties
        self.resize(1200, 1000)
        self.setLayout(main_layout)
        self.setWindowTitle('LetTheTinCanDoIt')
        self.show()

    def update_response(self, response):
        """
        Updates the response display in the UI.
        """
        self.response_display.setText(response)
        self.request_panel.set_processing(False)

    def set_additional_requests(self, additional_requests):
        """
        Sets the additional requests in the RequestPanel.
        """
        self.request_panel.set_additional_requests(additional_requests)
