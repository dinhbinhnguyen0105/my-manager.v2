# src/controllers/profile_controller.py

from typing import Dict, Any, Union, Optional, List, Tuple
from src.utils.logger import Logger
from src.services._service_manager import Service_Manager
from src.my_types import Profile_Type
from dataclasses import asdict


class InvalidInputError(Exception): pass
class ProfileNotFoundError(Exception): pass


class Profile_Controller:
    def __init__(self, service_manager: Service_Manager):
        self.profile_service = service_manager.profile_service
        self.logger = Logger(self.__class__.__name__)

    def create(self, request_data: Dict[str, Any]) -> Union[Profile_Type, Tuple[bool, str]]:
        try:
            if not request_data.get("profile_name"):
                raise InvalidInputError("Required field 'profile_name' is missing.")
            
            payload = Profile_Type(
                id=None, mobile_ua="", desktop_ua="", created_at=None, updated_at=None,
                uid=request_data.get("uid"),
                status=request_data.get("status", 1), 
                username=request_data.get("username"),
                password=request_data.get("password"),
                two_fa=request_data.get("two_fa"),
                email=request_data.get("email"),
                email_password=request_data.get("email_password"),
                phone_number=request_data.get("phone_number"),
                profile_note=request_data.get("profile_note"),
                profile_type=request_data.get("profile_type"),
                profile_group=request_data.get("profile_group", 1),
                profile_name=request_data["profile_name"],
            )
            
            new_profile = self.profile_service.create(payload)
            
            if isinstance(new_profile, Profile_Type):
                return new_profile 
            else:
                self.logger.error(f"Service failed to create profile: {payload.profile_name}")
                return False, "Failed to create profile. Check service logs."
        
        except InvalidInputError as e:
            return False, str(e)
        except Exception as e:
            error_msg = f"Unexpected error in create: {e}"
            self.logger.error(error_msg)
            return False, error_msg

    def read(self, profile_id: str) -> Union[Profile_Type, Tuple[bool, str]]:
        try:
            if not profile_id:
                raise InvalidInputError("Profile ID is required.")
                
            profile = self.profile_service.read(profile_id)
            
            if isinstance(profile, Profile_Type):
                return profile
            else:
                raise ProfileNotFoundError(f"Profile with ID '{profile_id}' not found.")
                
        except InvalidInputError as e:
            return False, str(e)
        except ProfileNotFoundError as e:
            return False, str(e)
        except Exception as e:
            error_msg = f"Unexpected error in read: {e}"
            self.logger.error(error_msg)
            return False, error_msg

    def update(self, profile_id: str, update_data: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        try:
            if not profile_id:
                raise InvalidInputError("Profile ID is required for update.")
            if not update_data:
                raise InvalidInputError("Update data cannot be empty.")

            current_profile = self.profile_service.read(profile_id)
            if not isinstance(current_profile, Profile_Type):
                raise ProfileNotFoundError(f"Profile with ID '{profile_id}' not found for update.")

            profile_dict = asdict(current_profile)
            profile_dict.update(update_data)
            
            updated_payload = Profile_Type(**profile_dict)

            is_updated = self.profile_service.update(updated_payload)

            if is_updated:
                return True, None
            else:
                error_msg = f"Service failed to update profile ID '{profile_id}'."
                self.logger.error(error_msg)
                return False, error_msg

        except InvalidInputError as e:
            return False, str(e)
        except ProfileNotFoundError as e:
            return False, str(e)
        except Exception as e:
            error_msg = f"Unexpected error in update: {e}"
            self.logger.error(error_msg)
            return False, error_msg

    def delete(self, profile_id: str) -> Tuple[bool, Optional[str]]:
        try:
            if not profile_id:
                raise InvalidInputError("Profile ID is required for delete.")

            is_deleted = self.profile_service.delete(profile_id)
            
            if is_deleted:
                return True, None
            else:
                error_msg = f"Failed to delete profile with ID '{profile_id}'. It may not exist."
                self.logger.error(error_msg)
                return False, error_msg

        except InvalidInputError as e:
            return False, str(e)
        except Exception as e:
            error_msg = f"Unexpected error in delete: {e}"
            self.logger.error(error_msg)
            return False, error_msg

    def read_all(self) -> List[Profile_Type]:
        return self.profile_service.read_all()