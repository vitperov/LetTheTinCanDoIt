import os
from PyQt5.QtCore import QSortFilterProxyModel

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
