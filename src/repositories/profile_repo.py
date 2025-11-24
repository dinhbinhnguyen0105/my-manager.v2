# src/repositories/profile_repo.py

from typing import Dict, Any, Optional, List, Union, Tuple
from dataclasses import asdict
from src.my_constants import DB_TABLES
from src.repositories._base_repo import BaseRepository
from src.my_types import Profile_Type


PROFILE_TABLE = DB_TABLES["profile"]


class Profile_Repo(BaseRepository):
    """
    Repository class for managing Profile records in the database.
    """

    def _dict_to_profile(self, data: Dict[str, Any]) -> Profile_Type:
        """Converts a database dictionary record into a Profile_Type dataclass."""
        # Ensure all keys required by Profile_Type are present, using None/default for safety
        required_keys = [
            field.name for field in Profile_Type.__dataclass_fields__.values()
        ]
        return Profile_Type(**{key: data.get(key) for key in required_keys})

    def insert(self, profile_payload: Profile_Type) -> Union[Profile_Type, bool]:
        """Inserts a single Profile_Type record into the database."""
        profile_payload.id = self.init_id()
        profile_payload.created_at = self.init_time()
        profile_payload.updated_at = profile_payload.created_at

        sql = f"""
        INSERT INTO {PROFILE_TABLE} (
            id, mobile_ua, desktop_ua, uid, status, username, password, two_fa, email, email_password, phone_number, profile_note, profile_type, profile_group, profile_name, created_at, updated_at
        ) VALUES (
            :id, :mobile_ua, :desktop_ua, :uid, :status, :username, :password, :two_fa, :email, :email_password, :phone_number, :profile_note, :profile_type, :profile_group, :profile_name, :created_at, :updated_at
        )
        """
        if self.insert(sql=sql, params=asdict(profile_payload)):
            return profile_payload
        return False

    def update_profile(self, profile_payload: Profile_Type) -> bool:
        """Updates an existing Profile_Type record based on its ID."""
        if not profile_payload.id:
            self.logger.error("Attempted to update profile without an ID.")
            return False

        profile_payload.updated_at = self.init_time()

        sql = f"""
        UPDATE {PROFILE_TABLE} SET
            mobile_ua = :mobile_ua,
            desktop_ua = :desktop_ua,
            uid = :uid,
            status = :status,
            username = :username,
            password = :password,
            two_fa = :two_fa,
            email = :email,
            email_password = :email_password,
            phone_number = :phone_number,
            profile_note = :profile_note,
            profile_type = :profile_type,
            profile_group = :profile_group,
            profile_name = :profile_name,
            updated_at = :updated_at
        WHERE id = :id
        """
        # Ensure only updatable fields and the ID are in the params
        params = asdict(profile_payload)
        return self.update(sql=sql, params=params)

    def delete_profile_by_id(self, profile_id: str) -> bool:
        """Deletes a profile record by its primary key ID."""
        sql = f"DELETE FROM {PROFILE_TABLE} WHERE id = :id"
        return self.delete(sql=sql, params={"id": profile_id})

    def delete_profile_by_uid(self, profile_uid: str) -> bool:
        """Deletes a profile record by its unique identifier (uid)."""
        sql = f"DELETE FROM {PROFILE_TABLE} WHERE uid = :uid"
        return self.delete(sql=sql, params={"uid": profile_uid})

    def get_profile_by_id(self, profile_id: str) -> Optional[Profile_Type]:
        """Retrieves a single profile record by its primary key ID."""
        sql = f"SELECT * FROM {PROFILE_TABLE} WHERE id = :id"
        result_dict = self.get_one(sql=sql, params={"id": profile_id})

        if result_dict:
            return self._dict_to_profile(result_dict)
        return None

    def get_profile_by_uid(self, profile_uid: str) -> Optional[Profile_Type]:
        """Retrieves a single profile record by its unique identifier (uid)."""
        sql = f"SELECT * FROM {PROFILE_TABLE} WHERE uid = :uid"
        result_dict = self.get_one(sql=sql, params={"uid": profile_uid})

        if result_dict:
            return self._dict_to_profile(result_dict)
        return None

    def get_all_profiles(self) -> List[Profile_Type]:
        """Retrieves all profile records from the table."""
        sql = f"SELECT * FROM {PROFILE_TABLE}"
        results_list = self.get_all(sql=sql)

        return [self._dict_to_profile(data) for data in results_list]

    def get_all_for_export(self) -> List[Dict[str, Any]]:
        """Retrieves all profile records as a list of dictionaries, suitable for export."""
        sql = f"SELECT * FROM {PROFILE_TABLE}"
        return self.get_all(sql=sql)

    def insert_bulk_profiles(self, profile_list: List[Profile_Type]) -> bool:
        """
        Inserts multiple Profile_Type records in a single transaction.
        Returns True on full success, False otherwise (with rollback).
        """
        if not profile_list:
            return True

        # 1. Prepare data and SQL outside the transaction callback
        params_list = []
        for profile in profile_list:
            profile.id = self.init_id()
            profile.created_at = self.init_time()
            profile.updated_at = profile.created_at
            params_list.append(asdict(profile))

        sql = f"""
        INSERT INTO {PROFILE_TABLE} (
            id, mobile_ua, desktop_ua, uid, status, username, password, two_fa, email, email_password, phone_number, profile_note, profile_type, profile_group, profile_name, created_at, updated_at
        ) VALUES (
            :id, :mobile_ua, :desktop_ua, :uid, :status, :username, :password, :two_fa, :email, :email_password, :phone_number, :profile_note, :profile_type, :profile_group, :profile_name, :created_at, :updated_at
        )
        """

        # 2. Define the callback for transaction execution
        def execute_bulk_insert() -> Tuple[bool, Any]:
            # execute_many handles the preparation and execution loop for each set of params
            success = self.execute_many(sql=sql, params_list=params_list)
            return success, None

        # 3. Execute the operation within a transaction
        success, _ = self.execute_in_transaction(execute_bulk_insert)
        return success
