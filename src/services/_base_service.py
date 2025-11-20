# src/services/_base_service.py
from fake_useragent import UserAgent
from typing import List, Dict, Any, Tuple, Optional
import json, csv

from src.utils.logger import Logger
from src.repositories._repo_manager import Repository_Manager


class BaseService:
    def __init__(self, repo_manager: Repository_Manager):
        self.repo_manager = repo_manager
        self.logger = Logger(self.__class__.__name__)

    def init_ua(self) -> Dict[str, str]:
        ua_desktop = UserAgent(os="Mac OS X")
        ua_mobile = UserAgent(os="iOS")
        return {"mobile": ua_mobile.random, "desktop": ua_desktop.random}

    # ----------------------------------------------------------------------
    # NEW: Export/Import Methods with CSV Support
    # ----------------------------------------------------------------------

    def export_data(
        self,
        file_path: str,
        data_to_export: List[Dict[str, Any]],
        data_format: str = "json",
    ) -> bool:
        """
        Exports a list of dictionary data to a specified file path and format (JSON or CSV).
        """
        if not data_to_export:
            self.logger.warning("Attempted to export data but the data list is empty.")
            return False

        data_format = data_format.lower()

        if data_format == "json":
            try:
                with open(file_path, "w", encoding="utf-8") as f:
                    json.dump(data_to_export, f, ensure_ascii=False, indent=4)
                self.logger.info(f"Data successfully exported to {file_path} as JSON.")
                return True
            except Exception as e:
                self.logger.error(f"Error exporting data to JSON: {e}")
                return False

        elif data_format == "csv":
            try:
                # Lấy headers (tên cột) từ khóa của bản ghi đầu tiên
                headers = list(data_to_export[0].keys())

                with open(file_path, "w", newline="", encoding="utf-8") as f:
                    writer = csv.DictWriter(f, fieldnames=headers)
                    writer.writeheader()
                    writer.writerows(data_to_export)

                self.logger.info(f"Data successfully exported to {file_path} as CSV.")
                return True
            except Exception as e:
                self.logger.error(f"Error exporting data to CSV: {e}")
                return False

        else:
            self.logger.error(
                f"Unsupported export format: {data_format}. Only 'json' and 'csv' are supported in BaseService."
            )
            return False

    def import_data(
        self,
        file_path: str,
        data_format: str = "json",
    ) -> Optional[List[Dict[str, Any]]]:
        """
        Imports data from a specified file path and format (JSON or CSV).
        """
        data_format = data_format.lower()

        if data_format == "json":
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)

                if isinstance(data, list):
                    self.logger.info(
                        f"Data successfully imported from {file_path} as JSON."
                    )
                    return data
                else:
                    self.logger.error(
                        "Imported JSON file does not contain a list of records."
                    )
                    return None
            except FileNotFoundError:
                self.logger.error(f"Import failed: File not found at {file_path}")
                return None
            except json.JSONDecodeError as e:
                self.logger.error(
                    f"Import failed: Invalid JSON format in file {file_path}: {e}"
                )
                return None
            except Exception as e:
                self.logger.error(f"Error importing data from JSON: {e}")
                return None

        elif data_format == "csv":
            try:
                data = []
                with open(file_path, "r", newline="", encoding="utf-8") as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        data.append(dict(row))

                if data:
                    self.logger.info(
                        f"Data successfully imported from {file_path} as CSV."
                    )
                    return data
                else:
                    self.logger.warning(f"Imported CSV file is empty: {file_path}")
                    return []

            except FileNotFoundError:
                self.logger.error(f"Import failed: File not found at {file_path}")
                return None
            except Exception as e:
                self.logger.error(f"Error importing data from CSV: {e}")
                return None

        else:
            self.logger.error(
                f"Unsupported import format: {data_format}. Only 'json' and 'csv' are supported in BaseService."
            )
            return None
