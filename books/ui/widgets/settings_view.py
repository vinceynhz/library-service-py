"""
 :author: vic on 2022-11-02
"""
from PyQt5.QtWidgets import QLineEdit, QLayout, QDialog, QDialogButtonBox, QLabel, QFormLayout, QShortcut, QComboBox
from PyQt5.QtGui import QKeySequence

from database.schema import BookFormat

import authority
import books.config


# noinspection PyUnresolvedReferences
class SettingsViewWidget(QDialog):
    def __init__(self, parent):
        super().__init__(parent)
        self.setWindowTitle("Books - Settings")

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
        self.languages_combo.setCurrentText(authority.desc_lang(books.config.get('language')))

        self.book_format_combo = QComboBox()
        for name, member in BookFormat.__members__.items():
            self.book_format_combo.addItem(name, userData=member)
        form.addRow(QLabel("Default Format"), self.book_format_combo)
        self.book_format_combo.setCurrentText(books.config.get('book_format'))

        self.file_text = QLineEdit()
        self.file_text.setText(books.config.get('db_file'))
        form.addRow(QLabel("Database File"), self.file_text)

        self.open_library_url_text = QLineEdit()
        self.open_library_url_text.setText(books.config.get('openlibrary_search_url'))
        form.addRow(QLabel("OpenLibrary URL"), self.open_library_url_text)

        self.library_service_url_text = QLineEdit()
        self.library_service_url_text.setText(books.config.get('library_service_url'))
        form.addRow(QLabel("Library Service URL"), self.library_service_url_text)

        form.addRow(button_box)
        self.setLayout(form)

    def save(self):
        if len(self.file_text.text()) == 0 \
                or len(self.open_library_url_text.text()) == 0 \
                or len(self.library_service_url_text.text()) == 0:
            return

        config = {
            'db_file': self.file_text.text().strip(),
            'book_format': self.book_format_combo.currentData().name,
            'language': self.languages_combo.currentData(),
            'openlibrary_search_url': self.open_library_url_text.text(),
            'library_service_url': self.library_service_url_text.text()
        }

        books.config.update(config)

        self.accept()
