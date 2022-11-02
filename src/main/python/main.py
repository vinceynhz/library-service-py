from fbs_runtime.application_context.PyQt5 import ApplicationContext
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QMainWindow, QPushButton, QHBoxLayout, QLineEdit, QLayout, QDialog, \
    QDialogButtonBox, QLabel, QFormLayout, QShortcut, QComboBox
from PyQt5.QtGui import QKeySequence

from typing import Callable

import sys
import json

import openlibrary
import authority


class SettingsViewWidget(QDialog):
    def __init__(self, parent, config: dict):
        super().__init__(parent)
        self.setWindowTitle("Books - Settings")
        self.config = config

        save_action = QShortcut(QKeySequence('Ctrl+S'), self)
        save_action.activated.connect(self.save)

        buttons = QDialogButtonBox.Cancel | QDialogButtonBox.Save
        button_box = QDialogButtonBox(buttons)
        button_box.accepted.connect(self.save)
        button_box.rejected.connect(self.reject)

        form = QFormLayout()
        form.setSizeConstraint(QLayout.SetFixedSize)

        self.languages_combo = QComboBox()
        for k in authority.get_langs():
            self.languages_combo.addItem(authority.desc_lang(k), k)
        form.addRow(QLabel("Default Language"), self.languages_combo)
        self.languages_combo.setCurrentText(authority.desc_lang(self.config['language']))

        self.book_format_combo = QComboBox()
        for name, member in openlibrary.BookFormat.__members__.items():
            self.book_format_combo.addItem(name, userData=member)
        form.addRow(QLabel("Default Format"), self.book_format_combo)
        self.book_format_combo.setCurrentText(self.config['book_format'])

        self.file_text = QLineEdit()
        self.file_text.setText(config['db_file'])
        form.addRow(QLabel("Database File"), self.file_text)

        form.addRow(button_box)
        self.setLayout(form)

    def save(self):
        if len(self.file_text.text()) == 0:
            return
        self.config['db_file'] = self.file_text.text().strip()
        self.config['book_format'] = self.book_format_combo.currentData().name
        self.config['language'] = self.languages_combo.currentData()

        with open('./database/config.json', 'w+') as outfile:
            json.dump(self.config, outfile, indent=4, sort_keys=True)

        self.accept()


class BookViewWidget(QDialog):
    def __init__(self, parent, config: dict, book: openlibrary.Book = None, param: str = None):
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

        self.author_list = QLineEdit()
        form.addRow(QLabel("Author"), self.author_list)

        self.isbn_text = QLineEdit()
        form.addRow(QLabel("ISBN"), self.isbn_text)

        self.year_text = QLineEdit()
        form.addRow(QLabel("Year"), self.year_text)

        self.languages_combo = QComboBox()
        for k in authority.get_langs():
            self.languages_combo.addItem(authority.desc_lang(k), k)
        form.addRow(QLabel("Language"), self.languages_combo)

        self.book_format_combo = QComboBox()
        for name, member in openlibrary.BookFormat.__members__.items():
            self.book_format_combo.addItem(name, userData=member)
        form.addRow(QLabel("Format"), self.book_format_combo)

        self.title_text.returnPressed.connect(self.author_list.setFocus)
        self.author_list.returnPressed.connect(self.isbn_text.setFocus)
        self.isbn_text.returnPressed.connect(self.year_text.setFocus)
        self.year_text.returnPressed.connect(self.languages_combo.setFocus)

        if self.book is not None:
            self.title_text.setText(book.get_title())
            self.author_list.setText(','.join(book.get_author()))
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
            self.languages_combo.setCurrentText(authority.desc_lang(config['language']))
            self.book_format_combo.setCurrentText(config['book_format'])

        form.addRow(button_box)
        self.setLayout(form)

    def save(self):
        if len(self.title_text.text()) == 0 \
                or len(self.author_list.text()) == 0 \
                or len(self.isbn_text.text()) == 0 \
                or len(self.year_text.text()) == 0:
            return
        if not self.book_format_combo.hasFocus():
            return
        if self.book is None:
            self.book = openlibrary.Book(
                self.title_text.text(),
                self.author_list.text().split(","),
                self.isbn_text.text(),
                self.languages_combo.currentData(),
                self.year_text.text(),
                self.book_format_combo.currentData()
            )
        else:
            self.book.set_title(self.title_text.text())
            self.book.set_author(self.author_list.text())
            self.book.set_isbn(self.isbn_text.text())
            self.book.set_language(self.languages_combo.currentData())
            self.book.set_year(self.year_text.text())
            self.book.set_book_format(self.book_format_combo.currentData())

        with open(self.config['db_file'], "a+") as outfile:
            outfile.write(json.dumps(self.book.json(), sort_keys=True, ensure_ascii=False))
            outfile.write("\n")
        self.accept()


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


class MainWindow(QMainWindow):
    def __init__(self, config: dict):
        super().__init__()
        self.config = config

        self.setWindowFlags(self.windowFlags() & ~Qt.WindowMaximizeButtonHint)
        self.layout().setSizeConstraint(QLayout.SetFixedSize)
        self.setWindowTitle("Books")

        quit_action = QShortcut(QKeySequence('Ctrl+Q'), self)
        quit_action.activated.connect(self.close)

        tools = self.addToolBar("File")
        tools.setMovable(False)

        add_action = tools.addAction("New Book")
        add_action.setShortcut(QKeySequence('Ctrl+N'))
        add_action.triggered.connect(self.on_add)

        settings_action = tools.addAction("Settings")
        settings_action.setShortcut(QKeySequence('Ctrl+K'))
        settings_action.triggered.connect(self.on_settings)

        self.search = SearchWidget(self.on_search)
        self.setCentralWidget(self.search)

        self.statusBar().setSizeGripEnabled(False)
        self.statusBar().showMessage("Ready")

    def on_search(self, param: str):
        self.statusBar().showMessage("Searching: " + param)
        try:
            book = openlibrary.search(param, self.config)
            book_view = BookViewWidget(self, self.config, book)
            if book_view.exec():
                self.statusBar().showMessage("Saved!")
            else:
                self.statusBar().showMessage("Ready")
            self.search.clear()
        except openlibrary.SearchException as error:
            if hasattr(error, 'message'):
                self.statusBar().showMessage("Error: " + error.message)
            else:
                self.statusBar().showMessage("Error: " + str(error))

    def on_add(self):
        self.statusBar().showMessage("Adding new book")
        book_view = BookViewWidget(self, self.config, param=self.search.get_text())
        if book_view.exec():
            self.statusBar().showMessage("Added!")
        else:
            self.statusBar().showMessage("Ready")
        self.search.clear()

    def on_settings(self):
        self.statusBar().showMessage("Settings")
        settings_view = SettingsViewWidget(self, self.config)
        if settings_view.exec():
            self.statusBar().showMessage("Settings updated!")
        else:
            self.statusBar().showMessage("Ready")


if __name__ == '__main__':
    appctxt = ApplicationContext()
    stylesheet = appctxt.get_resource('styles.qss')
    appctxt.app.setStyleSheet(open(stylesheet).read())

    with open('./database/config.json') as infile:
        data = json.load(infile)

    window = MainWindow(data)

    window.show()
    exit_code = appctxt.app.exec_()
    sys.exit(exit_code)
