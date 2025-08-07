import os
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QFileDialog, QLabel, QToolTip, QMenu, QMessageBox
from PyQt5.QtCore import Qt, pyqtSignal, QRect, QModelIndex, QUrl
from PyQt5.QtGui import QCursor, QDesktopServices
from .FileTreeView import FileTreeView
from .ExtensionFilterProxyModel import ExtensionFilterProxyModel
from .CustomFileSystemModel import CustomFileSystemModel
from modules.view.ProjectsHistoryWindow import ProjectsHistoryWindow
from modules.view.ProjectMetaSettingsDialog import ProjectMetaSettingsDialog
from modules.model.ProjectMeta.ProjectMeta import FileStatus

class FilesPanel(QWidget):
    proj_dir_changed = pyqtSignal(str)

    def __init__(self, parent=None, model=None):
        super().__init__(parent)
        self.model = model
        self.project_dir = None
        self.init_ui()
        if self.model:
            self.set_model(self.model)

    def set_model(self, model):
        self.model = model
        self.project_dir = self.load_last_project_directory()
        self.file_system_model.setRootPath(self.project_dir)
        self.handle_project_selected(self.project_dir)

    def init_ui(self):
        main_layout = QVBoxLayout()

        self.tree_view = FileTreeView()
        self.tree_view.setMouseTracking(True)
        self.tree_view.entered.connect(self.on_item_entered)
        self.tree_view.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tree_view.customContextMenuRequested.connect(self.on_context_menu)

        self.file_system_model = CustomFileSystemModel()
        self.proxy_model = ExtensionFilterProxyModel(self)
        self.proxy_model.setSourceModel(self.file_system_model)
        self.tree_view.setModel(self.proxy_model)
        self.tree_view.hideColumn(1)
        self.tree_view.hideColumn(2)
        self.tree_view.hideColumn(3)

        main_layout.addWidget(self.tree_view)
        self.setLayout(main_layout)

    def choose_directory(self):
        selected_dir = QFileDialog.getExistingDirectory(
            self,
            "Choose Project Directory",
            self.project_dir or os.path.expanduser('~')
        )
        if selected_dir:
            self.handle_project_selected(selected_dir)

    def show_projects_history(self):
        history_model = getattr(self.model, "historyModel", None)
        self.history_window = ProjectsHistoryWindow(history_model)
        self.history_window.project_selected.connect(self.handle_project_selected)
        self.history_window.exec_()

    def open_settings(self):
        if self.model is None:
            QMessageBox.critical(self, "Error", "Model is not set.")
            return
        from modules.view.SettingsDialog import SettingsDialog
        settings_dialog = SettingsDialog(self, model=self.model)
        settings_dialog.exec_()

    def open_project_settings(self):
        if self.model is None or getattr(self.model, "project_meta", None) is None:
            QMessageBox.critical(self, "Error", "Project Meta information is not available.")
            return
        dialog = ProjectMetaSettingsDialog(self.model.project_meta, self)
        dialog.exec_()

    def handle_project_selected(self, directory):
        if not directory:
            return
        self.file_system_model.setRootPath(directory)

        hidden_extensions = []
        if self.model and getattr(self.model, "project_meta", None):
            hidden_extensions = self.model.project_meta.getHiddenExtensions()
        self.proxy_model.set_hidden_extensions(hidden_extensions)

        if self.model and getattr(self.model, "project_meta", None):
            _, _ = self.model.project_meta.getIndexationParameters()
            relative_files = self.model.project_meta.getAll_project_files()
            statuses_map = {}
            for rel_path in relative_files:
                status = self.model.project_meta.getFileStatus(rel_path)
                abs_path = os.path.join(directory, rel_path)
                statuses_map[abs_path] = status
            self.file_system_model.set_status_map(statuses_map)

        source_index = self.file_system_model.index(directory)
        proxy_index = self.proxy_model.mapFromSource(source_index)
        if proxy_index.isValid():
            self.tree_view.setRootIndex(proxy_index)

        self.project_dir = directory
        self.proj_dir_changed.emit(directory)
        self.clear_checked_files()
        self.update_settings(directory)

    def load_last_project_directory(self):
        if self.model and hasattr(self.model, "historyModel"):
            return self.model.historyModel.get_last_project_directory()
        return os.path.expanduser('~')

    def update_settings(self, directory):
        if self.model and hasattr(self.model, "historyModel"):
            self.model.historyModel.update_last_project(directory)

    def get_checked_files(self):
        relative_files = [
            os.path.relpath(path, self.project_dir)
            for path, checked in self.file_system_model.checked_files.items()
            if checked
        ]
        return self.project_dir, relative_files

    def clear_checked_files(self):
        self.file_system_model.clear_checked_files()

    def on_item_entered(self, index):
        if not index.isValid():
            QToolTip.hideText()
            return
        src_index = self.proxy_model.mapToSource(index)
        if not src_index.isValid():
            QToolTip.hideText()
            return
        file_path = self.file_system_model.filePath(src_index)
        if os.path.isdir(file_path):
            QToolTip.hideText()
            return

        status = self.file_system_model.status_map.get(file_path)
        if status in (FileStatus.Indexed, FileStatus.Outdated):
            rel_path = os.path.relpath(file_path, self.project_dir)
            description = ""
            if self.model and getattr(self.model, "project_meta", None):
                description = self.model.project_meta.getFileDescription(rel_path)
            if description:
                html_desc = '<html><body style="white-space:pre-wrap;">{}</body></html>'.format(description)
                QToolTip.showText(QCursor.pos(), html_desc, self.tree_view, QRect(), 15000)
        else:
            QToolTip.hideText()

    def on_context_menu(self, point):
        proxy_index = self.tree_view.indexAt(point)
        if not proxy_index.isValid():
            return
        src_index = self.proxy_model.mapToSource(proxy_index)
        if not src_index.isValid():
            return
        item_path = self.file_system_model.filePath(src_index)

        menu = QMenu(self)
        if self.file_system_model.isDir(src_index):
            open_action = menu.addAction("Open")
            open_action.triggered.connect(lambda *_: self.open_directory(item_path))
        else:
            open_action = menu.addAction("Open")
            open_action.triggered.connect(lambda *_: self.open_file(item_path))
            index_action = menu.addAction("Index description")
            index_action.triggered.connect(lambda *_: self.index_description(item_path))
        menu.exec_(self.tree_view.viewport().mapToGlobal(point))

    def open_file(self, file_path):
        QDesktopServices.openUrl(QUrl.fromLocalFile(file_path))

    def open_directory(self, dir_path):
        QDesktopServices.openUrl(QUrl.fromLocalFile(dir_path))

    def index_description(self, file_path):
        rel_path = os.path.relpath(file_path, self.project_dir)
        self.model.project_meta.update_description(rel_path)
        new_status = self.model.project_meta.getFileStatus(rel_path)
        self.file_system_model.status_map[file_path] = new_status
        self.file_system_model.set_status_map(self.file_system_model.status_map)
        source_index = self.file_system_model.index(self.project_dir)
        proxy_index = self.proxy_model.mapFromSource(source_index)
        if proxy_index.isValid():
            self.tree_view.setRootIndex(proxy_index)
