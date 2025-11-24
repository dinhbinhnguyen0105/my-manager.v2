# src/controllers/setting_controller.py

from typing import Union, Optional, List, Tuple
from src.utils.logger import Logger
from src.services._service_manager import Service_Manager
from src.my_types import Setting_Type


class InvalidInputError(Exception): pass
class SettingNotFoundError(Exception): pass


class Setting_Controller:
    def __init__(self, service_manager: Service_Manager):
        self.setting_service = service_manager.setting_service
        self.logger = Logger(self.__class__.__name__)

    def read_by_name(self, setting_name: str) -> Union[Setting_Type, Tuple[bool, str]]:
        try:
            if not setting_name:
                raise InvalidInputError("Setting name is required.")
                
            setting = self.setting_service.read_by_name(setting_name)
            
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
            self.logger.error(error_msg)
            return False, error_msg

    def update(self, setting_name: str, new_value: str) -> Tuple[bool, Optional[str]]:
        try:
            if not setting_name:
                raise InvalidInputError("Setting name is required for update.")
            if new_value is None:
                raise InvalidInputError("New setting value cannot be None.")

            current_setting = self.setting_service.read_by_name(setting_name)
            if not isinstance(current_setting, Setting_Type):
                raise SettingNotFoundError(f"Setting with name '{setting_name}' not found for update.")

            current_setting.value = new_value

            is_updated = self.setting_service.update(current_setting)

            if is_updated:
                return True, None
            else:
                error_msg = f"Service failed to update setting name '{setting_name}'."
                self.logger.error(error_msg)
                return False, error_msg

        except InvalidInputError as e:
            return False, str(e)
        except SettingNotFoundError as e:
            return False, str(e)
        except Exception as e:
            error_msg = f"Unexpected error in update: {e}"
            self.logger.error(error_msg)
            return False, error_msg

    def read_all(self) -> List[Setting_Type]:
        return self.setting_service.read_all()