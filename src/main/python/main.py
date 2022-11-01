from fbs_runtime.application_context.PyQt5 import ApplicationContext
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QMainWindow, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QLineEdit, QLayout

import sys
import random

strings = [
    "souvenir",
    "reusable",
    "recyclable",
    "microwave"
]

class SearchScreen(QWidget):
    def __init__(self):
        super().__init__()
        self.text = QLineEdit()

        button = QPushButton('Search')
        button.clicked.connect(self.random_text)

        layout = QHBoxLayout()
        layout.addWidget(self.text)
        layout.addWidget(button)

        layout.setAlignment(button, Qt.AlignHCenter)

        self.setLayout(layout)

    def random_text(self):
        self.label.setText(random.choice(strings))


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowMaximizeButtonHint)
        self.layout().setSizeConstraint(QLayout.SetFixedSize)
        self.setWindowTitle("Books")

        self.statusBar().setSizeGripEnabled(False)
        self.statusBar().showMessage("Ready")
        self.setCentralWidget(SearchScreen())


if __name__ == '__main__':
    appctxt = ApplicationContext()
    stylesheet = appctxt.get_resource('styles.qss')
    appctxt.app.setStyleSheet(open(stylesheet).read())

    window = MainWindow()
    window.show()
    exit_code = appctxt.app.exec_()
    sys.exit(exit_code)
