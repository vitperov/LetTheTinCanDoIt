import os
import sys
import shutil
import subprocess
from PyQt5.QtWidgets import QMenu, QMessageBox
from PyQt5.QtCore import QUrl
from PyQt5.QtGui import QDesktopServices


class FilesPanelContextMenu:
    def __init__(self, files_panel):
        self.files_panel = files_panel

    def on_context_menu(self, point):
        proxy_index = self.files_panel.tree_view.indexAt(point)
        if not proxy_index.isValid():
            return
        src_index = self.files_panel.proxy_model.mapToSource(proxy_index)
        if not src_index.isValid():
            return
        item_path = self.files_panel.file_system_model.filePath(src_index)

        menu = QMenu(self.files_panel)
        if self.files_panel.file_system_model.isDir(src_index):
            open_action = menu.addAction("Open")
            open_action.triggered.connect(lambda *_: self.open_directory(item_path))
            if sys.platform.startswith("linux"):
                term_action = menu.addAction("Open in Terminal")
                term_action.triggered.connect(lambda *_: self.open_in_terminal(item_path))
        else:
            open_action = menu.addAction("Open")
            open_action.triggered.connect(lambda *_: self.open_file(item_path))
            index_action = menu.addAction("Index description")
            index_action.triggered.connect(lambda *_: self.index_description(item_path))
            delete_action = menu.addAction("Delete file")
            delete_action.triggered.connect(lambda *_: self.delete_file(item_path))
        menu.exec_(self.files_panel.tree_view.viewport().mapToGlobal(point))

    def open_file(self, file_path):
        QDesktopServices.openUrl(QUrl.fromLocalFile(file_path))

    def open_directory(self, dir_path):
        QDesktopServices.openUrl(QUrl.fromLocalFile(dir_path))

    def index_description(self, file_path):
        rel_path = os.path.relpath(file_path, self.files_panel.project_dir)
        self.files_panel.model.project_meta.update_description(rel_path)
        new_status = self.files_panel.model.project_meta.getFileStatus(rel_path)
        self.files_panel.file_system_model.status_map[file_path] = new_status
        self.files_panel.file_system_model.set_status_map(self.files_panel.file_system_model.status_map)
        source_index = self.files_panel.file_system_model.index(self.files_panel.project_dir)
        proxy_index = self.files_panel.proxy_model.mapFromSource(source_index)
        if proxy_index.isValid():
            self.files_panel.tree_view.setRootIndex(proxy_index)

    def delete_file(self, file_path):
        reply = QMessageBox.question(
            self.files_panel,
            "Delete File",
            f"Are you sure you want to delete this file?\n\n{file_path}",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            try:
                os.remove(file_path)
            except Exception as e:
                QMessageBox.critical(self.files_panel, "Error", f"Failed to delete file: {e}")

    def open_in_terminal(self, dir_path):
        if sys.platform.startswith("linux"):
            terminal = shutil.which("gnome-terminal") or shutil.which("konsole") or shutil.which("xfce4-terminal") or shutil.which("xterm")
            if not terminal:
                QMessageBox.critical(self.files_panel, "Error", "No terminal emulator found.")
                return
            try:
                if "gnome-terminal" in terminal or "xfce4-terminal" in terminal:
                    subprocess.Popen([terminal, "--working-directory", dir_path])
                elif "konsole" in terminal:
                    subprocess.Popen([terminal, "--workdir", dir_path])
                elif "xterm" in terminal:
                    subprocess.Popen([terminal, "-e", f"bash -c 'cd {dir_path}; exec bash'"])
                else:
                    subprocess.Popen([terminal])
            except Exception as e:
                QMessageBox.critical(self.files_panel, "Error", f"Failed to open terminal: {e}")
        else:
            QMessageBox.information(self.files_panel, "Not Supported", "Opening in terminal is not supported on this OS.")
