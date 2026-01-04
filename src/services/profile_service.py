

import os
from typing import Optional, List, Union, Dict, Any

from src.my_types import Profile_Type
from src.services._base_service import BaseService
from src.utils.profile_handlers import create_profile_folder, remove_profile_folder


PROFILE_CONTAINER_DIR = "profile_container_dir"


class Profile_Service(BaseService):
    """
    Service layer for Profile, handling business logic and file system coordination (profile folders).
    """

    def _dict_to_data_type(self, data: Dict[str, Any]) -> Profile_Type:
        """Converts a database dictionary record into a Profile_Type dataclass."""
        required_keys = [
            field.name for field in Profile_Type.__dataclass_fields__.values()
        ]
        return Profile_Type(**{key: data.get(key) for key in required_keys})

    def create(self, profile_payload: Profile_Type) -> Union[Profile_Type, bool]:
        """
        Creates a new profile record and associated profile folder.
        """
        new_ua = self.init_ua()
        profile_payload.mobile_ua = new_ua["mobile"]
        profile_payload.desktop_ua = new_ua["desktop"]
        new_profile = self.repo_manager.profile_repo.insert(profile_payload)
        if not new_profile:
            self.logger.error("Failed to insert profile into repository.")
            return False
        
        profile_container = self.repo_manager.setting_repo.get_setting_value_by_name(PROFILE_CONTAINER_DIR)
        
        if not profile_container or not os.path.exists(profile_container):
            self.logger.error(f"Profile container directory not found: {profile_container}. Aborting folder creation.")
            self.repo_manager.profile_repo.delete_profile_by_id(new_profile.id)
            return False

        current_profile_dir = os.path.join(profile_container, str(new_profile.id))
        if not create_profile_folder(current_profile_dir):
             self.logger.error(f"Failed to create profile folder at: {current_profile_dir}. Rolling back DB insert.")
             self.repo_manager.profile_repo.delete_profile_by_id(new_profile.id)
             return False
        
        self.logger.info(f"Profile created successfully: {new_profile.id}")
        return new_profile

    def update(self, profile_payload: Profile_Type) -> bool:
        """
        Updates an existing profile record.
        """
        is_updated = self.repo_manager.profile_repo.update_profile(profile_payload)
        if is_updated:
            self.logger.info(f"Profile updated successfully: {profile_payload.id}")
            return True
        self.logger.error(f"Failed to update profile: {profile_payload.id}")
        return False
    
    def change_status(self, id: str, status: str):
        is_updated = self.repo_manager.profile_repo.change_status(id, status)
        if is_updated:
            self.logger.info(f"Profile updated successfully: {id}")
            return True
        self.logger.error(f"Failed to update profile: {id}")
        return False

    def delete(self, profile_id: str) -> bool:
        """
        Deletes a profile record and its associated profile folder.
        """
        profile_container = self.repo_manager.setting_repo.get_setting_value_by_name(PROFILE_CONTAINER_DIR)
        current_profile_dir = os.path.join(profile_container, profile_id)
        
        if not remove_profile_folder(current_profile_dir):
            self.logger.warning(f"Failed to remove profile directory for profile: {profile_id}. Proceeding with DB deletion.")
        
        is_deleted = self.repo_manager.profile_repo.delete_profile_by_id(profile_id)
        
        if is_deleted:
            self.logger.info(f"Profile deleted successfully: {profile_id}")
            return True
        else:
            self.logger.error(f"Failed to delete profile from DB: {profile_id}")
            return False

    def read(self, profile_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieves a single profile record by ID, including its associated profile folder path.
        """
        profile_info = self.repo_manager.profile_repo.get_profile_by_id(profile_id)
        
        if not profile_info:
            self.logger.warning(f"Profile not found with ID: {profile_id}")
            return None
        
        profile_container = self.repo_manager.setting_repo.get_setting_value_by_name(PROFILE_CONTAINER_DIR)
        
        if not profile_container:
            self.logger.warning("Profile container directory setting is missing. Returning profile info only.")
        else:
            current_profile_dir = os.path.join(profile_container, profile_id)
            
        return {
            "info": profile_info,
            "profile_path": current_profile_dir
        }

    def read_all(self) -> List[Dict[str, Any]]:
        """
        Retrieves all profile records, including associated profile folder paths.
        """
        list_of_profile = self.repo_manager.profile_repo.get_all_profiles()
        results = []
        
        profile_container = self.repo_manager.setting_repo.get_setting_value_by_name(PROFILE_CONTAINER_DIR)
        
        if not profile_container:
            self.logger.warning("Profile container directory setting is missing. Returning profile info only.")
            for profile_info in list_of_profile:
                results.append({
                    "info": profile_info,
                    "profile_path": ""
                })
        else:
            for profile_info in list_of_profile:
                current_profile_dir = os.path.join(profile_container, str(profile_info.id))
                results.append({
                    "info": profile_info,
                    "profile_path": current_profile_dir
                })

        return results
    
    def get_all_uid(self) -> List[str]:
        uids = self.repo_manager.profile_repo.get_all_uid()
        return [uid.get("uid") for uid in uids]

    def refresh_ua(self, list_of_profile_id: List[str]) -> bool:
        """
        Refreshes the mobile_ua and desktop_ua fields for a list of profiles 
        by generating new User Agents and updating the records.
        """
        all_success = True

        for profile_id in list_of_profile_id:
            try:
                current_profile = self.repo_manager.profile_repo.get_profile_by_id(profile_id)
                if not current_profile:
                    self.logger.warning(f"Profile not found with ID: {profile_id}. Skipping UA refresh.")
                    all_success = False
                    continue
                    
                ua_dict = self.init_ua()
                
                current_profile.mobile_ua = ua_dict["mobile"]
                current_profile.desktop_ua = ua_dict["desktop"]
                current_profile.updated_at = self.repo_manager.profile_repo.init_time() 

                is_updated = self.repo_manager.profile_repo.update_profile(current_profile)
                
                if is_updated:
                    self.logger.info(f"User Agents refreshed for profile ID: {profile_id}")
                else:
                    self.logger.error(f"Failed to update User Agents for profile ID: {profile_id}. Database update failed.")
                    all_success = False

            except Exception as e:
                self.logger.error(f"Exception during UA refresh for profile ID {profile_id}: {e}")
                all_success = False
                
        return all_success

    def read_all_for_export(self) -> List[Dict[str, Any]]:
        """
        Retrieves all profile records in dictionary format for export/display.
        """
        return self.repo_manager.profile_repo.get_all_for_export()
    
    def create_bulk(self, payload: List[Profile_Type]) -> bool:
        """
        Inserts multiple Profile_Type records in a single database transaction.
        """
        if not payload:
            return True
        
        success = self.repo_manager.profile_repo.insert_bulk(payload)
        if success:
            self.logger.info(f"Successfully inserted {len(payload)} profiles in bulk.")
        else:
            self.logger.error(f"Failed to insert profiles in bulk. Transaction rolled back.")
        return success