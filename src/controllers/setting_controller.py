# src/controllers/setting_controller.py

from typing import Union, Optional, List, Tuple
from src.controllers._base_controller import BaseController
from src.services._service_manager import Service_Manager
from src.my_types import Setting_Type
from src.utils.exception_handler import log_exception


class InvalidInputError(Exception): pass
class SettingNotFoundError(Exception): pass


class Setting_Controller(BaseController):
    def __init__(self, service_manager:Service_Manager):
        super().__init__(service_manager)

    # --- CREATE ---
    def create(self, setting_payload: Setting_Type) -> Union[Setting_Type, Tuple[bool, str]]:
        """
        Creates a new setting record.
        Returns the created Setting_Type object or a failure Tuple.
        """
        try:
            if not setting_payload.name:
                raise InvalidInputError("Setting payload must include a name.")
            
            new_setting = self.service_manager.setting_service.create(setting_payload)
            
            if isinstance(new_setting, Setting_Type):
                return new_setting
            else:
                # Service layer handles internal failure logging (e.g., DB error)
                error_msg = f"Service failed to create setting: {setting_payload.name}. Check service logs."
                self.logger.error(error_msg)
                return False, error_msg
                
        except InvalidInputError as e:
            return False, str(e)
        except Exception as e:
            error_msg = f"Unexpected error in create: {e}"
            log_exception(e)
            return False, error_msg

    # --- READ by Name ---
    def read_by_name(self, setting_name: str) -> Union[Setting_Type, Tuple[bool, str]]:
        """
        Retrieves a single setting record by its unique name.
        """
        try:
            if not setting_name:
                raise InvalidInputError("Setting name is required.")
                
            setting = self.service_manager.setting_service.read_by_name(setting_name)
            
            if isinstance(setting, Setting_Type):
                return setting
            else:
                raise SettingNotFoundError(f"Setting with name '{setting_name}' not found.")
                
        except InvalidInputError as e:
            return False, str(e)
        except SettingNotFoundError as e:
            return False, str(e)
        except Exception as e:
            error_msg = f"Unexpected error in read_by_name: {e}"
            log_exception(e)
            return False, error_msg

    # --- READ by ID ---
    def read(self, setting_id: str) -> Union[Setting_Type, Tuple[bool, str]]:
        """
        Retrieves a single setting record by its ID.
        """
        try:
            if not setting_id:
                raise InvalidInputError("Setting ID is required.")
                
            setting = self.service_manager.setting_service.read(setting_id) # service.read is read by ID
            
            if isinstance(setting, Setting_Type):
                return setting
            else:
                raise SettingNotFoundError(f"Setting with ID '{setting_id}' not found.")
                
        except InvalidInputError as e:
            return False, str(e)
        except SettingNotFoundError as e:
            return False, str(e)
        except Exception as e:
            error_msg = f"Unexpected error in read: {e}"
            log_exception(e)
            return False, error_msg

    # --- READ All ---
    def read_all(self) -> List[Setting_Type]:
        """
        Retrieves all setting records.
        """
        return self.service_manager.setting_service.read_all()

    # --- UPDATE by Name ---
    def update(self, setting_name: str, new_value: str) -> Tuple[bool, Optional[str]]:
        """
        Updates the value of an existing setting record by its name.
        """
        try:
            if not setting_name:
                raise InvalidInputError("Setting name is required for update.")
            if new_value is None:
                raise InvalidInputError("New setting value cannot be None.")

            # Sử dụng hàm update_by_name ở tầng service để thực hiện việc fetch, update giá trị và lưu lại.
            is_updated = self.service_manager.setting_service.update_by_name(setting_name, new_value)

            if is_updated:
                return True, None
            else:
                # Vì service.update_by_name() không phân biệt lỗi 'not found' và 'DB failed', 
                # ta cần kiểm tra thủ công nếu muốn phân biệt lỗi rõ hơn, 
                # nhưng hiện tại ta sẽ dựa vào logic của service và cung cấp thông báo lỗi chung.
                # Nếu muốn chắc chắn lỗi là 'not found', nên thêm logic kiểm tra:
                if not self.service_manager.setting_service.read_by_name(setting_name):
                    raise SettingNotFoundError(f"Setting with name '{setting_name}' not found for update.")
                    
                error_msg = f"Service failed to update setting name '{setting_name}'. Check service logs."
                self.logger.error(error_msg)
                return False, error_msg

        except InvalidInputError as e:
            return False, str(e)
        except SettingNotFoundError as e:
            return False, str(e)
        except Exception as e:
            error_msg = f"Unexpected error in update: {e}"
            log_exception(e)
            return False, error_msg

    # --- DELETE ---
    def delete(self, setting_id: str) -> Tuple[bool, Optional[str]]:
        """
        Deletes a setting record by its ID.
        """
        try:
            if not setting_id:
                raise InvalidInputError("Setting ID is required for deletion.")

            # Kiểm tra sự tồn tại trước để có thể raise SettingNotFoundError rõ ràng
            current_setting = self.service_manager.setting_service.read(setting_id)
            if not isinstance(current_setting, Setting_Type):
                raise SettingNotFoundError(f"Setting with ID '{setting_id}' not found for deletion.")

            is_deleted = self.service_manager.setting_service.delete(setting_id)

            if is_deleted:
                return True, None
            else:
                error_msg = f"Service failed to delete setting with ID '{setting_id}'. Check service logs."
                self.logger.error(error_msg)
                return False, error_msg

        except InvalidInputError as e:
            return False, str(e)
        except SettingNotFoundError as e:
            return False, str(e)
        except Exception as e:
            error_msg = f"Unexpected error in delete: {e}"
            log_exception(e)
            return False, error_msg
    
    # --- TOGGLE SELECT ---
    def toggle_select(self, setting_id: str, is_selected: bool) -> Tuple[bool, Optional[str]]:
        """
        Toggles the 'is_selected' status of a setting record by its ID.

        Args:
            setting_id: The ID of the setting to change the status for.
            is_selected: The desired state (True for selected, False for unselected).

        Returns:
            A tuple (True, None) on successful toggle, or (False, error_message) otherwise.
        """
        try:
            if not setting_id:
                raise InvalidInputError("Setting ID is required for toggling selection.")

            # Kiểm tra sự tồn tại trước để có thể raise SettingNotFoundError rõ ràng
            current_setting = self.service_manager.setting_service.read(setting_id)
            if not isinstance(current_setting, Setting_Type):
                raise SettingNotFoundError(f"Setting with ID '{setting_id}' not found for toggling.")

            # Gọi tầng service để thực hiện logic cập nhật
            is_toggled = self.service_manager.setting_service.toggle_select(setting_id, is_selected)

            if is_toggled:
                return True, None
            else:
                # Service layer failure (e.g., DB error)
                status_str = "selected" if is_selected else "unselected"
                error_msg = f"Service failed to toggle setting ID '{setting_id}' to {status_str}. Check service logs."
                self.logger.error(error_msg)
                return False, error_msg

        except InvalidInputError as e:
            return False, str(e)
        except SettingNotFoundError as e:
            return False, str(e)
        except Exception as e:
            error_msg = f"Unexpected error in toggle_select: {e}"
            log_exception(e)
            return False, error_msg
    
    def import_data(self,file_path: str, data_format: str) -> Tuple[bool, Optional[str]]:
        return super().import_data("setting_service", file_path, data_format)
    def export_data(self, file_path, data_format = "json"):
        return super().export_data("setting_service", file_path, data_format)