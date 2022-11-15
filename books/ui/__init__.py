from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMainWindow, QLayout, QShortcut, QApplication
from PyQt5.QtGui import QKeySequence, QIcon

from books.ui.widgets import SettingsViewWidget, BookViewWidget, BookBrowserWidget, ContributorViewWidget, \
    ContributorBrowserWidget, SearchWidget
from books.ui.resources import get_icon, get_resource

import sys
import logging
import books.openlibrary as openlibrary
import books.config

__win__ = 'win' in sys.platform


# noinspection PyUnresolvedReferences
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowMaximizeButtonHint)
        self.layout().setSizeConstraint(QLayout.SetFixedSize)
        self.setWindowTitle("Books")

        quit_action = QShortcut(QKeySequence('Ctrl+Q'), self)
        quit_action.activated.connect(self.close)

        tools = self.addToolBar("File")
        tools.setMovable(False)

        add_book_action = tools.addAction(QIcon(get_icon("book.png")), "New Book")
        add_book_action.setShortcut(QKeySequence('Ctrl+N'))
        add_book_action.triggered.connect(self.on_add_book)
        add_book_action.setToolTip("New Book - Ctrl+N")

        browse_books_action = tools.addAction(QIcon(get_icon("library.png")), "Browse Books")
        browse_books_action.setShortcut(QKeySequence('Ctrl+B'))
        browse_books_action.triggered.connect(self.on_browse_books)
        browse_books_action.setToolTip("Browse - Ctrl+B")

        tools.addSeparator()

        add_contributor_action = tools.addAction(QIcon(get_icon("new_contributor.png")), "New Contributor")
        add_contributor_action.triggered.connect(self.on_add_contributor)

        browse_contributors_action = tools.addAction(QIcon(get_icon("contributors.png")), "Browse Contributor")
        browse_contributors_action.triggered.connect(self.on_browse_contributors)

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
            book = openlibrary.search(param)
            book_view = BookViewWidget(self, book)
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
            logging.getLogger("library.ui").error(error)

    def on_add_book(self):
        self.statusBar().showMessage("Adding new book")
        book_view = BookViewWidget(self, param=self.search.get_text())
        if book_view.exec():
            self.statusBar().showMessage("Added!")
        else:
            self.statusBar().showMessage("Ready")
        self.search.clear()

    def on_browse_books(self):
        self.statusBar().showMessage("Browse books")
        book_browser = BookBrowserWidget(self)
        book_browser.exec()
        self.statusBar().showMessage("Done!")

    def on_add_contributor(self):
        self.statusBar().showMessage("Adding new contributor")
        contributor_view = ContributorViewWidget(self)
        if contributor_view.exec():
            self.statusBar().showMessage("Added!")
        else:
            self.statusBar().showMessage("Ready")

    def on_browse_contributors(self):
        self.statusBar().showMessage("Browse contributors")
        contributor_browser = ContributorBrowserWidget(self)
        contributor_browser.exec()
        self.statusBar().showMessage("Done!")

    def on_settings(self):
        self.statusBar().showMessage("Settings")
        settings_view = SettingsViewWidget(self)
        if settings_view.exec():
            self.statusBar().showMessage("Settings updated!")
        else:
            self.statusBar().showMessage("Ready")


def run(argv):
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

    books.config.load("library.ui")

    window = MainWindow()
    window.show()

    exit_code = app.exec_()

    # window.search.hist
    sys.exit(exit_code)
