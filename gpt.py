#!/usr/bin/python3
import sys
from PyQt5.QtWidgets import QApplication
from chatgpt_controller import ChatGPTController

def main():
    app = QApplication(sys.argv)
    controller = ChatGPTController()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
