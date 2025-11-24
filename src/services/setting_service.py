# src/services/setting_service.py

from typing import Optional, List, Union, Dict, Any
from dataclasses import asdict

from src.my_types import Setting_Type
from src.services._base_service import BaseService


class Setting_Service(BaseService):
    """
    Service layer for Setting, handling application configuration logic.
    """

    def create(self, setting_payload: Setting_Type) -> Union[Setting_Type, bool]:
        """
        Creates a new setting record.
        """
        new_setting = self.repo_manager.setting_repo.insert(setting_payload)
        if new_setting:
            self.logger.info(f"Setting created successfully: {new_setting.name}")
            return new_setting
        self.logger.error(f"Failed to insert setting: {setting_payload.name}")
        return False

    def update(self, setting_payload: Setting_Type) -> bool:
        """
        Updates an existing setting record by ID.
        """
        is_updated = self.repo_manager.setting_repo.update_setting(setting_payload)
        if is_updated:
            self.logger.info(f"Setting updated successfully: {setting_payload.name}")
            return True
        self.logger.error(f"Failed to update setting: {setting_payload.name}")
        return False
    
    def update_by_name(self, setting_name: str, new_value: str) -> bool:
        """
        Updates the value of a setting by its unique name.
        """
        current_setting = self.repo_manager.setting_repo.get_setting_by_name(setting_name)
        if not current_setting:
            self.logger.error(f"Setting not found for update: {setting_name}")
            return False
            
        current_setting.value = new_value
        current_setting.updated_at = self.repo_manager.setting_repo.init_time() # Cập nhật thời gian
        
        # Dùng phương thức update theo ID
        is_updated = self.repo_manager.setting_repo.update_setting(current_setting)
        
        if is_updated:
            self.logger.info(f"Setting '{setting_name}' value updated to '{new_value}'.")
            return True
        self.logger.error(f"Failed to update setting value for: {setting_name}")
        return False


    def delete(self, setting_id: str) -> bool:
        """
        Deletes a setting record by ID.
        """
        is_deleted = self.repo_manager.setting_repo.delete_setting_by_id(setting_id)
        if is_deleted:
            self.logger.info(f"Setting deleted successfully: {setting_id}")
            return True
        self.logger.error(f"Failed to delete setting from DB: {setting_id}")
        return False

    def read(self, setting_id: str) -> Optional[Setting_Type]:
        """
        Retrieves a single setting record by ID.
        """
        return self.repo_manager.setting_repo.get_setting_by_id(setting_id)

    def read_by_name(self, setting_name: str) -> Optional[Setting_Type]:
        """
        Retrieves a single setting record by its unique name.
        """
        return self.repo_manager.setting_repo.get_setting_by_name(setting_name)

    def read_value_by_name(self, setting_name: str) -> Optional[str]:
        """
        Retrieves only the value of a setting by its unique name.
        """
        return self.repo_manager.setting_repo.get_setting_value_by_name(setting_name)

    def read_all(self) -> List[Setting_Type]:
        """
        Retrieves all setting records.
        """
        return self.repo_manager.setting_repo.get_all_settings()

    def read_all_for_export(self) -> List[Dict[str, Any]]:
        """
        Retrieves all setting records in dictionary format for export/display.
        """
        return self.repo_manager.setting_repo.get_all_for_export()