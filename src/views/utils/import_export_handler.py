# src/views/utils/export_import_handler.py
import os
from typing import Union
from PyQt6.QtWidgets import QFileDialog, QMessageBox, QTableView
from src.utils.logger import Logger
from src.controllers.misc_product_controller import MiscProduct_Controller
from src.controllers.profile_controller import Profile_Controller
from src.controllers.property_product_controller import PropertyProduct_Controller
from src.controllers.property_template_controller import PropertyTemplate_Controller
from src.controllers.setting_controller import Setting_Controller

class ImportExportHandler:
    def __init__(self, controller: Union[MiscProduct_Controller, Profile_Controller, PropertyProduct_Controller, PropertyTemplate_Controller, Setting_Controller], table_view: QTableView):
        self.controller = controller
        self.table_view = table_view
        self.logger = Logger(self.__class__.__name__)
    
    def handleImport(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self.table_view,
            "Import data", "",
            "JSON file (*.json);; CSV File (*.csv)"
        )
        if file_path:
            file_format = os.path.splitext(file_path)[1].lstrip(".").lower()
            if file_format not in ["json", "csv"]:
                QMessageBox.critical(
                    self.table_view,
                    "Error",
                    "Unsupported file format. Use .json or .csv.",
                )
                return
            try:
                if self.controller.import_data(file_path, file_format):
                    QMessageBox.information(
                        self.table_view,
                        "Success",
                        f"Data imported successfully.",
                    )
                else:
                    QMessageBox.critical(
                        self.table_view,
                        "Error",
                        f"Failed to import data. Check logs for details.",
                    )
            except Exception as e:
                self.logger.error(
                    f"Critical error during import: {e}"
                )
                QMessageBox.critical(
                    self.table_view,
                    "Fatal Error",
                    f"A critical error occurred during import: {e}",
                )
    
    def handleExport(self):
        """Handles the dialog and calls the Controller to export data."""
        default_file_name = f"untitled_export.csv"
        file_path, _ = QFileDialog.getSaveFileName(
            self.table_view,
            "Export Data",
            default_file_name,
            "CSV Files (*.csv);;JSON Files (*.json)",
        )
        if file_path:
            file_format = os.path.splitext(file_path)[1].lstrip(".").lower()
            if file_format not in ["json", "csv"]:
                QMessageBox.critical(
                    self.table_view,
                    "Error",
                    "Unsupported file format. Use .json or .csv.",
                )
                return

            try:
                # Call the export_data method on the controller
                if self.controller.export_data(
                    file_path=file_path,
                    data_format=file_format,
                ):
                    QMessageBox.information(
                        self.table_view,
                        "Success",
                        f"Data for exported successfully.",
                    )
                else:
                    QMessageBox.critical(
                        self.table_view,
                        "Error",
                        f"Failed to export data for. Check logs for details.",
                    )
            except Exception as e:
                self.logger.error(
                    f"Critical error during export for: {e}"
                )
                QMessageBox.critical(
                    self.table_view,
                    "Fatal Error",
                    f"A critical error occurred during export: {e}",
                )
