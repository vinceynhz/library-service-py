"""
 :author: vic on 2022-11-04
"""
from PyQt5.QtWidgets import QFormLayout, QHBoxLayout, QTableWidgetItem, QLabel, QPushButton, QSpinBox
from PyQt5.QtCore import Qt

from .book_view import BookViewWidget, ActionToolButton

from typing import Callable

import json
import authority


def concat(a: Callable[[], None], b: Callable[[], None]):
    a()
    b()


class BookBrowserWidget(BookViewWidget):
    def __init__(self, parent, config: dict):
        super().__init__(parent, config)
        db_file = config['db_file']
        with open(db_file) as infile:
            self.data = infile.readlines()
        self.current_index.setRange(1, len(self.data))
        self.max_index.setText(f"of {len(self.data)}")
        self.rendering_book = False
        self.json_book = None
        self.book_unchanged = False
        self.render_book()

        self.title_text.textChanged.connect(self.book_match)
        self.author_table.itemChanged.connect(self.book_match)
        self.author_table.itemDeleted.connect(self.book_match)
        self.isbn_text.textChanged.connect(self.book_match)
        self.year_text.textChanged.connect(self.book_match)
        self.languages_combo.currentTextChanged.connect(self.book_match)
        self.book_format_combo.currentTextChanged.connect(self.book_match)

    def render_book(self):
        # to prevent match checks while we populate the book
        self.rendering_book = True
        # remove line jump
        raw_book = self.data[self.current_index.value() - 1][:-1]
        self.json_book = json.loads(raw_book)
        self.title_text.setText(self.json_book['title'])
        self.author_table.setRowCount(len(self.json_book['author']))
        for i, author in enumerate(self.json_book['author']):
            item = QTableWidgetItem(author)
            self.author_table.setItem(i, 0, item)
        self.isbn_text.setText(self.json_book['isbn'])
        self.year_text.setText(str(self.json_book['year']))
        self.languages_combo.setCurrentText(authority.desc_lang(self.json_book['language']))
        self.book_format_combo.setCurrentText(self.json_book['book_format'])
        self.rendering_book = False
        # now we check for match
        self.book_match()

    def book_match(self):
        if not self.rendering_book:
            self.book_unchanged = self.title_text.text() == self.json_book['title'] \
                                  and self.author_table.get_data() == self.json_book['author'] \
                                  and self.isbn_text.text() == self.json_book['isbn'] \
                                  and self.year_text.text() == str(self.json_book['year']) \
                                  and self.languages_combo.currentData() == self.json_book['language'] \
                                  and self.book_format_combo.currentText() == self.json_book['book_format']
            if self.book_unchanged:
                self.setWindowTitle(self.get_title())
                self.button_save.setEnabled(False)
            else:
                self.setWindowTitle(self.get_title() + '*')
                self.button_save.setEnabled(True)

    def first_page(self):
        self.current_index.setValue(1)

    def last_page(self):
        self.current_index.setValue(len(self.data))

    def next_page(self):
        current_value = self.current_index.value()
        if current_value < (len(self.data)):
            self.current_index.setValue(current_value + 1)

    def prev_page(self):
        current_value = self.current_index.value()
        if current_value > 1:
            self.current_index.setValue(current_value - 1)

    def save(self) -> None:
        print("Save called")
        if self.book_unchanged:
            return
        result = self.get_updated_book()
        if result is not None:
            updated_book = json.dumps(result.json(), sort_keys=True, ensure_ascii=False)
            self.data[self.current_index.value() - 1] = updated_book + '\n'

            with open(self.config['db_file'], "w+") as outfile:
                outfile.writelines(self.data)

            self.render_book()

    def get_title(self):
        return "Books - Browse"

    # noinspection PyUnresolvedReferences
    def buttons(self, layout: QFormLayout):
        # add browse buttons
        first_book = ActionToolButton(self, "First Page", "Shift+Alt+Left", "first_page.png", self.first_page, "nav")
        prev_book = ActionToolButton(self, "Prev Page", "Alt+Left", "prev_page.png", self.prev_page, "nav")
        next_book = ActionToolButton(self, "Next Page", "Alt+Right", "next_page.png", self.next_page, "nav")
        last_book = ActionToolButton(self, "Last Page", "Shift+Alt+Right", "last_page.png", self.last_page, "nav")

        self.current_index = QSpinBox()
        self.current_index.setValue(1)
        self.current_index.valueChanged.connect(self.render_book)
        self.current_index.setProperty("nav", True)
        self.max_index = QLabel("of 999")
        self.max_index.setAlignment(Qt.AlignCenter)
        self.max_index.setProperty("nav", True)

        nav_box = QHBoxLayout()
        nav_box.setAlignment(Qt.AlignCenter)
        nav_box.addWidget(first_book)
        nav_box.addWidget(prev_book)
        nav_box.addWidget(self.current_index)
        nav_box.addWidget(self.max_index)
        nav_box.addWidget(next_book)
        nav_box.addWidget(last_book)

        layout.addRow(nav_box)

        button_box = QHBoxLayout()
        button_box.setAlignment(Qt.AlignRight)
        self.button_save = QPushButton("Save")
        self.button_save.clicked.connect(self.save)
        self.button_save.setEnabled(False)

        button_ok = QPushButton("Ok")
        button_ok.clicked.connect(self.accept)

        button_box.addWidget(self.button_save)
        button_box.addWidget(button_ok)
        layout.addRow(button_box)
