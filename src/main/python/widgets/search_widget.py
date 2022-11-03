"""
 :author: vic on 2022-11-02
"""
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QPushButton, QHBoxLayout, QLineEdit

from typing import Callable


# noinspection PyUnresolvedReferences
class SearchWidget(QWidget):
    def __init__(self, on_search: Callable[[str], None]):
        super().__init__()
        self._on_search = on_search if on_search is not None else lambda x: print(f"Search: {x}")

        self.text = QLineEdit()

        # User presses enter
        self.text.returnPressed.connect(self.search)

        self.button = QPushButton('Search')
        # User clicks the button
        self.button.clicked.connect(self.search)

        layout = QHBoxLayout()
        layout.addWidget(self.text)
        layout.addWidget(self.button)

        layout.setAlignment(self.button, Qt.AlignHCenter)

        self.setLayout(layout)

    def clear(self):
        self.text.setText("")

    def search(self):
        self._on_search(self.text.text())

    def get_text(self):
        return self.text.text()
