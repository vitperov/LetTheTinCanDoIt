#!/usr/bin/python3
import sys
from PyQt5.QtWidgets import QApplication
from modules.controller import *

def main():
    app = QApplication(sys.argv)
    controller = ProjectGPTController()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
