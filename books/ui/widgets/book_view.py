"""
 :author: vic on 2022-11-02
"""
from PyQt5.QtWidgets import QHBoxLayout, QLineEdit, QLayout, QDialog, QDialogButtonBox, QLabel, QFormLayout, \
    QShortcut, QComboBox, QTableWidget, QTableWidgetItem, QAbstractItemView, QToolButton, QVBoxLayout, QHeaderView
from PyQt5.QtGui import QKeySequence, QIcon, QFocusEvent
from PyQt5.QtCore import Qt

from dbschema import BookFormat
from books.openlibrary import Book
from ..resources import get_icon

import json
import authority


class AuthorToolButton(QToolButton):
    # noinspection PyUnresolvedReferences
    def __init__(self, parent, name: str, shortcut: str, icon: str, call):
        super().__init__(parent)
        self.setIcon(QIcon(get_icon(icon)))
        self.setToolTip(f"{name} - {shortcut}")
        self.setFocusPolicy(Qt.NoFocus)
        self.action = QShortcut(QKeySequence(shortcut), self)
        self.clicked.connect(call)
        self.action.activated.connect(call)
        self.setProperty("author", True)


class AuthorTable(QTableWidget):
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

        self.setWindowTitle("Books - Edit")
        self.book = book
        self.config = config

        save_action = QShortcut(QKeySequence('Ctrl+S'), self)
        save_action.activated.connect(self.save)

        buttons = QDialogButtonBox.Cancel | QDialogButtonBox.Save
        button_box = QDialogButtonBox(buttons)
        button_box.accepted.connect(self.save)
        button_box.rejected.connect(self.reject)

        form = QFormLayout()
        form.setSizeConstraint(QLayout.SetFixedSize)

        self.title_text = QLineEdit()
        form.addRow(QLabel("Title"), self.title_text)

        self.author_tools = QVBoxLayout()
        self.author_table = AuthorTable()
        self.author = QHBoxLayout()
        self.author.addWidget(self.author_table)
        self.author.addLayout(self.author_tools)

        add_author = AuthorToolButton(self, "Add", "Shift+Ctrl+A", "plus.png", self.author_table.add)
        del_author = AuthorToolButton(self, "Delete", "Shift+Ctrl+D", "delete.png", self.author_table.delete)
        up_author = AuthorToolButton(self, "Move Up", "Shift+Ctrl+Up", "up.png", self.author_table.up)
        dwn_author = AuthorToolButton(self, "Move Down", "Shift+Ctrl+Down", "down.png", self.author_table.down)

        self.author_tools.addWidget(add_author)
        self.author_tools.addWidget(del_author)
        self.author_tools.addWidget(up_author)
        self.author_tools.addWidget(dwn_author)
        self.author_tools.addStretch()

        form.addRow(QLabel("Author"), self.author)

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

        if self.book is not None:
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

        form.addRow(button_box)
        self.setLayout(form)

    def save(self):
        if len(self.title_text.text()) == 0 \
                or self.author_table.rowCount() == 0 \
                or len(self.isbn_text.text()) == 0 \
                or len(self.year_text.text()) == 0:
            return
        if not self.book_format_combo.hasFocus():
            return
        if self.book is None:
            self.book = Book(
                self.title_text.text(),
                self.author_table.get_data(),
                self.isbn_text.text(),
                self.languages_combo.currentData(),
                self.year_text.text(),
                self.book_format_combo.currentData()
            )
        else:
            self.book.set_title(self.title_text.text())
            self.book.set_author(self.author_table.get_data())
            self.book.set_isbn(self.isbn_text.text())
            self.book.set_language(self.languages_combo.currentData())
            self.book.set_year(self.year_text.text())
            self.book.set_book_format(self.book_format_combo.currentData())

        with open(self.config['db_file'], "a+") as outfile:
            outfile.write(json.dumps(self.book.json(), sort_keys=True, ensure_ascii=False))
            outfile.write("\n")
        self.accept()
