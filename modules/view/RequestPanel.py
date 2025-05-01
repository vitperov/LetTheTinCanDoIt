from PyQt5.QtWidgets import QWidget, QVBoxLayout, QGroupBox, QComboBox, QLabel, QTextEdit, QPushButton, QHBoxLayout, QLineEdit, QRadioButton, QButtonGroup, QCheckBox, QScrollArea, QGridLayout, QMenu
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QMovie, QCursor
from modules.view.RoleSelector import RoleSelector

class RequestPanel(QWidget):
    send_request_signal = pyqtSignal(str, str, str, str, bool)  # model, role, request, reasoning, editorMode
    send_batch_request_signal = pyqtSignal(str, str, str, str, str, bool)  # model, role, request, reasoning, description, editorMode

    def __init__(self, available_models):
        super().__init__()
        self.available_models = available_models
        self.additional_requests = []
        self.checkbox_list = []
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        parameters_groupbox = QGroupBox("Parameters")
        parameters_layout = QHBoxLayout()

        self.model_label = QLabel("Model:")
        self.model_dropdown = QComboBox()
        self.model_dropdown.addItems(self.available_models)

        self.reasoning_label = QLabel("Reasoning:")
        self.reasoning_dropdown = QComboBox()
        self.reasoning_dropdown.addItems(["low", "medium", "high"])
        self.reasoning_dropdown.setCurrentText("medium")

        parameters_layout.addWidget(self.model_label)
        parameters_layout.addWidget(self.model_dropdown)
        parameters_layout.addWidget(self.reasoning_label)
        parameters_layout.addWidget(self.reasoning_dropdown)
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

        self.additional_requests_checkbox_layout = QGridLayout()
        request_layout.addLayout(self.additional_requests_checkbox_layout)

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

    def set_additional_requests(self, additional_requests):
        self.additional_requests = additional_requests
        for checkbox in self.checkbox_list:
            self.additional_requests_checkbox_layout.removeWidget(checkbox)
            checkbox.deleteLater()
        self.checkbox_list = []
        for index, request in enumerate(self.additional_requests):
            checkbox = QCheckBox(request)
            row = index // 2
            col = index % 2
            self.additional_requests_checkbox_layout.addWidget(checkbox, row, col)
            self.checkbox_list.append(checkbox)

    def handle_send(self):
        self.handle_request(self.send_request_signal)

    def handle_send_batch(self):
        description_text = self.description_input.text()
        self.handle_request(self.send_batch_request_signal, description_text, True)

    def handle_request(self, signal, description_text='', is_batch=False):
        self.send_button.setEnabled(False)
        self.send_batch_button.setEnabled(False)
        self.movie.start()
        self.spinner.show()

        request_text = self.request_input.toPlainText()
        if request_text:
            role_description = self.role_selector.get_role_string()
            selected_model = self.model_dropdown.currentText()
            reasoning_effort = self.reasoning_dropdown.currentText() if self.reasoning_dropdown.isEnabled() else ""
            editor_mode = self.editor_mode_button.isChecked()
            checked_additional_requests = [cb.text() for cb in self.checkbox_list if cb.isChecked()]
            if checked_additional_requests:
                request_text += "\n\n" + "\n".join(checked_additional_requests)
            self.request_input.clear()
            if is_batch:
                signal.emit(selected_model, role_description, request_text, reasoning_effort, description_text, editor_mode)
            else:
                signal.emit(selected_model, role_description, request_text, reasoning_effort, editor_mode)

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
        self.reasoning_dropdown.setEnabled(supportReasoningEffort)
        self.reasoning_label.setEnabled(supportReasoningEffort)

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
