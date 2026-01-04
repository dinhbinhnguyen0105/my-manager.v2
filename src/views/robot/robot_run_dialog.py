# src/views/robot/robot_run_dialog.py
from PyQt6.QtWidgets import QDialog, QMessageBox
from PyQt6.QtCore import Qt, pyqtSignal

from src.ui.dialog_robot_run_ui import Ui_Dialog_RobotRun

class RobotRun(QDialog, Ui_Dialog_RobotRun):
    setting_data_signal = pyqtSignal(dict)
    def __init__(self, parent = None):
        super(RobotRun, self).__init__(parent)
        self.setupUi(self)
        self.setWindowTitle("Create new profile".title())
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        self.setupValidation()


    def setupValidation(self):
        """Thực hiện validate các trường input trước khi emit."""

        # 1. Thread Number (Số luồng)
        try:
            thread_num = int(self.thread_num_input.text())
            if thread_num <= 0:
                raise ValueError("Thread number must be greater than 0.")
        except ValueError as e:
            QMessageBox.critical(
                self, "Validation Error", f"Invalid Thread Number: {e}"
            )
            self.thread_num_input.setFocus()
            return None

        # 2. Group Number (Số nhóm đăng bài)
        try:
            group_num = int(self.group_num_input.text())
            if group_num < 0:
                raise ValueError("Group number cannot be negative.")
        except ValueError as e:
            QMessageBox.critical(self, "Validation Error", f"Invalid Group Number: {e}")
            self.group_num_input.setFocus()
            return None

        # 3. Delay Time (Thời gian delay)
        try:
            # FloatValidator đã đảm bảo đây là số hợp lệ
            delay_time = float(self.delay_time_input.text())
            if delay_time <= 0:
                raise ValueError("Delay time must be greater than 0.")
        except ValueError as e:
            QMessageBox.critical(self, "Validation Error", f"Invalid Delay Time: {e}")
            self.delay_time_input.setFocus()
            return None

    def accept(self):
        self.setting_data_signal.emit(
            {
                "thread_num": int(self.thread_num_input.text()),
                "group_num": int(self.group_num_input.text()),
                "delay_time": float(self.delay_time_input.text()),
                "rewrite_by_ai": self.is_rewrite_by_ai.isChecked(),
            }
        )
        return super().accept()

    def reject(self):
        return super().reject()