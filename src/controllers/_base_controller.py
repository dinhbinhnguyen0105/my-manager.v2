# src/controllers/_base_controller.py

from src.utils.logger import Logger
from src.services._service_manager import Service_Manager
import os
from typing import Tuple, Optional


class BaseController:
    def __init__(self, service_manager: Service_Manager):
        self.service_manager = service_manager
        self.logger = Logger(self.__class__.__name__)

    def export_data(
        self, service_name: str, file_path: str, data_format: str = "json"
    ) -> Tuple[bool, Optional[str]]:
        try:
            service = getattr(self.service_manager, service_name, None)
            if not service:
                error_msg = f"Error: Service not found: {service_name}"
                self.logger.error(error_msg)
                return False, error_msg

            data_to_export = service.get_all_for_export()

            if not data_to_export:
                warning_msg = f"Warning: No data available to export from {service_name}."
                self.logger.warning(warning_msg)
                return True, warning_msg

            data_format = data_format.lower()
            if data_format not in ["json", "csv"]:
                error_msg = f"Error: Unsupported data format '{data_format}'. Supported formats are 'json' and 'csv'."
                self.logger.error(error_msg)
                return False, error_msg

            success = service.export_data(
                file_path=file_path,
                data_to_export=data_to_export,
                data_format=data_format,
            )

            if success:
                return True, None
            else:
                error_msg = f"Export failed in Service Layer for {service_name}. Check service logs for details."
                self.logger.error(error_msg)
                return False, error_msg

        except Exception as e:
            error_msg = f"Unexpected error during export in Controller: {e}"
            self.logger.error(error_msg)
            return False, error_msg

    def import_data(
        self, service_name: str, file_path: str, data_format: str = "json"
    ) -> Tuple[bool, Optional[str]]:
        if not os.path.exists(file_path):
            error_msg = f"Import failed: File not found at {file_path}"
            self.logger.error(error_msg)
            return False, error_msg

        try:
            service = getattr(self.service_manager, service_name, None)
            if not service:
                error_msg = f"Error: Service not found: {service_name}"
                self.logger.error(error_msg)
                return False, error_msg

            data_format = data_format.lower()
            if data_format not in ["json", "csv"]:
                error_msg = f"Error: Unsupported data format '{data_format}'. Supported formats are 'json' and 'csv'."
                self.logger.error(error_msg)
                return False, error_msg

            raw_data = service.import_data(file_path=file_path, data_format=data_format)

            if not raw_data:
                warning_msg = f"Import process returned no data from file: {file_path}. Check service logs for file read error."
                self.logger.warning(warning_msg)
                return False, warning_msg

            success = service.insert_imported_data(raw_data)

            if success:
                return True, None
            else:
                error_msg = f"Data insertion failed in Service Layer for {service_name}. Check service logs for DB error."
                self.logger.error(error_msg)
                return False, error_msg

        except Exception as e:
            error_msg = f"Unexpected error during import in Controller: {e}"
            self.logger.error(error_msg)
            return False, error_msg