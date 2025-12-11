# src/views/properties/create_new_property_dialog.py
from typing import List
from PyQt6.QtWidgets import QDialog, QMessageBox
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QDragEnterEvent, QDropEvent, QPixmap

from src.ui.dialog_properties_ui import Ui_Dialog_Properties
from src.utils.validators import FloatValidator
from src.my_constants import (
    PROPERTY_PRODUCT__STATUS_OPTIONS,
    PROPERTY_PRODUCT__TRANSACTION_OPTIONS,
    PROPERTY_PRODUCT__PROVINCE_OPTIONS,
    PROPERTY_PRODUCT__DISTRICT_OPTIONS,
    PROPERTY_PRODUCT__WARD_OPTIONS,
    PROPERTY_PRODUCT__CATEGORY_OPTIONS,
    PROPERTY_PRODUCT__UNIT_OPTIONS,
    PROPERTY_PRODUCT__LEGAL_OPTIONS,
    PROPERTY_PRODUCT__BUILDING_LINE_OPTIONS,
    PROPERTY_PRODUCT__FURNITURE_OPTIONS,
)

class CreateNewPropertyDialog(QDialog, Ui_Dialog_Properties):
    property_data_signal = pyqtSignal(dict)
    def __init__(self, parent = None):
        super(CreateNewPropertyDialog, self).__init__(parent)
        self.setupUi(self)
        self.setWindowTitle("Create new property".title())
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        self.setModal(False)
        self.setup_data()
        self.setup_validator()
        self.setup_image_drop()
    
    def setup_data(self):
        self.transaction_combobox.clear()
        for key, value in PROPERTY_PRODUCT__TRANSACTION_OPTIONS.items():
            self.transaction_combobox.addItem(value.capitalize(), key)
        self.status_combobox.clear()
        for key, value in PROPERTY_PRODUCT__STATUS_OPTIONS.items():
            self.status_combobox.addItem(value.capitalize(), key)
        self.categories_combobox.clear()
        for key, value in PROPERTY_PRODUCT__CATEGORY_OPTIONS.items():
            self.categories_combobox.addItem(value.capitalize(), key)
        self.wards_combobox.clear()
        for key, value in PROPERTY_PRODUCT__WARD_OPTIONS.items():
            self.wards_combobox.addItem(value.title(), key)
        self.districts_combobox.clear()
        for key, value in PROPERTY_PRODUCT__DISTRICT_OPTIONS.items():
            self.districts_combobox.addItem(value.capitalize(), key)
        self.provinces_combobox.clear()
        for key, value in PROPERTY_PRODUCT__PROVINCE_OPTIONS.items():
            self.provinces_combobox.addItem(value.capitalize(), key)
        self.furniture_s_combobox.clear()
        for key, value in PROPERTY_PRODUCT__FURNITURE_OPTIONS.items():
            self.furniture_s_combobox.addItem(value.capitalize(), key)
        self.building_line_s_combobox.clear()
        for key, value in PROPERTY_PRODUCT__BUILDING_LINE_OPTIONS.items():
            self.building_line_s_combobox.addItem(value.capitalize(), key)
        self.legal_s_combobox.clear()
        for key, value in PROPERTY_PRODUCT__LEGAL_OPTIONS.items():
            self.legal_s_combobox.addItem(value.capitalize(), key)
    
    def setup_validator(self):
        validator = FloatValidator(self)
        self.price_input.setValidator(validator)
        self.area_input.setValidator(validator)
        self.structure_input.setValidator(validator)
    
    def setup_image_drop(self):
        self.image_input.setAcceptDrops(True)
        self.image_input.dragEnterEvent = self._imagesDragEnterEvent
        self.image_input.dropEvent = self._imagesDropEvent

    def _imagesDragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    def _imagesDropEvent(self, event: QDropEvent):
        if event.mimeData().hasUrls():
            images = [url.toLocalFile() for url in event.mimeData().urls()]
            self._handleDroppedImages(images)
            self.image_paths = images

    def _handleDroppedImages(self, image_paths):
        if image_paths:
            self._display_image(image_paths[0])
        else:
            self.image_input.setText("No images dropped.")

    def _display_image(self, image_path):
        pixmap = QPixmap(image_path)
        if not pixmap.isNull():
            self.image_input.setPixmap(
                pixmap.scaled(
                    self.image_input.size(),
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation,
                )
            )
        else:
            self.image_input.setText("Failed to load image.")

    def accept(self):
        area = float(
            self.area_input.text().strip().lower()
            if self.area_input.text().strip().lower()
            else 0
        )
        price = float(
            self.price_input.text().strip().lower()
            if self.price_input.text().strip().lower()
            else 0
        )
        structure = float(
            self.structure_input.text().strip().lower()
            if self.structure_input.text().strip().lower()
            else 0
        )
        product_data = {
            "id" : None,
            "pid" : None,
            "status" : self.status_combobox.itemData(self.status_combobox.currentIndex()),
            "transaction_type" : self.transaction_combobox.itemData(self.transaction_combobox.currentIndex()),
            "province" : self.provinces_combobox.itemData(self.provinces_combobox.currentIndex()),
            "district" : self.districts_combobox.itemData(self.districts_combobox.currentIndex()),
            "district" : self.districts_combobox.itemData(self.districts_combobox.currentIndex()),
            "ward" : self.wards_combobox.itemData(self.wards_combobox.currentIndex()),
            "street" : self.street_input.text().strip(),
            "category" : self.categories_combobox.itemData(self.categories_combobox.currentIndex()),
            "area" : area,
            "price" : price,
            "legal" : self.legal_s_combobox.itemData(self.legal_s_combobox.currentIndex()),
            
            "structure" : structure,
            "function" : self.function_input.text().strip(),
            "building_line" : self.building_line_s_combobox.itemData(self.building_line_s_combobox.currentIndex()),
            "furniture" : self.furniture_s_combobox.itemData(self.furniture_s_combobox.currentIndex()),
            "description": self.description_input.toPlainText(),
            "created_at": None,
            "updated_at": None,
        }
        if not self.image_paths:
            QMessageBox.warning(
                self,
                "Images missing",
                "At least 1 image is required for the product.",
                QMessageBox.StandardButton.Retry,
            )
            return
        if not product_data.get("price"):
            QMessageBox.warning(
                self,
                "Missing value for the 'Price' field.",
                "'Price' is a required field.",
                QMessageBox.StandardButton.Retry,
            )
            return
        self.product_data_signal.emit(
            {
                "image_paths": self.image_paths,
                "info": product_data,
            }
        )
        return super().accept()
    
    def reject(self):
        return super().reject()