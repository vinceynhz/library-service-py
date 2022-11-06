"""
 :author: vic on 2022-11-02
"""
from PyQt5.QtWidgets import QHBoxLayout, QLineEdit, QLayout, QDialog, QLabel, QFormLayout, \
    QShortcut, QComboBox, QTableWidget, QTableWidgetItem, QAbstractItemView, QToolButton, QVBoxLayout, QHeaderView, \
    QPushButton
from PyQt5.QtGui import QKeySequence, QIcon, QFocusEvent, QKeyEvent
from PyQt5.QtCore import Qt, pyqtSignal

from dbschema import BookFormat
from books.openlibrary import Book
from ..resources import get_icon

import json
import authority


class ActionToolButton(QToolButton):
    # noinspection PyUnresolvedReferences
    def __init__(self, parent, name: str, shortcut: str, icon: str, call, prop_name: str = "author"):
        super().__init__(parent)
        self.setIcon(QIcon(get_icon(icon)))
        self.setToolTip(f"{name} - {shortcut}")
        self.setFocusPolicy(Qt.NoFocus)
        self.action = QShortcut(QKeySequence(shortcut), self)
        self.clicked.connect(call)
        self.action.activated.connect(call)
        self.setProperty(prop_name, True)


class AuthorTable(QTableWidget):
    itemDeleted = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAlternatingRowColors(True)
        self.setSelectionBehavior(QAbstractItemView.SelectItems)
        self.setHorizontalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.setSelectionMode(QAbstractItemView.SingleSelection)
        self.setColumnCount(1)
        self.setTabKeyNavigation(False)
        self.setHorizontalHeaderLabels(["Name"])
        self.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)

    def focusOutEvent(self, e: QFocusEvent):
        self.clearSelection()

    def add(self):
        self.setFocus()
        self.clearSelection()

        row_count = self.rowCount()
        self.setRowCount(row_count + 1)

        item = QTableWidgetItem("")
        self.setItem(row_count, 0, item)
        self.setCurrentCell(row_count, 0)
        self.editItem(item)
        item.setSelected(True)

    def delete(self):
        self.setFocus()
        self.clearSelection()

        current_row = self.currentRow()
        self.removeRow(current_row)
        self.itemDeleted.emit()

    def up(self):
        current_row = self.currentRow()
        if current_row > 0:
            self.clearSelection()
            current_item = self.item(current_row, 0)
            current_item = QTableWidgetItem(current_item.text())

            self.removeRow(current_row)
            self.insertRow(current_row - 1)
            self.setItem(current_row - 1, 0, current_item)
            self.setCurrentCell(current_row - 1, 0)
            current_item.setSelected(True)

    def down(self):
        current_row = self.currentRow()
        if current_row < self.rowCount() - 1:
            self.clearSelection()
            current_item = self.item(current_row, 0)
            current_item = QTableWidgetItem(current_item.text())
            self.removeRow(current_row)
            self.insertRow(current_row + 1)
            self.setItem(current_row + 1, 0, current_item)
            self.setCurrentCell(current_row + 1, 0)
            current_item.setSelected(True)

    def get_data(self):
        return [self.item(row, 0).text() for row in range(self.rowCount())]


# noinspection PyUnresolvedReferences
class BookViewWidget(QDialog):
    def __init__(self, parent, config: dict, book: Book = None, param: str = None):
        super().__init__(parent)

        self.setWindowTitle(self.get_title())
        self.config = config

        save_action = QShortcut(QKeySequence('Ctrl+S'), self)
        save_action.activated.connect(self.save)

        form = QFormLayout()
        form.setSizeConstraint(QLayout.SetFixedSize)

        self.title_text = QLineEdit()
        form.addRow(QLabel("Title"), self.title_text)

        self.author_table = AuthorTable()

        add_author = ActionToolButton(self, "Add", "Shift+Ctrl+A", "plus.png", self.author_table.add)
        del_author = ActionToolButton(self, "Delete", "Shift+Ctrl+D", "delete.png", self.author_table.delete)
        up_author = ActionToolButton(self, "Move Up", "Shift+Ctrl+Up", "up.png", self.author_table.up)
        dwn_author = ActionToolButton(self, "Move Down", "Shift+Ctrl+Down", "down.png", self.author_table.down)

        author_tools = QVBoxLayout()
        author_tools.addWidget(add_author)
        author_tools.addWidget(del_author)
        author_tools.addWidget(up_author)
        author_tools.addWidget(dwn_author)
        author_tools.addStretch()

        author = QHBoxLayout()
        author.addWidget(self.author_table)
        author.addLayout(author_tools)

        form.addRow(QLabel("Author"), author)

        self.isbn_text = QLineEdit()
        form.addRow(QLabel("ISBN"), self.isbn_text)

        self.year_text = QLineEdit()
        form.addRow(QLabel("Year"), self.year_text)

        self.languages_combo = QComboBox()
        for k in authority.get_langs():
            self.languages_combo.addItem(authority.desc_lang(k), k)
        form.addRow(QLabel("Language"), self.languages_combo)

        self.book_format_combo = QComboBox()
        for name, member in BookFormat.__members__.items():
            self.book_format_combo.addItem(name, userData=member)
        form.addRow(QLabel("Format"), self.book_format_combo)

        self.title_text.returnPressed.connect(self.author_table.setFocus)
        self.isbn_text.returnPressed.connect(self.year_text.setFocus)
        self.year_text.returnPressed.connect(self.languages_combo.setFocus)

        self.current_index = None
        self.max_index = None
        self.button_save = None

        self.populate(book, param)
        self.buttons(form)
        self.setLayout(form)

    def keyPressEvent(self, event: QKeyEvent) -> None:
        if event.key() == Qt.Key_Enter or event.key() == Qt.Key_Return:
            return
        super().keyPressEvent(event)

    def populate(self, book: Book, param: str) -> None:
        if book is not None:
            self.title_text.setText(book.get_title())
            self.author_table.setRowCount(len(book.get_author()))
            for i, author in enumerate(book.get_author()):
                item = QTableWidgetItem(author)
                self.author_table.setItem(i, 0, item)
            self.isbn_text.setText(book.get_isbn())
            self.year_text.setText(str(book.get_year()))
            self.languages_combo.setCurrentText(authority.desc_lang(book.get_language()))
            self.book_format_combo.setCurrentText(book.get_book_format().name)
        else:
            if param is not None:
                args = param.split("+")
                for arg in args:
                    if arg.startswith("title:"):
                        self.title_text.setText(arg[6:])
                    elif arg.startswith("author:"):
                        self.author_list.setText(arg[7:])
                    elif arg.startswith("isbn:"):
                        self.isbn_text.setText(arg[5:])
            self.languages_combo.setCurrentText(authority.desc_lang(self.config['language']))
            self.book_format_combo.setCurrentText(self.config['book_format'])

    def save(self):
        result = self.get_updated_book()
        if result is not None:
            with open(self.config['db_file'], "a+") as outfile:
                outfile.write(json.dumps(result.json(), sort_keys=True, ensure_ascii=False))
                outfile.write("\n")
            self.accept()
        return

    def get_updated_book(self):
        if len(self.title_text.text()) == 0 \
                or self.author_table.rowCount() == 0 \
                or len(self.isbn_text.text()) == 0 \
                or len(self.year_text.text()) == 0:
            return None
        return Book(
            self.title_text.text(),
            self.author_table.get_data(),
            self.isbn_text.text(),
            self.languages_combo.currentData(),
            self.year_text.text(),
            self.book_format_combo.currentData()
        )

    def get_title(self):
        return "Books - Edit"

    def buttons(self, layout: QFormLayout):
        button_box = QHBoxLayout()
        button_box.setAlignment(Qt.AlignRight)
        self.button_save = QPushButton("Save")
        self.button_save.clicked.connect(self.save)
        button_cancel = QPushButton("Cancel")
        button_cancel.clicked.connect(self.reject)
        button_box.addWidget(button_cancel)
        button_box.addWidget(self.button_save)
        layout.addRow(button_box)
        pass
