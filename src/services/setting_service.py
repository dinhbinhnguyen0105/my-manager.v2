# src/services/setting_service.py

from typing import Optional, List, Union, Dict, Any
from dataclasses import asdict

from src.my_types import Setting_Type
from src.services._base_service import BaseService


class Setting_Service(BaseService):
    """
    Service layer for Setting, handling application configuration logic.
    """
    def _dict_to_data_type(self, data: Dict[str, Any]) -> Setting_Type:
        """Converts a database dictionary record into a Setting_Type dataclass."""
        required_keys = [
            field.name for field in Setting_Type.__dataclass_fields__.values()
        ]
        return Setting_Type(**{key: data.get(key) for key in required_keys})

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
    
    def toggle_select(self, setting_id: str, is_selected: bool) -> bool:
        """
        Updates the 'is_selected' status of a specific setting record by ID.
        
        Args:
            setting_id: The ID of the setting to change the status for.
            is_selected: The desired state (True for selected, False for unselected).
            
        Returns:
            True if the update was successful, False otherwise.
        """
        # Prepare a descriptive string for logging
        status_str = "SELECTED" if is_selected else "UNSELECTED"
        
        is_toggled = self.repo_manager.setting_repo.toggle_select(setting_id, is_selected)
        
        if is_toggled:
            self.logger.info(f"Setting ID '{setting_id}' successfully toggled to {status_str}.")
            return True
            
        self.logger.error(f"Failed to toggle 'is_selected' status for Setting ID: {setting_id} to {status_str}.")
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
    def get_proxies_selected(self) -> List[str]:
        return self.repo_manager.setting_repo.get_proxies_selected()
    
    def create_bulk(self, payload: List[Setting_Type]) -> bool:
        """
        Inserts multiple PropertyProduct_Type records in a single database transaction.
        """
        if not payload:
            return True
        
        success = self.repo_manager.setting_repo.insert_bulk(payload)
        if success:
            self.logger.info(f"Successfully inserted {len(payload)} property products in bulk.")
        else:
            self.logger.error(f"Failed to insert property products in bulk. Transaction rolled back.")
        return success