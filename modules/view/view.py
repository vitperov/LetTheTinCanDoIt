from PyQt5.QtWidgets import QApplication, QWidget, QTextEdit, QVBoxLayout, QHBoxLayout, QSplitter, QGroupBox
from PyQt5.QtCore import Qt
from modules.view.FilesPanel import FilesPanel
from modules.view.BatchesPanel import BatchesPanel
from modules.view.RequestPanel import RequestPanel

class ProjectGPTView(QWidget):
    def __init__(self, available_models):
        super().__init__()
        self.available_models = available_models
        self.init_ui()

    def init_ui(self):
        main_layout = QHBoxLayout()
        splitter = QSplitter(Qt.Horizontal)

        left_side_layout = QVBoxLayout()
        self.left_panel = FilesPanel()
        self.left_panel.setMinimumWidth(200)
        self.batches_panel = BatchesPanel()
        left_side_layout.addWidget(self.left_panel)
        left_side_layout.addWidget(self.batches_panel)

        left_side_widget = QWidget()
        left_side_widget.setLayout(left_side_layout)
        splitter.addWidget(left_side_widget)

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

        splitter.setSizes([250, 800])
        splitter.setHandleWidth(1)
        splitter.setChildrenCollapsible(False)
        main_layout.addWidget(splitter)

        self.resize(1000, 800)
        self.setLayout(main_layout)
        self.setWindowTitle('ChatGPT Application')
        self.show()

    def update_response(self, response):
        self.response_display.setText(response)