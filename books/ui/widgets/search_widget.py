"""
 :author: vic on 2022-11-02
"""
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QPushButton, QHBoxLayout, QComboBox
from PyQt5.QtGui import QKeyEvent

from typing import Callable


class SearchBox(QComboBox):
    def __init__(self, parent, on_enter: Callable[[], None]):
        super().__init__(parent)
        self.setProperty("search", True)
        self.setEditable(True)
        self.setMaxCount(10)
        self.setInsertPolicy(QComboBox.NoInsert)
        self.hist = []
        self.on_enter = on_enter

    def keyPressEvent(self, event: QKeyEvent) -> None:
        if (event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter) and len(self.currentText().strip()) != 0:
            self.on_enter()
        super().keyPressEvent(event)

    def add_current(self) -> None:
        current_text = self.currentText()
        if current_text not in self.hist:
            self.hist.insert(0, current_text)
            if self.count() == self.maxCount():
                self.removeItem(self.maxCount() - 1)
            # we just need to add to history if it hasn't been added yet
            self.insertItem(0, current_text)


# noinspection PyUnresolvedReferences
class SearchWidget(QWidget):
    def __init__(self, on_search: Callable[[str], None]):
        super().__init__()
        self._on_search = on_search if on_search is not None else lambda x: print(f"Search: {x}")

        self.text: SearchBox = SearchBox(self, self.search)

        self.button: QPushButton = QPushButton(self.tr("&Search"))
        self.button.clicked.connect(self.search)

        layout = QHBoxLayout()
        layout.addWidget(self.text)
        layout.addWidget(self.button)
        layout.setAlignment(self.button, Qt.AlignHCenter)

        self.setLayout(layout)

    def clear(self) -> None:
        self.text.add_current()
        self.text.setCurrentIndex(0)
        self.text.setCurrentText("")

    def search(self) -> None:
        self._on_search(self.get_text())

    def get_text(self) -> str:
        return self.text.currentText()
