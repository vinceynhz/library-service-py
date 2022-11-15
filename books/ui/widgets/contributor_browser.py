"""
 :author: vic on 2022-11-14
"""
from PyQt5.QtWidgets import QFormLayout, QHBoxLayout, QPushButton
from PyQt5.QtCore import Qt

from typing import Union
from .contributor_view import ContributorViewWidget

import logging
import books.client


class ContributorBrowserWidget(ContributorViewWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.data = books.client.get_contributors()
        self.current_index.setRange(1, len(self.data))
        self.max_index.setText(f"of {len(self.data)}")

        self.render_data()

        self.first_name_text.textChanged.connect(self.data_match)
        self.last_names_text.textChanged.connect(self.data_match)
        self.honorific_text.textChanged.connect(self.data_match)

    # override
    def save(self) -> None:
        if self.data_unchanged:
            return
        result = self._get_updated_contributor()
        if result is not None:
            try:
                updated = books.client.update_contributor(result)
                self.data[self.current_index.value() - 1] = updated
                self.render_data()
            except books.client.LibraryClientException as exception:
                self.status_bar.showMessage(f"{exception.status_code} - {exception.message}")
                logging.getLogger("library.ui").error(str(exception))
            except (Exception,) as exception:
                self.status_bar.showMessage(f"{str(exception)}")
                logging.getLogger("library.ui").error(str(exception))

    # override
    def get_title(self):
        return "Contributor - Browse"

    # override
    def buttons(self, layout: QFormLayout):
        # add browse buttons
        layout.addRow(self.nav_buttons())

        button_box = QHBoxLayout()
        button_box.setAlignment(Qt.AlignRight)

        button_done = QPushButton(self.tr("&Done"))
        button_done.clicked.connect(self.reject)

        self.button_save = QPushButton(self.tr("&Save"))
        self.button_save.clicked.connect(self.save)
        self.button_save.setEnabled(False)

        button_box.addWidget(button_done)
        button_box.addWidget(self.button_save)

        layout.addRow(button_box)

    # override
    def update_fields(self):
        self.json_data = self.data[self.current_index.value() - 1]
        self.first_name_text.setText(self.json_data['first_name'])
        self.last_names_text.setText(self.json_data['last_names'])
        self.honorific_text.setText(self._get_current_honorific())

    def is_data_unchanged(self) -> bool:
        return self.first_name_text.text() == self.json_data['first_name'] \
               and self.last_names_text.text() == self.json_data['last_names'] \
               and self.honorific_text.text() == self._get_current_honorific()

    def _get_current_honorific(self):
        if 'honorific' in self.json_data and self.json_data['honorific'] is not None:
            return self.json_data['honorific']
        else:
            return ''

    def _get_updated_contributor(self) -> Union[dict, None]:
        first_name = self.first_name_text.text().strip()
        last_names = self.last_names_text.text().strip()
        honorific = self.honorific_text.text().strip()
        if len(first_name) == 0 \
                or len(last_names) == 0:
            return None
        contributor = {
            'id': self.json_data['id']
        }
        if first_name != self.json_data['first_name']:
            contributor['first_name'] = first_name
        if last_names != self.json_data['last_names']:
            contributor['last_names'] = last_names
        if honorific != self.json_data['honorific']:
            contributor['honorific'] = honorific

        return contributor
