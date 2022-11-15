"""
 :author: vic on 2022-11-04
"""
from PyQt5.QtWidgets import QFormLayout, QHBoxLayout, QTableWidgetItem, QPushButton
from PyQt5.QtCore import Qt

from .book_view import BookViewWidget

from typing import Callable

import json
import authority
import books.config


def concat(a: Callable[[], None], b: Callable[[], None]):
    a()
    b()


class BookBrowserWidget(BookViewWidget):
    def __init__(self, parent):
        super().__init__(parent)
        db_file = books.config.get('db_file')
        with open(db_file) as infile:
            self.data = infile.readlines()
        self.current_index.setRange(1, len(self.data))
        self.max_index.setText(f"of {len(self.data)}")
        self.render_data()

        self.title_text.textChanged.connect(self.data_match)
        self.author_table.itemChanged.connect(self.data_match)
        self.author_table.itemDeleted.connect(self.data_match)
        self.isbn_text.textChanged.connect(self.data_match)
        self.year_text.textChanged.connect(self.data_match)
        self.languages_combo.currentTextChanged.connect(self.data_match)
        self.book_format_combo.currentTextChanged.connect(self.data_match)

    # override
    def save(self) -> None:
        if self.data_unchanged:
            return
        result = self._get_updated_book()
        if result is not None:
            updated_book = json.dumps(result.json(), sort_keys=True, ensure_ascii=False)
            self.data[self.current_index.value() - 1] = updated_book + '\n'

            with open(books.config.get('db_file'), "w+") as outfile:
                outfile.writelines(self.data)

            self.render_data()

    # override
    def get_title(self):
        return "Books - Browse"

    # override
    def buttons(self, layout: QFormLayout):
        layout.addRow(self.nav_buttons())

        button_box = QHBoxLayout()
        button_box.setAlignment(Qt.AlignRight)

        button_done = QPushButton(self.tr("&Done"))
        button_done.clicked.connect(self.accept)

        self.button_save = QPushButton(self.tr("&Save"))
        self.button_save.clicked.connect(self.save)
        self.button_save.setEnabled(False)

        button_box.addWidget(button_done)
        button_box.addWidget(self.button_save)
        layout.addRow(button_box)

    # override
    def is_data_unchanged(self) -> bool:
        return self.title_text.text() == self.json_data['title'] \
               and self.author_table.get_data() == self.json_data['author'] \
               and self.isbn_text.text() == self.json_data['isbn'] \
               and self.year_text.text() == str(self.json_data['year']) \
               and self.languages_combo.currentData() == self.json_data['language'] \
               and self.book_format_combo.currentText() == self.json_data['book_format']

    # override
    def update_fields(self):
        # remove line jump
        raw_book = self.data[self.current_index.value() - 1][:-1]
        self.json_data = json.loads(raw_book)
        self.title_text.setText(self.json_data['title'])
        self.author_table.setRowCount(len(self.json_data['author']))
        for i, author in enumerate(self.json_data['author']):
            item = QTableWidgetItem(author)
            self.author_table.setItem(i, 0, item)
        self.isbn_text.setText(self.json_data['isbn'])
        self.year_text.setText(str(self.json_data['year']))
        self.languages_combo.setCurrentText(authority.desc_lang(self.json_data['language']))
        self.book_format_combo.setCurrentText(self.json_data['book_format'])
