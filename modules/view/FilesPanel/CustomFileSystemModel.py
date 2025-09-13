import os
from PyQt5.QtWidgets import QFileSystemModel
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QIcon, QPainter, QBrush
from modules.model.ProjectMeta.ProjectMeta import FileStatus

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
        return super().flags(index) | Qt.ItemIsUserCheckable

    def data(self, index, role):
        if not index.isValid():
            return None
        if role == Qt.CheckStateRole:
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
        if role == Qt.CheckStateRole:
            file_path = self.filePath(index)
            checked = (value == Qt.Checked)
            self.checked_files[file_path] = checked
            if self.isDir(index):
                for row in range(self.rowCount(index)):
                    child_index = self.index(row, 0, index)
                    self.setData(child_index, value, role)
            self.dataChanged.emit(index, index)
            return True
        return super().setData(index, value, role)
