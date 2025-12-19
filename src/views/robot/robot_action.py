# src/views/robot/robot_action.py
from typing import List, Dict, Any
from PyQt6.QtWidgets import (
    QWidget,
    QFileDialog,
)
from PyQt6.QtCore import (
    Qt,
    pyqtSlot,
    QUrl,
)
from PyQt6.QtGui import QDragEnterEvent

from src.ui.robot_action_ui import Ui_RobotAction

from src.my_constants import (
    ROBOT_ACTION_OPTIONS,
    SELL__BY_MARKETPLACE,
    SELL__BY_GROUP,
    DISCUSSION__TO_GROUP,
    DISCUSSION__TO_NEW_FEED,
    SHARE__BY_MOBILE,
    SHARE__BY_DESKTOP,
    LAUNCH,
    TAKE_CARE__JOIN_GROUP,
    TAKE_CARE__ADD_FRIEND,
    TAKE_CARE__COMMENT_TO_GROUP,
    TAKE_CARE__COMMENT_TO_FRIEND_WALL,
    GET_COOKIES,
)

ACTION_OPTIONS = {
    "random": "random pid",
    "pid": "pid",
    "custom": "custom content"
}


class RobotAction(QWidget, Ui_RobotAction):
    def __init__(self, parent=None):
        super(RobotAction, self).__init__(parent)
        self.setupUi(self)
        self.setWindowTitle("facebook action widget".title())
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)

        self.image_paths: List[str] = []
        self.setup_UI()
        self.setup_data()
        self.setup_conections()

    def setup_UI(self):
        self.action_option.setHidden(True)
        # self.action_option.setItemData()
        self.action_payload.setHidden(True)
        self.action_payload.setText("")

        self.group_url_container.setHidden(True)
        self.group_url_input.setText("https://www.facebook.com/groups/475205321869395")

        self.content_container.setHidden(True)
        self.product_title_input.setText("")
        self.product_description_input.setPlainText("")
        self.product_images_list.clear()

    def setup_data(self):
        self.action_name.clear()
        self.action_name.addItem("--- Select action ---", None)
        self.action_name.setCurrentIndex(0)
        for key, value in ROBOT_ACTION_OPTIONS.items():
            self.action_name.addItem(value.capitalize(), key)

    def setup_conections(self):
        self.action_delete_btn.clicked.connect(self.on_delete_clicked)
        self.action_name.currentIndexChanged.connect(
            self.on_name_option_changed)
        self.action_option.currentIndexChanged.connect(self.on_action_option_changed)
        self.product_image_btn.setAcceptDrops(True)
        self.product_image_btn.dragEnterEvent = self.open_images_btn_dragEnterEvent
        self.product_image_btn.dropEvent = self.open_images_btn_dropEvent
        self.product_image_btn.clicked.connect(self.open_image_dialog)

    def get_value(self):
        data = {}
        current_action = self.action_name.currentData(
            Qt.ItemDataRole.UserRole)
        if current_action in [
            SHARE__BY_MOBILE,
        ]:
            data["mobile_mode"] = True
        else:
            data["mobile_mode"] = False
        if current_action == SELL__BY_GROUP:
            url = self.group_url_input.text()
            data["group_url"] = url if url.startswith("https://www.facebook.com/groups") else "https://www.facebook.com/groups/475205321869395"
        data["action_name"] = current_action

        if not self.action_option.hide():
            current_option = self.action_option.currentData(
                Qt.ItemDataRole.UserRole
            )
            if current_option == list(ACTION_OPTIONS.keys())[0]:
                data["pid"] = "random"
            elif current_option == list(ACTION_OPTIONS.keys())[1]:
                data["pid"] = self.action_payload.text()
            elif current_option == list(ACTION_OPTIONS.keys())[2]:
                data["title"] = self.product_title_input.text().upper()
                data["description"] = self.product_description_input.getPaintContext()
                data["image_paths"] = self.image_paths
        return data

# -----------------
# Slot
# -----------------

    @pyqtSlot(QDragEnterEvent)
    def open_images_btn_dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            # Chỉ chấp nhận nếu có file ảnh
            for url in event.mimeData().urls():
                if (
                    url.toLocalFile()
                    .lower()
                    .endswith((".png", ".jpg", ".jpeg", ".gif"))
                ):
                    event.acceptProposedAction()
                    return
        event.ignore()

    @pyqtSlot(QDragEnterEvent)
    def open_images_btn_dropEvent(self, event):
        urls = event.mimeData().urls()
        image_paths = []
        for url in urls:
            path = url.toLocalFile()
            if path.lower().endswith((".png", ".jpg", ".jpeg", ".gif")):
                image_paths.append(path)
        if image_paths:
            self.image_paths = image_paths
            # populate the product images list widget
            try:
                self.product_images_list.clear()
                self.product_images_list.setVisible(True)
                self.product_images_list.addItems(self.image_paths)
            except Exception:
                pass
        event.acceptProposedAction()

    @pyqtSlot()
    def open_image_dialog(self):
        """Open a file dialog to select multiple images and populate the images list."""
        options = QFileDialog.Option.ReadOnly
        files, _ = QFileDialog.getOpenFileNames(
            self,
            "Select images",
            "",
            "Image Files (*.png *.jpg *.jpeg *.gif);;All Files (*)",
            options=options,
        )
        if files:
            # store selected paths and update list widget
            self.image_paths = files
            self.product_images_list.clear()
            self.product_images_list.setVisible(True)
            self.product_images_list.addItems(self.image_paths)

    @pyqtSlot(int)
    def on_name_option_changed(self, idx: int):
        current_action = self.action_name.currentData(
            Qt.ItemDataRole.UserRole)
        if current_action in [
            SELL__BY_GROUP, SELL__BY_MARKETPLACE, DISCUSSION__TO_GROUP, DISCUSSION__TO_NEW_FEED
        ]:
            self.action_option.setHidden(False)
            self.action_option.clear()
            for key, value in ACTION_OPTIONS.items():
                self.action_option.addItem(value.capitalize(), key)
            self.action_option.setCurrentIndex(0)

            if current_action == SELL__BY_GROUP:
                self.group_url_container.setHidden(False)
                self.group_url_input.setText("https://www.facebook.com/groups/475205321869395")
            else:
                self.group_url_container.setHidden(True)
                self.group_url_input.setText("")


        else:
            self.action_option.clear()
            self.action_option.setHidden(True)
    
    @pyqtSlot(int)
    def on_action_option_changed(self, idx: int):
        def set_pid(clear: bool = True):
            self.action_payload.setHidden(clear)
            self.action_payload.setText("")
        def set_custom(clear: bool = True):
            self.content_container.setHidden(clear)
            self.product_description_input.setHidden(clear)
            self.product_description_input.setPlainText("")
            self.product_title_input.setHidden(clear)
            self.product_title_input.setText("")
            self.product_images_list.setHidden(clear)
            self.product_images_list.clear()
        current_option = self.action_option.currentData(
            Qt.ItemDataRole.UserRole
        )
        if current_option == list(ACTION_OPTIONS.keys())[0]:
            set_pid()
            set_custom(clear = True)
        elif current_option == list(ACTION_OPTIONS.keys())[1]:
            set_pid(clear=False)
            set_custom(clear = True)
        elif current_option == list(ACTION_OPTIONS.keys())[2]:
            set_pid(clear=True)
            set_custom(clear=False)
        else:
            set_pid(True)
            set_custom(True)


    @pyqtSlot()
    def on_delete_clicked(self):
        self.deleteLater()


if __name__ == "__main__":
    from PyQt6.QtWidgets import QApplication
    import sys

    app = QApplication(sys.argv)
    action = RobotAction()
    action.show()
    sys.exit(app.exec())
