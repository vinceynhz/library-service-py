"""
 :author: vic on 2022-11-02
"""
from PyQt5.QtWidgets import QLineEdit, QLayout, QDialog, QDialogButtonBox, QLabel, QFormLayout, QShortcut, QComboBox
from PyQt5.QtGui import QKeySequence

import json

import openlibrary
import authority


# noinspection PyUnresolvedReferences
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
