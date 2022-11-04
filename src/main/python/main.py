from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMainWindow, QLayout, QShortcut, QApplication
from PyQt5.QtGui import QKeySequence, QIcon

from src.main.python.base import get_resource
from src.main.python.widgets.settings_view import SettingsViewWidget
from src.main.python.widgets.book_view import BookViewWidget
from src.main.python.widgets.search_widget import SearchWidget

import sys
import json

import openlibrary

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

        add_action = tools.addAction(QIcon(get_resource("book.png")), "New Book")
        add_action.setShortcut(QKeySequence('Ctrl+N'))
        add_action.triggered.connect(self.on_add)
        add_action.setToolTip("New Book - Ctrl+N")

        tools.addSeparator()

        settings_action = tools.addAction(QIcon(get_resource("settings.png")), "Settings")
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
    if __win__:
        import ctypes
        myappid = 'tandv.library.ui' # arbitrary string
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

    app = QApplication(sys.argv)

    stylesheet = get_resource('styles.qss')
    app.setStyleSheet(open(stylesheet).read())

    icon = QIcon()
    icon.addFile('./src/main/icons/base/16.png')
    icon.addFile('./src/main/icons/base/24.png')
    icon.addFile('./src/main/icons/base/32.png')
    icon.addFile('./src/main/icons/base/48.png')
    icon.addFile('./src/main/icons/base/64.png')
    app.setWindowIcon(icon)

    with open('./database/config.json') as infile:
        data = json.load(infile)

    window = MainWindow(data)
    window.show()

    exit_code = app.exec_()
    sys.exit(exit_code)
