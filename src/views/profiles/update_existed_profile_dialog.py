# src/views/profiles/create_new_profile_dialog.py
import datetime
from PyQt6.QtWidgets import QDialog, QMessageBox
from PyQt6.QtCore import Qt, pyqtSignal

from src.my_types import Profile_Type
from src.my_constants import PROFILE__NAME_OPTIONS
PROFILE_LIVE = 1
PROFILE_DEAD = 0
from src.ui.dialog_profile_ui import Ui_Dialog_Profile

class UpdateExistedProfileDialog(QDialog, Ui_Dialog_Profile):
    profile_data_signal = pyqtSignal(dict)
    def __init__(self, prev_data: Profile_Type, parent = None):
        super(UpdateExistedProfileDialog, self).__init__(parent)
        self.setupUi(self)
        self.setWindowTitle("Create new profile".title())
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        self.prev_data = prev_data
        self.setModal(False)
        self.setup_data()

    def setup_data(self):
        self.name_combobox.clear()
        for key, value in PROFILE__NAME_OPTIONS.items():
            self.name_combobox.addItem(value, key)
                
        self.uid_input.setText(self.prev_data.uid),
        self.status_checkbox.setChecked(True if self.prev_data.status == PROFILE_LIVE else False)
        self.username_input.setText(self.prev_data.username)
        self.password_input.setText(self.prev_data.password)
        self.two_fa_input.setText(self.prev_data.two_fa)
        self.email_input.setText(self.prev_data.email)
        self.email_password_input.setText(self.prev_data.email_password)
        self.phone_number_input.setText(self.prev_data.phone_number)
        self.note_input.setText(self.prev_data.profile_note)
        self.name_combobox.setCurrentIndex(self.name_combobox.findData(self.prev_data.profile_name))
        self.type_input.setText(self.prev_data.profile_type)
        self.group_input.setText(str(self.prev_data.profile_group))
    
    def accept(self):
        data = {
            "id": self.prev_data.id,
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
            "mobile_ua": self.prev_data.mobile_ua,
            "desktop_ua": self.prev_data.desktop_ua,
            "created_at": self.prev_data.created_at,
            "updated_at": None,
        }
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