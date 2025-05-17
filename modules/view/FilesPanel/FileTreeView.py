from PyQt5.QtWidgets import QTreeView
from PyQt5.QtCore import QEvent

class FileTreeView(QTreeView):
    def viewportEvent(self, ev):
        if ev.type() == QEvent.ToolTip:
            return True
        return super().viewportEvent(ev)
