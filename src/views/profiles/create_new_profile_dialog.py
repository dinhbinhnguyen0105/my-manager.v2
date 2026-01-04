# src/views/profiles/create_new_profile_dialog.py
import datetime
from PyQt6.QtWidgets import QDialog, QMessageBox
from PyQt6.QtCore import Qt, pyqtSignal

from src.utils.password_handler import create_strong_password

from src.ui.dialog_profile_ui import Ui_Dialog_Profile

from src.my_constants import PROFILE__NAME_OPTIONS
PROFILE_LIVE = 1
PROFILE_DEAD = 0

class CreateNewProfileDialog(QDialog, Ui_Dialog_Profile):
    profile_data_signal = pyqtSignal(dict)
    def __init__(self, parent = None):
        super(CreateNewProfileDialog, self).__init__(parent)
        self.setupUi(self)
        self.setWindowTitle("Create new profile".title())
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        self.setModal(False)
        self.setup_data()
    
    def setup_data(self):
        self.name_combobox.clear()
        for key, value in PROFILE__NAME_OPTIONS.items():
            self.name_combobox.addItem(value, key)
        self.group_input.setText("-1")
        self.type_input.setText("take_care")
        self.password_input.setText(create_strong_password())
        current_date = datetime.date.today()
        x = current_date.day
        if x % 2 == 0:
            self.note_input.setText("even")
        else:
            self.note_input.setText("odd")
    
    def accept(self):
        data = {
            "id": None,
            "uid": self.uid_input.text().strip(),
            "status": PROFILE_LIVE if self.status_checkbox.isChecked() else PROFILE_DEAD,
            "username": self.username_input.text().strip(),
            "password": self.password_input.text().strip(),
            "two_fa": self.two_fa_input.text().strip(),
            "email": self.email_input.text().strip(),
            "email_password": self.email_password_input.text().strip(),
            "phone_number": self.phone_number_input.text().strip(),
            "profile_note": self.note_input.text().strip(),
            "profile_name": self.name_combobox.itemData(self.name_combobox.currentIndex()),
            "profile_type": self.type_input.text().strip(),
            "profile_group": float(self.group_input.text().strip()),
            "mobile_ua": "",
            "desktop_ua": "",
            "created_at": None,
            "updated_at": None,
        }
        self.name_combobox.itemData(self.name_combobox.currentIndex())
        if not data.get("username"):
            QMessageBox.warning(
                self,
                "The 'username' field is empty",
                "The 'username' field is required.",
                QMessageBox.StandardButton.Retry,
            )
            return
        if not data.get("password"):
            QMessageBox.warning(
                self,
                "The 'password' field is empty",
                "The 'password' field is required.",
                QMessageBox.StandardButton.Retry,
            )
            return
        self.profile_data_signal.emit(data)
        return super().accept()

    def reject(self):
        return super().reject()