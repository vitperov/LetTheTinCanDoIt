import os
import subprocess
from PyQt5.QtWidgets import QWidget, QTreeView, QVBoxLayout, QPushButton, QFileSystemModel, QFileDialog, QHBoxLayout, QLabel, QToolTip, QMenu, QMessageBox
from PyQt5.QtCore import QDir, Qt, pyqtSignal, QRect, QEvent, QSortFilterProxyModel, QModelIndex, QUrl
from PyQt5.QtGui import QPixmap, QIcon, QPainter, QBrush, QColor, QCursor, QDesktopServices
from PyQt5.QtWidgets import QStyle
from modules.view.ProjectsHistoryWindow import ProjectsHistoryWindow
from modules.view.ProjectMetaSettingsDialog import ProjectMetaSettingsDialog
from modules.model.ProjectMeta.ProjectMeta import FileStatus

class FileTreeView(QTreeView):
    def viewportEvent(self, ev):
        if ev.type() == QEvent.ToolTip:
            return True
        return super().viewportEvent(ev)

class ExtensionFilterProxyModel(QSortFilterProxyModel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.hidden_extensions = set()

    def set_hidden_extensions(self, hide_exts):
        self.hidden_extensions = set(hide_exts)
        self.invalidateFilter()

    def filterAcceptsRow(self, source_row, source_parent):
        if not self.hidden_extensions:
            return True
        model = self.sourceModel()
        index = model.index(source_row, 0, source_parent)
        if not index.isValid():
            return False
        if model.isDir(index):
            return True
        ext = os.path.splitext(model.filePath(index))[1][1:]
        return ext not in self.hidden_extensions

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
        button_layout = QHBoxLayout()

        self.icon_label = QLabel()
        pixmap = QPixmap('resources/tinCan.png')
        self.icon_label.setPixmap(pixmap)

        self.choose_dir_button = QPushButton("Open Project")
        self.choose_dir_button.setIcon(self.style().standardIcon(QStyle.SP_DirIcon))
        self.choose_dir_button.clicked.connect(self.choose_directory)

        self.last_projects_button = QPushButton("Last projects")
        self.last_projects_button.clicked.connect(self.show_projects_history)

        self.settings_button = QPushButton("Settings")
        self.settings_button.clicked.connect(self.open_settings)

        self.project_settings_button = QPushButton("Project settings")
        self.project_settings_button.clicked.connect(self.open_project_settings)

        button_layout.addWidget(self.icon_label)
        button_layout.addWidget(self.choose_dir_button)
        button_layout.addWidget(self.last_projects_button)
        button_layout.addWidget(self.settings_button)
        button_layout.addWidget(self.project_settings_button)

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

        main_layout.addLayout(button_layout)
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
        if not src_index.isValid() or self.file_system_model.isDir(src_index):
            return
        file_path = self.file_system_model.filePath(src_index)

        menu = QMenu(self)
        open_action = menu.addAction("Open")
        open_action.triggered.connect(lambda: self.open_file(file_path))
        open_with_action = menu.addAction("Open With...")
        open_with_action.triggered.connect(lambda: self.open_with(file_path))
        # Additional custom actions can be added here later

        menu.exec_(self.tree_view.viewport().mapToGlobal(point))

    def open_file(self, file_path):
        QDesktopServices.openUrl(QUrl.fromLocalFile(file_path))

    def open_with(self, file_path):
        program, _ = QFileDialog.getOpenFileName(self, "Open with", "", "")
        if program:
            try:
                subprocess.Popen([program, file_path])
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to open {file_path} with {program}: {e}")

class CustomFileSystemModel(QFileSystemModel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.checked_files = {}
        self.status_map = {}
        self._generate_icons()

    def _generate_icons(self):
        size = 12
        self.icons = {}
        color_map = {
            FileStatus.NotIndexed: Qt.red,
            FileStatus.Indexed: Qt.green,
            FileStatus.Outdated: Qt.yellow
        }
        for status, color in color_map.items():
            pixmap = QPixmap(size, size)
            pixmap.fill(Qt.transparent)
            painter = QPainter(pixmap)
            painter.setRenderHint(QPainter.Antialiasing)
            painter.setBrush(QBrush(color))
            painter.setPen(Qt.NoPen)
            painter.drawEllipse(0, 0, size, size)
            painter.end()
            self.icons[status] = QIcon(pixmap)

    def set_status_map(self, status_map):
        self.beginResetModel()
        self.status_map = status_map
        self.endResetModel()

    def clear_checked_files(self):
        self.checked_files = {}

    def flags(self, index):
        if not index.isValid():
            return Qt.NoItemFlags
        default_flags = super().flags(index)
        if self.isDir(index):
            return default_flags
        return default_flags | Qt.ItemIsUserCheckable | Qt.ItemIsEnabled

    def data(self, index, role):
        if not index.isValid():
            return None
        if role == Qt.CheckStateRole and not self.isDir(index):
            file_path = self.filePath(index)
            return Qt.Checked if self.checked_files.get(file_path, False) else Qt.Unchecked
        if role == Qt.DecorationRole and not self.isDir(index):
            file_path = self.filePath(index)
            icon = self.icons.get(self.status_map.get(file_path))
            if icon:
                return icon
        return super().data(index, role)

    def setData(self, index, value, role):
        if not index.isValid():
            return super().setData(index, value, role)
        if role == Qt.CheckStateRole and not self.isDir(index):
            file_path = self.filePath(index)
            self.checked_files[file_path] = (value == Qt.Checked)
            self.dataChanged.emit(index, index)
            return True
        return super().setData(index, value, role)
