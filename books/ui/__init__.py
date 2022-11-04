from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMainWindow, QLayout, QShortcut, QApplication
from PyQt5.QtGui import QKeySequence, QIcon

from books.ui.widgets import SettingsViewWidget, BookViewWidget, SearchWidget
from books.ui.resources import get_icon, get_resource

import sys
import json
import logging
import books.openlibrary as openlibrary

__win__ = 'win' in sys.platform


# noinspection PyUnresolvedReferences
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

        add_action = tools.addAction(QIcon(get_icon("book.png")), "New Book")
        add_action.setShortcut(QKeySequence('Ctrl+N'))
        add_action.triggered.connect(self.on_add)
        add_action.setToolTip("New Book - Ctrl+N")

        tools.addSeparator()

        settings_action = tools.addAction(QIcon(get_icon("settings.png")), "Settings")
        settings_action.setShortcut(QKeySequence('Ctrl+K'))
        settings_action.triggered.connect(self.on_settings)
        settings_action.setToolTip("Settings - Ctrl+K")

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
        except (Exception,) as error:
            if hasattr(error, 'message'):
                self.statusBar().showMessage("Error: " + error.message)
            else:
                self.statusBar().showMessage("Error: " + str(error))
            logging.error(error)

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


def run(argv):
    logging.basicConfig(level=logging.DEBUG, filename='./ui.log')
    if __win__:
        import ctypes
        myappid = 'tandv.library.books.ui'  # arbitrary string
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

    app = QApplication(argv)

    stylesheet = get_resource('styles.qss')
    app.setStyleSheet(open(stylesheet).read())

    icon = QIcon()
    if __win__:
        icon.addFile(get_icon('16.png'))
        icon.addFile(get_icon('24.png'))
        icon.addFile(get_icon('32.png'))
        icon.addFile(get_icon('48.png'))
        icon.addFile(get_icon('64.png'))
    else:
        icon.addFile(get_icon('128.png'))
        icon.addFile(get_icon('256.png'))
        icon.addFile(get_icon('512.png'))
        icon.addFile(get_icon('1024.png'))
    app.setWindowIcon(icon)

    with open('./database/config.json') as infile:
        data = json.load(infile)

    window = MainWindow(data)
    window.show()

    exit_code = app.exec_()
    sys.exit(exit_code)
