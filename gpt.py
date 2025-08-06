import sys
import os
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QIcon, QGuiApplication
from modules.controller import *

def main():
    app = QApplication(sys.argv)

    # Set application display name (tooltip in dock)
    app.setApplicationDisplayName("LetTheTinCanDoIt")
    app.setApplicationName("LetTheTinCanDoIt")

    # Let Wayland compositors know which desktop file belongs to this app
    QGuiApplication.setDesktopFileName("LetTheTinCanDoIt.desktop")

    # Prefer the themed icon (Wayland/GNOME); fall back to local file on X11
    themed_icon = QIcon.fromTheme("letthetincandoit")
    if not themed_icon.isNull():
        app.setWindowIcon(themed_icon)
    else:
        icon_path = os.path.join(os.path.dirname(__file__), "resources", "tinCan.png")
        if os.path.exists(icon_path):
            app.setWindowIcon(QIcon(icon_path))

    controller = ProjectGPTController()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
