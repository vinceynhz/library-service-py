"""
 :author: vic on 2022-11-08
"""
from PyQt5.QtWidgets import QHBoxLayout, QLineEdit, QLayout, QLabel, QFormLayout, QVBoxLayout, QPushButton, \
    QStatusBar, QCheckBox
from PyQt5.QtCore import Qt

from .book_view import QNavDialog

from typing import Union

import logging
import books.config
import books.client


class QStatusDialog(QNavDialog):
    def __init__(self, parent):
        super().__init__(parent)
        self.status_bar: QStatusBar = None

    def get_status_bar(self) -> QStatusBar:
        self.status_bar = QStatusBar()
        self.status_bar.setProperty("status", True)
        self.status_bar.showMessage("Ready")
        self.status_bar.setSizeGripEnabled(False)
        return self.status_bar


class ContributorViewWidget(QStatusDialog):
    def __init__(self, parent):
        super().__init__(parent)

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        form = QFormLayout()
        form.setContentsMargins(10, 10, 10, 10)
        form.setSizeConstraint(QLayout.SetFixedSize)

        self.first_name_text = QLineEdit()
        form.addRow(QLabel("First Name"), self.first_name_text)

        self.last_names_text = QLineEdit()
        form.addRow(QLabel("Last Name(s)"), self.last_names_text)

        self.honorific_text = QLineEdit()
        form.addRow(QLabel("Honorific"), self.honorific_text)

        self.first_name_text.returnPressed.connect(self.last_names_text.setFocus)
        self.last_names_text.returnPressed.connect(self.honorific_text.setFocus)
        self.honorific_text.returnPressed.connect(self.first_name_text.setFocus)

        self.add_another: QCheckBox = None

        self.buttons(form)

        layout.addLayout(form)
        layout.addWidget(self.get_status_bar())
        self.setLayout(layout)

    # override
    def get_title(self) -> str:
        return "Contributor - New"

    # override
    def save(self) -> None:
        result = self._get_updated_contributor()
        if result is not None:
            try:
                books.client.add_contributor(result)
                if self.add_another.isChecked():
                    # clear stuff
                    self.status_bar.showMessage("Added!")
                    self._clear()
                else:
                    # and we get out of the dialog
                    self.accept()
            except books.client.LibraryClientException as exception:
                self.status_bar.showMessage(f"{exception.status_code} - {exception.message}")
                logging.getLogger("library.ui").error(str(exception))
            except (Exception,) as exception:
                self.status_bar.showMessage(f"{str(exception)}")
                logging.getLogger("library.ui").error(str(exception))

    # override
    def buttons(self, layout: QFormLayout) -> None:
        button_box = QHBoxLayout()
        button_box.setAlignment(Qt.AlignRight)
        self.add_another = QCheckBox(self.tr("&Add another"))

        button_cancel = QPushButton(self.tr("&Cancel"))
        button_cancel.clicked.connect(self.reject)

        self.button_save = QPushButton(self.tr("&Save"))
        self.button_save.clicked.connect(self.save)

        button_box.addWidget(self.add_another)
        button_box.addWidget(button_cancel)
        button_box.addWidget(self.button_save)

        layout.addRow(button_box)

    def _clear(self):
        self.first_name_text.setText("")
        self.first_name_text.setFocus()
        self.last_names_text.setText("")
        self.honorific_text.setText("")

    def _get_updated_contributor(self) -> Union[dict, None]:
        first_name = self.first_name_text.text().strip()
        last_names = self.last_names_text.text().strip()
        honorific = self.honorific_text.text().strip()
        if len(first_name) == 0:
            return None
        contributor = {
            'first_name': first_name,
        }
        if len(last_names) > 0:
            contributor['last_names'] = last_names
        if len(honorific) > 0:
            contributor['honorific'] = honorific
        return contributor
