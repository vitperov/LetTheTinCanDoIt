from PyQt5.QtWidgets import QWidget, QVBoxLayout, QGroupBox, QComboBox, QLabel, QTextEdit, QPushButton, QHBoxLayout, QLineEdit, QRadioButton, QButtonGroup, QCheckBox, QScrollArea, QGridLayout, QMenu
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QMovie, QCursor
from modules.view.RoleSelector import RoleSelector
from modules.model.RequestOptions import RequestOptions

class RequestPanel(QWidget):
    send_request_signal = pyqtSignal(str, str, str, bool, object)  # model, role, request, editorMode, requestOptions
    send_batch_request_signal = pyqtSignal(str, str, str, str, bool, object)  # model, role, request, description, editorMode, requestOptions

    def __init__(self, available_models):
        super().__init__()
        self.available_models = available_models
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        parameters_groupbox = QGroupBox("Parameters")
        parameters_layout = QHBoxLayout()

        self.model_label = QLabel("Model:")
        self.model_dropdown = QComboBox()
        self.model_dropdown.addItems(self.available_models)

        parameters_layout.addWidget(self.model_label)
        parameters_layout.addWidget(self.model_dropdown)
        parameters_groupbox.setLayout(parameters_layout)
        layout.addWidget(parameters_groupbox)

        mode_groupbox = QGroupBox("Mode")
        mode_layout = QHBoxLayout()

        self.mode_button_group = QButtonGroup()

        self.editor_mode_button = QRadioButton("Editor mode")
        self.editor_mode_button.setChecked(True)
        self.answer_mode_button = QRadioButton("Answer mode (do not modify my files)")

        self.mode_button_group.addButton(self.editor_mode_button)
        self.mode_button_group.addButton(self.answer_mode_button)

        mode_layout.addWidget(self.editor_mode_button)
        mode_layout.addWidget(self.answer_mode_button)

        mode_groupbox.setLayout(mode_layout)
        layout.addWidget(mode_groupbox)

        request_groupbox = QGroupBox("Request")
        request_layout = QVBoxLayout()

        self.role_selector = RoleSelector()
        request_layout.addWidget(self.role_selector)

        self.request_label = QLabel('Request:')
        self.request_input = QTextEdit()
        self.request_input.setAcceptRichText(False)

        # New layout for request input and history button
        text_edit_layout = QHBoxLayout()
        text_edit_layout.addWidget(self.request_input)
        self.history_button = QPushButton("H")
        self.history_button.setFixedWidth(30)
        self.history_button.clicked.connect(self.show_history_menu)
        text_edit_layout.addWidget(self.history_button)

        request_layout.addWidget(self.request_label)
        request_layout.addLayout(text_edit_layout)

        # New single checkbox for including file list
        self.include_files_checkbox = QCheckBox("Include files list in the request")
        request_layout.addWidget(self.include_files_checkbox)

        # New checkbox for attaching last commit diff
        self.attach_diff_checkbox = QCheckBox("Attach last commit diff")
        request_layout.addWidget(self.attach_diff_checkbox)

        batch_layout = QHBoxLayout()

        self.description_label = QLabel('Description:')
        self.description_input = QLineEdit()

        self.send_batch_button = QPushButton('Send Batch')
        self.send_batch_button.clicked.connect(self.handle_send_batch)

        batch_layout.addWidget(self.description_label)
        batch_layout.addWidget(self.description_input)
        batch_layout.addWidget(self.send_batch_button)
        request_layout.addLayout(batch_layout)

        button_layout = QHBoxLayout()
        self.send_button = QPushButton('Send')
        self.send_button.clicked.connect(self.handle_send)
        button_layout.addWidget(self.send_button)
        self.spinner = QLabel()
        self.movie = QMovie("resources/spinner.gif")
        self.spinner.setMovie(self.movie)
        self.spinner.hide()
        button_layout.addWidget(self.spinner)
        request_layout.addLayout(button_layout)

        request_groupbox.setLayout(request_layout)
        layout.addWidget(request_groupbox)

        self.setLayout(layout)

    def handle_send(self):
        self._emit_send(is_batch=False)

    def handle_send_batch(self):
        self._emit_send(is_batch=True)

    def _emit_send(self, is_batch=False):
        self.send_button.setEnabled(False)
        self.send_batch_button.setEnabled(False)
        self.movie.start()
        self.spinner.show()

        request_text = self.request_input.toPlainText()
        if request_text:
            role_description = self.role_selector.get_role_string()
            selected_model = self.model_dropdown.currentText()
            editor_mode = self.editor_mode_button.isChecked()
            request_options = RequestOptions(
                includeFilesList=self.include_files_checkbox.isChecked(),
                attachLastCommitDiff=self.attach_diff_checkbox.isChecked()
            )
            self.request_input.clear()
            if is_batch:
                description_text = self.description_input.text()
                self.send_batch_request_signal.emit(selected_model, role_description, request_text, description_text, editor_mode, request_options)
            else:
                self.send_request_signal.emit(selected_model, role_description, request_text, editor_mode, request_options)

    def set_processing(self, is_processing):
        self.send_button.setEnabled(not is_processing)
        self.send_batch_button.setEnabled(not is_processing)
        if is_processing:
            self.movie.start()
            self.spinner.show()
        else:
            self.movie.stop()
            self.spinner.hide()

    def set_batch_support(self, supportBatch):
        self.send_batch_button.setEnabled(supportBatch)

    def set_reasoning_support(self, supportReasoningEffort):
        pass  # Remove reasoning support entirely

    def show_history_menu(self):
        menu = QMenu()
        parent = self.window()
        model = getattr(parent, "model", None)
        history = []
        if model is not None and hasattr(model, "requestHistoryModel"):
            history = model.requestHistoryModel.get_last_requests()
        for req in history:
            display_text = req if len(req) <= 20 else req[:20] + "..."
            action = menu.addAction(display_text)
            action.setData(req)
        action = menu.exec_(QCursor.pos())
        if action:
            full_request = action.data()
            self.request_input.setText(full_request)

    def set_additional_requests(self, additional_requests):
        pass
